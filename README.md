# Документация по API для фронтенда

## Базовый URL
```
https://transdigital.pythonanywhere.com
```

## Общая информация

API предоставляет интерфейс для управления пользователями компаний. Все запросы, кроме GET, используют метод POST и принимают данные в формате JSON.

## Эндпоинты

### 1. Добавление пользователя
**Endpoint:** `POST /api/add_user/<company>`

**Параметры:**
- `company` (string) - название компании (например: "rotor")

**Тело запроса (JSON):**
```json
{
    "name": "string",
    "password": "string", 
    "post": "string",
    "account": "string",
    "vk": "string",
    "disciplinary_actions": "string",
    "note": "string"
}
```

**Ответ:**
```json
{
    "status": "ok",
    "message": "user added"
}
```
или
```json
{
    "status": "error",
    "message": "error description"
}
```

---

### 2. Обновление пользователя
**Endpoint:** `POST /api/update_user/<company>`

**Параметры:**
- `company` (string) - название компании

**Тело запроса (JSON):**
```json
{
    "name": "string",
    "password": "string",
    "post": "string", 
    "account": "string",
    "vk": "string",
    "disciplinary_actions": "string",
    "note": "string"
}
```

**Ответ:**
```json
{
    "status": "ok", 
    "message": "user updated"
}
```
или
```json
{
    "status": "error",
    "message": "error description"
}
```

---

### 3. Удаление пользователя
**Endpoint:** `POST /api/delete_user/<company>`

**Параметры:**
- `company` (string) - название компании

**Тело запроса (JSON):**
```json
{
    "name": "string"
}
```

**Ответ:**
```json
{
    "status": "ok",
    "message": "user deleted"
}
```
или
```json
{
    "status": "error", 
    "message": "error description"
}
```

---

### 4. Получение базовой информации о пользователе
**Endpoint:** `POST /api/get_user/<company>`

**Параметры:**
- `company` (string) - название компании

**Тело запроса (JSON):**
```json
{
    "name": "string"
}
```

**Ответ:**
```json
{
    "status": "ok",
    "name": "string",
    "password": "string"
}
```
или
```json
{
    "status": "error",
    "message": "error description"
}
```

---

### 5. Получение расширенной информации о пользователе
**Endpoint:** `POST /api/get_user_info/<company>`

**Параметры:**
- `company` (string) - название компании

**Тело запроса (JSON):**
```json
{
    "name": "string"
}
```

**Ответ:**
```json
{
    "status": "ok",
    "name": "string",
    "post": "string",
    "account": "string", 
    "vk": "string",
    "disciplinary_actions": "string",
    "note": "string"
}
```
или
```json
{
    "status": "error",
    "message": "error description"
}
```

---

### 6. Получение информации о всех пользователях компании
**Endpoint:** `GET /api/get_users_info/<company>`

**Параметры:**
- `company` (string) - название компании

**Тело запроса:** не требуется

**Ответ:**
```json
{
    "status": "ok",
    "users": [
        {
            "name": "string",
            "post": "string",
            "account": "string",
            "vk": "string", 
            "disciplinary_actions": "string",
            "note": "string"
        }
    ]
}
```
или
```json
{
    "status": "error",
    "message": "error description"
}
```

## Коды ошибок

- `some fields are empty` - не все обязательные поля заполнены
- `company does not exist` - указанная компания не существует
- `user already exists` - пользователь с таким именем уже существует
- `user does not exist` - пользователь не найден
- `no users found` - в компании нет пользователей

## Пример использования

```javascript
// Добавление пользователя
const response = await fetch('https://transdigital.pythonanywhere.com/api/add_user/rotor', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        name: 'Иван Иванов',
        password: 'password123',
        post: 'Менеджер',
        account: 'ivanov_i',
        vk: 'vk.com/ivanov',
        disciplinary_actions: 'Нет',
        note: 'Пример заметки'
    })
});

const result = await response.json();
console.log(result);
```

## Примечания

- Все строковые поля обязательны для заполнения
- Название компании в URL должно соответствовать зарегистрированным компаниям
- Для работы с API необходимо корректно обрабатывать CORS
- Все данные передаются в кодировке UTF-8