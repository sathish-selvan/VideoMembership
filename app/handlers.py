from starlette.exceptions import HTTPException as StarletteHTTPException
from .users.exceptions import LoginRequiredException

from app.main import app
from app.shortcuts import redirect, render

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    status_code = exc.status_code
    template_name = 'errors/main.html'
    if status_code == 404:
        template_name = 'errors/404.html'
    context = {"status_code": status_code}
    return render(request, template_name, context, status_code=status_code)


@app.exception_handler(LoginRequiredException)
async def lofin_required_exception_handler(request, exc):
    return redirect(f'/login?next={request.url}', remove_session=True)


