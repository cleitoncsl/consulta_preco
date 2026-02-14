from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote_plus, urljoin

from playwright.sync_api import sync_playwright, Page
from consulta_ecom.clients.base import ProductItem
from consulta_ecom.utils.logger import setup_logger

# ==========================================================
# UTILITÁRIOS
# ==========================================================
def _norm_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def _extract_float_price(text: str) -> Optional[float]:
    if not text: return None
    # Busca R$ 1.000,00 ou 1.000,00
    m = re.search(r"R\$\s?(\d{1,3}(?:\.\d{3})*(?:,\d{2})|\d+(?:,\d{2}))", text)
    if not m:
        m = re.search(r"(\d{1,3}(?:\.\d{3})*(?:,\d{2})|\d+(?:,\d{2}))", text)
    if not m: return None
    raw = m.group(1).replace(".", "").replace(",", ".")
    try: return float(raw)
    except ValueError: return None

def _keywords_from_query(query: str) -> List[str]:
    q = _norm_spaces(query).lower()
    return [p for p in re.split(r"[\s\-_/]+", q) if p and len(p) >= 2]

def _is_relevant(title: str, query_keywords: List[str]) -> bool:
    t = (title or "").lower()
    blacklist = ("mídia", "media", "access", "carregador", "dock", "base", "suporte", "cabo", "capa", "case", "película", "skin", "adesivo", "borracha", "ventoinha")
    if any(b in t for b in blacklist): return False
    
    if "controle" in query_keywords:
        return "controle" in t or "dualsense" in t or "joystick" in t
    return True

@dataclass
class PichauClient:
    headless: bool = False
    page_size: int = 36
    user_agent: Optional[str] = None
    stealth_enabled: bool = True
    verbose: bool = False
    log_level: str = "INFO"
    log_file: str = "logs/consulta_ecom.log"
    log_console: bool = True
    debug_enabled: bool = True
    debug_dir: str = "logs/debug"
    
    BASE_URL: str = "https://www.pichau.com.br"
    USER_DATA_DIR: str = "./chrome_perfil"

    def __post_init__(self) -> None:
        lvl = "DEBUG" if self.verbose else self.log_level
        self.logger = setup_logger("PichauClient", level=lvl, log_file=self.log_file, console=self.log_console)

    def search(self, query: str, limit: int = 10, max_pages: int = 1) -> List[ProductItem]:
        results: List[ProductItem] = []
        
        if not Path(self.USER_DATA_DIR).exists():
            self.logger.critical(f"🛑 Perfil '{self.USER_DATA_DIR}' não encontrado. Rode setup_perfil.py.")
            return []

        self.logger.info(f"🔓 Usando Perfil Persistente...")

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=self.USER_DATA_DIR,
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
                viewport=None
            )
            
            page = context.pages[0] if context.pages else context.new_page()

            for page_idx in range(1, max_pages + 1):
                url = f"{self.BASE_URL}/search?q={quote_plus(query)}&p={page_idx}"
                self.logger.info(f"Página {page_idx}: {url}")
                
                try:
                    page.goto(url, wait_until="commit", timeout=30000)
                    try:
                        page.wait_for_selector("div.MuiCard-root", timeout=15000)
                    except:
                        pass # Segue mesmo se der timeout, tenta pegar o que tem
                    
                    # Scroll para carregar imagens e preços
                    for _ in range(4):
                        page.mouse.wheel(0, 800)
                        page.wait_for_timeout(500)

                except Exception as e:
                    self.logger.error(f"Erro navegação: {e}")
                    break

                # ALVO: Container do Card
                cards = page.locator("div.MuiCard-root")
                count = cards.count()
                self.logger.info(f"Cards na tela: {count}")

                for i in range(count):
                    try:
                        card = cards.nth(i)
                        
                        # Extração de Texto
                        text_content = card.inner_text()
                        
                        if "R$" not in text_content: 
                            continue

                        # --- ESTRATÉGIA HÍBRIDA DE LINK (A MÁGICA) ---
                        # Procura link dentro (querySelector) OU link pai (closest)
                        # Isso resolve o problema de timeout
                        href = card.evaluate("""element => {
                            const linkInside = element.querySelector('a');
                            if (linkInside) return linkInside.getAttribute('href');
                            
                            const linkWrapper = element.closest('a');
                            if (linkWrapper) return linkWrapper.getAttribute('href');
                            
                            return null;
                        }""")

                        if not href:
                            # self.logger.warning(f"Card {i} sem link. Pulando.")
                            continue

                        full_url = urljoin(self.BASE_URL, href)

                        # Extração de Título
                        # Tenta pegar h2, se não, pega do texto bruto
                        h2 = card.locator("h2")
                        if h2.count():
                            title = h2.first.inner_text()
                        else:
                            lines = [l for l in text_content.split('\n') if len(l) > 15]
                            title = lines[0] if lines else "Sem Título"
                        
                        title = _norm_spaces(title)

                        if not _is_relevant(title, _keywords_from_query(query)): 
                            continue

                        # Evita duplicatas
                        if any(p.url == full_url for p in results): continue

                        price = _extract_float_price(text_content)
                        
                        # Imagem
                        img_el = card.locator("img").first
                        img = img_el.get_attribute("src") if img_el.count() else None

                        results.append(ProductItem(
                            title=title, price=price, url=full_url, image=img, source="pichau", page=page_idx
                        ))

                        if len(results) >= limit: break
                    except Exception as e:
                        # self.logger.error(f"Erro processando card {i}: {e}")
                        continue
                
                self.logger.info(f"✅ Itens capturados: {len(results)}")
                if len(results) >= limit: break

            context.close()
            
        return results