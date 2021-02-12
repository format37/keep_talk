#CREATE TABLE requests(request_id INT NOT NULL AUTO_INCREMENT,created datetime default NULL,chat VARCHAR(100),source VARCHAR(1023),PRIMARY KEY ( request_id ));
#import pymysql.cursors

def sql_read(con):
    with con:  
        cur = con.cursor()
        cur.execute("SELECT * FROM requests ORDER BY created LIMIT 1;")
        return cur.fetchall()

def sql_remove(con,request_id):
    with con:  
        cur = con.cursor()
        cur.execute("DELETE FROM requests WHERE request_id="+str(request_id)+";") 
        rows = cur.fetchall()

# con = pymysql.connect('localhost', 'root', '9878987', 'mysql')		
# row=sql_read(con)
# if len(row):
	# request_id,source=row[0][0],row[0][3]
	# print(source,request_id)
	# sql_remove(con,request_id)
# else:
	# print('empty1')