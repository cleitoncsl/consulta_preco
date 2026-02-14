import os
from pathlib import Path

# Define a raiz do projeto
ROOT_DIR = Path(__file__).parent
SRC_DIR = ROOT_DIR / "src"

# Lista de pastas que PRECISAM ter o __init__.py
required_paths = [
    SRC_DIR / "consulta_ecom",
    SRC_DIR / "consulta_ecom" / "clients",
    SRC_DIR / "consulta_ecom" / "config",
    SRC_DIR / "consulta_ecom" / "sites",
    SRC_DIR / "consulta_ecom" / "utils",
]

print(f"🔧 Verificando estrutura em: {ROOT_DIR}\n")

for folder in required_paths:
    if not folder.exists():
        print(f"❌ Pasta não encontrada (Crie-a primeiro): {folder}")
        continue
    
    init_file = folder / "__init__.py"
    
    if not init_file.exists():
        print(f"⚠️  Criando __init__.py em: {folder}")
        with open(init_file, "w") as f:
            f.write("# Pacote Python")
    else:
        print(f"✅ {folder.name} já tem __init__.py")

print("\n🚀 Estrutura corrigida! Tente rodar o run_kabum.py agora.")