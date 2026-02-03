from data_handle import DataHandler
from strategy import UpDownStrategy

print("STARTING TEST...")

dh = DataHandler("AAPL.csv")
dh.load_data()

strategy = UpDownStrategy()

print("Entering loop...")

count = 0
while dh.has_data():
    bar = dh.get_next_bar()
    signal = strategy.on_bar(bar)
    print(bar.date, bar.close, signal)
    count += 1

print("DONE. Bars processed:", count)
print("Bars seen by strategy:", strategy.n_bars)
print("Closes seen:", [float(x) for x in strategy.close_upto_now()])
