from backtrader_tester import run_backtrader
from pandas_tester import run_pandas


DATASETS_PATH = "./data/mod/"
PLOT_ALL = False
args = {
    "start_date": "2000-01-01",
    "end_date": "2010-01-01",
    # To set the parameter for backtrader it needs to be done in the strategy.
    "roc_period": 200
}


def main():
    run_backtrader(args)
    run_pandas(args)


if __name__ == '__main__':
    main()
