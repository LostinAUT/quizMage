# -*- coding: utf-8 -*-
import sqlite3


# 建立数据库连接
def open_db():
    database = "./database.db"
    conn = sqlite3.connect(database)
    # conn.row_factory = sqlite3.Row
    return conn

'''
# 获取数据库连接
def get_sql(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    fields = []
    for field in cur.description:
        fields.append(field[0])

    result = cur.fetchall()
    # for item in result:
    #     print(item)
    cur.close()
    return result, fields

'''

# 关闭数据库连接
def close_db(conn):
    conn.close()

def get_sql(sql, conn=None):
    close_conn = False
    if conn is None:
        conn = open_db()
        close_conn = True
    
    cur = conn.cursor()
    cur.execute(sql)
    fields = [field[0] for field in cur.description]
    result = cur.fetchall()
    cur.close()
    
    if close_conn:
        close_db(conn)
    
    return result, fields

'''
# 获取数据库连接
def get_sql2(sql):
    conn = open_db()
    result, fields = get_sql(conn, sql)
    close_db(conn)
    return result, fields

'''
# 改
def update_data(data, tablename):
    conn = open_db()
    values = []
    cursor = conn.cursor()
    
    idName = list(data)[0]  # 只取 `tno`
    
    for v in list(data)[1:]:  # 从第 2 个字段开始
        values.append("%s='%s'" % (v, data[v]))
    
    sql = "UPDATE %s SET %s WHERE %s='%s'" % (
        tablename, ",".join(values), idName, data[idName]
    )
    
    cursor.execute(sql)
    conn.commit()
    close_db(conn)


# 增
def insert_data(data, tablename):
    conn = open_db()
    values = []
    cusor = conn.cursor()
    fieldNames = list(data)
    for v in fieldNames:
        values.append(data[v])
    sql = "insert into  %s (%s) values( %s) " % (tablename, ",".join(fieldNames), ",".join(["?"] * len(fieldNames)))
    # print(sql)
    cusor.execute(sql, values)
    conn.commit()
    close_db(conn)


# 删
def delete_data_by_id(id1, id2, value1, value2, tablename):
    conn = open_db()
    # values = []
    cursor = conn.cursor()

    sql = "delete from %s  where %s=? and %s=?" % (tablename, id1, id2)
    # print (sql)

    cursor.execute(sql, (value1, value2))
    conn.commit()
    close_db(conn)
