'use strict';
document.querySelectorAll('[data-copy]').forEach(button=>{
 button.addEventListener('click',async()=>{
  const source=document.getElementById(button.dataset.copy);
  const status=button.parentElement.querySelector('.copy-status');
  const value=source.textContent;
  try{
   if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(value);}
   else{
    const field=document.createElement('textarea');field.value=value;field.style.position='fixed';field.style.top='0';field.style.opacity='0';document.body.appendChild(field);field.focus();field.select();
    const success=document.execCommand('copy');field.remove();button.focus();if(!success)throw new Error('copy unsupported');
   }
   status.textContent='全文をコピーしました。貼り付けて内容を確認してください。';
  }catch{status.textContent='コピーできませんでした。下の全文を選択してコピーしてください。';}
 });
});
