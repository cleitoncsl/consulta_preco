# 📦 Consulta Preço E-commerce (Core Infrastructure)

**Engine de alta fidelidade para mineração de dados e inteligência de mercado em tempo real.**

[cite_start]Esta plataforma foi desenvolvida com foco em **estabilidade de rede**, **evasão de bloqueios (Anti-Bot)** e **padronização de dados** entre múltiplos marketplaces. [cite_start]A arquitetura utiliza o padrão **Src Layout**, garantindo o isolamento total da lógica de negócio em relação à infraestrutura de execução.

---

## 🏗️ 1. Arquitetura do Sistema e Design Patterns

[cite_start]O projeto foi estruturado para resolver problemas comuns de escalabilidade e importações circulares em Python.



### Componentes de Infraestrutura:
* [cite_start]**`src/consulta_ecom/clients/base.py`**: Contrato mestre `ProductItem`. [cite_start]Todos os crawlers (Kabum, Pichau, etc.) herdam este esquema, garantindo que o downstream (DBs ou APIs) receba dados normalizados.
* [cite_start]**`src/consulta_ecom/sites/`**: Camada de implementação por domínio. [cite_start]Cada módulo é um "especialista" em um DOM específico, protegendo o core do sistema contra mudanças repentinas no layout dos sites.
* [cite_start]**`src/consulta_ecom/utils/logger.py`**: Wrapper customizado sobre o `loguru` para auditoria técnica, logs rotativos e diagnóstico de falhas em tempo real.

---

## 🛡️ 2. Táticas de Evasão e Resiliência (Anti-Bot)

Para mitigar bloqueios de segurança, implementamos um conjunto de estratégias de "Guerra Eletrônica":

* **Playwright Stealth Integration**: Injeção de scripts no cabeçalho do navegador para mascarar propriedades de automação (ex: `navigator.webdriver`), fazendo o robô parecer um usuário orgânico.
* [cite_start]**Modo Tanque (Hard Wait Strategy)**: Sincronização forçada com o ciclo de vida de frameworks modernos (React/Next.js). [cite_start]O scraper aguarda a hidratação total do DOM antes de disparar a extração de dados.
* **Headless Engine (Modo Fantasma)**: Otimização de recursos através da execução sem interface gráfica, permitindo alta performance em ambientes Docker e servidores Linux.

---

## 📊 3. Modelo de Dados Normalizado (`ProductItem`)

Independente da fonte, os dados são convertidos para o seguinte esquema técnico:

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `title` | `str` | Nome completo higienizado (sem caracteres especiais de controle). |
| `price` | `float` | Valor numérico à vista (Float padrão IEEE 754). |
| `url` | `str` | Link absoluto (Deep Link) para a página de checkout. |
| `image` | `str` | URL da imagem de capa (CDN Original). |
| `source` | `str` | Identificador da fonte (ex: `kabum`, `pichau`). |
| `page` | `int` | Índice da página onde o item foi localizado. |

---

## ⚙️ 4. Gestão de Ambiente e Portabilidade

O projeto utiliza variáveis de ambiente (`.env`) para desacoplar a configuração do código:

```env
# Configurações de Busca
QUERY="controle ps5 dualsense"

# Infraestrutura de Log
LOG_LEVEL="DEBUG"
LOG_TO_FILE=True