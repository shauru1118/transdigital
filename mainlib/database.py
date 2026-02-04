import sqlite3
import os
from os import path
from typing import Dict, List, Optional, Union, Any

DB_DIR: str = path.join(".", "database")
CP_DIR: str = path.join(".", "companys")
db_files: Dict[str, str] = {}

PASSANGER_COST = 2000

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(CP_DIR, exist_ok=True)

# Загрузка списка компаний
def _load_companies():
    list_file = path.join(CP_DIR, "list.txt")
    if not path.exists(list_file):
        with open(list_file, "w") as f:
            pass
    
    with open(list_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if " " not in line:
                db_files[line] = f"{line}.db"
            else:
                name, db_file = line.split(" ", 1)
                db_files[name] = db_file

_load_companies()

def get_db_connection(file_name: str):
    """Создает и возвращает соединение с базой данных"""
    connection = sqlite3.connect(file_name)
    connection.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
    return connection

def execute_query(file_name: str, query: str, params: tuple = ()) -> List[sqlite3.Row]:
    """Выполняет SQL запрос и возвращает результат"""
    with get_db_connection(file_name) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
    return result

def execute_command(file_name: str, command: str, params: tuple = ()) -> None:
    """Выполняет SQL команду (INSERT, UPDATE, DELETE)"""
    with get_db_connection(file_name) as conn:
        cursor = conn.cursor()
        cursor.execute(command, params)

# ========== COMPANY FUNCTIONS ==========

def add_company(name: str) -> Dict[str, str]:
    """Добавляет новую компанию"""
    if not name:
        return {"status": "error", "message": "company name is empty"}
    
    if name in db_files:
        return {"status": "error", "message": "company already exists"}
    
    if " " in name:
        return {"status": "error", "message": "company name cannot contain spaces"}
    
    name = name.lower()
    db_files[name] = f"{name}.db"
    
    # Сохраняем в файл
    with open(path.join(CP_DIR, "list.txt"), "a") as f:
        f.write(f"{name}\n")
    
    # Инициализируем базу данных для компании
    company_db_path = get_db_path(name)
    INIT(company_db_path)
    
    return {"status": "ok", "message": "company added"}

def delete_company(name: str) -> Dict[str, str]:
    """Удаляет компанию"""
    if name not in db_files:
        return {"status": "error", "message": "company does not exist"}
    
    # Удаляем файл базы данных
    db_path = path.join(DB_DIR, db_files[name])
    if path.exists(db_path):
        os.remove(db_path)
    
    # Удаляем из списка
    del db_files[name]
    
    # Обновляем файл со списком компаний
    with open(path.join(CP_DIR, "list.txt"), "w") as f:
        for company in db_files:
            f.write(f"{company}\n")
    
    return {"status": "ok", "message": "company deleted"}

def get_companies() -> List[str]:
    """Возвращает список всех компаний"""
    return list(db_files.keys())

# ========== DATABASE INITIALIZATION ==========

def INIT(db_path: str = None):
    """Инициализирует таблицы в базе данных"""
    if db_path:
        # Инициализация конкретной базы
        _init_database(db_path)
    else:
        # Инициализация всех баз
        for db_file in db_files.values():
            db_path = path.join(DB_DIR, db_file)
            _init_database(db_path)

def _init_database(db_path: str):
    """Инициализирует таблицы в конкретной базе данных"""
    tables = [
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            post TEXT NOT NULL,
            account TEXT,
            vk TEXT,
            disciplinary_actions TEXT DEFAULT '0',
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT UNIQUE NOT NULL,
            total_salary REAL DEFAULT 0,
            period_salary REAL DEFAULT 0,
            total_round_trips INTEGER DEFAULT 0,
            period_round_trips INTEGER DEFAULT 0,
            total_passengers INTEGER DEFAULT 0,
            period_passengers INTEGER DEFAULT 0,
            FOREIGN KEY (user_name) REFERENCES users(name) ON DELETE CASCADE
        )""",
        
        """CREATE TABLE IF NOT EXISTS vehicles (
            number INTEGER PRIMARY KEY AUTOINCREMENT,
            board_number TEXT UNIQUE NOT NULL,
            state_number TEXT,
            model TEXT,
            built TEXT,
            since TEXT,
            note TEXT,
            state TEXT DEFAULT 'active',
            owner TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route TEXT UNIQUE NOT NULL,
            salary REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            date TEXT NOT NULL,
            route TEXT NOT NULL,
            num_round_trips INTEGER NOT NULL,
            num_passengers INTEGER NOT NULL,
            proof TEXT,
            status TEXT DEFAULT 'not_verified',
            verified_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_name) REFERENCES users(name) ON DELETE CASCADE,
            FOREIGN KEY (route) REFERENCES routes(route) ON DELETE CASCADE
        )""",
        
        """CREATE TABLE IF NOT EXISTS coefs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post TEXT UNIQUE NOT NULL,
            coef REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    ]
    
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        for table_sql in tables:
            cursor.execute(table_sql)
        
        # Добавляем стандартные конфигурации
        cursor.execute("INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)", 
                      ("passanger_cost", str(PASSANGER_COST)))
            
    print(f"Database initialized: {db_path}")

