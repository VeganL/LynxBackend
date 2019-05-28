#!/usr/bin/python
''' Imports of necessary modules '''
from functions import *
cgitb.enable()

#Defines resulting page/text as json format
print('Content-type: application/json\n')

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
elif actionType == 'get_profile_cards':
    profId = form.getvalue('profile_id')
    getProfileCards(profId)
elif actionType == 'insert_profile_card':
    profId = form.getvalue('profile_id')
    attrListStr = form.getvalue('attr_json_array')
    insertProfileCard(profId,attrListStr)
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