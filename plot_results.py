import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def main():
    bt = pd.read_csv("./results/backtrader_performance.csv")
    p = pd.read_csv("./results/pandas_performance.csv")

    df = pd.DataFrame(index=p.index)

    # Backtrader prints a flat line for the first 200 days so I added this logic to compensate
    df["pandas"] = p.iloc[:, 1] * 100000
    df["pandas"] = df["pandas"].pct_change()[200:]
    df["pandas"] = (1+df["pandas"]).cumprod() + 100000

    df["backtrader"] = bt.iloc[200:, 1]

    df.plot()
    plt.show()

if __name__ == '__main__':
    main()