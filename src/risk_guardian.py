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
        
    def calculate_lot_size(self, entry_price, stop_loss, risk_amount, account_balance):
        """
        Standard position size calculator.
        """
        # (Balance * Risk%) / (Distance * PipValue)
        # Simplified placeholder
        risk_per_share = abs(entry_price - stop_loss)
        if risk_per_share == 0: return 0
        
        shares = (account_balance * risk_amount) / risk_per_share
        return round(shares, 2)
        
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
