import os
import uuid

from flask import Flask, request, jsonify, make_response, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc


HASH_LEN = 8


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///url_shortener.db'
db = SQLAlchemy(app)


# For multiple models Would place in a models.py file
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

# Idempotent
db.create_all()


# WHAT IF GET REQUEST? V (auto resp 405 from Flask; method not allowed response builtin from Flask)
# !! POST req: WHAT IF SOMETHING WRONG WITH JSON V
# !! POST req: What if non-json V
@app.route("/shorten_url", methods=['POST'])
def shorten_url():
    if not request.json:
        abort(400, "Please specify json in the Content-Type header.")
    else:
        url = request.json.get("url")
        if not url:
            abort(400, "Please specify a 'url' attribute.")
     
    url_ = Url.query.filter_by(url=url).first()
    while not url_:
        hash_ = uuid.uuid4().hex[:HASH_LEN]
        url_ = Url(url=url, hash_=hash_)
        db.session.add(url_)
        try:
            db.session.commit()
        # If we happen to get the same hash for a diff url
        # (as hash is shortened version).
        except exc.IntegrityError as error:
            session.rollback()
            url_ = None

    body = {"shortened_url" : url_.shortened_url}
    return make_response(jsonify(body), 201)


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
            return abort(400, "Url not found. Create a shortened url first.")

    abort(400)


if __name__ == '__main__':
    app.run()

