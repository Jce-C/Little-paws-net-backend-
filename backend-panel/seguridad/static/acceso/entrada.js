"use strict";
const t=globalThis.gettext||((value)=>value);
const assetBase=document.currentScript.dataset.assets,iconBase=document.currentScript.dataset.icons;
const clouds=document.querySelector('.clouds');
if(clouds){
 // El lado corresponde al borde plano real de cada SVG. Nunca se invierte
 // hacia el centro ni se deja que el movimiento cruce el anclaje lateral.
 const positions=[['right',8,28],['left',14,26],['left',47,28],['left',78,30],['right',55,35],['right',83,30]];
 positions.forEach(([side,y,w],i)=>{const el=document.createElement('div');el.className='cloud side-'+side;el.dataset.side=side;el.dataset.asset=String(i+1);el.style.cssText=`--y:${y}%;--w:${w}vw;--duration:${14+i*2}s;--delay:${i*100}ms;--arrive-x:${side==='left'?'-':'+'}72px`;const art=document.createElement('div');art.className='cloud-art';const img=document.createElement('img');img.src=`${assetBase}nube-${i+1}.svg`;img.alt='';img.decoding='async';art.append(img);el.append(art);clouds.append(el);});
 const systemMotion=matchMedia('(prefers-reduced-motion: reduce)'),reduced={get matches(){return document.documentElement.dataset.motion==='reduce'||systemMotion.matches;},addEventListener(...args){systemMotion.addEventListener(...args);}},hero=document.querySelector('.hero');let frame=0,heroHeight=hero.offsetHeight,entered=0;
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

const password=document.querySelector('#id_password'),toggle=document.querySelector('#show-password');
toggle?.addEventListener('click',()=>{const visible=password.type==='password';password.type=visible?'text':'password';toggle.setAttribute('aria-pressed',String(visible));toggle.setAttribute('aria-label',visible?t('Ocultar contraseña'):t('Mostrar contraseña'));toggle.querySelector('use').setAttribute('href',iconBase+(visible?'#eye-off':'#eye'));});
const help=document.querySelector('#access-help');
document.querySelector('[data-access-help]')?.addEventListener('click',()=>help.showModal());
document.querySelectorAll('[data-close-help]').forEach(b=>b.addEventListener('click',()=>help.close()));
document.querySelector('#login-form')?.addEventListener('submit',()=>{const button=document.querySelector('#submit-login');button.disabled=true;button.textContent=t('Comprobando acceso…');});
addEventListener('pageshow',()=>{const button=document.querySelector('#submit-login');button.disabled=false;button.textContent=t('Iniciar sesión ↗');});
if(document.body.dataset.formActive==='true'){
 const show=()=>{document.querySelectorAll('.entry .reveal').forEach(el=>el.classList.add('is-visible'));document.querySelector('#ingreso').scrollIntoView({behavior:'instant'});};
 if(document.readyState==='complete')show();else addEventListener('load',show,{once:true});
}
