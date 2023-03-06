import sqlite3

# table storage


def get_con():
    con = sqlite3.connect("reg.db")
    cur = con.cursor()
    create_storage_table(con, cur)
    return con, cur


def create_storage_table(con, cur):
    cur.execute("CREATE TABLE if not exists storage(storage_id INTEGER PRIMARY KEY NOT NULL, nom, count)")
    con.commit()


def drop_table():
    con, cur = get_con()
    cur.execute("DROP TABLE IF EXISTS storage")
    con.commit()


def add_nom(nom):
    con, cur = get_con()
    sql_query = """INSERT INTO storage(nom, count) VALUES (?,0)"""
    cur.execute(sql_query, (nom,))
    con.commit()


def add_storage(storage_id, count):
    con, cur = get_con()
    now_count = get_count(storage_id)
    new_count = now_count + count
    sql_query = "UPDATE storage SET count=? WHERE storage_id=?"
    cur.execute(sql_query, (new_count, storage_id))
    con.commit()


def get_count(storage_id):
    con, cur = get_con()
    res = cur.execute("SELECT count FROM storage WHERE storage_id="+str(storage_id))
    res = res.fetchone()
    if res is None:
        return 0
    else:
        return res[0]


def delete_row(storage_id):
    con, cur = get_con()
    cur.execute("DELETE FROM storage WHERE storage_id=" + str(storage_id))
    con.commit()


def get_all_storage():
    con, cur = get_con()
    return cur.execute("SELECT storage_id, nom, count FROM storage").fetchall()


def make_reserve(storage_id, count) -> bool:
    now_count = get_count(storage_id)
    if count>now_count:
        return False
    else:
        add_storage(storage_id, -count)
        return True


def get_storage_name(storage_id)->str:
    _, cur = get_con()
    res = cur.execute("SELECT nom FROM storage WHERE storage_id=?", (storage_id,)).fetchone()
    if res is not None:
        return res[0]