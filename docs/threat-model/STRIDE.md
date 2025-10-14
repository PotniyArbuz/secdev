# STRIDE — Угрозы для Habit Tracker

| Поток/Элемент | Угроза (STRIDE) | Описание угрозы | Контроль | Ссылка на NFR | Проверка/Артефакт |
|---------------|------------------|-----------------|----------|---------------|-------------------|
| F1 (User → BFF) | S: Spoofing | Подделка пользователя (невалидный token) | JWT validation + rate-limit | NFR-01 (Auth) | Unit-тесты в test_habits.py; CI pytest |
| F1 (User → BFF) | T: Tampering | Изменение запроса (man-in-the-middle) | HTTPS/TLS 1.3 | NFR-01 (Auth) | SSL scan in CI (trivy) |
| F2 (BFF → API) | R: Repudiation | Отказ от запроса (no logs) | Correlation ID in logs | NFR-07 (Logging) | Log monitoring in CI |
| F3 (API → DB) | I: Information Disclosure | Утечка PII из DB | Encryption at rest (SQLite PRAGMA) | NFR-06 (Vulnerabilities) | Security scan in CI (dependabot) |
| F3 (API → DB) | D: Denial of Service | SQL injection или overload DB | Input validation + query limits | NFR-03 (Validation), NFR-04 (Performance) | ZAP baseline scan in CI |
| F4 (API → Auth) | E: Elevation of Privilege | Escalation via weak auth | Owner-only check in API | NFR-02 (Owner-only) | Unit-тесты в test_habits.py |
| F5 (API → Monitoring) | S: Spoofing | Фальшивые метрики | mTLS for monitoring | NFR-01 (Auth) | Network policy in CI |
| F6 (DB → Storage) | T: Tampering | Изменение бэкапа | Signed backups | NFR-06 (Vulnerabilities) | Integrity check in CI |
| API (Overall) | R: Repudiation | Нет аудита действий | Audit logs for CRUD | NFR-07 (Logging) | Log anaalysis in CI |
| DB (Overall) | I: Information Disclosure | Leak via error messages | Mask PII in errors | NFR-05 (Errors) | Contract tests in pytest |
