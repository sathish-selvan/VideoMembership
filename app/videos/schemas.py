from pydantic import (
    BaseModel,validator,root_validator 
)

from .extrators import extract_video_id
from app.users.exceptions import InvalidUserIdException
from .exceptions import InvalidYoutubeVideoURLException, VideoAddedException
from .models import Video

class VideoCreateSchema(BaseModel):
    url: str
    title: str
    user_id: str or None

    @validator('url')
    def validate_youtube_url(cls, v, values, **kwargs):
        url = v
        video_id = extract_video_id(url)
        if video_id is None:
            raise ValueError(f'{url} is not a valid YouTube URL')

        return url

    @root_validator
    def validate_data(cls, values):
        url = values.get('url')
        user_id = values.get('user_id')
        title = values.get('title')
        extra_data = {}
        if title is not None:
            extra_data['title'] = title

        video_obj = None
        try:
            video_obj = Video.add_video(url,user_id,**extra_data)
        except VideoAddedException as e:
            raise ValueError(f'{url} is already exists')
        except InvalidUserIdException as e:
            raise ValueError('Invalid username')
        except InvalidYoutubeVideoURLException as e:
            raise ValueError(f'{url} is an invalid Youtube Url')
        except:
            raise ValueError("There's problem with ur account")

        if video_obj is None:
            raise ValueError("There's problem with ur account")

        if not isinstance(video_obj,Video):
            raise ValueError("There's problem with ur account")

        return video_obj.as_data()


class VideoEditSchema(BaseModel):
    url: str
    title: str
    user_id: str or None

    @validator('url')
    def validate_youtube_url(cls, v, values, **kwargs):
        url = v
        video_id = extract_video_id(url)
        if video_id is None:
            raise ValueError(f'{url} is not a valid YouTube URL')

        return url
