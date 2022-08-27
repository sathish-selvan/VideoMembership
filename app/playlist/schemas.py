from pydantic import (
    BaseModel,validator,root_validator 
)

import uuid
from  app.videos.extrators import extract_video_id
from app.users.exceptions import InvalidUserIdException
from app.videos.exceptions import InvalidYoutubeVideoURLException, VideoAddedException
from app.videos.models import Video
from .models import Playlist

class PLaylistCreateSchema(BaseModel):

    title: str
    user_id: str or None




class PlaylistVideoAddSchema(BaseModel):
    url: str
    title: str
    user_id: uuid.UUID
    playlist_id : uuid.UUID

    @validator('url')
    def validate_youtube_url(cls, v, values, **kwargs):
        url = v
        video_id = extract_video_id(url)
        if video_id is None:
            raise ValueError(f'{url} is not a valid YouTube URL')
        return url


    @validator('playlist_id')
    def validate_playlist_id(cls, v, values, **kwargs):
        q = Playlist.objects.filter(db_id=v)
        if q.count() == 0:
            raise ValueError(f'Playlist Does not Exists')
        return v

    @root_validator
    def validate_data(cls, values):
        url = values.get('url')
        user_id = values.get('user_id')
        title = values.get('title')
        playlist_id = values.get('playlist_id')

        video_obj = None
        try:
            video_obj,created = Video.get_or_create_video(url,user_id,title=title)
        except Exception as e:
            raise ValueError(e)

        if not isinstance(video_obj,Video):
            raise ValueError("There's problem with ur account")
        else:
            playlist_obj = Playlist.objects.get(db_id=playlist_id)
            playlist_obj.add_host_ids(host_ids=[video_obj.host_id])
            playlist_obj.save()
        return video_obj.as_data()






