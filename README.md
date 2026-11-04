# Предзаказ обеда в университетской столовой

Учебный проект курса «Программная инженерия», Университет Пучон в Ташкенте, 2026.

Сервис даёт студенту заказать и оплатить обед заранее и забрать его по коду в выбранную перемену. Столовая получает список заказов по окнам и учёт продаж.

## Команда 1

| Роль | Участник |
|---|---|
| A — Product Owner и бизнес-аналитик | Шашкина Виктория |
| B — Системный аналитик и UX-дизайнер | Алиев Салим |
| C — Менеджер проекта и QA-инженер, капитан | Фаткулбаянов Руслан |

Преподаватель: Ботиров С. Р.

## Ссылки

- **Проектная работа, главы 1–3 (промежуточный контроль, PDF):** [docs/Team1_PK_Proektnaya_rabota_short_v1.pdf](docs/Team1_PK_Proektnaya_rabota_short_v1.pdf) — сокращённая версия для сдачи, 40 страниц.
- **Полная версия проектной работы (основа, 104 страницы):** [docs/Team1_PK_Proektnaya_rabota_v1.pdf](docs/Team1_PK_Proektnaya_rabota_v1.pdf)
- Презентация промежуточного контроля (PDF, 22 слайда): [docs/Team1_PK_Prezentaciya.pdf](docs/Team1_PK_Prezentaciya.pdf)
- Текст спикеров к презентации (PDF): [docs/Tekst_spikerov_PK_prezentaciya.pdf](docs/Tekst_spikerov_PK_prezentaciya.pdf)
- Новая смета от 04.11.2026 (PDF): [docs/smeta/Team1_Smeta_pereschet_v1.pdf](docs/smeta/Team1_Smeta_pereschet_v1.pdf), расчёт: [docs/smeta/smeta.md](docs/smeta/smeta.md)
- Глава 2 «Требования» (PDF): [docs/Team1_E2_Trebovaniya_v1.pdf](docs/Team1_E2_Trebovaniya_v1.pdf)
- Глава 3 «Проектирование» (PDF): [docs/Team1_E3_Proektirovanie_v1.pdf](docs/Team1_E3_Proektirovanie_v1.pdf)
- Модели этапа 3 (BPMN, UML, схема БД, архитектура): [models/](models/README.md)
- SQL-скрипт схемы базы данных: [models/schema.sql](models/schema.sql)
- Кликабельный прототип и экраны: [prototype/](prototype/README.md)
- Доска задач Trello: <ссылка>
- Папка Google Drive: https://drive.google.com/drive/folders/1GGYt6Z5PvZKHjVVLYaZPQQOUNuQwBNzI (доступ даёт капитан команды)
- Прототип Figma: https://www.figma.com/proto/rmpJx3sDMnKO9yX4EyJlqL/?node-id=1-2&starting-point-node-id=1%3A2&scaling=scale-down&content-scaling=fixed&page-id=0%3A1 (открывается без входа; исходный файл: https://www.figma.com/design/rmpJx3sDMnKO9yX4EyJlqL)
- Опрос Google Forms: <ссылка>

## Структура

| Папка | Что внутри |
|---|---|
| `/docs` | Документы: проектная работа (главы 1–3), презентация, текст спикеров, смета (`docs/smeta`) |
| `/models` | Матрица влияния, карта пути, BPMN, UML, схема БД (SQL, DBML), архитектура |
| `/prototype` | Ссылка на Figma, экраны PNG, кликабельный прототип HTML, инструкция по сборке в Figma |
| `/tests` | Список тест-кейсов TC-001…TC-070 и TC-101…TC-110 |
| `/team` | Устав команды, роли, правила работы |

## Правило коммитов

Каждый участник делает хотя бы один коммит через GitHub Desktop. Сообщение коммита: что изменено и в каком разделе, например `2.5: добавлены НФТ-01…10`.
