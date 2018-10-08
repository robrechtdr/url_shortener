import os
import uuid

from flask import (Flask, request, jsonify, make_response, redirect, 
                   abort, send_from_directory)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

from flask import send_from_directory


HASH_LEN = 8
LOADERIO_DIR = "loaderio"


app = Flask(__name__)


# Credential details would normally be read via environment vars or a file 
# not added to the git index .
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://me:pw@localhost/mydb'
db = SQLAlchemy(app)


# For multiple models would place in a models.py file
class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash_ = db.Column(db.String(HASH_LEN), unique=True, nullable=False)
    url = db.Column(db.String(64), unique=True, nullable=False)

    @property
    def shortened_url(self):
        # https://stackoverflow.com/questions/35616434/how-can-i-get-the-base-of-a-url-in-python
        base_url = os.path.dirname(self.url)
        return os.path.join(base_url, self.hash_)

    def __repr__(self):
        return '<Url {0}>'.format(self.shortened_url)


#db.drop_all()
# Idempotent
db.create_all()


# For stress testing via loaderio
@app.route("/loaderio-bb0e1b56753b9545a4b973bf46647a45.txt")
def serve_loaderio_file():
    return send_from_directory(LOADERIO_DIR, "loaderio.txt")


@app.route("/loaderio-req-vars.json")
def serve_loaderio_req_vars_file():
    return send_from_directory(LOADERIO_DIR, "loaderio_req_vars.json")


@app.route("/shorten_url", methods=['POST'])
def shorten_url():
    if not request.json:
        abort(400, "Please specify json in the Content-Type header.")
    else:
        url = request.json.get("url")
        if not url:
            abort(400, "Please specify a 'url' attribute.")

    created = False
    url_ = Url.query.filter_by(url=url).first()
    if not url_:
        created = True
        saved = False
        while not saved:
            hash_ = uuid.uuid4().hex[:HASH_LEN]
            url_ = Url(url=url, hash_=hash_)
            db.session.add(url_)
            try:
                db.session.commit()
                saved = True
            # If we happen to get the same hash for a diff url
            # (as hash is shortened version).
            except exc.IntegrityError as error:
                db.session.rollback()

    body = {"shortened_url" : url_.shortened_url}
    if created: 
        return make_response(jsonify(body), 201)
    else:
        return make_response(jsonify(body), 200)


@app.route("/<hash_>", methods=['GET'])
def show_original_url(hash_):
    if len(hash_) == HASH_LEN:
        # SQL-injection safe as we are not using Session.execute.
        url_ = Url.query.filter_by(hash_=hash_).first()
        if url_:
            # Else the url gets simply appended to the internal base url.
            if not "http://" in url_.url:
                url = "http://{0}".format(url_.url)
            else:
                url = url_.url
            return redirect(url)
        else:
            abort(400, "Url not found. Create a shortened url first.")

    abort(400)


if __name__ == '__main__':
    app.run(threaded=True)
