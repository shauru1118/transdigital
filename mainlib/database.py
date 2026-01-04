import sqlite3
import os
from os import path


DB_DIR:str = "database"
CP_DIR:str = "companys"
DB_FILES:dict = dict()

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(CP_DIR, exist_ok=True)

if not path.exists(path.join(CP_DIR, "list.txt")):
    with open(f"{CP_DIR}/list.txt", "w") as f:
        pass

with open(path.join(CP_DIR, "list.txt"), "r") as f:
    for line in f.readlines():
        if line.strip() == "":
            continue
        if len(line.split()) != 2:
            name = line.strip()
            DB_FILES[name] = f"{name}.db"
        else:
            name, db_file = line.strip().split(" ")
            DB_FILES[name] = db_file

def do_cmd(file_name:str, cmd:str, values:tuple=tuple()):
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()
    cursor.execute(cmd, values)
    result = cursor.fetchall()
    cursor.close()
    connection.commit()
    connection.close()
    return result

def add_company(name:str):
    if name in DB_FILES:
        return {
            "status":"error",
            "message":"company already exists"
        }
    if name.count(" ") != 0:
        return {
            "status":"error",
            "message":"company name cannot contain spaces"
        }
    name = name.lower()
    DB_FILES[name] = f"{name}.db"
    with open("companys/list.txt", "a") as f:
        f.write(f"{name}\n")
    INIT()
    return {
        "status":"ok",
        "message":"company added"
    }

def delete_company(name:str):
    if name not in DB_FILES:
        return {
            "status":"error",
            "message":"company does not exist"
        }
    os.remove(path.join(DB_DIR, DB_FILES[name]))
    del DB_FILES[name]
    with open("companys/list.txt", "w+") as f:
        for key in DB_FILES.keys():
            f.write(f"{key}\n")
    return {
        "status":"ok",
        "message":"company deleted"
    }

