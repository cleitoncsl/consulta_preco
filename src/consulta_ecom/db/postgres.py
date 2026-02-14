import sys
import os
from pathlib import Path

# --- BOOTSTRAP: AJUSTE DE CAMINHO ---
# Garante que o Python encontre a pasta 'src/consulta_ecom'
BASE_DIR = Path(__file__).resolve().parent
SRC_PATH = str(BASE_DIR / "src")

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

# --- IMPORTS SEM DB ---
try:
    from src.consulta_ecom.config.env import load_environment
    from src.consulta_ecom.sites.kabum import KabumClient
    print("✅ Módulos carregados com sucesso.")
except ModuleNotFoundError as e:
    print(f"❌ Erro de importação: {e}")
    sys.exit(1)

def main():
    # 1. Carrega variáveis de ambiente (QUERY, LIMIT, etc.)
    load_environment()
    
    query = os.getenv("QUERY", "controle ps5")
    limit = int(os.getenv("LIMIT", "20"))
    max_pages = int(os.getenv("MAX_PAGES", "2"))
    
    # Rodando com janela aberta (False) para você acompanhar o teste
    headless = False 

    # 2. Inicializa o Scraper da Kabum
    # Removida qualquer dependência de banco de dados aqui
    client = KabumClient(
        headless=headless,
        user_data_dir="./chrome_perfil", # Usa seu perfil de cookies
        verbose=True,
        page_size=100
    )

    print(f"\n🔎 Iniciando busca por: '{query}'")
    print(f"📄 Limite: {limit} produtos | Máximo de páginas: {max_pages}")
    print("-" * 50)

    # 3. Executa a extração
    products = client.search(query, limit=limit, max_pages=max_pages)

    # 4. Apenas exibe os resultados no terminal
    if products:
        print(f"\n🎯 Resultados Encontrados ({len(products)}):")
        print("=" * 60)
        for i, p in enumerate(products, 1):
            # Formatação limpa para leitura rápida
            print(f"{i:02d} | R$ {p.price if p.price else 'N/A':>8.2f} | {p.title[:60]}...")
            print(f"   🔗 URL: {p.url[:70]}...")
        print("=" * 60)
    else:
        print("\n⚠️ Nenhum produto foi extraído.")

if __name__ == "__main__":
    main()