
import sys
import os
from config import settings
from src.execution_bridge import MT5Handler
from src.visual_backtest import draw_spectacular_trade

def run_test():
    print("--- GENERANDO GRÁFICO DE PRUEBA (EURUSD) ---")
    
    # 1. Conexión
    bridge = MT5Handler(login=settings.MT5_LOGIN, password=settings.MT5_PASSWORD, server=settings.MT5_SERVER)
    if bridge.connect():
        # 2. Datos
        symbol = "EURUSD"
        print(f"Descargando datos de {symbol}...")
        df = bridge.get_data(symbol, "M15", n_bars=300)
        bridge.shutdown()
        
        if df is not None and not df.empty:
            # 3. Trade Simulado (En la última vela)
            last_close = df['Close'].iloc[-1]
            last_low = df['Low'].iloc[-1]
            
            fake_trade = {
                'symbol': symbol,
                'action': 'BUY',
                'entry': last_close,
                'sl': last_low - 0.0010, # 10 pips SL
                'tp': last_close + 0.0030, # 30 pips TP
                'reason': 'DEMO_TEST_VISUAL',
                'rr': 3.0,
                'real_liq_high': last_close + 0.0040, # Fake algo level
                'real_liq_low': last_close - 0.0040   # Fake algo level
            }
            
            # 4. Dibujar
            output = "test_eurusd_spectacular.png"
            print(f"Generando imagen '{output}'...")
            draw_spectacular_trade(df, fake_trade, output_file=output)
            print("¡Hecho! Revisa el archivo en la carpeta.")
        else:
            print("No se pudieron descargar datos.")
    else:
        print("Error conectando a MT5.")

if __name__ == "__main__":
    run_test()
