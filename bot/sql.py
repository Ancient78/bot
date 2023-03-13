import sqlite3
import urllib
from urllib import parse


def get_con():
    con = sqlite3.connect("../reg.db")
    cur = con.cursor()
    create_id_table(con, cur)
    return con, cur


def create_id_table(con, cur):
    cur.execute("CREATE TABLE if not exists id(user_id, first_name, last_name, passed)")
    con.commit()


def drop_tables():
    con, cur = get_con()
    cur.execute("DROP TABLE IF EXISTS id")
    con.commit()


def get_id_list():
    con, cur = get_con()
    res = cur.execute("SELECT user_id FROM id WHERE passed=True")
    return res.fetchall()


def get_master():
    _, cur = get_con()
    sql_query = "SELECT * FROM id WHERE user_id = ? or user_id = ?"
    data = (1553590834, 449379851)
    return cur.execute(sql_query, data).fetchall()


def get_unpassed():
    con, cur = get_con()
    res = cur.execute("SELECT user_id, first_name, last_name FROM id WHERE passed=False")
    return res.fetchall()


def pass_user(user_id):
    con, cur = get_con()
    sql_query = "UPDATE id SET passed=True WHERE user_id=" + user_id
    cur.execute(sql_query)
    con.commit()


def add_user(user_id, first_name, last_name):
    con, cur = get_con()
    sql_query = """INSERT INTO id(user_id, first_name, last_name, passed) VALUES (?,?,?,False)"""
    cur.execute(sql_query, (user_id, first_name, last_name))
    con.commit()


def get_full_table():
    con, cur = get_con()
    return cur.execute("SELECT * FROM id").fetchall()


def is_user_here(user_id):
    con, cur = get_con()
    return not cur.execute("SELECT user_id from id WHERE user_id="+str(user_id)).fetchone() is None


def get_full_data(user_id):
    con, cur = get_con()
    return cur.execute("SELECT last_name, first_name FROM id WHERE user_id="+str(user_id)).fetchone()


def get_user_name(user_id):
    _, cur = get_con()
    res = cur.execute("SELECT last_name, first_name FROM id WHERE user_id="+str(user_id)).fetchone()
    if res is not None:
        last_name, first_name = res
        return get_full_name(last_name, first_name)
    else:
        return ""


def get_full_name(last_name, first_name):
    if last_name is not None:
        last_name = urllib.parse.unquote(last_name)
    else:
        last_name = ""
    if first_name is not None:
        first_name = urllib.parse.unquote(first_name)
    else:
        first_name = ""
    return last_name + " " + first_name
