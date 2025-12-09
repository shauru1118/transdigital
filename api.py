import flask
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from mainlib import database


app = Flask(__name__)
CORS(app)
database.INIT()

app.config["JSON_AS_ASCII"] = False
app.config["JSON_SORT_KEYS"] = False


@app.route("/api/add_user/<string:company>", methods=["POST"])
def add_user(company:str):
    data = request.get_json()
    name = data["name"]
    password = data["password"]
    post = data["post"]
    account = data["account"]
    vk = data["vk"]
    disciplinary_actions = data["disciplinary_actions"]
    if "note" in data:
        note = data["note"]
    else:
        note = "-"
    if not name or not password or not post or not account or not vk or not disciplinary_actions:
        return jsonify({"status":"error", "message":"some fields are empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.add_user(database.get_db_path(company), name, password, post, account, vk, disciplinary_actions, note))

@app.route("/api/update_user/<string:company>", methods=["POST"])
def update_user(company:str):
    data = request.get_json()
    name = data["name"]
    password = data["password"]
    post = data["post"]
    account = data["account"]
    vk = data["vk"]
    disciplinary_actions = data["disciplinary_actions"]
    note = data["note"]
    if not name or not password or not post or not account or not vk or not disciplinary_actions or not note:
        return jsonify({"status":"error", "message":"name or password is empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.update_user(database.get_db_path(company), name, password, post, account, vk, disciplinary_actions, note))

@app.route("/api/delete_user/<string:company>", methods=["POST"])
def delete_user(company:str):
    data = request.get_json()
    name = data["name"]
    if not name:
        return jsonify({"status":"error", "message":"name is empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.delete_user(database.get_db_path(company), name))

@app.route("/api/get_user/<string:company>", methods=["POST"])
def get_user(company:str):
    data = request.get_json()
    name = data["name"]
    if not name:
        return jsonify({"status":"error", "message":"name is empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.get_user(database.get_db_path(company), name))

@app.route("/api/get_user_info/<string:company>", methods=["POST"])
def get_user_info(company:str):
    data = request.get_json()
    name = data["name"]
    if not name:
        return jsonify({"status":"error", "message":"name is empty"})
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.get_user_info(database.get_db_path(company), name))

@app.route("/api/get_users_info/<string:company>", methods=["GET"])
def get_users_info(company:str):
    if database.get_db_path(company) == "":
        return jsonify({"status":"error", "message":"company does not exist"})
    return jsonify(database.get_users_info(database.get_db_path(company)))

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
