import sqlite3
import datetime
from string import Template

# table date


def get_con():
    con = sqlite3.connect("reg.db")
    cur = con.cursor()
    create_storage_table(con, cur)
    return con, cur


def create_storage_table(con, cur):
    cur.execute("CREATE TABLE if not exists date(order_id , storage_id, ship_date TIMESTAMP, pay_date TIMESTAMP)")
    con.commit()


def drop_table():
    con, cur = get_con()
    cur.execute("DROP TABLE IF EXISTS date")
    con.commit()


def add_ship(storage_id_list):
    con, cur = get_con()
    sql_query = ""
    for row in storage_id_list:
        sql_query_temp = Template("SELECT * FROM date WHERE storage_id=$storage_id and order_id=$order_id")
        sql_query = sql_query_temp.substitute(storage_id=row[0], order_id=row[1])
        if cur.execute(sql_query).fetchone() is not None:
            sql_query = "UPDATE date SET ship_date=? WHERE storage_id=? and order_id=?"
            data = (datetime.datetime.now(), row[0], row[1])
        else:
            sql_query = "INSERT INTO date(storage_id, ship_date, order_id) VALUES (?, ?, ?)"
            data = (row[0], datetime.datetime.now(), row[1])
        cur.execute(sql_query, data)
        con.commit()


def add_pay(storage_id_list):
    con, cur = get_con()
    for row in storage_id_list:
        sql_query_temp = Template("SELECT * FROM date WHERE storage_id=$storage_id and order_id=$order_id")
        sql_query = sql_query_temp.substitute(storage_id=row[0], order_id=row[1])
        if cur.execute(sql_query).fetchone() is not None:
            sql_query="UPDATE date SET pay_date=? WHERE storage_id=? and order_id=?"
            data = (datetime.datetime.now(), row[0], row[1])
        else:
            sql_query = "INSERT INTO date(storage_id, pay_date, order_id) VALUES (?, ?, ?)"
            data = (row[0], datetime.datetime.now(), row[1])
        cur.execute(sql_query, data)
        con.commit()


def get_date(storage_id=None):
    _, cur = get_con()
    if storage_id is None:
        return cur.execute("SELECT * FROM date").fetchall()
    else:
        sql_query_temp = Template("SELECT * FROM date WHERE storage_id=$storage_id")
        sql_query = sql_query_temp.substitute(storage_id=storage_id)
        return cur.execute(sql_query).fetchall()