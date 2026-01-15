import sqlite3
import os
from os import path


DB_DIR:str = path.join(".", "database")
CP_DIR:str = path.join(".", "companys")
db_files:dict = dict()

PASSANGER_COST = 2000

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(CP_DIR, exist_ok=True)

if not path.exists(path.join(CP_DIR, "list.txt")):
    with open(path.exists(path.join(CP_DIR, "list.txt")), "a") as f:
        pass

with open(path.join(CP_DIR, "list.txt"), "r") as f:
    for line in f.readlines():
        if line.strip() == "":
            continue
        if len(line.split()) != 2:
            name = line.strip()
            db_files[name] = f"{name}.db"
        else:
            name, db_file = line.strip().split(" ")
            db_files[name] = db_file

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
    if name in db_files:
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
    db_files[name] = f"{name}.db"
    with open("companys/list.txt", "a") as f:
        f.write(f"{name}\n")
    INIT()
    return {
        "status":"ok",
        "message":"company added"
    }

def delete_company(name:str):
    if name not in db_files:
        return {
            "status":"error",
            "message":"company does not exist"
        }
    os.remove(path.join(DB_DIR, db_files[name]))
    del db_files[name]
    with open("companys/list.txt", "w+") as f:
        for key in db_files.keys():
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
    for _, db_file in db_files.items():
        db_path = path.join(DB_DIR, db_file)

        do_cmd(db_path, "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, " \
        "password TEXT, post TEXT, account TEXT, vk TEXT, disciplinary_actions TEXT, note TEXT)")

        do_cmd(db_path, "CREATE TABLE IF NOT EXISTS statistic (id INTEGER PRIMARY KEY AUTOINCREMENT, user_name TEXT, " \
        "total_salary TEXT, period_salary TEXT, total_round_trips TEXT, period_round_trips TEXT, total_passengers TEXT, period_passengers TEXT)")

        do_cmd(db_path, "CREATE TABLE IF NOT EXISTS vehicles (number INTEGER PRIMARY KEY AUTOINCREMENT, board_number TEXT, " \
        "state_number TEXT, model TEXT, built TEXT, since TEXT, note TEXT, state TEXT, owner TEXT)")

        do_cmd(db_path, "CREATE TABLE IF NOT EXISTS routes (id INTEGER PRIMARY KEY AUTOINCREMENT, route TEXT, salary TEXT)")

        do_cmd(db_path, "CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, " +
        "user_name TEXT, date TEXT, route TEXT, num_round_trips TEXT, num_passengers TEXT, proof TEXT, status TEXT)")

        do_cmd(db_path, "CREATE TABLE IF NOT EXISTS coefs (id INTEGER PRIMARY KEY AUTOINCREMENT, post TEXT, coef TEXT)")

        do_cmd(db_path, "CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, value TEXT)")
        add_config(db_path, "passanger_cost", str(PASSANGER_COST))

        print(f"database {db_path} created")


#* db

def get_db_path(company:str):
    if company not in db_files:
        return ""
    return path.join(DB_DIR, db_files[company])

#* config

def get_config(file_name:str, key:str):
    cmd = f"SELECT value FROM config WHERE key = ?"
    values = (key,)
    ans = do_cmd(file_name, cmd, values)
    if len(ans) == 0:
        return ""
    return ans[0][0]

def get_configs(file_name:str):
    cmd = f"SELECT * FROM config"
    values = tuple()
    ans = do_cmd(file_name, cmd, values)
    if len(ans) == 0:
        return {
            "status":"error",
            "message":"no configs found"
        }
    configs = []
    for config in ans:
        configs.append({
            "id":config[0],
            "key":config[1],
            "value":config[2],
        })
    return {
        "status":"ok",
        "configs":configs
    }

def set_config(file_name:str, key:str, value:str):
    cmd = f"UPDATE config SET value = ? WHERE key = ?"
    values = (value, key)
    do_cmd(file_name, cmd, values)
    return

def add_config(file_name:str, key:str, value:str):
    if get_config(file_name, key) != "":
        return
    cmd = f"INSERT INTO config (key, value) VALUES (?, ?)"
    values = (key, value)
    do_cmd(file_name, cmd, values)
    return

