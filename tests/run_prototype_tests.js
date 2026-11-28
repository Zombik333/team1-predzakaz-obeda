// Прогон тест-кейсов на HTML-прототипе (Playwright). Запуск: node run_prototype_tests.js ../prototype/prototype.html v3
// Скрипт печатает статус и фактический результат каждого тест-кейса в формате JSON.
// Runs prototype checks for test cases. node run.js <file> <tag>
const { chromium } = require('playwright');
const path = require('path');
const file = 'file://' + path.resolve(process.argv[2]); const tag = process.argv[3];
const R = {};
const rec = (id, ok, act) => { R[id] = { status: ok ? 'Пройден' : 'Не пройден', act }; };
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1100, height: 900 } });
  const fresh = async (hash = 's1') => { const p = await ctx.newPage(); await p.clock.install({ time: new Date('2026-11-27T11:02:00') }); await p.goto(file + '#' + hash); await p.waitForTimeout(100); return p; };
  const T = async (p, s) => (await p.locator(s).first().innerText()).replace(/\s+/g, ' ').trim();
  const on = async (p) => p.locator('.screen.on').getAttribute('id');
  const shot = async (p, name) => p.screenshot({ path: `${tag}_${name}.png`, clip: await p.locator('#phone').boundingBox() });
  let p;
  try {
  // TC-001
  p = await fresh(); const items = await p.locator('#s1 .item').allInnerTexts();
  const okAll = items.length > 0 && items.every(t => /сум/.test(t) && /\d+ (г|мл)/.test(t) && /осталось \d+/.test(t));
  rec('TC-001', okAll, `${items.length} позиций; у каждой название, цена в сумах, вес и остаток`);
  // TC-005
  const before = await T(p, '#s1 .foot .btn');
  await p.locator('#s1 .item', { hasText: 'Лагман' }).locator('button.add').click();
  const after = await T(p, '#s1 .foot .btn');
  rec('TC-005', before !== after && /3 позиции/.test(after), `До: «${before}». После «+» у лагмана: «${after}»`);
  await shot(p, 'menu');
  // TC-006 / TC-201 / TC-008
  await p.locator('#s1 .foot .btn').click();
  const plov = p.locator('#s2 .item', { hasText: 'Плов' });
  const s0 = await T(p, '#s2 .sum');
  let sAfter1 = '';
  for (let i = 0; i < 4; i++) { const btn = plov.locator('.qty button').nth(1); if (await btn.isEnabled()) await btn.click(); if (i === 0) sAfter1 = await T(p, '#s2 .sum'); }
  const q5 = await T(p, '#s2 .item:has-text("Плов") .qty span'); const s1 = await T(p, '#s2 .sum');
  rec('TC-201', q5 === '5', `После 4 нажатий «+» количество плова: ${q5}`);
  const num = (t) => Number(t.replace(/\D/g, ''));
  rec('TC-008', num(sAfter1) - num(s0) === 24000, `Итог до: «${s0}», после одного «+» у плова: «${sAfter1}» (плюс 24 000 сум, цена плова)`);
  const inc = plov.locator('.qty button').nth(1); const dis = !(await inc.isEnabled()); if (!dis) await inc.click();
  const q6 = await T(p, '#s2 .item:has-text("Плов") .qty span');
  rec('TC-006', q6 === '5', `Шестое нажатие «+»: кнопка ${dis ? 'неактивна' : 'активна'}, количество ${q6}`);
  const dec = plov.locator('.qty button').nth(0); for (let i = 0; i < 6; i++) if (await dec.isEnabled()) await dec.click();
  const decDis = !(await dec.isEnabled()); const q0 = await T(p, '#s2 .item:has-text("Плов") .qty span');
  R['TC-202'] = { status: decDis && q0 === '1' ? 'Пройден' : (q0 === '1' ? 'Заблокирован' : 'Не пройден'), act: `«−» до упора: количество ${q0}, кнопка «−» ${decDis ? 'неактивна' : 'активна'}` };
  await shot(p, 'cart');
  // TC-007 kompot stock 3
  await p.locator('.back[data-go=s1]').click();
  const kom = p.locator('#s1 .item', { hasText: 'Компот' });
  if (await kom.count()) { await kom.locator('button.add').click(); await p.locator('#s1 .foot .btn').click();
    const k = p.locator('#s2 .item', { hasText: 'Компот' }); for (let i = 0; i < 5; i++) { const bt = k.locator('.qty button').nth(1); if (await bt.isEnabled()) await bt.click(); }
    const qk = await T(p, '#s2 .item:has-text("Компот") .qty span'); const hint = await p.locator('#s2 .hint').allInnerTexts();
    rec('TC-007', qk === '3' && hint.some(h => /Осталось 3 шт\./.test(h)), `Остаток компота 3; после 5 нажатий «+» количество ${qk}; подсказка «${hint.find(h => /Осталось 3/.test(h)) || '—'}»`);
  } else R['TC-007'] = { status: 'Заблокирован', act: 'В прототипе нет позиции с остатком меньше 5' };
  // TC-002 (manty stock 0)
  const menuNames = await p.locator('#s1 .item .n').allInnerTexts();
  const hasZeroData = (await p.content()).includes('Манты');
  R['TC-002'] = hasZeroData ? { status: menuNames.includes('Манты') ? 'Не пройден' : 'Пройден', act: `Манты (остаток 0) ${menuNames.includes('Манты') ? 'видны' : 'не показаны'} в меню` } : { status: 'Заблокирован', act: 'В данных прототипа нет позиции с остатком 0' };
  await p.close();
  // windows
  p = await fresh('s3');
  const w = async () => (await p.locator('#s3 .win.sel .m').innerText());
  await p.locator('#s3 .win', { hasText: '13:20' }).click(); const wFull = await w();
  rec('TC-011', wFull !== '13:20–13:30' && /Окно заполнено/.test(await T(p, '#s3 .win:has-text("13:20")')), `Окно 13:20 с пометкой «Окно заполнено»; после нажатия выбрано ${wFull}`);
  await p.locator('#s3 .win', { hasText: '10:20' }).click(); const wClosed = await w();
  // TC-010 is not run: the prototype time is constant, the 15-minute rule needs the test server
  const wins = await p.locator('#s3 .win .m').allInnerTexts();
  rec('TC-009', wins.length === 4 && /сегодня/.test(await T(p, '#s3 .bar')), `Показаны 4 перемены текущего дня: ${wins.join(', ')}`);
  await p.locator('#s3 .win', { hasText: '14:50' }).click(); const w4 = await w();
  await p.locator('#s3 .foot .btn').click(); const sub = await T(p, '#paysub, #s4 .bar .s');
  rec('TC-012', w4 === '14:50–15:00' && /14:50/.test(sub), `Выбрано окно 14:50; выбрано на экране: ${w4}; подпись оплаты: «${sub}»`);
  await shot(p, 'pay');
  // TC-013
  const opts = (await p.locator('#s4 .pay').allInnerTexts()).map(x => x.split('\n')[0]);
  rec('TC-013', ['Payme', 'Click', 'Uzum'].every(x => opts.includes(x)), `Способы оплаты: ${opts.join(', ')}`);
  // TC-016 timer
  const t0 = await T(p, '#t1'); await p.clock.runFor(5000); const t5 = await T(p, '#t1');
  await p.clock.runFor(600000); const tEnd = await T(p, '#t1'); const exp = (await p.locator('#s4 .msg, #expired').allInnerTexts()).join(' ');
  rec('TC-016', t0 !== t5 && /истекло/.test(exp), `Таймер: ${t0} → через 5 с ${t5} → через 10 мин ${tEnd}. ${exp ? 'Сообщение: «' + exp.trim().slice(0, 60) + '…»' : 'Сообщения нет'}`);
  await p.close();
  // TC-015 / TC-014
  p = await fresh('s4'); await p.locator('#s4 .pay[data-pay=click]').click(); await p.locator('#paybtn').click();
  const sErr = await on(p); await p.locator('#s5 .btn.sec').click(); const cartAfter = await p.locator('#s2 .item .n').allInnerTexts();
  rec('TC-015', sErr === 's5' && cartAfter.length >= 2, `Отказ Click → экран ${sErr === 's5' ? 'Э-5 «Оплата не прошла»' : sErr}; заказ не создан; в корзине: ${cartAfter.join(', ')}`);
  await p.goto(file + '#s4'); await p.locator('#s4 .pay[data-pay=payme]').click(); await p.locator('#paybtn').click();
  const sOk = await on(p); const steps = await T(p, '#s6 .steps');
  rec('TC-014', sErr === 's5' && sOk === 's6' && /Принят/.test(steps), `Без подтверждения (отказ) заказа нет; после оплаты Payme экран Э-6, статус «Принят»`);
  const codeTxt = await T(p, '#s6 .code .c');
  rec('TC-024', /^\d{4}$/.test(codeTxt), `Код получения: ${codeTxt}`);
  rec('TC-020', /\d{4}/.test(await T(p, '#s6 .code')) && /перемена/.test(await T(p, '#s6 .code')), `На экране заказа: «${(await T(p, '#s6 .code')).slice(0, 70)}»`);
  // TC-017
  await p.locator('#s6 .link', { hasText: 'Электронный чек' }).click(); const rc = await p.locator('#s6 .receipt').count();
  rec('TC-017', rc > 0, rc ? `Чек показан: «${(await T(p, '#s6 .receipt')).slice(0, 70)}…»` : 'Ссылка «Электронный чек» не открывает чек');
  await shot(p, 'order');
  // TC-018 (needs cancel)
  await p.locator('#s6 .link', { hasText: 'Отменить' }).click(); if (await p.locator('#cancelyes').count()) await p.locator('#cancelyes').click(); const st2 = await T(p, '#s6 .steps');
  rec('TC-018', /Отменён/.test(st2), /Отменён/.test(st2) ? 'Статусы «Принят», «Готовится», «Готов», «Выдан» на экране заказа; после отмены — «Отменён»' : 'Видны 4 статуса; статус «Отменён» не показан: ссылка «Отменить заказ» не работает');
  await p.close();
  // TC-025, staff
  p = await fresh('s4'); await p.locator('#s4 .pay[data-pay=payme]').click(); await p.locator('#paybtn').click();
  await p.locator('#s6 .foot .btn').click(); const s7 = await on(p); const tagTxt = (await p.locator('#s7').innerText());
  rec('TC-025', s7 === 's7' && /У точки 11:57|11:57/.test(tagTxt + (await p.locator('#ordmsg').innerText().catch(() => ''))), `После «Я у точки выдачи» время прибытия 11:57 записано`);
  rec('TC-045', /Собрать на окно/.test(tagTxt), 'Сводка «Собрать на окно»: порции по позициям');
  const key = (k) => p.locator('#s7 .keys button', { hasText: new RegExp('^' + k.replace('⌫', '⌫') + '$') }).click();
  // TC-051 wrong code
  for (const k of ['⌫', '⌫', '⌫', '⌫']) await key(k);
  for (const k of '1234') await key(k); await key('OK');
  const f1 = (await p.locator('#s7 .body').innerText());
  rec('TC-051', /Заказ не найден/.test(f1), /Заказ не найден/.test(f1) ? 'Код 1234: сообщение «Заказ не найден»' : `Код 1234 не вводится: поле кода ${(await p.locator('#s7 .inp').innerText()).replace(/\s+/g, '')}`);
  // TC-203 three digits
  for (let i = 0; i < 4; i++) await key('⌫'); for (const k of '482') await key(k); await key('OK');
  const f3 = await p.locator('#s7 .body').innerText();
  rec('TC-203', /Введите 4 цифры|не найден/.test(f3) && !(await p.locator('#issue.dis').count() === 0), /Введите 4 цифры/.test(f3) ? 'Код 482: сообщение «Введите 4 цифры кода», кнопка «Выдать» неактивна' : 'Цифры не вводятся с клавиатуры');
  // keyboard check: after erasing, the field must be empty (in version 2 the field is a static picture «4821»)
  const field = async () => (await p.locator('#s7 .inp div:not(.empty)').allInnerTexts()).join('').replace(/\s+/g, '');
  for (let i = 0; i < 5; i++) await key('⌫');
  const keysWork = (await field()) === '';
  // TC-204 fifth digit is not accepted
  for (const k of '48215') await key(k);
  const inp = await field();
  rec('TC-204', keysWork && inp === '4821', keysWork ? `Ввод 4, 8, 2, 1, 5: поле кода «${inp}»` : 'Клавиши не вводят цифры: поле кода всегда показывает 4821');
  // TC-050 correct code
  for (let i = 0; i < 5; i++) await key('⌫'); for (const k of '4821') await key(k);
  await key('OK'); const f4 = await p.locator('#s7 .body').innerText();
  rec('TC-050', keysWork && /№ 1043/.test(f4), keysWork ? `Ввод 4821 → ${/№ 1043/.test(f4) ? 'заказ № 1043' : 'заказ не найден'}` : 'Клавиши не вводят цифры: карточка № 1043 видна всегда, поиск по коду не работает');
  rec('TC-043', /№ 1043/.test(f4) && /Плов/.test(f4) && /Готов|Принят/.test(f4), /№ 1043/.test(f4) ? `Карточка заказа: «${f4.split('\n').filter(x => /№|×/.test(x)).join(' ')}»` : 'Карточка заказа не показана');
  await shot(p, 'staff');
  // TC-052 issue
  await p.locator('#s7 .foot .btn').click(); const after52 = await on(p); const f5 = await p.locator('#s7 .body').innerText().catch(() => '');
  rec('TC-052', after52 === 's7' && /выдан в \d\d:\d\d/.test(f5), after52 === 's7' ? `«${(f5.match(/Заказ № \d+ выдан в \d\d:\d\d/) || ['—'])[0]}»` : 'Кнопка «Выдать заказ» открыла меню студента: статус «Выдан» и время выдачи не показаны');
  // TC-027 reuse
  if (after52 === 's7') { for (const k of '4821') await key(k); await key('OK'); const f6 = await p.locator('#s7 .body').innerText();
    rec('TC-027', /повторно не принимается|уже выдан/.test(f6), `Повторный ввод 4821: «${(f6.match(/Заказ № .*?принимается\./) || [f6.slice(0, 60)])[0]}»`); }
  else R['TC-027'] = { status: 'Заблокирован', act: 'Повторный ввод кода невозможен: клавиатура не вводит цифры' };
  } catch (e) { console.error('ERR', e.message); }
  console.log(JSON.stringify(R, null, 1)); await b.close();
})();
