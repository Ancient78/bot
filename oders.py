import sqlite3

# table storage


def get_con():
    con = sqlite3.connect("reg.db")
    cur = con.cursor()
    create_storage_table(con, cur)
    return con, cur


def create_storage_table(con, cur):
    cur.execute("CREATE TABLE if not exists orders(order_id INTEGER PRIMARY KEY NOT NULL, user_id, storage_id, count, shipped, paid, tel)")
    con.commit()


def drop_table():
    con, cur = get_con()
    cur.execute("DROP TABLE IF EXISTS orders")
    con.commit()


def add_order(user_id, storage_id, count):
    con, cur = get_con()
    now_count = get_orders_by_storage(user_id, storage_id)
    if now_count>0:
        sql_query = "UPDATE orders SET count=? WHERE user_id=? and storage_id=? and shipped=False and paid=False"
        data = (count+now_count, user_id, storage_id)
        cur.execute(sql_query, data)
    else:
        sql_query = """INSERT INTO orders(user_id, storage_id, count, shipped, paid) VALUES (?,?,?,0,0)"""
        data = (user_id, storage_id, count)
    cur.execute(sql_query, data)
    con.commit()


def get_orders_by_storage(user_id, storage_id):
    con, cur = get_con()
    sql_query = "SELECT count FROM orders WHERE user_id=? and storage_id=? and shipped=False and paid=False"
    data = (user_id, storage_id)
    res = cur.execute(sql_query, data).fetchone()
    if res is None:
        return 0
    else:
        return res[0]


def get_orders(user_id=None, shipped=None, paid=None):
    if user_id is not None and shipped is None and paid is None:
        sql_query = "SELECT * FROM orders WHERE user_id=?"
        data = (user_id,)
    elif user_id is not None and shipped is not None and paid is None:
        sql_query = "SELECT * FROM orders WHERE user_id=? and shipped=?"
        data = (user_id, shipped)
    elif user_id is not None and shipped is None and paid is not None:
        sql_query = "SELECT * FROM orders WHERE user_id=? and paid=?"
        data = (user_id, paid)
    elif user_id is not None and shipped is not None and paid is not None:
        sql_query = "SELECT * FROM orders WHERE user_id=? and shipped=? and paid=?"
        data = (user_id, shipped, paid)
    elif user_id is None and shipped is not None and paid is not None:
        sql_query = "SELECT * FROM orders WHERE shipped=? and paid=?"
        data = (shipped, paid)
    elif user_id is None and shipped is not None and paid is None:
        sql_query = "SELECT * FROM orders WHERE shipped=?"
        data = (shipped,)
    elif user_id is None and shipped is None and paid is not None:
        sql_query = "SELECT * FROM orders WHERE paid=?"
        data = (paid,)
    else:
        sql_query = "SELECT * FROM orders"
        data = ()
    con, cur = get_con()
    return cur.execute(sql_query, data).fetchall()


def set_ship(user_id):
    con, cur = get_con()
    sql_query = "UPDATE orders SET shipped=True WHERE user_id=" + str(user_id)
    cur.execute(sql_query)
    con.commit()


def set_paid(user_id):
    con, cur = get_con()
    sql_query = "UPDATE orders SET paid=True WHERE user_id=" + str(user_id)
    cur.execute(sql_query)
    con.commit()


def set_tel_in_order(user_id, tel):
    if tel != "":
        sql_query = "UPDATE orders SET Tel=? WHERE user_id=? and shipped=False"
        data = (tel, user_id)
        con, cur = get_con()
        cur.execute(sql_query, data)
        con.commit()