def delete_config(file_name:str, key:str):
    cmd = f"DELETE FROM config WHERE key = ?"
    values = (key,)
    do_cmd(file_name, cmd, values)
    return


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
    elif id:
        cmd = f"SELECT * FROM users WHERE id = ?"
        values = (id,)
        ans = do_cmd(file_name, cmd, values)
        if len(ans) == 0:
            return {
                "status":"error",
                "message":"user does not exist"
            }
        user = ans[0]
    else:
        user = ("", "", "", "", "", "", "","")
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

def get_users(file_name:str) -> list:
    cmd = f"SELECT * FROM users"
    ans = do_cmd(file_name, cmd)
    if len(ans) == 0:
        return []
    users:list[dict[str,str]] = []
    for user in ans:
        user_properties:dict[str,str] = {
            "id":str(user[0]),
            "name":str(user[1]),
            # "password":str(user[2]),
            "post":str(user[3]),
            "account":str(user[4]),
            "vk":str(user[5]),
            "disciplinary_actions":str(user[6]),
            "note":str(user[7])
        }
        users.append(user_properties)
    return users

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
    values = (name, password, post, account, vk, disciplinary_actions, note, id)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"user updated"
    }


#* statistics

def get_statistics(file_name:str):
    cmd = f"SELECT * FROM statistics"
    ans = do_cmd(file_name, cmd)
    if len(ans) == 0:
        return {
            "status":"error",
            "message":"users statistics does not exist"
        }
    statistics = []
    for stat in ans:
        statistics.append({
            "id":str(stat[0]),
            "user_name":str(stat[1]),
            "total_salary":str(stat[2]),
            "piriod_salary":str(stat[3]),
            "total_round_trips":str(stat[4]),
            "piriod_round_trips":str(stat[5]),
            "total_passengers":str(stat[6]),
            "piriod_passengers":str(stat[7])
        })
    return {
        "status":"ok",
        "statistics":statistics
    }

def get_user_statistics(file_name:str, user_name:str):
    ans = get_statistics(file_name)
    if ans["status"] == "error":
        return ans
    for stat in ans["statistics"]:
        if stat["user_name"] == user_name:
            return stat
    cmd = f"INSERT INTO statistics (user_name, total_salary, piriod_salary, total_round_trips, piriod_round_trips, total_passengers, piriod_passengers) VALUES (?, ?, ?, ?, ?, ?, ?)"
    values = (user_name, 0, 0, 0, 0, 0, 0)
    do_cmd(file_name, cmd, values)
    return get_user_statistics(file_name, user_name)

def update_statistics(file_name:str, id:str, user_name:str, total_salary:str, piriod_salary:str, total_round_trips:str, piriod_round_trips:str, total_passengers:str, piriod_passengers:str):
    ans = get_statistics(file_name)
    if ans["status"] == "error":
        return ans
    for stat in ans["statistics"]:
        if stat["id"] == id:
            break
    else:
        cmd = f"INSERT INTO statistics (user_name, total_salary, piriod_salary, total_round_trips, piriod_round_trips, total_passengers, piriod_passengers) VALUES (?, ?, ?, ?, ?, ?, ?)"
        values = (user_name, total_salary, piriod_salary, total_round_trips, piriod_round_trips, total_passengers, piriod_passengers)
        do_cmd(file_name, cmd, values)
        return {
            "status":"ok",
            "message":"statistics added"
        }

    cmd = f"UPDATE statistics SET user_name = ?, total_salary = ?, piriod_salary = ?, total_round_trips = ?, piriod_round_trips = ?, total_passengers = ?, piriod_passengers = ? WHERE id = ?"
    values = (user_name, total_salary, piriod_salary, total_round_trips, piriod_round_trips, total_passengers, piriod_passengers, id)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"statistics updated"
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
    routes:list[dict] = []
    for route in ans:
        if not route:
            continue
        routes.append({
            "id":route[0],
            "route":route[1],
            "salary":route[2],
        })
    return {
        "status":"ok",
        "routes":routes
    }

def add_route(file_name:str, route:str, salary:str):
    ans = get_routes(file_name)
    if ans["status"] != "error" and route in ans["routes"]:
        return {
            "status":"error",
            "message":"route already exists"
        }
    cmd = "INSERT INTO routes (route, salary) VALUES (?, ?)"
    values = (route, salary)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"route added"
    }

def delete_route(file_name:str, id:str):
    ans = get_routes(file_name)
    if ans["status"] == "error":
        return ans
    for route in ans["routes"]:
        if route["id"] == id:
            break
    else:
        return {
            "status":"error",
            "message":"route does not exist"
        }
    cmd = f"DELETE FROM routes WHERE id = ?"
    values = (id,)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"route deleted"
    }

