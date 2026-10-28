const states={
 incorrecto:{title:'Revisemos esos datos',copy:'El correo, la contraseña o la suma no coinciden. Revisa los campos e inténtalo de nuevo.',icon:'triangle-alert'},
 validando:{title:'Preparando tu espacio',copy:'Estamos verificando el acceso y las herramientas disponibles para tu cuenta.',icon:'refresh-cw'},
 pendiente:{title:'Tu acceso está pendiente',copy:'Tu cuenta todavía no tiene acceso al panel. Consulta al responsable de tu organización para conocer el siguiente paso.',icon:'timer'},
 bloqueado:{title:'Hagamos una pausa',copy:'Se han realizado varios intentos sin éxito. Espera antes de volver a intentarlo. Si necesitas ayuda, contacta al responsable de tu organización.',icon:'lock-keyhole'},
 expirado:{title:'Tu sesión terminó',copy:'Para proteger tu información, vuelve a iniciar sesión. Los cambios que no hayas guardado podrían perderse.',icon:'timer'},
 prohibido:{title:'Este espacio requiere otro permiso',copy:'Tu perfil no tiene autorización para realizar esta acción. Regresa a tus herramientas o consulta al responsable de tu organización.',icon:'shield-check'},
 recuperar:{title:'Recupera tu acceso',copy:'En la versión conectada podrás solicitar instrucciones de recuperación. La respuesta será la misma exista o no una cuenta, para proteger la privacidad. En esta demo no se envían correos.',icon:'mail'},
 sinconexion:{title:'No pudimos conectar',copy:'Comprueba tu conexión e inténtalo de nuevo. No se confirmó ninguna operación.',icon:'refresh-cw'},
 salida:{title:'Hasta pronto',copy:'Has salido del recorrido del panel. Puedes volver a explorar otro perfil cuando quieras.',icon:'circle-check'}
};
const dialog=document.querySelector('#state-dialog');
function openState(key){const state=states[key];if(!state||!dialog)return;document.querySelector('#state-title').textContent=state.title;document.querySelector('#state-copy').textContent=state.copy;document.querySelector('#state-icon-use').setAttribute('href','/static/seguridad/icons.svg#'+state.icon);if(!dialog.open)dialog.showModal();}
document.querySelectorAll('[data-state]').forEach(el=>el.addEventListener('click',()=>openState(el.dataset.state)));
dialog?.querySelectorAll('.close,#state-action').forEach(el=>el.addEventListener('click',()=>dialog.close()));
const clouds=document.querySelector('.clouds');
if(clouds){
 // El lado corresponde al borde plano real de cada SVG. Nunca se invierte
 // hacia el centro ni se deja que el movimiento cruce el anclaje lateral.
 const positions=[['right',8,28],['left',14,26],['left',47,28],['left',78,30],['right',55,35],['right',83,30]];
 positions.forEach(([side,y,w],i)=>{const el=document.createElement('div');el.className='cloud side-'+side;el.dataset.side=side;el.dataset.asset=String(i+1);el.style.cssText=`--y:${y}%;--w:${w}vw;--duration:${14+i*2}s;--delay:${i*100}ms;--arrive-x:${side==='left'?'-':'+'}72px`;const art=document.createElement('div');art.className='cloud-art';const img=document.createElement('img');img.src=`/static/acceso/nube-${i+1}.svg`;img.alt='';img.decoding='async';art.append(img);el.append(art);clouds.append(el);});
 const reduced=matchMedia('(prefers-reduced-motion: reduce)'),hero=document.querySelector('.hero');let frame=0,heroHeight=hero.offsetHeight,entered=0;
 const smooth=(a,b,t)=>{const v=Math.max(0,Math.min(1,(t-a)/(b-a)));return v*v*(3-2*v);};
 function draw(){frame=0;const p=Math.min(1,Math.max(0,scrollY/heroHeight));entered=Math.max(entered,smooth(0,.65,p));clouds.querySelectorAll('.cloud').forEach(el=>{const sign=el.dataset.side==='left'?-1:1;const offset=(1-entered)*Math.min(100,innerWidth*.1);el.style.transform=reduced.matches?'none':`translate3d(${sign*offset}px,0,0)`;});}
 const measure=()=>{heroHeight=hero.offsetHeight;clouds.style.height=heroHeight+'px';if(!frame)frame=requestAnimationFrame(draw);};
 if('ResizeObserver'in window)new ResizeObserver(measure).observe(hero);else addEventListener('resize',measure,{passive:true});measure();
 addEventListener('scroll',()=>{if(!frame&&!reduced.matches)frame=requestAnimationFrame(draw);},{passive:true});reduced.addEventListener('change',draw);
 if(!reduced.matches&&'IntersectionObserver'in window){
  document.body.classList.add('motion-ready');
  const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-visible');observer.unobserve(entry.target);}}),{threshold:.12});
  const loaded=document.readyState==='complete'?Promise.resolve():new Promise(resolve=>addEventListener('load',resolve,{once:true}));
  const ready=Promise.all([loaded,document.fonts?.ready||Promise.resolve()]);
  // No reproducir la entrada mientras todavía se están decodificando fondo y fuentes.
  Promise.race([ready,new Promise(resolve=>setTimeout(resolve,2000))]).then(()=>requestAnimationFrame(()=>requestAnimationFrame(()=>{
   document.body.classList.add('motion-started');
   document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));
  })));
 }
 document.querySelectorAll('a[href="#ingreso"]').forEach(el=>el.addEventListener('click',()=>document.querySelector('#ingreso').focus({preventScroll:true})));
}
const form=document.querySelector('#login-form');
if(form){const email=document.querySelector('#email'),password=document.querySelector('#password'),answer=document.querySelector('#answer'),feedback=document.querySelector('#form-feedback'),submit=document.querySelector('#submit-login'),profile=document.querySelector('#demo-profile');
 const profiles=[{"id": "admin_seguridad", "name": "Administrador de seguridad", "accent": "#4F6655", "soft": "#E2E9DA"}, {"id": "moderador", "name": "Moderador de plataforma", "accent": "#47656C", "soft": "#E0E9EA"}, {"id": "responsable_principal", "name": "Responsable principal", "accent": "#624A36", "soft": "#EBDDCC"}, {"id": "responsable_secundario", "name": "Responsable secundario", "accent": "#965331", "soft": "#F1DDCC"}, {"id": "gestor_rescates", "name": "Gestor de rescates", "accent": "#795B20", "soft": "#F2E6BF"}, {"id": "gestor_adopciones", "name": "Gestor de adopciones", "accent": "#6E642B", "soft": "#EBE8C7"}, {"id": "gestor_aportes", "name": "Gestor de aportes", "accent": "#856227", "soft": "#F3E4C5"}, {"id": "gestor_catalogo", "name": "Gestor de catálogo", "accent": "#7D6844", "soft": "#EDE4CF"}, {"id": "gestor_pedidos", "name": "Gestor de pedidos", "accent": "#8B5F35", "soft": "#F0DEC3"}, {"id": "gestor_fondo", "name": "Gestor de fondo", "accent": "#62633A", "soft": "#E8E6CF"}, {"id": "gestor_publicidad", "name": "Gestor de publicidad", "accent": "#826C19", "soft": "#F2E9BC"}, {"id": "veterinario", "name": "Veterinario verificado", "accent": "#456D61", "soft": "#DDEAE2"}, {"id": "preparador_cuentas", "name": "Preparador delegado de cuentas", "accent": "#74604F", "soft": "#ECE2D8"}];
 profiles.forEach(p=>{const option=document.createElement('option');option.value=p.id;option.textContent=p.name;profile.append(option);});
 document.querySelector('#fill-demo').addEventListener('click',()=>{email.value='demo@example.invalid';password.value='DemoLittlePaws';answer.value='7';feedback.hidden=true;submit.focus({preventScroll:true});});
 document.querySelector('#show-password').addEventListener('click',e=>{const button=e.currentTarget,show=password.type==='password';password.type=show?'text':'password';button.setAttribute('aria-pressed',String(show));button.setAttribute('aria-label',show?'Ocultar contraseña':'Mostrar contraseña');button.querySelector('use').setAttribute('href','/static/seguridad/icons.svg#'+(show?'eye-off':'eye'));});
 form.addEventListener('submit',event=>{event.preventDefault();feedback.hidden=true;[email,password,answer].forEach(el=>el.removeAttribute('aria-invalid'));
 let invalid=null,message='';if(email.value.trim()!=='demo@example.invalid'||password.value!=='DemoLittlePaws'){invalid=email;message='Esta es una demostración. Pulsa «Usar datos de ejemplo» para continuar.';}else if(answer.value.trim()!=='7'){invalid=answer;message='La respuesta no coincide. Revisa la suma 4 + 3.';}
 if(invalid){feedback.textContent=message;feedback.hidden=false;invalid.setAttribute('aria-invalid','true');invalid.setAttribute('aria-describedby','form-feedback');invalid.focus();return;}
 submit.disabled=true;submit.textContent='Preparando tu espacio…';setTimeout(()=>location.assign('/perfiles/'+profile.value+'/'),450);
 });
 const state=new URLSearchParams(location.search).get('estado');if(states[state]){document.querySelector('#ingreso').scrollIntoView({behavior:'instant'});openState(state);}
}
const grid=document.querySelector('.state-grid');if(grid){for(const [key,state]of Object.entries(states)){const card=document.createElement('article');card.className='state-preview';card.innerHTML=`<span class="state-icon"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="/static/seguridad/icons.svg#${state.icon}"></use></svg></span><h2>${state.title}</h2><p>${state.copy}</p><a href="/acceso/?estado=${key}#ingreso">Ver ventana ↗</a>`;grid.append(card);}}
