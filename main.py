from data_handler import DataHandler
from strategy import UpDownStrategy
from portfolio import Portfolio
from performance_analyser import PerformanceAnalyser

def run_backtest():
    dh = DataHandler('AAPL.csv')
    dh.load_data()
    
    strat = UpDownStrategy()
    pf = Portfolio(initial_cash=10000, trade_size=10, use_all_in=False)
    
    while dh.has_data():
        bar = dh.get_next_bar()
        signal = strat.on_bar(bar)
        pf.on_bar(bar, signal)
        
        
        print(bar.date, bar.close, signal, 'cash: ', pf.cash, 'pos: ', pf.position)
    
    analyser = PerformanceAnalyser(
        equity_curve=pf.equity_curve,
        trades=pf.trades,
        initial_cash=pf.initial_cash
    )

    print('\nPortfolio Summary:', pf.summary())
    print('Performance Summary:', analyser.summary())


if __name__ == '__main__':
    run_backtest()
