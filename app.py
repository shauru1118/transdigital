from flask import Flask, render_template, send_file, request, jsonify
from flask_cors import CORS
from mainlib import database
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Инициализируем все базы данных при запуске
database.INIT()

app.config["JSON_AS_ASCII"] = False
app.config["JSON_SORT_KEYS"] = False

# ========== WEB ROUTES ==========

@app.route("/", methods=["GET"])
def index():
    """Главная страница"""
    return render_template("index.html")

@app.route("/favicon.ico", methods=["GET"])
def favicon():
    """Favicon"""
    return send_file("static/favicon.ico")

@app.route("/db", methods=["GET"])
def download_database():
    """Скачать базу данных в виде архива"""
    import shutil
    shutil.make_archive("database", "zip", "database")
    return send_file("database.zip")

# ========== API ROUTES ==========

def _get_db_path(company: str):
    """Вспомогательная функция для получения пути к БД"""
    db_path = database.get_db_path(company)
    if not db_path:
        return None, jsonify({"status": "error", "message": "company does not exist"})
    return db_path, None

# ----- COMPANY ENDPOINTS -----

@app.route("/api/companies", methods=["GET"])
def get_companies():
    """Получить список всех компаний"""
    return jsonify({"status": "ok", "companies": database.get_companies()})

@app.route("/api/company", methods=["POST"])
def add_company():
    """Добавить новую компанию"""
    data = request.get_json()
    company = data.get("company", "").strip()
    
    if not company:
        return jsonify({"status": "error", "message": "company name is empty"})
    
    return jsonify(database.add_company(company))

@app.route("/api/company/<string:company>", methods=["DELETE"])
def delete_company(company: str):
    """Удалить компанию"""
    return jsonify(database.delete_company(company))

# ----- CONFIG ENDPOINTS -----

@app.route("/api/config/<string:company>", methods=["GET"])
def get_configs(company: str):
    """Получить все конфигурации компании"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.get_configs(db_path))

@app.route("/api/config/<string:company>", methods=["POST"])
def update_config(company: str):
    """Обновить конфигурацию"""
    data = request.get_json()
    key = data.get("key", "").strip()
    value = data.get("value", "").strip()
    
    if not key:
        return jsonify({"status": "error", "message": "key is empty"})
    
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.set_config(db_path, key, value))

# ----- USER ENDPOINTS -----

@app.route("/api/users/<string:company>", methods=["GET"])
def get_users(company: str):
    """Получить всех пользователей компании"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    users = database.get_users(db_path)
    return jsonify({"status": "ok", "users": users})

@app.route("/api/user/<string:company>", methods=["POST"])
def add_user(company: str):
    """Добавить нового пользователя"""
    data = request.get_json()
    
    required_fields = ["name", "password", "post"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"status": "error", "message": f"{field} is required"})
    
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.add_user(
        db_path,
        name=data["name"],
        password=data["password"],
        post=data["post"],
        account=data.get("account", ""),
        vk=data.get("vk", ""),
        disciplinary_actions=data.get("disciplinary_actions", "0"),
        note=data.get("note", "")
    ))

@app.route("/api/user/<string:company>/<string:user_id>", methods=["GET"])
def get_user(company: str, user_id: str):
    """Получить информацию о пользователе"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.get_user(db_path, user_id=user_id))

@app.route("/api/user/<string:company>/<string:user_id>", methods=["PUT"])
def update_user(company: str, user_id: str):
    """Обновить информацию о пользователе"""
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "no data provided"})
    
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    # Удаляем недопустимые поля
    data.pop("id", None)
    data.pop("created_at", None)
    
    return jsonify(database.update_user(db_path, user_id, **data))

@app.route("/api/user/<string:company>/<string:user_id>", methods=["DELETE"])
def delete_user(company: str, user_id: str):
    """Удалить пользователя"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.delete_user(db_path, user_id))

# ----- STATISTICS ENDPOINTS -----

@app.route("/api/statistics/<string:company>", methods=["GET"])
def get_statistics(company: str):
    """Получить всю статистику"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.get_statistics(db_path))

@app.route("/api/statistics/<string:company>/<string:user_name>", methods=["GET"])
def get_user_statistics(company: str, user_name: str):
    """Получить статистику пользователя"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.get_user_statistics(db_path, user_name))

@app.route("/api/statistics/<string:company>/reset", methods=["POST"])
def reset_period_statistics(company: str):
    """Сбросить периодическую статистику"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.reset_period_statistics(db_path))

# ----- VEHICLE ENDPOINTS -----

@app.route("/api/vehicles/<string:company>", methods=["GET"])
def get_vehicles(company: str):
    """Получить все транспортные средства"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.get_vehicles(db_path))

