from app import app, login_manager, nav_icon, google
from flask import g, redirect, url_for, session
from flask_login import logout_user, current_user, login_user
import msg
from jcfs_settings import s

# custom imports:

import admin__database as database
import account__database


#
#  LOGIN/LOGOUT
#


@login_manager.user_loader
def load_user(user_id):
    return database.read_user(user_id)


@app.before_request
def before_request():
    g.user = current_user
    g.s = s
    g.nav_icon = nav_icon
    if g.user.is_authenticated:
        g.account = account__database.read_account_byUser(g.user)
        g.display_name = g.account.s_name  # required
    else:
        g.account = None
        g.display_name = "Anonymous"  # required


@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/account/google-oauth2-callback/<est>')
@google.authorized_handler
def google_authorized(resp, est):
    if resp is None:
        msg.flash('Access denied: reason=%s error=%s' % (request.args['error_reason'], request.args['error_description']))
        return redirect(url_for('index'))
    if str(type(resp)) == "<class 'flask_oauthlib.client.OAuthException'>":
        msg.flash('Access denied: desc=%s error=%s' % (resp.data['error_description'], resp.data['error']))
        return redirect(url_for('index'))
    session['google_token'] = (resp['access_token'], '')
    person = google.get('userinfo')
    # person.data = {
    #     u'family_name': last_name,
    #     u'name': full_name,
    #     u'picture': url,
    #     u'gender': u'male' or u'female',
    #     u'email': email_addr,
    #     u'link': google_plus_url,
    #     u'given_name': first_name,
    #     u'id': u'101149719268028298009',
    #     u'hd': domain_name,
    #     u'verified_email': True  }
    session.pop('_flashes', None)
    email = person.data[u'email']
    authid = person.data[u'id']
    # picture_url = person.data[u'picture']
    if est == "new":
        user = database.create_user_byOAuth(email, authid, "google")
        if msg.is_bad(user):
            msg.flash(user)
            return redirect(url_for('index'))
        account = account__database.create_account(user, person.data[u'name'])
        if msg.is_bad(account):
            msg.flash(account)
            return redirect(url_for('index'))
        login_user(user)
        msg.flash(msg.success(
            'Welcome, your name has been determined to be <b>{}</b>'.format(account.s_name),
            return_def="index"
        ))
        return redirect(url_for('index'))
    user = database.read_user_byOAuth(email, authid, "google")
    if msg.is_bad(user):
        msg.flash(user)
        return redirect(url_for('index'))
    login_user(user)
    msg.flash(msg.success('Welcome back.', return_def="index"))
    return redirect(url_for('index'))


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')



