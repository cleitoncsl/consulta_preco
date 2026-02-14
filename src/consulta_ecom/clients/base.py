from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, List


@dataclass(frozen=True, slots=True)
class ProductItem:
    title: str
    price: Optional[float]
    url: str
    image: Optional[str] = None
    source: str = "unknown"
    page: int = 1


class BaseEcomClient(Protocol):
    def search(self, query: str, limit: int = 10, max_pages: int = 1) -> List[ProductItem]:
        ...
