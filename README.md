# TransDigital
## ТрансДиджитал
API находится на [transdigital.pythonanywhere.com](https://transdigital.pythonanywhere.com/)

## Документация API для фронтенд-разработчика

### Общая информация
Документация описывает API для работы с пользователями в системе. Все запросы выполняются методом POST.

### Базовые параметры
* **Endpoint**: `/api/`
* **Метод**: POST (если не указано иное)
* **Формат данных**: JSON

### Доступные эндпоинты

#### 1. Добавление пользователя
**URL**: `/api/add_user/{company}`

**Параметры**:
* **company** (path) - название компании
* **name** (body) - имя пользователя
* **password** (body) - пароль пользователя

**Пример запроса**:
```javascript
fetch('https://transdigital.pythonanywhere.com/api/add_user/rotor', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'testuser',
    password: '123456'
  })
})
```

**Ответ**:
```json
{
  "status": "ok",
  "message": "user added"
}
// или
{
  "status": "error",
  "message": "user already exists"
}
```

#### 2. Обновление пользователя
**URL**: `/api/update_user/{company}`

**Параметры**:
* **company** (path) - название компании
* **name** (body) - имя пользователя
* **password** (body) - новый пароль

**Пример запроса**:
```javascript
fetch('https://transdigital.pythonanywhere.com/api/update_user/rotor', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'testuser',
    password: 'newpassword'
  })
})
```

#### 3. Удаление пользователя
**URL**: `/api/delete_user/{company}`

**Параметры**:
* **company** (path) - название компании
* **name** (body) - имя пользователя

**Пример запроса**:
```javascript
fetch('https://transdigital.pythonanywhere.com/api/delete_user/rotor', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'testuser'
  })
})
```

#### 4. Получение информации о пользователе
**URL**: `/api/get_user/{company}`

**Параметры**:
* **company** (path) - название компании
* **name** (body) - имя пользователя

**Пример ответа**:
```json
{
  "status": "ok",
  "id": "1",
  "name": "testuser",
  "password": "123456"
}
```

#### 5. Получение всех пользователей
**URL**: `/api/get_all_users/{company}`

**Параметры**:
* **company** (path) - название компании

**Пример ответа**:
```json
{
  "status": "ok",
  "users": [
    {
      "id": "1",
      "name": "testuser",
      "password": "123456"
    },
    {
      "id": "2",
      "name": "admin",
      "password": "adminpass"
    }
  ]
}
```

### Обработка ошибок
Все ошибки возвращаются в следующем формате:
```json
{
  "status": "error",
  "message": "описание ошибки"
}
```

Возможные ошибки:
* **name or password is empty** - пустые обязательные поля
* **company does not exist** - несуществующая компания
* **user does not exist** - пользователь не найден
* **user already exists** - пользователь уже существует

### Рекомендации
1. Всегда проверяйте статус ответа перед обработкой данных
2. Обрабатывайте ошибки на стороне фронтенда
3. Используйте валидацию данных перед отправкой на сервер