# ========== UTILITY FUNCTIONS ==========

def get_db_path(company: str) -> Optional[str]:
    """Возвращает путь к базе данных компании"""
    if company not in db_files:
        return None
    return path.join(DB_DIR, db_files[company])

def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Конвертирует строку SQLite в словарь"""
    return {key: row[key] for key in row.keys()}

# ========== CONFIG FUNCTIONS ==========

def get_config(file_name: str, key: str) -> str:
    """Получает значение конфигурации по ключу"""
    query = "SELECT value FROM config WHERE key = ?"
    result = execute_query(file_name, query, (key,))
    return result[0]["value"] if result else ""

def get_configs(file_name: str) -> Dict[str, Any]:
    """Получает все конфигурации"""
    query = "SELECT key, value FROM config"
    result = execute_query(file_name, query)
    
    if not result:
        return {"status": "error", "message": "no configs found"}
    
    configs = {row["key"]: row["value"] for row in result}
    return {"status": "ok", "configs": configs}

def set_config(file_name: str, key: str, value: str) -> Dict[str, str]:
    """Устанавливает значение конфигурации"""
    query = "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)"
    execute_command(file_name, query, (key, value))
    return {"status": "ok", "message": "config updated"}

# ========== USER FUNCTIONS ==========

def get_user(file_name: str, user_id: str = None, name: str = None) -> Dict[str, Any]:
    """Получает информацию о пользователе по ID или имени"""
    if not user_id and not name:
        return {"status": "error", "message": "user_id or name required"}
    
    if user_id:
        query = "SELECT * FROM users WHERE id = ?"
        params = (user_id,)
    else:
        query = "SELECT * FROM users WHERE name = ?"
        params = (name,)
    
    result = execute_query(file_name, query, params)
    
    if not result:
        return {"status": "error", "message": "user does not exist"}
    
    user = _row_to_dict(result[0])
    # Не возвращаем пароль в ответе
    # user.pop("password", None)
    user["status"] = "ok"
    return user

def add_user(file_name: str, name: str, password: str, post: str, 
             account: str = "", vk: str = "", 
             disciplinary_actions: str = "0", note: str = "") -> Dict[str, str]:
    """Добавляет нового пользователя"""
    # Проверяем существование пользователя
    existing_user = get_user(file_name, name=name)
    if existing_user["status"] == "ok":
        return {"status": "error", "message": "user already exists"}
    
    query = """INSERT INTO users 
               (name, password, post, account, vk, disciplinary_actions, note) 
               VALUES (?, ?, ?, ?, ?, ?, ?)"""
    
    params = (name, password, post, account, vk, disciplinary_actions, note)
    
    try:
        execute_command(file_name, query, params)
        
        # Создаем запись статистики для пользователя
        stat_query = """INSERT INTO statistics (user_name) VALUES (?)"""
        execute_command(file_name, stat_query, (name,))
        
        return {"status": "ok", "message": "user added"}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "database error"}

def get_users(file_name: str) -> List[Dict[str, Any]]:
    """Получает список всех пользователей"""
    query = "SELECT id, name, post, account, vk, disciplinary_actions, note FROM users ORDER BY name"
    result = execute_query(file_name, query)
    return [_row_to_dict(row) for row in result]

def update_user(file_name: str, user_id: str, **kwargs) -> Dict[str, str]:
    """Обновляет информацию о пользователе"""
    if not kwargs:
        return {"status": "error", "message": "no fields to update"}
    
    # Проверяем существование пользователя
    user = get_user(file_name, user_id=user_id)
    if user["status"] == "error":
        return user
    
    # Строим SQL запрос
    set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
    query = f"UPDATE users SET {set_clause} WHERE id = ?"
    params = tuple(kwargs.values()) + (user_id,)
    
    execute_command(file_name, query, params)
    return {"status": "ok", "message": "user updated"}

def delete_user(file_name: str, user_id: str) -> Dict[str, str]:
    """Удаляет пользователя"""
    # Проверяем существование пользователя
    user = get_user(file_name, user_id=user_id)
    if user["status"] == "error":
        return user
    
    query = "DELETE FROM users WHERE id = ?"
    execute_command(file_name, query, (user_id,))
    return {"status": "ok", "message": "user deleted"}

def login(file_name: str, name: str, password: str) -> Dict[str, str]:
    """Проверяет логин и пароль"""
    query = "SELECT * FROM users WHERE name = ? AND password = ?"
    result = execute_query(file_name, query, (name, password))
    
    if not result:
        return {"status": "error", "message": "invalid login or password"}
    
    return {"status": "ok", "message": "login successful"}

# ========== STATISTICS FUNCTIONS ==========

def get_statistics(file_name: str) -> Dict[str, Any]:
    """Получает всю статистику"""
    query = """SELECT s.*, u.post 
               FROM statistics s 
               LEFT JOIN users u ON s.user_name = u.name 
               ORDER BY s.user_name"""
    
    result = execute_query(file_name, query)
    
    if not result:
        return {"status": "error", "message": "no statistics found"}
    
    stats = [_row_to_dict(row) for row in result]
    return {"status": "ok", "statistics": stats}

def get_user_statistics(file_name: str, user_name: str) -> Dict[str, Any]:
    """Получает статистику конкретного пользователя"""
    query = """SELECT s.*, u.post 
               FROM statistics s 
               LEFT JOIN users u ON s.user_name = u.name 
               WHERE s.user_name = ?"""
    
    result = execute_query(file_name, query, (user_name,))
    
    if not result:
        # Создаем запись статистики, если ее нет
        stat_query = "INSERT OR IGNORE INTO statistics (user_name) VALUES (?)"
        execute_command(file_name, stat_query, (user_name,))
        
        # Получаем созданную запись
        result = execute_query(file_name, query, (user_name,))
        if not result:
            return {"status": "error", "message": "failed to create statistics"}
    
    stat = _row_to_dict(result[0])
    stat["status"] = "ok"
    return stat

def update_user_statistics(file_name: str, user_name: str, 
                          salary: float = 0, round_trips: int = 0, 
                          passengers: int = 0, reset_period: bool = False) -> Dict[str, str]:
    """Обновляет статистику пользователя"""
    # Получаем текущую статистику
    stats = get_user_statistics(file_name, user_name)
    if stats["status"] == "error":
        return stats
    
    # Обновляем значения
    total_salary = stats.get("total_salary", 0) + salary
    total_round_trips = stats.get("total_round_trips", 0) + round_trips
    total_passengers = stats.get("total_passengers", 0) + passengers
    
    if reset_period:
        period_salary = salary
        period_round_trips = round_trips
        period_passengers = passengers
    else:
        period_salary = stats.get("period_salary", 0) + salary
        period_round_trips = stats.get("period_round_trips", 0) + round_trips
        period_passengers = stats.get("period_passengers", 0) + passengers
    
    query = """UPDATE statistics 
               SET total_salary = ?, period_salary = ?,
                   total_round_trips = ?, period_round_trips = ?,
                   total_passengers = ?, period_passengers = ?
               WHERE user_name = ?"""
    
    params = (total_salary, period_salary, total_round_trips, period_round_trips,
              total_passengers, period_passengers, user_name)
    
    execute_command(file_name, query, params)
    return {"status": "ok", "message": "statistics updated"}

def reset_period_statistics(file_name: str) -> Dict[str, str]:
    """Сбрасывает периодическую статистику для всех пользователей"""
    query = "UPDATE statistics SET period_salary = 0, period_round_trips = 0, period_passengers = 0"
    execute_command(file_name, query)
    return {"status": "ok", "message": "period statistics reset"}

def update_user_statistics_direct(file_name: str, user_name: str, **kwargs) -> Dict[str, str]:
    """Прямое обновление статистики пользователя по полям"""
    # Проверяем существование пользователя
    user_query = "SELECT name FROM users WHERE name = ?"
    user_result = execute_query(file_name, user_query, (user_name,))
    
    if not user_result:
        return {"status": "error", "message": "user does not exist"}
    
    # Получаем текущую статистику
    stats_query = "SELECT * FROM statistics WHERE user_name = ?"
    stats_result = execute_query(file_name, stats_query, (user_name,))
    
    # Если записи статистики нет, создаем ее
    if not stats_result:
        create_query = """INSERT INTO statistics 
                         (user_name, total_salary, period_salary, 
                          total_round_trips, period_round_trips, 
                          total_passengers, period_passengers) 
                         VALUES (?, 0, 0, 0, 0, 0, 0)"""
        execute_command(file_name, create_query, (user_name,))
    
    # Подготавливаем поля для обновления
    update_fields = []
    params = []
    
    allowed_fields = {
        'total_salary': 'total_salary',
        'period_salary': 'period_salary',
        'total_round_trips': 'total_round_trips',
        'period_round_trips': 'period_round_trips',
        'total_passengers': 'total_passengers',
        'period_passengers': 'period_passengers'
    }
    
    for key, value in kwargs.items():
        if key in allowed_fields:
            update_fields.append(f"{allowed_fields[key]} = ?")
            params.append(value)
    
    if not update_fields:
        return {"status": "error", "message": "no valid fields to update"}
    
    # Добавляем user_name в параметры для WHERE
    params.append(user_name)
    
    # Строим и выполняем запрос
    update_query = f"UPDATE statistics SET {', '.join(update_fields)} WHERE user_name = ?"
    
    try:
        execute_command(file_name, update_query, tuple(params))
        return {"status": "ok", "message": "statistics updated successfully"}
    except Exception as e:
        return {"status": "error", "message": f"database error: {str(e)}"}



# ========== VEHICLE FUNCTIONS ==========

def add_vehicle(file_name: str, board_number: str, state_number: str = "",
                model: str = "", built: str = "", since: str = "", 
                note: str = "", state: str = "active", owner: str = "") -> Dict[str, str]:
    """Добавляет новое транспортное средство"""
    # Проверяем существование транспортного средства
    existing = get_vehicle(file_name, board_number=board_number)
    if existing["status"] == "ok":
        return {"status": "error", "message": "vehicle already exists"}
    
    query = """INSERT INTO vehicles 
               (board_number, state_number, model, built, since, note, state, owner) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    
    params = (board_number, state_number, model, built, since, note, state, owner)
    
    try:
        execute_command(file_name, query, params)
        return {"status": "ok", "message": "vehicle added"}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "database error"}