@app.route("/api/vehicle/<string:company>", methods=["POST"])
def add_vehicle(company: str):
    """Добавить новое транспортное средство"""
    data = request.get_json()
    
    if not data.get("board_number"):
        return jsonify({"status": "error", "message": "board_number is required"})
    
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.add_vehicle(
        db_path,
        board_number=data["board_number"],
        state_number=data.get("state_number", ""),
        model=data.get("model", ""),
        built=data.get("built", ""),
        since=data.get("since", ""),
        note=data.get("note", ""),
        state=data.get("state", "active"),
        owner=data.get("owner", "")
    ))

@app.route("/api/vehicle/<string:company>/<string:vehicle_id>", methods=["GET"])
def get_vehicle(company: str, vehicle_id: str):
    """Получить информацию о транспортном средстве"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.get_vehicle(db_path, vehicle_id=vehicle_id))

@app.route("/api/vehicle/<string:company>/<string:vehicle_id>", methods=["PUT"])
def update_vehicle(company: str, vehicle_id: str):
    """Обновить информацию о транспортном средстве"""
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "no data provided"})
    
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    # Удаляем недопустимые поля
    data.pop("number", None)
    data.pop("created_at", None)
    
    return jsonify(database.update_vehicle(db_path, vehicle_id, **data))

@app.route("/api/vehicle/<string:company>/<string:vehicle_id>", methods=["DELETE"])
def delete_vehicle(company: str, vehicle_id: str):
    """Удалить транспортное средство"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.delete_vehicle(db_path, vehicle_id))

# ----- ROUTE ENDPOINTS -----

@app.route("/api/routes/<string:company>", methods=["GET"])
def get_routes(company: str):
    """Получить все маршруты"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.get_routes(db_path))

@app.route("/api/route/<string:company>", methods=["POST"])
def add_route(company: str):
    """Добавить новый маршрут"""
    data = request.get_json()
    
    if not data.get("route") or not data.get("salary"):
        return jsonify({"status": "error", "message": "route and salary are required"})
    
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    try:
        salary = float(data["salary"])
    except ValueError:
        return jsonify({"status": "error", "message": "salary must be a number"})
    
    return jsonify(database.add_route(db_path, data["route"], salary))

@app.route("/api/route/<string:company>/<string:route_id>", methods=["GET"])
def get_route(company: str, route_id: str):
    """Получить информацию о маршруте"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.get_route(db_path, route_id=route_id))

@app.route("/api/route/<string:company>/<string:route_id>", methods=["PUT"])
def update_route(company: str, route_id: str):
    """Обновить информацию о маршруте"""
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "no data provided"})
    
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    # Удаляем недопустимые поля
    data.pop("id", None)
    data.pop("created_at", None)
    
    return jsonify(database.update_route(db_path, route_id, **data))

@app.route("/api/route/<string:company>/<string:route_id>", methods=["DELETE"])
def delete_route(company: str, route_id: str):
    """Удалить маршрут"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.delete_route(db_path, route_id))

@app.route("/api/route/salary/<string:company>", methods=["POST"])
def get_route_salary(company: str):
    """Получить зарплату для маршрута"""
    data = request.get_json()
    
    if not data.get("route"):
        return jsonify({"status": "error", "message": "route is required"})
    
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.get_route_salary(db_path, data["route"]))

# ----- REPORT ENDPOINTS -----

@app.route("/api/reports/<string:company>", methods=["GET"])
def get_reports(company: str):
    """Получить все отчеты"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    user_name = request.args.get("user_name")
    status = request.args.get("status")
    
    return jsonify(database.get_reports(db_path, user_name, status))

@app.route("/api/report/<string:company>", methods=["POST"])
def add_report(company: str):
    """Добавить новый отчет"""
    data = request.get_json()
    
    required_fields = ["user_name", "date", "route", "num_round_trips", "num_passengers"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"status": "error", "message": f"{field} is required"})
    
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    try:
        num_round_trips = int(data["num_round_trips"])
        num_passengers = int(data["num_passengers"])
    except ValueError:
        return jsonify({"status": "error", "message": "num_round_trips and num_passengers must be numbers"})
    
    return jsonify(database.add_report(
        db_path,
        user_name=data["user_name"],
        date=data["date"],
        route=data["route"],
        num_round_trips=num_round_trips,
        num_passengers=num_passengers,
        proof=data.get("proof", "")
    ))

