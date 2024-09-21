import os
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from flask_socketio import SocketIO, emit, send
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from config import Config
from forms import LoginForm, MediaForm, RegistrationForm
from models import Message, User, db

#Update app.py to include real-time messaging with Socket.IO. 
# The goal is to allow users to send messages to each other in real-time using WebSockets.
"""
Flask: The web framework.
Flask-SQLAlchemy: For managing the database.
Flask-SocketIO: For real-time communication (chat).
Flask-Bcrypt: For password hashing.
Flask-Login: For handling user sessions.
Flask-WTF: For handling forms securely.
"""
from config import Config
from forms import LoginForm, MediaForm, RegistrationForm
from models import Message, User, db

app = Flask(__name__)
#SECRET KEY finns i config.py
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
socketio = SocketIO(app, async_mode='eventlet')
login_manager = LoginManager(app)
login_manager.login_view = 'login'  #login_view, fr CGPT; 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

# Messaging route
@app.route('/chat/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def chat(recipient_id):
    recipient = User.query.get_or_404(recipient_id)
    
    
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == recipient_id)) | 
        ((Message.sender_id == recipient_id) & (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp).all()

    if request.method == 'POST':
        # Send message via POST request
        message_content = request.form.get('message')
        if message_content:
            message = Message(sender_id=current_user.id, recipient_id=recipient_id, content=message_content)
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('chat', recipient_id=recipient_id))  # Reload the page to display the new message

    return render_template('chat.html', recipient=recipient, messages=messages)

# WebSocket for real-time chat
@socketio.on('message')
def handle_message(data):
    recipient_id = data['recipient_id']
    message_content = data['message']

    # Save message to the database
    message = Message(sender_id=current_user.id, recipient_id=recipient_id, content=message_content)
    db.session.add(message)
    db.session.commit()

    # Broadcast message to the recipient
    emit('message', {'message': message_content, 'sender': current_user.username}, broadcast=True)

@app.route('/register', methods=['GET', 'POST'])
def register():
    #FORM
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, bio=form.bio.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('profile', user_id=user.id))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


#använder <int:user_id>
@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    form = MediaForm()
    if form.validate_on_submit():
        file = form.media.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        user.media = filename
        db.session.commit()
    return render_template('profile.html', user=user, form=form)

@app.route('/meetnewpeople')
@login_required
def meetnewpeople():
    users = User.query.all()
    return render_template('meetnewpeople.html', users=users)

# SocketIO for chat
@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)

"""
Here’s what the code does:

SocketIO is used to handle WebSockets for real-time chat.
Messages are stored in the database with sender_id, recipient_id, and content.
The handle_message function is triggered when a user sends a message, and it saves the message to the database and broadcasts it to the recipient.
"""

