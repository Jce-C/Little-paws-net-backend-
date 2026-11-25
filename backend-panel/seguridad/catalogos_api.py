from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .views import VistaSegura
from . import catalogos as c
from .autorizacion import exigir

class CatalogoView(VistaSegura):
    def get(self,request,tipo,pk=None):
        exigir(request.user,'catalogos.ver')
        if tipo not in c.MODELOS:raise ValidationError('Catálogo no disponible.')
        qs=c.MODELOS[tipo].objects.order_by('nombre')
        if request.query_params.get('q'):qs=qs.filter(nombre__icontains=request.query_params['q'][:100])
        def row(o):return {'id':o.pk,**{k:(getattr(o,k+'_id') if k=='especie' else getattr(o,k)) for k in c.CAMPOS[tipo]},'version':c.version(o)}
        if pk:return Response(row(get_object_or_404(qs,pk=pk)))
        from django.core.paginator import Paginator
        p=Paginator(qs,50).get_page(request.query_params.get('pagina'))
        return Response({'total':p.paginator.count,'pagina':p.number,'results':[row(o) for o in p]})
    def post(self,request,tipo,pk=None):
        if tipo not in c.MODELOS:raise ValidationError('Catálogo no disponible.')
        allowed=set(c.CAMPOS[tipo])|{'version'}
        if set(request.data)-allowed:raise ValidationError('Campos de catálogo no reconocidos.')
        obj=c.guardar(request.user,tipo,request.data,pk,request.data.get('version'))
        return Response({'id':obj.pk,'version':c.version(obj)},status=200 if pk else 201)
    def patch(self,request,tipo,pk):
        if tipo not in c.MODELOS:raise ValidationError('Catálogo no disponible.')
        exigir(request.user,'catalogos.editar');obj=get_object_or_404(c.MODELOS[tipo],pk=pk)
        data={k:(getattr(obj,'especie_id') if k=='especie' else getattr(obj,k)) for k in c.CAMPOS[tipo]};data.update(request.data)
        from types import SimpleNamespace
        return self.post(SimpleNamespace(user=request.user,data=data),tipo,pk)
