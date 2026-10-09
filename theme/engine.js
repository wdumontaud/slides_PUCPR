// theme/engine.js — builds the whole presentation from the parts found in #stage.
//
// Conventions for the parts/*.html files:
//   <!-- section: Introduction -->        starts a section  -> table of contents + top bar
//   <!-- subsection: Governing equation -->  starts a subsection (table of contents only)
//   <section class="slide" data-title="Slide title"> ... </section>   one slide  -> one bubble
//     data-layout="free"   children are positioned freely (no .content wrapper)
//     data-layout="title"  title slide (no header / footer)
//     data-auto="toc"      the slide content is the automatic table of contents
//     data-steps="2"       2 extra steps inside the slide (like beamer \pause): → reveals them one by one
//       <div data-from="1">  shown from step 1 on      <div data-until="0">  shown up to step 0 only
//       the slide also gets data-step="k" (for CSS) and receives a 'step' event {detail:{step,instant}} (for JS),
//       and a 'leave' event when another slide is shown
(()=>{
const CFG=window.CONFIG||{};
const stage=document.getElementById('stage');
const params=new URLSearchParams(location.search);
const PRINT=params.has('print');
const NS='http://www.w3.org/2000/svg';

// ---------- 1. collect slides, sections and subsections (document order) ----------
const slides=[]; const toc=[]; let sec='',sub='';
[...stage.childNodes].forEach(n=>{
  if(n.nodeType===8){
    const t=n.nodeValue.trim(); let m;
    if((m=t.match(/^section:\s*(.+)$/i))){ sec=m[1].trim(); sub=''; toc.push({name:sec,subs:[]}); }
    else if((m=t.match(/^subsection:\s*(.+)$/i))){ sub=m[1].trim(); if(toc.length) toc[toc.length-1].subs.push(sub); }
  } else if(n.nodeType===1 && n.matches('section.slide')){
    n.dataset.section=sec; n.dataset.subsection=sub; slides.push(n);
  }
});

// ---------- 2. normalise slides (title bar, content wrapper, automatic TOC) ----------
slides.forEach(s=>{
  const layout=s.dataset.layout||'';
  if(layout==='title') s.classList.add('s-title');
  if(s.dataset.title){ const ft=document.createElement('div'); ft.className='frametitle'; ft.innerHTML=s.dataset.title; s.prepend(ft); }
  if(!layout){
    const c=document.createElement('div'); c.className='content';
    [...s.children].forEach(ch=>{ if(!ch.matches('.frametitle,.field')) c.appendChild(ch); });
    s.appendChild(c);
  }
  if(s.dataset.auto==='toc'){
    s.classList.add('s-toc');
    s.querySelector('.content').innerHTML='<ol>'+toc.map(t=>
      `<li>${t.name}`+(t.subs.length?'<ol>'+t.subs.map(x=>`<li>${x}</li>`).join('')+'</ol>':'')+'</li>').join('')+'</ol>';
  }
});
const isTitle=s=>s.classList.contains('s-title');
const nSteps=s=>parseInt(s.dataset.steps)||0;
function setStep(s,k,instant){
  s.dataset.step=k;
  s.querySelectorAll('[data-from],[data-until]').forEach(e=>{
    const f=parseInt(e.dataset.from), u=parseInt(e.dataset.until);
    e.classList.toggle('step-hidden',(!isNaN(f)&&k<f)||(!isNaN(u)&&k>u)); });
  s.dispatchEvent(new CustomEvent('step',{detail:{step:k,instant:!!instant}}));
}
const dots=[]; slides.forEach((s,k)=>{ if(s.dataset.section) dots.push({k,sec:s.dataset.section}); });
const secNames=[...new Set(dots.map(d=>d.sec))];

// ---------- 3. navigation "wave": one bubble per sectioned slide ----------
const NW=1280, NH=50, PAD=60, INTRA_PX=46, INTER_MIN=90, LAB_GAP=26;
const rnd=rng(11);
// pixel layout: bubbles of a section stay close; the gap between sections just fits the labels
const mctx=document.createElement('canvas').getContext('2d'); mctx.font='14px "CMU Sans Serif",sans-serif';
const grp=secNames.map(name=>{const g=dots.filter(d=>d.sec===name);
  return {g,w:mctx.measureText(name).width+8,span:(g.length-1)*INTRA_PX}});
let x=0;
grp.forEach((G,gi)=>{ if(gi){ const A=grp[gi-1];
    x+=Math.max(INTER_MIN,LAB_GAP+(A.w-A.span)/2+(G.w-G.span)/2); }
  G.g.forEach((d,n)=>{d.x=x+n*INTRA_PX;}); x+=G.span; });
const kx=Math.min(1,(NW-2*PAD)/Math.max(x,1)), X0=(NW-x*kx)/2;
dots.forEach((d,n)=>{ d.x=X0+d.x*kx; d.y=(n%2?29:41)+(rnd()-.5)*4; });
// irregular wave through the bubbles (Catmull-Rom through extra control points)
const pts=[]; let sign=1; const first=[];
dots.forEach((d,n)=>{ first.push(pts.length); pts.push(d);
  if(n<dots.length-1){ const e=dots[n+1], long=e.sec!==d.sec, m=long?2:1;
    for(let j=1;j<=m;j++){
      if(rnd()<.8) sign=-sign;
      const t=(j-.5+(rnd()-.5)*.5)/m, amp=(long?8:6)+rnd()*7;
      pts.push({x:d.x+(e.x-d.x)*t, y:Math.max(26,Math.min(47,d.y+(e.y-d.y)*t+sign*amp))}); } } });
const P=i=>pts[Math.max(0,Math.min(pts.length-1,i))];
const seg=i=>{const a=P(i),b=P(i+1),p0=P(i-1),p3=P(i+2);
  return `C${a.x+(b.x-p0.x)/6},${a.y+(b.y-p0.y)/6} ${b.x-(p3.x-a.x)/6},${b.y-(p3.y-a.y)/6} ${b.x},${b.y}`};

function makeNav(onDotClick){
  const el=document.createElement('div'); el.className='nav';
  const svg=document.createElementNS(NS,'svg'); svg.setAttribute('viewBox',`0 0 ${NW} ${NH}`);
  const mk=(t,a,txt)=>{const e=document.createElementNS(NS,t);for(const q in a)e.setAttribute(q,a[q]);if(txt!=null)e.textContent=txt;svg.appendChild(e);return e};
  // drawing order matters: lines first, bubbles last => the line never shows over a bubble
  const segs=[];
  for(let n=0;n<dots.length-1;n++){ let d=`M${dots[n].x},${dots[n].y}`;
    for(let i=first[n];i<first[n+1];i++) d+=' '+seg(i);
    segs.push(mk('path',{d,class:'seg'})); }
  const labs=secNames.map(name=>{ const g=dots.filter(d=>d.sec===name);
    return mk('text',{x:(g[0].x+g[g.length-1].x)/2,y:18,class:'lab'},name); });
  const cs=dots.map(d=>{const c=mk('circle',{cx:d.x,cy:d.y,r:5});
    if(onDotClick) c.addEventListener('click',e=>{e.stopPropagation();onDotClick(d.k)}); return c});
  el.appendChild(svg);
  return {el, set(i){
    let cur=-1; dots.forEach((d,n)=>{ if(d.k<=i) cur=n; });
    const onDot=cur>=0&&dots[cur].k===i;
    cs.forEach((c,n)=>{const on=onDot&&n===cur;
      c.setAttribute('class',on?'cur':(n<cur||(n===cur&&!onDot)?'past':'')); c.style.r=on?'7px':'5px';});
    segs.forEach((p,n)=>{ if(p._L==null){p._L=p.getTotalLength();p.style.strokeDasharray=p._L;p.style.strokeDashoffset=p._L;}
      p.style.strokeDashoffset=(n<cur)?0:p._L; });
    labs.forEach(l=>l.setAttribute('class','lab'+(onDot&&l.textContent===dots[cur].sec?' cur':'')));
  }};
}
function makeFoot(){
  const el=document.createElement('div'); el.className='foot';
  el.innerHTML=`<i class="prog"></i><span class="a">${CFG.author||''}</span><span class="t">${CFG.short_title||''}</span><span class="n"></span>`;
  return {el, set(i){
    el.querySelector('.n').textContent=`${i+1} / ${slides.length}`;
    el.querySelector('.prog').style.width=(100*i/Math.max(1,slides.length-1))+'%'; }};
}

// ---------- 4a. PDF / print mode : one page per slide, static frame of the animated backgrounds ----------
async function printMode(){
  document.body.classList.add('print');
  try{ await document.fonts.ready; }catch(e){}
  const pages=document.createElement('div'); document.body.appendChild(pages);
  slides.forEach((s,k)=>{
    s.querySelectorAll('canvas.field').forEach(cv=>{
      const f=FIELD(cv); if(!f) return; f.draw(33);
      const img=new Image(); img.className='field'; img.src=cv.toDataURL(); cv.replaceWith(img); });
    const pg=document.createElement('div'); pg.className='page'; pages.appendChild(pg);
    s.classList.add('active','noanim'); pg.appendChild(s); setStep(s,nSteps(s),true);
    if(!isTitle(s)){
      const nv=makeNav(), ft=makeFoot(); nv.el.classList.add('noanim');
      pg.appendChild(nv.el); pg.appendChild(ft.el); nv.set(k); ft.set(k); }
  });
  stage.querySelectorAll('style').forEach(st=>document.head.appendChild(st));   // keep the parts' own CSS
  stage.remove();
  window.__ready=true;
  if(params.get('dialog')) setTimeout(()=>print(),500);
}
if(PRINT){ printMode(); return; }

// ---------- 4b. interactive mode ----------
let i=Math.min(slides.length-1,Math.max(0,(parseInt(location.hash.slice(1))||1)-1)), st=0;
const nav=makeNav(k=>show(k,0)), foot=makeFoot();
stage.appendChild(nav.el); stage.appendChild(foot.el);
const fields=[...stage.querySelectorAll('canvas.field')].map(FIELD).filter(Boolean);

function show(n,step){
  const prev=i; i=Math.max(0,Math.min(slides.length-1,n));
  if(prev!==i) slides[prev].dispatchEvent(new CustomEvent('leave'));
  if(prev!==i||step!=null){ st=step==null?0:Math.min(step,nSteps(slides[i])); setStep(slides[i],st,true); }
  slides.forEach((s,k)=>s.classList.toggle('active',k===i));
  const t=isTitle(slides[i]);
  nav.el.style.opacity=foot.el.style.opacity=t?0:1; nav.el.style.pointerEvents=t?'none':'auto';
  nav.set(i); foot.set(i);
  history.replaceState(null,'','#'+(i+1));
}
function fit(){const k=Math.min(innerWidth/1280,innerHeight/720);stage.style.transform=`translate(-50%,-50%) scale(${k})`}
function toggleFullscreen(){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}
function next(){ if(st<nSteps(slides[i])) setStep(slides[i],++st); else show(i+1); }
function prev(){ if(st>0) setStep(slides[i],--st); else if(i>0){ const k=i-1; show(k,nSteps(slides[k])); } }
addEventListener('resize',fit); fit(); show(i,0);

addEventListener('keydown',e=>{
  if(['ArrowRight','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();next()}
  else if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();prev()}
  else if(e.key==='Home')show(0); else if(e.key==='End')show(slides.length-1);
  else if(e.key==='f'||e.key==='F') toggleFullscreen();
});
addEventListener('click',e=>{ if(e.target.closest('a,#tools'))return; e.clientX>innerWidth/2?next():prev(); });

// viewer UI: fullscreen + PDF buttons (visible while the mouse moves), hint fading after a few seconds
const hint=Object.assign(document.createElement('div'),{className:'hint',textContent:'← → / space: navigate · F: fullscreen'});
const tools=document.createElement('div'); tools.id='tools';
tools.innerHTML='<button id="bFs" title="Fullscreen (F)">⛶ Fullscreen</button><button id="bPdf" title="Open the print dialog: choose Save as PDF">⤓ PDF</button>';
document.body.append(hint,tools);
tools.querySelector('#bFs').onclick=toggleFullscreen;
tools.querySelector('#bPdf').onclick=()=>window.open(location.pathname+'?print=1&dialog=1','_blank');
let hide; addEventListener('mousemove',()=>{tools.classList.add('show');clearTimeout(hide);hide=setTimeout(()=>tools.classList.remove('show'),2500)});
setTimeout(()=>hint.style.opacity=0,4000);

(function loop(ms){fields.forEach(f=>{if(f.cv.closest('.slide').classList.contains('active'))f.draw(ms/1000+20)});requestAnimationFrame(loop)})(0);
})();
