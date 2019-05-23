#!/usr/bin/python
''' Imports of necessary modules '''
import cgi,cgitb,re,json
cgitb.enable()
from mysql.connector import MySQLConnection, Error
from pythonMySQL_dbConfig import readDbConfig

insCounter = 0

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
        if insCounter == 0:
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
    jsonStr = '{"Profiles": ['
    for i in range(len(profiles)):
        if profiles[i] == profiles[-1]:
            jsonStr += '{"profile_id": ' + str(profiles[i][0]) + ', ' + profiles[i][1][1:]
        else:
            jsonStr += '{"profile_id": ' + str(profiles[i][0]) + ', ' + profiles[i][1][1:] + ', '
    jsonStr += ']}'
    print(jsonStr)

def insertProfile(accId,profileName):
    title = '{"profileName": "' + profileName + '"}'
    query = "INSERT INTO profiles(account_id,title) " \
        "VALUES(%s,%s)"
    args = (accId,title)
    dbIns(query,args)

# prints json with card_id s from the profile with the given profile_id
def getProfileCards(profId):
    query = "SELECT card_id, name FROM cards WHERE profile_id = " + str(profId)
    cards = dbQ(query)
    jsonStr = '{"profile' + profId + '_cards": ['
    for i in range(len(cards)):
        if cards[i] == cards[-1]:
            jsonStr += '{"card_id":' + str(cards[i][0]) + ', ' + cards[i][1][1:]
        else:
            jsonStr += '{"card_id":' + str(cards[i][0]) + ', ' + cards[i][1][1:] + ', '
    jsonStr += ']}'
    print(jsonStr)

# Inserts new card_id into cards table with the given profile_id
def insertProfileCard(profId,cardName):
    name = '{"cardName": "' + cardName + '"}'
    query = "INSERT INTO cards(profile_id,name) VALUES(%s,%s)"
    args = (profId,name)
    dbIns(query,args)

def getProfileAttributes(profId):
    query = "SELECT attribute_id, attribute FROM attributes WHERE profile_id = " + str(profId)
    result = dbQ(query)
    jsonStr = '{"profile' + profId + '_attributes": ['
    for i in range(len(result)):
        if result[i] == result[-1]:
            jsonStr += '{"attribute_id":' + str(result[i][0]) + ', ' + result[i][1][1:]
        else:
            jsonStr += '{"attribute_id":' + str(result[i][0]) + ', ' + result[i][1][1:] + ', '
    jsonStr += ']}'
    print(jsonStr)

def insertProfileAttributes(profId,jsonStr):
    pyDict = json.loads(jsonStr)
    for key, value in pyDict.items():
        query = "INSERT INTO attributes(profile_id,attribute) " \
            "VALUES(%s,%s)"
        args = (profId,'{"' + key + '":"' + value + '"}')
        dbIns(query,args)

# prints list of card_id that have been shared with given account_id
def getWallet(accId):
    query = "SELECT card_id, name FROM account_cards WHERE account_id = " + str(accId)
    cards = dbQ(query)
    jsonStr = '{"wallet": ['
    for i in range(len(cards)):
        if cards[i] == cards[-1]:
            jsonStr += '{"card_id": ' + str(cards[i][0]) + ', ' + cards[i][1][1:]
        else:
            jsonStr += '{"card_id": ' + str(cards[i][0]) + ', ' + cards[i][1][1:] + ', '
    jsonStr += ']}'
    print(jsonStr)

def getCardQr(jsonStr):
    pass

# inserts a row into account_cards
def addCardWalletConf(accId,cardId):
    query = "INSERT INTO account_cards(account_id, card_id) VALUES(%s,%s)"
    args = (accId,cardId)
    dbIns(query,args)

def removeCardWallet(accId, cardId):
    query = "DELETE FROM account_cards WHERE account_id = " + str(accId) + " card_id = " + str(cardId)
    dbQ(query)
#TESTING



#Takes form data sent from app and runs related function(s)
form = cgi.FieldStorage()
actionType = form.getvalue('type')
if actionType == 'register': ### ACCOUNT INITIATION FUNCTIONS
    username = form.getvalue('username')
    email = form.getvalue('email')
    password = form.getvalue('password')
    register(username,email,password)
#DONE
elif actionType == 'login':
    username = form.getvalue('username')
    password = form.getvalue('password')
    login(username,password)
#DONE
elif actionType == 'get_profiles': ### PROFILE FUNCTIONS
    accId = form.getvalue('account_id')
    getProfiles(accId)
#DONE
elif actionType == 'insert_profile':
    accId = form.getvalue('account_id')
    profileName = form.getvalue('profile_name')
    insertProfile(accId,profileName)
#DONE
elif actionType == 'get_profile_cards': # PROFILE CARDS
    profId = form.getvalue('profile_id')
    getProfileCards(profId)
#DONE
elif actionType == 'insert_profile_card':
    profId = form.getvalue('profile_id')
    cardName = form.getvalue('card_name')
    insertProfileCard(profId,cardName)
#WIP - extend functionality
elif actionType == 'get_profile_attributes': # PROFILE ATTRIBUTES
    profId = form.getvalue('profile_id')
    getProfileAttributes(profId)
#DONE
elif actionType == 'insert_profile_attributes':
    profId = form.getvalue('profile_id')
    jsonStr = form.getvalue('attr_2_ins')
    insertProfileAttributes(profId,jsonStr)
elif actionType == 'get_wallet': ### WALLET FUNCTIONS
    accId = form.getvalue('account_id')
    getWallet(accId)
#DONE
elif actionType == 'get_card_qr':
    #automates card download process
    pass
elif actionType == 'add_card_wallet_conf':
    accId = form.getvalue('account_id')
    cardId = form.getvalue('card_id')
    addCardWalletConf(accId,cardId)
#WIP
elif actionType == 'remove_card_wallet':
    accId = form.getvalue('account_id')
    cardId = form.getvalue('card_id')
    removeCardWallet(accId,cardId)
    #removes a card from account's wallet
#TESTING
else: #The following is to test if any changes to code breaks code in-browser; default response
    foo = { "Lynx Backend Script": "This is the default returned JSON string for backend.py", "err": True }
    data = json.dumps(foo)
    print(data)
