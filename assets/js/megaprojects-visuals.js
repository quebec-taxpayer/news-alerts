/* Article-only progressive enhancement. Exact labels/widths remain untouched. */
(function(){'use strict';
var root=document.querySelector('[data-megaprojects-visuals]');if(!root)return;
var mq=window.matchMedia?window.matchMedia('(prefers-reduced-motion: reduce)'):null;
var running=[];function reduced(){return !!(mq&&mq.matches);}
function stop(){running.forEach(function(a){a.cancel();});running=[];}
function mark(id){root.querySelectorAll('.mpv-stop').forEach(function(a){if(a.getAttribute('href')==='#'+id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});root.querySelectorAll('#timeline .vt-item').forEach(function(e){e.classList.toggle('mpv-selected',e.id===id);});}
root.querySelectorAll('.mpv-stop').forEach(function(a){a.addEventListener('click',function(){var id=a.getAttribute('href').slice(1),target=document.getElementById(id);if(!target)return;mark(id);target.setAttribute('tabindex','-1');target.focus({preventScroll:true});/* Keep native anchor navigation/hash and its no-JS fallback. */});});
window.addEventListener('hashchange',function(){mark(location.hash.slice(1));});mark(location.hash.slice(1));
function reveal(figure){if(reduced())return;figure.querySelectorAll('.vb-fill,.sb-seg').forEach(function(fill,i){if(typeof fill.animate!=='function')return;try{var a=fill.animate([{transform:'scaleX(.75)',transformOrigin:'left center'},{transform:'scaleX(1)',transformOrigin:'left center'}],{duration:550,delay:i*70,easing:'ease-out'});running.push(a);a.onfinish=function(){var n=running.indexOf(a);if(n>=0)running.splice(n,1);};}catch(e){/* Static final width is always the underlying style. */}});}
var charts=root.querySelectorAll('figure.vb,figure.sb');
charts.forEach(function(figure){
var help=document.createElement('p');help.className='mpv-chart-help';help.innerHTML='<span class="l-fr" lang="fr">Choisissez un libellé pour mettre sa valeur en évidence; choisissez-le à nouveau pour retirer la sélection. Les chiffres et les sources restent visibles.</span><span class="l-en" lang="en">Choose a label to emphasise its value; choose it again to clear the selection. Figures and sources stay visible.</span>';figure.appendChild(help);
var labels=figure.classList.contains('vb')?figure.querySelectorAll('.vb-label'):figure.querySelectorAll('.sb-list>li');
labels.forEach(function(label,index){var button=document.createElement('button');button.type='button';button.className='mpv-label-button';button.setAttribute('aria-pressed','false');while(label.firstChild)button.appendChild(label.firstChild);label.appendChild(button);button.addEventListener('click',function(){var on=button.getAttribute('aria-pressed')!=='true';figure.querySelectorAll('.mpv-label-button').forEach(function(b){b.setAttribute('aria-pressed','false');});figure.querySelectorAll('.mpv-highlight').forEach(function(x){x.classList.remove('mpv-highlight');});if(on){button.setAttribute('aria-pressed','true');button.classList.add('mpv-highlight');var values=figure.querySelectorAll('.vb-fill,.sb-seg');if(values[index])values[index].classList.add('mpv-highlight');}});});
});
/* No initial opacity/transform class is applied. Observer failure cannot hide evidence. */
if(!reduced()&&'IntersectionObserver' in window){try{var observer=new IntersectionObserver(function(entries){entries.forEach(function(en){if(en.isIntersecting){reveal(en.target);observer.unobserve(en.target);}});},{threshold:.15});charts.forEach(function(f){observer.observe(f);});}catch(e){/* All figures remain static. */}}
if(mq){if(mq.addEventListener)mq.addEventListener('change',function(){if(reduced())stop();});else if(mq.addListener)mq.addListener(function(){if(reduced())stop();});}
window.addEventListener('beforeprint',stop);
})();
