import sys
import time
import os
# Add parent dir to sys path to locate config and src if run from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
import MetaTrader5 as mt5

from config import settings
from src.smc_analyst import SMCAnalyst
from src.execution_bridge import MT5Handler, ExecutionManager
from src.risk_guardian import RiskGuardian

def run_fusion_bot():
    print(f"Starting {settings.PROJECT_NAME}...")
    
    # Initialize Agents
    analyst = SMCAnalyst(swing_lookback=settings.SWING_LOOKBACK)
    bridge = MT5Handler(login=settings.MT5_LOGIN, password=settings.MT5_PASSWORD, server=settings.MT5_SERVER)
    guardian = RiskGuardian(daily_loss_limit_pct=settings.DAILY_LOSS_LIMIT)
    exec_manager = ExecutionManager()
    
    # Connection Check
    if not bridge.connect():
        print("Failed to connect to MT5. Exiting...")
        return
        
    # Set initial account balance for PnL calculation
    account_info = bridge.get_data("EURUSD", "M15", n_bars=1) # Dummy call to ensure connection
    # TODO: Add get_account_info to bridge proper
    
    print("All systems GREEN. Entering main loop...")
    
    # State Memory
    active_trap_zone = None
    
    try:
        while True:
            # 1. Update Portfolio & Risk
            open_positions = exec_manager.get_open_positions()
            current_balance = 100000.0 # Placeholder: Implement get_balance
            
            # Update Trailing Stops (Free Rolling)
            current_tick = 1.05000 # Placeholder: Implement get_tick
            exec_manager.update_trailing_stops(current_tick, bridge)
            
            # Check Risk Guardian GLOBAL
            if not guardian.can_trade():
                print("Risk Guardian has blocked trading.")
                time.sleep(300)
                continue
            
            # --- MULTI-ASSET SCANNING LOOP ---
            for symbol in settings.SYMBOLS:
                # 2. Data Ingestion
                # Fetch latest 500 candles for analysis
                df_ltf = bridge.get_data(symbol, settings.TIMEFRAME_LTF, n_bars=500)
                
                if df_ltf is None or df_ltf.empty:
                    # print(f"Warning: No data for {symbol}. Skipping...")
                    continue
                
                # 3. Analysis (Fusion Logic)
                # Run the full analysis pipeline
                analysis_result = analyst.analyze(df_ltf)
                
                trap = analysis_result['trap_zone']
                signal = analysis_result['signal']
                
                # Logging Status (Only if trap exists to reduce noise)
                if trap:
                    # Note: We don't store global 'active_trap' per symbol in this simple loop yet
                    # For production, we should have a dict: active_traps[symbol]
                    # For now, just print the opportunity
                    # print(f"      [{symbol}] Liq Range: {trap['high_liq']} - {trap['low_liq']}")
                    pass
                
                # 4. Signal Execution
                if signal:
                    print(f"\n[$$$] ENTRY SIGNAL: {symbol} {signal['action']} @ {signal['price']}")
                    print(f"      Reason: {signal['reason']}")
                    
                    # Check Risk & Calculate Size
                    sl_price = signal['sl']
                    entry_price = signal['price']
                    
                    # Dynamic lot size calculation based on risk
                    lot_size = guardian.calculate_lot_size(entry_price, sl_price, settings.RISK_PER_TRADE, current_balance)
                    print(f"      Lot Size: {lot_size}")
                    
                    # EXECUTION (LIVE DEMO)
                    if lot_size > 0:
                        print(f"      [>>>] PLACING LIVE ORDER ({lot_size} lots)...")
                        
                        # Calculate TP based on Golden Ratio
                        risk_dist = abs(entry_price - sl_price)
                        tp_price = entry_price + (risk_dist * settings.RISK_REWARD_RATIO) if signal['action'] == 'BUY' else entry_price - (risk_dist * settings.RISK_REWARD_RATIO)
                        
                        # Send Order
                        action_type = mt5.ORDER_TYPE_BUY if signal['action'] == 'BUY' else mt5.ORDER_TYPE_SELL
                        
                        # Since we are reacting to a completed candle Close, we use Market Order or aggressive Limit
                        # For simplicity and guarantee fill on sweep reclaim: Market Order
                        res = bridge.place_market_order(symbol, action_type, lot_size, sl_price, tp_price)
                        
                        if res: 
                            exec_manager.register_primary_entry(res.order)
                            print(f"      [V] ORDER FILLED! Ticket: {res.order}")
            
            print(f". Scanning {len(settings.SYMBOLS)} assets... {datetime.now().strftime('%H:%M:%S')}", end='\r')
            time.sleep(10) # Scan every 10s
            
    except KeyboardInterrupt:
        print("Shutdown signal received.")
        bridge.shutdown()

if __name__ == "__main__":
    run_fusion_bot()
