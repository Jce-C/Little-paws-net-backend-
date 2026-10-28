
const config=JSON.parse(document.querySelector('#vista-config').textContent);
const fixtures=JSON.parse(document.querySelector('#vista-fixtures').textContent);
const originalFetch=window.fetch.bind(window);
window.fetch=async function(url,options={}){
 const u=new URL(url,location.origin);
 if(u.origin!==location.origin||!u.pathname.startsWith('/api/'))return originalFetch(url,options);
 const method=(options.method||'GET').toUpperCase();
 if(method!=='GET')return new Response(JSON.stringify({detalle:'Esta es una vista de diseño. Los cambios no se guardan.'}),{status:403,headers:{'Content-Type':'application/json'}});
 let data=fixtures[config.module]||[];
 if(u.pathname.includes('/mis-registros/'))data={asignaciones:[]};
 else if(/\/roles\/\d+\/permisos\//.test(u.pathname))data=fixtures.permisos.slice(0,3);
 else if(u.pathname==='/api/seguridad/permisos/')data={results:fixtures.permisos,count:fixtures.permisos.length};
 else if(u.pathname==='/api/seguridad/roles/')data={results:fixtures.roles,count:fixtures.roles.length};
 else if(!Array.isArray(data)){}
 else data={results:data,count:data.length,next:null,previous:null};
 return new Response(JSON.stringify(data),{status:200,headers:{'Content-Type':'application/json'}});
};
document.addEventListener('DOMContentLoaded',()=>{
 document.querySelector('#preview-profile').value=config.profile;
 document.querySelector('#preview-profile').addEventListener('change',e=>location.assign('/perfiles/'+e.target.value+'/'));
 document.querySelectorAll('form').forEach(form=>{
  if(form.id==='formulario-dialogo')return;
  form.addEventListener('submit',e=>{e.preventDefault();if(form.querySelector('.salir')){location.assign('/acceso/?estado=salida#ingreso');return;}const toast=document.querySelector('#toast');if(toast){toast.textContent='Vista de diseño: esta acción no cambia cuentas ni datos.';toast.hidden=false;}});
 });
});
