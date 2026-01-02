from datetime import datetime

class RiskGuardian:
    """
    Agente 3: Risk_Guardian (Risk & Psychology)
    Gestión de capital estricta.
    """
    
    def __init__(self, daily_loss_limit_pct=0.02):
        self.daily_loss_limit_pct = daily_loss_limit_pct
        self.current_daily_loss = 0.0
        self.is_trading_allowed = True
        self.start_balance = 0.0 # Should be set on init
        
    def update_daily_pnl(self, current_balance):
        """
        Updates the PnL for the day and checks kill switch.
        """
        if self.start_balance == 0:
            self.start_balance = current_balance
            
        pnl_pct = (current_balance - self.start_balance) / self.start_balance
        
        if pnl_pct <= -self.daily_loss_limit_pct:
            self.activate_kill_switch()
            
    def activate_kill_switch(self):
        print("CRITICAL: Daily Loss Limit Reached. KILL SWITCH ACTIVATED. No more trading for 24h.")
        self.is_trading_allowed = False
        
    def calculate_lot_size(self, symbol, entry_price, stop_loss, risk_pct, account_balance):
        """
        Calculates position size using the Master Formula (Risk / TickVal).
        Mathematically precise for ANY asset (Forex, Crypto, Metals).
        """
        # Ensure MT5 is initialized
        import MetaTrader5 as mt5 
        if not mt5.initialize(): return 0.0

        if entry_price == 0 or stop_loss == 0: return 0.0
        
        # 1. Get real data
        info = mt5.symbol_info(symbol)
        if info is None: return 0.0
        
        # 2. Risk in Cash
        risk_amount_cash = account_balance * risk_pct
        
        # 3. Stop Loss Distance
        points_at_risk = abs(entry_price - stop_loss)
        
        # Safety check for tiny SL (avoid division by infinity)
        if points_at_risk < info.point: 
            return 0.0
            
        # 4. Correct Tick Value Calculation
        tick_value = info.trade_tick_value
        tick_size = info.trade_tick_size
        
        if tick_size == 0 or tick_value == 0: return 0.0
        
        # MASTER FORMULA:
        # LotSize = RiskCash / ( (PointsAtRisk / TickSize) * TickValue )
        # explanation: (Points / TickSize) = Number of Ticks
        # Number of Ticks * TickValue = Loss per 1.0 Lot
        
        loss_per_lot = (points_at_risk / tick_size) * tick_value
        
        if loss_per_lot == 0: return 0.0
        
        raw_lot_size = risk_amount_cash / loss_per_lot
        
        # 5. Normalize
        step = info.volume_step
        min_vol = info.volume_min
        max_vol = info.volume_max
        
        if step > 0:
            final_lot = round(raw_lot_size / step) * step
        else:
            final_lot = raw_lot_size
            
        # 6. Margin Check (Final Guard)
        try:
            margin_req = mt5.order_calc_margin(mt5.ORDER_TYPE_BUY, symbol, final_lot, entry_price)
            account_info = mt5.account_info()
            if margin_req and account_info and margin_req > account_info.margin_free:
                # Resize to fit margin
                scale = (account_info.margin_free * 0.95) / margin_req
                final_lot = final_lot * scale
                # Re-round
                if step > 0: final_lot = round(final_lot / step) * step
        except:
            pass
            
        # Final Limits
        final_lot = max(min_vol, min(final_lot, max_vol))
        
        return round(final_lot, 2)
        
    def can_trade(self):
        return self.is_trading_allowed

    def check_free_rolling(self, primary_trade_profit):
        """
        Lógica de 'Free Rolling': Si la entrada 1 está en profit,
        permite financiar el riesgo de la ráfaga.
        """
        if primary_trade_profit > 0:
            return True
        return False
