# -*- coding: utf-8 -*-

from flask import Flask, request, Response, url_for
from flask_restplus import Api, Resource
from libs.sqlite import SQLService
from pybadges import badge as badge


import sys
import logging
logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)-5s: %(message)s")


class MyApi(Api):
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        scheme = 'http' if '5000' in self.base_url else 'https'
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)


app = Flask(__name__)
api = MyApi(app, version="1.0", title="Badgeservice API",
            description="A simple API")

init = SQLService()
init.createTable()
del init


@api.route("/")
class CreateBadge(Resource):

    def post(self):
        """
        Creates a new Badge ID in the DB with default values
        """
        badgen = SQLService()
        badgen.generateBadge()
        badgen.updateBadge()
        getUrl = "%s%s" % (request.url_root,
                           badgen.badgeId)
        putUrl = "%s%s?token=%s" % (request.url_root,
                                    badgen.badgeId,
                                    badgen.token)
        return {"get_url": getUrl, "put_url": putUrl}, 200


@api.route("/<id>")
class UseBadge(Resource):

    @api.doc(params={"id": "Badge ID"})
    @api.doc(responses={200: "Success",
                        404: "Not Found"})
    @api.representation('image/svg+xml')
    def get(self, id):
        """
        Returns the Badge with the given ID
        """
        badgen = SQLService(id)
        logging.info("Get badge with ID: %s" % badgen.badgeId)
        if not badgen.getBadge():
            api.abort(404)

        svg = badge(left_text=badgen.name,
                    right_text=badgen.value,
                    left_color=badgen.name_color,
                    right_color=badgen.value_color)

        return Response(svg, mimetype='image/svg+xml')

    @api.doc(params={"id": 'Badge ID',
                     "token": "Access token",
                     "name": "Left name for Badge",
                     "value": "Right name for Badge",
                     "ncolor": "Color of name",
                     "vcolor": "Color of value"})
    @api.doc(responses={200: "Success",
                        403: "Not Authorized"})
    def put(self, id):
        """
        Changes the Badge on the ID with Token
        """
        logging.info("Change badge with ID: %s" % id)
        token = request.args.get("token")
        badgen = SQLService(id, token)

        if not badgen.validateToken():
            logging.error("Could not validate token!")
            api.abort(403)

        badgen.name = request.args.get("name")
        badgen.value = request.args.get("value")
        badgen.name_color = request.args.get("ncolor")
        badgen.value_color = request.args.get("vcolor")

        badgen.updateBadge()
        return {}


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)
