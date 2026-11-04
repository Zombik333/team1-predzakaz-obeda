"""Расчёт новой сметы «Предзаказ обеда» (задача 3 пересчёта).
Запуск: python3 smeta_calc.py  — печатает все промежуточные числа.
Документы smeta.md и docx строит smeta_doc.py из функции calc() этого файла.
Цены: ../market-prices.md, нагрузка и инфраструктура: ../load-infra.md.
Все суммы — в сумах. Курс: 1 USD = 11 911,71 сум (ЦБ РУз, 04.11.2026)."""
import math

USD = 11911.71
RATE = 100_000            # сум/ч: 87 121 (middle, центр, налоги) x 1,15 накладные = 100 189
RATE_STAFF_MID = 87_121
LV = ('low', 'base', 'high')
L3 = lambda a, b, c: dict(low=a, base=b, high=c)

# ---------- 1. Разработка: декомпозиция (часы middle-разработчика) ----------
# id, что делаем, приоритет, SP, число тест-кейсов, (низк., база, выс.), состав
STORIES = [
    ('US-01', 'Меню дня с ценой и остатком', 'Must', 3, 4, (8, 11, 16), 'модели меню, API, кэш Valkey 60 с, экран Э-1'),
    ('US-02', 'Корзина, количество 1–5', 'Must', 2, 4, (4, 6, 9), 'состояние корзины на клиенте, проверка остатка'),
    ('US-03', 'Окна получения, закрытие за 15 мин, лимит', 'Must', 5, 4, (8, 11, 16), 'окна по расписанию, проверка лимита, экран Э-3'),
    ('US-04', 'Оплата Payme, Click, Uzum и резерв 10 мин', 'Must', 8, 5, (30, 43, 70),
     'резерв в одной транзакции 8 ч; Payme 12 ч; Click 8 ч; Uzum 10 ч (библиотека paytechuz, MIT); экран оплаты и чек 5 ч'),
    ('US-05', 'Статус заказа', 'Must', 3, 3, (4, 6, 9), 'API статуса, опрос с экрана Э-6'),
    ('US-06', 'Уведомление «Готов» в Telegram', 'Should', 3, 3, (5, 8, 12), 'бот aiogram, привязка по ссылке, задача Celery'),
    ('US-07', 'Код получения и «Я на месте»', 'Must', 3, 4, (4, 6, 9), 'код из 4 цифр на день, отметка прибытия'),
    ('US-08', 'Отмена и возврат денег', 'Should', 8, 4, (10, 16, 26), 'отмена 4 ч; возврат через 3 сервиса 9 ч; экран 3 ч'),
    ('US-09', 'Повтор заказа', 'Could', 2, 3, (2, 3, 5), 'кнопка «Повторить», проверка остатка'),
    ('US-10', 'История заказов за 30 дней', 'Could', 2, 3, (2, 3, 5), 'список заказов'),
    ('US-11', 'Вход по номеру и SMS-коду', 'Must', 3, 4, (7, 10, 14), 'код 6 цифр, блок после 5 ошибок, сессия 30 дней, шлюз SMS'),
    ('US-12', 'Панель: заказы по окнам и сводка порций', 'Must', 5, 4, (8, 11, 16), 'экран Э-7, опрос 10 с'),
    ('US-13', 'Смена статуса, «Готов» для всего окна', 'Must', 3, 4, (4, 6, 9), 'порядок статусов, журнал времени'),
    ('US-14', 'Поиск заказа по коду, «Выдан»', 'Must', 2, 4, (3, 5, 7), 'поиск по коду дня, отметка выдачи'),
    ('US-15', '«Закончилось» одним действием', 'Should', 2, 3, (2, 4, 6), 'остаток 0, пометка оплаченных заказов'),
    ('US-16', 'Публикация меню дня', 'Must', 5, 4, (5, 8, 14), 'админка Django: блюда, цены, остатки, публикация'),
    ('US-17', 'Лимит заказов на окно', 'Should', 3, 3, (2, 3, 5), 'поле лимита в админке, проверка'),
    ('US-18', 'Отчёт продаж и файл .xlsx', 'Should', 8, 4, (6, 10, 16), 'запросы за период, выгрузка openpyxl'),
    ('US-19', 'Среднее время получения по окнам', 'Could', 3, 3, (3, 4, 6), 'расчёт от «Я на месте» до «Выдан»'),
]
CROSS = [
    ('X1', 'Каркас проекта', (8, 12, 18), 'Django, DRF, Docker Compose, CI GitHub Actions, React + Vite'),
    ('X2', 'Интерфейс и PWA', (10, 16, 24), 'общие компоненты по прототипу Figma, манифест, сервис-воркер'),
    ('X3', 'Ежедневная сверка с выпиской', (4, 6, 10), 'NFR-04, BG-3: сверка заказов с выпиской платёжных сервисов'),
    ('X4', 'Безопасность', (3, 4, 8), 'ограничение попыток, сессия сотрудника 12 ч, журналы без номера карты'),
    ('X5', 'Скрипты развёртывания и копий', (6, 8, 12), 'Nginx, certbot, pg_dump в хранилище S3, скрипт восстановления'),
]
N_TC_FUNC, N_TC_NFR = 70, 10
TEST = dict(auto=(8, 12, 18), run1=(0.2, 0.3, 0.4), run2=(0.1, 0.15, 0.2), nfr=(1.0, 1.5, 2.0))
FIX = (0.08, 0.10, 0.15)          # исправление ошибок, доля от часов кода
SPRINT_CAP = 72                    # ч команды за спринт: 3 студента x 12 ч/нед x 2 нед (допущение)
PM_PER_SPRINT = 7                  # 3 чел. x (планирование 1 ч + обзор и ретро 1 ч) + встреча со столовой 1 ч


