
import sys
import os
import pandas as pd
import numpy as np
# Eliminamos vectorbt para evitar problemas de dependencias
# import vectorbt as vbt 

from datetime import datetime

# Add parent dir to sys path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import settings
from src.execution_bridge import MT5Handler
try:
    from src.smc_analyst import SMCAnalyst
except ImportError:
    pass

def simulate_trade_vectorized(df, entries, sl_pips, rr_ratio):
    """
    Simula trades de forma vectorizada usando Pandas/Numpy.
    Retorna: Net Profit (R-Multiples)
    """
    # Convert pips to price diff
    sl_dist = sl_pips * 0.0001
    tp_dist = sl_dist * rr_ratio
    
    # Get entry prices
    entry_prices = df.loc[entries != 0, 'Close'].values
    entry_directions = entries[entries != 0].values # 1 for Buy, -1 for Sell
    entry_indices = np.where(entries != 0)[0]
    
    if len(entry_indices) == 0:
        return 0.0
    
    wins = 0
    losses = 0
    
    highs = df['High'].values
    lows = df['Low'].values
    
    for i, idx in enumerate(entry_indices):
        entry_price = entry_prices[i]
        direction = entry_directions[i]
        
        if direction == 1: # BUY
            tp_price = entry_price + tp_dist
            sl_price = entry_price - sl_dist
        else: # SELL
            tp_price = entry_price - tp_dist
            sl_price = entry_price + sl_dist
        
        # Look forward
        future_highs = highs[idx+1:]
        future_lows = lows[idx+1:]
        
        if len(future_highs) == 0: continue
            
        # Find hits
        if direction == 1: # BUY
            sl_hits = future_lows < sl_price
            tp_hits = future_highs > tp_price
        else: # SELL
            sl_hits = future_highs > sl_price  # Stop Hit (High goes above SL)
            tp_hits = future_lows < tp_price   # TP Hit (Low goes below TP)
        
        if not sl_hits.any() and not tp_hits.any():
            continue 
            
        first_sl = np.argmax(sl_hits) if sl_hits.any() else 999999
        first_tp = np.argmax(tp_hits) if tp_hits.any() else 999999
        
        if first_tp < first_sl:
            wins += 1
        else:
            losses += 1
            
    total_r = (wins * rr_ratio) - (losses * 1.0)
    return total_r

def run_optimization():
    print("--- Starting NATIVE Optimization Pipeline (Pandas) ---")
    
    # 1. Connect & Fetch Data
    bridge = MT5Handler(login=settings.MT5_LOGIN, password=settings.MT5_PASSWORD, server=settings.MT5_SERVER)
    if not bridge.connect(): return

    # Fetch significant history
    # 10k bars is fast now with vectorized logic
    N_BARS = 10000 
    TARGET_SYMBOL = "EURUSD" # Optimize on EURUSD
    print(f"Fetching last {N_BARS} candles for {TARGET_SYMBOL}...")
    df = bridge.get_data(TARGET_SYMBOL, settings.TIMEFRAME_LTF, n_bars=N_BARS)
    bridge.shutdown()
    
    if df is None: return

    # 2. Format Data
    df.columns = [x.capitalize() for x in df.columns] 
    if 'Time' in df.columns: df.set_index('Time', inplace=True)
    df.index = pd.to_datetime(df.index)

    # 3. Generate Signals
    analyst = SMCAnalyst(swing_lookback=settings.SWING_LOOKBACK)
    print("Analyzing structure and generating signal vector...")
    entries = analyst.generate_historical_signals(df)
    
    n_signals = entries.sum()
    print(f"Total Signals Generated: {n_signals}")
    
    if n_signals == 0:
        print("No signals found.")
        return

    # 4. Grid Search Simulation
    print("Simulating Parameters...")
    
    # Grid
    stops_pips = [5, 10, 15, 20, 30] # Pips
    rr_ratios = [1.5, 2.0, 3.0, 5.0, 10.0]
    
    results = [] # (SL, RR, Total_R, WinRate)
    
    # We assume signals are BUY for the simulation logic above.
    # The analyst 'TRAP SWEEP' logic returns BUY for Bull Trap sweep.
    # So we simulate Longs.
    
    for sl in stops_pips:
        row_res = []
        for rr in rr_ratios:
            total_r = simulate_trade_vectorized(df, entries, sl, rr)
            results.append({
                'SL_Pips': sl,
                'RR': rr,
                'Total_R': total_r
            })
            print(f". Tested SL={sl} pips, RR=1:{rr} -> Result: {total_r:.2f} R")
    
    # 5. Analysis
    res_df = pd.DataFrame(results)
    
    # Create Pivot Table (Heatmap style)
    pivot = res_df.pivot(index='SL_Pips', columns='RR', values='Total_R')
    
    print("\n\n=== GOLDEN PARAMETERS HEATMAP (Total R-Multiples) ===")
    print(pivot.to_string())
    
    best = res_df.loc[res_df['Total_R'].idxmax()]
    print(f"\nWINNER CONFIGURATION:")
    print(f"Stop Loss: {best['SL_Pips']} pips")
    print(f"Take Profit: 1:{best['RR']} ({(best['SL_Pips']*best['RR']):.1f} pips)")
    print(f"Total Gain: {best['Total_R']:.2f} R")
    
    # Save
    pivot.to_csv('optimization_results.csv')
    print("Saved to optimization_results.csv")

if __name__ == "__main__":
    run_optimization()
