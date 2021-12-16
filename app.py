import os
import base64

from flask import Flask, render_template, redirect, session, flash, jsonify, request, g, url_for
# from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User,Plans,NewPlans,Geom,Likes

from forms import RegisterForm,LoginForm, ChangePasswordFrom,UpdateForm,NewPlanForm
from functools import wraps
import geoalchemy2.functions as func

import json
import smtplib
import datetime
from itsdangerous import SignatureExpired
from itsdangerous.url_safe import URLSafeTimedSerializer

import sqlalchemy
from sqlalchemy.exc import IntegrityError

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink

try: 
    import config as cfg
except:
    print('Configs not imported')

CURR_USER_KEY = "curr_user"
DEFAULT_EMAIL_BODY = 'This email is from the SCA group project.'

app = Flask(__name__)


###################Configurations#############
# work here! << this is where yo left off
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
#     'DATABASE_URL', 'postgres:///iop') # DATABASE_URL = url from 22nd line, iop should be cit
# this is the global link
# you're going to have to set the global link 
#
# Locally
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@127.0.0.1/cit'
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://jykztlfyiujmsg:bbe0ddc19b7221fb23a3a6bc3841574556d96820f08f68761177f77aba1bfefc@ec2-35-153-114-74.compute-1.amazonaws.com:5432/d4n0vbk2s8v0tc'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = 'abc123'
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False


# Email configurations for email sendoffs.
gmail_user = cfg.APP_USER
gmail_password = cfg.APP_PASSWORD
email_reviewer = cfg.APP_REVIEWER

connect_db(app)

# toolbar = DebugToolbarExtension(app)

###################User#############

def login_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect(url_for('homepage'))

        return f(*args, **kwargs)

    return decorated_function

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get_or_404(session[CURR_USER_KEY])

    else:
        g.user = None

@app.route('/register', methods = ["GET", "POST"])
def register_user():
    """User register form and handing register"""
    form = RegisterForm()

    if form.validate_on_submit():
        try:
            username = form.username.data
            password = form.password.data
            email = form.email.data
            first_name = form.first_name.data
            last_name = form.last_name.data
            New_user = User.register(username=username, password=password,email=email,first_name=first_name,last_name=last_name)
            db.session.add(New_user)
            db.session.commit()
            session[CURR_USER_KEY]=New_user.username
            if New_user.is_admin == True:
                session["admin"]=True
            else:
                session["admin"]=False
            return redirect(f"/users/{New_user.username}")
        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('/register.html', form=form)
    else:
        if session.get(CURR_USER_KEY):
            return redirect("/401")
        else:
            return render_template("/user/register.html", form=form)

@app.route('/login', methods = ["GET", "POST"])
def login_user():
    """User login form and handing login"""
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username=username, password=password)
        if(user):
            session[CURR_USER_KEY]=user.username
            if user.is_admin == True:
                session["admin"]=True
            else:
                session["admin"]=False
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors= ["Bad username/password"]
            return render_template("/user/login.html", form=form)
    else:
        if session.get(CURR_USER_KEY):
            return redirect("/401")
        else:
            return render_template("/user/login.html", form=form)

@app.route('/users/<username>')
def view_user_detail(username):
    """Show user detail"""
    print(session[CURR_USER_KEY])
    if(session.get(CURR_USER_KEY)) and (username == session.get(CURR_USER_KEY) or session.get("admin")==True):
        user = User.query.get_or_404(session[CURR_USER_KEY])
        return render_template("/user/user_detail.html", user= user)
    else:
        return redirect("/401")

@app.route('/users/<username>/delete', methods = ["POST"])
def delete_user(username):
    """delete a user"""
    if(session.get(CURR_USER_KEY)) and (username == session.get(CURR_USER_KEY) or session.get("admin")==True):
        user = User.query.get_or_404(username)
        db.session.delete(user)
        db.session.commit()
        session.pop(CURR_USER_KEY)
    return redirect("/")
   
@app.route("/logout", methods= ["POST"])
def logout():
    """Logs user out and redirects to homepage."""
    session.pop(CURR_USER_KEY)

    return redirect("/")

