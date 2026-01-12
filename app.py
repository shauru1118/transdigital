from flask import Flask, render_template, send_file, request, jsonify, redirect, url_for
from flask_cors import CORS
from mainlib import database
import os

app = Flask(__name__)
CORS(app)
database.INIT()

app.config["JSON_AS_ASCII"] = False
app.config["JSON_SORT_KEYS"] = False



#! ---- WEB ----

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_file("static/favicon.ico")

@app.route("/db", methods=["GET"])
def db():
    import shutil
    shutil.make_archive("database", "zip", "database")
    zip_folder = send_file("database.zip")
    return zip_folder


#! ---- API ----

#* companys

@app.route("/api/add_company", methods=["POST"])
def add_company():
    data = request.get_json()
    company = data.get("company", "")
    if not company:
        return jsonify({"status":"error", "message":"company name is empty"})
    if database.get_db_path(company) != "":
        return jsonify({"status":"error", "message":"company already exists"})
    return jsonify(database.add_company(company))

@app.route("/api/delete_company", methods=["POST"])
def delete_company():
    data = request.get_json()
    company = data.get("company", "")
    if not company:
        return jsonify({"status":"error", "message":"company name is empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.delete_company(company))


#* users

@app.route("/api/add_user/<string:company>", methods=["POST"])
def add_user(company:str):
    data:dict = request.get_json()
    name = data.get("name", "")
    password = data.get("password", "")
    post = data.get("post", "")
    account = data.get("account", "")
    vk = data.get("vk", "")
    disciplinary_actions = data.get("disciplinary_actions", "0")
    note = data.get("note", "")
    if not name or not password or not post or not account or not vk or not disciplinary_actions or not note:
        return jsonify({"status":"error", "message":"some fields are empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.add_user(database.get_db_path(company), name, password, post, account, vk, disciplinary_actions, note))

@app.route("/api/update_user/<string:company>", methods=["POST"])
def update_user(company:str):
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})

    data:dict = request.get_json()
    id = data.get("id", "")

    if not id:
        return jsonify({"status":"error", "message":"id is empty"})

    user = database.get_user(database.get_db_path("rotor"), id=id)
    name = data.get("name",         user.get("name"))
    password = data.get("password", user.get("password"))
    post = data.get("post",         user.get("post"))
    account = data.get("account",   user.get("account"))
    vk = data.get("vk",             user.get("vk"))
    disciplinary_actions = data.get("disciplinary_actions", user.get("disciplinary_actions"))
    note = data.get("note",         user.get("note"))

    return jsonify(database.update_user(database.get_db_path(company), id, name, password, post, account, vk, disciplinary_actions, note))

@app.route("/api/delete_user/<string:company>", methods=["POST"])
def delete_user(company:str):
    data = request.get_json()
    id = data.get("id", "")
    if not id:
        return jsonify({"status":"error", "message":"name is empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.delete_user(database.get_db_path(company), id))

@app.route("/api/get_user/<string:company>", methods=["POST"])
def get_user(company:str):
    data = request.get_json()
    name = data.get("name", "")
    id = data.get("id", "")
    if not name and not id:
        return jsonify({"status":"error", "message":"name and id is empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    if id:
        return jsonify(database.get_user(database.get_db_path(company), id=id))
    if name:
        return jsonify(database.get_user(database.get_db_path(company), name=name))

@app.route("/api/get_users/<string:company>", methods=["GET"])
def get_users(company:str):
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    users = database.get_users(database.get_db_path(company))
    if len(users) == 0:
        return jsonify({
            "status":"error",
            "message":"no users found"
        })
    return jsonify({
        "status":"ok",
        "users":users
    })


#* vehicles

@app.route("/api/add_vehicle/<string:company>", methods=["POST"])
def add_vehicle(company:str):
    data = request.get_json()
    board_number = data.get("board_number", "")
    state_number = data.get("state_number", "")
    model = data.get("model", "")
    built = data.get("built", "")
    since = data.get("since", "")
    note = data.get("note", "")
    state = data.get("state", "")
    owner = data.get("owner", "")
    if not board_number:
        return jsonify({"status":"error", "message":"board_number is empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.add_vehicle(database.get_db_path(company), board_number, state_number, model, built, since, note, state, owner))

@app.route("/api/get_vehicles/<string:company>", methods=["GET"])
def get_vehicles(company:str):
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.get_vehicles(database.get_db_path(company)))

@app.route("/api/update_vehicle/<string:company>", methods=["POST"])
def update_vehicle(company:str):
    data = request.get_json()
    number = data.get("number", "")
    board_number = data.get("board_number", "")
    state_number = data.get("state_number", "")
    model = data.get("model", "")
    built = data.get("built", "")
    since = data.get("since", "")
    note = data.get("note", "")
    state = data.get("state", "")
    owner = data.get("owner", "")
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.update_vehicle(database.get_db_path(company), number, board_number, state_number, model, built, since, note, state, owner))

@app.route("/api/delete_vehicle/<string:company>", methods=["POST"])
def delete_vehicle(company:str):
    data = request.get_json()
    number = data.get("number", "")
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.delete_vehicle(database.get_db_path(company), number))


#* routes

@app.route("/api/get_routes/<string:company>", methods=["GET"])
def get_routes(company:str):
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.get_routes(database.get_db_path(company)))

@app.route("/api/add_route/<string:company>", methods=["POST"])
def add_route(company:str):
    data = request.get_json()
    route = data.get("route", "")
    if not route:
        return jsonify({"status":"error", "message":"route is empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.add_route(database.get_db_path(company), route))

@app.route("/api/delete_route/<string:company>", methods=["POST"])
def delete_route(company:str):
    data = request.get_json()
    route = data.get("route", "")
    if not route:
        return jsonify({"status":"error", "message":"route is empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.delete_route(database.get_db_path(company), route))


#* reports

@app.route("/api/get_reports/<string:company>", methods=["GET"])
def get_reports(company:str):
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.get_reports(database.get_db_path(company)))

@app.route("/api/add_report/<string:company>", methods=["POST"])
def add_report(company:str):
    data = request.get_json()
    user_name = data.get("user_name", "")
    date = data.get("date", "")
    route = data.get("route", "")
    num_round_trip = data.get("num_round_trip", "")
    num_passengers = data.get("num_passengers", "")
    proof = data.get("proof", "")
    if not all([user_name, date, route, num_round_trip, num_passengers, proof]):
        return jsonify({"status":"error", "message":"some fields are empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.add_report(database.get_db_path(company), user_name, date, route, num_round_trip, num_passengers, proof))

@app.route("/api/delete_report/<string:company>", methods=["POST"])
def delete_report(company:str):
    data = request.get_json()
    id = data.get("id", "")
    if not id:
        return jsonify({"status":"error", "message":"id is empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.delete_report(database.get_db_path(company), id))

@app.route("/api/verify_report/<string:company>", methods=["POST"])
def verify_report(company:str):
    data = request.get_json()
    id = data.get("id", "")
    if not id:
        return jsonify({"status":"error", "message":"id is empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.verify_report(database.get_db_path(company), id))

@app.route("/api/reject_report/<string:company>", methods=["POST"])
def reject_report(company:str):
    data = request.get_json()
    id = data.get("id", "")
    if not id:
        return jsonify({"status":"error", "message":"id is empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.reject_report(database.get_db_path(company), id))



#! HTML previews

from mainlib.User import User

@app.route("/dashboard/<username>", methods=["GET"])
def dashboard(username:str):
    company = request.host.split(".")[0]
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    user_dict = database.get_user(database.get_db_path(company), name=username)
    if user_dict["status"] == "error":
        return jsonify(user_dict)
    user = User(user_dict["id"], user_dict["name"], user_dict["password"], user_dict["post"], user_dict["account"], user_dict["vk"], user_dict["disciplinary_actions"], user_dict["note"])
    return render_template("dashboard.html", company=company.capitalize(), user=user, url=request.url)

@app.route("/users", methods=["GET"])
def users():
    company = request.host.split(".")[0]
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    users = []
    ans_users = database.get_users(database.get_db_path(company))
    if len(ans_users) == 0:
        return jsonify({
            "status":"error",
            "message":"no users found",
        })
    for user in ans_users:
        users.append(User(id=user["id"], name=user["name"], password="secure", post=user["post"], account=user["account"], vk=user["vk"],
            disciplinary_actions=user["disciplinary_actions"], note=user["note"]))
    return render_template("users.html", company=company.capitalize(), users=users, url=request.url)
