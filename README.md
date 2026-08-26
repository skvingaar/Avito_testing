# UI-тесты платформы модерации

Автоматизация задания 2.2 выполнена на Python, pytest и Playwright. Покрыты фильтры цены и категории, сортировка цены в обоих направлениях, «Только срочные», управление таймером статистики и мобильное переключение темы.

Решение обязательного задания 1 по скриншоту находится в `SCREENSHOT_BUGS.md`, тест-кейсы UI — в `TESTCASES.md`, найденные на стенде дефекты — в `BUGS.md`.

## Запуск

Требуется Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
pytest --browser chromium
```

Для видимого браузера:

```bash
pytest --browser chromium --headed
```

Запуск только desktop- или mobile-сценариев:

```bash
pytest -m desktop
pytest -m mobile
```

При падении assertion pytest выводит ожидаемый результат и фактические проблемные значения. Трассы и скриншоты pytest-playwright сохраняет согласно переданным параметрам командной строки, например:

```bash
pytest --tracing retain-on-failure --screenshot only-on-failure
```

Важно: прямое открытие `/stats` на Netlify возвращает 404, поэтому тест корректно переходит туда через SPA-ссылку главной страницы.

## Текущий результат

Известные воспроизводимые дефекты связаны с тестами через `pytest.mark.xfail(strict=True)`: если дефект неожиданно исчезнет, результат `XPASS(strict)` уронит прогон и потребует удалить устаревшую отметку. Подробности и ручное подтверждение дефектов приведены в `BUGS.md`.

Проверенный результат полного прогона на 26.08.2026: **7 passed, 2 xfailed**, exit code 0.
