# Configuration parameters for the bot
# Project Settings
PROJECT_NAME = "Antigravity Fusion Bot"
# SYMBOLS TO TRADE (Forex + Indices + Gold)
SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY",  # Majors
    "XAUUSD",                      # Gold
    "US500", "US100",              # Indices (SP500, Nasdaq - Check broker naming!)
    "BTCUSD"                       # Crypto (Optional)
]
TIMEFRAME_HTF = "H4"
TIMEFRAME_LTF = "M15"
TIMEFRAME_BURST = "M1"

# Risk Management
RISK_PER_TRADE = 0.01      # 1% Risk per trade
DAILY_LOSS_LIMIT = 0.03    # 3% Daily Hard Stop

# Golden Parameters (Optimized Dec 2025)
FIXED_SL_PIPS = 20         # 20 Pips Fixed Stop (Base)
RISK_REWARD_RATIO = 3.0    # 1:3 RR Strategy
MAX_DRAWDOWN_SESSION = 0.01

# Strategy Parameters
SWING_LOOKBACK = 1  # n=1 for micro-structure sensitivity (More signals)
TRAP_BOS_COUNT = 2  # Number of BOS to consider a trap

# Credentials
# OPCIÓN A: Escríbelas aquí directamente para pruebas rápidas (Reemplaza los valores).
# OPCIÓN B: Déjalas como están y usa un archivo .env para mayor seguridad (Recomendado para Docker).

import os
from dotenv import load_dotenv

# Carga variables del archivo .env si existe
load_dotenv()

# Intentamos leer de variables de entorno primero, si no existen, usa el valor por defecto (tu credencial)
# PASO 1: Reemplaza los valores por defecto aquí abajo con tus datos reales de MT5:
MT5_LOGIN = int(os.getenv("MT5_LOGIN", 5044231636))          # <--- Pon tu ID de cuenta aquí (ej: 12345678)
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "Qb_gMsN8")        # <--- Pon tu contraseña aquí
MT5_SERVER = os.getenv("MT5_SERVER", "MetaQuotes-Demo")            # <--- Pon tu servidor aquí (ej: "MetaQuotes-Demo")
