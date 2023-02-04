from app import application
from flask import request, jsonify, make_response
from database import db_session, Client, Validators, BlocksToValidate
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
import random
import socket
from sqlalchemy import desc

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

logged_on_users = list()


@application.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response("Could not verify headers",401, {"WWW-Authenticate": 'Basic realm="Login required!"'})

    user = Client.query.filter_by(name=auth.username).first()

    if not user:
        return make_response("Could not verify user",401, {"WWW-Authenticate": 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        if user.name not in logged_on_users:
            logged_on_users.append(user.name)
            token = jwt.encode({'id': user.id, 'exp': datetime.utcnow() + timedelta(minutes=30)}, application.config["SECRET_KEY"])
            return jsonify({'token': token, 'user_id': str(user.id)})
        else:
            return jsonify('MESSAGE', 'ALREADY LOGGED IN'), 406


    return make_response("Could not verify password", 401, {"WWW-Authenticate": 'Basic realm="Login required!"'})

@application.route('/client', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data["password"], method='sha256')

    tokens = random.randint(10,100)
    new_client = Client(name=data["name"], password=hashed_password, tokens=tokens)
    db_session.add(new_client)
    db_session.commit()

    return jsonify({'message': 'NEW USER CREATED'})

@application.route('/client/<id>', methods=["GET"])
# @token_required
def get_users(id):
    user = Client.query.filter_by(id=id).first()
    is_validator = False

    if not user:
        return jsonify({'message':'NO USER FOUND'})

    validator = Validators.query.filter_by(client=id).first()

    if validator:
        is_validator = True

    user_data = {}
    user_data['id'] = user.id
    user_data['name'] = user.name
    user_data['tokens'] = user.tokens
    user_data['is_validator'] = is_validator

    return jsonify({'user':user_data})

@application.route('/clients', methods=['GET'])
def get_all_users():
    items = Client.query.all()
    output = []
    for item in items:
        data = {}
        data['id'] = item.id
        data['username'] = item.name
        data['password'] = item.password
        data['tokens'] = item.tokens
        output.append(data)
    return jsonify({'users': output})

@application.route('/loggedOnClients', methods=['GET'])
def get_logged_on_clients():
    output = []
    for item in logged_on_users:
        data = {}
        data['username'] = item
        output.append(data)
    return jsonify({'users': output})


@application.route("/server_test", methods=["GET"])
def server_test():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect(ADDR)
    print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")
    connection.send("!LIST".encode(FORMAT))
    info = connection.recv(SIZE).decode(FORMAT)

    num_list = info.split('/')

    return jsonify({'numbers': num_list})

@application.route("/validator", methods=["POST"])
def add_validator():
    data = request.get_json()
    user = Client.query.filter_by(id=data["user_id"]).first()
    is_validator = Validators.query.filter_by(client=data["user_id"]).first()

    if not user:
        return jsonify({'message':'THIS USER DOES NOT EXISTS'})

    if is_validator:
        return jsonify({'message':'USER IS ALREADY A VALIDATOR'})

    tokens = int(user.tokens)
    staked_amount = int(data["stake"])

    if staked_amount > tokens:
        return jsonify({'message':'YOU DO NOT HAVE ENOUGH TOKENS TO STAKE THAT AMOUNT'})
    else:
        tokens -= staked_amount
        user.tokens = tokens
        new_validator = Validators(client=data["user_id"], staked_amount=staked_amount)
        db_session.add(new_validator)
        db_session.commit()
        return jsonify({'message':'NEW VALIDATOR ADDED'})

@application.route("/validators", methods=["GET"])
def get_validators():
    validators = Validators.query.all()

    output = []
    for item in validators:
        client = Client.query.filter_by(id=item.client).first()
        data = {}
        data["id"] = client.id
        data["name"] = client.name
        data["staked_amount"] = item.staked_amount
        output.append(data)

    return jsonify({'validators': output})


@application.route('/winner', methods=["POST"])
def add_winning_validator():
    data = request.get_json()
    winner = Validators.query.filter_by(id=data["id"]).first()

    new_block = BlocksToValidate(validator=winner.id, data=data["data"])
    db_session.add(new_block)
    db_session.commit()
    return jsonify({'message': 'added block'})

@application.route('/most_recent_winner', methods=["GET"])
def get_most_recent_winner():
    winner = BlocksToValidate.query.order_by(BlocksToValidate.time_created.desc()).first()

    data = {}
    if winner:
        val_id = Validators.query.filter_by(id=winner.validator).first()
        if val_id:
            client = Client.query.filter_by(id=val_id.client).first()
            data["id"] = client.id
            data["name"] = client.name
            data["time"] = winner.time_created


    return jsonify({'message': data})

@application.route('/blocks_to_mine/<id>', methods=["GET"])
def mine_blocks(id):
    val = Validators.query.filter_by(client=id).first()

    if val:
        blocks = BlocksToValidate.query.filter_by(validator=val.id)

        output = []
        for block in blocks:
            data = {}
            data["data"] = block.data
            data["time"] = block.time_created
            output.append(data)

        return jsonify({'blocks': output})
    else:
        return jsonify({'message': 'NOT A VALIDATOR'})

@application.route('/validate_block/<user_id>/<block_id>', methods=["POST"])
def validate_block(user_id, block_id):
    return jsonify({'message': 'NOT A VALIDATOR'})


@application.route("/blockchain", methods=["GET"])
def chain():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect(ADDR)
    print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")
    connection.send("!CHAIN".encode(FORMAT))
    info = connection.recv(SIZE).decode(FORMAT)
    output = []
    block = info.split('#')

    for b in block:
        data = {}
        temp = b.split("£")
        if len(temp) != 1:
            data["index"] = temp[0]
            data["timestamp"] = temp[1]
            data["hash"] = temp[2]
            data["previous_hash"] = temp[3]
            data["validator"] = temp[4]
            output.append(data)
    return jsonify({'blockchain': output})


if __name__ == '__main__':
    application.run(host="0.0.0.0", port=8080, debug=True)
