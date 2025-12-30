
# 📘 Manual de Usuario para Dummies: Antigravity Bot

¡Felicidades! Tienes en tus manos un algoritmo de trading profesional. No te asustes, usarlo es tan fácil como encender una licuadora. Sigue estos pasos.

---

## Paso 1: Encender el Motor (MetaTrader 5) 🏎️
Antes de nada, el bot necesita que **MetaTrader 5 esté abierto** en tu computadora.
1.  Abre MT5.
2.  Asegúrate de que estás logueado en tu cuenta (Demo o Real).
3.  Asegúrate de que las cotizaciones se mueven (tienes internet).
4.  **IMPORTANTE:** Activa el botón "AutoTrading" en la barra superior de MT5 (debe estar en verde ▶️).
5.  Ve a `Herramientas > Opciones > Asesores Expertos` y marca "Permitir trading algorítmico".

## Paso 2: Configurar tu Riesgo 💰
¿Cuánto quieres arriesgar?
1.  Ve a la carpeta del proyecto y abre el archivo `config/settings.py` con cualquier bloc de notas.
2.  Busca la línea: `RISK_PER_TRADE = 0.01`
    *   `0.01` significa 1% de tu cuenta por operación.
    *   Si quieres ser conservador, pon `0.005` (0.5%).
3.  Guarda el archivo.

## Paso 3: Arrancar el Bot 🚀
1.  Abre la terminal de comandos (CMD o PowerShell) en la carpeta del bot.
2.  Escribe el siguiente comando mágico y presiona ENTER:
    ```
    python src/main.py
    ```
3.  Si todo va bien, verás un mensaje verde: **"All systems GREEN. Entering main loop..."**

## Paso 4: ¿Qué está haciendo? 🤔
El bot te hablará en la pantalla negra (consola):
*   `. Heartbeat...`: El bot está vivo y vigilando. Todo bien.
*   `[i] Liquidity Range...`: Ha detectado zonas interesantes, pero aún no dispara.
*   `[$$$] ENTRY SIGNAL...`: ¡Acción! Ha encontrado una oportunidad.
*   `[V] ORDER FILLED!`: **¡Ya estás dentro del mercado!** Ve a tu MT5 y verás la operación abierta con su Stop Loss y Take Profit automáticos.

## Paso 5: Apagarlo 🛑
Cuando quieras irte a dormir o detener el trading:
1.  Ve a la pantalla negra donde corre el bot.
2.  Presiona `Ctrl + C` en tu teclado.
3.  El bot dirá "Shutdown signal received" y se apagará limpiamente.

---
## Preguntas Frecuentes

**¿Necesito tener la pantalla encendida?**
Sí. Si tu PC se duerme, el bot se duerme. Configura Windows para que "Nunca suspenda" si vas a dejarlo solo.

**¿Puedo cerrar la ventana negra?**
¡NO! Si la cierras, apagas el cerebro del bot. Minimízala, pero no la cierres.

**¿Puedo abrir operaciones manuales a la vez?**
Sí, el bot solo gestionará las suyas. Pero cuidado con el margen libre.

---
*¡Buena caza!* 🏹
