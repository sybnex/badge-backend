# -*- coding: utf-8 -*-

from flask import Flask, request, Response
from flask_restplus import Api, Resource
from libs.sqlite import SQLService
from pybadges import badge as badge


import sys
import logging
logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)-5s: %(message)s")


app = Flask(__name__)
api = Api(app, version="1.0", title="Badgeservice API")

init = SQLService()
init.createTable()
del init


@api.route("/")
class CreateBadge(Resource):

    def post(self):
        """
        Creates a new Badge ID in the DB
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
    @api.representation('text/xml')
    def get(self, id):
        """
        Returns the Badge with the given ID
        """
        badgen = SQLService(id)
        if not badgen.getBadge():
            api.abort(404)
        logging.info("ID: %s, Name: %s, Val: %s" % (badgen.badgeId,
                                                    badgen.name,
                                                    badgen.value))
        svg = badge(left_text=badgen.name,
                    right_text=badgen.value,
                    left_color=badgen.name_color,
                    right_color=badgen.value_color)

        # return render_template("svg.jinja", svg=Markup(svg))
        return Response(svg, mimetype='text/xml')

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
        token = request.args.get("token")
        badgen = SQLService(id, token)

        if not badgen.validateToken():
            logging.error("Could not validate token!")
            api.abort(403)

        badgen.name = request.args.get("name")
        badgen.value = request.args.get("value")
        badgen.ncolor = request.args.get("ncolor")
        badgen.vcolor = request.args.get("vcolor")
        logging.info("Changing: ID: %s, Name: %s, Val: %s" % (badgen.badgeId,
                                                              badgen.name,
                                                              badgen.value))

        badgen.updateBadge()
        return {}


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, debug=True)
