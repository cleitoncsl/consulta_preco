from __future__ import annotations

import os
import sys
from pathlib import Path

# ==========================================================
# BOOTSTRAP: adiciona /src no PYTHONPATH
# ==========================================================
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from consulta_ecom.config.env import load_environment
from consulta_ecom.sites.pichau import PichauClient


def _env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "sim", "y")


def _env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or not str(v).strip():
        return default
    try:
        return int(v)
    except ValueError:
        return default


def main():
    env = load_environment()
    print(f"🚀 Ambiente ativo: {env.upper()}")

    query = os.getenv("QUERY", "controle playstation 5")
    limit = _env_int("LIMIT", 200)
    max_pages = _env_int("MAX_PAGES", 7)

    # logs
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "logs/consulta_ecom.log")
    log_console = _env_bool("LOG_CONSOLE", True)
    verbose = _env_bool("VERBOSE", False)

    # debug
    debug_enabled = _env_bool("DEBUG_ENABLED", True)
    debug_dir = os.getenv("DEBUG_DIR", "logs/debug")

    headless = _env_bool("HEADLESS", True)
    user_agent = os.getenv("USER_AGENT")
    stealth_enabled = _env_bool("PICHAU_STEALTH", True)

    page_size = _env_int("PICHAU_PAGE_SIZE", 36)

    client = PichauClient(
        headless=headless,
        page_size=page_size,
        user_agent=user_agent,
        stealth_enabled=stealth_enabled,
        verbose=verbose,
        log_level=log_level,
        log_file=log_file,
        log_console=log_console,
        debug_enabled=debug_enabled,
        debug_dir=debug_dir,
    )

    items = client.search(query, limit=limit, max_pages=max_pages)

    print("\n================ RESULTADOS ================\n")
    print("Site: PICHAU")
    print(f"Busca: {query}")
    print(f"Encontrados: {len(items)}\n")

    for i, p in enumerate(items, start=1):
        print(f"{i:02d}. {p.title}")
        print(f"    Preço : {'R$ ' + str(p.price) if p.price is not None else 'N/A'}")
        print(f"    URL   : {p.url}")
        print(f"    Img   : {p.image}")
        print(f"    Pagina: {p.page}\n")


if __name__ == "__main__":
    main()
