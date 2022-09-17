# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import datetime, timezone, timedelta

from functools import wraps
import random
import time

from flask import request
from flask_restx import Api, Resource, fields

import jwt

from .models import db, Users, JWTTokenBlocklist
from .config import BaseConfig

from faker import Faker
import json

rest_api = Api(version="1.0", title="Users API")


"""
    Flask-Restx models for api request and response data
"""

signup_model = rest_api.model('SignUpModel', {"username": fields.String(required=True, min_length=2, max_length=32),
                                              "email": fields.String(required=True, min_length=4, max_length=64),
                                              "password": fields.String(required=True, min_length=4, max_length=16)
                                              })

login_model = rest_api.model('LoginModel', {"email": fields.String(required=True, min_length=4, max_length=64),
                                            "password": fields.String(required=True, min_length=4, max_length=16)
                                            })

user_edit_model = rest_api.model('UserEditModel', {"userID": fields.String(required=True, min_length=1, max_length=32),
                                                   "username": fields.String(required=True, min_length=2, max_length=32),
                                                   "email": fields.String(required=True, min_length=4, max_length=64)
                                                   })


"""
   Helper function for JWT token required
"""

def token_required(f):

    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if "authorization" in request.headers:
            token = request.headers["authorization"]

        if not token:
            return {"success": False, "msg": "Valid JWT token is missing"}, 400

        try:
            data = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=["HS256"])
            current_user = Users.get_by_email(data["email"])

            if not current_user:
                return {"success": False,
                        "msg": "Sorry. Wrong auth token. This user does not exist."}, 400

            token_expired = db.session.query(JWTTokenBlocklist.id).filter_by(jwt_token=token).scalar()

            if token_expired is not None:
                return {"success": False, "msg": "Token revoked."}, 400

            if not current_user.check_jwt_auth_active():
                return {"success": False, "msg": "Token expired."}, 400

        except:
            return {"success": False, "msg": "Token is invalid"}, 400

        return f(current_user, *args, **kwargs)

    return decorator


"""
    Flask-Restx routes
"""


@rest_api.route('/api/users/register')
class Register(Resource):
    """
       Creates a new user by taking 'signup_model' input
    """

    @rest_api.expect(signup_model, validate=True)
    def post(self):

        req_data = request.get_json()

        _username = req_data.get("username")
        _email = req_data.get("email")
        _password = req_data.get("password")

        user_exists = Users.get_by_email(_email)
        if user_exists:
            return {"success": False,
                    "msg": "Email already taken"}, 400

        new_user = Users(username=_username, email=_email)

        new_user.set_password(_password)
        new_user.save()

        return {"success": True,
                "userID": new_user.id,
                "msg": "The user was successfully registered"}, 200


@rest_api.route('/api/users/login')
class Login(Resource):
    """
       Login user by taking 'login_model' input and return JWT token
    """

    @rest_api.expect(login_model, validate=True)
    def post(self):

        req_data = request.get_json()

        _email = req_data.get("email")
        _password = req_data.get("password")

        user_exists = Users.get_by_email(_email)

        if not user_exists:
            return {"success": False,
                    "msg": "This email does not exist."}, 400

        if not user_exists.check_password(_password):
            return {"success": False,
                    "msg": "Wrong credentials."}, 400

        # create access token uwing JWT
        token = jwt.encode({'email': _email, 'exp': datetime.utcnow() + timedelta(minutes=30)}, BaseConfig.SECRET_KEY)

        user_exists.set_jwt_auth_active(True)
        user_exists.save()

        return {"success": True,
                "token": token,
                "user": user_exists.toJSON()}, 200


@rest_api.route('/api/users/edit')
class EditUser(Resource):
    """
       Edits User's username or password or both using 'user_edit_model' input
    """

    @rest_api.expect(user_edit_model)
    @token_required
    def post(self, current_user):

        req_data = request.get_json()

        _new_username = req_data.get("username")
        _new_email = req_data.get("email")

        if _new_username:
            self.update_username(_new_username)

        if _new_email:
            self.update_email(_new_email)

        self.save()

        return {"success": True}, 200


@rest_api.route('/api/users/logout')
class LogoutUser(Resource):
    """
       Logs out User using 'logout_model' input
    """

    @token_required
    def post(self, current_user):

        _jwt_token = request.headers["authorization"]

        jwt_block = JWTTokenBlocklist(jwt_token=_jwt_token, created_at=datetime.now(timezone.utc))
        jwt_block.save()

        self.set_jwt_auth_active(False)
        self.save()

        return {"success": True}, 200

