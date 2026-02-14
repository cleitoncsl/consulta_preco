import sys
import os
from pathlib import Path

# --- BOOTSTRAP ---
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from consulta_ecom.config.env import load_environment
from consulta_ecom.sites.pichau import PichauClient

def main():
    # 1. Carrega Ambiente
    env = load_environment()
    print(f"⚡ [PICHAU] Ambiente: {env.upper()}")

    # 2. Configurações
    query = os.getenv("QUERY", "controle ps5")
    limit = int(os.getenv("LIMIT", "10"))
    max_pages = int(os.getenv("MAX_PAGES", "3"))
    headless = os.getenv("HEADLESS", "false").lower() == "true" 

    # 3. Inicializa o Cliente
    # CORREÇÃO: USER_DATA_DIR deve ser maiúsculo conforme sua classe original
    client = PichauClient(
        headless=headless,
        USER_DATA_DIR="./chrome_perfil", 
        stealth_enabled=True,
        verbose=True
    )

    # 4. Executa
    print(f"🔎 Buscando: '{query}'...")
    products = client.search(query=query, limit=limit, max_pages=max_pages)

    # 5. Output
    print(f"\n✅ Encontrados: {len(products)}")
    for p in products:
        price_fmt = f"R$ {p.price:.2f}" if p.price else "N/A"
        print(f"[{price_fmt}] {p.title[:60]}... | {p.url}")

if __name__ == "__main__":
    main()