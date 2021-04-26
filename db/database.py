import mysql.connector
import sys
from mysql.connector import errorcode

_fname, _lname, _gate, _terminal, _seat = ([] for i in range(5))
def insert():
    try:
        cnx = mysql.connector.connect(
            host='host',
            user='user',
            password='password',
            database='db_name'
        )
        _id = cnx.cursor()
        ids = ("SELECT id, firstname FROM info")
        _id.execute(ids)
        print("Already have id: ")
        for i,_ in _id:
            print(f"\t({i},{_})", end='')
        print("\n")
        id, fname, lname, gate, terminal, seat = (  input("Id: "),
                                                input("Firstname: "),
                                                input("Lastname: "),
                                                input("Gate: "),
                                                input("Terminal: "),
                                                input("Seat: ") )
        info = (id, fname, lname, gate, terminal, seat)
        renew = ("ALTER TABLE info AUTO_INCREMENT=1")
        inst = ("INSERT INTO info (id, firstname, lastname, gate, terminal, seat) VALUES (%s, %s, %s, %s, %s, %s)")
        cursor = cnx.cursor()
        cursor.execute(renew)
        cursor.execute(inst, info)
        print("Insert Successfully")

        cnx.commit()
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(err)
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Username or Password Wrong")

def queryDB():
    global _fname, _lname, _gate, _terminal, _seat
    cnx = mysql.connector.connect(  host='host',
                                user='user',
                                password='password',
                                database='db_name'  )
    cursor = cnx.cursor()
    query = ("SELECT firstname, lastname, gate, terminal, seat FROM info")
    cursor.execute(query)
        
    for fname, lname, gate, terminal, seat in cursor:
        _fname.append(fname)
        _lname.append(lname)
        _gate.append(gate)
        _terminal.append(terminal)
        _seat.append(seat)

if '__main__' == __name__:
    insert()
