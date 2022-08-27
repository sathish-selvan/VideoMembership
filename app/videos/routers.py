from email.policy import default
from typing import Optional
import uuid
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from .models import Video
from app import utils
from app.shortcuts import render,redirect,get_object_or_404, is_htmx
from app.users.decorators import login_required
from .schemas import VideoCreateSchema, VideoEditSchema
from starlette.exceptions import HTTPException
from app.watch_event.models import WatchEvent
from .extrators import extract_video_id

router = APIRouter(prefix="/videos")



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
def video_create_view(request:Request, playlist:Optional[uuid.UUID]=None,is_htmx=Depends(is_htmx)):
    print(playlist)
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
            'title':data.get('title'),
            'errors': errors,
        }
        if len(errors) > 0:
            return render(request,'videos/htmx/create.html',context)
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

@router.get('/{host_id}/edit',response_class=HTMLResponse)
@login_required
def video_edit_view(request: Request, host_id:str):
    obj = get_object_or_404(Video, host_id=host_id)
    
    context = {
        "host_id":host_id,
        "object":obj,
    }
    return render(request, 'videos/edit.html',context)


@router.post('/{host_id}/edit',response_class=HTMLResponse)
@login_required
def video_edit_post_view(request:Request,
    host_id:str,
    url:str=Form(...), 
    title:str=Form(...),
    is_htmx=Depends(is_htmx)):
    raw_data = {
        'url':url,
        'title':title,
        "user_id": request.user.username
    }
    obj = get_object_or_404(Video, host_id=host_id)
    data, errors = utils.valid_schema_data_or_error(raw_data,VideoEditSchema)
    context ={
        'object': obj,
        'errors': errors,
    }
    if len(errors) > 0:
        return render(request,'videos/edit.html',context, status_code=400)
    obj.title = data.get("title") or obj.title
    obj.update_video_url(url, save=True)
    context ={
        'object': obj,
    }
    return render(request,'videos/edit.html',context)


@router.get('/{host_id}/hx-edit',response_class=HTMLResponse)
@login_required
def video_hx_edit_view(request: Request, host_id:str,is_htmx=Depends(is_htmx)):
    if not is_htmx:
        raise HTTPException(status_code=400)
    obj= None
    not_found = False
    try:
        obj = get_object_or_404(Video, host_id=host_id)
    except:
        not_found = True
    if not_found:
        return HTMLResponse('Not Found, please try again')
    context = {
        "host_id":host_id,
        "object":obj,
    }
    return render(request, 'videos/htmx/edit.html',context)


@router.post('/{host_id}/hx-edit',response_class=HTMLResponse)
@login_required
def video_hx_edit_post_view(request:Request,
    host_id:str,
    url:str=Form(...), 
    title:str=Form(...),
    is_htmx=Depends(is_htmx),
    delete:Optional[bool]=Form(default=False)):
    if not is_htmx:
        raise HTTPException(status_code=400)
    obj= None
    not_found = False
    try:
        obj = get_object_or_404(Video, host_id=host_id)
    except:
        not_found = True
    if not_found:
        return HTMLResponse('Not Found, please try again')
    if delete:
        obj.delete()
        return HTMLResponse("Item Deleted")
    raw_data = {
        'url':url,
        'title':title,
        "user_id": request.user.username
    }
    data, errors = utils.valid_schema_data_or_error(raw_data,VideoEditSchema)
    context ={
        'object':obj,
        'errors': errors,
    }
    if len(errors) > 0:
        return render(request,'videos/htmx/edit.html',context, status_code=400)
    obj.title = data.get("title") or obj.title
    obj.url = data.get("url") or obj.url
    hs_id = extract_video_id(obj.url)
    obj.host_id = hs_id or obj.host_id
    
    # obj.update_video_url(url, save=True)
    obj.save()
    context ={
        'object':obj,
        'errors': errors,
    }
    return render(request,'videos/htmx/list-inline.html',context)









