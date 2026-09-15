# Remediation case study: fail-open authentication bypass

Проект: [Camp Management Platform](https://github.com/Hackcatimka/camp-management-platform)  
Тип работы: defensive static review; эксплуатация не проводилась  
Severity до исправления: **Critical**  
Статус: **предложено и покрыто regression-тестом в portfolio lab**

## Краткое резюме

Production compose задавал `AUTH_BYPASS` со значением `true`, если переменная окружения отсутствовала. Backend также имел небезопасный default и при включённом флаге возвращал bypass-пользователя до проверки bearer token. Проверка ролей отдельно доверяла тому же флагу.

В результате ошибка конфигурации превращалась не в отказ запуска, а в полное отключение двух независимых границ: authentication и authorization. Это классический fail-open control.

## Подтверждённый путь данных

```text
AUTH_BYPASS отсутствует в deploy environment
        ↓
docker-compose.prod.yml подставляет true
        ↓
Settings.AUTH_BYPASS == True
        ↓
get_current_user() возвращает bypass user без bearer token
        ↓
require_roles() пропускает проверку роли
        ↓
защищённый endpoint выполняется с привилегированным контекстом
```

Затронутые места snapshot-версии:

- `docker-compose.prod.yml`: backend и frontend bypass имели default `true`;
- `backend/app/core/config.py`: `AUTH_BYPASS: bool = True`;
- `backend/app/core/deps.py`: ранний возврат bypass user и пропуск role check.

## Security invariants

Исправление должно обеспечивать следующие свойства:

1. Отсутствующая настройка никогда не включает bypass.
2. Production, staging и неизвестное окружение отклоняют `AUTH_BYPASS=true` при старте.
3. Bypass возможен только в явно выбранном изолированном test environment.
4. Frontend-флаг не считается защитой и не влияет на server-side authorization.
5. Production image не содержит кода или учётных данных, создающих привилегированного bypass user.

## Предлагаемое исправление

Минимальный конфигурационный diff:

```diff
- AUTH_BYPASS: bool = True
+ AUTH_BYPASS: bool = False
```

```diff
- AUTH_BYPASS: ${AUTH_BYPASS:-true}
+ AUTH_BYPASS: ${AUTH_BYPASS:-false}
```

Этого недостаточно само по себе: при явной ошибочной переменной bypass снова включится. Поэтому приложение должно валидировать инвариант до открытия сетевого порта:

```python
if settings.AUTH_BYPASS and settings.ENV.strip().lower() != "test":
    raise RuntimeError("AUTH_BYPASS is forbidden outside isolated tests")
```

Исполняемый fail-closed пример находится в [`examples/remediation/auth_bypass_guard.py`](../examples/remediation/auth_bypass_guard.py).

## Regression verification

[`tests/test_auth_bypass_remediation.py`](../tests/test_auth_bypass_remediation.py) проверяет четыре случая:

| Environment | AUTH_BYPASS | Ожидаемый результат |
|---|---:|---|
| default (`production`) | `false` | успешный старт |
| `production` | `true` | отказ запуска |
| `staging` | `true` | отказ запуска |
| `test` | `true` | разрешено только явно |

Дополнительный integration-тест в исходном приложении должен запускать защищённый endpoint без bearer token и ожидать `401`, а с токеном недостаточной роли — `403`.

## Defense in depth

- удалить frontend bypass из production build arguments;
- собирать test-only dependency override только в отдельном test target;
- добавить deploy policy, запрещающую `AUTH_BYPASS=true`;
- проверить итоговую rendered compose-конфигурацию перед deploy;
- логировать только факт отказа конфигурации, не значения секретов;
- защищать main branch обязательными CI checks.

## Mapping

- CWE-1188 — Insecure Default Initialization of Resource;
- CWE-306 — Missing Authentication for Critical Function;
- CWE-862 — Missing Authorization;
- OWASP ASVS — authentication, access-control и secure-configuration requirements.

## Остаточный риск

Этот case study демонстрирует исправление конфигурационного инварианта, но не изменяет автоматически исходный Camp Management Platform. Статус можно перевести в **verified fixed** только после применения эквивалентного патча в исходном проекте и выполнения его integration-тестов.
