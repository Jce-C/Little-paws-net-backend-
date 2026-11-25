"""SSE en ASGI. Un lector de revisión por proceso, no uno por cliente conectado."""
import asyncio
import json
import time
import logging
from asgiref.sync import sync_to_async
from django.db import close_old_connections
from django.http import StreamingHttpResponse, JsonResponse
from .models import RevisionPanel


def revision():
    return RevisionPanel.objects.filter(pk=1).values_list('version',flat=True).first() or 0


class Hub:
    def __init__(self):
        self.version=None
        self.condition=asyncio.Condition()
        self.clients=0
        self.task=None

    async def leer(self):
        def consulta():
            close_old_connections()
            try:
                return revision()
            finally:
                close_old_connections()
        return await sync_to_async(consulta,thread_sensitive=False)()

    async def run(self):
        try:
            while self.clients:
                try:
                    version=await self.leer()
                except Exception:
                    logging.getLogger(__name__).exception('No se pudo leer la revisión del panel; se reintentará')
                    await asyncio.sleep(2)
                    continue
                if version!=self.version:
                    self.version=version
                    async with self.condition:
                        self.condition.notify_all()
                await asyncio.sleep(1)
        finally:
            self.task=None

    async def stream(self):
        self.clients+=1
        if self.task is None:
            self.task=asyncio.create_task(self.run())
        anterior=None
        try:
            yield 'retry: 2000\n\n'
            while True:
                if self.version is not None and self.version!=anterior:
                    anterior=self.version
                    yield 'event: revision\ndata: '+json.dumps({'revision':anterior})+'\n\n'
                timeout=False
                async with self.condition:
                    try:
                        await asyncio.wait_for(self.condition.wait(),timeout=15)
                    except asyncio.TimeoutError:
                        timeout=True
                if timeout:yield 'event: verificar\ndata: {}\n\n'
        finally:
            self.clients-=1


_hubs={}


async def eventos(request):
    if not hasattr(request,'scope'):
        return JsonResponse({'detalle':'La sincronización requiere ASGI: inicia el panel con Uvicorn.'},status=503)
    user=await request.auser()
    if not user.is_authenticated:
        return JsonResponse({'detalle':'Inicia sesión'},status=401)
    from accounts.models import Usuario
    if not await Usuario.objects.filter(pk=user.pk,is_active=True,debe_cambiar_clave=False).aexists():
        return JsonResponse({'detalle':'Cuenta no disponible'},status=401)
    loop=asyncio.get_running_loop()
    hub=_hubs.setdefault(loop,Hub())
    response=StreamingHttpResponse(hub.stream(),content_type='text/event-stream')
    response['Cache-Control']='no-store'
    response['X-Accel-Buffering']='no'
    return response
