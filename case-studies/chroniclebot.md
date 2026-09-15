# ChronicleBot — статический AppSec-разбор

Источник: [Hackcatimka/ChronicleBot](https://github.com/Hackcatimka/ChronicleBot), публичный snapshot ветки `main`.

## Архитектура и границы доверия

В репозитории находятся два продукта: Python Telegram-бот с PostgreSQL и web-приложение Cloudflare/vinext с Supabase Auth, D1 и внешними AI-провайдерами. Ключевые границы — Telegram user input, Supabase bearer identity, профильные данные D1, административный API и оплачиваемые AI-вызовы.

## Подтверждённые находки

| Severity | Находка | Корень проблемы | Рекомендация |
|---|---|---|---|
| Medium | Cross-profile повреждение связей moment-goal | Ownership-проверенный `UPDATE` может затронуть 0 строк, но после него выполняется `DELETE` связей только по `moment_id` | Проверять affected rows, ограничить delete через owned parent и выполнять замену атомарно |
| Medium | Неограниченное потребление AI capacity | Каждый аутентифицированный запрос вызывает оплачиваемого провайдера до учёта usage | До вызова атомарно резервировать per-user/global budget, concurrency и rate limits |
| Medium (условно) | Админ-авторизация доверяет email-заголовку | Неподписанный request header принимается как самостоятельная identity | Использовать валидированный Supabase ID/role либо подписанное edge assertion |
| Low | Protocol-relative open redirect после login | Проверка `startsWith('/')` принимает `//host` | Нормализовать URL и требовать точное совпадение origin |
| Low | Stored Telegram HTML в сообщении администратору | Feedback смешивается с доверенной HTML-разметкой без escaping | Экранировать substitutions либо отключать parse mode |

Условная находка с заголовком становится недостижимой, если доверенный edge гарантированно удаляет клиентскую копию и сам формирует проверенное значение. Это внешнее условие отсутствует в snapshot, поэтому confidence снижен.

Отправка дневникового текста во внешний AI до подтверждения сохранения отмечена как privacy-design рекомендация, а не как самостоятельная уязвимость: AI заявлен как основная функция, а политика, запрещающая такого обработчика, не предоставлена.

## Положительные контроли

- Supabase bearer token проверяется через user endpoint.
- Большинство D1 операций ограничены `profile_id` и используют bind-параметры.
- React выводит пользовательские строки как text nodes.
- В Telegram-коде есть корректный пример `html.escape`, который можно централизовать.


