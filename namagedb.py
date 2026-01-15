# from flask import Flask
# app = Flask(__name__)
# app.config['JSON_AS_ASCII'] = False
# from flask import jsonify
# @app.route("/task", methods=['GET'])
# def get_task():
#     vals = {"value": "Привет!"}
#     return jsonify(vals)
# if __name__ == "__main__":
#     app.run()

import sqlite3
from os import path

con = sqlite3.connect(path.join("database", "rotor.db"))
cur = con.cursor()

users = cur.execute("SELECT * FROM users").fetchall()

cur.close()
con.commit()
con.close()

import os
os.system("rm ./database/rotor.db")

print(*users, sep="\n")

input("Press enter to continue...")

from mainlib.database import INIT
INIT()



con = sqlite3.connect(path.join("database", "rotor.db"))
cur = con.cursor()

for user in users:
    args = list(user)[1:]
    args[5] = args[5][0]
    cur.execute("INSERT INTO users (name, password, post, account, vk, disciplinary_actions, note) VALUES (?, ?, ?, ?, ?, ?, ?)", args)

cur.close()
con.commit()
con.close()