class Store:

    """
    Store dummy data for pruducts
    """

    products = {
                "0": {
                "id": 1,
                "seller_id": random.randint(200, 510),
                "Title": "LG Television",
                "Price": "$175.22",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "Logitech MK295 Wireless Mouse & Keyboard Combo with SilentTouch Technology, Full Numpad, Advanced Optical Tracking, Lag-Free Wireless, 90% Less Noise - Graphite",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "1": {
                "id": 2,
                "seller_id": random.randint(10, 305),
                "Title": "Wakie Talkie",
                "Price": "$175.22",
                "Quantity": random.randint(1, 5),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "Logitech MK295 Wireless Mouse & Keyboard Combo with SilentTouch Technology, Full Numpad, Advanced Optical Tracking, Lag-Free Wireless, 90% Less Noise - Graphite",
                "ProductCategory_id":random.randint(1, 5),
                "Ratings": random.randint(0,5)
            },
            "2": {
                "id": 3,
                "seller_id": random.randint(200, 510),
                "Title": "Satalite Dish",
                "Price": "$175.22",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "Logitech MK295 Wireless Mouse & Keyboard Combo with SilentTouch Technology, Full Numpad, Advanced Optical Tracking, Lag-Free Wireless, 90% Less Noise - Graphite",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "3": {
                "id": 4,
                "seller_id": random.randint(200, 510),
                "Title": "4KW Generator",
                "Price": "$175.22",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "Logitech MK295 Wireless Mouse & Keyboard Combo with SilentTouch Technology, Full Numpad, Advanced Optical Tracking, Lag-Free Wireless, 90% Less Noise - Graphite",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "4": {
                "id": 5,
                "seller_id": random.randint(200, 510),
                "Title": "Engineering Glooves",
                "Price": "$1.22",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "Logitech MK295 Wireless Mouse & Keyboard Combo with SilentTouch Technology, Full Numpad, Advanced Optical Tracking, Lag-Free Wireless, 90% Less Noise - Graphite",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "5": {
                "id": 6,
                "seller_id": random.randint(200, 510),
                "Title": "Wheel Chair",
                "Price": "$105.22",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "Logitech MK295 Wireless Mouse & Keyboard Combo with SilentTouch Technology, Full Numpad, Advanced Optical Tracking, Lag-Free Wireless, 90% Less Noise - Graphite",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "6": {
                "id": 7,
                "seller_id": random.randint(200, 510),
                "Title": "Lab Coat",
                "Price": "$50.22",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "Logitech MK295 Wireless Mouse & Keyboard Combo with SilentTouch Technology, Full Numpad, Advanced Optical Tracking, Lag-Free Wireless, 90% Less Noise - Graphite",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "7": {
                "id": 8,
                "seller_id": random.randint(200, 510),
                "Title": "Helmet",
                "Price": "$5.22",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "Logitech MK295 Wireless Mouse & Keyboard Combo with SilentTouch Technology, Full Numpad, Advanced Optical Tracking, Lag-Free Wireless, 90% Less Noise - Graphite",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "8": {
                "id": 9,
                "seller_id": random.randint(200, 510),
                "Title": "Samsung 32' Television",
                "Price": "$105.22",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "Logitech MK295 Wireless Mouse & Keyboard Combo with SilentTouch Technology, Full Numpad, Advanced Optical Tracking, Lag-Free Wireless, 90% Less Noise - Graphite",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "9": {
                "id": 10,
                "seller_id": random.randint(200, 510),
                "Title": "Iphone 14 Promax",
                "Price": "$1405.22",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "Logitech MK295 Wireless Mouse & Keyboard Combo with SilentTouch Technology, Full Numpad, Advanced Optical Tracking, Lag-Free Wireless, 90% Less Noise - Graphite",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "10": {
                "id": 11,
                "seller_id": random.randint(200, 510),
                "Title": "Gucci shoe",
                "Price": "$100.22",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "11": {
                "id": 12,
                "seller_id": random.randint(200, 510),
                "Title": "Diner Plates",
                "Price": "$50.22",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "12": {
                "id": 13,
                "seller_id": random.randint(200, 510),
                "Title": "Frying Pan",
                "Price": "$60.25",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
                "13": {
                "id": 14,
                "seller_id": random.randint(200, 510),
                "Title": "Jeans Shirt",
                "Price": "$15.30",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
                "14": {
                "id": 15,
                "seller_id": random.randint(200, 510),
                "Title": "Mini Skirt",
                "Price": "$80.25",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "15": {
                "id": 16,
                "seller_id": random.randint(200, 510),
                "Title": "Babe Shoe",
                "Price": "$7.25",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "16": {
                "id": 17,
                "seller_id": random.randint(200, 510),
                "Title": "Face Cap",
                "Price": "$2.15",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "17": {
                "id": 18,
                "seller_id": random.randint(200, 510),
                "Title": "Suit",
                "Price": "$120.15",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "18": {
                "id": 19,
                "seller_id": random.randint(200, 510),
                "Title": "Thinkpad IBM Laptop",
                "Price": "$120.15",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            },
            "19": {
                "id": 20,
                "seller_id": random.randint(200, 510),
                "Title": "Security Lamp",
                "Price": "$120.15",
                "Quantity": random.randint(1, 10),
                "CreatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "UpdatedAt": time.strftime("%H:%M:%S", time.localtime()),
                "Published": time.strftime("%H:%M:%S", time.localtime()),
                "Content": "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system",
                "ProductCategory_id":random.randint(1, 10),
                "Ratings": random.randint(0,5)
            }
        }