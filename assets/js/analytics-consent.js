/* Consent Mode v2 (advanced): load gtag on every page. analytics_storage is
   denied by default unless the visitor already accepted; ads storage stays
   denied. No analytics cookies before consent; cookieless pings carry the
   consent state. */
(function () {
'use strict';
var id='G-C1PEZXHCTW',key='altviews-analytics-consent-v1',choice=null;
try{choice=localStorage.getItem(key);}catch(e){}
window.dataLayer=window.dataLayer||[];
window.gtag=function(){window.dataLayer.push(arguments);};
window.gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:choice==='granted'?'granted':'denied',wait_for_update:500});
window.gtag('set','ads_data_redaction',true);
window.gtag('set','url_passthrough',false);
window.gtag('js',new Date());
window.gtag('config',id,{allow_google_signals:false,allow_ad_personalization_signals:false});
var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+id;s.id='altviews-ga4';document.head.appendChild(s);
function clearCookies(){
 var host=location.hostname.split('.');
 document.cookie.split(';').forEach(function(c){var n=c.split('=')[0].trim();if(!/^_ga(?:_|$)|^_gid$|^_gat/.test(n))return;
 document.cookie=n+'=; Max-Age=0; path=/; SameSite=Lax';
 for(var i=0;i<host.length-1;i++)document.cookie=n+'=; Max-Age=0; path=/; domain=.'+host.slice(i).join('.')+'; SameSite=Lax';});
}
function restoreFocus(){var trigger=document.querySelector('[data-analytics-settings]');if(trigger)trigger.focus();}
function save(v){choice=v;try{localStorage.setItem(key,v);}catch(e){}document.getElementById('analytics-consent').hidden=true;restoreFocus();
 if(v==='granted')window.gtag('consent','update',{analytics_storage:'granted'});
 else{window.gtag('consent','update',{analytics_storage:'denied'});clearCookies();}}
function ui(){
 var box=document.createElement('section');box.id='analytics-consent';box.setAttribute('aria-label','Choix de statistiques / Analytics choices');box.hidden=choice==='granted'||choice==='denied';
 var a=document.querySelector('a[href$="/analytics-privacy/"]'),url=a?a.getAttribute('href'):'/analytics-privacy/';
 box.innerHTML='<p><span class="l-fr" lang="fr">Sans votre accord, Google reçoit uniquement des signaux anonymes, sans témoin. Avec votre accord, nous mesurons les statistiques de visite. Refuser ne limite pas le site. Retirez votre accord dans le pied de page.</span><span class="l-en" lang="en">Without your permission, Google receives only anonymous, cookieless signals. With permission, we collect full visit statistics. Declining does not limit the site. Withdraw permission in the footer.</span> <a href="/analytics-privacy/"><span class="l-fr" lang="fr">En savoir plus</span><span class="l-en" lang="en">Learn more</span></a></p><div class="consent-actions"><button type="button" data-choice="denied"><span class="l-fr" lang="fr">Refuser / Retirer</span><span class="l-en" lang="en">Decline / Withdraw</span></button><button type="button" data-choice="granted"><span class="l-fr" lang="fr">Accepter les statistiques</span><span class="l-en" lang="en">Accept analytics</span></button><button type="button" data-consent-close><span class="l-fr" lang="fr">Fermer sans changer</span><span class="l-en" lang="en">Close without changing</span></button></div>';
 box.querySelector('a').setAttribute('href',url);
 document.body.appendChild(box);
 box.querySelectorAll('[data-choice]').forEach(function(b){b.addEventListener('click',function(){save(b.getAttribute('data-choice'));});});
 box.querySelector('[data-consent-close]').addEventListener('click',function(){box.hidden=true;restoreFocus();});
 document.querySelectorAll('[data-analytics-settings]').forEach(function(b){b.addEventListener('click',function(){box.hidden=false;box.querySelector('button').focus();});});
 window.addEventListener('storage',function(e){if(e.key!==key&&e.key!==null)return;choice=e.key===null?null:e.newValue;if(choice==='granted'){window.gtag('consent','update',{analytics_storage:'granted'});box.hidden=true;}else{window.gtag('consent','update',{analytics_storage:'denied'});clearCookies();box.hidden=choice==='denied';}});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ui);else ui();
})();
