"use strict";
/* localized-ui-30 */
(()=>{const ui=globalThis.gettext||((v)=>v);

"use strict";
(()=>{const body=document.body,sidebar=document.querySelector('#navegacion'),toggle=document.querySelector('[data-sidebar-toggle]');
const mobile=matchMedia('(max-width:800px)');let folded=localStorage.getItem('lpn_sidebar_folded')==='1';
function menu(open){if(sidebar){sidebar.inert=mobile.matches&&!open;sidebar.setAttribute('aria-hidden',String(mobile.matches&&!open));}if(mobile.matches){body.classList.toggle('sidebar-mobile-open',open);sidebar?.classList.toggle('abierta',open);}else{folded=!open;body.classList.toggle('sidebar-folded',folded);localStorage.setItem('lpn_sidebar_folded',folded?'1':'0');}toggle?.setAttribute('aria-expanded',String(open));toggle?.setAttribute('aria-label',(globalThis.gettext||((v)=>v))(open?'Contraer navegación':ui('Expandir navegación')));}
if(toggle){menu(!mobile.matches&&!folded);toggle.addEventListener('click',()=>menu(mobile.matches?!body.classList.contains('sidebar-mobile-open'):body.classList.contains('sidebar-folded')));document.querySelector('[data-sidebar-close]')?.addEventListener('click',()=>{menu(false);toggle.focus();});document.addEventListener('keydown',e=>{if(e.key==='Escape'&&mobile.matches){menu(false);toggle.focus();}});mobile.addEventListener('change',()=>{body.classList.remove('sidebar-mobile-open');menu(!mobile.matches&&!folded);});}
const workspace=document.querySelector('[data-rbac-workspace]');if(!workspace)return;workspace.dataset.controls='switch';workspace.querySelectorAll('.matrix-control input').forEach(i=>i.setAttribute('role','switch'));
workspace.querySelectorAll('[data-resource-row]').forEach(row=>{const all=row.querySelector('[data-resource-toggle]'),items=[...row.querySelectorAll('input[name=permisos]')];all?.addEventListener('change',()=>{if(all.checked){if(!items.some(i=>i.checked)&&items[0])items[0].checked=true;}else items.forEach(i=>i.checked=false);row.dispatchEvent(new Event('change',{bubbles:true}));});items.forEach(i=>i.addEventListener('change',()=>{all.checked=items.some(i=>i.checked);}));});
workspace.querySelector('[data-filter-matrix]')?.addEventListener('input',e=>{const clean=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();const q=clean(e.target.value);workspace.querySelectorAll('[data-resource-row]').forEach(r=>r.hidden=!clean(r.textContent).includes(q));});
})();
// Dirty state is delegated by interacciones.js for both full and partial views.

document.querySelector('[data-cart-add]')?.addEventListener('click',()=>{const total=document.querySelector('#id_lineas-TOTAL_FORMS');if(+total.value>=50)return;const t=document.querySelector('[data-cart-empty]').innerHTML.replaceAll('__prefix__',total.value);document.querySelector('[data-cart-rows]').insertAdjacentHTML('beforeend',t);total.value=String(+total.value+1);});

document.addEventListener("submit",e=>{if(e.target.method?.toLowerCase()==="post"&&!e.defaultPrevented)document.body.dataset.submitting="true";});



})();
