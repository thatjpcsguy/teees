#/usr/bin/env python2.7

from werkzeug._internal import _log
import stripe

import logging
import flask
import os

db_user = 'root'
db_pass = os.environ['TEEES_MYSQL_PW']
db_host = 'localhost'
db_db   = 'teees'
db_port = 3306


# Server settings
host = "0.0.0.0"
port = 5000

debug = os.environ['TEEES_DEV_ENVIRON'] == 'True'

if os.environ['TEEES_DEV_ENVIRON'] == 'False':
    from OpenSSL import SSL
    # SSL parameters
    context = SSL.Context(SSL.SSLv23_METHOD)
    context.use_privatekey_file(os.environ['TEEES_SSL_LOCATION'] + '/flask.pem')
    context.use_certificate_file(os.environ['TEEES_SSL_LOCATION'] + '/flask.crt')

# Flask parameters
SECRET_KEY = os.environ['TEEES_FLASK_SECRET_KEY']

# Recaptcha
app = flask.Flask(__name__, static_folder='static')
app.config.from_object(__name__)


stripe_keys = {
    'secret_key': os.environ['TEEES_STRIPE_SECRET_KEY'],
    'publishable_key': os.environ['TEEES_STRIPE_PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

@app.after_request
def after_request(response):
    return response


@app.route("/", methods=['GET'])
def index():
    return flask.render_template("index.html", stripe_key=stripe_keys['publishable_key'])


@app.route('/charge', methods=['POST'])
def charge():
    # Amount in cents
    amount = 2500

    customer = stripe.Customer.create(
        email='customer@example.com',
        card=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Teees: July Teee'
    )

    return render_template('charge.html', amount=amount)


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
    print "Main!"
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    if os.environ['TEEES_DEV_ENVIRON'] == 'False':
        app.run(host=host, port=port, ssl_context=context)
    else:
        app.run(host=host, debug=debug, port=port)



