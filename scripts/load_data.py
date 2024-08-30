import sqlite3

def run():
    conn = sqlite3.connect("db_save.sqlite3")
    c = conn.cursor()
    c.execute("ATTACH DATABASE 'db.sqlite3' AS new_db")
    input(c.execute("SELECT id, username FROM auth_user").fetchall())
    c.execute("INSERT INTO new_db.Blog_user(id, password, last_login, username, first_name, last_name, email, is_staff, is_superuser, date_joined, is_active) SELECT id, password, last_login, username, first_name, last_name, email, is_staff, is_superuser, date_joined, is_active FROM auth_user")
    input(c.execute("SELECT id, username FROM new_db.Blog_user").fetchall())
    conn.commit()
    conn.close()