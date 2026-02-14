# 🏷️ Consulta Preço - E-commerce Monitor

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Automator-45ba4b?style=for-the-badge&logo=playwright&logoColor=white)

> **Status:** 🟢 V1.0 - Estável (Kabum & Pichau)

Este projeto é uma solução de Engenharia de Dados focada em **Web Scraping de Alta Performance** para monitoramento de preços de hardware em e-commerces brasileiros.

A arquitetura foi desenhada para resistir a bloqueios (WAF/Cloudflare) e garantir a integridade dos dados via **Upsert** no banco relacional.

---

## 🚀 Funcionalidades (v1.0)

- **🕷️ Multi-Site Scraping:** Suporte nativo para **Kabum** e **Pichau**.
- **🛡️ Anti-Bot Evasion:**
  - Uso de perfis persistentes do Chrome para contornar Cloudflare.
  - Injeção de JavaScript (`page.evaluate`) para extração em massa (redução de latência de 40s para <1s).
- **💾 Persistência Robusta:**
  - Banco de dados **PostgreSQL**.
  - Estratégia de **Bulk Upsert** (COPY + Temp Table + ON CONFLICT) para evitar duplicatas e garantir performance.
- **⚙️ Configuração Dinâmica:** Gerenciamento de ambientes (`dev` vs `prd`) via variáveis de ambiente.

---

## 🛠️ Tech Stack

- **Linguagem:** Python 3.11+
- **Automação:** Playwright (Sync API)
- **Banco de Dados:** PostgreSQL (Driver: `psycopg` v3 - Binary Protocol)
- **Parsers:** Regex & DOM Manipulation via JS Injection
- **Logging:** `logging` com rotação de arquivos (`RotatingFileHandler`)

---

## 📂 Estrutura do Projeto

```bash
consulta_preco/
├── chrome_perfil/       # Sessão persistente (Ignorado no Git)
├── logs/                # Logs de execução e Debug HTML
├── src/
│   └── consulta_ecom/
│       ├── clients/     # Protocolos e Dataclasses
│       ├── config/      # Carregamento de .env
│       ├── db/          # Gerenciador de Conexão e Upsert
│       ├── sites/       # Lógica de Scraping (Kabum/Pichau)
│       └── utils/       # Loggers e Helpers
├── .env                 # Variáveis de ambiente (Segredos)
├── run_kabum.py         # Entrypoint Kabum
├── run_pichau.py        # Entrypoint Pichau
└── setup_perfil.py      # Script de setup de sessão humana