def get_route_salary(file_name:str, route:str):
    cmd = f"SELECT salary FROM routes WHERE route = ?"
    values = (route,)
    ans = do_cmd(file_name, cmd, values)
    if len(ans) == 0:
        return {
            "status":"error",
            "message":"no route found"
        }
    return {
        "status":"ok",
        "salary":str(ans[0][0])
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

    reportes = get_reports()
    if reportes["status"] == "error":
        return reportes
    report:dict
    for report_ in reportes["reports"]:
        if report_["id"] == id:
            report = report_
            break
    else:
        return {
            "status":"error",
            "message":"no report found"
        }


    routes = get_routes(file_name)
    if routes["status"] == "error":
        return routes
    route:dict
    for route_ in routes["routes"]:
        if route_["route"] == report["route"]:
            route = route_
            break
    else:
        return {
            "status":"error",
            "message":"no route found"
        }
    
    user = get_user(file_name, name=report["user_name"])
    if user["status"] == "error":
        return user
    

    salary = float(report["num_round_trips"]) * float(route["salary"]) + float(report["num_passengers"]) * float(get_config(file_name, "passanger_cost")) 
    salary *= float(get_coef(file_name, user["post"]))

    
    user_statistics = get_user_statistics(file_name, user["name"])
    if user_statistics["status"] == "error":
        return user_statistics
    
    user_statistics["total_salary"] = str(float(user_statistics["total_salary"]) + salary)
    user_statistics["total_round_trips"] = str(float(user_statistics["total_round_trips"]) + float(report["num_round_trips"]))
    user_statistics["total_passengers"] = str(float(user_statistics["total_passengers"]) + float(report["num_passengers"]))

    user_statistics["piriod_salary"] = str(float(user_statistics["piriod_salary"]) + salary)
    user_statistics["piriod_round_trips"] = str(float(user_statistics["piriod_round_trips"]) + float(report["num_round_trips"]))
    user_statistics["piriod_passengers"] = str(float(user_statistics["piriod_passengers"]) + float(report["num_passengers"]))

    update_statistics(file_name, user_statistics["id"], user_statistics["user_name"], user_statistics["total_salary"], 
                      user_statistics["piriod_salary"], user_statistics["total_round_trips"], user_statistics["piriod_round_trips"], 
                      user_statistics["total_passengers"], user_statistics["piriod_passengers"])
    
    # verefy report
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


#* coefs

def get_coefs(file_name:str):
    cmd = f"SELECT * FROM coefs"
    values = tuple()
    ans = do_cmd(file_name, cmd, values)
    if len(ans) == 0:
        return {
            "status":"error",
            "message":"no coefs found"
        }
    coefs = []
    for coef in ans:
        coefs.append({
            "id":coef[0],
            "post":coef[1],
            "coef":coef[2],
        })
    return {
        "status":"ok",
        "coefs":coefs
    }

def get_coef(file_name:str, post:str):
    cmd = f"SELECT * FROM coefs WHERE post = ?"
    values = (post,)
    ans = do_cmd(file_name, cmd, values)
    if len(ans) == 0:
        return {
            "status":"error",
            "message":"no coef found"
        }
    coef = ans[0]
    return {
        "status":"ok",
        "coef":coef[2],
    }

def add_coef(file_name:str, post:str, coef:str):
    cmd = "INSERT INTO coefs (post, coef) VALUES (?, ?)"
    values = (post, coef)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"coef added"
    }

def delete_coef(file_name:str, id:str):
    cmd = f"DELETE FROM coefs WHERE id = ?"
    values = (id,)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"coef deleted"
    }

def update_coef(file_name:str, id:str, post:str, coef:str):
    cmd = f"UPDATE coefs SET post = ?, coef = ? WHERE id = ?"
    values = (post, coef, id)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"coef updated"
    }

if __name__ == "__main__":
    INIT()
    cmd = "DROP TABLE IF EXISTS users_info "
    do_cmd(get_db_path("rotor"), cmd)
    cmd = "DROP TABLE IF EXISTS config "
    do_cmd(get_db_path("rotor"), cmd)
    cmd = "DROP TABLE IF EXISTS routes "
    do_cmd(get_db_path("rotor"), cmd)
    INIT()