def get_vehicle(file_name: str, vehicle_id: str = None, board_number: str = None) -> Dict[str, Any]:
    """Получает информацию о транспортном средстве"""
    if not vehicle_id and not board_number:
        return {"status": "error", "message": "vehicle_id or board_number required"}
    
    if vehicle_id:
        query = "SELECT * FROM vehicles WHERE number = ?"
        params = (vehicle_id,)
    else:
        query = "SELECT * FROM vehicles WHERE board_number = ?"
        params = (board_number,)
    
    result = execute_query(file_name, query, params)
    
    if not result:
        return {"status": "error", "message": "vehicle does not exist"}
    
    vehicle = _row_to_dict(result[0])
    vehicle["status"] = "ok"
    return vehicle

def get_vehicles(file_name: str) -> Dict[str, Any]:
    """Получает список всех транспортных средств"""
    query = "SELECT * FROM vehicles ORDER BY board_number"
    result = execute_query(file_name, query)
    
    if not result:
        return {"status": "error", "message": "no vehicles found"}
    
    vehicles = [_row_to_dict(row) for row in result]
    return {"status": "ok", "vehicles": vehicles}

def update_vehicle(file_name: str, vehicle_id: str, **kwargs) -> Dict[str, str]:
    """Обновляет информацию о транспортном средстве"""
    if not kwargs:
        return {"status": "error", "message": "no fields to update"}
    
    # Проверяем существование транспортного средства
    vehicle = get_vehicle(file_name, vehicle_id=vehicle_id)
    if vehicle["status"] == "error":
        return vehicle
    
    # Строим SQL запрос
    set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
    query = f"UPDATE vehicles SET {set_clause} WHERE number = ?"
    params = tuple(kwargs.values()) + (vehicle_id,)
    
    execute_command(file_name, query, params)
    return {"status": "ok", "message": "vehicle updated"}

