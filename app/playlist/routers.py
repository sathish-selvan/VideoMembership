from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from .models import Playlist
from app import utils
from app.shortcuts import render,redirect,get_object_or_404,is_htmx
from app.users.decorators import login_required
from .schemas import PLaylistCreateSchema, PlaylistVideoAddSchema
from app.videos.schemas import VideoCreateSchema
from starlette.exceptions import HTTPException

from app.watch_event.models import WatchEvent
from typing import Optional
import uuid

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
def playlist_detail_view(request: Request, db_id:uuid.UUID):
    obj = get_object_or_404(Playlist, db_id=db_id)
    user_id = request.user.username
    context = {
        "object":obj,
        'videos':obj.get_videos(),
    }
    return render(request, 'playlist/detail.html',context)



@router.get('/{db_id}/add-video',response_class=HTMLResponse)
@login_required
def playlist_video_add_view(request:Request, db_id:uuid.UUID,is_htmx=Depends(is_htmx)):

    context={"db_id":db_id}
    if not is_htmx:
        raise HTTPException(status_code=400)
        # return render(request,'videos/htmx/create.html', context)
    
    return render(request,'playlist/htmx/add-video.html', context)


@router.post('/{db_id}/add-video',response_class=HTMLResponse)
@login_required
def playlist_video_add_post_view(request:Request, db_id:uuid.UUID, url:str=Form(...), title:str=Form(...),is_htmx=Depends(is_htmx)):
    raw_data = {
        'url':url,
        'title':title,
        "user_id": request.user.username,
        "playlist_id":db_id,
    }
    print('hello')
    data, errors = utils.valid_schema_data_or_error(raw_data,PlaylistVideoAddSchema)
    
    if not is_htmx:
        raise HTTPException(status_code=400)
    redirect_path = data.get('path')  or  f"playlist/{db_id}/"
    
    context = {
        'path':redirect_path,
        'title':data.get('title'),
        'errors': errors,
        'db_id':db_id
    }
    if len(errors) > 0:
        return render(request,'playlist/htmx/add-video.html',context)
    return render(request, "videos/htmx/link.html",context)
    



@router.post('/{db_id}/{host_id}/delete',response_class=HTMLResponse)
@login_required
def playlist_remove_item_view(request: Request, 
        db_id:uuid.UUID,
        host_id:str,
        is_htmx=Depends(is_htmx),
        index:Optional[int]=Form(default=None)):
    if not is_htmx:
        raise HTTPException(status_code=400)
    try:
        obj = get_object_or_404(Playlist, db_id=db_id)
    except:
        return HTMLResponse("Error, Please reload the page.")
    user_id = request.user.username
    context = {
        "object":obj,
        'videos':obj.get_videos(),
    }
    if isinstance(index, int):
        host_ids = obj.host_ids
        host_ids.pop(index)
        obj.add_host_ids(host_ids, replace_all=True)
    print(obj.db_id, host_id)
    return HTMLResponse("Deleted")








