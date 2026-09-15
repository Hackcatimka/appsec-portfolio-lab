# AppSec Portfolio Lab

Практический портфель по Application Security и DevSecOps: обезличенные разборы собственных публичных проектов и безопасная утилита для быстрой проверки защитных HTTP-заголовков сайта.

## Что внутри

- [`case-studies/chroniclebot.md`](case-studies/chroniclebot.md) — Telegram/Python + Cloudflare/Supabase web application;
- [`case-studies/crypto-market-alert-bot.md`](case-studies/crypto-market-alert-bot.md) — асинхронный Telegram-бот с WebSocket-потоками;
- [`case-studies/camp-management-platform.md`](case-studies/camp-management-platform.md) — FastAPI/Vue-система с ролями, файлами и платежами;
- [`src/siteposture`](src/siteposture) — MVP CLI для пассивного анализа HTTP response headers;
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
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Ответственное использование

Проверяйте только собственные системы или цели, на которые у вас есть явное разрешение. Подробные правила — в [`ETHICS.md`](ETHICS.md). Если обнаружены реальные персональные данные или действующие секреты, не публикуйте их в issue или case study: сначала ограничьте доступ, отзовите секреты и следуйте процедуре инцидента.

