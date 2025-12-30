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
        Calculates position size based on risk percentage and stop loss distance.
        Uses MT5 symbol info for accurate multi-asset sizing.
        """
        # Ensure MT5 is initialized, though main usually does this
        import MetaTrader5 as mt5 
        if not mt5.initialize(): return 0.0

        if entry_price == 0 or stop_loss == 0: return 0.0
        
        # 1. Get Symbol Properties
        info = mt5.symbol_info(symbol)
        if info is None:
            print(f"RiskGuardian: Symbol {symbol} not found")
            return 0.0
            
        contract_size = info.trade_contract_size
        tick_size = info.trade_tick_size
        tick_value = info.trade_tick_value
        min_vol = info.volume_min
        max_vol = info.volume_max
        step_vol = info.volume_step
        
        # 2. Calculate Risk Amount (Cash)
        risk_cash = account_balance * risk_pct
        
        # 3. Calculate Stop Loss Distance in points
        # SAFETY CHECK: Enforce minimum SL distance of 10 pips (0.0010) 
        # to avoid "Invalid Stops" and crazy lot sizes on small candles.
        min_sl_dist = 0.0010  # 10 pips for Forex
        price_diff = abs(entry_price - stop_loss)
        
        if price_diff < min_sl_dist:
            # print(f"      [Guardian] Adjusting SL from {price_diff:.5f} to {min_sl_dist} (Min 10 pips)")
            price_diff = min_sl_dist
            # Note: We don't change the actual order SL here, just the risk calculation.
            # ideally we should tell main to push SL further away.
        
        loss_per_lot = (price_diff / tick_size) * tick_value
        
        if loss_per_lot == 0: return min_vol
        
        # 4. Normalize Volume
        
        # [NEW] MARGIN CHECK
        # Calculate Margin required for this volume
        try:
            margin_req = mt5.order_calc_margin(mt5.ORDER_TYPE_BUY, symbol, volume, entry_price)
            account_info = mt5.account_info()
            
            if margin_req and account_info and margin_req > account_info.margin_free:
                # Reduce volume to fit free margin (leaving 5% buffer)
                # MaxVolume = (FreeMargin * 0.95) / MarginPerUnit * Volume 
                # Simplification: Scale down
                scale_factor = (account_info.margin_free * 0.90) / margin_req
                volume = volume * scale_factor
                # print(f"      [Guardian] Not enough margin. Scaling down to {volume:.2f} lots")
        except Exception as e:
            print(f"      [Guardian] Margin check error: {e}")

        # Clip to limits (HARD CAP 1.0 LOT FOR SAFETY)
        sane_max = 1.0
        volume = max(min_vol, min(volume, sane_max, max_vol))
        
        # Round to step
        # E.g. 0.123 -> 0.12 if step is 0.01
        if step_vol > 0:
            volume = round(volume / step_vol) * step_vol
            
        return round(volume, 2)
        
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
