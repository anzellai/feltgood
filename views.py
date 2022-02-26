from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
import models
from auth import login_required
from datetime import datetime
import re
import parsedatetime

bp = Blueprint("views", __name__, url_prefix="/views")


@bp.route(
    "/interactions",
    methods=("POST",),
)
@login_required
def interactions():
    error = None
    interaction = request.form.get("interaction", "")
    if interaction == "":
        error = "Interaction is required."
        flash(error)
        return redirect(url_for("views.index"))

    people = models.Person.get_or_create(
        *[{"name": p} for p in re.findall(r"@(\w+)", interaction)]
    )
    verbs = ",".join(re.findall(r"/(\w+)", interaction))
    when = re.findall(r"\[(.*?)\]", interaction)
    if when:
        calendar = parsedatetime.Calendar()
        ts, status = calendar.parse(when[0])
        when = datetime(*ts[:6])
    else:
        when = datetime.now()
    topics = models.Topic.get_or_create(
        *[{"name": t} for t in re.findall(r"#(\w+)", interaction)]
    )
    print({"activity": interaction, "when": when, "verbs": verbs})

    for person in people:
        g.user.interactions.connect(
            person, {"activity": interaction, "when": when, "verbs": verbs}
        )
        if topics:
            for topic in topics:
                person.tags.connect(topic, {"when": when})

    return redirect(url_for("index"))


## Contacts

@bp.route(
    "/contacts",
    methods=("GET",),
)
@login_required
def contacts():
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
        "views/contacts.html", context=context,
    )


@bp.route(
    "/contacts/<name>",
    methods=("GET",),
)
@login_required
def contact(name):
    error = None
    contact = models.Person.nodes.get_or_none(name=name)
    if not contact:
        error = "Contact not found."
        flash(error)
        return redirect(url_for("views.contacts"))
    contacts = contact.get_contacts()
    topics = contact.get_topics()
    interactions = contact.get_interactions()    
    upcomings = contact.get_upcomings()
    actions = contact.get_actions()        

    context = {
        "contact": contact,
        "contacts": [contact for contact in contacts],
        "topics": [topic for topic in topics],
        "interactions": interactions,
        "upcomings": upcomings,
        "actions": actions,
    }
    return render_template(
        "views/contact.html", context=context,
    )

## Topics

@bp.route(
    "/topics",
    methods=("GET",),
)
@login_required
def topics():
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
        "views/topics.html", context=context,
    )


@bp.route(
    "/topics/<name>",
    methods=("GET",),
)
@login_required
def topic(name):
    error = None
    topic = models.Topic.nodes.get_or_none(name=name)
    if not topic:
        error = "Topic not found."
        flash(error)
        return redirect(url_for("views.topics"))

    contacts = topic.get_contacts()
    topics = [topic]
    interactions = topic.get_interactions()    
    upcomings = topic.get_upcomings()
    actions = topic.get_actions()        

    context = {
        "contacts": [contact for contact in contacts],
        "topic": topic,
        "topics": [topic for topic in topics],
        "interactions": interactions,
        "upcomings": upcomings,
        "actions": actions,
    }
    return render_template(
        "views/topic.html", context=context,
    )


## Actions

@bp.route(
    "/actions",
    methods=("GET",),
)
@login_required
def actions():
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
        "views/actions.html", context=context,
    )


@bp.route(
    "/actions/<name>",
    methods=("GET",),
)
@login_required
def action(name):
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
        "action": name,
    }
    return render_template(
        "views/action.html", context=context,
    )
