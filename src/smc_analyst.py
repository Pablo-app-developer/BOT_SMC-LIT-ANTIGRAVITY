
import pandas as pd
import numpy as np

class SMCAnalyst:
    """
    Agente 1: SMC_Analyst (Rediseñado - Pro Version)
    Estrategia: Liquidity Sweep + Range Reclaim (Turtle Soup Pattern)
    """

    def __init__(self, swing_lookback=96):
        # 96 velas M15 = 24 horas (Daily Cycle)
        self.swing_lookback = swing_lookback 
        print(f"SMC_Analyst Pro initialized (Daily Liquidity Window={swing_lookback}).")

    def analyze(self, df: pd.DataFrame, trend_bias=0):
        """
        Analiza setups con Liquidez Diaria + Reclamo.
        """
        signal = self._check_candle_signal(df, -1, trend_bias)
        
        last_high = df['High'].iloc[-self.swing_lookback-1:-1].max()
        last_low = df['Low'].iloc[-self.swing_lookback-1:-1].min()
        
        return {
            'trap_zone': {'high_liq': last_high, 'low_liq': last_low},
            'signal': signal
        }

    def _check_candle_signal(self, df, idx, trend_bias=0):
        if len(df) < self.swing_lookback + 2: return None
        
        current = df.iloc[idx]
        
        if idx < 0:
            window = df.iloc[idx - self.swing_lookback : idx]
        else:
            window = df.iloc[idx - self.swing_lookback : idx]
            
        if window.empty: return None

        liq_high = window['High'].max()
        liq_low = window['Low'].min()
        
        # Métricas de la vela
        open_p, close_p, high_p, low_p = current['Open'], current['Close'], current['High'], current['Low']
        total_range = high_p - low_p
        if total_range == 0: return None
        
        is_bullish = close_p > open_p
        is_bearish = close_p < open_p
        
        # --- FILTRO PRO: DESPLAZAMIENTO > 0.7 ---
        
        # SEÑAL COMPRA
        if trend_bias >= 0:
            if low_p < liq_low and close_p > liq_low and is_bullish:
                strength = (close_p - low_p) / total_range
                
                # Exigimos cierre en el 30% SUPERIOR (Fuerza > 0.7 desde el bajo)
                if strength > 0.7: 
                    return {
                        'action': 'BUY',
                        'price': close_p,
                        'sl': low_p - 0.0005, # Buffer 5 pips
                        'reason': 'DAILY_LOW_SWEEP_STRONG',
                        'timestamp': current.name
                    }
                    
        # SEÑAL VENTA
        if trend_bias <= 0:
            if high_p > liq_high and close_p < liq_high and is_bearish:
                strength = (high_p - close_p) / total_range
                
                # Exigimos cierre en el 30% INFERIOR (Fuerza > 0.7 desde el alto)
                if strength > 0.7:
                    return {
                        'action': 'SELL',
                        'price': close_p,
                        'sl': high_p + 0.0005, # Buffer 5 pips
                        'reason': 'DAILY_HIGH_SWEEP_STRONG',
                        'timestamp': current.name
                    }
            
        return None

    def generate_historical_signals(self, df: pd.DataFrame):
        """
        Genera vector de señales para Backtesting (VectorBT / Pandas).
        Optimizado para velocidad.
        """
        signals = pd.Series(False, index=df.index)
        
        # Vectorized Approach (Rolling Window)
        # 1. Shifted Rolling Max/Min (Liquidez previa)
        # closed='left' means the window excludes the current point (Perfect for looking back)
        
        r_high = df['High'].rolling(window=self.swing_lookback, closed='left').max()
        r_low = df['Low'].rolling(window=self.swing_lookback, closed='left').min()
        
        # 2. Boolean Conditions
        # Buy Signal: Low < PrevLow AND Close > PrevLow AND Bullish Candle
        buy_cond = (df['Low'] < r_low) & (df['Close'] > r_low) & (df['Close'] > df['Open'])
        
        # Sell Signal: High > PrevHigh AND Close < PrevHigh AND Bearish Candle
        sell_cond = (df['High'] > r_high) & (df['Close'] < r_high) & (df['Close'] < df['Open'])
        
        # Combine
        signals = buy_cond | sell_cond
        
        return signals
