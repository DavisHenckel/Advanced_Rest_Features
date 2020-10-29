from google.cloud import datastore
from flask import Flask, request
import json
import constants

app = Flask(__name__)
client = datastore.Client()

#allows for debugging in VS code.
from werkzeug.debug import DebuggedApplication
app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

@app.route('/')
def index():
    return "Please navigate to /boats"\

jsonErrorStringArgs = '{ "Error":"The request object is missing at least one of the required attributes"}'

#assigns the self variable
def create_self(item):
    selfURL = request.base_url + '/' + str(item.id)
    item["self"] = selfURL
    return item

@app.route('/boats', methods=['POST','GET'])
def boats_get_or_post():
    if request.method == 'POST':
        content = request.get_json()
        if "name" not in content or "type" not in content or "length" not in content:
            return (jsonErrorStringArgs, 400)
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({"name": content["name"], "type": content["type"],
          "length": content["length"],"loads": content["loads"]})
        client.put(new_boat)
        new_boat["id"] = new_boat.id
        create_self(new_boat)
        return (new_boat, 201)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)