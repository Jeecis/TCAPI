import json
from flask import Blueprint, request, jsonify
from redis_client import user_redis

login_blueprint = Blueprint('login', __name__)

@login_blueprint.route('/user/register', methods=['POST'])
def register():
    record_data = json.loads(request.data)
    name = record_data.get('name')
    password = record_data.get('password')

    if checkExistance(name):
        return jsonify({"error": "User with such name already exists"}), 500

    try:
        user_redis.set(name, str({"password": password, "rooms":{} }))
    except Exception:
        return jsonify({"Error": "Error occurred while writing to Redis"}), 500

    return jsonify({"message": "User added successfully", "user": name}), 201


@login_blueprint.route('/user/login', methods=['PUT'])
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

@login_blueprint.route('/user', methods=['DELETE'])
def delete_user():
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
        
    user_redis.delete(name)
        
    return jsonify(f"User {name} deleted")

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