def dev_hours(i, coding_factor=1.0):
    stories = sum(s[5][i] for s in STORIES) * coding_factor
    cross = sum(c[2][i] for c in CROSS) * coding_factor
    coding = stories + cross
    t_auto = TEST['auto'][i]
    t_run1 = N_TC_FUNC * TEST['run1'][i]
    t_run2 = N_TC_FUNC * TEST['run2'][i]
    t_nfr = N_TC_NFR * TEST['nfr'][i]
    tests = t_auto + t_run1 + t_run2 + t_nfr
    fixes = coding * FIX[i]
    sub = coding + tests + fixes
    sprints = math.ceil(sub / SPRINT_CAP)
    pm = sprints * PM_PER_SPRINT
    return dict(stories=stories, cross=cross, coding=coding, t_auto=t_auto, t_run1=t_run1, t_run2=t_run2,
                t_nfr=t_nfr, tests=tests, fixes=fixes, sub=sub, sprints=sprints, pm=pm, total=sub + pm)


# ---------- 2. Внедрение ----------
ROLL1 = [  # первая столовая
    ('Подключение Payme, Click, Uzum', (9, 12, 18), '3 сервиса x 4 ч: заявки от имени столовой, договоры, тестовые платежи, боевые ключи'),
    ('Установка на рабочий сервер', (3, 4, 6), 'VPS, домен, DNS, HTTPS, копии, мониторинг по скриптам X5'),
    ('Обучение сотрудника и администратора', (2, 3, 4), 'обучение 2 ч + памятка на 1 странице 1 ч'),
    ('Сопровождение пилотной недели', (5, 10, 15), '5 дней x 1 ч большой перемены x 2 человека'),
    ('Приёмка по тест-кейсам Must, акт', (3, 4, 6), 'администратор столовой'),
]
ROLLN = [  # каждая следующая столовая
    ('Подключение Payme, Click, Uzum', (9, 12, 18), 'у каждой столовой свои договоры (C-03)'),
    ('Настройка столовой в системе', (1, 1, 2), 'тот же сервер, новая запись столовой и окон'),
    ('Тест k6 перед подключением', (1, 2, 3), 'порог T1 из load-infra.md'),
    ('Обучение сотрудника и администратора', (2, 3, 4), 'как в первой столовой'),
    ('Сопровождение первой недели', (3, 5, 10), 'процесс уже проверен пилотом'),
    ('Приёмка по тест-кейсам Must, акт', (3, 4, 6), 'администратор столовой'),
]
BRV = 440_000
CASH1 = [  # разовые денежные расходы при запуске первой столовой
    ('Сервер и копия до запуска', (47_400, 317_000, 634_000), 'load-infra.md, 7.1: 5 дней почасово / 1 мес / 2 мес'),
    ('QR-наклейки (60 столов) и 10 плакатов', (330_000, 330_000, 330_000), 'оценка команды, раздел 1.3; рынком не проверена'),
    ('Регистрация ИП (договор SMS-шлюза, приём комиссии)', (0, round(0.9 * BRV), BRV),
     '0 — договор на юрлицо столовой; 0,9 БРВ — онлайн; 1 БРВ — лично'),
]
CASHN = [
    ('QR-наклейки и плакаты', (330_000, 330_000, 330_000), 'как в первой столовой'),
    ('Почасовая аренда сервера для теста k6', (5_000, 5_000, 5_000), 'load-infra.md, 7.1: меньше 5 000'),
]
RESERVE = 0.10   # резерв на перерасход часов: 10 % от разовых работ


