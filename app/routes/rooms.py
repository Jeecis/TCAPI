import json
from flask import Blueprint, request, jsonify
import uuid
from redis_client import user_redis, inventory_redis
from .login import Login

rooms_blueprint = Blueprint('rooms', __name__)

@rooms_blueprint.route('/room', methods=['POST'])
def add_room():
    record_data = json.loads(request.data)

    name = record_data.get('name')
    password = record_data.get('password')

    roomName = record_data.get('roomName')
    desc = record_data.get('description')
    roomID =  str(uuid.uuid4()) 
    photo = record_data.get('photo')

    status = Login(name,password)

    if not status == 200:
        return jsonify({"error": "Unauthorized"}), 401

    user_data = user_redis.get(name)

    user_json_str = user_data.replace("'", '"')

    user_data = json.loads(user_json_str)

    new_room = {
        "roomName": roomName,
        "description": desc,
        "photo": photo
    }

    # Store the room in the dictionary with roomID as the key
    user_data["rooms"][roomID] = new_room

    # Store updated user data back into Redis
    user_redis.set(name, json.dumps(user_data))

    # Capture and print any additional variables in the request
    required_keys = {"name", "password", "roomName", "description", "photo"}
    additional_data = {key: value for key, value in record_data.items() if key not in required_keys}
    inventory_redis.set(roomID, json.dumps(additional_data))

    return jsonify({"message": "Room added successfully", "room": new_room}), 201



@rooms_blueprint.route('/room', methods=['DELETE'])
def delete_room():
    record_data = json.loads(request.data)
    name = record_data.get('name')
    password = record_data.get('password')
    room_id =record_data.get('roomID')

    # Authenticate the user
    status = Login(name, password)
    if not status == 200:
        return jsonify({"error": "Unauthorized"}), 401


    user_data = user_redis.get(name)

    user_json_str = user_data.replace("'", '"')

    user_data = json.loads(user_json_str)

    if not user_data["rooms"][room_id]:
        return jsonify({"error": "Room not found"}), 404
    
    del user_data["rooms"][room_id]

    user_redis.set(name, json.dumps(user_data))

    if inventory_redis.exists(room_id):
        inventory_redis.delete(room_id)

    return jsonify({"message": "Room deleted successfully"}), 200

@rooms_blueprint.route('/inventory', methods=['PUT'])
def get_inventory():
    try:
        record_data = json.loads(request.data)
        name = record_data.get('name')
        password = record_data.get('password')
        room_id =record_data.get('roomID')

        status = Login(name, password)
        if not status == 200:
            return jsonify({"error": "Unauthorized"}), 401
        
        inventory_data = inventory_redis.get(room_id)

        if not inventory_data:
            return jsonify({"error": "Room inventory not found"}), 404
        
        inv_json_str = inventory_data.replace("'", '"')

        # Parse inventory data
        inventory_data = json.loads(inv_json_str)

        return jsonify({"roomID": room_id, "inventory": inventory_data}), 200
    except Exception as e:
        return jsonify({"error": f"Error occurred: {str(e)}"}), 500
    
@rooms_blueprint.route('/inventory/list', methods=['PUT'])
def get_all_inventory():
    records_list = []
    try:
        keys = inventory_redis.keys()
    except Exception:
        return jsonify({"Error": "Error occurred while reading Redis entries"}), 500

    for key in keys:
        try:
            record = inventory_redis.get(key)
            record_json_str = record.replace("'", '"')
            record_json = json.loads(record_json_str)
            records_list.append({key: record_json})
        except Exception:
            return jsonify({"Error": "Error occurred while reading Redis entries"}), 500

    return jsonify(records_list)