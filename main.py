from google.cloud import datastore
from flask import Flask, request, make_response
import json
from json2html import *
import constants

app = Flask(__name__)
client = datastore.Client()

#allows for debugging in VS code.
from werkzeug.debug import DebuggedApplication
app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

@app.route('/')
def index():
    return "Please navigate to /boats"

jsonErrorStringBoatID = '{ "Error":"No boat with this boat_id exists"}'
jsonErrorStringArgs = '{ "Error":"The request object is missing at least one of the required attributes"}'
jsonOnlyAcceptJson = '{ "Error":"This method only accepts JSON"}'
jsonTypeNotSupported = '{ "Error": "This type is not supported, must be JSON or HTML"}'
jsonInvalidRequest= '{ "Error": "IDs are immutable"}'
jsonCannotDelAll = '{ "Error": "Cannot delete or edit the list of all boats"}'
jsonNameNotUnique = '{ "Error": "Name must be unique"}'
jsonErrorInvalidInputName = '{ "Error": "Name cannot be longer than 16 characters. It can also only contain letters of the alphabet"}'
jsonErrorInvalidInputType = '{ "Error": "Type cannot be longer than 16 characters. It can also only contain letters of the alphabet"}'
jsonErrorInvalidInputLength = '{ "Error": "Length cannot be longer than 7 digits. It can also only contain numbers"}'
jsonErrorTooManyAttribs = '{ "Error": "Boats only have 3 attributes Name, Length and Type"}'
jsonErrorMustBeInt =  '{ "Error": "Length must be an integer"}'
jsonErrorMustBeStrType =  '{ "Error": "Type must be a string"}'
jsonErrorMustBeStrName =  '{ "Error": "Name must be a string"}'
#assigns the self variable
def create_self(item):
    selfURL = request.base_url + '/' + str(item.id)
    item["self"] = selfURL
    return item

def create_self_second(item):
    item["self"] = request.base_url
    return item

#takes in list of results and returns a bool if key exists or not.
def check_ID_existence(results, id):
    for object in results:
        if id == 'null':
            break
        if object.id == int(id):
            return True #id is in
    return False

#takes in list of results and returns a bool if key exists or not.
def check_name_existence(results, nameStr):
    for object in results:
        if object['name'] == nameStr:
            return True #id is in
    return False

def validate_input(input, value):
    if input == "name":
        if len(value) > 16:
            return False
        for eachChar in value:
            if ((eachChar >= 'a' and eachChar <= 'z') or (eachChar >= 'A' and eachChar <= 'Z')):
                continue
            if (eachChar == ' '):
                continue
            else:
                return False
        return True
    elif input == "type":
        if len(value) > 16:
            return False
        for eachChar in value:
            if ((eachChar >= 'a' and eachChar <= 'z') or (eachChar >= 'A' and eachChar <= 'Z')):
                continue
            if (eachChar == ' '):
                continue
            else:
                return False
        return True
    elif input == "length":
        iterable = str(value)
        if len(str(value)) > 7:
            return False
        for eachChar in iterable:
            try:
                if (int(eachChar) > 9 or int(eachChar) < 0):
                    return False
            except:
                return False
        return True
    else:
        return 'Invalid attribute supplied'

def count_valid_attribs(content):
    count = 0
    if "name" in content:
        count += 1
    if "length" in content:
        count += 1
    if "type" in content:
        count += 1
    return count

@app.route('/boats', methods=['POST','GET', 'PUT', 'DELETE'])
def boats_get_or_post():
    if request.method == 'POST':
        content = request.get_json()
        if (not(content)): #if could not get the content in json format
            return(jsonOnlyAcceptJson, 415)
        if "name" not in content or "type" not in content or "length" not in content:
            return (jsonErrorStringArgs, 400)
        if len(content) > 3:
            return (jsonErrorTooManyAttribs, 400)
        query = client.query(kind=constants.boats) #load the boats
        results = list(query.fetch()) #store boats into a list
        if (check_name_existence(results, content['name']) == False): #if the name is not unque, return 403
            new_boat = datastore.entity.Entity(key=client.key(constants.boats))
            if type(content['name']) != str:
                return (jsonErrorMustBeStrName, 400)
            if (validate_input('name', content['name']) == True):
                pass
            else:
                return (jsonErrorInvalidInputName, 400)
            if type(content['type']) != str:
                return (jsonErrorMustBeStrType, 400)
            if (validate_input('type', content['type']) == True):
                pass
            else:
                return (jsonErrorInvalidInputType, 400)
            if (validate_input('length', content['length']) == True):
                if type(content['length']) != int:
                    return (jsonErrorMustBeInt, 400)
            else:
                return (jsonErrorInvalidInputLength, 400)
            new_boat.update({"name": content["name"], "type": content["type"],
            "length": content["length"]})
            client.put(new_boat)
            new_boat["id"] = new_boat.id
            create_self(new_boat)
            return (new_boat, 201)
        else:
            return (jsonNameNotUnique, 403)

    
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        if 'application/json' in request.accept_mimetypes:
            query = client.query(kind=constants.boats)
            results = list(query.fetch())
            for e in results:
                e["id"] = e.key.id
            jsonData = json.dumps(results)
            return (jsonData, 200)
        elif 'text/html' in request.accept_mimetypes:
            res = make_response(json2html.convert(json = json.dumps(results)))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 200
            return res
        else:
            return (jsonTypeNotSupported, 406)
    
    elif request.method == 'PUT' or request.method == 'DELETE':
        return (jsonCannotDelAll, 405)
    
    else:
        return 'Method not recogonized'

