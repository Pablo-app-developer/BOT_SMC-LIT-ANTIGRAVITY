import MetaTrader5 as mt5
import time
import pandas as pd
from datetime import datetime
from config import settings

class MT5Handler:
    """
    Agente 2: Execution_Bridge (MT5 Connectivity)
    Gestión de conexión con el broker y órdenes.
    """

    def __init__(self, login=None, password=None, server=None):
        self.login = login
        self.password = password
        self.server = server
        self.connected = False

    def connect(self):
        """
        Initializes connection to MT5.
        """
        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            return False
        
        # If credentials provided, login
        if self.login and self.password and self.server:
            authorized = mt5.login(self.login, password=self.password, server=self.server)
            if not authorized:
                print("failed to connect at account #{}, error code: {}".format(self.login, mt5.last_error()))
                return False
        
        self.connected = True
        print("Connected to MT5 Terminal")
        return True

    def get_data(self, symbol, timeframe, n_bars=1000):
        """
        Fetches historical data.
        """
        if not self.connected:
            self.connect()
            
        # MT5 timeframe mapping (simplified)
        tf_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4
        }
        
        rates = mt5.copy_rates_from_pos(symbol, tf_map.get(timeframe, mt5.TIMEFRAME_M15), 0, n_bars)
        
        if rates is None:
            print(f"No data for {symbol}")
            return None
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Normalize columns for SMC Analysis (Capitalized)
        df.rename(columns={
            'time': 'Time', 
            'open': 'Open', 
            'high': 'High', 
            'low': 'Low', 
            'close': 'Close', 
            'tick_volume': 'Volume'
        }, inplace=True)
        
        # Set index to Time for easier manipulation
        df.set_index('Time', inplace=True)
        
        return df

    def place_limit_order(self, symbol, order_type, price, stop_loss, take_profit, volume):
        """
        Places a limit order using raw MT5 logic.
        """
        if not self.connected:
            return None
            
        action = mt5.TRADE_ACTION_PENDING
        type_op = mt5.ORDER_TYPE_BUY_LIMIT if order_type == 'BUY' else mt5.ORDER_TYPE_SELL_LIMIT
        
        request = {
            "action": action,
            "symbol": symbol,
            "volume": volume,
            "type": type_op,
            "price": price,
            "sl": stop_loss,
            "tp": take_profit,
            "magic": 123456, 
            "comment": "Fusion Bot Entry",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order failed: {result.comment}")
            return None
            
        return result

    def modify_sl_to_be(self, ticket, open_price):
        """
        Moves SL to Break Even.
        """
        # Logic to modify order positions would go here
        print(f"Moving SL for ticket {ticket} to {open_price}")
        pass

    def shutdown(self):
        mt5.shutdown()

    def place_market_order(self, symbol, order_type, volume, stop_loss, take_profit):
        """
        Places a Market Order (Instant Execution).
        """
        if not mt5.initialize(): return None
        
        tick = mt5.symbol_info_tick(symbol)
        price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": order_type,
            "price": price,
            "sl": float(stop_loss),
            "tp": float(take_profit),
            "deviation": 20,
            "magic": 123456,
            "comment": "Fusion Bot Algo",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order Failed: {result.comment}")
            return None
            
        print(f"Order Sent Successfully! Ticket: {result.order}")
        return result

class ExecutionManager:
    """
    Manages the state of the bot's portfolio:
    - Tracking Primary Entry vs Bursts
    - Managing Risks (SL Moves)
    """
    def __init__(self):
        self.primary_trade = None # Ticket ID
        self.burst_trades = [] # List of Ticket IDs
        self.active_trap = None # ID of the trap we are trading

    def register_primary_entry(self, ticket):
        self.primary_trade = ticket
        print(f"ExecManager: Registered Primary Trade #{ticket}")

    def register_burst_entry(self, ticket):
        self.burst_trades.append(ticket)
        print(f"ExecManager: Registered Burst Trade #{ticket}")
        
    def get_open_positions(self):
        # Wrapper to get actual positions from MT5 (All symbols)
        if not mt5.initialize(): return []
        return mt5.positions_get()

    def check_burst_eligibility(self, current_price):
        """
        Determines if we can fire a 'Burst' trade (Pyramiding).
        Rule: Primary trade must be Risk Free (SL at BE or better).
        """
        if not self.primary_trade:
            return False
            
        # Get position details
        positions = mt5.positions_get(ticket=self.primary_trade)
        if not positions:
            print(f"Primary trade {self.primary_trade} not found (closed?). Resetting.")
            self.primary_trade = None
            return False
            
        pos = positions[0]
        
        # Check if SL is at Breakeven or better
        # Buy: SL >= PriceOpen
        # Sell: SL <= PriceOpen
        is_buy = pos.type == mt5.ORDER_TYPE_BUY
        
        if is_buy:
            if pos.sl >= pos.price_open: return True
        else:
            if pos.sl > 0 and pos.sl <= pos.price_open: return True
            
        return False

    def update_trailing_stops(self, current_price, bridge_handler):
        """
        Logic to move SL to Break Even ('Free Rolling').
        Trigger: When price moves 1R in our favor.
        """
        if not self.primary_trade: return
        
        positions = mt5.positions_get(ticket=self.primary_trade)
        if not positions: return
        pos = positions[0]
        
        # 1R Logic (Simplified: 20 pips or similar, should be config based)
        # For now, let's say if we are 0.2% in profit
        entry = pos.price_open
        is_buy = pos.type == mt5.ORDER_TYPE_BUY
        
        profit_pct = (current_price - entry) / entry if is_buy else (entry - current_price) / entry
        
        # Threshold to move to BE (e.g., 0.15% move)
        BE_THRESHOLD = 0.0015 
        
        if profit_pct > BE_THRESHOLD:
            # Check if already at BE to avoid spamming modification
            if (is_buy and pos.sl < entry) or (not is_buy and (pos.sl == 0 or pos.sl > entry)):
                print(f"Securing Profit! Moving SL to BE for Trade #{self.primary_trade}")
                
                # Call MT5 modify
                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": pos.ticket,
                    "symbol": pos.symbol,
                    "sl": entry, # Move to Entry
                    "tp": pos.tp
                }
                
                res = mt5.order_send(request)
                if res.retcode != mt5.TRADE_RETCODE_DONE:
                    print(f"Failed to move SL: {res.comment}")
