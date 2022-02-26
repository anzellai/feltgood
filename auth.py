import functools
from flask import (
    Blueprint,
    flash,
    g,
    session,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
)

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.route("/me", methods=("GET",))
def me():
    import models
    return jsonify([p.json for p in models.Person.nodes])


@bp.before_app_request
def load_logged_in_user():
    import models
    name = session.get("user")
    if name is None:
        g.user = None
    else:
        g.user = models.Person.nodes.get_or_none(name=name)


@bp.route("/register", methods=("GET", "POST"))
def register():
    import models
    if request.method == "POST":
        name = request.form["name"]
        error = None

        if not name:
            error = "Name is required."

        if error is None:
            try:
                models.Person(**request.form).save()
            except:
                error = f"User {name} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    import models
    if request.method == "POST":
        name = request.form["name"]
        error = None

        if not name:
            error = "Name is required."

        user = models.Person.nodes.get_or_none(name=name)

        if user is None:
            error = "Incorrect user."

        if error is None:
            session.clear()
            session["user"] = user.name
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
