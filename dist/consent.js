(()=>{
  const KEY='terra_consent_v1';
  const css=document.createElement('style');
  css.textContent='.terra-consent{position:fixed;left:16px;right:80px;bottom:16px;z-index:2147482900;max-width:680px;padding:16px 20px;border-radius:16px;border:1px solid rgba(0,198,255,.32);border-top-color:rgba(245,166,35,.55);background:rgba(7,19,31,.92);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);box-shadow:0 16px 40px rgba(0,0,0,.5);color:#DDECF0;font:13.5px/1.55 Montserrat,Arial,sans-serif;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:14px}.terra-consent[hidden]{display:none}.terra-consent p{margin:0;flex:1 1 280px;color:#c7d7dc}.terra-consent a{color:#00C6FF;text-decoration:underline}.terra-consent-actions{display:flex;gap:10px;flex-shrink:0}.terra-consent-btn{padding:9px 16px;border-radius:999px;font:600 12.5px/1.2 Montserrat,Arial,sans-serif;cursor:pointer;border:1px solid rgba(0,198,255,.35);background:rgba(11,27,43,.8);color:#DDECF0;transition:border-color .2s,background .2s}.terra-consent-btn:hover{border-color:#F5A623;color:#fff}.terra-consent-accept{background:linear-gradient(135deg,#F5A623,#e39b20);border-color:#F5A623;color:#07131F}.terra-consent-accept:hover{color:#07131F;filter:brightness(1.06)}@media(max-width:700px){.terra-consent{left:12px;right:12px;bottom:76px;padding:14px 16px}}';
  document.head.append(css);

  const banner=document.createElement('div');
  banner.className='terra-consent';
  banner.setAttribute('role','dialog');
  banner.setAttribute('aria-label','Preferencias de privacidad y cookies');
  banner.innerHTML='<p>Usamos Google Analytics de forma agregada solo si aceptas, para conocer qué guías ayudan más. <a href="/transparencia.html#analitica">Más información</a></p><div class="terra-consent-actions"><button type="button" class="terra-consent-btn" data-consent="denied">Rechazar</button><button type="button" class="terra-consent-btn terra-consent-accept" data-consent="granted">Aceptar</button></div>';
  banner.hidden=true;
  document.body.append(banner);

  function setConsent(state){
    try{localStorage.setItem(KEY,state)}catch{}
    window.dataLayer=window.dataLayer||[];
    function gtag(){window.dataLayer.push(arguments)}
    gtag('consent','update',{
      analytics_storage:state==='granted'?'granted':'denied',
      ad_storage:'denied',
      ad_user_data:'denied',
      ad_personalization:'denied'
    });
    window.dataLayer.push({event:'consent_update',consent_state:state});
    banner.hidden=true;
  }

  banner.querySelectorAll('[data-consent]').forEach(b=>b.addEventListener('click',()=>setConsent(b.dataset.consent)));
  document.addEventListener('click',e=>{
    const t=e.target.closest('[data-consent-prefs]');
    if(t){e.preventDefault();banner.hidden=false}
  });

  let saved=null;
  try{saved=localStorage.getItem(KEY)}catch{}
  if(!saved)banner.hidden=false;
})();
