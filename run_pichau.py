import sys
import os
from pathlib import Path

# BOOTSTRAP
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from consulta_ecom.config.env import load_environment
from consulta_ecom.sites.pichau import PichauClient
from consulta_ecom.db.postgres import DatabaseManager

def main():
    # 1. Carrega configs
    env = load_environment()
    print(f"⚡ [PICHAU] Ambiente: {env.upper()}")
    
    query = os.getenv("QUERY", "controle ps5")
    limit = int(os.getenv("LIMIT", "50"))
    max_pages = int(os.getenv("MAX_PAGES", "3"))
    
    # IMPORTANTE: Pichau deve rodar com headless=False para enganar o Cloudflare
    headless = False 

    # 2. Inicializa Banco
    db = DatabaseManager()
    db.init_db()

    # 3. Inicializa Cliente
    # CORREÇÃO: USER_DATA_DIR deve ser maiúsculo, conforme sua classe original
    user_profile = "./chrome_perfil"
    if not Path(user_profile).exists():
        print(f"⚠️  ALERTA: Pasta '{user_profile}' não encontrada. Rode 'setup_perfil.py' primeiro!")

    print(f"🔎 Buscando '{query}' na Pichau (Perfil Persistente)...")
    client = PichauClient(
        headless=headless,
        USER_DATA_DIR=user_profile,  # <--- CORREÇÃO AQUI
        stealth_enabled=True,
        verbose=True
    )

    # 4. Executa
    products = client.search(query, limit=limit, max_pages=max_pages)

    # 5. Salva e Mostra
    print(f"\n✅ Encontrados: {len(products)}")
    db.save_products(products)

    for p in products:
        print(f"R$ {p.price} | {p.title[:50]}...")

if __name__ == "__main__":
    main()