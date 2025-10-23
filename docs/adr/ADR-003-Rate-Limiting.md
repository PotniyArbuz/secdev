# ADR-003: Rate Limiting for /habits Endpoint

**Дата**: 2025-10-22  
**Статус**: Accepted

## Context
Эндпойнт `/habits` уязвим к брутфорсу или DoS-атакам (риск R1, P04). Нужно ограничить частоту запросов для защиты производительности (NFR-04). Альтернативы:  
- `fastapi-limiter` (зависимость от Redis, сложнее для SQLite).  
- Встроенный middleware в FastAPI (лёгкий, но менее гибкий).  
- Nginx rate limiting (внешний компонент, не для API).  

## Decision
Реализовать middleware в `src/app/main.py` для ограничения запросов на `/habits`:  
- Лимит: 50 запросов в минуту на IP.  
- Ошибка 429 в формате RFC 7807 (ADR-001) при превышении.  
Будет реализовано в будущем PR.  

## Consequences
**Плюсы**:  
- Закрывает риск R1 (брутфорс, P04).  
- Поддерживает NFR-04 (Performance).  
- Простое решение без внешних зависимостей.  
**Минусы**:  
- Требует доработки middleware.  
- Не масштабируется для распределённых систем.  
**Trade-offs**: Простота против масштабируемости.  

## Links
- NFR-04 (Performance, P03)  
- R1 (Брутфорс, P04)  
- F1 (User → BFF, P04)  
- tests/test_main.py::test_rate_limit_exceeded  
