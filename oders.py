import sqlite3

import storage


# table storage


def get_con():
    con = sqlite3.connect("reg.db")
    cur = con.cursor()
    create_reg_table(con, cur)
    return con, cur


def create_reg_table(con, cur):
    cur.execute("CREATE TABLE if not exists orders(order_id INTEGER PRIMARY KEY NOT NULL, user_id, storage_id, count, "
                "cost, shipped, paid, tel)")
    con.commit()


def drop_table():
    con, cur = get_con()
    cur.execute("DROP TABLE IF EXISTS orders")
    con.commit()


def add_order(user_id, storage_id, count):
    con, cur = get_con()
    now_count = get_orders_by_storage(user_id, storage_id)
    temp_price = storage.get_price(storage_id)
    if temp_price is not None:
        price = temp_price[0]
    else:
        price = 0
    if now_count > 0:
        sql_query = "UPDATE orders SET count=?, cost=? WHERE user_id=? and storage_id=? and shipped=False and " \
                    "paid=False"
        cost = round(price*(count+now_count), 2)
        data = (count+now_count, cost, user_id, storage_id)
        cur.execute(sql_query, data)
    else:
        sql_query = """INSERT INTO orders(user_id, storage_id, count, cost, shipped, paid) VALUES (?,?,?,?,0,0)"""
        cost = round(price * count, 2)
        data = (user_id, storage_id, count, cost)
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


def set_new_count(temp_storage_index, user_id, count):
    if temp_storage_index > 0:
        sql_query = "SELECT storage_id, count FROM orders WHERE user_id=? and shipped=FALSE and paid=FALSE"
        data = (user_id,)
        con, cur = get_con()
        res = cur.execute(sql_query, data).fetchall()
        if res is not None:
            storage_id, now_count = res[temp_storage_index]
            sql_query = "UPDATE orders SET count=? WHERE user_id=? and storage_id=? and shipped=False"
            data = (count, user_id, storage_id)
            cur.execute(sql_query, data)
            con.commit()
            return storage_id, now_count-count


def delete_row(user_id, temp_storage_index):
    if temp_storage_index > 0:
        sql_query = "SELECT storage_id, count FROM orders WHERE user_id=? and shipped=FALSE and paid=FALSE"
        data = (user_id,)
        con, cur = get_con()
        res = cur.execute(sql_query, data).fetchall()
        if res is not None:
            storage_id, now_count = res[temp_storage_index]
            sql_query = "DELETE FROM orders WHERE user_id=? and storage_id=? and shipped=False"
            data = (user_id, storage_id)
            cur.execute(sql_query, data)
            con.commit()
            return storage_id, now_count


def get_connection(user_id):
    _, cur = get_con()
    return cur.execute("SELECT tel FROM orders WHERE user_id="+str(user_id)).fetchall()


def clear_shiped():
    con, cur = get_con()
    cur.execute("UPDATE orders SET shipped=False")
    con.commit()


def clear_paid():
    con, cur = get_con()
    cur.execute("UPDATE orders SET paid=False")
    con.commit()
