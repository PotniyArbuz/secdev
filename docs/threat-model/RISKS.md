# RISKS — Реестр рисков для Habit Tracker

Оценка: L (вероятность 1..5), I (влияние 1..5), Risk = L×I

| RiskID | Описание                         | Связь (F/NFR) | L | I | Risk | Стратегия (принять/снизить/избежать/перенести) | Владелец | Срок  | Критерий закрытия                 |
|--------|----------------------------------|---------------|---|---|------|-----------|----------|-------|-----------------------------------|
| R1     | Брутфорс логина                  | F1, NFR-01    | 4 | 5 | 20   | Снизить   | @PotniyArbuz | 2025-10-20 | CI: rate-limit + негативные тесты |
| R2     | Утечка PII из DB                 | F3, NFR-06    | 3 | 5 | 15   | Снизить   | @PotniyArbuz | 2025-10-25 | Encryption at rest + SCA scan in CI |
| R3     | DoS от invalid запросов          | F3, NFR-04    | 3 | 4 | 12   | Снизить   | @PotniyArbuz | 2025-10-30 | Input validation + load test in CI |
| R4     | Escalation через weak auth       | F4, NFR-02    | 4 | 3 | 12   | Избежать  | @PotniyArbuz | 2025-10-15 | Unit-тесты owner-only + CI pytest |
| R5     | Фальшивые метрики                | F5, NFR-01    | 2 | 3 | 6    | Снизить   | @PotniyArbuz | 2025-11-01 | mTLS for monitoring + audit logs |
| R6     | Изменение бэкапа                 | F6, NFR-06    | 2 | 4 | 8    | Снизить   | @PotniyArbuz | 2025-11-05 | Signed backups + integrity check |
| R7     | Нет аудита действий              | API, NFR-07   | 3 | 3 | 9    | Снизить   | @PotniyArbuz | 2025-10-25 | Audit logs in CI + log analysis |
| R8     | Leak via error messages          | API, NFR-05   | 3 | 4 | 12   | Избежать  | @PotniyArbuz | 2025-10-20 | Mask PII in errors + contract tests |