@app.route('/boats/<id>', methods=['GET', 'DELETE', 'PUT', 'PATCH'])
def boats_get_delete_patch(id):
    if request.method == 'DELETE':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        if check_ID_existence(results, id) == False:
            return(jsonErrorStringBoatID, 404)
        boat_key = client.key(constants.boats, int(id))
        client.delete(boat_key) #delete the boat
        return ('', 204)
    
    elif request.method == 'PUT':
        content = request.get_json()
        if (not(content)): #if could not get the content in json format
            return(jsonOnlyAcceptJson, 415)
        if  "id" in content:
            return (jsonInvalidRequest, 400)
        if "name" not in content or "type" not in content or "length" not in content:
            return (jsonErrorStringArgs, 400)
        query = client.query(kind=constants.boats)
        results = list(query.fetch()) #load boats into list object
        if check_ID_existence(results, id) == False:
            return(jsonErrorStringBoatID, 404)
        if type(content['name']) != str:
            return (jsonErrorMustBeStrName, 400)
        if type(content['type']) != str:
            return (jsonErrorMustBeStrType, 400)
        if (check_name_existence(results, content['name']) == False): #if the name is not unque, return 403
            if (validate_input('name', content['name']) == True):
                pass
            else:
                return (jsonErrorInvalidInputName, 400)
            if (validate_input('type', content['type']) == True):
                pass
            else:
                return (jsonErrorInvalidInputType, 400)
            if (validate_input('length', content['length']) == True):
                if type(content['length']) != int:
                    return (jsonErrorMustBeInt, 400)
            else:
                return (jsonErrorInvalidInputLength, 400)
            if (count_valid_attribs(content) < len(content)):
                return(jsonErrorTooManyAttribs, 400)
            boat_key = client.key(constants.boats, int(id))
            boat = client.get(key=boat_key) #load the boat
            boat.update({"name": content["name"], "type": content["type"],
            "length": content["length"]})
            client.put(boat)
            boat['id'] = int(id)
            create_self_second(boat)
            return (boat, 303)
        else:
            return (jsonNameNotUnique, 403)
    
    elif request.method == 'PATCH':
        content = request.get_json()
        if (not(content)): #if could not get the content in json format
            return(jsonOnlyAcceptJson, 415)
        if  "id" in content:
            return (jsonInvalidRequest, 400)
        if "name" not in content and "type" not in content and "length" not in content:
            return (jsonErrorStringArgs, 400)
        query = client.query(kind=constants.boats)
        results = list(query.fetch()) #load boats into list object
        if check_ID_existence(results, id) == False:
            return(jsonErrorStringBoatID, 404)
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key) #load the boat
        count = count_valid_attribs(content)
        if "name" in content:
            if type(content['name']) != str:
                return (jsonErrorMustBeStrName, 400)
            if (validate_input('name', content['name']) == True): #make sure name is not longer than 16 chars
                if (check_name_existence(results, content['name']) == False): #if the name is not unique, return 403
                    boat.update({"name": content["name"]})
                else:
                    return (jsonNameNotUnique, 403)
            else:
                return (jsonErrorInvalidInputName, 400)
        if "length" in content:
            if type(content['length']) != int:
                return (jsonErrorMustBeInt, 400)
            if (validate_input('length', content['length']) == True):
                boat.update({"length": content["length"]})
            else:
                return (jsonErrorInvalidInputLength, 400)
        if "type" in content:
            if type(content['type']) != str:
                return (jsonErrorMustBeStrType, 400)
            if (validate_input('type', content['type']) == True):
                boat.update({"type": content["type"]})
            else:
                return (jsonErrorInvalidInputType, 400)
        if count < len(content):
            return (jsonErrorTooManyAttribs, 400)
        client.put(boat)
        boat['id'] = int(id)
        create_self_second(boat)
        return (boat, 200)

    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch()) #load boats into list object          
        if check_ID_existence(results, id) == False:
            return(jsonErrorStringBoatID, 404)
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key) #load the boat
        boat['id'] = int(id)
        if 'application/json' in request.accept_mimetypes:
            jsonData = json.dumps(boat)
            return (jsonData, 200)
        elif 'text/html' in request.accept_mimetypes:
            res = make_response(json2html.convert(json = json.dumps(boat)))
            res.headers.set('Content-Type', 'text/html')
            res.status_code = 200
            return res
        else:
            return (jsonTypeNotSupported, 406)

    else:
        return 'Method not recogonized'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
    
    
