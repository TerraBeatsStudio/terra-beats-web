(()=>{
  const root=document.querySelector('.hero-carousel');
  if(!root)return;
  const slides=[...root.querySelectorAll('.carousel-slide')];
  const dots=[...root.querySelectorAll('[data-slide]')];
  const caption=root.querySelector('.carousel-caption');
  const descEl=root.querySelector('.carousel-desc');
  const countEl=root.querySelector('.carousel-count');
  const captions=['Agua en movimiento','Bosque al amanecer','Cañón del Río Chíllar','Arroyo entre rocas'];
  let idx=0,timer=null,touchX=null;

  // Lightbox
  const lb=document.createElement('div');
  lb.className='terra-lightbox';
  lb.hidden=true;
  lb.setAttribute('role','dialog');
  lb.setAttribute('aria-modal','true');
  lb.setAttribute('aria-label','Vista ampliada del paisaje');
  lb.innerHTML='<button type="button" class="terra-lightbox-close" aria-label="Cerrar vista ampliada">×</button><div class="terra-lightbox-inner"><img class="terra-lightbox-img" alt=""><div class="terra-lightbox-bar"><div><strong class="lb-title"></strong><div class="lb-desc" style="font-size:13px;color:#b8cfd6"></div></div><div style="display:flex;gap:8px"><button type="button" class="carousel-btn lb-prev" aria-label="Anterior">‹</button><button type="button" class="carousel-btn lb-next" aria-label="Siguiente">›</button></div></div></div>';
  document.body.append(lb);
  const lbImg=lb.querySelector('.terra-lightbox-img');
  const lbTitle=lb.querySelector('.lb-title');
  const lbDesc=lb.querySelector('.lb-desc');

  function syncLb(){
    const s=slides[idx];
    lbImg.src=s.src;lbImg.alt=s.alt;
    lbTitle.textContent=captions[idx]||'';
    lbDesc.textContent=s.dataset.desc||'';
  }
  function openLb(){syncLb();lb.hidden=false;stop()}
  function closeLb(){lb.hidden=true;start()}

  function show(n){
    idx=(n+slides.length)%slides.length;
    slides.forEach((s,i)=>s.classList.toggle('is-active',i===idx));
    dots.forEach((d,i)=>d.setAttribute('aria-selected',String(i===idx)));
    if(caption)caption.textContent=captions[idx]||'';
    if(descEl)descEl.textContent=slides[idx].dataset.desc||'';
    if(countEl)countEl.textContent=String(idx+1).padStart(2,'0')+' / '+String(slides.length).padStart(2,'0');
    if(!lb.hidden)syncLb();
  }
  function start(){if(!lb.hidden)return;stop();timer=setInterval(()=>show(idx+1),5000)}
  function stop(){if(timer){clearInterval(timer);timer=null}}

  root.querySelector('[data-prev]')?.addEventListener('click',e=>{e.stopPropagation();show(idx-1);start()});
  root.querySelector('[data-next]')?.addEventListener('click',e=>{e.stopPropagation();show(idx+1);start()});
  dots.forEach(d=>d.addEventListener('click',e=>{e.stopPropagation();show(Number(d.dataset.slide));start()}));
  root.querySelector('[data-expand]')?.addEventListener('click',e=>{e.stopPropagation();openLb()});
  root.querySelector('.carousel-track')?.addEventListener('click',openLb);

  lb.querySelector('.terra-lightbox-close').addEventListener('click',closeLb);
  lb.querySelector('.lb-prev').addEventListener('click',()=>{show(idx-1)});
  lb.querySelector('.lb-next').addEventListener('click',()=>{show(idx+1)});
  lb.addEventListener('click',e=>{if(e.target===lb)closeLb()});
  window.addEventListener('keydown',e=>{
    if(lb.hidden)return;
    if(e.key==='Escape')closeLb();
    else if(e.key==='ArrowLeft')show(idx-1);
    else if(e.key==='ArrowRight')show(idx+1);
  });

  root.addEventListener('mouseenter',stop);
  root.addEventListener('mouseleave',start);
  root.addEventListener('touchstart',e=>{touchX=e.touches[0].clientX},{passive:true});
  root.addEventListener('touchend',e=>{
    if(touchX===null)return;
    const dx=e.changedTouches[0].clientX-touchX;
    touchX=null;
    if(Math.abs(dx)>40){show(dx<0?idx+1:idx-1);start()}
  },{passive:true});
  start();
})();
