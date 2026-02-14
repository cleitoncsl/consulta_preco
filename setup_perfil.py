from playwright.sync_api import sync_playwright
import os

# Define uma pasta local para salvar o perfil do navegador
USER_DATA_DIR = "./chrome_perfil"

def configurar_humano():
    print(f"🚀 Criando perfil persistente em: {USER_DATA_DIR}")
    
    with sync_playwright() as p:
        # Inicia um contexto persistente (como se fosse o seu Chrome oficial)
        # Isso salva cookies, cache e credenciais na pasta
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False, # Tem que ser visível
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled", # Esconde que é robô
                "--no-sandbox"
            ],
            viewport=None # Usa o tamanho real da janela
        )
        
        page = context.pages[0] # Pega a aba que já abriu
        
        print("👉 Acessando Pichau...")
        page.goto("https://www.pichau.com.br/search?q=controle%20ps5", timeout=90000)

        print("\n" + "█"*60)
        print("⚡ SUA MISSÃO ZEUS ⚡")
        print("1. Se a tela estiver BRANCA: Aperte F5 (Atualizar) até carregar.")
        print("2. Se tiver CAPTCHA: Resolva.")
        print("3. Navegue até ver os controles na tela.")
        print("4. VOLTE AQUI e aperte ENTER para gravar e sair.")
        print("█"*60 + "\n")
        
        input("Pressione ENTER após ver os produtos na tela...")
        
        context.close()
        print("✅ Perfil salvo! Agora o robô vai usar essa identidade.")

if __name__ == "__main__":
    configurar_humano()