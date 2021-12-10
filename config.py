import os
from pathlib import Path

# For testing on local instance:

# Read the app_id and app_key required for MathPix API.
# app_user_path = Path("configs/app_user.txt")
# app_password_path = Path("configs/app_password.txt")
# app_reviewer_path = Path("configs/app_reviewer.txt")

# APP_USER = app_user_path.read_text()
# APP_PASSWORD = app_password_path.read_text()
# APP_REVIEWER = app_reviewer_path.read_text()

# For deployment on Heroku:

# Need to set these config variables beforehand in Heroku environment settings
# For more details, refer to https://devcenter.heroku.com/articles/config-vars
APP_USER = os.environ['APP_USER']
APP_PASSWORD = os.environ['APP_PASSWORD']
APP_REVIEWER = os.environ['APP_REVIEWER']
