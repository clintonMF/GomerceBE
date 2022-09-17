# -*- encoding: utf-8 -*-

"""
Copyright (c) 2022 - present ajiozi.com
"""
import pytest
import json

from api import app

"""
   Sample test data
"""

DUMMY_USERNAME = "sunny"
DUMMY_EMAIL = "sunny@ajiozi.com"
DUMMY_PASS = "newpassword" 

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_user_signup(client):
    """
       Tests /users/register API
    """
    response = client.post(
        "api/users/register",
        data=json.dumps(
            {
                "username": DUMMY_USERNAME,
                "email": DUMMY_EMAIL,
                "password": DUMMY_PASS
            }
        ),
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert "The user was successfully registered" in data["msg"]


def test_user_signup_invalid_data(client):
    """
       Tests /users/register API: invalid data like email field empty
    """
    response = client.post(
        "api/users/register",
        data=json.dumps(
            {
                "username": DUMMY_USERNAME,
                "email": "",
                "password": DUMMY_PASS
            }
        ),
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert "'' is too short" in data["msg"]


def test_user_login_correct(client):
    """
       Tests /users/signup API: Correct credentials
    """
    response = client.post(
        "api/users/login",
        data=json.dumps(
            {
                "email": DUMMY_EMAIL,
                "password": DUMMY_PASS
            }
        ),
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert data["token"] != ""


def test_user_login_error(client):
    """
       Tests /users/signup API: Wrong credentials
    """
    response = client.post(
        "api/users/login",
        data=json.dumps(
            {
                "email": DUMMY_EMAIL,
                "password": DUMMY_EMAIL
            }
        ),
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert "Wrong credentials." in data["msg"]

def test_all_products_bad_request(client):
    """
        Tests /products API: Product request could not processed 
    """
    response = client.get('/products')
    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert response.success == True
       
       
def test_all_products_no_product(client):
    """
        Tests /products API: No product found 
    """
    response = client.get('/products')
    data = json.loads(response.data.decode())
    assert response.data.length == 0
    assert response.status_code == 204 
    assert response.success == True
    
def test_paginate_products(client):
    response = client.get('/products')
    data = json.loads(response.data.decode())
    
    assert response.data.length == 0
    assert response.status_code == 200 
    assert response.success == True
    assert response.data
    

def test_404_invalid_page_numbers(client):
    response = client.get('/products?page=10000')
    data = json.loads(response.data.decode())
    
    assert response.data.length == 0
    assert response.status_code == 422 
    assert response.success == False
    assert response.data
    
