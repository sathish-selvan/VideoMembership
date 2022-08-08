from pydantic import (
    BaseModel,validator,root_validator 
)

from .models import Playlist

class PLaylistCreateSchema(BaseModel):

    title: str
    user_id: str or None





