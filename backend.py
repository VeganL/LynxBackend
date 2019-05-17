#!/usr/bin/python
''' Imports of necessary modules '''
import cgi,cgitb,json,re
cgitb.enable()
from mysql.connector import MySQLConnection, Error
from pythonMySQL_dbConfig import readDbConfig

#Defines resulting page/text as json format 
print('Content-type: application/json\n')

#Function to set grab size for querying with fetchmany() in dbQ()
def iterRow(cursor, size):
    while True:
        rows = cursor.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row

#Function takes query and arguments as parameters and returns result as list
def dbQ(query,args):
    result = []
    try:
        dbconfig = readDbConfig()
        connect = MySQLConnection(**dbconfig)

        cursor = connect.cursor()
        cursor.execute(query,args)

        for row in iterRow(cursor,10):
            result.append(row)
    except Error as e:
        print(e)
    finally:
        cursor.close()
        connect.close()

    result = list(result)
    return result

#Register function, adds valid information to database
def register(username,email,password):
    username = str(username)
    email = str(email)
    password = str(password)
    #Regexes for verifying inputted email data and password data meet criteria
    searchEmail = re.search("^[a-z0-9]+[\.'\-a-z0-9_]*[a-z0-9]+@(gmail|googlemail)\.com$", email.lower())
    searchPass = re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', password)
    #returns json error object if criteria are not met
    if (len(username) < 5 or len(username) > 13) and (not searchEmail) and (not searchPass):
        print('{"err":true}')
    else: #Adds information to database and returns json confirmation object
        query = "INSERT INTO accounts(username,email,password) " \
                "VALUES(%s,%s,%s)"
        args = (username,email,password)

        try:
            dbconfig = readDbConfig()
            connect = MySQLConnection(**dbconfig)

            cursor = connect.cursor()
            cursor.execute(query,args)

            connect.commit()
        except Error as e:
            print(e)
        finally:
            cursor.close()
            connect.close()
        print('{"err":false}')

#Login function, returns account_id connected to valid username and password
def login(username,password):
    result = []
    query = "SELECT account_id FROM accounts WHERE username = %s AND password = %s"
    args = (username,password)
    uid = dbQ(query,args)
    if len(uid) == 1:
        uidInt = json.dumps(uid[0])
        print('{ "account_id":', uidInt[1], '}')
    else:
        print('{"err":true}')

def getProfiles(accId):
    pass

def getCards(accId):
    pass

#Takes form data sent from app and runs related function(s)
form = cgi.FieldStorage()
actionType = form.getvalue('type')
if actionType == 'register':
    username = form.getvalue('username')
    email = form.getvalue('email')
    password = form.getvalue('password')
    register(username,email,password)
elif actionType == 'login':
    username = form.getvalue('username')
    password = form.getvalue('password')
    login(username,password)
elif actionType == 'getProfiles':
    accId = form.getvalue('account_id')
    getProfiles(accId)
elif actionType == 'getCards':
    accId = form.getvalue('account_id')
    getCards(accId)
else: #The following is to test if any changes to code breaks code in-browser; default response
    foo = { "Lynx Backend Script": "This is the default returned JSON string for backend.py", "err": True }
    data = json.dumps(foo)
    print(data)
