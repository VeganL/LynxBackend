import json, cgi, cgitb, os, sys, subprocess
from mysql.connector import MySQLConnection, Error
from pythonMySQL_dbConfig import readDbConfig

insCounter = 0

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
        
        for row in iterRow(cursor,50):
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
        dbW(query,args)

#Login function, returns account_id connected to valid username and password
def login(username,password):
    query = "SELECT account_id, username, password FROM accounts WHERE username = %s AND password = %s"
    args = (username,password)
    uid = dbQ(query,args)
    if len(uid) == 1 and uid[0][1] == username and uid[0][2] == password:
        getProfiles(uid[0][0])
    else:
        print('{"err":"Invalid login information"}')

def insertPhoto(photo):
    uploadDir = '/var/www/html/LynxPhotos/'
    if photo.filename:
        fn = os.path.basename(photo.filename)
        open(uploadDir + fn, 'wb').write(photo.file.read())

def getProfiles(accId):
    query = "SELECT profile_id, title FROM profiles WHERE account_id = " + str(accId)
    profiles = dbQ(query)

    jsonStr = '{"account_id":' + str(accId) + ', "profiles": ['
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

def editProfile(profId,attributesJson):
    attrDict = json.loads(attributesJson)
    attrStrL = []
    for key, value in attrDict.items():
        attrStrL.append('{"' + key + '":"' + str(value) + '"}')

    query = "SELECT attribute_id FROM attributes WHERE profile_id = " + str(profId)
    raw = dbQ(query)
    attrIdL = []
    for i in raw:
        attrIdL.append(i[0])

    if len(attrIdL) == len(attrStrL):
        query = "UPDATE attributes SET attribute = %s WHERE attribute_id = %s"
        for i in range(len(attrIdL)):
            args = (attrStrL[i],attrIdL[i])
            dbW(query,args)
    else:
        print('{"err":"JSON string is in an invalid format"}')

def getProfileCards(profId):
    query = "SELECT card_id, attribute_id_list FROM cards WHERE profile_id = " + str(profId)
    cards = dbQ(query)
    jsonStr = '{"profile_cards": ['
    for i in range(len(cards)):
        attrIdList = json.loads(cards[i][1])
        jsonStr += '{"card_id":' + str(cards[i][0]) + ', "attributes": {'
        for r in range(len(attrIdList)):
            query = "SELECT attribute FROM attributes WHERE attribute_id = " + str(attrIdList[r])
            attribute = dbQ(query)
            jsonStr += attribute[0][0][1:-1]
            if attrIdList[r] != attrIdList[-1]:
                jsonStr += ', '
        jsonStr += '}'
        if cards[i] != cards[-1]:
            jsonStr += '}, '
    jsonStr += '}]}'
    print(jsonStr)

def insertProfileCard(profId,attrListStr):
    query = "INSERT INTO cards(profile_id,attribute_id_list) VALUES (%s,%s)"
    if '{' in attrListStr or '}' in attrListStr:
        print('{"err":"Invalid attribute list format"}')
    else:
        args = (profId,attrListStr)
        dbW(query,args)

def editProfileCard(cardId,attrListStr):
    query = "UPDATE cards SET attribute_id_list = %s WHERE card_id = %s"
    if '{' in attrListStr or '}' in attrListStr:
        print('{"err":"Invalid attribute list format"}')
    else:
        args = (attrListStr,cardId)
        dbW(query,args)

def removeProfileCard(cardId):
    query = "DELETE FROM cards WHERE card_id = " + str(cardId)
    dbW(query)

def getWallet(accId):
    query = "SELECT card_id FROM account_cards WHERE account_id = " + str(accId)
    cardIds = dbQ(query)
    jsonStr = '{"account_id":' + str(accId) + ', "wallet": ['
    for x in range(len(cardIds)):
        for i in range(len(cardIds[x])):
            jsonStr += '{"card_id":' + str(cardIds[x][i]) + ', "attributes": {'
            query = "SELECT attribute_id_list FROM cards WHERE card_id = " + str(cardIds[x][i])
            cardAttr = dbQ(query)
            cardAttr = json.loads(cardAttr[0][0])
            for r in range(len(cardAttr)):
                query = "SELECT attribute FROM attributes WHERE attribute_id = " + str(cardAttr[r])
                attr = dbQ(query)
                jsonStr += attr[0][0][1:-1]
                if cardAttr[r] != cardAttr[-1]:
                    jsonStr += ', '
            jsonStr += '}'
        if cardIds[x] != cardIds[-1]:
            jsonStr += '}, '
    jsonStr += '}]}'
    print(jsonStr)

def getCardQr(cardId):
    query = "SELECT attribute_id_list FROM cards WHERE card_id = " + str(cardId)
    cardAttr = dbQ(query)
    cardAttr = json.loads(cardAttr[0][0])
    jsonStr = '{"card_id":' + str(cardId) + ', "attributes": {'
    for i in range(len(cardAttr)):
        query = "SELECT attribute FROM attributes WHERE attribute_id = " + str(cardAttr[i])
        attr = dbQ(query)
        jsonStr += attr[0][0][1:-1]
        if cardAttr[i] != cardAttr[-1]:
            jsonStr += ', '
    jsonStr += '}}' 
    print(jsonStr)

def addCardWalletConf(accId,cardId):
    query = "INSERT INTO account_cards(account_id,card_id) VALUES (%s,%s)"
    args = (accId,cardId)
    dbW(query,args)

def removeCardWallet(cardId,accId):
    query = "DELETEalter table attributes auto_increment = 1;alter table attributes auto_increment = 1;alter table attributes auto_increment = 1;alter table attributes auto_increment = 1; FROM account_cards WHERE card_id = %s and account_id = %s"
    args = (cardId,accId)
    dbW(query,args)
