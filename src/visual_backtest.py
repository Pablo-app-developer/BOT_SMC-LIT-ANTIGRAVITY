import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import sys
import os

# Add parent dir to sys path for settings if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import settings

def draw_spectacular_trade(df, trade_data, output_file="trade_audit.png"):
    """
    Genera un gráfico estilo TradingView 'Elite Dark Mode' con:
    - Fondo Oscuro (#131722)
    - Etiquetas de Liquidez estilo TV (Badge a la derecha)
    - Killzones Sutiles
    - Panel de Info Flotante
    - DETECCIÓN DE FAIR VALUE GAPS (FVG)
    """
    # 0. Validación de Datos
    if df is None or df.empty: return
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    # --- CONFIGURACIÓN DE ESTILO TRADINGVIEW DARK ---
    mc = mpf.make_marketcolors(up='#089981', down='#f23645', edge='inherit', wick='inherit', volume='in')
    s = mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=mc, 
                           gridstyle=':', gridcolor='#2a2e39', facecolor='#131722', 
                           edgecolor='#2a2e39', figcolor='#131722',
                           rc={
                               'font.family': 'sans-serif', 
                               'font.size': 10,
                               'axes.labelsize': 11,
                               'axes.labelcolor': '#d1d4dc',
                               'xtick.color': '#d1d4dc',
                               'ytick.color': '#d1d4dc',
                               'axes.edgecolor': '#2a2e39'
                           })

    # Usamos las últimas 200 velas para contexto
    plot_df = df.tail(200).copy()
    
    # Label for Timeframe
    tf_label = settings.TIMEFRAME_LTF
    symbol = trade_data.get('symbol', 'UNKNOWN')
    action = trade_data.get('action', 'ACTION')
    title_text = f"\n{symbol}  •  {tf_label}  •  {action}"

    # Creamos la figura con espacio para etiquetas a la derecha
    fig, axlist = mpf.plot(
        plot_df, type='candle', style=s, 
        title=title_text,
        ylabel='Price', figsize=(16, 10), returnfig=True,
        tight_layout=True, xrotation=0, datetime_format='%d %H:%M',
        volume=False
    )
    ax = axlist[0]
    ax.set_title(title_text, color='#d1d4dc', fontsize=16, fontweight='bold')
    ax.yaxis.label.set_color('#d1d4dc')

    # --- 0. MARCA DE AGUA (WATERMARK) ---
    ax.text(0.5, 0.5, "🚀 ANTIGRAVITY AI", transform=ax.transAxes,
            fontsize=50, color='#eceff1', alpha=0.08,
            ha='center', va='center', rotation=0, fontweight='bold')

    # --- 1. DIBUJO DE FVG (FAIR VALUE GAPS) ---
    # Analizamos las velas visibles para encontrar desequilibrios
    # Un FVG es el hueco entre la mecha de la vela i-2 y la vela i
    
    start_fvg_scan = 2
    
    opens = plot_df['Open'].values
    highs = plot_df['High'].values
    lows = plot_df['Low'].values
    closes = plot_df['Close'].values
    
    # Limitamos FVGs a las ultimas 50 velas para no saturar
    scan_start_idx = max(start_fvg_scan, len(plot_df) - 60)
    
    for i in range(scan_start_idx, len(plot_df)):
        width_box = min(15, len(plot_df)-i) # Definición Global para el bucle
        
        # BULLISH FVG (Gap Alcista)
        if lows[i] > highs[i-2]:
            top = lows[i]
            bottom = highs[i-2]
            # Caja más brillante (Alpha 0.3) y color Neon
            rect = mpatches.Rectangle((i-2, bottom), width_box, top - bottom, 
                                      color='#00e676', alpha=0.25, linewidth=0)
            ax.add_patch(rect)
            
            # Etiqueta
            if i > len(plot_df) - 30: # Solo etiquetar los muy recientes
                ax.text(i, (top+bottom)/2, "FVG", color='#00e676', fontsize=7, fontweight='bold', va='center', ha='left')
            
        # BEARISH FVG (Gap Bajista)
        elif highs[i] < lows[i-2]:
            top = lows[i-2]
            bottom = highs[i]
            rect = mpatches.Rectangle((i-2, bottom), width_box, top - bottom, 
                                      color='#ff1744', alpha=0.25, linewidth=0)
            ax.add_patch(rect)
            
            # Etiqueta
            if i > len(plot_df) - 30:
                ax.text(i, (top+bottom)/2, "FVG", color='#ff1744', fontsize=7, fontweight='bold', va='center', ha='left')

    # --- 2. DIBUJO DE SESIONES (Sombreado Vertical) ---
    for i in range(len(plot_df)):
        dt = plot_df.index[i]
        hour = dt.hour
        
        # Killzone Londres (Azul Soft)
        if 8 <= hour < 12:
            ax.axvspan(i-0.5, i+0.5, color='#2962ff', alpha=0.08, linewidth=0)
        # Killzone NY (Naranja Soft)
        elif 13 <= hour < 17:
            ax.axvspan(i-0.5, i+0.5, color='#ff9800', alpha=0.08, linewidth=0)
        # Rango Asia (Gris/Caja)
        elif 0 <= hour < 8:
            ax.axvspan(i-0.5, i+0.5, color='#787b86', alpha=0.05, linewidth=0)

    # --- 3. NIVELES DE LIQUIDEZ CON ETIQUETAS ---
    # Usamos los datos reales pasados por el Analyst
    h_liq = trade_data.get('real_liq_high', 0.0)
    l_liq = trade_data.get('real_liq_low', 0.0)
    
    # Si no vienen del bot (o son 0), usamos los extremos VISIBLES del gráfico
    # para que siempre haya referencia.
    suffix = " (ALGO)"
    if h_liq == 0: 
        h_liq = plot_df['High'].max()
        suffix = " (SESSION)"
    if l_liq == 0: 
        l_liq = plot_df['Low'].min()

    # Dibujamos SIEMPRE
    ax.axhline(h_liq, color='#ff5252', linestyle='-', linewidth=1.5, alpha=0.8) # Rojo vibrante
    ax.text(len(plot_df)+1, h_liq, f' PDH{suffix} ', color='white', fontsize=9, fontweight='bold', va='center',
            bbox=dict(facecolor='#ff5252', alpha=1.0, edgecolor='none', boxstyle='square,pad=0.2'))

    ax.axhline(l_liq, color='#69f0ae', linestyle='-', linewidth=1.5, alpha=0.8) # Verde vibrante
    ax.text(len(plot_df)+1, l_liq, f' PDL{suffix} ', color='black', fontsize=9, fontweight='bold', va='center',
            bbox=dict(facecolor='#69f0ae', alpha=1.0, edgecolor='none', boxstyle='square,pad=0.2'))

    # --- 4. CAJA DE RIESGO/BENEFICIO (La "Caja de Trade") ---
    if trade_data:
        try:
            entry = float(trade_data.get('entry', 0))
            sl = float(trade_data.get('sl', 0))
            tp = float(trade_data.get('tp', 0))
            
            if entry > 0:
                idx_entry = len(plot_df) - 1 

                # Caja Profit (Verde)
                top_p, bot_p = max(entry, tp), min(entry, tp)
                rect_tp = mpatches.Rectangle((idx_entry, bot_p), 20, top_p - bot_p, 
                                             facecolor='#00e676', alpha=0.2, linewidth=0)
                ax.add_patch(rect_tp)

                # Caja Stop (Roja)
                top_s, bot_s = max(entry, sl), min(entry, sl)
                rect_sl = mpatches.Rectangle((idx_entry, bot_s), 20, top_s - bot_s, 
                                             facecolor='#ff1744', alpha=0.2, linewidth=0)
                ax.add_patch(rect_sl)

                # Flecha EXECUTION
                ax.annotate('EXECUTION', xy=(idx_entry, entry), xytext=(idx_entry-15, entry),
                            arrowprops=dict(facecolor='#d1d4dc', shrink=0.05, width=1.5, headwidth=6),
                            color='#d1d4dc', fontsize=10, fontweight='bold', va='center')

                # PANEL DE INFO
                rr_val = trade_data.get('rr', settings.RISK_REWARD_RATIO)
                info_text = (f"⚡ {trade_data.get('reason', 'SIGNAL')}\n"
                             f"RR: 1:{rr_val}\n"
                             f"Entry: {entry:.5f}")
                
                # Caja de texto flotante Dark
                props = dict(boxstyle='round,pad=0.5', facecolor='#1e222d', alpha=0.9, edgecolor='#2a2e39')
                ax.text(0.02, 0.05, info_text, transform=ax.transAxes, color='#d1d4dc',
                        fontsize=11, verticalalignment='bottom', bbox=props)
        except Exception as e:
            print(f"Error drawing trade items: {e}")

    # Títulos de Sesiones en la parte superior (Tipo Legend)
    ax.text(0.05, 0.96, "ASIA", transform=ax.transAxes, color='#90a4ae', fontsize=9, fontweight='bold')
    ax.text(0.12, 0.96, "LONDON", transform=ax.transAxes, color='#2979ff', fontsize=9, fontweight='bold')
    ax.text(0.20, 0.96, "NEW YORK", transform=ax.transAxes, color='#ffa726', fontsize=9, fontweight='bold')

    # Guardar
    try:
        fig.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='#131722')
        print(f"      [Visual] Elite FVG Chart saved: {output_file}")
    except Exception as e:
        print(f"      [Visual] Error saving chart: {e}")
    finally:
        plt.close(fig)

# Alias for compatibility if needed, but we will update main.py to call draw_spectacular_trade
def draw_professional_chart(df, output_file="audit.png"):
    draw_spectacular_trade(df, {}, output_file)