@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    form = UpdateForm(obj= g.user)
    if form.validate_on_submit():
        if(User.authenticate(g.user.username, form.password.data)):
            if(form.email.data):
                g.user.email = form.email.data
            if(form.first_name.data):
                g.user.first_name = form.first_name.data
            if(form.last_name.data):
                g.user.last_name= form.last_name.data
            db.session.add(g.user)
            db.session.commit()
            return redirect(url_for('view_user_detail',username =g.user.username))
        else:
            flash("Wrong password", "danger")
            return redirect(url_for('homepage'))
    return render_template('user/edit.html', form=form)

@app.route('/users/changepassword', methods=["GET", "POST"])
@login_check
def change_password():
    """Update profile for current user."""

    form = ChangePasswordFrom()

    if form.validate_on_submit():
        user = User.change_password(g.user.username, form.password.data, form.newpassword.data)
        if(user):
            g.user = user
            db.session.add(g.user)
            db.session.commit()
            return redirect(url_for('view_user_detail',username =g.user.username))
        else:
            return redirect(url_for('homepage'))
    return render_template('user/changepassword.html', form=form)

###################Emails#############
class Emails():

    # Serializer.
    serializer = URLSafeTimedSerializer('new_plan_confirmation')
 
    def __init__(self, 
                 sent_from = gmail_user, 
                 gmail_password = gmail_password, 
                 to = [email_reviewer],
                 ):

        self.sent_from = sent_from
        self.gmail_password = base64.b64encode(gmail_password.encode('utf-8'))

        self.to = to
        self.subject = 'sca_project_test_email at: ' + str(datetime.datetime.now())
        self.email_text = ''

        # self.new_plan = new_plan
    
    # @
    # def 
    # Create plan confirmation page workflow 
#     @app.route('/users/<plan_id>/delete', methods = ["POST"])
#     def delete_user(username):
    #     """delete a user"""
    #     if(session.get(CURR_USER_KEY)) and (username == session.get(CURR_USER_KEY) or session.get("admin")==True):
    #         user = User.query.get_or_404(username)
    #         db.session.delete(user)
    #         db.session.commit()
    #         session.pop(CURR_USER_KEY)
#     return redirect("/")'

# @app.route('/users/<username>')
# def view_user_detail(username):
#     """Show user detail"""
#     print(session[CURR_USER_KEY])
#     if(session.get(CURR_USER_KEY)) and (username == session.get(CURR_USER_KEY) or session.get("admin")==True):
#         user = User.query.get_or_404(session[CURR_USER_KEY])
#         return render_template("/user/user_detail.html", user= user)
#     else:
#         return redirect("/401")

    def email_body(self, new_plan, email_text = DEFAULT_EMAIL_BODY, ):

        form = NewPlanForm()

        # token = Emails.serializer.dumps()
        token = Emails.serializer.dumps(new_plan.serialize())
        
        link_head = 'http://127.0.0.1:5000'
        confirmation_link = url_for('confirm_email', token=token, external=True)
        confirmation_link = link_head + confirmation_link

        body = 'sca_project_test_email at: ' + str(datetime.datetime.now())
        body += '\n This is a test email from Python Dev App.'
        body += '\n user request: ' + new_plan.username
        body += '\n plan name: ' + new_plan.plan_name
        body += '\n plan time frame: ' + str(new_plan.plan_timeframe)
        body += '\n plan link: ' + new_plan.plan_url
        body += '\n\n Click this link to confirm new plan and add to the database: {}'.format(confirmation_link)
    
        email_text = """
        From: %s
        To: %s
        Subject: %s
        %s
        """ % (self.sent_from, ", ".join(self.to), self.subject, body)
        self.email_text = email_text

        # Protecting Proprietary or Sensitive Information.
        ## Some plan review has already happened. 
        ## Endangered species locations.
        ## How to review proprietary and sensitive information....
        ## Maybe include a disclaimer in the message.

    def email_send(self, new_plan):
        try:

            self.email_body(new_plan)

            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp_server.ehlo()
            smtp_server.login(self.sent_from, base64.b64decode(self.gmail_password).decode())
            smtp_server.sendmail(self.sent_from, self.to, self.email_text)

            smtp_server.close()
            print ("Email sent successfully!")
            return True

        except Exception as ex:
            print ("Something went wrong….", ex)
            return False
 
    
    @app.route('/confirm_email/<token>')
    def confirm_email(token):

        try: 
            # Max age is in seconds. 
            Emails.serializer.loads(token, max_age=10000)
             
            print('making the push to the database')
            db.session.add()
            db.session.commit()

        except SignatureExpired:
            #Token is expired works!!
            return '<h1> The token is expired! </h1>'

        return '<h1>  The plans have been added. </h1>'




