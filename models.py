import os
from neomodel import (
    DateTimeProperty,
    Relationship,
    StringProperty,
    StringProperty,
    StructuredNode,
    StructuredRel,
    config,
)
from datetime import datetime, timezone, timedelta

config.DATABASE_URL = os.getenv("NEO4J_BOLT_URL")
config.AUTO_INSTALL_LABELS = True


class InteractsWith(StructuredRel):
    activity = StringProperty(required=True)
    when = DateTimeProperty()
    verbs = StringProperty()

    @property 
    def json(self):
        return {
            "activity": self.activity,
            "when": self.when,
            "verbs": self.verbs,
        }

    @property
    def when_string(self):
        return str(self.when)[:19]


class TagsWith(StructuredRel):
    when = DateTimeProperty(default_now=True)
    

class Person(StructuredNode):
    __primarykey__ = "name"

    name = StringProperty(unique_index=True, required=True)
    interactions = Relationship("Person", "INTERACTS_WITH", model=InteractsWith)
    tags = Relationship("Topic", "TAGS_WITH", model=TagsWith)

    @property
    def json(self):
        return {
            "name": self.name,
        }

    def get_contacts(self):
        results, columns = self.cypher("match (Person {name:\""+self.name+"\"})-[r]-(p:Person) return distinct p")
        contacts = [self.inflate(row[0]) for row in results]
        return contacts

    def get_topics(self):
        results, columns = self.cypher("match (t:Topic) return distinct t")
        topics = [Topic.inflate(row[0]) for row in results]
        return topics

    def get_interactions(self):
        results, columns = self.cypher("match (Person {name:\""+self.name+"\"})-[r]-(p:Person) return distinct r")
        interactions = [InteractsWith.inflate(row[0]) for row in results] 
        interactions = dict([(i.activity, i) for i in interactions]).values()
        return interactions

    def get_upcomings(self):
        results, columns = self.cypher("match (Person {name:\""+self.name+"\"})-[r:INTERACTS_WITH]-(p:Person) return distinct r")
        interacts = [InteractsWith.inflate(*row) for row in results]
        upcomings = [interact for interact in interacts if interact.when > datetime.now().replace(tzinfo=timezone(timedelta()))]
        upcomings = dict([(upcoming.activity, upcoming) for upcoming in upcomings]).values()
        return upcomings

    def get_actions(self):
        interactions = self.get_interactions()
        actions = set()
        for interaction in interactions:
            for action in interaction.json["verbs"].split(","):
                actions.add(action)
        return sorted(actions)


class Topic(StructuredNode):
    __primarykey__ = "name"

    name = StringProperty(unique_index=True, required=True)

    @property
    def json(self):
        return {
            "name": self.name,
        }

    def get_contacts(self):
        results, columns = self.cypher("match (Topic {name:\""+self.name+"\"})-[r]-(p:Person) return distinct p")
        contacts = [self.inflate(row[0]) for row in results]
        return contacts

    def get_interactions(self):
        results, columns = self.cypher("match (Topic {name:\""+self.name+"\"})-[:TAGS_WITH]-(p:Person)-[r:INTERACTS_WITH]-(m:Person) return distinct r")
        interactions = [InteractsWith.inflate(row[0]) for row in results] 
        interactions = dict([(i.activity, i) for i in interactions]).values()
        return interactions

    def get_upcomings(self):
        results, columns = self.cypher("match (Topic {name:\""+self.name+"\"})-[:TAGS_WITH]-(p:Person)-[r:INTERACTS_WITH]-(m:Person) return distinct r")
        interacts = [InteractsWith.inflate(*row) for row in results]
        upcomings = [interact for interact in interacts if interact.when > datetime.now().replace(tzinfo=timezone(timedelta()))]
        upcomings = dict([(upcoming.activity, upcoming) for upcoming in upcomings]).values()
        return upcomings

    def get_actions(self):
        interactions = self.get_interactions()
        actions = set()
        for interaction in interactions:
            for action in interaction.json["verbs"].split(","):
                actions.add(action)
        return sorted(actions)


