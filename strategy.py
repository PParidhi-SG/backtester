from abc import ABC, abstractmethod

class Strategy(ABC):
    def __init__(self):
        self.bars =[]
        
    def on_bar(self, bar):
       self.bars.append(bar)
       return self.generate_signal()
    def close_upto_now(self):
       return [b.close for b in self.bars]
    def window_closes(self, window: int):
       if window <= 0:
           return []
       return [b.close for b in self.bars[-window:]]
    
    @property
    def n_bars(self):
        return len(self.bars)
    
    @abstractmethod
    def generate_signal(self):
        pass
    
class UpDownStrategy(Strategy):
    def generate_signal(self):
        if self.n_bars < 2:
            return 'Hold'
        
        closes = self.close_upto_now()
        
        if closes [-1] > closes[-2]:
            return 'Buy'
        elif closes[-1] < closes[-2]:
            return 'Sell'
        return 'Hold'