#################New plan##################### ,.m, 

@app.route('/users/<username>/plan/add', methods=["GET","POST"])
def add_plan(username):
    """User plan form and handing add plan"""
    form = NewPlanForm()
    email = Emails()

    if form.validate_on_submit():
        plan_name = form.plan_name.data
        plan_url = form.plan_url.data
        plan_resolution= form.plan_resolution.data
        planning_method = form.planning_method.data
        # acquisition =form.acquisition.data,
        # easement = form.easement.data,
        # stewardship = form.stewardship.data,
        plan_timeframe = form.plan_timeframe.data,
        agency_lead = form.agency_lead.data,
        geo_extent = form.geo_extent.data,
        habitat = form.habitat.data,
        water_quality = form.water_quality .data,
        resources_species = form.resources_species.data,
        community_resilience = form.community_resilience.data,
        ecosystem_resilience = form.ecosystem_resilience.data,
        gulf_economy = form.gulf_economy.data,
        related_state = form.related_state.data

        # JL: use above information to include in the email.
        # /new-plan/validate/, methods = ["POST"]
        # then in the body you'll have some information, plan name, blah blah blah
        # this information will be as a post.  
        # gmail for developers: 

        new_plan = NewPlans(plan_name =plan_name,
                            plan_url = plan_url,
                            plan_resolution=plan_resolution, 
                            planning_method = planning_method,
                            # acquisition =acquisition,
                            # easement = easement,
                            # stewardship = stewardship,
                            plan_timeframe = plan_timeframe,
                            agency_lead = agency_lead ,
                            geo_extent = geo_extent,
                            habitat = habitat ,
                            water_quality = water_quality,
                            resources_species = resources_species,
                            community_resilience=community_resilience,
                            ecosystem_resilience=ecosystem_resilience,
                            gulf_economy = gulf_economy,
                            related_state =related_state,
                            username = username,
                            published = False,
                            )

        # Add new plan here.
        # Persist database but have a verified or not column (boolean). 
        db.session.add(new_plan)
        db.session.commit()
        
        # Implement email notification
        try:
            email_success = email.email_send(new_plan)
            if email_success:
                flash('Email has been sent for approval to the committee.')
            else:
                flash('Email confirmation has failed while submitting new plans!')
                # Maybe redirect to an error page.
                # THIS will e implemented elsewhere as a whoel functionality. 
                # thus the posting triggered by the link will trigger this  job down here
  
        finally: 
            # JL: no matter what we re-direct.
            # Front end might want to add a success or fail message though.
            # May want a check email message sent??
            return redirect(f"/users/{new_plan.username}")

    else:
        # JL: 
        if (not session.get(CURR_USER_KEY)):
            return redirect("/401")
        elif session.get(CURR_USER_KEY)!=username and session.get("admin")==False:
            return redirect("/401")
        else:
            return render_template("newplan.html", form=form)

@app.route('/newplan/<plan_id>')
def show_newplan(plan_id):
    """show newplans"""
    if(not session.get(CURR_USER_KEY)):
        return redirect("/401")
    else:
        new_plan = NewPlans.query.get_or_404(plan_id)
        if(new_plan.username == session[CURR_USER_KEY] or session.get("admin")==True):
            return render_template('newplan_detail.html', plan = new_plan)
        else:
            return redirect(f"/users/{session[CURR_USER_KEY]}")

