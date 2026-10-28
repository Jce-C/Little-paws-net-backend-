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
