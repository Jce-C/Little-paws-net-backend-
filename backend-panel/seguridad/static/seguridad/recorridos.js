/* Accessible progressive enhancement for authenticated business screens. */
(()=>{'use strict';const t=globalThis.gettext||((s)=>s),norm=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase().trim();let seq=0;
function combo(select){
 if(select.dataset.comboReady)return;select.dataset.comboReady='1';
 const original=select.id||'choice-'+(++seq),wrap=document.createElement('div'),input=document.createElement('input'),list=document.createElement('div'),note=document.createElement('span');
 wrap.className='searchable-choice';list.className='choice-options';list.id=original+'-options';list.setAttribute('role','listbox');list.hidden=true;
 input.type='text';input.id=original;input.autocomplete='off';input.setAttribute('role','combobox');input.setAttribute('aria-autocomplete','list');input.setAttribute('aria-controls',list.id);input.setAttribute('aria-expanded','false');input.required=select.required;input.placeholder=t('Escribe para buscar');
 note.className='sr-only';note.setAttribute('role','status');note.id=original+'-status';input.setAttribute('aria-describedby',note.id);
 select.id=original+'-native';select.required=false;select.hidden=true;select.before(wrap);wrap.append(input,select,list,note);
 const current=()=>[...select.options].filter(o=>o.value&&!o.disabled&&!o.hidden),label=()=>select.selectedOptions[0]?.value?select.selectedOptions[0].textContent:'';input.value=label();
 let shown=[],index=-1;
 function close(){list.hidden=true;input.setAttribute('aria-expanded','false');input.removeAttribute('aria-activedescendant');}
 function choose(o){select.value=o.value;input.value=o.textContent;input.setCustomValidity('');close();select.dispatchEvent(new Event('change',{bubbles:true}));}
 function paint(){const q=norm(input.value);shown=current().filter(o=>!q||norm(o.textContent).includes(q)).slice(0,10);index=-1;list.replaceChildren();for(const [i,o]of shown.entries()){const item=document.createElement('div');item.id=list.id+'-'+i;item.setAttribute('role','option');item.setAttribute('aria-selected','false');item.textContent=o.textContent;item.addEventListener('mousedown',e=>e.preventDefault());item.addEventListener('click',()=>choose(o));list.append(item);}if(!shown.length){const empty=document.createElement('p');empty.textContent=t('No hay coincidencias. Revisa el nombre.');list.append(empty);}note.textContent=shown.length+' '+t('coincidencias');list.hidden=false;input.setAttribute('aria-expanded','true');}
 input.addEventListener('input',()=>{select.value='';input.setCustomValidity(input.value?t('Selecciona una coincidencia de la lista.'):input.required?t('Selecciona una opción.'): '');paint();select.dispatchEvent(new Event('change',{bubbles:true}));});
 input.addEventListener('focus',()=>{if(!input.value)paint();});
 input.addEventListener('keydown',e=>{if(e.key==='Escape'&&!list.hidden){e.preventDefault();e.stopPropagation();close();return;}if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();if(list.hidden)paint();index=Math.max(0,Math.min(shown.length-1,index+(e.key==='ArrowDown'?1:-1)));[...list.children].forEach((o,i)=>o.setAttribute('aria-selected',String(i===index)));if(shown[index]){input.setAttribute('aria-activedescendant',list.children[index].id);list.children[index].scrollIntoView({block:'nearest'});}}if(e.key==='Enter'&&!list.hidden){e.preventDefault();const exact=current().filter(o=>norm(o.textContent)===norm(input.value)||norm(o.textContent.split('·')[0])===norm(input.value));const o=shown[index]|| (exact.length===1?exact[0]:shown.length===1?shown[0]:null);if(o)choose(o);else note.textContent=t('Elige una coincidencia con las flechas.');}});
 input.addEventListener('blur',()=>{const exact=current().filter(o=>norm(o.textContent)===norm(input.value)||norm(o.textContent.split('·')[0])===norm(input.value));if(!select.value&&exact.length===1)choose(exact[0]);if(!input.value){select.value='';input.setCustomValidity(input.required?t('Selecciona una opción.'):'');}close();});
 select.addEventListener('choice:sync',()=>{input.value=label();input.setCustomValidity('');close();});
 select.form?.addEventListener('reset',()=>queueMicrotask(()=>{input.value=label();input.setCustomValidity('');close();}));
}
function init(){
 document.querySelectorAll('[data-operation-context]').forEach(s=>s.dataset.originalValue=s.value);
 document.querySelectorAll('select[data-species-map]').forEach(raza=>{if(raza.dataset.breedReady)return;raza.dataset.breedReady='1';const especie=raza.form?.querySelector('select[name=especie_id]');if(!especie)return;const map=JSON.parse(raza.dataset.speciesMap);if(!especie.value&&raza.value)especie.value=String(map[raza.value]||'');const filter=()=>{for(const o of raza.options){o.hidden=!!(o.value&&especie.value&&String(map[o.value])!==especie.value);o.disabled=o.hidden;}if(raza.selectedOptions[0]?.disabled){raza.value='';raza.dispatchEvent(new Event('choice:sync'));}};especie.addEventListener('change',filter);filter();});
 document.querySelectorAll('select[data-searchable-select]').forEach(combo);
 const modal=document.querySelector('.panel-modal[open]');if(modal){
  let footer=modal.querySelector(':scope > .modal-actions');if(!footer){footer=document.createElement('div');footer.className='modal-actions';modal.append(footer);}
  const body=modal.querySelector('.modal-body'),bar=body?.querySelector('.matrix-save');
  if(bar){footer.replaceChildren();const form=bar.closest('form');if(form){let formId=form.getAttribute('id');if(!formId){formId='dialog-form-'+(++seq);form.setAttribute('id',formId);}footer.dataset.owner=formId;bar.querySelectorAll('button,input,select,textarea').forEach(el=>el.setAttribute('form',formId));footer.append(bar);}}else if(!body?.querySelector('#'+CSS.escape(footer.dataset.owner||'no-form')))footer.replaceChildren();footer.hidden=!footer.children.length;
 }
}
document.addEventListener('change',e=>{const select=e.target;if(!select.matches('[data-operation-context]'))return;e.stopImmediatePropagation();const form=select.form,modal=select.closest('.panel-modal');const url=new URL(modal?.dataset.url||location.href);url.searchParams.set('organizacion',select.value);if(form.dataset.dirty==='true')select.value=select.dataset.originalValue||'';if(modal)window.PanelUI?.context(url.href);else if(window.PanelUI)window.PanelUI.route(url.href);else location.assign(url.href);},true);
document.addEventListener('keydown',e=>{if(e.key!=='Enter'||e.isComposing||!e.target.closest('.audit-filters'))return;const form=e.target.closest('form');if(e.target.matches('input')){e.preventDefault();window.PanelUI?.filter(form)||form.requestSubmit();}},true);
document.addEventListener('panel:formready',init);document.addEventListener('panel:ruta',init);document.addEventListener('panel:estado',init);init();
})();
