# /tests — тестирование (этап 4)

| Файл | Что содержит |
|---|---|
| `Team1_E4_API_proverka.postman_collection.json` | Коллекция Postman: 3 запроса к jsonplaceholder.typicode.com, 8 проверок кода и тела ответа (раздел 4.4) |
| `postman_run_2026-11-27.png` | Снимок прогона коллекции в Postman Runner 27.11.2026: 8 из 8 проверок пройдены |
| `test-cases.md` | 48 тест-кейсов (TC-001…TC-060, TC-201…TC-204) и 10 тест-кейсов НФТ (TC-101…TC-110) со статусами |
| `bug-reports.md` | 8 баг-репортов BUG-001…BUG-008 |
| `screenshots/` | Снимки экрана к баг-репортам |
| `run_prototype_tests.js` | Скрипт Playwright: прогон тест-кейсов на HTML-прототипе |
| `katalog_TC.md` | Каталог всех номеров TC-001…TC-070 и TC-101…TC-110 из этапа 2, включая истории Should и Could |

## Как запустить коллекцию Postman

1. Откройте Postman (приложение или web.postman.co).
2. Нажмите **Import** и выберите файл коллекции.
3. Откройте коллекцию и нажмите **Run** → **Run Team1_E4_API_proverka**.
4. Проверьте результат: Passed 8, Failed 0.

## Как запустить прогон прототипа

1. Установите Node.js и Playwright (`npm i playwright`, затем `npx playwright install chromium`).
2. Выполните: `node run_prototype_tests.js ../prototype/prototype.html v3`.
3. Скрипт печатает статус каждого тест-кейса и сохраняет снимки экрана.
