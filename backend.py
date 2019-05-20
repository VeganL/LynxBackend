#!/usr/bin/python
''' Imports of necessary modules '''
import cgi,cgitb,re,json
cgitb.enable()
from mysql.connector import MySQLConnection, Error
from pythonMySQL_dbConfig import readDbConfig

#Defines resulting page/text as json format 
print('Content-type: application/json\n')

#Function to set grab size for querying with fetchmany() in dbQ()
def iterRow(cursor,size):
    while True:
        rows = cursor.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row

def dbIns(query,args=None):
    try:
        dbconfig = readDbConfig()
        connect = MySQLConnection(**dbconfig)

        cursor = connect.cursor()
        if args == None:
            cursor.execute(query)
        else:
            cursor.execute(query,args)

        connect.commit()
        print('{"err":false}')
    except:
        print('{"err":true}')
    finally:
        cursor.close()
        connect.close()

#Function takes query and arguments as parameters and returns result as list
def dbQ(query,args=None):
    result = []
    try:
        dbconfig = readDbConfig()
        connect = MySQLConnection(**dbconfig)

        cursor = connect.cursor()
        if args == None:
            cursor.execute(query)
        else:
            cursor.execute(query,args)

        for row in iterRow(cursor,10):
            result.append(row)
    except:
        print('{"err":true}')
    finally:
        cursor.close()
        connect.close()
        return result

#Register function, adds valid information to database
def register(username,email,password):
    query = "INSERT INTO accounts(username,email,password) " \
            "VALUES(%s,%s,%s)"
    args = (username,email,password)
    dbIns(query,args)

#Login function, returns account_id connected to valid username and password
def login(username,password):
    query = "SELECT account_id FROM accounts WHERE username = %s AND password = %s"
    args = (username,password)
    uid = dbQ(query,args)
    if len(uid) == 1:
        uidInt = json.dumps(uid[0])
        print('{ "account_id":', uidInt[1], '}')
    else:
        print('{"err":"Invalid login information"}')

def getProfiles(accId):
    query = "SELECT profile_id, title FROM profiles WHERE account_id = " + accId
    profiles = dbQ(query)
    print('{"Profiles": [ ', end='')
    if len(profiles) == 1:
        print('{"profile_id": ' + str(profiles[0][0]) + ', ' + profiles[0][1][1:], end='')
    else:
        for i in range(len(profiles)):
            if profiles[i] == profiles[-1]:
                print('{"profile_id": ' + str(profiles[i][0]) + ', ' + profiles[i][1][1:], end='')
            else:
                print('{"profile_id": ' + str(profiles[i][0]) + ', ' + profiles[i][1][1:] + ', ', end='')
    print(']}')

def insertProfile(jsonStr):
    pyDict = json.loads(jsonStr)
    accId = pyDict['account_id']
    profDesc = pyDict['profileName']
    title = '{"profileName": "' + profDesc + '"}'
    query = "INSERT INTO profiles(account_id,title) " \
            "VALUES(%s,%s)"
    args = (accId,title)
    dbIns(query,args)

def getCardIds(profId):
    query = "SELECT card_id, name FROM cards WHERE profile_id = " + profId
    cards = dbQ(query)

def insertCard(profId,jsonStr):
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
elif actionType == 'get_profiles':
    accId = form.getvalue('account_id')
    getProfiles(accId)
elif actionType == 'get_card_ids':
    profId = form.getvalue('profile_id')
    getCardIds(profId)
elif actionType == 'insert_profile':
    jsonStr = form.getvalue('json_str')
    insertProfile(jsonStr)
elif actionType == 'insert_card':
    profId = form.getvalue('profile_id')
    cardAttr = form.getvalue('card_attrib')
    insertCard(profId,cardAttr)
else: #The following is to test if any changes to code breaks code in-browser; default response
    foo = { "Lynx Backend Script": "This is the default returned JSON string for backend.py", "err": True }
    data = json.dumps(foo)
    print(data)
