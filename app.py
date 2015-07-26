#/usr/bin/env python2.7
# from OpenSSL import SSL
from werkzeug._internal import _log

import logging
import flask
import db
import os
import forms


# Server settings
host = "0.0.0.0"
port = 5000

debug = True
db.engine.echo = True

if os.environ['DEV_ENVIRON'] == 'False':
    # SSL parameters
    context = SSL.Context(SSL.SSLv23_METHOD)
    context.use_privatekey_file('ssl/flask.pem')
    context.use_certificate_file('ssl/flask.crt')

# Flask parameters
SECRET_KEY = os.environ['FLASK_SECRET_KEY']

# Recaptcha
app = flask.Flask(__name__, static_folder='static')
app.config.from_object(__name__)


@app.after_request
def after_request(response):
    response.headers.add('Content-Security-Policy', "default-src 'self'; frame-src 'none'; object-src 'none'; reflected-xss 'block'")
    response.headers.add('X-Permitted-Cross-Domain-Policies', 'master-only')
    response.headers.add('X-XSS-Protection', '1; mode=block')
    response.headers.add('X-Frame-Options', 'SAMEORIGIN')
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.headers.add('Pragma', 'no-cache')
    response.headers.add('Expires', '-1')
    return response


@app.route("/", methods=['GET'])
def index():
    return flask.render_template("index.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    try:
        if flask.session['logged_in']:
            return flask.redirect('/')
    except KeyError as KE:
        pass

    error = None
    form = forms.LoginForm()
    if flask.request.method == 'POST' and form.validate_on_submit():
        user_agent = db.clean(str(flask.request.user_agent))
        username = db.clean(form.username.data)
        password = db.clean(form.password.data)
        ip = flask.request.remote_addr

        if db.login(username, password):
            db.security_log(username, ip, user_agent, action_type='auth_success')
            flask.session['logged_in'] = True
            flask.session['username'] = username
            return flask.redirect('/')
        else:
            db.security_log(username, ip, user_agent, action_type='auth_failure')
            error = "Invalid username/password!"

    elif form.csrf_token.errors:
        db.security_log(username, ip, user_agent, action_type='csrf')
        flask.abort(403)

        return flask.redirect('/')

    return flask.render_template("login.html", form=form, error=error)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    try:
        if flask.session['logged_in']:
            return flask.redirect('/')
    except KeyError as KE:
        pass

    errors = None
    form = forms.RegistrationForm()
    if flask.request.method == 'POST':
        if form.validate_on_submit():
            user_agent = db.clean(str(flask.request.user_agent))
            username = db.clean(form.username.data)
            password = db.clean(form.password.data)
            email = db.clean(form.email.data)
            ip = flask.request.remote_addr

            if not db.user_exists(username):
                if db.create_user(username, password, email):
                    db.security_log(username, ip, user_agent, action_type='account_create')
            else:
                _log('warning', "User: %s already exists, cannot create user" % username)
                error = "Sorry, but that username is taken!"

        else:
            _log('critical', 'One or more form elements did not pass validation! Errors: %s' % str(form.errors))
            errors = str(form.errors)

    return flask.render_template("signup.html", form=form, error=errors)


@app.route('/logout')
def logout():
    try:
        if not flask.session['logged_in']:
            return flask.redirect('/')
    except KeyError as KE:
        pass

    user_agent = db.clean(str(flask.request.user_agent))
    username = flask.session['username']
    ip = flask.request.remote_addr

    db.security_log(username, ip, user_agent, action_type='auth_logout')
    flask.session.pop('logged_in', None)
    return flask.redirect('/')


@app.route('/robots.txt')
@app.route('/humans.txt')
def serve_static():
    return flask.send_from_directory(app.static_folder, flask.request.path[1:])


@app.errorhandler(403)
def forbidden(error):
    return flask.render_template("403.html")


@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template("404.html")


if __name__ == "__main__":
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    if os.environ['DEV_ENVIRON'] == 'False':
        app.run(host=host, port=port, ssl_context=context)
    else:
        app.run(host=host, debug=debug, port=port)



