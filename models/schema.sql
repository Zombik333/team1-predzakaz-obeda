-- Схема базы данных сервиса предзаказа обеда (команда 1). PostgreSQL 16.
-- Сгенерировано из модели раздела 3.3. Суммы — в сумах (integer).

-- Сотрудники
CREATE TABLE staff (
  id serial PRIMARY KEY,
  name varchar(60) NOT NULL,
  phone varchar(13) NOT NULL UNIQUE,
  role varchar(12) NOT NULL CHECK (role IN ('сотрудник', 'администратор')),
  password_hash varchar(100) NOT NULL,
  is_active boolean DEFAULT true NOT NULL
);

-- Блюда
CREATE TABLE dishes (
  id serial PRIMARY KEY,
  name varchar(80) NOT NULL,
  portion_g smallint NOT NULL CHECK (portion_g > 0),
  is_active boolean DEFAULT true NOT NULL
);

-- Меню дня
CREATE TABLE daily_menus (
  id serial PRIMARY KEY,
  menu_date date NOT NULL UNIQUE,
  published_at timestamptz NOT NULL,
  published_by int REFERENCES staff(id)
);

-- Позиции меню дня
CREATE TABLE menu_items (
  id bigserial PRIMARY KEY,
  daily_menu_id int NOT NULL REFERENCES daily_menus(id),
  dish_id int NOT NULL REFERENCES dishes(id),
  price integer NOT NULL CHECK (price > 0),
  stock smallint NOT NULL CHECK (stock >= 0),
  UNIQUE (daily_menu_id, dish_id)
);

-- Студенты
CREATE TABLE students (
  id bigserial PRIMARY KEY,
  phone varchar(13) NOT NULL UNIQUE,
  name varchar(60) NOT NULL,
  telegram_chat_id bigint,
  created_at timestamptz DEFAULT now() NOT NULL
);

-- Окна получения
CREATE TABLE pickup_windows (
  id serial PRIMARY KEY,
  window_date date NOT NULL,
  break_name varchar(30) NOT NULL,
  starts_at time NOT NULL,
  accept_until time NOT NULL,
  order_limit smallint DEFAULT 40 NOT NULL,
  UNIQUE (window_date, starts_at)
);

-- Резервы
CREATE TABLE reservations (
  id bigserial PRIMARY KEY,
  student_id bigint NOT NULL REFERENCES students(id),
  window_id int NOT NULL REFERENCES pickup_windows(id),
  total integer NOT NULL,
  status varchar(10) NOT NULL CHECK (status IN ('активен', 'оплачен', 'истёк')),
  created_at timestamptz DEFAULT now() NOT NULL,
  expires_at timestamptz NOT NULL
);

-- Позиции резерва
CREATE TABLE reservation_items (
  id bigserial PRIMARY KEY,
  reservation_id bigint NOT NULL REFERENCES reservations(id),
  menu_item_id bigint NOT NULL REFERENCES menu_items(id),
  qty smallint NOT NULL CHECK (qty BETWEEN 1 AND 5),
  price integer NOT NULL
);

-- Платежи
CREATE TABLE payments (
  id bigserial PRIMARY KEY,
  reservation_id bigint NOT NULL REFERENCES reservations(id),
  provider varchar(8) NOT NULL CHECK (provider IN ('payme', 'click', 'uzum')),
  provider_txn_id varchar(64) NOT NULL UNIQUE,
  amount integer NOT NULL,
  status varchar(10) NOT NULL CHECK (status IN ('создан', 'оплачен', 'отказ')),
  receipt_url varchar(255),
  created_at timestamptz DEFAULT now() NOT NULL,
  confirmed_at timestamptz
);

-- Заказы
CREATE TABLE orders (
  id bigserial PRIMARY KEY,
  reservation_id bigint NOT NULL REFERENCES reservations(id) UNIQUE,
  student_id bigint NOT NULL REFERENCES students(id),
  window_id int NOT NULL REFERENCES pickup_windows(id),
  order_date date NOT NULL,
  pickup_code char(4) NOT NULL CHECK (pickup_code ~ '^[0-9]{4}$'),
  total integer NOT NULL,
  status varchar(10) NOT NULL CHECK (status IN ('Принят', 'Готовится', 'Готов', 'Выдан', 'Отменён')),
  paid_at timestamptz NOT NULL,
  arrived_at timestamptz,
  issued_at timestamptz,
  issued_by int REFERENCES staff(id),
  UNIQUE (order_date, pickup_code)
);

-- Позиции заказа
CREATE TABLE order_items (
  id bigserial PRIMARY KEY,
  order_id bigint NOT NULL REFERENCES orders(id),
  menu_item_id bigint NOT NULL REFERENCES menu_items(id),
  qty smallint NOT NULL CHECK (qty BETWEEN 1 AND 5),
  price integer NOT NULL
);

-- Возвраты
CREATE TABLE refunds (
  id bigserial PRIMARY KEY,
  order_id bigint NOT NULL REFERENCES orders(id),
  payment_id bigint NOT NULL REFERENCES payments(id),
  amount integer NOT NULL,
  status varchar(10) NOT NULL CHECK (status IN ('запрошен', 'выполнен')),
  requested_at timestamptz DEFAULT now() NOT NULL,
  completed_at timestamptz
);

-- Журнал статусов
CREATE TABLE order_status_log (
  id bigserial PRIMARY KEY,
  order_id bigint NOT NULL REFERENCES orders(id),
  status varchar(10) NOT NULL,
  changed_at timestamptz DEFAULT now() NOT NULL,
  changed_by int REFERENCES staff(id)
);

CREATE INDEX ON orders (window_id, status);
CREATE INDEX ON reservations (expires_at) WHERE status = 'активен';
CREATE INDEX ON order_status_log (order_id, changed_at);
