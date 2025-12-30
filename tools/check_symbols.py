
import MetaTrader5 as mt5
import pandas as pd

def find_symbols():
    if not mt5.initialize():
        print("MT5 Init Failed")
        return

    # Get all symbols
    symbols = mt5.symbols_get()
    
    print("\n🔍 BUSCANDO SÍMBOLOS DISPONIBLES EN TU BROKER...\n")
    
    # Filter keywords
    keywords = ['BTC', 'ETH', '100', '500', 'NAS', 'TEC', 'SPX', 'USD']
    found = []
    
    for s in symbols:
        for k in keywords:
            if k in s.name.upper():
                found.append(s.name)
                break
    
    # Sort and Print unique
    found = sorted(list(set(found)))
    
    print("--- RESULTADOS ---")
    for s in found:
        # Print info regarding path to help identify category
        print(f"✅ {s}")
        
    mt5.shutdown()

if __name__ == "__main__":
    find_symbols()
