(()=>{
  const root=document.querySelector('.hero-carousel');
  if(!root)return;
  const slides=[...root.querySelectorAll('.carousel-slide')];
  const dots=[...root.querySelectorAll('[data-slide]')];
  const caption=root.querySelector('.carousel-caption');
  const captions=['Agua en movimiento','Bosque al amanecer','Cañón del Río Chíllar','Arroyo entre rocas'];
  let idx=0,timer=null,touchX=null;

  function show(n){
    idx=(n+slides.length)%slides.length;
    slides.forEach((s,i)=>s.classList.toggle('is-active',i===idx));
    dots.forEach((d,i)=>d.setAttribute('aria-selected',String(i===idx)));
    if(caption)caption.textContent=captions[idx]||'';
  }
  function start(){stop();timer=setInterval(()=>show(idx+1),5000)}
  function stop(){if(timer){clearInterval(timer);timer=null}}

  root.querySelector('[data-prev]')?.addEventListener('click',()=>{show(idx-1);start()});
  root.querySelector('[data-next]')?.addEventListener('click',()=>{show(idx+1);start()});
  dots.forEach(d=>d.addEventListener('click',()=>{show(Number(d.dataset.slide));start()}));
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
