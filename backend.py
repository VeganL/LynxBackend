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

#Returns jsonString representation of an attribute
def getAttribute(att_id):
    query = "SELECT attribute FROM attributes where attribute_id = %s"
    args = (att_id)
    att = dbQ(query,args)
    jsonStr = f'{{"attribute_id": {str(att_id)}, {att}}}'
    return jsonStr

#Returns jsonString representation of a card
def getCard(card_id):
    queryC = "Select name FROM cards WHERE card_id = %s"
    argsC = (card_id)
    card_name = dbQ(queryC,argsC)
    queryA = "SELECT attribute_id FROM attributes_cards WHERE card_id = %s"
    argsA = (card_id)
    att_ids = dbQ(queryA,argsA)

    jsonStr = f'{{"card_id": {str(card_id)}, "card_name": {card_name}, "attributes": ['
    for att_id in att_ids:
        jsonStr += f'{getAttribute(att_id)}'
        if att_id != att_ids[-1]:
            jsonStr += ', '
    jsonStr += ']}'
    return jsonStr

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
        print('{ "account_id":', uidInt[1], '}')
    else:
        print('{"err":"Invalid login information"}')

def getProfiles(accId): # To-Do: Extend so profile attributes are also loaded
    query = "SELECT profile_id, title FROM profiles WHERE account_id = " + accId
    profiles = dbQ(query)
    jsonStr = '{"Profiles": ['
    for i in range(len(profiles)):
        if profiles[i] == profiles[-1]:
            jsonStr += '{"profile_id": ' + str(profiles[i][0]) + ', ' + profiles[i][1][1:]
        else:
            jsonStr += '{"profile_id": ' + str(profiles[i][0]) + ', ' + profiles[i][1][1:] + ', '
    jsonStr += ']}'
    print(jsonStr)

def insertProfile(accId,profileJson): #WIP
    # profileJson: {"profile_name":"name","attributes":["{"name":"dudename"}",...]}
    pass

def getProfileCards(profId): #NEEDS TESTING
    query = "SELECT card_id FROM cards WHERE profile_id = %s"
    args = (profId)
    cards = dbQ(query,args)
    jsonStr = '{"Cards": ['
    for card in cards:
        jsonStr += getCard(card)
        if card != cards[-1]:
            jsonStr += ', '
    jsonStr += ']}'
    print(jsonStr)

def insertProfileCard(profId,cardJson,attIdJson): #WIP
    print(attIdJson)
    attlist = json.loads(attIdJson)
    query = "INSERT INTO cards(profile_id,name) VALUES(%s,%s)"
    args = (profId,cardJson)
    dbW(query,args)
    queryC = "SELECT card_id WHERE profile_id = %s AND name = %s"
    argsC = (profId,cardJson)
    cardId = dbQ(queryC,argsC)
    queryA = "INSERT INTO attributes_cards(card_id,attribute_id) VALUES(%s,%s)"
    for attId in attlist:
        print(attId)
        argsA = (cardId,attId)
        dbW(queryA,argsA)



def getWallet(accId):
    pass

def addCardWalletConf(accId,cardId):
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
elif actionType == 'get_profiles': #WIP
    accId = form.getvalue('account_id')
    getProfiles(accId)
elif actionType == 'insert_profile': #WIP
    accId = form.getvalue('account_id')
    profJson = form.getvalue('profile_json')
    insertProfile(accId,profJson)
elif actionType == 'edit_profile': #WIP
    pass
### PROFILE CARDS ###
elif actionType == 'get_profile_cards': #WIP
    profId = form.getvalue('profile_id')
    getProfileCards(profId)
elif actionType == 'insert_profile_card': #WIP
    profId = form.getvalue('profile_id')
    cardJson = form.getvalue('card_json')
    attidjson = form.getvalue('att_id_json')
    insertProfileCard(profId,cardJson,attidjson)
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