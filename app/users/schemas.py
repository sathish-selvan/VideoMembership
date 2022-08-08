
from pydantic import BaseModel, EmailStr, SecretStr, validator, root_validator
from .models import User
from app.users import auth

class UserLoginSchema(BaseModel):
    email : EmailStr
    password : SecretStr
    token : str = None

    @root_validator
    def validate_user(cls, values):
        error_msg = "Incorrect Credentials. Please try again"
        email = values.get('email') or None
        password = values.get('password') or None
        
        if email is None or password is None:
            raise ValueError(error_msg)
            
        password = password.get_secret_value()
        user_obj = auth.authenticate(email=email, password=password)
        
        if user_obj is None:
            raise ValueError(error_msg)

        token = auth.login(user_obj=user_obj)
        return {'session_id': token}


class UserSignUpSchema(BaseModel):
    email : EmailStr
    password1 : SecretStr
    password2 : SecretStr

    @validator("email")
    def email_available(cls, v, values, **kwargs ):
        q = User.objects.filter(email=v)
        if q.count() != 0:
            raise ValueError('Email is not available')

    @validator("password2")
    def password_match(cls, v ,values, **kwargs):
        password = values.get('password1')
        password_confirm = v
        if password != password_confirm:
            raise ValueError('Password Does not Match')
        return v


