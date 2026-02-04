# Документация API RotoBus

## Содержание

1. [Общая информация](#общая-информация)
2. [Базовый URL](#базовый-url)
3. [Формат ответов](#формат-ответов)
4. [Структура компании](#структура-компании)
5. [API Endpoints](#api-endpoints)
   - [Компании](#компании)
   - [Пользователи](#пользователи)
   - [Аутентификация](#аутентификация)
   - [Маршруты](#маршруты)
   - [Отчеты](#отчеты)
   - [Транспортные средства](#транспортные-средства)
   - [Коэффициенты](#коэффициенты)
   - [Статистика](#статистика)
   - [Конфигурация](#конфигурация)
6. [HTML страницы](#html-страницы)
7. [Особенности расчета зарплаты](#особенности-расчета-зарплаты)
8. [Примеры использования](#примеры-использования)
9. [Ошибки и их обработка](#ошибки-и-их-обработка)
10. [Примечания для разработчика](#примечания-для-разработчика)

---

## Общая информация

API RotoBus предоставляет RESTful интерфейс для управления транспортной компанией. Система поддерживает многокомпанейскую архитектуру, где каждая компания имеет свою собственную изолированную базу данных.

### Основные возможности:
- Управление пользователями (водители, кондукторы, администраторы)
- Учет маршрутов и тарифов
- Создание и верификация отчетов о работе
- Учет транспортных средств
- Расчет статистики и зарплат
- Настройка коэффициентов для разных должностей

## Базовый URL

```
https://rotorbus.ru
```

**Важно:** Все запросы должны содержать заголовок:
```http
Content-Type: application/json
```

## Формат ответов

### Успешный ответ:
```json
{
  "status": "ok",
  "message": "Операция выполнена успешно",
  "data": {...}  // опционально
}
```

### Ошибка:
```json
{
  "status": "error",
  "message": "Описание ошибки"
}
```

## Структура компании

Каждая компания в системе имеет следующие сущности:
1. **Пользователи** - сотрудники компании с различными должностями
2. **Маршруты** - транспортные маршруты с фиксированной оплатой
3. **Отчеты** - ежедневные отчеты о рейсах и пассажирах
4. **Транспорт** - автобусы и их технические характеристики
5. **Коэффициенты** - коэффициенты для расчета зарплаты по должностям
6. **Статистика** - сводные данные по работе сотрудников

---

## API Endpoints

### Компании

#### Получить список всех компаний
```http
GET /api/companies
```

**Ответ:**
```json
{
  "status": "ok",
  "companies": ["company1", "company2", "company3"]
}
```

#### Создать новую компанию
```http
POST /api/company
```

**Тело запроса:**
```json
{
  "company": "название_компании"
}
```

**Ограничения:**
- Имя компании не должно содержать пробелов
- Регистр не имеет значения (сохраняется в нижнем регистре)

#### Удалить компанию
```http
DELETE /api/company/{company_name}
```

### Пользователи

#### Получить всех пользователей компании
```http
GET /api/users/{company_name}
```

**Ответ:**
```json
{
  "status": "ok",
  "users": [
    {
      "id": 1,
      "name": "Иван Иванов",
      "post": "водитель",
      "account": "41001234567890",
      "vk": "id123456",
      "disciplinary_actions": "0",
      "note": "Стаж 5 лет"
    }
  ]
}
```

#### Получить информацию о конкретном пользователе
```http
GET /api/user/{company_name}/{user_id}
```

#### Создать нового пользователя
```http
POST /api/user/{company_name}
```

**Тело запроса:**
```json
{
  "name": "Иван Иванов",
  "password": "пароль123",
  "post": "водитель",
  "account": "41001234567890",
  "vk": "id123456",
  "disciplinary_actions": "0",
  "note": "Стаж 5 лет"
}
```

**Обязательные поля:** `name`, `password`, `post`

#### Обновить информацию о пользователе
```http
PUT /api/user/{company_name}/{user_id}
```

**Тело запроса:** JSON с полями для обновления.

**Запрещено обновлять:** `id`, `created_at`

#### Удалить пользователя
```http
DELETE /api/user/{company_name}/{user_id}
```

### Аутентификация

#### Вход в систему
```http
POST /api/login/{company_name}
```

**Тело запроса:**
```json
{
  "name": "Иван Иванов",
  "password": "пароль123"
}
```

**Ответ при успехе:**
```json
{
  "status": "ok",
  "message": "login successful"
}
```

**Ответ при ошибке:**
```json
{
  "status": "error",
  "message": "invalid login or password"
}
```

### Маршруты

#### Получить все маршруты компании
```http
GET /api/routes/{company_name}
```

**Ответ:**
```json
{
  "status": "ok",
  "routes": [
    {
      "id": 1,
      "route": "Маршрут №1",
      "salary": 500.0,
      "created_at": "2024-01-15 10:30:00"
    }
  ]
}
```

#### Создать новый маршрут
```http
POST /api/route/{company_name}
```

**Тело запроса:**
```json
{
  "route": "Маршрут №1",
  "salary": 500.0
}
```

**Обязательные поля:** `route`, `salary`

#### Получить зарплату для конкретного маршрута
```http
POST /api/route/salary/{company_name}
```

**Тело запроса:**
```json
{
  "route": "Маршрут №1"
}
```

**Ответ:**
```json
{
  "status": "ok",
  "salary": 500.0
}
```

#### Управление маршрутом
- `GET /api/route/{company_name}/{route_id}` - получить информацию
- `PUT /api/route/{company_name}/{route_id}` - обновить информацию
- `DELETE /api/route/{company_name}/{route_id}` - удалить маршрут

### Отчеты

#### Получить все отчеты (с фильтрацией)
```http
GET /api/reports/{company_name}
```

**Параметры запроса (опционально):**
- `user_name` - фильтр по имени пользователя
- `status` - фильтр по статусу (`not_verified`, `verified`, `rejected`)

**Пример:**
```http
GET /api/reports/company1?user_name=Иван&status=not_verified
```

#### Создать отчет
```http
POST /api/report/{company_name}
```

**Тело запроса:**
```json
{
  "user_name": "Иван Иванов",
  "date": "2024-01-15",
  "route": "Маршрут №1",
  "num_round_trips": 5,
  "num_passengers": 120,
  "proof": "https://example.com/photo.jpg"
}
```

**Обязательные поля:** `user_name`, `date`, `route`, `num_round_trips`, `num_passengers`

#### Верификация отчета
```http
POST /api/report/verify/{company_name}/{report_id}
```

**При верификации:**
- Автоматически рассчитывается зарплата
- Обновляется статистика пользователя
- Отчет помечается как `verified`

#### Отклонение отчета
```http
POST /api/report/reject/{company_name}/{report_id}
```

#### Управление отчетом
- `GET /api/report/{company_name}/{report_id}` - получить информацию
- `PUT /api/report/{company_name}/{report_id}` - обновить информацию
- `DELETE /api/report/{company_name}/{report_id}` - удалить отчет

### Транспортные средства

#### Получить все транспортные средства
```http
GET /api/vehicles/{company_name}
```

**Ответ:**
```json
{
  "status": "ok",
  "vehicles": [
    {
      "number": 1,
      "board_number": "А123АА123",
      "state_number": "1234",
      "model": "ПАЗ-3205",
      "built": "2020",
      "since": "2021-01-15",
      "note": "Замена двигателя в 2023",
      "state": "active",
      "owner": "ИП Петров",
      "created_at": "2024-01-15 10:30:00"
    }
  ]
}
```

#### Создать транспортное средство
```http
POST /api/vehicle/{company_name}
```

**Тело запроса:**
```json
{
  "board_number": "А123АА123",
  "state_number": "1234",
  "model": "ПАЗ-3205",
  "built": "2020",
  "since": "2021-01-15",
  "note": "Замена двигателя в 2023",
  "state": "active",
  "owner": "ИП Петров"
}
```

**Обязательные поля:** `board_number`

**Возможные значения `state`:**
- `active` - активен
- `inactive` - неактивен
- `repair` - в ремонте

#### Управление транспортным средством
- `GET /api/vehicle/{company_name}/{vehicle_id}` - получить информацию
- `PUT /api/vehicle/{company_name}/{vehicle_id}` - обновить информацию
- `DELETE /api/vehicle/{company_name}/{vehicle_id}` - удалить ТС

### Коэффициенты

#### Получить все коэффициенты
```http
GET /api/coefs/{company_name}
```

**Ответ:**
```json
{
  "status": "ok",
  "coefs": [
    {
      "id": 1,
      "post": "водитель",
      "coef": 1.0,
      "created_at": "2024-01-15 10:30:00"
    },
    {
      "id": 2,
      "post": "кондуктор",
      "coef": 0.8,
      "created_at": "2024-01-15 10:30:00"
    }
  ]
}
```

#### Создать коэффициент
```http
POST /api/coef/{company_name}
```

**Тело запроса:**
```json
{
  "post": "водитель",
  "coef": 1.0
}
```

**Обязательные поля:** `post`, `coef`

#### Управление коэффициентом
- `PUT /api/coef/{company_name}/{coef_id}` - обновить коэффициент
- `DELETE /api/coef/{company_name}/{coef_id}` - удалить коэффициент

### Статистика

#### Получить всю статистику компании
```http
GET /api/statistics/{company_name}
```

**Ответ:**
```json
{
  "status": "ok",
  "statistics": [
    {
      "id": 1,
      "user_name": "Иван Иванов",
      "post": "водитель",
      "total_salary": 150000.0,
      "period_salary": 25000.0,
      "total_round_trips": 300,
      "period_round_trips": 50,
      "total_passengers": 7200,
      "period_passengers": 1200
    }
  ]
}
```

#### Получить статистику пользователя
```http
GET /api/statistics/{company_name}/{user_name}
```

#### Прямое обновление статистики
```http
PUT /api/statistics/{company_name}/user/{user_name}
```

**Тело запроса:**
```json
{
  "total_salary": 160000.0,
  "period_salary": 30000.0,
  "total_round_trips": 350,
  "period_round_trips": 60
}
```

**Доступные поля для обновления:**
- `total_salary` - общая зарплата
- `period_salary` - зарплата за период
- `total_round_trips` - общее количество рейсов
- `period_round_trips` - рейсы за период
- `total_passengers` - общее количество пассажиров
- `period_passengers` - пассажиры за период

#### Сбросить периодическую статистику
```http
POST /api/statistics/{company_name}/reset
```

**Сбрасывает:** `period_salary`, `period_round_trips`, `period_passengers` у всех пользователей.

### Конфигурация

#### Получить все настройки
```http
GET /api/config/{company_name}
```

**Ответ:**
```json
{
  "status": "ok",
  "configs": {
    "passanger_cost": "2000"
  }
}
```

#### Обновить настройку
```http
POST /api/config/{company_name}
```

**Тело запроса:**
```json
{
  "key": "passanger_cost",
  "value": "2500"
}
```

**Важные настройки:**
- `passanger_cost` - стоимость одного пассажира (по умолчанию: 2000)

---

## HTML страницы

### Дашборд пользователя
```
https://rotorbus.ru/dashboard/{username}
```

### Список пользователей
```
https://rotorbus.ru/users
```

### Главная страница
```
https://rotorbus.ru/
```

### Скачать базу данных (архив)
```
https://rotorbus.ru/db
```

---

## Особенности расчета зарплаты

При верификации отчета происходит автоматический расчет зарплаты по формуле:

```
Зарплата = (рейсы × оплата_за_рейс + пассажиры × стоимость_пассажира) × коэффициент_должности
```

**Где:**
- `рейсы` - количество рейсов из отчета
- `оплата_за_рейс` - зарплата за маршрут
- `пассажиры` - количество пассажиров из отчета
- `стоимость_пассажира` - настройка `passanger_cost` из конфигурации
- `коэффициент_должности` - коэффициент для должности пользователя

---

## Примеры использования

### Пример 1: Создание и верификация отчета

```javascript
// 1. Создаем отчет
const createReport = async () => {
  const response = await fetch('https://rotorbus.ru/api/report/company1', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_name: 'Иван Иванов',
      date: '2024-01-15',
      route: 'Маршрут №1',
      num_round_trips: 5,
      num_passengers: 120,
      proof: 'https://example.com/photo.jpg'
    })
  });
  return await response.json();
};

// 2. Верифицируем отчет (ID получен из предыдущего запроса)
const verifyReport = async (reportId) => {
  const response = await fetch(`https://rotorbus.ru/api/report/verify/company1/${reportId}`, {
    method: 'POST'
  });
  return await response.json();
};
```

### Пример 2: Получение статистики с фильтрацией

```javascript
// Получить все неверифицированные отчеты для конкретного пользователя
const getReports = async () => {
  const response = await fetch(
    'https://rotorbus.ru/api/reports/company1?user_name=Иван&status=not_verified'
  );
  const data = await response.json();
  
  if (data.status === 'ok') {
    data.reports.forEach(report => {
      console.log(`Отчет ${report.id}: ${report.num_round_trips} рейсов, ${report.num_passengers} пассажиров`);
    });
  }
};
```

### Пример 3: Работа с пользователями

```javascript
// Получить всех пользователей и отфильтровать по должности
const getDrivers = async () => {
  const response = await fetch('https://rotorbus.ru/api/users/company1');
  const data = await response.json();
  
  if (data.status === 'ok') {
    const drivers = data.users.filter(user => user.post === 'водитель');
    console.log(`Найдено водителей: ${drivers.length}`);
  }
};
```

---

## Ошибки и их обработка

### Частые ошибки и их причины:

| Код ошибки | Причина | Решение |
|------------|---------|---------|
| `"company does not exist"` | Компания не найдена | Проверьте название компании |
| `"user does not exist"` | Пользователь не найден | Проверьте ID или имя пользователя |
| `"route does not exist"` | Маршрут не найден | Проверьте название маршрута |
| `"invalid login or password"` | Неверные учетные данные | Проверьте логин и пароль |
| `"report not found or already verified"` | Отчет не найден или уже верифицирован | Проверьте ID отчета и его статус |
| `"database error"` | Внутренняя ошибка базы данных | Обратитесь к администратору |
| `"key is empty"` | Пустой ключ в запросе | Укажите значение для ключа |

### Рекомендации по обработке ошибок:

1. **Всегда проверяйте поле `status`** в ответе
2. **Используйте try-catch** для сетевых запросов
3. **Показывайте пользователю понятные сообщения** на основе `message`
4. **Логируйте ошибки** для отладки

---

## Примечания для разработчика

### Рекомендуемая структура фронтенда:

```
src/
├── api/
│   ├── client.js          # Базовый клиент API
│   ├── company.js         # Работа с компаниями
│   ├── users.js           # Работа с пользователями
│   ├── routes.js          # Работа с маршрутами
│   ├── reports.js         # Работа с отчетами
│   ├── vehicles.js        # Работа с транспортом
│   ├── statistics.js      # Работа со статистикой
│   └── config.js          # Работа с конфигурацией
├── utils/
│   ├── auth.js            # Функции аутентификации
│   ├── validation.js      # Валидация данных
│   └── formatters.js      # Форматирование данных
└── constants/
    └── api.js             # Константы API
```

### Пример базового клиента API:

```javascript
class ApiClient {
  constructor(baseUrl = 'https://rotorbus.ru') {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });
      const data = await response.json();
      
      if (data.status === 'error') {
        throw new Error(data.message);
      }
      
      return data;
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Компании
  getCompanies() {
    return this.request('/api/companies');
  }

  // Пользователи
  getUsers(company) {
    return this.request(`/api/users/${company}`);
  }

  // Отчеты
  getReports(company, filters = {}) {
    const params = new URLSearchParams(filters).toString();
    const endpoint = `/api/reports/${company}${params ? `?${params}` : ''}`;
    return this.request(endpoint);
  }

  // ... остальные методы
}
```

### Важные моменты:

1. **Кэширование:** Рекомендуется кэшировать статические данные (маршруты, пользователей)
2. **Оптимистичные обновления:** Для улучшения UX можно применять оптимистичные обновления интерфейса
3. **Обработка соединения:** Добавьте обработку потери интернет-соединения
4. **Лоадеры:** Показывайте индикаторы загрузки для долгих операций
5. **Пагинация:** Для больших списков реализуйте пагинацию на фронтенде

### Тестирование:

Для тестирования API можно использовать инструменты:
- Postman
- Insomnia
- curl (для быстрых проверок)

### Мониторинг:

Рекомендуется отслеживать:
- Количество ошибок API
- Время ответа сервера
- Популярные эндпоинты
- Частоту использования функций

---

**Последнее обновление:** Январь 2024  
**Версия API:** 1.0  
**Поддержка:** Для вопросов обращайтесь к администратору системы