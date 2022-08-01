
import os
from flask import Flask, request, jsonify, abort
import json
import sys
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES


@app.route('/')
def index():

    return 'Hello World'


'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
        short_drinks = [drink.short() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': short_drinks
        })

    except:
        abort(404)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        print(drinks)
        long_drinks = [drink.long() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': long_drinks
        })

    except:
        abort(404)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):

    try:
        body = request.get_json()
        drink_recipe = body.get('recipe')
        title = body.get('title')
        if not title or not drink_recipe:
            abort(404)

        for recipe in drink_recipe:
            color = recipe.get('color')
            name = recipe.get('name')
            parts = recipe.get('parts')
        post_drink = Drink.query.filter_by(title=title).first()
        if post_drink:
            abort(400)
        new_drink = Drink(title=title, recipe=json.dumps(drink_recipe))
        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': [new_drink.long()]
        })

    except Exception:
        abort(400)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink_by_id(payload, drink_id):
#def update_drink_by_id(drink_id):

    try:
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)

        body = request.get_json()

        drink_title = body.get('title')
        drink_recipe = body.get('recipe')

        if drink_title:
            drink.title = drink_title

        if drink_recipe:
            for recipe in drink_recipe:
                color = recipe.get('color')
                name = recipe.get('name')
                parts = recipe.get('parts')
            drink.recipe = json.dumps(drink_recipe)

        drink.update()

        long_drink = [drink.long()]

        return jsonify({
            'success': True,
            'drinks': long_drink
        })

    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink_by_id(payload, drink_id):
    try:
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id

        })

    except Exception:
        abort(422)


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


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    })


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(AuthError)
def process_AuthError(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
