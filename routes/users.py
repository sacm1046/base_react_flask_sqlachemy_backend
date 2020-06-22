from flask import Blueprint, jsonify, request, render_template, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt
from libs.functions import sendMail
from itsdangerous import URLSafeSerializer
from itsdangerous import URLSafeTimedSerializer
from models import db, User

bcrypt = Bcrypt()
user_route = Blueprint('user_route', __name__)
@user_route.route('/users', methods=['GET'])
@user_route.route('/user/<int:id>', methods=['GET'])
@jwt_required
def user(id=None):
    if request.method == 'GET':
        if id is not None:
            user = User.query.get(id)
            if user:
                return jsonify(user.serialize()), 200
            else:
                return jsonify({"msg":"Not Found"}), 404
        else:
            users = User.query.all()
            users = list(map(lambda user: user.serialize(), users))
            return jsonify(users), 200

@user_route.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    if not email:
        return jsonify({"error": "Insert your email"}), 422
    if not password:
        return jsonify({"error": "Insert your password"}), 422
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email is not registered"}), 404
    pw_hash = bcrypt.generate_password_hash(password)
    if bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.email)
        data = {
            "access_token": access_token,
            "user": user.serialize()
        }
        return jsonify(data), 200
    else: 
        return jsonify({"error": "Email or password is not correct"}), 401

@user_route.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    fullname = request.json.get('fullname')
    password = request.json.get('password')
    if not email:
        return jsonify({"error": "Email is required"}), 422
    if not fullname:
        return jsonify({"error": "Fullname is required"}), 422             
    if not password:
        return jsonify({"error": "Password is required"}), 422
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"error": "This email already exist"}), 422
    user = User()
    user.email = email
    user.fullname = fullname
    user.password = bcrypt.generate_password_hash(password)
    db.session.add(user)
    db.session.commit()
    if bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.email)
        data = {
            "access_token": access_token,
            "user": user.serialize()
        }
        return jsonify(data), 200

#Change password route
@user_route.route('/change-password', methods=['PUT'])
@jwt_required
def changepassword():
    oldpassword = request.json.get('oldpassword', None)
    password = request.json.get('password', None)
    if oldpassword == password:
       return jsonify({"error": "La nueva contraseña debe ser distinta de la anterior"}), 400
    if not oldpassword or oldpassword == '':
        return jsonify({"error": "Su contraseña actual es obligatoria"}), 400
    if not password or password == '':
        return jsonify({"error": "Su nueva contraseña es obligatoria"}), 400
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if bcrypt.check_password_hash(user.password, oldpassword):
        user.password = bcrypt.generate_password_hash(password)
        db.session.commit()
        return jsonify({"success": "password has changed"}), 200
    else:
        return jsonify({"error": "old password is incorrect"}), 400

#Forget password routes
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=86400):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

@user_route.route('/forget-password', methods=['POST'])
def forget_password():
        email = request.json.get('email', None)
        if not email or email == '':
            return None
        user = User()
        user.email = email
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"msg": "This email is not registered"}), 404
        token = generate_confirmation_token(user.email)
        print(token)
        confirm_url = 'http://localhost:3000/confirmation/' + token
        html = render_template('email_confirmation.html', confirm_url=confirm_url)
        subject = "Por favor, Confirmar su email."
        sendMail("Por favor, Confirmar su email.",'','', user.email, html)
        return jsonify({"success": "Email send successfully"}), 200

@user_route.route('/forget-password-confirm/<token>', methods=['POST'])
def forget_password_confirm(token):
    password = request.json.get('password', None)
    if not password or password == '':
        return jsonify({"msg": "You need to write your password"}), 422 
    try:
        email = confirm_token(token)
    except:
        return jsonify({"msg": "El enlace de confirmacion es invalido o ha expirado."}), 401
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "This email is not registered"}), 404
    user.password = bcrypt.generate_password_hash(password)
    db.session.commit()
    return jsonify({"msg": "password changed"}), 200

