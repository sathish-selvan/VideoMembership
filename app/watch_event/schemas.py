from xmlrpc.client import Boolean
from pydantic import BaseModel
from typing import Optional


class WatchEventSchema(BaseModel):
    host_id : str
    start_time:float
    end_time:float
    complete: bool
    duration: float
    path : Optional[str]

