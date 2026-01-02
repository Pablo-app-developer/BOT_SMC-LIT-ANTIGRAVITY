
import sys
import os
import time
from datetime import datetime
from config import settings
import MetaTrader5 as mt5
from src.execution_bridge import MT5Handler
from src.risk_guardian import RiskGuardian
from src.notifications import TelegramNotifier

def print_status(component, status, message=""):
    icon = "✅" if status else "❌"
    print(f"{icon} [{component}]: {message if message else 'OK'}")

def pre_flight_check():
    print("\n" + "="*40)
    print("   🚀 ANTIGRAVITY PRE-FLIGHT CHECK   ")
    print("="*40 + "\n")
    
    all_systems_go = True

    # 1. TEST CONEXIÓN MT5
    bridge = MT5Handler(login=settings.MT5_LOGIN, password=settings.MT5_PASSWORD, server=settings.MT5_SERVER)
    if bridge.connect():
        print_status("MT5 Connection", True, f"Connected to {settings.MT5_SERVER}")
        
        # Obtener Balance Real
        account_info = mt5.account_info()
        if account_info:
            balance = account_info.balance
            print_status("Account Balance", True, f"${balance:.2f} USD")
        else:
            print_status("Account Info", False, "Could not fetch balance")
            all_systems_go = False
            balance = 0
            
    else:
        print_status("MT5 Connection", False, "Failed to connect")
        all_systems_go = False
        return # Si no hay MT5, abortar

    # 2. TEST DE RIESGO (Simulación)
    if balance > 0:
        risk_guard = RiskGuardian()
        # Simulamos un trade en EURUSD con SL de 10 pips
        dummy_entry = 1.10000
        dummy_sl = 1.09900
        # Args: symbol, entry, sl, risk_pct (1%), balance
        lots = risk_guard.calculate_lot_size("EURUSD", dummy_entry, dummy_sl, 0.01, balance)
        
        if lots > 0:
            print_status("Risk Guardian", True, f"Lot Calc OK. (Risk 1% of ${balance:.2f} -> {lots} lots on EURUSD)")
        else:
            print_status("Risk Guardian", False, "Lot calculation returned 0!")
            all_systems_go = False
    
    # 3. TEST DE KILLZONE (Horario)
    current_hour = datetime.now().hour
    if current_hour in settings.KILLZONES:
        print_status("Killzone Timing", True, f"We are LIVE in a Killzone (Hour {current_hour})")
    else:
        # No es error critico, solo aviso
        print_status("Killzone Timing", True, f"Out of Killzone (Hour {current_hour}). Waiting for {settings.KILLZONES}")

    # 4. TEST TELEGRAM
    notifier = TelegramNotifier(token=settings.TELEGRAM_TOKEN, chat_id=settings.TELEGRAM_CHAT_ID)
    msg = "🚀 **PRE-FLIGHT CHECK PASSED**\n\nAll systems are GREEN. Ready for launch."
    try:
        notifier.send_alert(msg)
        print_status("Telegram Link", True, "Test message sent successfully.")
    except Exception as e:
        print_status("Telegram Link", False, f"Failed to send: {e}")
        all_systems_go = False

    bridge.shutdown()
    
    print("\n" + "="*40)
    if all_systems_go:
        print("✅✅✅ SYSTEM READY FOR 72H LAUNCH ✅✅✅")
    else:
        print("❌❌❌ SYSTEM CHECK FAILED - DO NOT LAUNCH ❌❌❌")
    print("="*40 + "\n")

if __name__ == "__main__":
    pre_flight_check()
