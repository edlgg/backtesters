import os
import pandas as pd
import pandas_ta as ta

def load_data(args):
    files = os.listdir(f"./data/mod/")
    stocks = []
    for f in files:
        df = pd.read_csv(f"./data/mod/{f}", index_col="date")
        df.name = f.split(".")[0]
        stocks.append(df)

    return stocks

def add_indicators(stocks, args):
    for df in stocks:
        df["returns"] = df["close"].pct_change()
        df["roc"] = ta.roc(df["close"], length=args["roc_period"])
    return stocks

def filter_dates(stocks, args):
    l = []
    for s in stocks:
        df = s.loc[args["start_date"]:args["end_date"]]
        df.name = s.name
        l.append(df)
    return l

def prepare_data(stocks, args):
    close = pd.DataFrame(index=stocks[0].index)
    returns = pd.DataFrame(index=stocks[0].index)
    roc = pd.DataFrame(index=stocks[0].index)
    
    for s in stocks:
        close[s.name] = s["close"]
        returns[s.name] = s["returns"]
        roc[s.name] = s["roc"]

    return close, returns, roc

def compute_weights(close, returns, roc, args):
    weights = pd.DataFrame(float(0), index=close.index, columns=close.columns)
    for date in list(weights.index):
        top10 = list(roc.loc[date].sort_values(ascending=False)[:10].index)
        for symbol in top10:
            weights.loc[date][symbol] = 0.1
    return weights

def compute_performance(weights, returns):
    weighted_returns = (weights * returns.shift(-1)).sum(axis=1)
    performance = (1+weighted_returns).cumprod()
    print(performance)
    return performance

def run_pandas(args):
    # Filter date in datas and remove filter from code
    stocks = load_data(args)
    stocks = add_indicators(stocks, args)
    stocks = filter_dates(stocks, args)
    close, returns, roc = prepare_data(stocks, args)
    weights = compute_weights(close, returns, roc, args)
    performance = compute_performance(weights, returns)
    performance.to_csv("./results/pandas_performance.csv")