def rollout(i, steps, cash):
    h = sum(s[1][i] for s in steps)
    c = sum(s[1][i] for s in cash)
    return dict(hours=h, labor=h * RATE, cash=c)


# ---------- 3. Регулярные расходы ----------
SC = dict(S1=dict(n=1, name='S1 «Минимальный запуск»'), S2=dict(n=3, name='S2 «Ожидаемый рост»'),
          S3=dict(n=5, name='S3 «Повышенная нагрузка»'))
INFRA_M = dict(S1=(204_500, 317_000, 418_870), S2=(204_500, 317_000, 518_000), S3=(404_500, 575_000, 851_780))
DOMAIN_Y = (27_000, 33_000, 45_000)
SMS_N = (150, 180, 300)              # SMS на столовую в учебный месяц
SMS_P = (85, 220, 220)               # сум за 1 SMS
SUPPORT_H = (2, 3, 6)                # ч/мес для первой столовой
SUPPORT_ADD = (0.5, 1, 2)            # ч/мес на каждую следующую столовую
DEVEL_H_Y = (0, 20, 40)              # развитие, ч/год
STUDY_M, DAYS = 9, 22


def regular(sc, i):
    n = SC[sc]['n']
    infra_m = INFRA_M[sc][i]
    sms_m = SMS_N[i] * SMS_P[i] * n
    sup_h = SUPPORT_H[i] + SUPPORT_ADD[i] * (n - 1)
    sup_m = sup_h * RATE
    devel_y = DEVEL_H_Y[i] * RATE
    dom_y = DOMAIN_Y[i]
    year = infra_m * 12 + dom_y + sms_m * STUDY_M + sup_m * 12 + devel_y
    study_month = infra_m + sms_m + sup_m + dom_y / 12 + devel_y / 12
    summer_month = infra_m + sup_m + dom_y / 12 + devel_y / 12
    cash_study_month = infra_m + sms_m + dom_y / 12
    fixed_y = infra_m * 12 + dom_y + sup_m * 12 + devel_y
    return dict(n=n, infra_m=infra_m, sms_m=sms_m, sup_h=sup_h, sup_m=sup_m, devel_y=devel_y, dom_y=dom_y,
                year=year, study_month=study_month, summer_month=summer_month,
                cash_study_month=cash_study_month, fixed_y=fixed_y,
                infra_y=infra_m * 12, sms_y=sms_m * STUDY_M, sup_y=sup_m * 12)


# ---------- 4. Юнит-экономика ----------
ORDERS_DAY = 50
CHECK = 25_000
COMMISSION = 0.05


def unit(sc, i='base', demand=1.0, invest=None):
    r = regular(sc, LV.index(i) if isinstance(i, str) else i)
    n = r['n']
    orders_m = ORDERS_DAY * demand * DAYS * n
    rev = CHECK * COMMISSION
    var = SMS_N[1] * SMS_P[1] / (ORDERS_DAY * DAYS)   # сум SMS на заказ (база)
    margin = rev - var
    fixed_m = r['fixed_y'] / STUDY_M
    result_m = orders_m * margin - fixed_m
    be_day = fixed_m / margin / DAYS / n          # заказов в день на столовую
    payback = invest / result_m if (invest and result_m > 0) else None
    return dict(orders_m=orders_m, rev=rev, var=var, margin=margin, margin_m=orders_m * margin, fixed_m=fixed_m,
                result_m=result_m, be_day=be_day, payback_m=payback)


# ---------- 5. Сводка ----------
def calc():
    D = {i: dev_hours(k) for k, i in enumerate(LV)}
    R1 = {i: rollout(k, ROLL1, CASH1) for k, i in enumerate(LV)}
    RN = {i: rollout(k, ROLLN, CASHN) for k, i in enumerate(LV)}
    out = dict(D=D, R1=R1, RN=RN, scen={})
    for k, i in enumerate(LV):
        dev = D[i]['total'] * RATE
        labor1 = dev + R1[i]['labor']
        reserve1 = labor1 * RESERVE
        initial = labor1 + R1[i]['cash'] + reserve1
        out.setdefault('init', {})[i] = dict(dev=dev, roll=R1[i]['labor'], cash=R1[i]['cash'], reserve=reserve1,
                                            labor=labor1, total=initial, cash_only=R1[i]['cash'])
        for sc in SC:
            n = SC[sc]['n']
            grow_labor = RN[i]['labor'] * (n - 1)
            grow_cash = RN[i]['cash'] * (n - 1)
            grow_res = grow_labor * RESERVE
            grow = grow_labor + grow_cash + grow_res
            reg = regular(sc, k)
            out['scen'].setdefault(sc, {})[i] = dict(
                reg=reg, grow=grow, grow_labor=grow_labor, grow_cash=grow_cash, grow_res=grow_res,
                year1=initial + grow + reg['year'], tco3=initial + grow + 3 * reg['year'],
                invest=initial + grow)
    return out


