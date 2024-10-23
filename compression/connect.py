import psycopg2
def con():
    conn = psycopg2.connect(
        dbname="compress_image",
        user="postgres",
        password="12345",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    return conn, cursor
