#!/usr/bin/python
''' Imports of necessary modules '''
import cgi,cgitb,re,json
cgitb.enable()
from mysql.connector import MySQLConnection, Error
from pythonMySQL_dbConfig import readDbConfig

insCounter = 0
delCounter = 0

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

def dbW(query,args=None,silentRun=False):
    global insCounter
    try:
        dbconfig = readDbConfig()
        connect = MySQLConnection(**dbconfig)
        
        cursor = connect.cursor()
        if args == None:
            cursor.execute(query)
        else:
            cursor.execute(query,args)
        
        connect.commit()
        if insCounter == 0 and silentRun == False:
            print('{"err":false}')
            insCounter += 1
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

#Return JsonList
def getAttributes(attIdList):
    pass

def insertAttributes(profId,attJsonList):
    pass

#Register function, adds valid information to database
def register(username,email,password):
    query = "SELECT * FROM accounts WHERE username = '" + str(username) + "'"
    usernameTaken = dbQ(query)
    query = "SELECT * FROM accounts WHERE email = '" + str(email) + "'"
    emailTaken = dbQ(query)
    if len(usernameTaken) > 0:
        print('{"err":"Username already taken"}')
    elif len(emailTaken) > 0:
        print('{"err":"An account is already registered to this E-mail address"}')
    else:
        query = "INSERT INTO accounts(username,email,password) " \
            "VALUES(%s,%s,%s)"
        args = (username,email,password)
        dbW(query,args)

#Login function, returns account_id connected to valid username and password
def login(username,password):
    query = "SELECT account_id FROM accounts WHERE username = %s AND password = %s"
    args = (username,password)
    uid = dbQ(query,args)
    if len(uid) == 1:
        uidInt = json.dumps(uid[0])
        getProfiles(uidInt[1])
    else:
        print('{"err":"Invalid login information"}')

def getProfiles(accId):
    query = "SELECT profile_id, title FROM profiles WHERE account_id = " + str(accId)
    profiles = dbQ(query)

    jsonStr = '{['
    for i in range(len(profiles)):
        query = "SELECT attribute_id, attribute FROM attributes WHERE profile_id = " + str(profiles[i][0])
        profAttr = dbQ(query)
        jsonStr += '{"profile_id":' + str(profiles[i][0]) + ', ' + profiles[i][1][1:-1] + ', "attributes":['
        for r in range(len(profAttr)):
            jsonStr += '{"attribute_id":' + str(profAttr[r][0]) + ', ' + profAttr[r][1][1:]
            if profAttr[r] != profAttr[-1]:
                jsonStr += ', '
        jsonStr += ']}'
        if profiles[i] != profiles[-1]:
            jsonStr += ', '
    jsonStr += ']}'
    print(jsonStr)

def insertProfile(accId,profileJson,attributesJson):
    attrDict = json.loads(attributesJson)

    query = "INSERT INTO profiles(account_id,title) VALUES (%s,%s)"
    args = (accId,profileJson)
    dbW(query,args,True)

    query = "SELECT profile_id FROM profiles WHERE account_id = " + str(accId)
    profId = dbQ(query)[-1][-1]

    for key, value in attrDict.items():
        query = "INSERT INTO attributes(profile_id,attribute) VALUES (%s,%s)"
        args = (profId,'{"' + key + '":"' + str(value) + '"}')
        dbW(query,args)

def getProfileCards(profId): #WIP
    query = "SELECT card_id,name FROM cards WHERE profile_id = %s VALUES(profile_id)"
    args = (profId)
    cards = dbQ(query,args)
    jsonStr = '{"Cards": ['
    for card in cards:
        jsonStr += '{"card_id": ' + str(card[0]) + ', ' + card[1][:-1] + ', {"Attributes": ['
        queryC = "SELECT attribute_id FROM attributes_cards WHERE card_id = %s VALUES(card_id)"
        argsC = (card)
        attributes = dbQ(queryC,argsC)
        for att in attributes:
            queryA = "SELECT attribute FROM attributes WHERE attribute_id = %s VALUES(attribute_id)"
            argsA = (att)
            value = dbQ(queryA,argsA)
            jsonStr += '{"attribute_id": ' + str(att) + ', ' + str(value)
            if att != attributes[-1]:
                jsonStr += ', '
        jsonStr += ']}'
        if card != cards[-1]:
            jsonStr += ', '
    jsonStr += ']}'
    print(jsonStr)

def insertProfileCard(profId,cardJson): #WIP
    pass

def getWallet(accId): #WIP
    pass

def addCardWalletConf(accId,cardId): #WIP
    pass


''' Request handling '''
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
##############################################################
elif actionType == 'get_profiles':
    accId = form.getvalue('account_id')
    getProfiles(accId)
elif actionType == 'insert_profile':
    accId = form.getvalue('account_id')
    profNameJson = form.getvalue('profile_name_json')
    attrJson = form.getvalue('attributes_json')
    insertProfile(accId,profNameJson,attrJson)
elif actionType == 'edit_profile': #WIP
    pass
### PROFILE CARDS ###
elif actionType == 'get_profile_cards': #WIP
    profId = form.getvalue('profile_id')
    getProfileCards(profId)
elif actionType == 'insert_profile_card': #WIP
    profId = form.getvalue('profile_id')
    cardJson = form.getvalue('card_json')
    insertProfileCard(profId,cardJson)
elif actionType == 'edit_card': #WIP
    pass
elif actionType == 'remove_card_profile': #WIP
    pass
##############################################################
elif actionType == 'get_wallet': #WIP
    accId = form.getvalue('account_id')
    getWallet(accId)
elif actionType == 'get_card_qr': #WIP
    #automates card download process
    pass
elif actionType == 'add_card_wallet_conf': #WIP
    accId = form.getvalue('account_id')
    cardId = form.getvalue('card_id')
    addCardWalletConf(accId,cardId)
elif actionType == 'remove_card_wallet': #WIP
    pass
##############################################################
else: #The following is to test if any changes to code breaks code in-browser; default response
    foo = { "Lynx Backend Script": "This is the default returned JSON string for backend.py", "err": True }
    data = json.dumps(foo)
    print(data)