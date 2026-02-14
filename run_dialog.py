import sys
import os
from pathlib import Path

# --- CONFIGURAÇÃO DE CORES ---
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
YELLOW = "\033[93m"

def check_file(path, content=None):
    p = Path(path)
    if p.exists():
        print(f"{GREEN}✅ Arquivo encontrado: {path}{RESET}")
        return True
    else:
        print(f"{RED}❌ FALTANDO: {path}{RESET}")
        if content:
            print(f"{YELLOW}   -> Criando arquivo automaticamente...{RESET}")
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"{GREEN}   -> Arquivo criado com sucesso!{RESET}")
            return True
        return False

def main():
    print("🔍 --- INICIANDO DIAGNÓSTICO DE INFRAESTRUTURA ---\n")
    
    base_dir = Path(__file__).parent.resolve()
    src_dir = base_dir / "src"
    
    # 1. VERIFICA O SYS.PATH
    print(f"📂 Diretório Base: {base_dir}")
    if str(src_dir) not in sys.path:
        print(f"{YELLOW}⚠️  'src' não estava no path. Adicionando...{RESET}")
        sys.path.insert(0, str(src_dir))
    
    # 2. VERIFICA ARQUIVOS CRÍTICOS (E CRIA SE FALTAR)
    
    # Conteúdo do base.py
    code_base = """from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductItem:
    title: str
    price: Optional[float]
    url: str
    source: str
    image: Optional[str] = None
    page: int = 1
"""
    
    # Conteúdo do __init__.py da raiz
    code_init = ""

    # Checklist
    checks = [
        (src_dir / "consulta_ecom" / "__init__.py", code_init),
        (src_dir / "consulta_ecom" / "clients" / "__init__.py", code_init),
        (src_dir / "consulta_ecom" / "clients" / "base.py", code_base), # <--- AQUI É O PULO DO GATO
    ]

    all_ok = True
    for path, content in checks:
        if not check_file(path, content):
            all_ok = False

    print("\n🧪 --- TESTE DE IMPORTAÇÃO ---")
    try:
        from consulta_ecom.clients.base import ProductItem
        print(f"{GREEN}🚀 SUCESSO: O módulo 'ProductItem' foi importado corretamente!{RESET}")
    except ImportError as e:
        print(f"{RED}🔥 ERRO FATAL DE IMPORTAÇÃO: {e}{RESET}")
        print(f"   Sys.path atual: {sys.path}")
        all_ok = False
    except Exception as e:
        print(f"{RED}🔥 ERRO DESCONHECIDO: {e}{RESET}")
        all_ok = False

    if all_ok:
        print(f"\n{GREEN}✅ TUDO PRONTO! Agora você pode rodar 'python run_kabum.py'.{RESET}")
    else:
        print(f"\n{RED}❌ Ainda há erros. Verifique as mensagens acima.{RESET}")

if __name__ == "__main__":
    main()