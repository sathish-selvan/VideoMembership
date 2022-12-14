from ast import Num
from urllib import response
from cassandra.cqlengine.management import sync_table
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Form
from starlette.middleware.authentication import AuthenticationMiddleware
from . import config,db,utils
from .indexing.client import (update_index, search_index)
from .users.backends import JWTCookieBackend
from .users.models import User
from .users.schemas import UserLoginSchema, UserSignUpSchema
from .shortcuts import redirect, render
from .users.decorators import login_required
from typing import Optional
from .videos.models import Video
from .watch_event.models import WatchEvent
from .watch_event.routers import router as watch_event_router
from .videos.routers import router as video_router
from .playlist.routers import router as playlist_router

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
    sync_table(Video)
    sync_table(WatchEvent)


app.include_router(video_router)
app.include_router(watch_event_router)
app.include_router(playlist_router)

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
    password: str=Form(...),
    next: Optional[str]= '/'):

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

    if "http://127.0.0.1" not in next:
        next = '/'

    return redirect(next, cookies=data)

@app.get("/logout",response_class=HTMLResponse)
def logout_get_view(request: Request):
    return render(request,"auth/logout.html",{})

@app.post("/logout",response_class=HTMLResponse)
def logout_post_view(request: Request):
    return redirect('/login',remove_session=True)

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


@app.post("/update-index",response_class=HTMLResponse)
def htmx_update_index_view(request:Request):
    count = update_index()
    return HTMLResponse(f"({count}) Refreshed")

@app.get('/search')
def search_detail_view(request:Request, q:Optional[str]=None):
    query = None
    if q is not None:
        query = q
        results = search_index(query)
        hits = results.get('hits') or []
        num_hits = results.get('nbHits')
        context = {
            'query':q,
            'hits':hits,
            'num_hits':num_hits
        }


    return render(request, 'search/search_detail.html', context)






