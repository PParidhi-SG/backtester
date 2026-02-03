from Bar_data import Bar

import pandas as pd

class DataHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.current_index = 0
    
    def load_data(self):
        self.data = pd.read_csv(self.file_path)
        print('Data loaded')
        print('Rows:', len(self.data))
        print(self.data.head())
        
    def has_data(self):
        return self.current_index < len(self.data)
    
    def get_next_bar(self):
        if not self.has_data():
            return None
        
        row = self.data.iloc[self.current_index]
        self.current_index += 1
        
        return Bar(
            row['date'],
            float(row['open']),
            float(row['close']),
            float(row['high']),
            float(row['low']),
            int(row['volume']),
        )
        
dh = DataHandler('AAPL.csv')
dh.load_data()

while dh.has_data():
    bar = dh.get_next_bar()
    print(bar.date, bar.open, bar.close)