from playwright.sync_api import sync_playwright

def diagnosticar_dom():
    print("🕵️‍♂️ Iniciando Diagnóstico de Estrutura...")
    with sync_playwright() as p:
        # Usa o mesmo perfil que já funcionou
        context = p.chromium.launch_persistent_context(
            user_data_dir="./chrome_perfil",
            headless=False, # Precisa ver a tela
            viewport=None
        )
        page = context.pages[0]
        
        # Vai para a busca
        page.goto("https://www.pichau.com.br/search?q=controle%20ps5")
        page.wait_for_timeout(5000) # Espera 5s para garantir carregamento
        
        print("\n--- RELATÓRIO DO QUE O ROBÔ VÊ ---")
        
        # 1. Título da página (para ver se não caiu em erro)
        print(f"TITLE: {page.title()}")
        
        # 2. Contagem de Links Totais
        links = page.locator("a").count()
        print(f"LINKS TOTAIS NA PÁGINA: {links}")
        
        # 3. Testa seletores comuns da Pichau
        selectors = [
            "div[data-cy='product-card']",
            "div.product-item",
            "div.MuiCard-root",
            "a[href*='/p/']",
            "div:has-text('R$')"
        ]
        
        for sel in selectors:
            count = page.locator(sel).count()
            print(f"Seletor '{sel}': {count} encontrados")
            
        print("----------------------------------")
        context.close()

if __name__ == "__main__":
    diagnosticar_dom()