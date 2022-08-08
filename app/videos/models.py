import uuid
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns
from app.shortcuts import templates
from app.config import get_settings
from app.users.models import User
from app.users.exceptions import InvalidUserIdException
from .exceptions import VideoAddedException,InvalidYoutubeVideoURLException

settings = get_settings()
from .extrators import extract_video_id

class Video(Model):
    __keyspace__ = settings.keyspace
    host_id = columns.Text(primary_key=True)
    db_id = columns.UUID(primary_key=True, default=uuid.uuid1)
    host_service = columns.Text(default='youtube')
    title = columns.Text()
    url = columns.Text()
    user_id = columns.UUID()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'Video(title={self.title}, host_id={self.host_id}, host_service={self.host_service})'

    def as_data(self):
        return {"title":self.title,f'{self.host_service}_id':self.host_id,
            "path":self.path}

    def render(self):
        basename = self.host_service
        template_path = f'videos/renderers/{basename}.html'
        context = {"host_id":self.host_id}
        t =templates.get_template(template_path)
        return t.render(context)


    @property
    def path(self):
        return f'/videos/{self.host_id}'

        
    @staticmethod
    def add_video(url,title, user_id=None):
        host_id = extract_video_id(url)
        if host_id is None:
            raise InvalidYoutubeVideoURLException

        user_exists = User.check_exists(user_id)
        if not user_exists:
            raise InvalidUserIdException

        q = Video.objects.allow_filtering().filter(host_id = host_id, user_id=user_id)

        if q.count() != 0:
            raise VideoAddedException

        return Video.create(host_id=host_id, title=title ,user_id=user_id,url=url)