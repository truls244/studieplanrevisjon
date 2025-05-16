from flask import Flask, jsonify, request, Blueprint
from app.models import  User
from app import jwt, mail
from services import ServiceFactory
from flask_jwt_extended import create_access_token, jwt_required, current_user, unset_jwt_cookies, set_access_cookies, get_jwt, get_jwt_identity
from datetime import datetime, timedelta, timezone
import bcrypt
from flask_mail import Message
import uuid


user_bp = Blueprint('user', __name__)

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.email


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_headers, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(email=identity).one_or_none()


@user_bp.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(days=2))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response


@user_bp.route("/login", methods=["POST"])
def login():
    userservices = ServiceFactory.get_user_service()
    email = request.json.get("email").lower()
    password = request.json.get("password")
    pass_encoded = password.encode(encoding="utf-8")
    user = userservices.get_user_by_email(email)
    if user is None:
        return jsonify({"message": "Feil e-postadresse eller passord"}), 401
    
    if user.check_password(pass_encoded) == False:
        return jsonify({"message": "Feil e-postadresse eller passord"}), 401

    response= jsonify({"message": "Successful login"})
    access_token = create_access_token(identity=user)
    set_access_cookies(response,access_token)
    return response


@user_bp.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@user_bp.route("/register", methods=["POST"])
def register():
    email = request.json.get("email").lower()
    name = request.json.get("name")
    password = bcrypt.hashpw(request.json.get("password1", None).encode(encoding="utf-8"),bcrypt.gensalt())
    userservices = ServiceFactory.get_user_service()
    if userservices.check_if_user_exist_by_email(email):
        return jsonify({"message": "Email already registered"}), 400
    if name == "Admin":
        user = userservices.create_user(email=email,password=password,name=name,role="admin") ## FJERN NÅR ME LEVERE (ellerfør)
    else:
        user = userservices.create_user(email=email,password=password,name=name,role="user")

    verification_token = str(uuid.uuid4())
    userservices.create_verification_token(token=verification_token, email=email)
    msg = Message(
        subject="Verifikasjonlenke til studieplanrevisjon",
        sender="trulsovrebo@gmail.com",
        recipients=[email],
        body = f"Hei velkommen til stueplanrevisjon. Her er lenken til å verifisere kontoen 127.0.0.1:3000/verifytoken/{verification_token}"
    )
    mail.send(msg)
    return jsonify({"message":f"Velkommen til Studiegeneratoren {user.name}!"})



@user_bp.route("/delete/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try: 
        userservice = ServiceFactory.get_user_service()
        userservice.delete_user(user_id)
        return jsonify({"message" : "User has been deleted"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.get("/get_user")
@jwt_required()
def protected():
    return current_user.serialize()

@user_bp.post("/verify/<string:token>")
def verify_user(token):
    userservice = ServiceFactory.get_user_service()
    print("koawkd")
    verified = userservice.verify_token(token=token)

    if verified:
        return jsonify({"message":"Du ble verifisert!"})
    else:
        return jsonify({"message":"Det skjedde en feil"})
    

@user_bp.post("/verify/newtoken")
def new_token():
    user = request.json.get("email")
    userservice = ServiceFactory.get_user_service()
    token = str(uuid.uuid4())
    result = userservice.create_verification_token(token=token , email=user)
    if result:
        msg = Message(
        subject="Verifikasjonlenke til studieplanrevisjon",
        sender="trulsovrebo@gmail.com",
        recipients=[{user}],
        body = f"Her er ny lenke til studiplanrevisjon 127.0.0.1:3000/verifytoken/{token}")
        mail.send(msg)
        return jsonify({"message":"Det ble sendt en ny lenke til e-posten din"})
    return jsonify({"message":"Det skjedde en feil"})
    

@user_bp.route("/reset_password", methods=["POST"])
def reset_pasword():
    email = request.json.get("forgottenEmail")
    userservice = ServiceFactory.get_user_service()
    user=userservice.get_user_by_email(email)
    if user:
        token = str(uuid.uuid4())
        userservice.create_verification_token(token=token, email=email)
        msg = Message(
            subject="Tilbakesill passord",
            sender="trulsovrebo@gmail.com",
            recipients=[user.email],
            body = f"{email} vil tilbakestille passordet sitt. Her er lenken 127.0.0.1:3000/reset_password/{token}"
        )
        mail.send(msg)
        return jsonify({"message":"Hvis e-postadressen er registrert, ble det sendt en e-post"})
    else:
        return jsonify({"message":"Hvis e-postadressen er registrert, ble det sendt en e-post"})


@user_bp.post("/reset/<string:token>")
def reset(token):
    userservice = ServiceFactory.get_user_service()
    password = bcrypt.hashpw(request.json.get("password1", None).encode(encoding="utf-8"),bcrypt.gensalt())
    isReset = userservice.change_password(password=password,token=token)
    if isReset:
        return jsonify({"message": "Passordet ble endret"})
    else:
        return jsonify({"message": "Det skjedde en feil"})

@user_bp.get("/get_all_users")
def get_all_users():
    userservice = ServiceFactory.get_user_service()
    users = userservice.get_all_users()
    return jsonify(users)

@user_bp.get("/get_logs")
def get_logs():
    userservice = ServiceFactory.get_user_service()
    logs = userservice.get_logs()
    return jsonify(logs)
