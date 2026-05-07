import bcrypt
from flask import make_response, jsonify

from daos.user_dao import UserDAO
from db import Session
from jwtutil import encode_auth_token


# Adapted from Lab 9 user service.

class LoginAPI:
    @staticmethod
    def login(post_data):
        session = Session()
        try:
            email = post_data.get('email')
            password = post_data.get('password')
            if not email or not password:
                res = {'status': 'fail', 'message': 'Email and password are required.'}
                return make_response(jsonify(res)), 400

            user = session.query(UserDAO).filter(UserDAO.email == email).first()

            if user and bcrypt.checkpw(
                password.encode('utf-8'),
                user.password.encode('utf-8')   # password stored as string, re-encode for bcrypt
            ):
                auth_token = encode_auth_token(user.id)
                if auth_token:
                    res = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token,
                        'user_id': user.id
                    }
                    return make_response(jsonify(res)), 200
                else:
                    res = {'status': 'fail', 'message': 'There is no token.'}
                    return make_response(jsonify(res)), 401
            else:
                res = {'status': 'fail', 'message': 'Invalid email or password.'}
                return make_response(jsonify(res)), 401
        except Exception as e:
            print(e)
            res = {'status': 'fail', 'message': 'Try again'}
            return make_response(jsonify(res)), 500
        finally:
            session.close()
