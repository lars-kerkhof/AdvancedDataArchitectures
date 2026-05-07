from flask import jsonify, make_response

from daos.user_dao import UserDAO
from db import Session
from jwtutil import encode_auth_token, decode_auth_token


# Adapted from Lab 9 user service.
# Reference: https://realpython.com/token-based-authentication-with-flask/

class User:

    @staticmethod
    def create(post_data):
        session = Session()
        try:
            email = post_data.get('email')
            password = post_data.get('password')
            if not email or not password:
                res = {'status': 'fail', 'message': 'Email and password are required.'}
                return make_response(jsonify(res)), 400

            # Check if user already exists (by email — lab bug filtered by id)
            existing = session.query(UserDAO).filter(UserDAO.email == email).first()
            if existing:
                res = {'status': 'fail', 'message': 'User already exists. Please log in.'}
                return make_response(jsonify(res)), 202

            try:
                user = UserDAO(email=email, password=password)
                session.add(user)
                session.commit()
                # Generate the auth token using the new user's id
                auth_token = encode_auth_token(user.id)
                res = {
                    'status': 'success',
                    'message': 'Successfully registered.',
                    'auth_token': auth_token,
                    'user_id': user.id
                }
                return make_response(jsonify(res)), 200
            except Exception as e:
                print(e)
                res = {'status': 'fail', 'message': 'Some error occurred. Please try again.'}
                return make_response(jsonify(res)), 401
        finally:
            session.close()

    @staticmethod
    def get(auth_header):
        """Verify a token from the Authorization: Bearer <token> header
        and return the associated user."""
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                auth_token = ''
        else:
            auth_token = ''

        if not auth_token:
            res = {'status': 'fail', 'message': 'Provide a valid auth token.'}
            return make_response(jsonify(res)), 401

        resp = decode_auth_token(auth_token)
        if isinstance(resp, str):
            # decode_auth_token returns an error string on failure
            res = {'status': 'fail', 'message': resp}
            return make_response(jsonify(res)), 401

        # resp is the user_id (string UUID)
        session = Session()
        try:
            user = session.query(UserDAO).filter(UserDAO.id == resp).first()
            if not user:
                res = {'status': 'fail', 'message': 'User not found for this token.'}
                return make_response(jsonify(res)), 404
            res = {
                'status': 'success',
                'data': {
                    'user_id': user.id,
                    'email': user.email,
                    'admin': user.admin,
                    'registered_on': user.registered_on.isoformat()
                }
            }
            return make_response(jsonify(res)), 200
        finally:
            session.close()
