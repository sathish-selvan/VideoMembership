from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from .models import Video
from app import utils
from app.shortcuts import render,redirect,get_object_or_404
from app.users.decorators import login_required
from .schemas import VideoCreateSchema

from app.watch_event.models import WatchEvent

router = APIRouter(prefix="/videos")

def is_htmx(request:Request):
    return request.headers.get('hx-request') == 'true'

@router.get('/',response_class=HTMLResponse)
@login_required
def video_list_view(request: Request):
    q = Video.objects.all()
    context = {
        "object_list" : q,
    }
    return render(request, 'videos/list.html',context)



@router.get('/create',response_class=HTMLResponse)
@login_required
def video_create_view(request:Request, is_htmx=Depends(is_htmx)):

    context={}
    if is_htmx:
        return render(request,'videos/htmx/create.html', context)
    
    return render(request,'videos/create.html', context)


@router.post('/create',response_class=HTMLResponse)
@login_required
def video_create_post_view(request:Request, url:str=Form(...), title:str=Form(...),is_htmx=Depends(is_htmx)):
    raw_data = {
        'url':url,
        'title':title,
        "user_id": request.user.username
    }
    data, errors = utils.valid_schema_data_or_error(raw_data,VideoCreateSchema)
    
    if is_htmx:
        redirect_path = data.get('path')  or  "videos/create.html"
        context = {
            'path':redirect_path,
            'title':data.get('title')
        }
        return render(request, "videos/htmx/link.html",context)
    context ={
        'data':data,
        'errors': errors,
        'url': url,
        "title":title,
    }
    if len(errors) > 0:
        return render(request,'videos/create.html',context, status_code=400)
    redirect_path = data.get('path')  or  "videos/create.html"
    return redirect(redirect_path, context)


@router.get('/{host_id}',response_class=HTMLResponse)
@login_required
def video_detail_view(request: Request, host_id:str):
    obj = get_object_or_404(Video, host_id=host_id)
    user_id = request.user.username
    start_time = WatchEvent.get_resumed_time(host_id, user_id)
    context = {
        "host_id":host_id,
        "object":obj,
        'start_time':start_time,
    }
    return render(request, 'videos/detail.html',context)











