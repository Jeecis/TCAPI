import json
from flask import Blueprint, request, jsonify
from redis_client import user_redis, booking_redis
import time
import random
from datetime import datetime
import smtplib
import ssl
from email.message import EmailMessage

booking_blueprint = Blueprint('booking', __name__)

@booking_blueprint.route('/booking', methods=['POST'])
def add_booking():
    record_data = json.loads(request.data)

    roomID = record_data.get('roomID')
    name = record_data.get('recipient')
    startTime = record_data.get('from')
    endTime = record_data.get('to')
    email = record_data.get('email')

    # Convert startTime and endTime to integers and calculate time difference
    try:
        startTime = int(startTime)
        endTime = int(endTime)
    except ValueError:
        return jsonify({"error": "Invalid time format. 'from' and 'to' must be integers."}), 400
    
    now = datetime.now().minute
    
    time = endTime-now

    if time <= 0:
        return jsonify({"error": "'to' must be greater than 'from'."}), 400

    required_keys = {"roomID", "recipient", "from", "to", "email"}
    additional_data = {key: value for key, value in record_data.items() if key not in required_keys}

    # Create the booking data
    new_booking = {
        "recipient": name,
        "from": startTime,
        "to": endTime,
        'email': email,
        'inventory': additional_data
    }

    # Generate a unique booking code
    code = generateCode()

    # Create the Redis key
    key = f"{roomID}:{code}"

    send_email(email, code)

    try:
        booking_redis.setex(key, time, json.dumps(new_booking))  # Assuming 'time' is in minutes
    except Exception as e:
        return jsonify({"error": f"Failed to store booking: {str(e)}"}), 500

    return jsonify({"message": "Booking done successfully", "room": roomID, "code": code}), 201

@booking_blueprint.route('/booking', methods=['PUT'])
def get_booking():
    try:
        record_data = json.loads(request.data)

        room_id = record_data.get('roomID')
        code = record_data.get('code')
        key = f"{room_id}:{code}"
        
        booking_data = booking_redis.get(key)
        
        if not booking_data:
            return jsonify({"error": "Booking not found"}), 404
        
        book_json_str = booking_data.replace("'", '"')
        
        booking_data = json.loads(book_json_str)

        startTime = int(booking_data["from"])
        current_time=time.time()
        if startTime>current_time:
            return jsonify({"error": "You dont have a booking right now"}), 401
        
        return jsonify("Success"), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve booking: {str(e)}"}), 500

@booking_blueprint.route('/booking', methods=['DELETE'])
def delete_booking():
    try:
        # Parse request data
        record_data = json.loads(request.data)

        # Get roomID and code from the request
        room_id = record_data.get('roomID')
        code = record_data.get('code')

        if not room_id or not code:
            return jsonify({"error": "Missing 'roomID' or 'code' in the request."}), 400

        # Create the Redis key
        key = f"{room_id}:{code}"

        # Check if the booking exists
        if not booking_redis.exists(key):
            return jsonify({"error": "Booking not found"}), 404

        # Delete the booking
        booking_redis.delete(key)

        return jsonify({"message": "Booking deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete booking: {str(e)}"}), 500
    
@booking_blueprint.route('/booking/list', methods=['GET'])
def get_all_booking():
    records_list = []
    try:
        keys = booking_redis.keys()
    except Exception:
        return jsonify({"Error": "Error occurred while reading Redis entries"}), 500

    for key in keys:
        try:
            record = booking_redis.get(key)
            record_json_str = record.replace("'", '"')
            record_json = json.loads(record_json_str)
            records_list.append({key: record_json})
        except Exception:
            return jsonify({"Error": "Error occurred while reading Redis entries"}), 500

    return jsonify(records_list)

def generateCode():
    while True:
        # Generate a random 4-digit code
        code = f"{random.randint(1000, 9999)}"
        
        # Check if any key in booking_redis ends with ':code' and matches the generated code
        matching_keys = booking_redis.scan_iter(f"*:{code}")
        
        if not any(matching_keys):  # If no matching key exists
            return code

def send_email(receiver_email, pin_code):
    
    body_template = """
    <html>
    <body>

    <h1>Your pin code is {pin_code}</h1>
    
    </body>
    </html>
    """

    body=body_template.format(
        pin_code=pin_code
    )



    em = EmailMessage()
    em['From'] = "cryptoemail377@gmail.com"
    em['To'] = receiver_email
    em['Subject'] = "Your pin code"
    em.add_alternative(body, subtype='html')

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login("cryptoemail377@gmail.com", "durh yszf uljk xwet")
            smtp.send_message(em)
            print(f"Email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"Error sending email to {receiver_email}: {e}")
        raise