from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import jsonify
from flask import url_for
from flask import flash
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Pokemon, PokemonUser
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import httplib2
import json
import requests

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///pokemonusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login')
def login():
    # create a state token to prevent request forgery
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    # store it in session for later use
    login_session['state'] = state
    return render_template('login.html', STATE = state)

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# Disconnect based on provider
@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        return redirect(url_for('showTrainers'))
    else:
        return redirect(url_for('showTrainers'))


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

#JSON API to view Pokemon User
@app.route('/trainers/<int:user_id>/pokemon/JSON')
def pokemonuserJSON(user_id):
    trainer = session.query(User).filter_by(id=user_id).one()
    pokemonuser = session.query(PokemonUser).filter_by(user_id=user_id).all()
    pokemon=[]
    for value in pokemonuser:
        pokemon += session.query(Pokemon).filter_by(id=value.pokemon_id).all()
    return jsonify(pokemons = [i.serialize for i in pokemon])

@app.route('/trainers/JSON')
def trainersJSON():
    trainer = session.query(User).order_by(asc(User.name))
    return jsonify(trainers = [i.serialize for i in trainer])

#Show all Users
@app.route('/')
@app.route('/trainers')
def showTrainers():
    trainer = session.query(User).order_by(asc(User.name))
    return render_template('user.html', trainers = trainer)

#Edit User Profile
@app.route('/trainers/<int:user_id>/editProfile', methods=['GET', 'POST'])
def editProfile(user_id):
    trainer = session.query(User).filter_by(id=user_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if trainer.id != login_session['user_id']:
        flash("Not an Authorized User")
        return redirect(url_for('showTrainers'))
    if request.method == 'POST':
        if request.form['name']:
            trainer.name = request.form['name']
            trainer.email = request.form['email']
            trainer.hometown = request.form['hometown']
            flash("Successfully Updated!")
            return redirect(url_for('showTrainers'))
    else:
        return render_template('editProfile.html', trainers=trainer)

#Delete Pokemon From Database
@app.route('/trainers/delete', methods=['GET', 'POST'])
def deletePokemon():
    pokemons = session.query(Pokemon)
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        name = request.form['name']
        pokemon = session.query(Pokemon).filter_by(name=name).one()
        session.delete(pokemon)
        session.commit()
        flash("Pokemon Removed Successfully!")
        return redirect(url_for('showTrainers'))
    else:
        return render_template('deletePokemon.html', pokemons=pokemons)

#Add Pokemon to Database
@app.route('/trainers/add', methods=['GET','POST'])
def addPokemon():
    pokemons = session.query(Pokemon).all()
    if 'username' not in login_session:
        return redirect('/login')
    pokemoname = []
    for pokemon in pokemons:
        pokemoname.append((pokemon.name).upper())
    if request.method == 'POST':
        name = request.form['name']
        if name.upper() not in pokemoname:
            newPokemon = Pokemon(name=name)
            session.add(newPokemon)
            session.commit()
        else:
            flash('Pokemon Already Exists!')
        flash("Pokemon Added Successfully!")
        return redirect(url_for('showTrainers'))
    else:
        return render_template('addPokemon.html')

#Shows the list of Pokemons User have
@app.route('/trainers/<int:user_id>/pokemon')
def pokemonDetails(user_id):
    trainer = session.query(User).filter_by(id=user_id).one()
    pokemonuser = session.query(PokemonUser).filter_by(user_id=user_id).all()
    #pokemon = session.query(Pokemon).filter_by(id=.pokemon_id).all()
    pokemon = []
    if 'username' not in login_session:
        return redirect('/login')
    for value in pokemonuser:
        pokemon += session.query(Pokemon).filter_by(id=value.pokemon_id).all()
    return render_template('pokemon.html', trainers=trainer, pokemons=pokemon)

#Add pokemon associate to User
@app.route('/trainers/<int:user_id>/addpokemonuser', methods=['GET','POST'])
def addPokemonUser(user_id):
    trainer = session.query(User).filter_by(id=user_id).one()
    pokemons = session.query(Pokemon).all()
    pokemonuser = session.query(PokemonUser).filter_by(user_id=user_id).all()
    pokemonid = []
    if 'username' not in login_session:
        return redirect('/login')
    if trainer.id != login_session['user_id']:
        flash("Not an Authorized User to Add the Pokemon")
        return redirect(url_for('showTrainers'))
    for pokemon in pokemonuser:
        pokemonid.append(pokemon.pokemon_id)
    if request.method == 'POST':
        name = request.form['name']
        pokemon = session.query(Pokemon).filter_by(name=name).one()
        if pokemon.id not in pokemonid:
            newPokemon = PokemonUser(user_id=user_id, pokemon_id=pokemon.id)
            session.add(newPokemon)
            session.commit()
        flash("Pokemon Added Successfully!")
        return redirect(url_for('showTrainers'))
    else:
        return render_template('addPokemonUser.html',trainers=trainer, pokemons=pokemons)

#Delete Pokemon associated to User
@app.route('/trainers/<int:user_id>/<int:pokemon_id>/pokemon/deletepokemonuser', methods=['GET','POST'])
def deletePokemonUser(user_id,pokemon_id):
    pokemon = session.query(Pokemon).filter_by(id=pokemon_id).one()
    pokemonuser = session.query(PokemonUser).filter_by(user_id=user_id, pokemon_id=pokemon_id).one()
    trainer = session.query(User).filter_by(id=pokemonuser.user_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if trainer.id != login_session['user_id']:
        flash("Not an Authorized User to Delete the Pokemon")
        return redirect(url_for('showTrainers'))
    if request.method == 'POST':
        session.delete(pokemonuser)
        session.commit()
        flash("Pokemon Deleted Successfully!")
        return redirect(url_for('showTrainers'))
    else:
        return render_template('deletePokemonUser.html',trainers=trainer, pokemons=pokemon)

if __name__ =='__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)

