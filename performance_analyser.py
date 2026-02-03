import pandas as pd
import math

class PerformanceAnalyser:
    def __init__(self, equity_curve: list, trades: list, initial_cash: float):
        self.equity_curve = equity_curve or []
        self.trades = trades or []
        self.initial_cash = float(initial_cash)
        
    def equity_df(self) -> pd.DataFrame:
        if not self.equity_curve:
            return pd.DataFrame(columns=['date', 'equity', 'returns'])
        
        df = pd.DataFrame(self.equity_curve).copy()
        
        df['date'] = pd.to_datetime(df['date'].astype(str), format='%Y-%m-%d', errors='coerce')
        df = df.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
        
        df['equity'] = df['equity'].astype(float)
        df['returns'] = df['equity'].pct_change().fillna(0.0)
        
        return df
        
    def drawdown_series(self, equity_df: pd.DataFrame) -> pd.Series:
        if equity_df.empty:
            return pd.Series(dtype=float)
        running_max = equity_df['equity'].cummax()
        dd = (equity_df['equity'] / running_max) - 1.0
        return dd
    def trade_df(self) -> pd.DataFrame:
        if not self.trades:
            return pd.DataFrame(columns=['date', 'side', 'shares', 'price'])
        df = pd.DataFrame(self.trades).copy()
        df['date'] = pd.to_datetime(df['date'].astype(str), format='%Y-%m-%d', errors='coerce')
        df = df.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
        if 'shares' in df.columns:
            df['shares'] = df['shares'].astype(int)
        if 'price' in df.columns:
            df['price'] = df['price'].astype(float)
        if 'side' in df.columns:
            df['side'] = df['side'].astype(str).str.lower()
        return df
    
    def compute_trade_pnl(self) -> dict:
        df = self.trade_df()
        if df.empty:
            return {
                'num_round_trips': 0,
                'win_rate_pct': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
                'total_trade_pnl': 0.0,
                }
        buy_queue = []
        round_trip_pnls = []
        
        for _, row in df.iterrows():
            side = row.get('side', '')
            shares = int(row.get('shares', 0))
            price = float(row.get('price', 0))
            
            if side == 'buy' and shares > 0:
                buy_queue.append([shares, price])
            
            elif side == 'sell' and shares > 0:
                remaining = shares
                pnl = 0.0
                
                while remaining > 0 and buy_queue:
                    b_shares, b_price = buy_queue[0]
                    take = min(remaining, b_shares)
                    pnl += take * (price - b_price)
                    
                    b_shares -= take
                    remaining -= take
                    
                    if b_shares == 0:
                        buy_queue.pop(0)
                    else:
                        buy_queue[0][0] = b_shares
                        
                if shares != remaining:
                    round_trip_pnls.append(pnl)
        
        if not round_trip_pnls:
            return {
                'num_round_trips': 0,
                'win_rate_pct': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
                'total_trade_pnl': 0.0,
                }
        
        wins = [x for x in round_trip_pnls if x > 0]
        losses = [x for x in round_trip_pnls if x < 0]
        
        total_win = sum(wins)
        total_loss_abs = abs(sum(losses))
        profit_factor = (total_win / total_loss_abs) if total_loss_abs > 0 else float('inf')
        
        win_rate = (len(wins) / len(round_trip_pnls)) * 100.0
        
        avg_win = (sum(wins) / len(wins)) if wins else 0.0
        avg_loss = (sum(losses) / len(losses)) if losses else 0.0 
        
        return {
            'num_round_trips': len(round_trip_pnls),
            'win_rate_pct': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor if math.isfinite(profit_factor) else 0.0,
            'total_trade_pnl': sum(round_trip_pnls),
        }
    def summary(self, period_per_year: int = 252) -> dict:
        eq = self.equity_df()
        
        if eq.empty:
            return {
                'initial_cash': self.initial_cash,
                'final_equity': self.initial_cash,
                'total_return_pct': 0.0,
                'volatility_pct': 0.0,
                'sharpe': 0.0,
                'num_bars': 0,
                'num_trades': 0,
                **self.compute_trade_pnl()
            }
        final_equity = float(eq['equity'].iloc[-1])
        total_return_pct = ((final_equity / self.initial_cash) - 1.0) * 100.0
        
        dd = self.drawdown_series(eq)
        max_dd_pct = float(dd.min()) * 100.0 
        
        rets = eq['returns']
        vol = float(rets.std()) * math.sqrt(period_per_year) * 100.0
        
        mean_ret = float(rets.mean()) * period_per_year
        std_ret = float(rets.std()) * math.sqrt(period_per_year)
        sharpe = (mean_ret / std_ret) if std_ret > 0 else 0.0
        
        trade_stats = self.compute_trade_pnl()
        
        return {
            'initial_cash': self.initial_cash,
            'final_equity': final_equity,
            'total_return_pct': total_return_pct,
            'max_drawdown_pct': max_dd_pct,
            'volatility_pct': vol,
            'sharpe': sharpe,
            'num_bars': int(len(eq)),
            'num_trades': int(len(self.trades)),
            **trade_stats
        }
                        
                    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            