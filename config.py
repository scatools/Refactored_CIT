from pathlib import Path

# Read the app_id and app_key required for MathPix API.
app_user_path = Path("configs/app_user.txt")
app_password_path = Path("configs/app_password.txt")
app_reviewer_path = Path("configs/app_reviewer.txt")

APP_USER = app_user_path.read_text()
APP_PASSWORD = app_password_path.read_text()
APP_REVIEWER = app_reviewer_path.read_text()