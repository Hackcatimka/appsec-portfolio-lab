# Camp Management Platform — статический AppSec-разбор

Источник: [Hackcatimka/camp-management-platform](https://github.com/Hackcatimka/camp-management-platform), публичный snapshot ветки `main`.

Примечание о тестовых данных: владелец проекта подтвердил, что размещённый в репозитории пример сертификата полностью синтетический и не относится к реальному ребёнку. Поэтому он не считается утечкой PII и исключён из списка уязвимостей. Для предотвращения неоднозначности такие fixtures всё равно полезно явно маркировать как synthetic/test data.

## Подтверждённые находки

| Severity | Находка | Основная мера |
|---|---|---|
| Critical | Deploy-конфигурация по умолчанию включает полный `AUTH_BYPASS` | Default false; запрет запуска вне изолированного test env |
| Critical | Telegram login доверяет заявленному ID без проверки `initData` | Серверная HMAC+freshness проверка Telegram initData и безопасный account linking |
| High | Group code даёт roster-wide PII и mutation capability | Разделить узкие expiring invites; trainer auth и parent-child ownership |
| High | PayKeeper webhook fail-open при пустом token | Обязательная provider signature, replay protection и invoice binding |
| Medium | Pending placements admin endpoint без auth | Role dependency на весь admin router и anonymous-route test |
| Medium | Public uploads позволяют накопительное resource exhaustion | Rate/quota, cleanup старых объектов, pixel limits и bounded OCR workers |

## Положительные контроли

- JWT algorithm ограничен явно; refresh tokens хэшируются и ротируются.
- Signed file URLs используют HMAC, срок действия и path containment.
- Большинство parent/child/trainer операций применяют ownership filters.
- Загруженные изображения получают случайные имена и перекодируются.