def delete_vehicle(file_name: str, vehicle_id: str) -> Dict[str, str]:
    """Удаляет транспортное средство"""
    # Проверяем существование транспортного средства
    vehicle = get_vehicle(file_name, vehicle_id=vehicle_id)
    if vehicle["status"] == "error":
        return vehicle
    
    query = "DELETE FROM vehicles WHERE number = ?"
    execute_command(file_name, query, (vehicle_id,))
    return {"status": "ok", "message": "vehicle deleted"}

# ========== ROUTE FUNCTIONS ==========

def add_route(file_name: str, route: str, salary: float) -> Dict[str, str]:
    """Добавляет новый маршрут"""
    # Проверяем существование маршрута
    existing = get_route(file_name, route=route)
    if existing["status"] == "ok":
        return {"status": "error", "message": "route already exists"}
    
    query = "INSERT INTO routes (route, salary) VALUES (?, ?)"
    
    try:
        execute_command(file_name, query, (route, salary))
        return {"status": "ok", "message": "route added"}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "database error"}

def get_route(file_name: str, route_id: str = None, route: str = None) -> Dict[str, Any]:
    """Получает информацию о маршруте"""
    if not route_id and not route:
        return {"status": "error", "message": "route_id or route required"}
    
    if route_id:
        query = "SELECT * FROM routes WHERE id = ?"
        params = (route_id,)
    else:
        query = "SELECT * FROM routes WHERE route = ?"
        params = (route,)
    
    result = execute_query(file_name, query, params)
    
    if not result:
        return {"status": "error", "message": "route does not exist"}
    
    route_data = _row_to_dict(result[0])
    route_data["status"] = "ok"
    return route_data

