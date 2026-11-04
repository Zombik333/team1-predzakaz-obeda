"""Расчёт нагрузки и инфраструктуры (load-infra.md). Запуск: python3 load_infra_calc.py
Все допущения названы в load-infra.md, раздел 3."""
USD = 11911.71   # 04.11.2026, market-prices.md раздел 2.1
EUR = 13383.01   # 03.11.2026, norma.uz
RUB = 147.65     # 03.11.2026, norma.uz
DAYS, MONTHS = 22, 9

SC = {  # сценарии нагрузки
    'S1-30%': dict(n=1, od=35, st=105),
    'S1':     dict(n=1, od=50, st=150),
    'S2':     dict(n=3, od=150, st=450),
    'S3':     dict(n=5, od=250, st=750),
}
REQ_ORDER, REQ_BROWSE = 15, 3        # запросов API на сессию (оценка, табл. 4.2)
STAFF_DEV, POLL_S, PANEL_H = 2, 10, 4  # телефонов, опрос панели (с), часов панели в день
KB_REQ, KB_ORDER_DB, KB_PWA = 3, 2, 300
CPU_MS = (40, 20)                    # мс процессора на запрос: пессим., оптим.
UTIL = 0.7

def load(v):
    n = v['n']
    peak_o, conc = 60 * n, 100 * n           # NFR-02, NFR-01 на столовую
    browse = conc - peak_o
    polls = STAFF_DEV * n * 600 / POLL_S
    acts = 2 * peak_o
    req10 = peak_o * REQ_ORDER + browse * REQ_BROWSE + polls + acts
    rps_conc = conc / 10                      # 1 запрос на пользователя за 10 с
    day = v['od'] * (REQ_ORDER + REQ_BROWSE + 2) + STAFF_DEV * n * PANEL_H * 3600 / POLL_S
    om = v['od'] * DAYS
    return dict(orders_m=om, orders_y=om * MONTHS, peak_orders=peak_o, cap40=40 * n, conc=conc,
                req10=req10, rps_avg=req10 / 600, rps_burst=req10 / 600 * 5, rps=rps_conc,
                rps_design=rps_conc * 2, req_day=day, req_m=day * DAYS,
                db_y_mb=om * MONTHS * KB_ORDER_DB / 1024, db_3y_mb=om * MONTHS * 3 * KB_ORDER_DB / 1024,
                api_gb=day * DAYS * KB_REQ / 1024**2, pwa_gb=v['st'] * KB_PWA * 2 / 1024**2,
                log_mb=day * DAYS * 0.25 / 1024, mbit_api=rps_conc * 2 * KB_REQ * 8 / 1024,
                mbit_first=conc * KB_PWA * 8 / 1024 / 60,
                sms=(v['st'] * 1.0, v['st'] * 1.2, v['st'] * 2.0), sms_doc=500 * n,
                tg_m=om, tg_burst_s=40 * n / 30)

for k, v in SC.items():
    r = load(v)
    print(k, {a: (round(b, 2) if isinstance(b, float) else b) for a, b in r.items()})
for c in (2, 4, 6):
    print(f'{c} vCPU: {c*UTIL/CPU_MS[0]*1000:.0f}–{c*UTIL/CPU_MS[1]*1000:.0f} RPS')

RAM = dict(os=350, nginx=20, gunicorn=4*100, celery_worker=220, celery_beat=80, postgres=450, valkey=40, cron=100)
RAM3 = dict(RAM, gunicorn=8*100, postgres=900)
print('RAM S1 MB', sum(RAM.values()), ' RAM S3 MB', sum(RAM3.values()))

# Цены, сум/мес (источники — раздел 6)
P = dict(airnet_strong_2_4=200000, uzcloud_basic_2_4_ip=308000, serverspace_vps4_2_4=2566*RUB,
         uzcloud_custom_4_4_ip=4*85000+4*12000+20*2000+50000, uzcloud_std_4_8_ip=566000,
         airnet_nano_4_8=400000, serverspace_vps5_4_8=5498*RUB, tcloud_pro_6_8=530000,
         bk_low=4500, bk_base=9000, bk_high=40000)
print({k: round(v) for k, v in P.items()})
M = {
 'S1': (P['airnet_strong_2_4']+P['bk_low'], P['uzcloud_basic_2_4_ip']+P['bk_base'], P['serverspace_vps4_2_4']+P['bk_high']),
 'S2': (P['airnet_strong_2_4']+P['bk_low'], P['uzcloud_basic_2_4_ip']+P['bk_base'], P['uzcloud_custom_4_4_ip']+P['bk_high']),
 'S3': (P['airnet_nano_4_8']+P['bk_low'], P['uzcloud_std_4_8_ip']+P['bk_base'], P['serverspace_vps5_4_8']+P['bk_high']),
}
for k, (lo, ba, hi) in M.items():
    oy = load(SC[k])['orders_y']
    print(f'{k}: month {lo:.0f}/{ba:.0f}/{hi:.0f}; year {lo*12:.0f}/{ba*12:.0f}/{hi*12:.0f}; 3y {lo*36:.0f}/{ba*36:.0f}/{hi*36:.0f}; per order (base) {ba*12/oy:.0f}')
ONE = (5*24*395, P['uzcloud_basic_2_4_ip']+P['bk_base'], 2*(P['uzcloud_basic_2_4_ip']+P['bk_base']))
print('one-time pre-launch', ONE)
lo, ba, hi = M['S1']
print('first year S1', ONE[0]+lo*12, ONE[1]+ba*12, ONE[2]+hi*12)
print('3y S1 incl one-time', ONE[0]+lo*36, ONE[1]+ba*36, ONE[2]+hi*36, ' old 9 000 000')
# Покупка против аренды
H_local, H_eu = 30816177, 1590.90*EUR
COLO, COLO_INST = 550000, 95000
for H in (H_local, H_eu):
    print(f'H={H:.0f}: R* (60 мес) = {COLO + H/60:.0f}; R* (36 мес) = {COLO + H/36:.0f}; '
          f'free hosting payback vs 308k {H/308000:.0f} мес, vs 566k {H/566000:.0f} мес')
print('own 3y', H_local + COLO_INST + COLO*36, ' VPS 3y', 308000*36, ' 4/8 3y', 566000*36)
print('hourly 2/2 month', 395*24*30)
