from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

EnvName = Literal["dev", "prd"]


def load_environment() -> EnvName:
    """
    Carrega .env conforme ENV:
      - ENV=dev -> .env.dev
      - ENV=prd -> .env.prd
    fallback: .env (se existir)
    """
    root = Path(__file__).resolve().parents[3]  # .../src/consulta_ecom/config -> raiz do projeto
    env = (os.getenv("ENV") or "dev").strip().lower()
    if env not in ("dev", "prd"):
        env = "dev"

    candidates = [
        root / f".env.{env}",
        root / ".env",
    ]

    for p in candidates:
        if p.exists():
            load_dotenv(dotenv_path=p, override=True)
            return env  # type: ignore[return-value]

    return env  # type: ignore[return-value]
