"use strict";
(() => {
  const $ = (selector, padre=document) => padre.querySelector(selector);
  const nodo = (tag, texto, clase) => { const el=document.createElement(tag); if(texto!==undefined)el.textContent=texto; if(clase)el.className=clase; return el; };
  $("[data-ver-password]")?.addEventListener("click", event => {
    const boton=event.currentTarget, campo=$("#id_password"), visible=campo.type==="password";
    campo.type=visible?"text":"password"; boton.textContent=visible?"Ocultar":"Ver";
    boton.setAttribute("aria-label",visible?"Ocultar contraseña":"Mostrar contraseña"); boton.setAttribute("aria-pressed",String(visible));
  });
  $("[data-menu]")?.addEventListener("click", event => {
    const abierta=$("#navegacion").classList.toggle("abierta"); event.currentTarget.setAttribute("aria-expanded",String(abierta));
  });
  const tabla=$("[data-tabla]"); if(!tabla)return;
  const codigo=tabla.dataset.codigo, csrf=$("meta[name=csrf-token]").content;
  const dialogo=$("#dialogo"), formulario=$("#formulario-dialogo"), campos=$("#dialogo-campos");
  let guardar=null, anterior=null, siguiente=null, direccion=tabla.dataset.endpoint;
  const etiquetas={id_usuario:"ID",id_rol:"ID",id_permiso:"ID",id:"ID",nombre:"Nombre",email:"Correo",telefono:"Teléfono",is_active:"Estado",activo:"Estado",codigo:"Código",ambito:"Ámbito",descripcion:"Descripción",recurso_codigo:"Recurso",alcance:"Alcance",fecha:"Fecha",accion:"Acción",actor_id:"Actor",recurso:"Recurso",objeto_id:"Registro",usuario_id:"Usuario",roles:"Roles",principal:"Principal",estado:"Estado",banco:"Banco",tipo:"Tipo",titular:"Titular",ultimos4:"Terminación",titulo:"Título",texto:"Contenido",url:"Destino",inicio:"Inicio",fin:"Fin",id_producto:"ID",precio:"Precio",existencias:"Existencias",id_caso:"ID",estado_caso__nombre:"Estado",fecha_aceptacion:"Aceptación",id_fondo:"ID",id_mascota:"ID",autorizacion_hasta:"Autorización hasta",detalle:"Anotación",enmiendas:"Enmiendas",respuestas:"Respuestas",versiones:"Cambios de respuestas",observaciones:"Observaciones",documentos:"Documentos",declaraciones:"Declaraciones",confirmaciones:"Confirmaciones",lineas:"Productos",mascota_id:"Mascota",entidad_id:"Organización",mime:"Formato",tamano:"Tamaño",creada:"Fecha",motivo:"Motivo",observacion:"Observación",preparador_id:"Preparado por",numero:"Número de cuenta",estado_producto_id:"Estado de producto",anuncio_id:"Anuncio"};
  const columnas={usuarios:["id_usuario","nombre","email","is_active"],roles:["nombre","codigo","ambito","activo"],recursos:["nombre","codigo","activo"],permisos:["codigo","recurso_codigo","alcance","activo"],auditoria:["fecha","accion","actor_id","recurso","objeto_id"],equipo:["nombre","roles","principal","activo"],cuentas:["id","banco","titular","ultimos4","estado"],publicidad:["id","titulo","estado","inicio","fin"],"revision-publicidad":["id","titulo","texto","inicio","fin"],reclamaciones:["id","estado"],catalogo:["id_producto","nombre","precio","existencias"],rescates:["id_caso","estado_caso__nombre","fecha_aceptacion"],fondos:["id_fondo","nombre"],expedientes:["id_mascota","nombre","autorizacion_hasta"]};
  const vacio="No hay registros disponibles en este ámbito.";
  const formato=valor => valor===null||valor===undefined?"—":typeof valor==="boolean"?(valor?"Sí":"No"):Array.isArray(valor)?valor.map(x=>typeof x==="object"?JSON.stringify(x):String(x)).join(" · "):typeof valor==="object"?JSON.stringify(valor,null,2):String(valor);
  const errorTexto=datos => typeof datos==="string"?datos:Object.entries(datos||{}).map(([k,v])=>(etiquetas[k]||k)+": "+formato(v)).join(" · ");
  async function api(url, opciones={}) {
    const destino=new URL(url,location.origin);
    if(destino.origin!==location.origin||!destino.pathname.startsWith("/api/"))throw Error("La dirección de la operación no es válida.");
    const respuesta=await fetch(destino,{credentials:"same-origin",...opciones,headers:{"Accept":"application/json",...(opciones.body?{"Content-Type":"application/json","X-CSRFToken":csrf}:{}),...opciones.headers}});
    const datos=await respuesta.json().catch(()=>({detalle:"No pudimos completar la operación. Actualiza la página."}));
    if(respuesta.status===401){location.assign("/panel/login/?next="+encodeURIComponent(location.pathname));throw Error("Tu sesión terminó. Inicia sesión nuevamente.");}
    if(!respuesta.ok)throw Error(errorTexto(datos)); return datos;
  }
  function toast(texto){const t=$("#toast");t.textContent=texto;t.hidden=false;setTimeout(()=>{t.hidden=true;},6500);}
  function abrir(titulo, funcion){$("#dialogo-titulo").textContent=titulo;campos.replaceChildren();$("#dialogo-error").hidden=true;$("#dialogo-guardar").hidden=!funcion;guardar=funcion;dialogo.showModal();}
  function cerrar(){dialogo.close();formulario.reset();campos.replaceChildren();guardar=null;}
  document.querySelectorAll("[data-cerrar]").forEach(b=>b.addEventListener("click",cerrar));
  dialogo.addEventListener("cancel",()=>{formulario.reset();campos.replaceChildren();guardar=null;});
  formulario.addEventListener("submit",async event=>{event.preventDefault();if(!guardar)return;const boton=$("#dialogo-guardar");boton.disabled=true;try{await guardar();cerrar();toast("Cambios guardados.");await cargar();}catch(error){$("#dialogo-error").textContent=error.message;$("#dialogo-error").hidden=false;}finally{boton.disabled=false;}});
  function campo(nombre,label,tipo="text",valor="",opciones){const cont=nodo("div",undefined,"campo"), id="editor-"+nombre; const etiqueta=nodo("label",label);etiqueta.htmlFor=id;cont.append(etiqueta);let input;
    if(opciones){input=nodo("select");for(const [v,t] of opciones){const o=nodo("option",t);o.value=v;input.append(o);}}else{input=nodo("input");input.type=tipo;}
    input.id=id;input.name=nombre;if(tipo==="checkbox"){input.checked=Boolean(valor);}else{input.value=valor??"";}if(tipo==="password")input.autocomplete="new-password";cont.append(input);campos.append(cont);return input;
  }
  function datosFormulario(){const salida={};for(const input of campos.querySelectorAll("[name]"))salida[input.name]=input.type==="checkbox"?input.checked:input.value;return salida;}
  function editar(fila){const nuevo=!fila;const pk=fila?.id_usuario??fila?.id_rol??fila?.id;abrir((nuevo?"Crear ":"Editar ")+(codigo==="usuarios"?"usuario":codigo==="roles"?"rol":"recurso"),async()=>{const d=datosFormulario();await api(tabla.dataset.endpoint+(nuevo?"":pk+"/"),{method:nuevo?"POST":"PATCH",body:JSON.stringify(d)});});
    if(codigo==="usuarios"){campo("nombre","Nombre completo","text",fila?.nombre);campo("email","Correo electrónico","email",fila?.email);campo("telefono","Teléfono","tel",fila?.telefono);if(nuevo)campo("password","Contraseña inicial","password");campo("is_active","Cuenta activa","checkbox",fila?.is_active??true);}
    if(codigo==="roles"){campo("nombre","Nombre del rol","text",fila?.nombre);if(nuevo){campo("codigo","Código del rol");campo("ambito","Ámbito","text","ENTIDAD",[["ENTIDAD","Una organización"],["GLOBAL","Plataforma"]]);campo("delegable","Delegable dentro de la organización","checkbox",true);}campo("descripcion","Descripción","text",fila?.descripcion);campo("activo","Rol activo","checkbox",fila?.activo??true);}
    if(codigo==="recursos"){campo("nombre","Nombre del recurso","text",fila?.nombre);if(nuevo)campo("codigo","Código del recurso");campo("descripcion","Descripción","text",fila?.descripcion);campo("activo","Recurso activo","checkbox",fila?.activo??true);}
  }
  async function matriz(fila){try{const [asignados,catalogo]=await Promise.all([api(`/api/seguridad/roles/${fila.id_rol}/permisos/`),api("/api/seguridad/permisos/?limite=100")]);
    abrir("Permisos de "+fila.nombre,async()=>{const ids=Array.from(campos.querySelectorAll("input:checked")).map(x=>Number(x.value));await api(`/api/seguridad/roles/${fila.id_rol}/permisos/`,{method:"POST",body:JSON.stringify({permisos:ids})});});
    campos.append(nodo("p","Las acciones y los alcances se validan al guardar. Los roles del sistema conservan sus límites."));
    const seleccionados=new Set(asignados.map(x=>x.id_permiso));for(const p of catalogo.results){const label=nodo("label",undefined,"asignacion"), input=nodo("input");input.type="checkbox";input.value=p.id_permiso;input.checked=seleccionados.has(p.id_permiso);label.append(input,nodo("span",`${p.codigo} · ${p.alcance}`));campos.append(label);}
  }catch(e){toast(e.message);}}
  async function rolesUsuario(fila){try{const catalogo=await api("/api/seguridad/roles/?limite=100");abrir("Asignar o revocar un rol global",async()=>{const d=datosFormulario();await api(`/api/seguridad/usuarios/${fila.id_usuario}/roles-globales/`,{method:"POST",body:JSON.stringify({rol_id:Number(d.rol_id),revocar:d.revocar,motivo:d.motivo})});});campos.append(nodo("p",fila.nombre+" · "+fila.email));campo("rol_id","Rol global","text","",catalogo.results.filter(r=>r.ambito==="GLOBAL"&&r.activo).map(r=>[String(r.id_rol),r.nombre]));campo("revocar","Revocar este rol","checkbox",false);campo("motivo","Motivo");}catch(e){toast(e.message);}}
  function mostrarDetalle(datos,titulo="Detalle autorizado"){abrir(titulo,null);for(const [k,v] of Object.entries(datos)){const div=nodo("div",undefined,"detalle-fila");div.append(nodo("strong",etiquetas[k]||k),nodo("span",formato(v)));campos.append(div);}}
  async function abrirPrivado(recurso,id){try{const d=await api(`/api/seguridad/operaciones/registros/${recurso}/${id}/`);mostrarDetalle(d);}catch(e){toast(e.message);}}
  async function trabajo(){if(!tabla.dataset.cola)return;const area=$("#mi-trabajo");try{const d=await api("/api/seguridad/operaciones/mis-registros/");area.replaceChildren();const asignadas=d.asignaciones.filter(a=>a.recurso__codigo===tabla.dataset.cola&&!a.fecha_revocacion);for(const a of asignadas){const cont=nodo("div",undefined,"asignacion");cont.append(nodo("span","Solicitud #"+a.objeto_id));const b=nodo("button","Abrir","boton secundario pequeno");b.type="button";b.addEventListener("click",()=>abrirPrivado(a.recurso__codigo,a.objeto_id));cont.append(b);area.append(cont);}if(!asignadas.length)area.append(nodo("p","Todavía no tienes solicitudes asignadas en este módulo."));}catch(e){area.textContent=e.message;}}
  async function cargar(url=direccion){$("#estado-tabla").textContent="Actualizando…";try{let datos;if(url){datos=await api(url);direccion=url;}else datos=JSON.parse($("#datos-iniciales").textContent)||[];
    const filas=Array.isArray(datos)?datos:datos.results||[];anterior=datos.previous||null;siguiente=datos.next||null;$("[data-anterior]").hidden=!anterior;$("[data-siguiente]").hidden=!siguiente;
    $("#conteo").textContent=String(datos.count??filas.length);const cols=tabla.dataset.cola?["id","recurso"]:columnas[codigo]||["id","estado"];const head=nodo("tr");for(const c of cols){const th=nodo("th",etiquetas[c]||c);th.scope="col";if(["id","id_usuario","precio","existencias"].includes(c))th.className="dato-numero";head.append(th);}const actionHeader=nodo("th","Acciones");actionHeader.scope="col";head.append(actionHeader);$("#columnas").replaceChildren(head);$("#filas").replaceChildren();
    if(!filas.length){const tr=nodo("tr"),td=nodo("td",undefined,"tabla-vacia");td.colSpan=cols.length+1;td.append(nodo("strong","Todo en orden por aquí."),nodo("span",vacio));tr.append(td);$("#filas").append(tr);}
    for(const fila of filas){const tr=nodo("tr");for(const c of cols){const td=nodo("td");if(["nombre","titulo"].includes(c))td.className="dato-principal";else if(["id","id_usuario","precio","existencias"].includes(c))td.className="dato-numero";if(["is_active","activo"].includes(c)){td.append(nodo("span",fila[c]?"Activo":"Inactivo","estado-tag"+(fila[c]?"":" inactivo")));}else td.textContent=formato(fila[c]);tr.append(td);}const acciones=nodo("td");
      const boton=(texto,fn)=>{const b=nodo("button",texto,"boton secundario pequeno");b.type="button";b.addEventListener("click",fn);acciones.append(b,document.createTextNode(" "));};
      if(tabla.dataset.cola){boton("Tomar solicitud",async()=>{try{await api(`/api/seguridad/asignaciones/${tabla.dataset.cola}/${fila.id}/tomar/`,{method:"POST",body:"{}"});toast("Solicitud asignada a tu cuenta.");await cargar();}catch(e){toast(e.message);}});}
      else if(["usuarios","roles","recursos"].includes(codigo)){boton("Editar",()=>editar(fila));if(codigo==="roles")boton("Permisos",()=>matriz(fila));if(codigo==="usuarios")boton("Roles",()=>rolesUsuario(fila));}
      else if(codigo==="expedientes")boton("Abrir",()=>abrirPrivado("expediente",fila.id_mascota));
      else if(codigo==="cuentas")boton("Ver propuesta",async()=>{try{mostrarDetalle(await api(`/api/seguridad/operaciones/propuestas-cuenta/${fila.id}/`),"Propuesta de cuenta");}catch(e){toast(e.message);}});
      else boton("Detalle",()=>mostrarDetalle(fila));
      tr.append(acciones);$("#filas").append(tr);
    }$("#estado-tabla").textContent="Mostrando solo los registros disponibles para tu cuenta.";await trabajo();
  }catch(e){$("#estado-tabla").textContent=e.message;$("#filas").replaceChildren();const tr=nodo("tr"),td=nodo("td",e.message,"tabla-vacia");td.colSpan=10;tr.append(td);$("#filas").append(tr);}}
  $("[data-crear]")?.addEventListener("click",()=>editar(null));$("[data-actualizar]").addEventListener("click",()=>cargar());$("[data-anterior]").addEventListener("click",()=>{if(anterior)cargar(anterior);});$("[data-siguiente]").addEventListener("click",()=>{if(siguiente)cargar(siguiente);});
  cargar();
})();
