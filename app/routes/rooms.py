import json
from flask import Blueprint, request, jsonify
import uuid
from redis_client import user_redis
from login import Login

rooms_blueprint = Blueprint('login', __name__)

@rooms_blueprint.route('/room', methods=['POST'])
def add_room():
    record_data = json.loads(request.data)
    
    name = record_data.get('name')
    password = record_data.get('password')
    roomName = record_data.get('roomName')
    desc = record_data.get('description')
    roomID = uuid.uuid4()
    photo = record_data.get('photo')

    status = Login(name,password)




    if not status == 200:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        user_redis.set(name, str({"password": password, "rooms":{} }))
    except Exception:
        return jsonify({"Error": "Error occurred while writing to Redis"}), 500

    return jsonify({"message": "User added successfully", "user": name}), 201


@rooms_blueprint.route('/user/login', methods=['GET'])
def login():
    record_data = json.loads(request.data)
    name = record_data.get('name')
    password = record_data.get('password')

    status = Login(name, password)

    match(status):
        case 404:
            return jsonify({"Error": f"No user found for name {name}"}), 404
        case 401:
            return jsonify({"Error": f"Invalid password"}), 401
        case 500:
            return jsonify({"Error": "Error occurred while reading Redis entry"}), 500
        
    return jsonify("Success")

def checkExistance(name):
    exists = user_redis.get(name)
    if exists is None:
        return False
    return True

def Login(name, password):
    try:
        record = user_redis.get(name)
        if not record:
            return 404
    except Exception:
        return 500

    record_json_str = record.replace("'", '"')
    record_json = json.loads(record_json_str)

    if password != record_json["password"]:
        return 401
    
    return 200
