
import pandas as pd
import numpy as np

class SMCAnalyst:
    """
    Agente 1: SMC_Analyst (Rediseñado - Pro Version)
    Estrategia: Liquidity Sweep + Range Reclaim (Turtle Soup Pattern)
    """

    def __init__(self, swing_lookback=20):
        # Lookback aumentado: Buscamos liquidez significativa, no ruido de 1 vela.
        # 20 velas M15 = 5 horas de rango. Perfecto para sesiones.
        self.swing_lookback = swing_lookback 
        print(f"SMC_Analyst Pro initialized (Liquidity Window={swing_lookback}).")

    def analyze(self, df: pd.DataFrame):
        """
        Analiza el dataframe en busca de setups de 'Sweep & Reclaim' en la vela actual.
        """
        # Calcular señales solo para la última vela (Live Trading)
        signal = self._check_candle_signal(df, -1)
        
        # Para visualización/debug, podríamos retornar niveles clave
        last_high = df['High'].iloc[-self.swing_lookback-1:-1].max()
        last_low = df['Low'].iloc[-self.swing_lookback-1:-1].min()
        
        return {
            'trap_zone': {'high_liq': last_high, 'low_liq': last_low},
            'signal': signal
        }

    def _check_candle_signal(self, df, idx):
        """
        Verifica si la vela en 'idx' completó un patrón de Sweep & Reclaim.
        """
        if len(df) < self.swing_lookback + 2: return None
        
        # Datos de la vela actual (o la que analizamos)
        current = df.iloc[idx]
        prev_close = df['Close'].iloc[idx-1] # Para confirmar momentum si quisiéramos
        
        # 1. Definir Rango de Liquidez PREVIO a esta vela
        # Miramos hacia atrás desde la vela anterior (idx-1)
        # No incluimos la vela actual en el cálculo del rango, porque ella es la que rompe.
        
        # Slice range: from (idx - lookback) to (idx)
        # Note: iloc slicing excludes end, so idx means up to idx-1
        
        # Ajuste de índices para funcionar tanto con idx negativo (live) como positivo (backtest)
        if idx < 0:
            window = df.iloc[idx - self.swing_lookback : idx]
        else:
            window = df.iloc[idx - self.swing_lookback : idx]
            
        if window.empty: return None

        liq_high = window['High'].max()
        liq_low = window['Low'].min()
        
        # 2. Lógica de Bear Trap (Buy Signal)
        # El precio rompe el mínimo (toma liquidez venta) pero cierra ARRIBA del mínimo.
        # Condición extra: La vela debe ser alcista (Close > Open) para confirmar rechazo.
        
        is_bullish_candle = current['Close'] > current['Open']
        
        if current['Low'] < liq_low and current['Close'] > liq_low and is_bullish_candle:
            # Filtro opcional: ¿El barrido fue significativo o solo 0.1 pip?
            # Para M15, pedimos al menos 1 pip de sweep para evitar ruido de spread
            # sweep_size = liq_low - current['Low']
            # if sweep_size > 0.0001: ...
            
            return {
                'action': 'BUY',
                'price': current['Close'],
                'sl': current['Low'], # SL en la mecha que hizo el barrido
                'reason': 'LIQUIDITY_RAID_BUY',
                'timestamp': current.name
            }

        # 3. Lógica de Bull Trap (Sell Signal)
        # El precio rompe el máximo (toma liquidez compra) pero cierra ABAJO del máximo.
        # Condición extra: Vela bajista.
        
        is_bearish_candle = current['Close'] < current['Open']
        
        if current['High'] > liq_high and current['Close'] < liq_high and is_bearish_candle:
            return {
                'action': 'SELL',
                'price': current['Close'],
                'sl': current['High'], # SL en la mecha superior
                'reason': 'LIQUIDITY_RAID_SELL',
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
