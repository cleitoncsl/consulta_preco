from playwright.sync_api import sync_playwright
import time

# User-Agent FIXO e MODERNO (Chrome 122)
UA_FIXO = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

def capturar_sessao():
    print("🚀 Abrindo navegador para autenticação humana...")
    
    with sync_playwright() as p:
        # Lança o Chrome em modo VISÍVEL
        browser = p.chromium.launch(
            headless=False, 
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        
        # Cria contexto IDÊNTICO ao que o robô vai usar
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=UA_FIXO
        )
        page = context.new_page()

        # Tenta aplicar stealth se disponível (ajuda a passar mais rápido)
        try:
            from playwright_stealth import stealth_sync
            stealth_sync(page)
        except:
            pass

        print("👉 Acessando a Pichau...")
        page.goto("https://www.pichau.com.br/search?q=controle%20ps5", timeout=90000)

        print("\n" + "█"*60)
        print("⚡⚡ MISSÃO DO USUÁRIO (VOCÊ) ⚡⚡")
        print("1. Olhe para a janela do navegador.")
        print("2. Se aparecer 'Verificação de Segurança' (Cloudflare), CLIQUE NO QUADRADO.")
        print("3. Aguarde até ver os PRODUTOS (Controles) na tela.")
        print("4. Role a página um pouco para baixo.")
        print("5. SÓ DEPOIS DISSO, volte aqui e aperte ENTER.")
        print("█"*60 + "\n")
        
        input("Pressione ENTER aqui APÓS ver os produtos na tela...")

        # Salva o "Passaporte"
        context.storage_state(path="pichau_state.json")
        print("✅ Sessão salva com sucesso em 'pichau_state.json'!")
        
        browser.close()

if __name__ == "__main__":
    capturar_sessao()