def get_routes(file_name: str) -> Dict[str, Any]:
    """Получает список всех маршрутов"""
    query = "SELECT * FROM routes ORDER BY route"
    result = execute_query(file_name, query)
    
    if not result:
        return {"status": "error", "message": "no routes found"}
    
    routes = [_row_to_dict(row) for row in result]
    return {"status": "ok", "routes": routes}

def update_route(file_name: str, route_id: str, **kwargs) -> Dict[str, str]:
    """Обновляет информацию о маршруте"""
    if not kwargs:
        return {"status": "error", "message": "no fields to update"}
    
    # Проверяем существование маршрута
    route_data = get_route(file_name, route_id=route_id)
    if route_data["status"] == "error":
        return route_data
    
    # Строим SQL запрос
    set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
    query = f"UPDATE routes SET {set_clause} WHERE id = ?"
    params = tuple(kwargs.values()) + (route_id,)
    
    execute_command(file_name, query, params)
    return {"status": "ok", "message": "route updated"}

def delete_route(file_name: str, route_id: str) -> Dict[str, str]:
    """Удаляет маршрут"""
    # Проверяем существование маршрута
    route_data = get_route(file_name, route_id=route_id)
    if route_data["status"] == "error":
        return route_data
    
    query = "DELETE FROM routes WHERE id = ?"
    execute_command(file_name, query, (route_id,))
    return {"status": "ok", "message": "route deleted"}

