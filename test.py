from sql_lib import sql_read, sql_remove
import pymysql.cursors
#adress, user,pass,db
con = pymysql.connect('192.168.1.23', 'client', 'password', 'gpt2')