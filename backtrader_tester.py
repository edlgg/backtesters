import backtrader as bt
import os
from datetime import datetime
import math
import pandas as pd
import numpy as np
import collections



DATASETS_PATH = "./data/"


class DOHLCVPData(bt.feeds.GenericCSVData):
    lines = ('padding', )
    params = (
        ('nullvalue', float('NaN')),
        ('dtformat', '%Y-%m-%d'),
        ('datetime', 0),
        ('time', -1),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', 5),
        ('padding', 6),
        ('openinterest', -1),
    )

class MaxRiskSizer(bt.Sizer):
    '''
    Returns the number of shares rounded down that can be purchased for the
    max rish tolerance
    '''
    params = (('risk', 0.1),)

    def __init__(self):
        if self.p.risk > 1 or self.p.risk < 0:
            raise ValueError('The risk parameter is a percentage which must be'
                             'entered as a float. e.g. 0.5')

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy == True:
            size = math.floor((cash * self.p.risk) / data[0])
        else:
            size = math.floor((cash * self.p.risk) / data[0]) * -1
        return size

class Momentum(bt.Strategy):

    params = dict(
        roc_period=200,
        num_positions=10,
    )

    def __init__(self):
        self.idx = self.datas[0]
        self.inds = collections.defaultdict(dict)
        for d in self.datas:
            self.inds[d]["roc"] = bt.indicators.RateOfChange(
                d.close, period=self.p.roc_period)


    def apply_filters(self, start_date):
        stocks = self.datas
        stocks = sorted(
            stocks, key=lambda d: self.inds[d]["roc"], reverse=True
        )
        return stocks

    def next(self):
        date = self.datas[0].datetime.date()
        print(date)
        start_date = datetime.strftime(date, "%Y-%m-%d")
        ranked_stocks = self.apply_filters(start_date)

        if len(ranked_stocks) == 0:
            for d in self.datas:
                if self.broker.getposition(d) != 0:
                    self.close(d)
            return

        for i, d in reversed(list(enumerate(ranked_stocks))):
            if i <= self.p.num_positions:
                self.buy(d)
            else:
                if self.broker.getposition(d) != 0:
                    self.close(d)

def run_backtrader(args):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)
    cerebro.addstrategy(Momentum)
    cerebro.addsizer(MaxRiskSizer, risk=0.1)


    files = os.listdir(f"{DATASETS_PATH}mod/")
    # files = files[20:] # Remove
    for file in files:
        add_symbol(cerebro=cerebro,
                   data_path=f"{DATASETS_PATH}mod/{file}",
                   start_date=args["start_date"],
                   end_date=args["end_date"])

    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="timereturn")
    

    results = cerebro.run()
    st = results[0]
    curve = list(st.observers.broker.lines[1].array[:])
    curve = [x for x in curve if str(x) != 'nan']
    df = pd.DataFrame(curve)
    df.to_csv("./results/backtrader_performance.csv")



def add_symbol(cerebro: bt.Cerebro, data_path: str, start_date: str, end_date: str):
    data = DOHLCVPData(
        dataname=data_path,
        headers=True,
        fromdate=datetime.strptime(start_date, "%Y-%m-%d"),
        todate=datetime.strptime(end_date, "%Y-%m-%d"),
        reverse=False,
    )
    data.plotinfo.plot = False
    data.plotinfo.subplot = False
    data_name = data_path.split("/")[-1][:-4]

    cerebro.adddata(data, name=data_name)
    return data
