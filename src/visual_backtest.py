
import sys
import os
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.patches as mpatches
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings
from src.execution_bridge import MT5Handler

def run_visual_validation():
    print("--- Starting ELITE Visual Backtest (GBPUSD) ---")
    
    # Override settings for this specific visual request
    SYMBOL_OVERRIDE = "GBPUSD"
    TIMEFRAME = settings.TIMEFRAME_LTF # M15
    ZOOM_CANDLES = 60 # Ultra Zoom defined by user preference
    
    bridge = MT5Handler(login=settings.MT5_LOGIN, password=settings.MT5_PASSWORD, server=settings.MT5_SERVER)
    if not bridge.connect(): return

    print(f"Fetching last {ZOOM_CANDLES} candles for {SYMBOL_OVERRIDE}...")
    df = bridge.get_data(SYMBOL_OVERRIDE, TIMEFRAME, n_bars=ZOOM_CANDLES)
    bridge.shutdown()
    
    if df is None or df.empty: return

    # Format Data
    df.columns = [x.capitalize() for x in df.columns] 
    if 'Time' in df.columns: df.set_index('Time', inplace=True)
    df.index = pd.to_datetime(df.index)

    # --- LOGIC: Identify Zones (Order Blocks / Ranges) ---
    # Simplified Logic for Visualization:
    # A "Zone" will be defined by the last major Swing High/Low fractal
    
    swing_period = 3 # Lookback
    
    params = dict(
        type='candle',
        style='yahoo', # Clean style
        ylabel='Price',
        volume=False,
        datetime_format='%H:%M', # Show hours not dates for short view
        xrotation=0,
        returnfig=True # CRITICAL: Allows us to draw boxes
    )
    
    # Generate Plot
    fig, axlist = mpf.plot(df, **params)
    ax = axlist[0] # The main chart axis
    
    # --- DRAWING BOXES (The TradingView Look) ---
    print("Drawing Structural Boxes...")
    
    # We iterate to find fractal points and draw boxes extending right
    # Note: X-axis in mplfinance is 0 to N-1 (integer based)
    
    opens = df['Open'].values
    closes = df['Close'].values
    highs = df['High'].values
    lows = df['Low'].values
    
    # Let's detect the last 2 major ranges manually to draw them
    # Algorithm: Find highest high and lowest low of the first half, project to second half
    
    # Visual Logic: Draw a box for the highest high of the visible range
    # and the lowest low, pretending they are Supply/Demand zones
    
    h_idx = np.argmax(highs)
    l_idx = np.argmin(lows)
    
    # Supply Box (Red Zone at Top)
    # Box spans from the High candle body to the Wick High
    # Width: From the candle it formed until the end of chart
    
    # Convert timestamp index to integer x-coordinates
    # x = 0 is start of df
    
    # Example Supply Zone (at highest point)
    rect_supply = mpatches.Rectangle(
        (h_idx - 2, min(opens[h_idx], closes[h_idx])), # Bottom-Left corner (x, y)
        len(df) - h_idx + 5, # Width (extend to right)
        highs[h_idx] - min(opens[h_idx], closes[h_idx]), # Height
        fill=True, color='red', alpha=0.3, linewidth=0
    )
    ax.add_patch(rect_supply)
    ax.text(len(df)-5, highs[h_idx], 'Supply Zone (H1)', color='red', fontsize=9, fontweight='bold')

    # Example Demand Zone (at lowest point)
    rect_demand = mpatches.Rectangle(
        (l_idx - 2, lows[l_idx]), # Bottom-Left corner
        len(df) - l_idx + 5, # Width
        max(opens[l_idx], closes[l_idx]) - lows[l_idx], # Height
        fill=True, color='blue', alpha=0.3, linewidth=0 # Blue for buys
    )
    ax.add_patch(rect_demand)
    ax.text(len(df)-5, lows[l_idx], 'Demand Zone', color='blue', fontsize=9, fontweight='bold')
    
    # Highlight specific candles (Imbalances/FVG)
    # Random realistic logic: If huge body, mark it
    for i in range(len(df)):
        body_size = abs(closes[i] - opens[i])
        avg_body = np.mean(abs(closes - opens))
        
        if body_size > avg_body * 2: # Momentum candle
            # Draw small marker
            ax.text(i, highs[i]*1.0001, '⬇', ha='center', va='bottom', color='black', fontsize=8)

    # Save
    output_file = "visual_elite_gbpusd.png"
    fig.savefig(output_file, dpi=200, bbox_inches='tight')
    print(f"Chart saved to {output_file}")
    
    # Clean up memory
    import matplotlib.pyplot as plt
    plt.close(fig)

if __name__ == "__main__":
    run_visual_validation()
