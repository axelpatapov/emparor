# Backend Code (Python/Flask)

import os

class Config:
    SECRET_KEY = 'yoursecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
