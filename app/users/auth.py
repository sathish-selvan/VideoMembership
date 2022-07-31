

from app import config
from jose import jwt, ExpiredSignatureError

from .models import User

settings = config.get_settings()

def authenticate(email, password):
    try:
        user_obj = User.objects.get(email=email)
        print(password)
        if not user_obj.verify_password(password):
            return None
        return user_obj

    except Exception as e:
        return None


def login(user_obj):
    raw_data = {
        'user_id' : f'{user_obj.user_id}',
        
    }
    return jwt.encode(raw_data, settings.secret_key, algorithm=settings.algo)


def verify_user_id(token):
    data= {}
    verified = False
    try:
        data = jwt.decode(token, settings.secret_key, algorithms=settings.algo)
        verified = True
    except ExpiredSignatureError as e:
        print(e)
    except Exception as e:
        print(e)

    if 'user_id' not in data:
        return None

    return data













