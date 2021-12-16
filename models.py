from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from geoalchemy2.types import Geometry
import geoalchemy2.functions as func
import json

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """Class to refer to users"""
    __tablename__= "users"

    username = db.Column(db.String(20), primary_key= True)
    password = db.Column(db.Text, nullable = False)
    email = db.Column(db.String(50),nullable = False)
    first_name = db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    is_admin = db.Column(db.Boolean, nullable = False, default = False)

    plans = db.relationship('NewPlans',backref="user", cascade = "all, delete-orphan")
    likes = db.relationship( 'Plans', secondary="likes")
    
    def __repr__(self):
        u = self
        return f"<user username={u.username} first_name={u.first_name} last_name={u.last_name}>"
    
    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        return cls(username= username, password = hashed_utf8, email = email, first_name= first_name, last_name =last_name)
    
    @classmethod
    def authenticate(cls, username, password):
        u = User.query.get(username)

        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False
    
    @classmethod
    def change_password(cls, username, password, newpassword):
        """Change password"""
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                hashed_newpwd= bcrypt.generate_password_hash(newpassword).decode('UTF-8')
                user.password = hashed_newpwd
                return user

        return False
    

class Plans(db.Model):
    """Class to refer to plans"""

    __tablename__="plans"

    id=db.Column(db.Integer,primary_key=True,autoincrement= True)
    plan_name = db.Column(db.Text, nullable= False)
    plan_url = db.Column(db.Text, nullable= False)
    plan_resolution = db.Column(db.Text)
    planning_method = db.Column(db.Text)
    acquisition = db.Column(db.Text)
    easement = db.Column(db.Text)
    stewardship = db.Column(db.Text)
    plan_timeframe = db.Column(db.Text)
    agency_lead = db.Column(db.Text)
    geo_extent = db.Column(db.Text)
    habitat = db.Column(db.Text)
    water_quality = db.Column(db.Text)
    resources_species = db.Column(db.Text)
    community_resilience = db.Column(db.Text)
    ecosystem_resilience = db.Column(db.Text)
    gulf_economy = db.Column(db.Text)
    related_state = db.Column(db.Text)

    def serialize(self):
        return {
            'id': self.id,
            'plan_name':self.plan_name,
            'plan_url': self.plan_url,
            'plan_resolution': self.plan_resolution,
            'planning_method': self.planning_method,
            'acquisition':self.acquisition,
            'easement': self.easement,
            'stewardship': self.stewardship,
            'plan_timeframe': self.plan_timeframe,
            'agency_lead':self.agency_lead,
            'habitat': self.habitat,
            'water_quality': self.water_quality,
            'resources_species': self.resources_species,
            'community_resilience': self.community_resilience,
            'ecosystem_resilience': self.ecosystem_resilience,
            'gulf_economy':self.gulf_economy,
            'related_state': self.related_state
        }

class NewPlans(db.Model):
    """Class to refer to plans"""

    __tablename__="newplans"

    id=db.Column(db.Integer,primary_key=True,autoincrement= True)
    plan_name = db.Column(db.Text, nullable= False)
    plan_url = db.Column(db.Text, nullable= False)
    plan_resolution = db.Column(db.Text)
    planning_method = db.Column(db.Text)
    acquisition = db.Column(db.Text)
    easement = db.Column(db.Text)
    stewardship = db.Column(db.Text)
    plan_timeframe = db.Column(db.Text)
    agency_lead = db.Column(db.Text)
    geo_extent = db.Column(db.Text)
    habitat = db.Column(db.Text)
    water_quality = db.Column(db.Text)
    resources_species = db.Column(db.Text)
    community_resilience = db.Column(db.Text)
    ecosystem_resilience = db.Column(db.Text)
    gulf_economy = db.Column(db.Text)
    related_state = db.Column(db.Text)
    status = db.Column(db.Text, nullable =False,default="pending")
    is_new = db.Column(db.Boolean, nullable=False, default=True)
    existing_planid = db.Column(db.Integer, db.ForeignKey('plans.id', ondelete="cascade"))
    username = db.Column(db.String(20), db.ForeignKey('users.username'), nullable=False)
    published = db.Column(db.Boolean, nullable=False, default=False)

    existing_plan = db.relationship('Plans')

    def serialize(self):
        return {
            'id': self.id,
            'plan_name':self.plan_name,
            'plan_url': self.plan_url,
            'plan_resolution': self.plan_resolution,
            'planning_method': self.planning_method,
            'acquisition':self.acquisition,
            'easement': self.easement,
            'stewardship': self.stewardship,
            'plan_timeframe': self.plan_timeframe,
            'agency_lead':self.agency_lead,
            'habitat': self.habitat,
            'water_quality': self.water_quality,
            'resources_species': self.resources_species,
            'community_resilience': self.community_resilience,
            'ecosystem_resilience': self.ecosystem_resilience,
            'gulf_economy':self.gulf_economy,
            'related_state': self.related_state,
            'status':self.status,
            'is_new':self.is_new,
            'existing_planid':self.existing_planid,
            'username':self.username,
            'published':self.published,
        }

class Geom(db.Model):
    """Class to refer to """
    __tablename__="spatial"

    gid = db.Column(db.Integer,primary_key=True,autoincrement= True )
    name = db.Column(db.Text, nullable = False)
    habitat = db.Column(db.Integer,nullable=False)
    water = db.Column(db.Integer,nullable = False)
    species = db.Column(db.Integer, nullable = False)
    community = db.Column(db.Integer,nullable=False)
    ecosystem = db.Column(db.Integer,nullable = False)
    economy = db.Column(db.Integer, nullable = False)
    f2012 = db.Column(db.Integer,nullable=False)
    f2007 = db.Column(db.Integer,nullable = False)
    f2002 = db.Column(db.Integer, nullable = False)
    scale = db.Column(db.Text, nullable = False)
    geom = db.Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))
    coords = db.column_property(func.ST_AsGeoJSON(geom))

    def serialize(self):
        obj= {}
        obj["geometry"]=json.loads(self.coords)
        obj["geometry"]["type"]="MultiPolygon"
        obj["properties"]={
            'id': self.gid,
            'name':self.name,
            'habitat': self.habitat,
            'water': self.water,
            'species': self.species,
            'community':self.community,
            'ecosystem': self.ecosystem,
            'economy': self.economy,
            'f2012': self.f2012,
            'f2007':self.f2007,
            'f2002': self.f2002,
            'scale': self.scale
        }
        obj["type"]="Feature"
        return obj 
    
class Likes(db.Model):
    """Mapping user likes to warbles."""

    __tablename__ = 'likes' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_username = db.Column(
        db.Integer,
        db.ForeignKey('users.username', ondelete='cascade')
    )

    plan_id = db.Column(
        db.Integer,
        db.ForeignKey('plans.id', ondelete='cascade')
    )