from app import app, bcrypt, qrcode
from flask import Flask, request, g, redirect, url_for, \
    render_template, Markup, send_file

import msg
import admin_database as database
from jcfs_settings import s


#
#  LOGIN/LOGOUT
#


# TBD TBD TBD: the "generic default version" of this need to made.

@login_manager.user_loader
def load_user(user_id):
    return database.read_user(user_id)


@app.before_request
def before_request():
    g.user = current_user
    g.s = s



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        this_user = database.check_login(request.form, bcrypt)
        if msg.is_good(this_user):
            login_user(this_user)
            msg.flash('Welcome, {}'.format(this_user.s_name))
            return redirect(url_for('index'))
        else:
            msg.flash(this_user)
            return redirect(url_for('login'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# @app.route('/new-player-form', methods=['GET', 'POST'])

# @login_required
# @app.route('/player-settings', methods=['GET', 'POST'])


# {{{--INSERT-MARKER--}}}


# eof
