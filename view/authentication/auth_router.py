import datetime
import uuid
from functools import wraps

import jwt
from flask import Blueprint
from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash

from application.authentication.auth_model import User

auth_router = Blueprint('auth', __name__)

__secret = "verrrry secret key"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, __secret, algorithms=["HS256"])
            current_user = User.get(User.public_id == data['publicId'])
        except jwt.exceptions.ExpiredSignatureError as e:
            return jsonify({'message': 'Token is outdated!'}), 401
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@auth_router.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    users = User.select()

    output = []

    for user in users:
        user_data = {}
        user_data['publicId'] = user.public_id
        user_data['email'] = user.email
        user_data['password'] = user.password
        output.append(user_data)

    return jsonify({'users': output})


@auth_router.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    user = User.get_or_none(User.public_id == public_id)

    if not user:
        return jsonify({'message': 'No user found!'}), 404

    user_data = {}
    user_data['publicId'] = user.public_id
    user_data['email'] = user.email
    user_data['password'] = user.password

    return jsonify(user_data)


@auth_router.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data.get('password'), method='sha256')

    new_user = User.create(public_id=str(uuid.uuid4()), email=data.get('email'), password=hashed_password)
    if new_user.save() == 1:
        return jsonify({'message': 'New user created!'})
    return jsonify({'message': 'New user creation fail!'}), 400


@auth_router.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.get_or_none(email=auth.username)

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {'publicId': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, __secret,
            algorithm="HS256")
        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
