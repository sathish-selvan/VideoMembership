import pathlib
from cassandra.cqlengine.management import sync_table
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Form
from . import config,db
from .users.models import User

BASE_DIR = pathlib.Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / 'templates'

app = FastAPI()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


DB_SESSION = None
settings = config.get_settings()

@app.on_event('startup')
def startup():
    global DB_SESSION
    DB_SESSION=db.get_session()
    sync_table(User)





@app.get('/', response_class=HTMLResponse)
def homepage(request: Request):
    context = {
        'request': request,
        'user' : 'Naren'
    }
    return templates.TemplateResponse('home.html',context)



@app.get("/login",response_class=HTMLResponse)
def login_get_view(request: Request):
    return templates.TemplateResponse("auth/login.html",{
        'request':request,
    })

@app.post("/login",response_class=HTMLResponse)
def login_post_view(request: Request,
    email:str=Form(...),
    password: str=Form(...)):

    print(email, password)
    return templates.TemplateResponse("auth/login.html",{
        'request':request,
    })

@app.get('/signup', response_class=HTMLResponse)
def login_get_view(request: Request):
    return templates.TemplateResponse("auth/signup.html",{
        'request':request,
    })


@app.post("/signup",response_class=HTMLResponse)
def login_post_view(request: Request,
    email:str=Form(...),
    password1: str=Form(...),\
    password2: str=Form(...)):

    print(email, password1, password2)
    return templates.TemplateResponse("auth/signup.html",{
        'request':request,
    })


@app.get('/users')
def users_list_view():
    q = User.objects.all()
    response_json={}
    for users in q:
        response_json[users.email] = [users.email, users.user_id]

    return response_json
