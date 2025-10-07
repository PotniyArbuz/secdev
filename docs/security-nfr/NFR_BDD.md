Feature: Аутентификация пользователей (NFR-01)
  Scenario: Защищённый эндпойнт требует валидный token
    Given пользователь не авторизован (token отсутствует)
    When отправляется GET /habits
    Then возвращается 401 ошибка с "error": {"code": "http_error", "message": "Invalid token"}

Feature: Авторизация owner-only (NFR-02)
  Scenario: Доступ к чужим данным запрещён
    Given пользователь авторизован (user_id=1), но данные принадлежат user_id=2
    When отправляется GET /habits/1
    Then возвращается 404 ошибка с "error": {"code": "not_found", "message": "habit not found"}

Feature: Валидация periodicity (NFR-03)
  Scenario: Создание привычки с invalid periodicity
    Given пользователь авторизован
    When отправляется POST /habits с "periodicity": "invalid"
    Then возвращается 422 ошибка с "error": {"code": "validation_error", "message": "Periodicity must be 'daily' or 'weekly'"}

Feature: Производительность эндпойнтов (NFR-04)
  Scenario: p95 времени ответа для POST /habits ≤ 200 ms
    Given нагрузка 50 RPS на stage
    When запускается 5-минутный нагрузочный тест
    Then p95 времени ответа ≤ 200 ms
