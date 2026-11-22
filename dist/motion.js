(()=>{'use strict';
const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
if(reduced.matches || !('IntersectionObserver' in window)) return;
const targets=document.querySelectorAll('.intro > div, .section-head, .tool-tabs, .project-narrative > .eyebrow, .project-narrative > h2, .project-narrative > p, .project-pillars article, .brand-manifesto, .nature-notes, .inner-space');
const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('is-visible');observer.unobserve(entry.target)}}),{threshold:.06,rootMargin:'0px 0px -20px 0px'});
targets.forEach(el=>{const rect=el.getBoundingClientRect(); if(rect.top>innerHeight){el.classList.add('reveal');observer.observe(el)}});
document.documentElement.classList.add('motion-ready');
const art=document.querySelector('.hero-art');let queued=false;
function update(){queued=false;if(!art||reduced.matches)return;const rect=art.getBoundingClientRect();if(rect.bottom>0&&rect.top<innerHeight){const offset=Math.max(-10,Math.min(10,(innerHeight/2-(rect.top+rect.height/2))*.025));art.style.setProperty('--landscape-shift',offset.toFixed(1)+'px')}}
addEventListener('scroll',()=>{if(!queued){queued=true;requestAnimationFrame(update)}},{passive:true});update();
})();
