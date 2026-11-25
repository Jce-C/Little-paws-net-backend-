from asgiref.sync import iscoroutinefunction
from django.utils.decorators import sync_and_async_middleware
from .autorizacion import _cache


@sync_and_async_middleware
def MotorMiddleware(get_response):
    if iscoroutinefunction(get_response):
        async def middleware(request):
            token = _cache.set({})
            try:
                return await get_response(request)
            finally:
                _cache.reset(token)
    else:
        def middleware(request):
            token = _cache.set({})
            try:
                return get_response(request)
            finally:
                _cache.reset(token)
    return middleware
