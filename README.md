
# 🌌 Antigravity Fusion Bot v1.0

> **SMC + Liquidity Inducement Theorem (LIT) Automated Trading System**

Este bot es una implementación algorítmica de la estrategia "Fusion Concepts". Opera de forma autónoma identificando zonas de liquidez, esperando trampas de mercado (Sweeps) y ejecutando entradas cuando el precio reclama el rango previo.

## 🚀 Características Principales

*   **Lógica "Sweep & Reclaim":** No adivina techos ni suelos. Espera a que el mercado saque a los traders retail (Take Liquidity) y entra en la reversión confirmada.
*   **Multi-Activo:** Escanea simultáneamente una cesta de activos configurables (EURUSD, SP500, NASDAQ, ORO, etc.).
*   **Gestión de Riesgo "Risk Guardian":** Calcula el tamaño del lotaje dinámicamente basado en el % de riesgo por operación (1%) y detiene el trading si se alcanza el límite de pérdida diaria (3%).
*   **Free Rolling:** Mueve automáticamente el Stop Loss a Breakeven.
*   **Optimizaciones Golden:** Calibrado estadísticamente con Stop Loss fijos de 20 pips y ratio Riesgo:Beneficio de 1:3.

## 📋 Requisitos

*   **Sistema Operativo:** Windows (Requerido para MetaTrader 5 Terminal).
*   **Software:**
    *   Python 3.10+
    *   MetaTrader 5 (Logueado en tu cuenta Broker).
*   **Librerías Python:** Ver `requirements.txt`.

## 🛠️ Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/Pablo-app-developer/BOT_SMC-LIT-ANTIGRAVITY.git
    cd BOT_SMC-LIT-ANTIGRAVITY
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar Credenciales:**
    *   Abre `config/settings.py`.
    *   Coloca tu Login, Password y Servidor de MT5 (o usa un archivo `.env` para mayor seguridad).

## ⚡ Ejecución

Asegúrate de tener tu terminal MetaTrader 5 abierta.

```bash
python src/main.py
```

El bot iniciará el ciclo:
1.  Conectará con MT5.
2.  Escaneará todos los símbolos definidos en `settings.py`.
3.  Imprimirá "[$$$] ENTRY SIGNAL" cuando ejecute una operación.

## 📊 Estrategia

*   **Identificación:** Ventana de Liquidez de 20 velas (Rolling Window).
*   **Trigger:** Cierre de vela contrario tras barrer liquidez (High/Low).
*   **Stop Loss:** 20 Pips (Adaptativo).
*   **Take Profit:** 60 Pips (1:3 RR).

---
*Desarrollado con ❤️ e IA por Pablo & Antigravity Agent.*
