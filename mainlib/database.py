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
    for company, db_file in DB_FILES.items():
        db_path = os.path.join(DB_DIR, db_file)
        create_table(db_path, "users", "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT")

def get_db_path(file_name:str):
    if file_name not in DB_FILES:
        return ""
    return os.path.join(DB_DIR, DB_FILES[file_name])

def add_user(file_name:str, name:str, password:str):
    if len(get_user(file_name, name)) > 0:
        return {
            "status":"error",
            "message":"user already exists"
            }
    cmd = f"INSERT INTO users (name, password) VALUES (?, ?)"
    values = (name, password)
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
        "id":str(user[0]),
        "name":str(user[1]),
        "password":str(user[2])
    }

def get_all_users(file_name:str):
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
            "password":str(user[2])
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
    return {
        "status":"ok",
        "message":"user deleted"
    }

def update_user(file_name:str, name:str, password:str):
    if len(get_user(file_name, name)) == 0:
        return {
            "status":"error",
            "message":"user does not exist"
        }
    cmd = f"UPDATE users SET password = ? WHERE name = ?"
    values = (password, name)
    do_cmd(file_name, cmd, values)
    return {
        "status":"ok",
        "message":"user updated"
    }


if __name__ == "__main__":
    INIT()
    print(get_all_users(get_db_path("rotor")))
    delete_user(get_db_path("rotor"), "admin")
    print(get_all_users(get_db_path("rotor")))
    # delete_user(get_db_path("rotor"), "admin")
    # print(get_user(get_db_path("rotor"), "admin"))

