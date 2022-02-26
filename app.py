import flask
from flask import g
import os
import secrets
from flask import render_template


def create_app():
    app = flask.Flask(__name__)
    app_secret = os.getenv("FELTGOOD_SECRET")
    if app_secret == "":
        app_secret = secrets.token_urlsafe()
    app.secret_key = app_secret

    import auth, views

    app.register_blueprint(auth.bp)
    app.register_blueprint(views.bp)

    @app.template_filter("colourised")
    def colourised(s):
        import re

        s = re.sub(
            r"\/(?P<action>\w+)",
            r'<a href="/views/actions/\g<action>"><label class="label actions">\g<action></label></a>',
            s,
        )
        s = re.sub(
            r"#(?P<topic>\w+)",
            r'<a href="/views/topics/\g<topic>"><label class="label topics">\g<topic></label></a>',
            s,
        )
        s = re.sub(
            r"@(?P<contact>\w+)",
            r'<a href="/views/contacts/\g<contact>"><label class="label contacts">\g<contact></label></a>',
            s,
        )
        s = re.sub(r"\[(?P<when>\W+)\]", r"\g<when>", s)
        return s

    @app.route("/")
    @auth.login_required
    def index():
        contacts = g.user.get_contacts()
        topics = g.user.get_topics()
        interactions = g.user.get_interactions()
        upcomings = g.user.get_upcomings()
        actions = g.user.get_actions()

        context = {
            "contacts": [contact for contact in contacts],
            "topics": [topic for topic in topics],
            "interactions": interactions,
            "upcomings": upcomings,
            "actions": actions,
        }
        return render_template(
            "index.html",
            context=context,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=80, debug=True)
