# ADR-001: Standardize Error Responses with RFC 7807

**Дата**: 2025-10-22  
**Статус**: Accepted

## Context
Habit Tracker API возвращает ошибки в неструктурированном формате, что может привести к утечке PII или стека (риск R8, P04). Нужно стандартизировать ошибки согласно RFC 7807, чтобы маскировать детали и добавлять `correlation_id` для аудита. Альтернативы:  
- Собственный формат JSON (меньше стандартизации, сложнее интеграция).  
- RFC 7807 (стандарт, поддержка в FastAPI/Starlette, проще логи).  
- Простой текст (не машином читаемый, не подходит).  

## Decision
Реализовать обработчик ошибок в формате RFC 7807 в `src/app/errors.py` с полями: `type`, `title`, `status`, `detail`, `correlation_id`. Все 4xx/5xx ошибки используют эту функцию. Пример: `{"type": "about:blank", "title": "Invalid input", "status": 422, "detail": "Periodicity must be 'daily' or 'weekly'", "correlation_id": "uuid"}`.  

## Consequences
**Плюсы**:  
- Маскирование PII и стека (закрывает R8, P04).  
- Упрощает аудит (NFR-07, P03).  
- Совместимость с клиентами (стандарт RFC 7807).  
**Минусы**:  
- Дополнительный код для обработки ошибок.  
- Нужно обновить все эндпойнты для использования `problem()`.  
**Trade-offs**: Увеличивает время разработки, но повышает безопасность и читаемость.  

## Links
- NFR-05 (Errors, P03)  
- R8 (Leak via error messages, P04)  
- F3 (API → DB, P04)  
- tests/test_errors.py::test_rfc7807_format  