def create_table(file_name:str, table_name:str, variables:str):
    cmd = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
{variables}
)
"""
    do_cmd(file_name, cmd)


def INIT():
    for _, db_file in DB_FILES.items():
        db_path = path.join(DB_DIR, db_file)
        create_table(db_path, "users", "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, " \
        "password TEXT, post TEXT, account TEXT, vk TEXT, disciplinary_actions TEXT, note TEXT")
        create_table(db_path, "vehicles", 
        "number INTEGER PRIMARY KEY AUTOINCREMENT, board_number TEXT, state_number TEXT, model TEXT, built TEXT, since TEXT, note TEXT, state TEXT, owner TEXT")
        create_table(db_path, "routes", "id INTEGER PRIMARY KEY AUTOINCREMENT, route TEXT")
        create_table(db_path, "reports", "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
        "user_name TEXT, date TEXT, route TEXT, num_round_trips TEXT, num_passengers TEXT, proof TEXT, status TEXT")

#* db

def get_db_path(file_name:str):
    if file_name not in DB_FILES:
        return ""
    return path.join(DB_DIR, DB_FILES[file_name])

#* users

def get_user(file_name:str, name:str|None=None, id:str|None=None):
    if name:
        cmd = f"SELECT * FROM users WHERE name = ?"
        values = (name,)
        ans = do_cmd(file_name, cmd, values)
        if len(ans) == 0:
            return {
                "status":"error",
                "message":"user does not exist"
            }
        user = ans[0]
    if id:
        cmd = f"SELECT * FROM users WHERE id = ?"
        values = (id,)
        ans = do_cmd(file_name, cmd, values)
        if len(ans) == 0:
            return {
                "status":"error",
                "message":"user does not exist"
            }
        user = ans[0]
    return {
        "status":"ok",
        "id":str(user[0]),
        "name":str(user[1]),
        "password":str(user[2]),
        "post":str(user[3]),
        "account":str(user[4]),
        "vk":str(user[5]),
        "disciplinary_actions":str(user[6]),
        "note":str(user[7])
    }

def add_user(file_name:str, name:str, password:str, post:str, account:str, vk:str, disciplinary_actions:str, note:str):
    ans = get_user(file_name, name)
    if ans["status"] == "ok":
        return {
            "status":"error",
            "message":"user already exists"
            }
    cmd = f"INSERT INTO users (name, password, post, account, vk, disciplinary_actions, note) VALUES (?, ?, ?, ?, ?, ?, ?)"
    values = (name, password, post, account, vk, disciplinary_actions, note)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"user added"
    }

def get_users(file_name:str):
    cmd = f"SELECT * FROM users"
    ans = do_cmd(file_name, cmd)
    if len(ans) == 0:
        return {
            "status":"error",
            "message":"no users found"
        }
    users = []
    for user in ans:
        users.append({
            "id":str(user[0]),
            "name":str(user[1]),
            # "password":str(user[2]),
            "post":str(user[3]),
            "account":str(user[4]),
            "vk":str(user[5]),
            "disciplinary_actions":str(user[6]),
            "note":str(user[7])
        })
    return {
        "status":"ok",
        "users":users
    }

def delete_user(file_name:str, id:str):
    if len(get_user(file_name, id=id)) == 0:
        return {
            "status":"error",
            "message":"user does not exist"
        }
    cmd = f"DELETE FROM users WHERE id = ?"
    values = (id,)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"user deleted"
    }

def update_user(file_name:str, id:str, name:str, password:str, post:str, account:str, vk:str, disciplinary_actions:str, note:str):

    if len(get_user(file_name, id=id)) == 0:
        return {
            "status":"error",
            "message":"user does not exist"
        }
    cmd = f"UPDATE users SET name = ?, password = ?, post = ?, account = ?, vk = ?, disciplinary_actions = ?, note = ? WHERE id = ?"
    values = (password, name)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"user updated"
    }


#* vehicles

def add_vehicle(file_name:str, board_number:str, state_number:str, model:str, built:str, since:str, note:str, state:str, owner:str):
    ans = get_vehicle(file_name, None, board_number)
    if ans["status"] == "ok":
        return {
            "status":"error",
            "message":"vehicle already exists"
        }
    cmd = "INSERT INTO vehicles (board_number, state_number, model, built, since, note, state, owner) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    values = (board_number, state_number, model, built, since, note, state, owner)

    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"vehicle added"
    }

def get_vehicle(file_name:str, number:str|None=None, board_number:str|None=None):
    if board_number is not None:
        cmd = f"SELECT * FROM vehicles WHERE board_number = ?"
        values = (board_number,)
        ans = do_cmd(file_name, cmd, values)
    else:
        cmd = f"SELECT * FROM vehicles WHERE number = ?"
        values = (number,)
        ans = do_cmd(file_name, cmd, values)
    if len(ans) == 0:
        return {
            "status":"error",
            "message":"vehicle does not exist"
        }
    vehicle = ans[0]
    return {
        "status":"ok",
        "number":str(vehicle[0]),
        "board_number":str(vehicle[1]),
        "state_number":str(vehicle[2]),
        "model":str(vehicle[3]),
        "built":str(vehicle[4]),
        "since":str(vehicle[5]),
        "note":str(vehicle[6]),
        "state":str(vehicle[7]),
        "owner":str(vehicle[8])
    }

def get_vehicles(file_name:str):
    cmd = f"SELECT * FROM vehicles"
    ans = do_cmd(file_name, cmd)
    if len(ans) == 0:
        return {
            "status":"error",
            "message":"no vehicles found"
        }
    vehicles = []
    for vehicle in ans:
        vehicles.append({
            "number":str(vehicle[0]),
            "board_number":str(vehicle[1]),
            "state_number":str(vehicle[2]),
            "model":str(vehicle[3]),
            "built":str(vehicle[4]),
            "since":str(vehicle[5]),
            "note":str(vehicle[6]),
            "state":str(vehicle[7]),
            "owner":str(vehicle[8])
        })
    return {
        "status":"ok",
        "vehicles":vehicles
    }

def delete_vehicle(file_name:str, number:str):
    if get_vehicle(file_name, number)["status"] == "error":
        return {
            "status":"error",
            "message":"vehicle does not exist"
        }
    cmd = f"DELETE FROM vehicles WHERE number = ?"
    values = (number,)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"vehicle deleted"
    }

def update_vehicle(file_name:str, number:str, board_number:str, state_number:str, model:str, built:str, since:str, note:str, state:str, owner:str):
    ans = get_vehicle(file_name, number, None)
    if ans["status"] == "error":
        return {
            "status":"error",
            "message":"vehicle does not exist"
        }
    board_number = board_number or ans["board_number"]
    state_number = state_number or ans["state_number"]
    model = model or ans["model"]
    built = built or ans["built"]
    since = since or ans["since"]
    note = note or ans["note"]
    state = state or ans["state"]
    owner = owner or ans["owner"]
    cmd = f"UPDATE vehicles SET board_number = ?, state_number = ?, model = ?, built = ?, since = ?, note = ?, state = ?, owner = ? WHERE number = ?"
    values = (board_number, state_number, model, built, since, note, state, owner, number)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"vehicle updated"
    }


#* routes

def get_routes(file_name:str):
    cmd = f"SELECT * FROM routes"
    ans = do_cmd(file_name, cmd)
    if len(ans) == 0:
        return {
            "status":"error",
            "message":"no routes found"
        }
    routes = []
    for route in ans:
        routes.append(str(route[1]))
    return {
        "status":"ok",
        "routes":routes
    }

def add_route(file_name:str, route:str):
    ans = get_routes(file_name)
    if ans["status"] != "error" and route in ans["routes"]:
        return {
            "status":"error",
            "message":"route already exists"
        }
    cmd = "INSERT INTO routes (route) VALUES (?)"
    values = (route,)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"route added"
    }

def delete_route(file_name:str, route:str):
    ans = get_routes(file_name)
    if route not in ans["routes"]:
        return {
            "status":"error",
            "message":"route does not exist"
        }
    cmd = f"DELETE FROM routes WHERE route = ?"
    values = (route,)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"route deleted"
    }


#* reports

def get_reports(file_name:str):
    cmd = f"SELECT * FROM reports"
    ans = do_cmd(file_name, cmd)
    if len(ans) == 0:
        return {
            "status":"error",
            "message":"no reports found"
        }
    reports = []
    for report in ans:
        reports.append({
            "id":str(report[0]),
            "user_name":str(report[1]),
            "date":str(report[2]),
            "route":str(report[3]),
            "num_round_trips":str(report[4]),
            "num_passengers":str(report[5]),
            "proof":str(report[6]),
            "status":str(report[7])
        })
    return {
        "status":"ok",
        "reports":reports
    }

def add_report(file_name:str, user_name:str, date:str, route:str, num_round_trip:str, num_passengers:str, proof:str):
    cmd = "INSERT INTO reports (user_name, date, route, num_round_trips, num_passengers, proof, status) VALUES (?, ?, ?, ?, ?, ?, ?)"
    values = (user_name, date, route, num_round_trip, num_passengers, proof, "not verified")
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"report added"
    }

def delete_report(file_name:str, id:str):
    cmd = f"DELETE FROM reports WHERE id = ?"
    values = (id,)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"report deleted"
    }

def verify_report(file_name:str, id:str):
    cmd = f"UPDATE reports SET status = ? WHERE id = ?"
    values = ("verified", id)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"report verified"
    }

def reject_report(file_name:str, id:str):
    cmd = f"UPDATE reports SET status = ? WHERE id = ?"
    values = ("rejected", id)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"report rejected"
    }



def rebuild():
    DB = "rotor.db"
    import sqlite3

    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("SELECT * FROM users_info")
    users = cur.fetchall()

    cur.execute("SELECT password FROM users")
    passes = cur.fetchall()


    cur.execute("DROP TABLE users_info")
    cur.execute("DROP TABLE users")


    cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT, post TEXT, account TEXT, vk TEXT, disciplinary_actions TEXT, note TEXT)")

    for i in range(len(users)):
        cur.execute("INSERT INTO users (name, password, post, account, vk, disciplinary_actions, note) VALUES (?, ?, ?, ?, ?, ?, ?)", (users[i][1], passes[i][0], *users[i][2:]))

    con.commit()
    con.close()


if __name__ == "__main__":
    ans = get_users(get_db_path("rotor"))
    print(ans)
    print(*ans.get("users", ["NO USERS"]), sep="\n")

