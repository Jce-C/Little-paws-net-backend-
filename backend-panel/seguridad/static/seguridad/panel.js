"use strict";
const t=globalThis.gettext||((value)=>value);
(() => {
  const $ = (selector, padre=document) => padre.querySelector(selector);
  const nodo = (tag, texto, clase) => { const el=document.createElement(tag); if(texto!==undefined)el.textContent=texto; if(clase)el.className=clase; return el; };
  $("[data-ver-password]")?.addEventListener("click", event => {
    const boton=event.currentTarget, campo=$("#id_password"), visible=campo.type==="password";
    campo.type=visible?"text":"password"; boton.textContent=visible?t("Ocultar"):t("Ver");
    boton.setAttribute("aria-label",visible?t("Ocultar contraseña"):t("Mostrar contraseña")); boton.setAttribute("aria-pressed",String(visible));
  });
  $("[data-menu]")?.addEventListener("click", event => {
    const abierta=$("#navegacion").classList.toggle("abierta"); event.currentTarget.setAttribute("aria-expanded",String(abierta));
  });
  const tabla=$("[data-tabla]"); if(!tabla)return;
  const codigo=tabla.dataset.codigo, csrf=$("meta[name=csrf-token]").content;
  const dialogo=$("#dialogo"), formulario=$("#formulario-dialogo"), campos=$("#dialogo-campos");
  let guardar=null, anterior=null, siguiente=null, direccion=tabla.dataset.endpoint;
  const etiquetas={id_usuario:"ID",id_rol:"ID",id_permiso:"ID",id:"ID",nombre:t("Nombre"),email:t("Correo"),telefono:t("Teléfono"),is_active:t("Estado"),activo:t("Estado"),codigo:t("Código"),ambito:t("Ámbito"),descripcion:t("Descripción"),recurso_codigo:t("Recurso"),alcance:t("Alcance"),fecha:t("Fecha"),accion:t("Acción"),actor_id:t("Actor"),recurso:t("Recurso"),objeto_id:t("Registro"),usuario_id:t("Usuario"),roles:t("Roles"),principal:t("Principal"),estado:t("Estado"),banco:t("Banco"),tipo:t("Tipo"),titular:t("Titular"),ultimos4:t("Terminación"),titulo:t("Título"),texto:t("Contenido"),url:t("Destino"),inicio:t("Inicio"),fin:t("Fin"),id_producto:"ID",precio:t("Precio"),existencias:t("Existencias"),id_caso:"ID",estado_caso__nombre:t("Estado"),fecha_aceptacion:t("Aceptación"),id_fondo:"ID",id_mascota:"ID",autorizacion_hasta:t("Autorización hasta"),detalle:t("Anotación"),enmiendas:t("Enmiendas"),respuestas:t("Respuestas"),versiones:t("Cambios de respuestas"),observaciones:t("Observaciones"),documentos:t("Documentos"),declaraciones:t("Declaraciones"),confirmaciones:t("Confirmaciones"),lineas:t("Productos"),mascota_id:t("Mascota"),entidad_id:t("Organización"),mime:t("Formato"),tamano:t("Tamaño"),creada:t("Fecha"),motivo:t("Motivo"),observacion:t("Observación"),preparador_id:t("Preparado por"),numero:t("Número de cuenta"),estado_producto_id:t("Estado de producto"),anuncio_id:t("Anuncio")};
  const columnas={usuarios:["id_usuario","nombre","email","is_active"],roles:["nombre","codigo","ambito","activo"],recursos:["nombre","codigo","activo"],permisos:["codigo","recurso_codigo","alcance","activo"],auditoria:["fecha","accion","actor_id","recurso","objeto_id"],equipo:["nombre","roles","principal","activo"],cuentas:["id","banco","titular","ultimos4","estado"],publicidad:["id","titulo","estado","inicio","fin"],"revision-publicidad":["id","titulo","texto","inicio","fin"],reclamaciones:["id","estado"],catalogo:["id_producto","nombre","precio","existencias"],rescates:["id_caso","estado_caso__nombre","fecha_aceptacion"],fondos:["id_fondo","nombre"],expedientes:["id_mascota","nombre","autorizacion_hasta"]};
  const vacio=t("No hay registros disponibles en este ámbito.");
  const formato=valor => valor===null||valor===undefined?"—":typeof valor==="boolean"?(valor?t("Sí"):t("No")):Array.isArray(valor)?valor.map(x=>typeof x==="object"?JSON.stringify(x):String(x)).join(" · "):typeof valor==="object"?JSON.stringify(valor,null,2):String(valor);
  const errorTexto=datos => typeof datos==="string"?datos:Object.entries(datos||{}).map(([k,v])=>(etiquetas[k]||k)+": "+formato(v)).join(" · ");
  async function api(url, opciones={}) {
    const destino=new URL(url,location.origin);
    if(destino.origin!==location.origin||!destino.pathname.startsWith("/api/"))throw Error(t("La dirección de la operación no es válida."));
    const respuesta=await fetch(destino,{credentials:"same-origin",...opciones,headers:{"Accept":"application/json",...(opciones.body?{"Content-Type":"application/json","X-CSRFToken":csrf}:{}),...opciones.headers}});
    const datos=await respuesta.json().catch(()=>({detalle:t("No pudimos completar la operación. Actualiza la página.")}));
    if(respuesta.status===401){location.assign("/panel/login/?next="+encodeURIComponent(location.pathname));throw Error(t("Tu sesión terminó. Inicia sesión nuevamente."));}
    if(!respuesta.ok)throw Error(errorTexto(datos)); return datos;
  }
  function toast(texto){const t=$("#toast");t.textContent=texto;t.hidden=false;setTimeout(()=>{t.hidden=true;},6500);}
  function abrir(titulo, funcion){$("#dialogo-titulo").textContent=titulo;campos.replaceChildren();$("#dialogo-error").hidden=true;$("#dialogo-guardar").hidden=!funcion;guardar=funcion;dialogo.showModal();}
  function cerrar(){dialogo.close();formulario.reset();campos.replaceChildren();guardar=null;}
  document.querySelectorAll("[data-cerrar]").forEach(b=>b.addEventListener("click",cerrar));
  dialogo.addEventListener("cancel",()=>{formulario.reset();campos.replaceChildren();guardar=null;});
  formulario.addEventListener("submit",async event=>{event.preventDefault();if(!guardar)return;const boton=$("#dialogo-guardar");boton.disabled=true;try{await guardar();cerrar();toast(t("Cambios guardados."));await cargar();}catch(error){$("#dialogo-error").textContent=error.message;$("#dialogo-error").hidden=false;}finally{boton.disabled=false;}});
  function campo(nombre,label,tipo="text",valor="",opciones){const cont=nodo("div",undefined,"campo"), id="editor-"+nombre; const etiqueta=nodo("label",label);etiqueta.htmlFor=id;cont.append(etiqueta);let input;
    if(opciones){input=nodo("select");for(const [v,t] of opciones){const o=nodo("option",t);o.value=v;input.append(o);}}else{input=nodo("input");input.type=tipo;}
    input.id=id;input.name=nombre;if(tipo==="checkbox"){input.checked=Boolean(valor);}else{input.value=valor??"";}if(tipo==="password")input.autocomplete="new-password";cont.append(input);campos.append(cont);return input;
  }
  function datosFormulario(){const salida={};for(const input of campos.querySelectorAll("[name]"))salida[input.name]=input.type==="checkbox"?input.checked:input.value;return salida;}
  function editar(fila){const nuevo=!fila;const pk=fila?.id_usuario??fila?.id_rol??fila?.id_permiso??fila?.id;abrir(({usuarios:nuevo?t("Crear usuario"):t("Editar usuario"),roles:nuevo?t("Crear rol"):t("Editar rol"),permisos:nuevo?t("Crear permiso"):t("Editar permiso"),recursos:nuevo?t("Crear recurso"):t("Editar recurso")})[codigo],async()=>{const d=datosFormulario();await api(tabla.dataset.endpoint+(nuevo?"":pk+"/"),{method:nuevo?"POST":"PATCH",body:JSON.stringify(d)});});
    if(codigo==="usuarios"){campo("nombre",t("Nombre completo"),"text",fila?.nombre);campo("email",t("Correo electrónico"),"email",fila?.email);campo("telefono",t("Teléfono"),"tel",fila?.telefono);if(nuevo)campo("password",t("Contraseña inicial"),"password");campo("is_active",t("Cuenta activa"),"checkbox",fila?.is_active??true);}
    if(codigo==="roles"){campo("nombre",t("Nombre del rol"),"text",fila?.nombre);if(nuevo){campo("codigo",t("Código del rol"));campo("ambito",t("Ámbito"),"text","ENTIDAD",[["ENTIDAD",t("Una organización")],["GLOBAL",t("Plataforma")]]);campo("delegable",t("Delegable dentro de la organización"),"checkbox",true);}campo("descripcion",t("Descripción"),"text",fila?.descripcion);campo("activo",t("Rol activo"),"checkbox",fila?.activo??true);}
    if(codigo==="recursos"){campo("nombre",t("Nombre del recurso"),"text",fila?.nombre);if(nuevo)campo("codigo",t("Código del recurso"));campo("descripcion",t("Descripción"),"text",fila?.descripcion);campo("activo",t("Recurso activo"),"checkbox",fila?.activo??true);}
    if(codigo==="permisos"){campos.append(nodo("p",`${fila.codigo} · ${fila.alcance}. ${t("La acción y su alcance están definidos por el servidor.")}`));campo("descripcion",t("Descripción"),"text",fila.descripcion);campo("activo",t("Permiso activo"),"checkbox",fila.activo);}
  }
  async function matriz(fila){try{const editable=tabla.dataset.editar==="true",asignados=await api(`/api/seguridad/roles/${fila.id_rol}/permisos/`),catalogo=editable?await api("/api/seguridad/permisos/?limite=100"):{results:asignados};
    abrir(interpolate(t("Permisos de %(nombre)s"),{nombre:fila.nombre},true),editable?async()=>{const ids=Array.from(campos.querySelectorAll("input:checked")).map(x=>Number(x.value));await api(`/api/seguridad/roles/${fila.id_rol}/permisos/`,{method:"POST",body:JSON.stringify({permisos:ids})});}:null);
    campos.append(nodo("p",t("Las acciones y los alcances se validan al guardar. Los roles del sistema conservan sus límites.")));
    const seleccionados=new Set(asignados.map(x=>x.id_permiso));for(const p of catalogo.results){const label=nodo("label",undefined,"asignacion"), input=nodo("input");input.type="checkbox";input.value=p.id_permiso;input.checked=seleccionados.has(p.id_permiso);input.disabled=!editable;label.append(input,nodo("span",`${p.codigo} · ${p.alcance}`));campos.append(label);}
  }catch(e){toast(e.message);}}
  async function rolesUsuario(fila){try{const catalogo=await api("/api/seguridad/roles/?limite=100");abrir(t("Asignar o revocar un rol global"),async()=>{const d=datosFormulario();await api(`/api/seguridad/usuarios/${fila.id_usuario}/roles-globales/`,{method:"POST",body:JSON.stringify({rol_id:Number(d.rol_id),revocar:d.revocar,motivo:d.motivo})});});campos.append(nodo("p",fila.nombre+" · "+fila.email));campo("rol_id",t("Rol global"),"text","",catalogo.results.filter(r=>r.ambito==="GLOBAL"&&r.activo).map(r=>[String(r.id_rol),r.nombre]));campo("revocar",t("Revocar este rol"),"checkbox",false);campo("motivo",t("Motivo"));}catch(e){toast(e.message);}}
  function mostrarDetalle(datos,titulo=t("Detalle autorizado")){abrir(titulo,null);for(const [k,v] of Object.entries(datos)){const div=nodo("div",undefined,"detalle-fila");div.append(nodo("strong",etiquetas[k]||k),nodo("span",formato(v)));campos.append(div);}}
  async function abrirPrivado(recurso,id){try{const d=await api(`/api/seguridad/operaciones/registros/${recurso}/${id}/`);mostrarDetalle(d);}catch(e){toast(e.message);}}
  async function trabajo(){if(!tabla.dataset.cola)return;const area=$("#mi-trabajo");try{const d=await api("/api/seguridad/operaciones/mis-registros/");area.replaceChildren();const asignadas=d.asignaciones.filter(a=>a.recurso__codigo===tabla.dataset.cola&&!a.fecha_revocacion);for(const a of asignadas){const cont=nodo("div",undefined,"asignacion");cont.append(nodo("span",t("Solicitud #")+a.objeto_id));const b=nodo("button",t("Abrir"),"boton secundario pequeno");b.type="button";b.addEventListener("click",()=>abrirPrivado(a.recurso__codigo,a.objeto_id));cont.append(b);area.append(cont);}if(!asignadas.length)area.append(nodo("p",t("Todavía no tienes solicitudes asignadas en este módulo.")));}catch(e){area.textContent=e.message;}}
  async function cargar(url=direccion){$("#estado-tabla").textContent=t("Actualizando…");try{let datos;if(url){datos=await api(url);direccion=url;}else datos=JSON.parse($("#datos-iniciales").textContent)||[];
    const filas=Array.isArray(datos)?datos:datos.results||[];anterior=datos.previous||null;siguiente=datos.next||null;$("[data-anterior]").hidden=!anterior;$("[data-siguiente]").hidden=!siguiente;
    $("#conteo").textContent=String(datos.count??filas.length);const cols=tabla.dataset.cola?["id","recurso"]:columnas[codigo]||["id","estado"];const head=nodo("tr");for(const c of cols){const th=nodo("th",etiquetas[c]||c);th.scope="col";if(["id","id_usuario","precio","existencias"].includes(c))th.className="dato-numero";head.append(th);}const actionHeader=nodo("th",t("Acciones"));actionHeader.scope="col";head.append(actionHeader);$("#columnas").replaceChildren(head);$("#filas").replaceChildren();
    if(!filas.length){const tr=nodo("tr"),td=nodo("td",undefined,"tabla-vacia");td.colSpan=cols.length+1;td.append(nodo("strong",t("Todo en orden por aquí.")),nodo("span",vacio));tr.append(td);$("#filas").append(tr);}
    for(const fila of filas){const tr=nodo("tr");for(const c of cols){const td=nodo("td");if(["nombre","titulo"].includes(c))td.className="dato-principal";else if(["id","id_usuario","precio","existencias"].includes(c))td.className="dato-numero";if(["is_active","activo"].includes(c)){td.append(nodo("span",fila[c]?t("Activo"):t("Inactivo"),"estado-tag"+(fila[c]?"":" inactivo")));}else td.textContent=formato(fila[c]);tr.append(td);}const acciones=nodo("td");
      const boton=(texto,fn)=>{const b=nodo("button",texto,"boton secundario pequeno");b.type="button";b.addEventListener("click",fn);acciones.append(b,document.createTextNode(" "));};
      if(tabla.dataset.cola){boton(t("Tomar solicitud"),async()=>{try{await api(`/api/seguridad/asignaciones/${tabla.dataset.cola}/${fila.id}/tomar/`,{method:"POST",body:"{}"});toast(t("Solicitud asignada a tu cuenta."));await cargar();}catch(e){toast(e.message);}});}
      else if(["usuarios","roles","recursos","permisos"].includes(codigo)){if(tabla.dataset.editar==="true")boton(t("Editar"),()=>editar(fila));else boton(t("Detalle"),()=>mostrarDetalle(fila));if(codigo==="roles")boton(t("Permisos"),()=>matriz(fila));if(codigo==="usuarios"&&tabla.dataset.asignarRoles==="true")boton(t("Roles"),()=>rolesUsuario(fila));}
      else if(codigo==="expedientes")boton(t("Abrir"),()=>abrirPrivado("expediente",fila.id_mascota));
      else if(codigo==="cuentas")boton(t("Ver propuesta"),async()=>{try{mostrarDetalle(await api(`/api/seguridad/operaciones/propuestas-cuenta/${fila.id}/`),t("Propuesta de cuenta"));}catch(e){toast(e.message);}});
      else boton(t("Detalle"),()=>mostrarDetalle(fila));
      tr.append(acciones);$("#filas").append(tr);
    }$("#estado-tabla").textContent=t("Mostrando solo los registros disponibles para tu cuenta.");await trabajo();
  }catch(e){$("#estado-tabla").textContent=e.message;$("#filas").replaceChildren();const tr=nodo("tr"),td=nodo("td",e.message,"tabla-vacia");td.colSpan=10;tr.append(td);$("#filas").append(tr);}}
  $("[data-crear]")?.addEventListener("click",()=>editar(null));$("[data-actualizar]").addEventListener("click",()=>cargar());$("[data-anterior]").addEventListener("click",()=>{if(anterior)cargar(anterior);});$("[data-siguiente]").addEventListener("click",()=>{if(siguiente)cargar(siguiente);});
  cargar();
})();
