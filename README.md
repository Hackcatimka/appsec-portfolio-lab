# AppSec Portfolio Lab

[![CI](https://github.com/Hackcatimka/appsec-portfolio-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/Hackcatimka/appsec-portfolio-lab/actions/workflows/ci.yml)
[![CodeQL](https://github.com/Hackcatimka/appsec-portfolio-lab/actions/workflows/codeql.yml/badge.svg)](https://github.com/Hackcatimka/appsec-portfolio-lab/actions/workflows/codeql.yml)

Практический портфель по Application Security и DevSecOps: обезличенные разборы собственных публичных проектов и безопасная утилита для быстрой проверки защитных HTTP-заголовков сайта.

## Что внутри

- [`case-studies/chroniclebot.md`](case-studies/chroniclebot.md) — Telegram/Python + Cloudflare/Supabase web application;
- [`case-studies/crypto-market-alert-bot.md`](case-studies/crypto-market-alert-bot.md) — асинхронный Telegram-бот с WebSocket-потоками;
- [`case-studies/camp-management-platform.md`](case-studies/camp-management-platform.md) — FastAPI/Vue-система с ролями, файлами и платежами;
- [`src/siteposture`](src/siteposture) — MVP CLI для пассивного анализа HTTP response headers;
- [`remediations/camp-auth-bypass.md`](remediations/camp-auth-bypass.md) — полный remediation case study: причина, исправление, тесты и проверка;
- [`METHODOLOGY.md`](METHODOLOGY.md) и [`ETHICS.md`](ETHICS.md) — методика, ограничения и правила безопасного использования.

## Результаты первой ревизии

| Проект | Critical | High | Medium | Low |
|---|---:|---:|---:|---:|
| ChronicleBot | 0 | 0 | 3 | 2 |
| Crypto Market Alert Bot | 0 | 0 | 3 | 0 |
| Camp Management Platform | 2 | 2 | 2 | 0 |

Это статическая проверка текущих публичных snapshot-версий. Она не доказывает безопасность всего продукта и не включает эксплуатацию, fuzzing, подбор идентификаторов, сканирование инфраструктуры или анализ приватных репозиториев.

## SitePosture CLI

Локальный режим анализирует сохранённые заголовки без сетевого доступа:

```bash
python -m siteposture --headers-file examples/secure-headers.txt --scheme https --format markdown
```

Одноразовая проверка URL делает ровно один GET, не следует redirect и не отправляет тестовые payloads. Она требует явного подтверждения авторизации:

```bash
python -m siteposture --url https://example.org --authorized --format json
```

Установка для разработки:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
ruff check .
bandit -q -r src examples/remediation
```

## DevSecOps automation

Для каждого push и pull request GitHub Actions выполняет тесты на поддерживаемых версиях Python, lint и SAST-проверку. Отдельный CodeQL workflow анализирует Python-код при изменениях и по расписанию. Dependabot еженедельно проверяет Python-зависимости и используемые GitHub Actions.

Все workflows работают с минимальными permissions. Сетевой режим SitePosture в CI не запускается: автоматические проверки используют только локальные fixtures.

## Ответственное использование

Проверяйте только собственные системы или цели, на которые у вас есть явное разрешение. Подробные правила — в [`ETHICS.md`](ETHICS.md). Если обнаружены реальные персональные данные или действующие секреты, не публикуйте их в issue или case study: сначала ограничьте доступ, отзовите секреты и следуйте процедуре инцидента.
