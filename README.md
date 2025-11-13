# transdigital
all code for TransDigital




## Документация API для фронтенд-разработчика

### Общая информация
Документация описывает API для работы с пользователями в системе. Все запросы выполняются методом POST, за исключением получения списка всех пользователей.

### Базовые настройки
* **Версия API**: 1.0
* **URL API**: `/api/`
* **Метод аутентификации**: не требуется
* **Формат данных**: JSON

### Доступные эндпоинты

#### 1. Добавление пользователя
* **URL**: `/api/add_user/<company>`
* **Метод**: POST
* **Параметры URL**:
  * `company` - название компании (строка)
* **Тело запроса**:
```json
{
    "name": "string",
    "password": "string"
}
```
* **Ответ**:
```json
{
    "status": "ok/error",
    "message": "user added/user already exists"
}
```

#### 2. Обновление пользователя
* **URL**: `/api/update_user/<company>`
* **Метод**: POST
* **Параметры URL**:
  * `company` - название компании (строка)
* **Тело запроса**:
```json
{
    "name": "string",
    "password": "string"
}
```
* **Ответ**:
```json
{
    "status": "ok/error",
    "message": "user updated/user does not exist"
}
```

#### 3. Удаление пользователя
* **URL**: `/api/delete_user/<company>`
* **Метод**: POST
* **Параметры URL**:
  * `company` - название компании (строка)
* **Тело запроса**:
```json
{
    "name": "string"
}
```
* **Ответ**:
```json
{
    "status": "ok/error",
    "message": "user deleted/user does not exist"
}
```

#### 4. Получение информации о пользователе
* **URL**: `/api/get_user/<company>`
* **Метод**: POST
* **Параметры URL**:
  * `company` - название компании (строка)
* **Тело запроса**:
```json
{
    "name": "string"
}
```
* **Ответ**:
```json
{
    "status": "ok/error",
    "id": integer,
    "name": "string",
    "password": "string"
}
```

#### 5. Получение списка всех пользователей
* **URL**: `/api/get_all_users/<company>`
* **Метод**: GET
* **Параметры URL**:
  * `company` - название компании (строка)
* **Ответ**:
```json
{
    "status": "ok/error",
    "users": [
        {
            "id": integer,
            "name": "string",
            "password": "string"
        }
    ]
}
```

### Обработка ошибок
Возможные ошибки в ответах:
* `company does not exist` - компания не существует
* `name or password is empty` - пустые обязательные поля
* `user does not exist` - пользователь не найден
* `user already exists` - пользователь уже существует

### Пример использования (JavaScript)
```javascript
// Добавление пользователя
async function addUser(company, name, password) {
    try {
        const response = await fetch(`/api/add_user/${company}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                password: password
            })
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Получение всех пользователей
async function getAllUsers(company) {
    try {
        const response = await fetch(`/api/get_all_users/${company}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Ошибка:', error);
    }
}
```

### Рекомендации
* Всегда проверяйте статус ответа перед использованием данных
* Обрабатывайте ошибки на стороне клиента
* Используйте валидацию данных перед отправкой запросов
