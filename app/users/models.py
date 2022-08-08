
import uuid
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns
from app.config import get_settings
from . import validators, security
from .exceptions import InvalidEmailException, UserHasAccoutException

settings = get_settings()

class User(Model):
    __keyspace__ = settings.keyspace
    email = columns.Text(primary_key=True)
    user_id = columns.UUID(primary_key=True, default=uuid.uuid1)
    password = columns.Text()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'User(email={self.email}, user_id={self.user_id})'

    def set_password(self, pw, commit=False):
        pw_hash = security.generate_hash(pw)
        self.password = pw_hash
        if commit:
            self.save()
        return True

    def verify_password(self, pw):
        pw_hash = self.password
        verified,_ = security.verify_hash(pw_hash=pw_hash,pw_raw=pw)
        return verified

    @staticmethod
    def create_user(email, password=None):
        valid,msg,email = validators._validate_email(email=email)
        if not valid:
            raise InvalidEmailException(f"Invalid Email: {msg}")
        q = User.objects.filter(email=email)
        if q.count() != 0:
            raise UserHasAccoutException("User already has account")
        obj = User(email=email)
        obj.set_password(pw=password)
        # obj.password = security.generate_hash(password)
        obj.save()
        return obj

    @staticmethod
    def check_exists(user_id):
        q = User.objects.filter(user_id=user_id).allow_filtering()
        return q.count() != 0

    @staticmethod
    def by_user_id(user_id=None):
        if user_id is None:
            return None
        q = User.objects.filter(user_id = user_id).allow_filtering()
        if q.count != 1:
            return None
        return q.first()