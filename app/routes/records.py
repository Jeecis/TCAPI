import json
import uuid
from flask import Blueprint, request, jsonify
from redis_client import user_redis

record_blueprint = Blueprint('record', __name__)

@record_blueprint.route('/record', methods=['POST'])
def add_record():
    record_data = json.loads(request.data)
    name = record_data.get('name')
    data = record_data.get('data')

    if not name or not data:
        return jsonify({"error": "Invalid input"}), 400

    record_id = str(uuid.uuid4())
    try:
        user_redis.set(record_id, str({"name": name, "data": data}))
    except Exception:
        return jsonify({"Error": "Error occurred while writing to Redis"}), 500

    return jsonify({"message": "Record added successfully", "record": record_data}), 201


@record_blueprint.route('/record/<id>', methods=['GET'])
def get_record(id):
    try:
        record = user_redis.get(id)
        if not record:
            return jsonify({"Error": f"No record found for ID {id}"}), 404
    except Exception:
        return jsonify({"Error": "Error occurred while reading Redis entry"}), 500

    record_json_str = record.replace("'", '"')
    record_json = json.loads(record_json_str)

    return jsonify(record_json)


@record_blueprint.route('/record', methods=['DELETE'])
def delete_record():
    record_data = json.loads(request.data)
    id = record_data.get('id')

    if not id:
        return jsonify({"error": "Invalid input"}), 400

    try:
        user_redis.delete(id)
    except Exception:
        return jsonify({"Error": "Error occurred while deleting Redis entry"}), 500

    return jsonify({"message": "Record deleted successfully"}), 200


@record_blueprint.route('/record/list', methods=['GET'])
def get_all_records():
    records_list = []
    try:
        keys = user_redis.keys()
    except Exception:
        return jsonify({"Error": "Error occurred while reading Redis entries"}), 500

    for key in keys:
        try:
            record = user_redis.get(key)
            record_json_str = record.replace("'", '"')
            record_json = json.loads(record_json_str)
            records_list.append({key: record_json})
        except Exception:
            return jsonify({"Error": "Error occurred while reading Redis entries"}), 500

    return jsonify(records_list)