@app.route('/newplan/<plan_id>/update',methods= ["GET","POST"])
def update_newplan(plan_id):
    """update newplan"""
    if(not session.get(CURR_USER_KEY)):
        return redirect("/401")
    else:
        new_plan = NewPlans.query.get_or_404(plan_id)
        if(new_plan.username == session[CURR_USER_KEY] or session.get("admin")==True):
            form = NewPlanForm(obj = new_plan)
            if form.validate_on_submit():
                new_plan.plan_name = form.plan_name.data
                new_plan.plan_url = form.plan_url.data
                new_plan.plan_resolution= form.plan_resolution.data
                new_plan.planning_method = form.planning_method.data
                # new_plan.acquisition =form.acquisition.data,
                # new_plan.easement = form.easement.data,
                # new_plan.stewardship = form.stewardship.data,
                new_plan.plan_timeframe = form.plan_timeframe.data,
                new_plan.agency_lead = form.agency_lead.data,
                new_plan.geo_extent = form.geo_extent.data,
                new_plan.habitat = form.habitat.data,
                new_plan.water_quality = form.water_quality .data,
                new_plan.resources_species = form.resources_species.data,
                new_plan.community_resilience = form.community_resilience.data,
                new_plan.ecosystem_resilience = form.ecosystem_resilience.data,
                new_plan.gulf_economy = form.gulf_economy.data,
                new_plan.related_state = form.related_state.data

                db.session.add(new_plan)
                db.session.commit()
                return redirect(f"/users/{session[CURR_USER_KEY]}")
            else:
                return render_template("newplan.html", form = form)
        else:
            return redirect(f"/users/{session[CURR_USER_KEY]}")

@app.route('/newplan/<plan_id>/delete',methods= ["POST"])
def remove_newplan(plan_id):
    """remove a new plan"""
    if(not session.get(CURR_USER_KEY)):
        return redirect("/401")
    else:
        new_plan = NewPlans.query.get_or_404(plan_id)
        if(new_plan.username == session[CURR_USER_KEY] or session.get("admin")==True):
            db.session.delete(new_plan)
            db.session.commit()
        return redirect(f"/users/{session[CURR_USER_KEY]}")

#################Plan#########################
@app.route('/plans/<int:plan_id>')
def show_plan_detail(plan_id):
    """Show Plan Detail"""
    plan = Plans.query.get_or_404(plan_id)
    if(g.user):
        if(plan in g.user.likes):
            liked = True
        else:
            liked = False
    else:
        liked = False
    
    return render_template('plan_detail.html', plan = plan,liked = liked)

@app.route('/plans/<int:plan_id>/like', methods= ["POST"])
def like_plan(plan_id):
    """Like a plan and add that into databse"""
    if(not session.get(CURR_USER_KEY)):
        return redirect("/401")
    else:
        target_plan = Plans.query.get_or_404(plan_id)
        user_likes = g.user.likes

        if target_plan in user_likes:
            g.user.likes = [like for like in user_likes if like != target_plan]
        else:
            g.user.likes.append(target_plan)

        db.session.commit()

        return jsonify({'msg': "done"}) 

@app.route('/plans/<int:plan_id>/update',methods=["GET","POST"])
def update_plan(plan_id):
    """User plan form and handing add plan"""
    plan = Plans.query.get_or_404(plan_id)
    form = NewPlanForm(obj = plan)
    if form.validate_on_submit():
        plan_name = form.plan_name.data
        plan_url = form.plan_url.data
        plan_resolution= form.plan_resolution.data
        planning_method = form.planning_method.data
        # acquisition =form.acquisition.data,
        # easement = form.easement.data,
        # stewardship = form.stewardship.data,
        plan_timeframe = form.plan_timeframe.data,
        agency_lead = form.agency_lead.data,
        geo_extent = form.geo_extent.data,
        habitat = form.habitat.data,
        water_quality = form.water_quality .data,
        resources_species = form.resources_species.data,
        community_resilience = form.community_resilience.data,
        ecosystem_resilience = form.ecosystem_resilience.data,
        gulf_economy = form.gulf_economy.data,
        related_state = form.related_state.data

        new_plan = NewPlans(plan_name =plan_name,
                            plan_url = plan_url,
                            plan_resolution=plan_resolution, 
                            planning_method = planning_method,
                            # acquisition =acquisition,
                            # easement = easement,
                            # stewardship = stewardship,
                            plan_timeframe = plan_timeframe,
                            agency_lead = agency_lead ,
                            geo_extent = geo_extent,
                            habitat = habitat ,
                            water_quality = water_quality,
                            resources_species = resources_species,
                            community_resilience=community_resilience,
                            ecosystem_resilience=ecosystem_resilience,
                            gulf_economy = gulf_economy,
                            related_state =related_state,
                            username = g.user.username,
                            is_new = False,
                            existing_planid = plan_id
                            )
        db.session.add(new_plan)
        db.session.commit()
        return redirect(f"/users/{new_plan.username}")
    else:
        if (not session.get(CURR_USER_KEY)):
            return redirect("/401")
        else:
            return render_template("newplan.html", form=form)

