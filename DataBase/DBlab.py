import pymysql

cont = pymysql.connect('localhost', user='root', passwd='1234')
cur = cont.cursor()
sql = '''create databases if not exists testdb'''
cur.execute(sql)
