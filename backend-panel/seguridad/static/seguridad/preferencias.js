"use strict";
/* localized-ui-30 */
(()=>{const ui=globalThis.gettext||((v)=>v);

"use strict";
(() => {
  const preferencias=document.querySelector('.preferencias-detalles');
  if(!preferencias)return;
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&preferencias.open){
      preferencias.open=false;
      preferencias.querySelector('summary').focus();
    }
  });
  document.addEventListener('click',event=>{
    if(preferencias.open&&!preferencias.contains(event.target))preferencias.open=false;
  });
})();

(()=>{const root=document.querySelector('.preferencias-contenido');if(!root)return;let chain=Promise.resolve();const attrs={tema:'theme',texto:'textSize',contraste:'contrast',movimiento:'motion'};const symbols={tema:['◐','☀','☾'],texto:['A','A+','A++'],contraste:['◐','◑'],movimiento:['▶','▌▌']};root.querySelectorAll('select[name]').forEach(select=>{if(!attrs[select.name])return;const form=select.form,group=document.createElement('div');group.className='preference-options';group.setAttribute('role','group');group.setAttribute('aria-label',root.querySelector(`label[for="${select.id}"]`)?.textContent||select.name);[...select.options].forEach((option,index)=>{const button=document.createElement('button');button.type='button';button.className='preference-choice';button.setAttribute('aria-pressed',String(option.selected));const icon=document.createElement('span');icon.className='preference-symbol';icon.setAttribute('aria-hidden','true');icon.textContent=symbols[select.name][index];const label=document.createElement('span');label.textContent=option.textContent;button.append(icon,label);button.addEventListener('click',()=>{select.value=option.value;document.documentElement.dataset[attrs[select.name]]=option.value;group.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));const data=new FormData(form);chain=chain.catch(()=>{}).then(async()=>{const response=await fetch(form.action,{method:'POST',body:data,credentials:'same-origin',headers:{Accept:'application/json'}});const status=root.querySelector('[data-preference-status]');if(!response.ok){status.textContent=ui('No se pudo guardar. Vuelve a intentarlo.');return;}status.textContent=ui('Preferencia aplicada');});});group.append(button);});select.hidden=true;select.after(group);root.querySelector(`label[for="${select.id}"]`)?.removeAttribute('for');const save=form.querySelector('button[type=submit]:not([name])');if(save)save.hidden=true;});const lang=root.querySelector('select[name=language]');if(lang){lang.form.querySelector('button[type=submit]').hidden=true;lang.addEventListener('change',()=>lang.form.requestSubmit());}root.querySelector('select[name=perfil_visual]')?.addEventListener('change',async e=>{const data=new FormData(e.target.form);const r=await fetch(e.target.form.action,{method:'POST',body:data,headers:{Accept:'application/json'}});if(r.ok)document.body.dataset.profile=e.target.value;});})();

})();
