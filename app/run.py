# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, Markup
from flask_restplus import Api, Resource
from libs.sqlite import SQLService
from pybadges import badge as badgeGen


import sys
import logging
logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)-5s: %(message)s")


app = Flask(__name__)
api = Api(app)

init = SQLService()
init.createTable()
del init


@api.route("/")
class CreateBadge(Resource):

    def post(self):
        """
        Creates a new Badge ID in the DB
        """
        badge = SQLService()
        badge.generateBadge()

        getUrl = "%s%s" % (request.url_root,
                           badge.badgeId)
        putUrl = "%s%s?token=%s" % (request.url_root,
                                    badge.badgeId,
                                    badge.token)
        return {"get_url": getUrl, "put_url": putUrl}, 200


@api.route("/<int:id>")
class UseBadge(Resource):

    @api.doc(params={'id': 'An ID'})
    def get(self, id):
        """
        Returns the Badge with the given ID
        """
        badge = SQLService()
        badge.getBadge()
        svg = badgeGen(left_text=badge.name,
                       right_text=badge.value,
                       left_color=badge.name_color,
                       right_color=badge.value_color)

        return render_template("svg.jinja", svg=Markup(svg))

    @api.doc(params={'id': 'An ID', "token": "Access token"})
    @api.doc(responses={403: 'Not Authorized'})
    def put(self, id, token, name, value, ncolor, vcolor):
        """
        Changes the Badge on the ID with Token
        """
        token = request.form['token']if "token" in request.form else None
        name = request.form['name'] if "name" in request.form else None
        value = request.form['value'] if "value" in request.form else None
        ncolor = request.form['ncolor'] if "ncolor" in request.form else None
        vcolor = request.form['vcolor'] if "vcolor" in request.form else None

        badge = SQLService(id, token)
        if not badge.getBadge():
            api.abort(403)
        badge.updateBadge(name, value, ncolor, vcolor)
        return {}


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)
