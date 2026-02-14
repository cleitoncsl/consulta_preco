import sys
import os
from pathlib import Path

# --- BOOTSTRAP: Adiciona ./src ao path para o Python achar o consulta_ecom ---
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from consulta_ecom.config.env import load_environment
from consulta_ecom.sites.kabum import KabumClient

def main():
    # 1. Carrega Variáveis de Ambiente (.env)
    env = load_environment()
    print(f"⚡ [KABUM] Ambiente: {env.upper()}")

    # 2. Configurações
    query = os.getenv("QUERY", "controle ps5")
    limit = int(os.getenv("LIMIT", "10"))
    max_pages = int(os.getenv("MAX_PAGES", "3"))
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    
    # 3. Inicializa o Cliente Kabum
    # NOTA: O KabumClient NÃO usa 'user_data_dir' nem 'stealth_enabled'
    print(f"🔎 Iniciando busca na Kabum por: '{query}'")
    client = KabumClient(
        headless=headless,
        verbose=True,      # Mostra logs detalhados no console
        page_size=100      # Pega até 100 itens por página
    )

    # 4. Executa a Busca
    try:
        products = client.search(query=query, limit=limit, max_pages=max_pages)
    except Exception as e:
        print(f"❌ Erro durante a busca: {e}")
        return

    # 5. Exibe Resultados
    print(f"\n✅ Encontrados: {len(products)}")
    print("="*80)
    for i, p in enumerate(products, 1):
        price_fmt = f"R$ {p.price:.2f}" if p.price else "N/A"
        # Mostra Título, Preço e Link
        print(f"{i:02d}. [{price_fmt}] {p.title[:60]:<60} | {p.url}")
    print("="*80)

if __name__ == "__main__":
    main()