class Portfolio:
    def __init__(self, initial_cash = 10000.0, trade_size = 10, use_all_in = False):
        self.initial_cash = float(initial_cash)
        self.cash = float(initial_cash)
        
        self.position = 0
        self.avg_entry_price = 0.0
        
        self.trade_size = int(trade_size)
        self.use_all_in = bool(use_all_in)
        
        self.trades = []
        self.equity_curve = []
        
    def _portfolio_valuse(self, price: float) -> float:
        return self.cash + self.position * float(price)
    
    def _record_equity(self, date, price: float):
        self.equity_curve.append({
            'date': date,
            'price': float(price),
            'cash': self.cash,
            'position': self.position,
            'equity': self._portfolio_valuse(price),
            })
    
    def _buy_shares(self, date, price: float, shares: int):
        price = float(price)
        shares = int(shares)
        if shares <= 0:
            return
        
        cost = shares * price
        if cost > self.cash:
            shares = int(self.cash // price)
            cost = shares * price
            if shares <= 0:
                return
            
        new_total_shares = self.position + shares
        if self.position == 0:
            self.avg_entry_price = price
        else:
            self.avg_entry_price = (
                (self.avg_entry_price * self.position) + (price * shares)
                ) / new_total_shares
        self.position = new_total_shares
        self.cash -= cost
        
        self.trades.append({
            'date': date,
            'side': 'BUY',
            'shares': shares,
            'price': price,
            'cash after': self.cash,
            'position_after': self.position
            })
    def _sell_shares(self, date, price: float, shares:int):
        price = float(price)
        shares = int(shares)
        if shares <= 0 or self.position <= 0:
            return
        
        shares = min(shares, self.position)
        proceeds = shares * price
        
        self.position -= shares
        self.cash += proceeds
        
        if self.position == 0:
            self.avg_entry_price = 0.0
            
        self.trades.append({
            'date': date,
            'side': 'SELL',
            'shares': shares,
            'price': price,
            'cash after': self.cash,
            'position_after': self.position
        })
        
    def on_bar(self, bar, signal: str):
        signal = (signal or '').strip().upper()
        price = bar.close
        
        if signal == 'BUY':
            if self.use_all_in:
                shares = int(self.cash // price)
            else:
                shares = self.trade_size
            self._buy_shares(bar.date, price, shares)
            
        elif signal == 'SELL':
            if self.use_all_in:
                shares = self.position
            else:
                shares = self.trade_size
            self._sell_shares(bar.date, price, shares)
        self._record_equity(bar.date, price)
        
    def summary(self):
        if not self.equity_curve:
            return {
                'initial_cash': self.initial_cash,
                'final_equity': self.initial_cash,
                'return_pct': 0.0,
                'num_trades': 0,
                'final_cash': self.cash,
                'final_position': self.position
            }
        
        final_equity = self.equity_curve[-1]['equity']
        return_pct = (final_equity / self.initial_cash - 1.0) * 100.0
        
        return {
            'initial_cash': self.initial_cash,
            'final_equity': final_equity,
            'return_pct': return_pct,
            'num_trades': len(self.trades),
            'final_cash': self.cash,
            'final_position': self.position
        }
            
        
    
    