def get_route_salary(file_name: str, route: str) -> Dict[str, Any]:
    """Получает зарплату для маршрута"""
    route_data = get_route(file_name, route=route)
    if route_data["status"] == "error":
        return route_data
    
    return {"status": "ok", "salary": route_data["salary"]}

# ========== REPORT FUNCTIONS ==========

def add_report(file_name: str, user_name: str, date: str, route: str,
               num_round_trips: int, num_passengers: int, proof: str = "") -> Dict[str, str]:
    """Добавляет новый отчет"""
    query = """INSERT INTO reports 
               (user_name, date, route, num_round_trips, num_passengers, proof, status) 
               VALUES (?, ?, ?, ?, ?, ?, ?)"""
    
    params = (user_name, date, route, num_round_trips, num_passengers, proof, "not_verified")
    
    try:
        execute_command(file_name, query, params)
        return {"status": "ok", "message": "report added"}
    except sqlite3.IntegrityError as e:
        return {"status": "error", "message": f"database error: {str(e)}"}

def get_reports(file_name: str, user_name: str = None, status: str = None) -> Dict[str, Any]:
    """Получает список отчетов"""
    conditions = []
    params = []
    
    if user_name:
        conditions.append("user_name = ?")
        params.append(user_name)
    
    if status:
        conditions.append("status = ?")
        params.append(status)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    query = f"""SELECT r.*, u.post, rt.salary as route_salary 
                FROM reports r 
                LEFT JOIN users u ON r.user_name = u.name 
                LEFT JOIN routes rt ON r.route = rt.route 
                WHERE {where_clause} 
                ORDER BY r.date DESC, r.created_at DESC"""
    
    result = execute_query(file_name, query, tuple(params))
    
    if not result:
        return {"status": "error", "message": "no reports found"}
    
    reports = [_row_to_dict(row) for row in result]
    return {"status": "ok", "reports": reports}

def update_report(file_name: str, report_id: str, **kwargs) -> Dict[str, str]:
    """Обновляет информацию об отчете"""
    if not kwargs:
        return {"status": "error", "message": "no fields to update"}
    
    # Проверяем существование отчета
    query = "SELECT id FROM reports WHERE id = ?"
    result = execute_query(file_name, query, (report_id,))
    
    if not result:
        return {"status": "error", "message": "report does not exist"}
    
    # Строим SQL запрос
    set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
    if "status" in kwargs and kwargs["status"] == "verified":
        kwargs["verified_at"] = "CURRENT_TIMESTAMP"
    
    query = f"UPDATE reports SET {set_clause} WHERE id = ?"
    params = tuple(kwargs.values()) + (report_id,)
    
    execute_command(file_name, query, params)
    return {"status": "ok", "message": "report updated"}

def delete_report(file_name: str, report_id: str) -> Dict[str, str]:
    """Удаляет отчет"""
    # Проверяем существование отчета
    query = "SELECT id FROM reports WHERE id = ?"
    result = execute_query(file_name, query, (report_id,))
    
    if not result:
        return {"status": "error", "message": "report does not exist"}
    
    query = "DELETE FROM reports WHERE id = ?"
    execute_command(file_name, query, (report_id,))
    return {"status": "ok", "message": "report deleted"}

