import sys
import os
import time
from pathlib import Path

# --- CONFIGURAÇÃO DE INFRAESTRUTURA (Obrigatório vir antes dos imports locais) ---
BASE_DIR = Path(__file__).resolve().parent
SRC_PATH = str(BASE_DIR / "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# --- IMPORTS DO PROJETO ---
try:
    from consulta_ecom.clients.base import ProductItem
    from consulta_ecom.sites.kabum import KabumClient
    from consulta_ecom.config.env import load_environment
except ImportError as e:
    print(f"❌ Erro técnico de importação: {e}")
    sys.exit(1)

def main():
    load_environment()
    query = os.getenv("QUERY", "controle ps5")
    
    # --- CONFIGURAÇÃO DO MODO FANTASMA ---
    client = KabumClient(
        headless=True,  # <--- MODO FANTASMA: O site NÃO vai aparecer
        verbose=True
    )

    print(f"🚀 Iniciando varredura invisível (Headless) na Kabum...")
    print(f"🔎 Alvo: '{query}' | Meta: 5 páginas")
    print("-" * 70)

    start_time = time.time()
    
    try:
        # Executa a busca (limit=500 para garantir que ele tente as 5 páginas)
        products = client.search(query=query, limit=500, max_pages=5)
        
        duration = time.time() - start_time
        
        if products:
            print("\n" + "=" * 110)
            print(f"📊 RELATÓRIO FINAL: {len(products)} itens encontrados em {duration:.2f}s")
            print("=" * 110)
            print(f"{'PG':<3} | {'PREÇO (R$)':<12} | {'TÍTULO'}")
            print("-" * 110)
            
            # Mostra uma amostra dos resultados
            for p in products[:20]:
                price_fmt = f"{p.price:10.2f}" if p.price else "   ---    "
                print(f"{p.page:02d} | {price_fmt} | {p.title[:80]}")
            
            if len(products) > 20:
                print(f"... e outros {len(products) - 20} itens.")
            print("=" * 110)
        else:
            print("\n⚠️  Busca concluída, mas nenhum produto foi extraído.")

    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")

if __name__ == "__main__":
    main()