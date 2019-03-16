from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Data_Setup import Base,PilgrimageName,StateName, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
import datetime

engine = create_engine('sqlite:///pilgrimages.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "Pilgrimages"

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Create anti-forgery state token
gvs_sa = session.query(PilgrimageName).all()


# login
@app.route('/login')
def showLogin():
    
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    gvs_sa = session.query(PilgrimageName).all()
    vi = session.query(StateName).all()
    return render_template('login.html',
                           STATE=state, gvs_sa=gvs_sa, vi=vi)
    # return render_template('myhome.html', STATE=state
    # gvs_sa=gvs_sa,vi=vi)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
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
    output += ' " style = "width: 300px; height: 300px; border-radius: 150px;'
    '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# User Helper Functions
def createUser(login_session):
    User1 = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(User1)
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
    except Exception as error:
        print(error)
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session

#completed
# Home
@app.route('/')
@app.route('/home')
def home():
    gvs_sa = session.query(PilgrimageName).all()
    return render_template('myhome.html', gvs_sa=gvs_sa)

#####completed
# Pilgrimage Hub for admins
@app.route('/PilgrimageHub')
def PilgrimageHub():
    try:
        if login_session['username']:
            name = login_session['username']
            gvs_sa = session.query(PilgrimageName).all()
            san = session.query(PilgrimageName).all()
            vi = session.query(StateName).all()
            return render_template('myhome.html', gvs_sa=gvs_sa,
                                   san=san, vi=vi, uname=name)
    except:
        return redirect(url_for('showLogin'))

######completed
# Showing pilgrimages based on pilgrimage category
@app.route('/PilgrimageHub/<int:g4id>/AllPilgrimages')
def showPilgrimages(g4id):
    gvs_sa = session.query(PilgrimageName).all()
    san = session.query(PilgrimageName).filter_by(id=g4id).one()
    vi = session.query(StateName).filter_by(pilgrimagenameid=g4id).all()
    try:
        if login_session['username']:
            return render_template('showPilgrimages.html', gvs_sa=gvs_sa,
                                   san=san, vi=vi,
                                   uname=login_session['username'])
    except:
        return render_template('showPilgrimages.html',
                               gvs_sa=gvs_sa, san=san, vi=vi)

#####completed
# Add New Pilgrimage
@app.route('/PilgrimageHub/addPilgrimageName', methods=['POST', 'GET'])
def addPilgrimageName():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        pilgrimagename = PilgrimageName(name=request.form['name'],
                           user_id=login_session['user_id'])
        session.add(pilgrimagename)
        session.commit()
        return redirect(url_for('PilgrimageHub'))
    else:
        return render_template('addPilgrimageName.html', gvs_sa=gvs_sa)

########completed
# Edit Pilgrimage Name
@app.route('/PilgrimageHub/<int:g4id>/edit', methods=['POST', 'GET'])
def editPilgrimageName(g4id):
    if 'username' not in login_session:
        return redirect('/login')
    editPilgrimageName = session.query(PilgrimageName).filter_by(id=g4id).one()
    creator = getUserInfo(editPilgrimageName.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this Pilgrimage Name."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('PilgrimageHub'))
    if request.method == "POST":
        if request.form['name']:
            editPilgrimageName.name = request.form['name']
        session.add(editPilgrimageName)
        session.commit()
        flash("Pilgrimage Name Edited Successfully")
        return redirect(url_for('PilgrimageHub'))
    else:
        # gvs_sa is global variable we can them in entire application
        return render_template('editPilgrimageName.html',
                               dsa=editPilgrimageName, gvs_sa=gvs_sa)

######completed
# Delete PilgrimageName
@app.route('/PilgrimageHub/<int:g4id>/delete', methods=['POST', 'GET'])
def deletePilgrimageName(g4id):
    if 'username' not in login_session:
        return redirect('/login')
    dsa = session.query(PilgrimageName).filter_by(id=g4id).one()
    creator = getUserInfo(dsa.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot Delete this Pilgrimage Name."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('PilgrimageHub'))
    if request.method == "POST":
        session.delete(dsa)
        session.commit()
        flash("Pilgrimage Name Deleted Successfully")
        return redirect(url_for('PilgrimageHub'))
    else:
        return render_template('deletePilgrimageName.html', dsa=dsa, gvs_sa=gvs_sa)

######completed
# Add New Pilgrimage Name Details
@app.route('/PilgrimageHub/addPilgrimageName/addPilgrimageStateDetails/<string:osname>/add',
           methods=['GET', 'POST'])
def addPilgrimageDetails(osname):
    if 'username' not in login_session:
        return redirect('/login')
    san = session.query(PilgrimageName).filter_by(name=osname).one()
    # See if the logged in user is not the owner of pilgrimage
    creator = getUserInfo(san.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't add new Pilgrimage state"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showPilgrimages', g4id=san.id))
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        god = request.form['god']
        area = request.form['area']
        statedetails = StateName(name=name, address=address,
                              god=god,
                              area=area,
                              date=datetime.datetime.now(),
                              pilgrimagenameid=san.id,
                              user_id=login_session['user_id'])
        session.add(statedetails)
        session.commit()
        return redirect(url_for('showPilgrimages', g4id=san.id))
    else:
        return render_template('addPilgrimageStateDetails.html',
                               osname=san.name, gvs_sa=gvs_sa)

######completed
# Edit State details
@app.route('/PilgrimageHub/<int:g4id>/<string:luename>/edit',
           methods=['GET', 'POST'])
def editPilgrimageState(g4id, luename):
    if 'username' not in login_session:
        return redirect('/login')
    dsa = session.query(PilgrimageName).filter_by(id=g4id).one()
    statedetails = session.query(StateName).filter_by(name=luename).one()
    # See if the logged in user is not the owner of Pilgrimage
    creator = getUserInfo(dsa.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't edit this pilgrimage state"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showPilgrimages', g4id=dsa.id))
    # POST methods
    if request.method == 'POST':
        statedetails.name = request.form['name']
        statedetails.address = request.form['address']
        statedetails.god = request.form['god']
        statedetails.area = request.form['area']
        statedetails.date = datetime.datetime.now()
        session.add(statedetails)
        session.commit()
        flash("State Edited Successfully")
        return redirect(url_for('showPilgrimages', g4id=g4id))
    else:
        return render_template('editPilgrimageState.html',
                               g4id=g4id, statedetails=statedetails, gvs_sa=gvs_sa)

#####completed
# Delte states in pilgrimages
@app.route('/PilgrimageHub/<int:g4id>/<string:luename>/delete',
           methods=['GET', 'POST'])
def deletePilgrimageState(g4id, luename):
    if 'username' not in login_session:
        return redirect('/login')
    dsa = session.query(PilgrimageName).filter_by(id=g4id).one()
    statedetails = session.query(StateName).filter_by(name=luename).one()
    # See if the logged in user is not the owner of item
    creator = getUserInfo(dsa.user_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You can't delete this state"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showPilgrimages', g4id=dsa.id))
    if request.method == "POST":
        session.delete(statedetails)
        session.commit()
        flash("Deleted state Successfully")
        return redirect(url_for('showPilgrimages', g4id=g4id))
    else:
        return render_template('deletePilgrimageState.html',
                               g4id=g4id, statedetails=statedetails, gvs_sa=gvs_sa)