#################Table########################
@app.route('/table')
def show_table():
    """render plans table"""
    if(g.user):
        likes = [like.id for like in g.user.likes] 
    else:
        likes = []
    return render_template('table.html', likes = likes)

@app.route('/table_get_data')
def table_get_data():
  """ Create data for table"""
  query_scale = request.args.get("scale")
  if query_scale and query_scale != "ALL" :
      if query_scale == "SE":
          query_scale = "Regional"
      plans = Plans.query.filter(Plans.geo_extent == query_scale).all()
  else:
      plans = Plans.query.all()
  
  return_data = []
  for plan in plans:
      return_data.append(plan.serialize())
  data = {
    "data": return_data
  }
  return jsonify(data)

###########Error handling#####################

@app.errorhandler(404)
def page_not_found(e):
    """404 page"""
    return (render_template('/error/404.html'), 404)

@app.route("/401")
def page_not_allowed():
    """401 page"""
    return render_template('/error/401.html')

###############Home page####################
@app.route('/')
def homepage():
    return render_template('home.html')

###############Contact Us Page##############
@app.route('/contactus')
def show_contactus_page():
    return render_template('contactus.html')

###############Map geojson##################

# @app.route('/get_map_data')
# def get_map_data():
#     print(request.args.get("scale"))
#     if not request.args.get("scale") or request.args.get("scale")=="States":
#         geometries = Geom.query.filter(Geom.name.in_(["TX","LA","AL","MS","FL"])).all()
#     else:
#         query_scale = request.args.get("scale")
#         geometries = Geom.query.filter(Geom.scale == query_scale).all()

#     return_data = []
#     for geometry in geometries:
#       return_data.append(geometry.serialize())
#     data = {
#       "data": return_data
#     }

#     return jsonify(data)

@app.route('/spatial_query')
def spatial_query():
    content = {
        "type": "Point",
        "coordinates": [request.args.get("lng"),request.args.get("lat")]
    }
    content = json.dumps(content)
    query = Geom.query.filter(func.ST_Intersects(func.ST_GeomFromGeoJSON(Geom.coords), func.ST_GeomFromGeoJSON(content))).all()
    matchedgeom = []
    for geom in query:
        matchedgeom.append(geom.name)
    plans = Plans.query.filter(Plans.related_state.in_(matchedgeom)).order_by(Plans.id).all()
    return_data = []
    for plan in plans:
      return_data.append(plan.serialize())
    data = {
      "data": return_data
    }
    return jsonify(data)

################Admin module with flask admin################

admin = Admin(app, name='Inventory of Plan', base_template='admin_tem/layout.html', template_mode='bootstrap3')
# Add administrative views here

class CustomView(ModelView):
    def is_accessible(self):
        if g.user:
            if g.user.is_admin:
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('homepage'))

    list_template = 'admin_tem/list.html'
    create_template = 'admin_tem/create.html'
    edit_template = 'admin_tem/edit.html'


class UserView(CustomView):
    column_exclude_list = ('password')
    can_create = False
    form_excluded_columns = ['password']

class PlanView(CustomView):

    def _plan_url_formatter(view, context, model, name):
        # Format your string here e.g show first 20 characters
        # can return any valid HTML e.g. a link to another view to show the detail or a popup window
        return model.plan_url[:20]
    can_view_details = True
    column_exclude_list = ('habitat','water_quality','resources_species','community_resilience','ecosystem_resilience','gulf_economy','acquisition','easement','stewardship','plan_timeframe','plan_resolution')
    column_formatters = {
        'plan_url': _plan_url_formatter
    }
    form_choices = {
        'related_state': [
        ('TX', 'Texas'),
        ('AL', 'Alabama'),
        ('FL', 'Florida'),
        ('MS', 'Mississippi'),
        ('LA', 'Louisana'),
        ('SE', 'Southeast Region')],
        'status':[
        ('pending','Pending'),
        ('reviewing','Needs review'),
        ('commited','Commited')
        ]
    }

admin.add_view(UserView(User, db.session))
admin.add_view(PlanView(Plans, db.session))
admin.add_view(PlanView(NewPlans, db.session))

if __name__ == '__main__':
    app.run(debug=True)