@app.route("/api/report/<string:company>/<string:report_id>", methods=["GET"])
def get_report(company: str, report_id: str):
    """Получить информацию об отчете"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    # Реализация будет зависеть от того, как вы хотите получать конкретный отчет
    # В текущей версии database.py нет функции get_report_by_id
    # Можно добавить или использовать get_reports с фильтрацией
    
    reports = database.get_reports(db_path)
    if reports["status"] == "error":
        return jsonify(reports)
    
    for report in reports.get("reports", []):
        if str(report.get("id")) == report_id:
            return jsonify({"status": "ok", "report": report})
    
    return jsonify({"status": "error", "message": "report not found"})

@app.route("/api/report/<string:company>/<string:report_id>", methods=["PUT"])
def update_report(company: str, report_id: str):
    """Обновить информацию об отчете"""
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "no data provided"})
    
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    # Удаляем недопустимые поля
    data.pop("id", None)
    data.pop("created_at", None)
    data.pop("verified_at", None)
    
    return jsonify(database.update_report(db_path, report_id, **data))

@app.route("/api/report/<string:company>/<string:report_id>", methods=["DELETE"])
def delete_report(company: str, report_id: str):
    """Удалить отчет"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.delete_report(db_path, report_id))

@app.route("/api/report/verify/<string:company>/<string:report_id>", methods=["POST"])
def verify_report(company: str, report_id: str):
    """Верифицировать отчет"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.verify_report(db_path, report_id))

@app.route("/api/report/reject/<string:company>/<string:report_id>", methods=["POST"])
def reject_report(company: str, report_id: str):
    """Отклонить отчет"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.reject_report(db_path, report_id))

# ----- COEF ENDPOINTS -----

@app.route("/api/coefs/<string:company>", methods=["GET"])
def get_coefs(company: str):
    """Получить все коэффициенты"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.get_coefs(db_path))

@app.route("/api/coef/<string:company>", methods=["POST"])
def add_coef(company: str):
    """Добавить новый коэффициент"""
    data = request.get_json()
    
    if not data.get("post") or not data.get("coef"):
        return jsonify({"status": "error", "message": "post and coef are required"})
    
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    try:
        coef = float(data["coef"])
    except ValueError:
        return jsonify({"status": "error", "message": "coef must be a number"})
    
    return jsonify(database.add_coef(db_path, data["post"], coef))

@app.route("/api/coef/<string:company>/<string:coef_id>", methods=["PUT"])
def update_coef(company: str, coef_id: str):
    """Обновить коэффициент"""
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "no data provided"})
    
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    # Удаляем недопустимые поля
    data.pop("id", None)
    data.pop("created_at", None)
    
    return jsonify(database.update_coef(db_path, coef_id, **data))

@app.route("/api/coef/<string:company>/<string:coef_id>", methods=["DELETE"])
def delete_coef(company: str, coef_id: str):
    """Удалить коэффициент"""
    db_path, error = _get_db_path(company)
    if error:
        return error
    
    return jsonify(database.delete_coef(db_path, coef_id))

# ========== HTML PREVIEWS ==========

from mainlib.User import User

@app.route("/dashboard/<username>", methods=["GET"])
def dashboard(username: str):
    """Дашборд пользователя"""
    company = request.host.split(".")[0]
    db_path, error = _get_db_path(company)
    if error:
        return error[1]  # Возвращаем JSON ошибку
    
    user_dict = database.get_user(db_path, name=username)
    if user_dict["status"] == "error":
        return jsonify(user_dict)
    
    user = User(
        user_dict["id"], 
        user_dict["name"], 
        "",  # Пароль не передаем
        user_dict["post"], 
        user_dict.get("account", ""), 
        user_dict.get("vk", ""), 
        user_dict.get("disciplinary_actions", "0"), 
        user_dict.get("note", "")
    )
    
    return render_template("dashboard.html", company=company.capitalize(), user=user, url=request.url)

@app.route("/users", methods=["GET"])
def users_page():
    """Страница со списком пользователей"""
    company = request.host.split(".")[0]
    db_path, error = _get_db_path(company)
    if error:
        return error[1]  # Возвращаем JSON ошибку
    
    users_data = database.get_users(db_path)
    if not users_data:
        return jsonify({"status": "error", "message": "no users found"})
    
    users = []
    for user_data in users_data:
        users.append(User(
            id=user_data["id"],
            name=user_data["name"],
            password="",  # Пароль не передаем
            post=user_data["post"],
            account=user_data.get("account", ""),
            vk=user_data.get("vk", ""),
            disciplinary_actions=user_data.get("disciplinary_actions", "0"),
            note=user_data.get("note", "")
        ))
    
    return render_template("users.html", company=company.capitalize(), users=users, url=request.url)

if __name__ == "__main__":
    app.run(debug=True)