from app import db
from app.models import User, Verificationtokens, Log
import datetime
from datetime import timezone


class UserService:
    def __init__(self, db_session=None):
        self.db = db_session or db

    def get_user(self, user_id):
        return self.db.query(User).get(user_id)

    def get_user_by_email(self, email):
        return self.db.query(User).filter(User.email == email).first()
    
    def check_if_user_exist_by_email(self, email):
        if self.db.query(User).filter(User.email == email).first():
            return True
        return False

    def create_user(self, email, password, name, role):
        user = User(
            email=email,
            password=password,
            name=name,
            role=role
        )
        log = Log(f"Opprettet ny bruker {user.email}")
        self.db.add(log)
        self.db.add(user)
        self.db.commit()

        return user

    def update_user(self, user_id, email=None, password=None, first_name=None, last_name=None, studyprogram_id=None):
        user = self.get_user(user_id)

        if email:
            user.email = email
        if password:
            user.password = password
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if studyprogram_id:
            user.studyprogram_id = studyprogram_id

        
        self.db.commit()

        return user

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        self.db.delete(user)
        self.db.commit()
        
        return True

    def create_verification_token(self, token, email):
        old_token = self.db.query(Verificationtokens).get(email)
        if old_token is not None:
            self.db.delete(old_token)
        token = Verificationtokens(token=token, email=email)
        self.db.add(token)
        self.db.commit()
        return True
    
    def verify_token(self, token):
        token = self.db.query(Verificationtokens).get(token)
        if token is None:
            return False
        
        if token.expiration_time.replace(tzinfo = timezone.utc) < datetime.datetime.now(timezone.utc):
            self.db.delete(token)
            return False
        user = self.get_user_by_email(token.email)
        user.verified = True
        log = Log(f"Verifisert bruker {user.email}")
        self.db.add(log)
        self.db.delete(token)
        self.db.commit()
        return True

    def change_password(self, password, token):
        token = self.db.query(Verificationtokens).get(token)
        if token is None:
            return False
        if token.expiration_time.replace(tzinfo = timezone.utc) < datetime.datetime.now(timezone.utc):
            self.db.delete(token)
            return False
        user = self.get_user_by_email(token.email)
        user.password = password
        self.db.delete(token)
        log = Log(f"Endret passord {user.email}")
        self.db.add(log)
        self.db.commit()
        return True
    
    def get_all_users(self):
        users= self.db.query(User).all()
        return [user.serialize() for user in users]
    
    def get_logs(self):
        logs= self.db.query(Log).all()

        return [log.serialize() for log in logs]

