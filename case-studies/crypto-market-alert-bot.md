# Crypto Market Alert Bot — статический AppSec-разбор

Источник: [Hackcatimka/crypto-market-alert-bot](https://github.com/Hackcatimka/crypto-market-alert-bot), публичный snapshot ветки `master`.

## Архитектура и границы доверия

Aiogram принимает команды пользователей, Binance/Bybit поставляют HTTPS/WSS market data, SQLite хранит настройки, а analyzer передаёт события одному Telegram notifier через общую asyncio-очередь.

## Подтверждённые находки

| Severity | Находка | Корень проблемы | Рекомендация |
|---|---|---|---|
| Medium | `.env` может попасть в Docker image | Документация создаёт `.env`, build context — корень, используется `COPY . .`, `.dockerignore` отсутствует | Добавить `.dockerignore`, копировать явные файлы, хранить секреты только runtime |
| Medium | `/top` блокирует event loop | Команда без throttling синхронно проходит все symbol buffers и создаёт новые списки | Кэшировать результат, вести rolling aggregates, добавить rate limit |
| Medium | Неограниченная очередь уведомлений | Fan-out user×symbol пишет через `put_nowait` в queue без `maxsize`, consumer один | Bounded queue, coalescing, budgets и ограниченная конкурентность отправки |

## Положительные контроли

- Настройки всегда привязаны к `message.from_user.id`; cross-user ID не принимается.
- SQL values параметризованы, динамические поля ограничены allowlist.
- Exchange endpoints зафиксированы как HTTPS/WSS и имеют timeouts.
- Бот не хранит exchange credentials и не исполняет сделки.


