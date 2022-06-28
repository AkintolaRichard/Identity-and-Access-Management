import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks():
    allDrinks = Drink.query.all()
    drinks = [drink.short() for drink in allDrinks]
    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    allDrinks = Drink.query.all()
    drinks = [drink.long() for drink in allDrinks]
    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    recipeString = str(recipe)
    recipeString = recipeString.replace("\'", "\"")
    thedrink = Drink(
        title=title,
        recipe=recipeString
    )
    thedrink.insert()
    drink = thedrink.long()
    return jsonify({
        'success': True,
        'drinks': drink
    })

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):
    body = request.get_json()
    title = body.get('title', None)
    thedrink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    error = False
    if title != None:
        thedrink.title = title
    try:
        thedrink.update()
    except Exception as e:
        error = True
    if error:
        abort(400)
    else:
        drink = [thedrink.long()]
        return jsonify({
            'success': True,
            'drinks': drink
        })

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    drink.delete()
    return jsonify({
        'success': True,
        'delete': drink_id
    })

# Error Handling
'''
Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def notfound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "not found"
    }), 404


@app.errorhandler(AuthError)
def notauthenticated(error):
    return jsonify({
        "success": False,
        "error": error.code,
        "message": "Authentication Error"
    }), error.code

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401

@app.errorhandler(500)
def servererror(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "server error"
    }), 500

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403