OLD = dict(dev=48_000_000, roll=4_000_000, infra=9_000_000, backup=0, prep=0, domain=600_000, sms=1_800_000,
           support=21_600_000, devel=12_000_000, reserve=9_700_000, total=106_700_000, initial=52_000_000,
           fixed_m=1_600_000, be_day=61, payback3=29, hours=480)

if __name__ == '__main__':
    o = calc()
    for i in LV:
        d = o['D'][i]
        print(i, {k: round(v, 1) for k, v in d.items()})
    for i in LV:
        print('R1', i, o['R1'][i], 'RN', o['RN'][i])
    for i in LV:
        print('INIT', i, {k: round(v) for k, v in o['init'][i].items()})
    for sc in SC:
        for i in LV:
            s = o['scen'][sc][i]
            print(sc, i, 'year', round(s['reg']['year']), 'grow', round(s['grow']), 'year1', round(s['year1']),
                  'tco3', round(s['tco3']), 'study_m', round(s['reg']['study_month']), 'cash_m', round(s['reg']['cash_study_month']))
    for sc in SC:
        inv = o['scen'][sc]['base']['invest']
        for dm in (1.0, 0.7):
            u = unit(sc, 'base', dm, inv)
            print('UNIT', sc, dm, {k: (round(v, 1) if v is not None else None) for k, v in u.items()})


# ---------- 6. Варианты А и Б по новым ценам (для раздела 3.6 работы ПК) ----------
def variants():
    """TCO за 3 года, S1, база. Метод тот же, что у варианта В."""
    o = calc()
    ib = o['init']['base']
    reg = regular('S1', 1)
    roll_v = [('Подключение Payme, Click, Uzum', 12), ('Установка', 4), ('Обучение', 3), ('Пилотная неделя', 10), ('Приёмка', 4)]
    bubble_m = 32 * USD                     # Starter, оплата за год
    delever_3y = 1_300_000 * 36 + 100 * 1950 * 27   # 1 100 заказов в уч. месяц: 100 сверх лимита
    cash_ab = CASH1[1][1][1] + CASH1[2][1][1]       # печать + ИП (сервера нет)
    V = {}
    # А: конструктор 120 ч (оценка команды), установка 2 ч (домен в Bubble)
    a = dict(code=120 * RATE, tests=0, roll=(12 + 2 + 3 + 10 + 4) * RATE, cash=cash_ab,
             platform=bubble_m * 36, domain=reg['dom_y'] * 3, sms=reg['sms_y'] * 3,
             support=3 * RATE * 36, devel=15 * RATE * 3)
    # Б: настройка 20 ч, подключение оплаты через поставщика 8 ч, установка 2 ч; поддержка 1 ч/мес
    bb = dict(code=20 * RATE, tests=0, roll=(8 + 2 + 3 + 10 + 4) * RATE, cash=cash_ab,
              platform=delever_3y, domain=0, sms=0, support=1 * RATE * 36, devel=0)
    d = o['D']['base']
    v = dict(code=(d['coding'] + d['fixes'] + d['pm']) * RATE, tests=d['tests'] * RATE, roll=ib['roll'], cash=ib['cash'],
             platform=reg['infra_y'] * 3 + CASH1[0][1][1] * 0, domain=reg['dom_y'] * 3, sms=reg['sms_y'] * 3,
             support=reg['sup_y'] * 3, devel=reg['devel_y'] * 3)
    for k, x in (('A', a), ('B', bb), ('V', v)):
        x['reserve'] = RESERVE * (x['code'] + x['tests'] + x['roll'])
        x['g1'] = x['code'] + x['tests']
        x['g2'] = x['roll'] + x['cash']
        x['g3'] = x['platform'] + x['domain'] + x['sms']
        x['g4'] = x['support'] + x['devel']
        x['g5'] = x['reserve']
        x['total'] = x['g1'] + x['g2'] + x['g3'] + x['g4'] + x['g5']
        x['invest'] = x['g1'] + x['g2'] + x['g5']
        V[k] = x
    return V


if __name__ == '__main__':
    for k, x in variants().items():
        print('VAR', k, {a: round(b) for a, b in x.items()})