def verify_report(file_name: str, report_id: str) -> Dict[str, str]:
    """Верифицирует отчет и обновляет статистику"""
    # Получаем отчет
    query = """SELECT r.*, u.post, rt.salary as route_salary, c.coef 
               FROM reports r 
               LEFT JOIN users u ON r.user_name = u.name 
               LEFT JOIN routes rt ON r.route = rt.route 
               LEFT JOIN coefs c ON u.post = c.post 
               WHERE r.id = ? AND r.status = 'not_verified'"""
    
    result = execute_query(file_name, query, (report_id,))
    
    if not result:
        return {"status": "error", "message": "report not found or already verified"}
    
    report = _row_to_dict(result[0])
    
    # Рассчитываем зарплату
    route_salary = float(report["route_salary"])
    num_round_trips = int(report["num_round_trips"])
    num_passengers = int(report["num_passengers"])
    coef = float(report["coef"]) if report["coef"] else 1.0
    passanger_cost = float(get_config(file_name, "passanger_cost"))
    
    salary = (num_round_trips * route_salary + num_passengers * passanger_cost) * coef
    
    # Обновляем статистику пользователя
    stats_result = update_user_statistics(
        file_name, 
        report["user_name"],
        salary=salary,
        round_trips=num_round_trips,
        passengers=num_passengers
    )
    
    if stats_result["status"] == "error":
        return stats_result
    
    # Обновляем статус отчета
    update_query = """UPDATE reports 
                      SET status = 'verified', verified_at = CURRENT_TIMESTAMP 
                      WHERE id = ?"""
    
    execute_command(file_name, update_query, (report_id,))
    
    return {"status": "ok", "message": "report verified", "calculated_salary": salary}

def reject_report(file_name: str, report_id: str) -> Dict[str, str]:
    """Отклоняет отчет"""
    return update_report(file_name, report_id, status="rejected")

# ========== COEF FUNCTIONS ==========

def add_coef(file_name: str, post: str, coef: float) -> Dict[str, str]:
    """Добавляет новый коэффициент"""
    # Проверяем существование коэффициента
    existing = get_coef(file_name, post=post)
    if existing["status"] == "ok":
        return {"status": "error", "message": "coef already exists for this post"}
    
    query = "INSERT INTO coefs (post, coef) VALUES (?, ?)"
    
    try:
        execute_command(file_name, query, (post, coef))
        return {"status": "ok", "message": "coef added"}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "database error"}

def get_coef(file_name: str, post: str) -> Dict[str, Any]:
    """Получает коэффициент для должности"""
    query = "SELECT * FROM coefs WHERE post = ?"
    result = execute_query(file_name, query, (post,))
    
    if not result:
        return {"status": "error", "message": "coef not found for this post"}
    
    coef_data = _row_to_dict(result[0])
    coef_data["status"] = "ok"
    return coef_data

def get_coefs(file_name: str) -> Dict[str, Any]:
    """Получает все коэффициенты"""
    query = "SELECT * FROM coefs ORDER BY post"
    result = execute_query(file_name, query)
    
    if not result:
        return {"status": "error", "message": "no coefs found"}
    
    coefs = [_row_to_dict(row) for row in result]
    return {"status": "ok", "coefs": coefs}

def update_coef(file_name: str, coef_id: str, **kwargs) -> Dict[str, str]:
    """Обновляет коэффициент"""
    if not kwargs:
        return {"status": "error", "message": "no fields to update"}
    
    # Проверяем существование коэффициента
    query = "SELECT id FROM coefs WHERE id = ?"
    result = execute_query(file_name, query, (coef_id,))
    
    if not result:
        return {"status": "error", "message": "coef does not exist"}
    
    # Строим SQL запрос
    set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
    query = f"UPDATE coefs SET {set_clause} WHERE id = ?"
    params = tuple(kwargs.values()) + (coef_id,)
    
    execute_command(file_name, query, params)
    return {"status": "ok", "message": "coef updated"}

def delete_coef(file_name: str, coef_id: str) -> Dict[str, str]:
    """Удаляет коэффициент"""
    # Проверяем существование коэффициента
    query = "SELECT id FROM coefs WHERE id = ?"
    result = execute_query(file_name, query, (coef_id,))
    
    if not result:
        return {"status": "error", "message": "coef does not exist"}
    
    query = "DELETE FROM coefs WHERE id = ?"
    execute_command(file_name, query, (coef_id,))
    return {"status": "ok", "message": "coef deleted"}

if __name__ == "__main__":
    INIT()
    print("All databases initialized")