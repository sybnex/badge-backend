# -*- coding: utf-8 -*-

from flask import Flask, jsonify, render_template, request
from flask_restplus import Api, Resource
from libs.sqlite import NotizService


import sys
import logging
import time
logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)-5s: %(message)s")


flask_app = Flask(__name__)
app = Api(app = flask_app)
name_space = app.namespace('main', description='Main APIs')

init = SQLService()
init.createTable()
del init

@name_space.route("/")
class MainClass(Resource):
	def get(self):
		return {
			"status": "Got new data"
		}
	def post(self):
		return {
			"status": "Posted new data"
		}


def request_wants_json():
    best = request.accept_mimetypes.best_match(['application/json',
                                                'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


@app.route('/', methods=['GET'])
def index():
    hugo = NotizService()
    anzahl = hugo.countMessage()
    url = "%s" % (request.url_root)
    return render_template('index.jinja', anzahl=anzahl, url=url)


@app.route('/', methods=['POST'])
def save():
    hugo = NotizService()
    identity = request.form['id'] if "id" in request.form else None
    data = request.form['note']
    if request_wants_json():
        if identity:
            if len(identity) <= 8:
                hugo.hashval = identity
                if hugo.checkDupId():
                    msg = "Diese ID existiert bereits."
                    return jsonify({"error": True, "message": msg}), 406
            else:
                msg = "ID darf max. 8 Zeichen lang sein."
                return jsonify({"error": True, "message": msg}), 400
    if len(data) > 0:
        hugo.generateId()
        hugo.saveMessage(data)
        url = "%s%s" % (request.url_root, hugo.hashval)
        if request_wants_json():
            return jsonify({"url": url})
        else:
            return render_template('save.jinja', url=url)
    else:
        if request_wants_json():
            msg = "Sie haben keine Nachricht eingegeben."
            return jsonify({"error": True, "message": msg}), 400
        else:
            msg = "Sie haben keine Nachricht eingegeben."
            return render_template('error.jinja', text=msg,
                                   code=400, error=True)


@app.route('/<pk_id>', methods=['GET'])
def show(pk_id=None):
    hugo = NotizService()
    data = hugo.readMessage(pk_id)
    if pk_id and data:
        if request_wants_json():
            return jsonify({"date": data[1], "data": data[2]})
        else:
            return render_template('show.jinja', data=data)
    else:
        if request_wants_json():
            msg = "Es existiert keine Nachricht unter dieser ID."
            return jsonify({"error": True, "message": msg}), 400
        else:
            msg = "Es existiert keine Nachricht unter dieser ID."
            return render_template('error.jinja', text=msg)


@app.route('/all', methods=['GET'])
def all():
    hugo = NotizService()
    messages = hugo.readAllMessages()
    if messages:
        return render_template('all.jinja', messages=messages)
    else:
        return render_template('error.jinja',
                               text="Es existieren keine Nachrichten.")


@app.route('/deleteNote/<pk_id>')
def delete(pk_id=None):
    hugo = NotizService()
    if pk_id is None:
        if request_wants_json():
            msg = "Bitte ID mitschicken."
            return jsonify({"error": True, "message": msg}), 406
        else:
            msg = "Bitte ID mitschicken."
            return render_template('error.jinja', text=msg,
                                   code=400, error=True)
    else:
        hugo.deleteMessage(pk_id)
        if request_wants_json():
            return jsonify({"delete": True,
                            "message": "Ihre Nachricht wurde geloescht"})
        else:
            return render_template('delete.jinja',
                                   text="Ihre Nachricht wurde gelöscht.")


@app.route('/<seconds>', methods=['GET'])
def wait(seconds=5):
    try:
        time.sleep(int(seconds))
    except ValueError:
        text = "Ungültiger Wert mitgegeben!"
    else:
        text = "Ich habe % s Sekunden geschlafen." % seconds

    return render_template('error.jinja', text=text)


if __name__ == '__main__':
    # init = NotizService()
    # init.createTable()
    # del init
    app.run(host='0.0.0.0', threaded=True, debug=True)