####
# Logout from current user
@app.route('/logout')
def logout():
    access_token = login_session['access_token']
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    if access_token is None:
        print ('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected....'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type': 'application/x-www-form-urlencoded'})[0]

    print (result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected user..'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successful logged out")
        return redirect(url_for('showLogin'))
        # return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

#####completed
# Json
@app.route('/PilgrimageHub/JSON')
def allPilgrimagesJSON():
    pilgrimagenames = session.query(PilgrimageName).all()
    category_dict = [c.serialize for c in pilgrimagenames]
    for c in range(len(category_dict)):
        pilgrimages = [i.serialize for i in session.query(
                 StateName).filter_by(pilgrimagenameid=category_dict[c]["id"]).all()]
        if pilgrimages:
            category_dict[c]["pilgrimages"] = pilgrimages
    return jsonify(PilgrimageName=category_dict)

####completed
@app.route('/PilgrimageHub/pilgrimageName/JSON')
def categoriesJSON():
    pilgrimages = session.query(PilgrimageName).all()
    return jsonify(pilgrimageName=[c.serialize for c in pilgrimages])

####completed
@app.route('/PilgrimageHub/pilgrimages/JSON')
def statesJSON():
    states = session.query(StateName).all()
    return jsonify(pilgrimages=[i.serialize for i in states])

#####completed
@app.route('/PilgrimageHub/<path:pilgrimage_name>/pilgrimages/JSON')
def categoryStatesJSON(pilgrimage_name):
    pilgrimageName = session.query(PilgrimageName).filter_by(name=pilgrimage_name).one()
    pilgrimages = session.query(StateName).filter_by(pilgrimagename=pilgrimageName).all()
    return jsonify(pilgrimageName=[i.serialize for i in pilgrimages])

#####completed
@app.route('/PilgrimageHub/<path:pilgrimage_name>/<path:pilgrimagestate_name>/JSON')
def StateJSON(pilgrimage_name, pilgrimagestate_name):
    pilgrimageName = session.query(PilgrimageName).filter_by(name=pilgrimage_name).one()
    pilgrimageStateName = session.query(StateName).filter_by(
           name=pilgrimagestate_name, pilgrimagename=pilgrimageName).one()
    return jsonify(pilgrimageStateName=[pilgrimageStateName.serialize])

if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=8000)
