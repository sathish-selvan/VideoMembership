from cassandra.cqlengine.management import sync_table
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Form
from starlette.middleware.authentication import AuthenticationMiddleware
from . import config,db,utils
from .users.backends import JWTCookieBackend
from .users.models import User
from .users.schemas import UserLoginSchema, UserSignUpSchema
from .shortcuts import redirect, render
from .users.decorators import login_required




app = FastAPI()
app.add_middleware(AuthenticationMiddleware, backend=JWTCookieBackend())

from .handlers import *

DB_SESSION = None
settings = config.get_settings()

@app.on_event('startup')
def startup():
    global DB_SESSION
    DB_SESSION=db.get_session()
    sync_table(User)





@app.get('/', response_class=HTMLResponse)
def homepage(request: Request):
    if request.user.is_authenticated:
        return render(request,"dashboard.html",{},status_code=200)
    context = {}
    return render(request,'home.html',context)


@app.get('/account', response_class=HTMLResponse)
@login_required
def account_page(request: Request):
    context = {}
    return render(request,'account.html',context)



@app.get("/login",response_class=HTMLResponse)
def login_get_view(request: Request):
    session_id = request.cookies.get('session_id') or None
    return render(request,"auth/login.html",{'logged_in':session_id})

@app.post("/login",response_class=HTMLResponse)
def login_post_view(request: Request,
    email:str=Form(...),
    password: str=Form(...),):

    raw_data={
        'email':email,
        'password':password,
        
    }

    data,errors = utils.valid_schema_data_or_error(raw_data, UserLoginSchema)
    context ={
        'data':data,
        'errors': errors
    }
    if len(errors) >0:
        return render(request,"auth/login.html",context=context,status_code=400)
    print(data)
    return redirect('/', cookies=data)

@app.get('/signup', response_class=HTMLResponse)
def login_get_view(request: Request):
    return render(request,"auth/signup.html",{})


@app.post("/signup",response_class=HTMLResponse)
def login_post_view(request: Request,
    email:str=Form(...),
    password1: str=Form(...),
    password2: str=Form(...)):

    raw_data={
        'email':email,
        'password1':password1,
        'password2':password2
    }

    data,errors = utils.valid_schema_data_or_error(raw_data, UserSignUpSchema)

    if len(errors) >0:
        return render(request,"auth/signup.html",{
        "data" : data,
        "errors" : errors
    },status_code=400)


    return redirect('/login',{
        "data" : data,
        "errors" : errors
    })


@app.get('/users')
def users_list_view():
    q = User.objects.all()
    response_json={}
    for users in q:
        response_json[users.email] = [users.email, users.user_id]

    return response_json
