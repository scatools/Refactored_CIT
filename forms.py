from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,TextAreaField, BooleanField,SelectField, IntegerField
from wtforms.fields.html5 import EmailField,URLField
from wtforms.validators import InputRequired, Length,EqualTo,NumberRange


class RegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired(),Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired(),Length(min=6)])
    email = EmailField("Email",validators=[InputRequired()])
    first_name = StringField("First Name",validators=[InputRequired(),Length(max=30)])
    last_name = StringField("Last Name",validators=[InputRequired(),Length(max=30)])

class LoginForm(FlaskForm):
    """Form for logging in a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])



class ChangePasswordFrom(FlaskForm):
    """Change password"""
    password = PasswordField('Current Password', validators=[Length(min=6)])
    newpassword = PasswordField('New Password', validators=[Length(min=6), EqualTo('newpassword_confirm', message='Passwords must match')])
    newpassword_confirm = PasswordField('Confirm New Password', validators=[Length(min=6)])

class UpdateForm(FlaskForm):
    """Form for updating a user."""
    password = PasswordField("Password", validators=[InputRequired(),Length(min=6)])
    email = EmailField("Email",validators=[InputRequired()])
    first_name = StringField("First Name",validators=[InputRequired(),Length(max=30)])
    last_name = StringField("Last Name",validators=[InputRequired(),Length(max=30)])

class NewPlanForm(FlaskForm):
    """Form for a new plan"""
    plan_name = StringField("Plan Name", validators=[InputRequired()])
    plan_url = URLField("Plan URL", validators=[InputRequired()])
    plan_resolution= SelectField("Plan Resolution", choices=[('regional', 'Regional level'), ('statewide', 'State level'), ('county', 'County level'), ('local', 'Local level'),('other','Other')])
    planning_method= SelectField("Planning Method", choices=[('data driven', 'Data driven'), ('stakeholder driven', 'Stakeholder driven'), ('expert opinion', 'Expert opinion'),('other','Other')])
    # acquisition =BooleanField("Acquisition")
    # easement = BooleanField("Easement")
    # stewardship = BooleanField("Stewardship")
    plan_timeframe = IntegerField("Plan Timeframe", validators=[InputRequired(),NumberRange(min=1900,max=2100,message="Value needs to fall within 1900 to current year")] , render_kw={"placeholder": "Optional"})
    agency_lead = StringField("Agency Lead", render_kw={"placeholder": "Optional"})
    geo_extent = SelectField("Geo Extent", choices=[('SE', 'Southeast Region'), ('AL', 'Alabama'), ('FL', 'Florida'),('MS', 'Mississippi'), ('LA', 'Louisana'), ('TX', 'Texas')])
    habitat = TextAreaField("Habitat", render_kw={"placeholder": "Optional"})
    water_quality = TextAreaField("Water Quality", render_kw={"placeholder": "Optional"})
    resources_species = TextAreaField("Resources Species", render_kw={"placeholder": "Optional"})
    community_resilience = TextAreaField("Community Resilience", render_kw={"placeholder": "Optional"})
    ecosystem_resilience = TextAreaField("Ecosystem Resilience", render_kw={"placeholder": "Optional"})
    gulf_economy = TextAreaField("Gulf Economy", render_kw={"placeholder": "Optional"})
    related_state = SelectField("Related State", choices=[('SE', 'Southeast Region'), ('AL', 'Alabama'), ('FL', 'Florida'),('MS', 'Mississippi'), ('LA', 'Louisana'), ('TX', 'Texas')])