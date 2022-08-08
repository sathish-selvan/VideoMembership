from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from .models import Playlist
from app import utils
from app.shortcuts import render,redirect,get_object_or_404
from app.users.decorators import login_required
from .schemas import PLaylistCreateSchema

from app.watch_event.models import WatchEvent

router = APIRouter(prefix="/playlist")



@router.get('/',response_class=HTMLResponse)
@login_required
def playlist_list_view(request: Request):
    q = Playlist.objects.all()
    context = {
        "object_list" : q,
    }
    return render(request, 'playlist/list.html',context)



@router.get('/create',response_class=HTMLResponse)
@login_required
def playlist_create_view(request:Request):
    context={}
    return render(request,'playlist/create.html', context)



@router.post('/create',response_class=HTMLResponse)
@login_required
def playlist_create_post_view(request:Request, title:str=Form(...)):
    raw_data = {
        'title':title,
        "user_id": request.user.username
    }
    data, errors = utils.valid_schema_data_or_error(raw_data,PLaylistCreateSchema)
    context ={
        'data':data,
        'errors': errors,
        "title":title,
    }
    if len(errors) > 0:
        return render(request,'playlist/create.html',context, status_code=400)
    print(data)
    obj = Playlist.objects.create(**data)
    redirect_path = obj.path  or  "playlist/create.html"
    return redirect(redirect_path, context)



@router.get('/{db_id}',response_class=HTMLResponse)
@login_required
def playlist_detail_view(request: Request, db_id:str):
    obj = get_object_or_404(Playlist, db_id=db_id)
    user_id = request.user.username
    context = {
        "object":obj,
        'videos':obj.get_videos(),
    }
    return render(request, 'playlist/detail.html',context)












