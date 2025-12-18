import sqlite3
import os


DB_DIR:str = "database"
DB_FILES:dict = dict()

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs("companys", exist_ok=True)

if not os.path.exists("companys/list.txt"):
    with open("companys/list.txt", "w+") as f:
        f.write("")

with open("companys/list.txt", "r") as f:
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
    os.remove(os.path.join(DB_DIR, DB_FILES[name]))
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
        db_path = os.path.join(DB_DIR, db_file)
        create_table(db_path, "users", "name TEXT, password TEXT")
        create_table(db_path, "users_info", "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, post TEXT, " + 
                     "account TEXT, vk TEXT, disciplinary_actions TEXT, note TEXT")
        create_table(db_path, "vehicles", 
        "number INTEGER PRIMARY KEY AUTOINCREMENT, board_number TEXT, state_number TEXT, model TEXT, built TEXT, since TEXT, note TEXT, state TEXT, owner TEXT")
        create_table(db_path, "routes", "id INTEGER PRIMARY KEY AUTOINCREMENT, route TEXT")


#* db

def get_db_path(file_name:str):
    if file_name not in DB_FILES:
        return ""
    return os.path.join(DB_DIR, DB_FILES[file_name])

#* users

def add_user(file_name:str, name:str, password:str, post:str, account:str, vk:str, disciplinary_actions:str, note:str):
    ans = get_user(file_name, name)
    if ans["status"] == "ok":
        return {
            "status":"error",
            "message":"user already exists"
            }
    cmd = f"INSERT INTO users (name, password) VALUES (?, ?)"
    values = (name, password)
    do_cmd(file_name, cmd, values)
    cmd = f"INSERT INTO users_info (name, post, account, vk, disciplinary_actions, note) VALUES (?, ?, ?, ?, ?, ?)"
    values = (name, post, account, vk, disciplinary_actions, note)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"user added"
    }

def get_user(file_name:str, name:str):
    cmd = f"SELECT * FROM users WHERE name = ?"
    values = (name,)
    ans = do_cmd(file_name, cmd, values)
    if len(ans) == 0:
        return {
            "status":"error",
            "message":"user does not exist"
        }
    user = ans[0]
    return {
        "status":"ok",
        "name":str(user[1]),
        "password":str(user[2])
    }

def get_user_info(file_name:str, name:str):
    cmd = f"SELECT * FROM users_info WHERE name = ?"
    values = (name,)
    ans = do_cmd(file_name, cmd, values)
    if len(ans) == 0:
        return {
            "status":"error",
            "message":"user does not exist"
        }
    user = ans[0]
    return {
        "status":"ok",
        "name":str(user[1]),
        "post":str(user[2]),
        "account":str(user[3]),
        "vk":str(user[4]),
        "disciplinary_actions":str(user[5]),
        "note":str(user[6])
    }

def get_users_info(file_name:str):
    cmd = f"SELECT * FROM users_info"
    ans = do_cmd(file_name, cmd)
    if len(ans) == 0:
        return {
            "status":"error",
            "message":"no users found"
        }
    users = []
    for user in ans:
        users.append({
            "name":str(user[1]),
            "post":str(user[2]),
            "account":str(user[3]),
            "vk":str(user[4]),
            "disciplinary_actions":str(user[5]),
            "note":str(user[6])
        })
    return {
        "status":"ok",
        "users":users
    }

def delete_user(file_name:str, name:str):
    if len(get_user(file_name, name)) == 0:
        return {
            "status":"error",
            "message":"user does not exist"
        }
    cmd = f"DELETE FROM users WHERE name = ?"
    values = (name,)
    do_cmd(file_name, cmd, values)
    cmd = f"DELETE FROM users_info WHERE name = ?"
    values = (name,)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"user deleted"
    }

def update_user(file_name:str, name:str, password:str, post:str, account:str, vk:str, disciplinary_actions:str, note:str):

    if len(get_user(file_name, name)) == 0:
        return {
            "status":"error",
            "message":"user does not exist"
        }
    cmd = f"UPDATE users SET password = ? WHERE name = ?"
    values = (password, name)
    do_cmd(file_name, cmd, values)
    cmd = f"UPDATE users_info SET post = ?, account = ?, vk = ?, disciplinary_actions = ?, note = ? WHERE name = ?"
    values = (post, account, vk, disciplinary_actions, note, name)
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






if __name__ == "__main__":
    INIT()
    # print(get_user("database/rotor.db", "albert"))
    # print(get_users_info("database/rotor.db"))
    from pprint import pprint
    # print(add_vehicle("database/rotor.db", "numddrr", "", "", "", "", "", "", ""))
    print(update_vehicle("database/rotor.db", "3", "numddrr", "", "", "45", "", "", "4555", "alik"))
    pprint(get_vehicles("database/rotor.db"))

