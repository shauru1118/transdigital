import sqlite3
import os


DB_DIR = "database"
DB_FILES = {
    "rotor":"rotor.db"
}

os.makedirs(DB_DIR, exist_ok=True)

def do_cmd(file_name:str, cmd:str, values:tuple=tuple()):
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()
    cursor.execute(cmd, values)
    result = cursor.fetchall()
    cursor.close()
    connection.commit()
    connection.close()
    return result

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

def get_db_path(file_name:str):
    if file_name not in DB_FILES:
        return ""
    return os.path.join(DB_DIR, DB_FILES[file_name])

def add_user(file_name:str, name:str, password:str, post:str, account:str, vk:str, disciplinary_actions:str, note:str):
    if len(get_user(file_name, name)) > 0:
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


if __name__ == "__main__":
    INIT()
    print(get_users_info(get_db_path("rotor")))
    delete_user(get_db_path("rotor"), "admin")
    print(get_users_info(get_db_path("rotor")))
    # delete_user(get_db_path("rotor"), "admin")
    # print(get_user(get_db_path("rotor"), "admin"))

