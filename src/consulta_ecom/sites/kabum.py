from __future__ import annotations

import re
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote

from playwright.sync_api import sync_playwright, Page

from src.consulta_ecom.clients.base import ProductItem
from src.consulta_ecom.utils.logger import setup_logger


STOPWORDS_PT = {
    "de", "da", "do", "das", "dos", "para", "com", "sem", "e", "ou", "a", "o", "as", "os",
}


def _norm_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _slug_kabum(query: str) -> str:
    q = _norm_spaces(query).upper().replace(" ", "-")
    return quote(q, safe="-")


def _extract_float_price(text: str) -> Optional[float]:
    if not text:
        return None
    m = re.search(r"(\d{1,3}(?:\.\d{3})*(?:,\d{2})|\d+(?:,\d{2}))", text)
    if not m:
        return None
    raw = m.group(1).replace(".", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def _keywords_from_query(query: str) -> List[str]:
    q = _norm_spaces(query).lower()
    return [p for p in re.split(r"[\s\-_/]+", q) if p and p not in STOPWORDS_PT]


def _is_relevant(title: str, query_keywords: List[str]) -> bool:
    t = (title or "").lower()

    blacklist = (
        "mídia", "media",
        "access",
        "carregamento", "carregador", "charging", "dock", "base",
        "suporte", "stand",
        "cabo", "cable",
        "capa", "case", "skin", "silicone",
        "película", "pelicula",
        "adaptador", "adapter",
        "volante", "arcade",
    )
    if any(b in t for b in blacklist):
        return False

    has_controle = ("controle" in query_keywords) or ("control" in query_keywords)
    wants_ps = any(k in query_keywords for k in ("ps5", "playstation", "5"))

    if has_controle and wants_ps:
        is_dualsense = "dualsense" in t
        is_edge = "edge" in t
        is_wireless = ("sem fio" in t) or ("wireless" in t)
        mentions_ps = ("ps5" in t) or ("playstation" in t)
        return (is_dualsense or is_edge) or (("controle" in t) and is_wireless and mentions_ps)

    hits = sum(1 for k in set(query_keywords) if k in t)
    return hits >= min(2, max(1, len(set(query_keywords)) // 2))


def _safe_name(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_\-]+", "_", s.strip())
    return s[:80] if len(s) > 80 else s


def _url_hash(url: str) -> str:
    return hashlib.sha1((url or "").encode("utf-8")).hexdigest()


@dataclass
class KabumClient:
    # Browser
    headless: bool = True
    page_size: int = 100

    # Logs (parametrizados)
    verbose: bool = False                 # True -> DEBUG
    log_level: str = "INFO"               # INFO/DEBUG/WARNING/ERROR
    log_file: str = "logs/consulta_ecom.log"
    log_console: bool = True
    log_max_bytes: int = 2_000_000
    log_backup_count: int = 5

    # Debug artifacts
    debug_enabled: bool = True
    debug_dir: str = "logs/debug"

    # Controle de paginação/robustez
    zero_streak_stop: int = 2             # para após N páginas seguidas sem novos
    retry_if_links0: int = 1              # retries quando links_dom=0

    def __post_init__(self) -> None:
        lvl = "DEBUG" if self.verbose else (self.log_level or "INFO")
        self.logger = setup_logger(
            name="KabumClient",
            level=lvl,
            log_file=self.log_file,
            console=self.log_console,
            max_bytes=self.log_max_bytes,
            backup_count=self.log_backup_count,
        )
        if self.debug_enabled:
            Path(self.debug_dir).mkdir(parents=True, exist_ok=True)

    def _goto(self, page: Page, url: str) -> None:
        self.logger.info(f"GET {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass

    def _kick_render(self, page: Page) -> None:
        try:
            page.wait_for_selector("a[href*='/produto/']", timeout=12000)
            return
        except Exception:
            pass

        for _ in range(5):
            page.mouse.wheel(0, 2600)
            page.wait_for_timeout(900)

        try:
            page.wait_for_selector("a[href*='/produto/']", timeout=12000)
        except Exception:
            pass

    def _dump_debug(self, page: Page, page_idx: int, tag: str, query: str) -> None:
        if not self.debug_enabled:
            return
        try:
            stamp = _safe_name(query)
            html_path = Path(self.debug_dir) / f"kabum_{stamp}_p{page_idx}_{tag}.html"
            html_path.write_text(page.content(), encoding="utf-8")
            self.logger.warning(f"DEBUG HTML salvo: {html_path}")

            png_path = Path(self.debug_dir) / f"kabum_{stamp}_p{page_idx}_{tag}.png"
            page.screenshot(path=str(png_path), full_page=True)
            self.logger.warning(f"DEBUG PNG salvo: {png_path}")

            try:
                self.logger.warning(f"DEBUG title: {page.title()}")
            except Exception:
                pass
        except Exception as e:
            self.logger.warning(f"Falha ao salvar debug: {e}")

    def _build_url_100(self, query: str, page_number: int) -> str:
        base = f"https://www.kabum.com.br/busca/{_slug_kabum(query)}"
        return (
            f"{base}"
            f"?page_number={page_number}"
            f"&page_size={self.page_size}"
            f"&facet_filters="
            f"&sort=most_searched"
            f"&variant=catalog"
        )

    def _extract_products_from_dom(
        self,
        page: Page,
        query_keywords: List[str],
        page_idx: int,
    ) -> tuple[List[ProductItem], int, int]:
        selector = "a[href*='/produto/']"
        anchors = page.locator(selector)
        links_dom = anchors.count()

        self.logger.debug(f'Seletor: "{selector}" | links_dom={links_dom}')

        items: List[ProductItem] = []
        seen_urls = set()
        filtered_out = 0

        for i in range(min(links_dom, 2500)):
            try:
                href = anchors.nth(i).get_attribute("href") or ""
            except Exception:
                continue

            if not href:
                continue
            if href.startswith("/"):
                href = "https://www.kabum.com.br" + href
            if "/produto/" not in href:
                continue

            if href in seen_urls:
                continue
            seen_urls.add(href)

            a = anchors.nth(i)

            title: Optional[str] = None
            for sel in ("h2", "h3", "[data-testid='product-title']", "span"):
                try:
                    title = a.locator(sel).first.inner_text(timeout=350)
                    title = _norm_spaces(title)
                    if title and len(title) >= 6:
                        break
                except Exception:
                    title = None

            if not title:
                title = _norm_spaces(a.get_attribute("title") or a.get_attribute("aria-label") or "")
            if not title:
                continue

            if not _is_relevant(title, query_keywords):
                filtered_out += 1
                continue

            img_url: Optional[str] = None
            try:
                img = a.locator("img").first
                img_url = img.get_attribute("src") or img.get_attribute("data-src")
            except Exception:
                img_url = None

            price: Optional[float] = None
            try:
                card = a.locator("xpath=ancestor::*[self::article or self::div][1]")
                price_text = card.inner_text(timeout=600)
                price = _extract_float_price(price_text)
            except Exception:
                price = None

            items.append(
                ProductItem(
                    title=title,
                    price=price,
                    url=href,
                    image=img_url or None,
                    source="kabum",
                    page=page_idx,
                )
            )

        return items, links_dom, filtered_out

    def search(self, query: str, limit: int = 10, max_pages: int = 1) -> List[ProductItem]:
        query = _norm_spaces(query)
        query_keywords = _keywords_from_query(query)

        self.logger.info(
            f"SEARCH query='{query}' | limit={limit} | max_pages={max_pages} | page_size={self.page_size} | headless={self.headless}"
        )

        results: List[ProductItem] = []
        seen_hashes = set()

        zero_streak = 0

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()

            for page_idx in range(1, max_pages + 1):
                url = self._build_url_100(query, page_idx)
                self.logger.info(f"Página {page_idx} | URL(100): {url}")

                self._goto(page, url)
                self._kick_render(page)

                items, links_dom, filtered_out = self._extract_products_from_dom(page, query_keywords, page_idx)

                # retry leve se veio 0 links
                retries = 0
                while links_dom == 0 and retries < self.retry_if_links0:
                    retries += 1
                    self.logger.warning(f"Página {page_idx}: links_dom=0 | retry {retries}/{self.retry_if_links0}")
                    self._goto(page, url)
                    self._kick_render(page)
                    items, links_dom, filtered_out = self._extract_products_from_dom(page, query_keywords, page_idx)

                if links_dom == 0:
                    self._dump_debug(page, page_idx, "links0", query)

                added = 0
                for it in items:
                    h = _url_hash(it.url)
                    if h in seen_hashes:
                        continue
                    seen_hashes.add(h)
                    results.append(it)
                    added += 1
                    if len(results) >= limit:
                        break

                self.logger.info(
                    f"Página {page_idx}: links_dom={links_dom} | capturados={len(items)} | novos={added} | filtrados={filtered_out} | acumulado={len(results)}"
                )

                if len(results) >= limit:
                    break

                if added == 0:
                    zero_streak += 1
                    self.logger.warning(f"Página {page_idx}: 0 novos | zero_streak={zero_streak}")
                    if zero_streak >= self.zero_streak_stop:
                        self.logger.warning("Parando: páginas seguidas sem novos itens.")
                        break
                else:
                    zero_streak = 0

            browser.close()

        self.logger.info(f"FINAL extraídos={len(results)} (limit={limit})")
        return results
