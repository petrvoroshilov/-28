'use strict';
var LS_QUEST='th_quest_v9', LS_TEST='th_test_battle_v9', Q=null;
var TYPES=['bone','moss','azure','ember','violet','gold','armored'];
var TCOLOR={bone:'#e8e1cf',moss:'#9ec98a',azure:'#9fd0ef',ember:'#f0a878',violet:'#c9a8ef',gold:'#f3d98a',armored:'#cdd6e4',boss:'#e8c87a'};
var qrLibPromise=null;
function $(id){return document.getElementById(id);}
init();
function init(){try{var s=localStorage.getItem(LS_QUEST);if(s)Q=JSON.parse(s);}catch(e){}
  if(!Q||!Q.stages||!Q.stages.length){try{var r=new XMLHttpRequest();r.open('GET','./quests/default/quest.json',false);r.send();Q=JSON.parse(r.responseText);}catch(e){Q=fresh();}}
  if(!Q.settings)Q.settings={age:'kid',tts:true,playerDamage:false};if(!Q.treasure)Q.treasure={hint:'',keyHint:'',code:''};if(!Q.boss)Q.boss={name:'Босс',type:'boss',hp:300,damagePerHit:25,intro:'Клад мой!'};
  polish(Q);render();bind();
}
function polish(q){
  if(!q||!Array.isArray(q.stages))return;
  var L=q.stages.length;
  if(L>0){var s=q.stages[L-1];s.miniBoss=true;s.sizeMul=Math.max(s.sizeMul||1,1.3);}
  if(q.boss)q.boss.sizeMul=Math.max(q.boss.sizeMul||1,1.35);
  if(!q.treasure)q.treasure={};
  if(!q.treasure.keyHint)q.treasure.keyHint=q.treasure.hint||'КЛЮЧ К КАРТЕ НАХОДИТСЯ В УЧЕБНИКЕ «ОКРУЖАЮЩИЙ МИР»';
}
function fresh(){return{title:'Новый квест',settings:{age:'kid',tts:true,playerDamage:false},map:{scale:60,width:6,height:5},stages:[],boss:{name:'Босс',type:'boss',hp:300,damagePerHit:25,intro:'Клад мой!'},treasure:{hint:'Ищи в антресоли',keyHint:'КЛЮЧ К КАРТЕ НАХОДИТСЯ В УЧЕБНИКЕ «ОКРУЖАЮЩИЙ МИР»',code:'1234'}};}
function loadScript(src){ return new Promise(function(resolve,reject){ var s=document.createElement('script'); s.async=true; s.src=src; s.onload=function(){resolve();}; s.onerror=function(){reject(new Error('load '+src));}; document.head.appendChild(s); }); }
function ensureQRCode(){ if(window.QRCode&&QRCode.toCanvas) return Promise.resolve(); if(!qrLibPromise){ qrLibPromise=loadScript('https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js').then(function(){ if(!(window.QRCode&&QRCode.toCanvas)) throw new Error('QRCode not global'); }); } return qrLibPromise; }
function qrToCanvas(cv,text){
  return new Promise(function(resolve,reject){
    var done=false;
    function ok(){ if(done)return; done=true; resolve(); }
    function bad(e){ if(done)return; done=true; reject(e||new Error('qr fail')); }
    if(!(window.QRCode&&QRCode.toCanvas)){ bad(new Error('no QRCode lib')); return; }
    var opts={width:240,margin:2,errorCorrectionLevel:'M',color:{dark:'#000000',light:'#ffffff'}};
    var timer=setTimeout(function(){ bad(new Error('QR timeout')); },2500);
    try{
      var ret=QRCode.toCanvas(cv,text,opts,function(err){ clearTimeout(timer); if(err) bad(err); else ok(); });
      if(ret && typeof ret.then==='function'){
        ret.then(function(){ clearTimeout(timer); ok(); }).catch(function(e){ clearTimeout(timer); bad(e); });
      }
    }catch(e){ clearTimeout(timer); bad(e); }
  });
}
function qrViaImage(cv,text){
  return new Promise(function(resolve,reject){
    var settled=false;
    function ok(){
      if(settled)return; settled=true; clearTimeout(timer);
      try{
        var g=cv.getContext('2d');
        g.fillStyle='#fff'; g.fillRect(0,0,cv.width,cv.height);
        g.drawImage(img,0,0,cv.width,cv.height);
        resolve();
      }catch(e){ reject(e); }
    }
    function bad(e){ if(settled)return; settled=true; clearTimeout(timer); reject(e||new Error('image qr fail')); }
    var img=new Image(); img.crossOrigin='anonymous';
    var timer=setTimeout(function(){ bad(new Error('image timeout')); },5000);
    img.onload=ok;
    img.onerror=function(){ bad(new Error('image network')); };
    img.src='https://api.qrserver.com/v1/create-qr-code/?size=240x240&margin=10&data='+encodeURIComponent(text);
  });
}
function makeQR(cv,text){
  return ensureQRCode()
    .then(function(){ return qrToCanvas(cv,text); })
    .catch(function(){ return qrViaImage(cv,text); })
    .catch(function(){ var big=(text.indexOf('THMARK:')===0?text.slice(7):'START'); fallbackCv(cv,big,text); });
}
function bind(){$('saveBtn').onclick=save;$('exportBtn').onclick=function(){collect();var blob=new Blob([JSON.stringify(Q,null,2)],{type:'application/json'});var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='quest.json';a.click();};
  $('importFile').onchange=function(e){var f=e.target.files[0];if(!f)return;var rd=new FileReader();rd.onload=function(){try{Q=JSON.parse(rd.result);polish(Q);render();toast('Импортировано');}catch(err){alert('Битый JSON');}};rd.readAsText(f);};
  $('printBtn').onclick=printMarkers;$('openGameBtn').onclick=function(){collect();polish(Q);localStorage.setItem(LS_QUEST,JSON.stringify(Q));window.location.href='index.html';};
  $('addStage').onclick=function(){collect();var used=(Q.stages||[]).map(function(s){return s.type;});var nt=TYPES.filter(function(t){return used.indexOf(t)<0;})[0]||'bone';Q.stages.push({zone:'Зона',point:[1,1],riddle:'Загадка',type:nt,hp:100,damagePerHit:20,dodge:0.28,hitbox:1.3,emerge:1.4,hideInterval:6,hideTime:1.4,name:'Костяш'});polish(Q);render();};
}
function save(){collect();polish(Q);localStorage.setItem(LS_QUEST,JSON.stringify(Q));toast('Сохранено. Открыть игру применит настройки сразу.');}
function toast(m){var t=document.createElement('div');t.textContent=m;t.style.cssText='position:fixed;bottom:16px;left:50%;transform:translateX(-50%);background:#22c55e;color:#06281a;padding:10px 16px;border-radius:12px;font-weight:800;z-index:99';document.body.appendChild(t);setTimeout(function(){t.remove();},2500);}
function collect(){Q.title=$('qTitle').value;Q.settings.age=$('qAge').value;Q.settings.tts=$('qTts').checked;Q.settings.playerDamage=($('qAge').value==='hard');Q.treasure.hint=$('qHint').value;Q.treasure.keyHint=$('qKeyHint').value;Q.treasure.code=$('qCode').value;
  document.querySelectorAll('.stage-row').forEach(function(row){var i=+row.dataset.i,s=Q.stages[i];s.zone=row.querySelector('[f=zone]').value;s.riddle=row.querySelector('[f=riddle]').value;s.name=row.querySelector('[f=name]').value;s.type=row.querySelector('[f=type]').value;s.point=[+row.querySelector('[f=px]').value,+row.querySelector('[f=py]').value];s.hp=+row.querySelector('[f=hp]').value;s.damagePerHit=+row.querySelector('[f=dmg]').value;s.dodge=+row.querySelector('[f=dodge]').value/100;s.hitbox=+row.querySelector('[f=hb]').value/100;s.emerge=+row.querySelector('[f=em]').value;s.hideInterval=+row.querySelector('[f=hi]').value;s.hideTime=+row.querySelector('[f=ht]').value;});
  var bb=document.querySelector('.boss-row');if(bb){Q.boss.name=bb.querySelector('[f=bname]').value;Q.boss.type='boss';Q.boss.hp=+bb.querySelector('[f=bhp]').value;Q.boss.damagePerHit=+bb.querySelector('[f=bdmg]').value;Q.boss.dodge=+bb.querySelector('[f=bdodge]').value/100;Q.boss.hitbox=+bb.querySelector('[f=bhb]').value/100;Q.boss.intro=bb.querySelector('[f=bintro]').value;}
}
function testBattle(key){collect();polish(Q);localStorage.setItem(LS_QUEST,JSON.stringify(Q));localStorage.setItem(LS_TEST,key);window.location.href='index.html';}
window.testBattle=testBattle;
function render(){$('qTitle').value=Q.title||'';$('qAge').value=Q.settings.age||'kid';$('qTts').checked=!!Q.settings.tts;$('qHint').value=Q.treasure.hint||'';$('qKeyHint').value=Q.treasure.keyHint||'';$('qCode').value=Q.treasure.code||'';
  var st=$('stages');st.innerHTML='';(Q.stages||[]).forEach(function(s,i){var d=document.createElement('div');d.className='stage-row';d.dataset.i=i;d.innerHTML=stageHTML(s,i);st.appendChild(d);d.querySelector('.del').onclick=function(){collect();Q.stages.splice(i,1);polish(Q);render();};d.querySelector('.test').onclick=function(){testBattle(String(i));};});
  var bs=$('bossBox');bs.innerHTML='';var bd=document.createElement('div');bd.className='boss-row';bd.innerHTML=bossHTML(Q.boss||{});bs.appendChild(bd);bd.querySelector('.test').onclick=function(){testBattle('boss');};
}
function typeSelect(cur){return '<select f="type">'+TYPES.map(function(t){return '<option value="'+t+'"'+(cur===t?' selected':'')+'>'+t+'</option>';}).join('')+'</select>';}
function num(label,val,attr,step){return '<label>'+label+'<input type="number" step="'+(step||1)+'" f="'+attr+'" value="'+val+'"></label>';}
function stageHTML(s,i){var last=(i===(Q.stages.length-1));var badge=last?' <span class="swatch" style="background:#fb7185"></span>МИНИ-БОСС':'';return '<div class="rowhead"><span class="lft"><strong>Этап '+(i+1)+' <span class="swatch" style="background:'+(TCOLOR[s.type]||'#888')+'"></span>'+(s.type||'')+badge+'</strong></span><span><button class="test" type="button">Тест боя</button> <button class="del" type="button">удалить</button></span></div>'+
 '<div class="grid2">'+
 '<label>Зона<input f="zone" value="'+(s.zone||'')+'"></label>'+
 '<label>Имя моба<input f="name" value="'+(s.name||'Костяш')+'"></label>'+
 '<label>Внешний вид'+typeSelect(s.type)+'</label>'+
 '<label>X карты<input f="px" type="number" step="0.1" value="'+(s.point?s.point[0]:1)+'"></label>'+
 '<label>Y карты<input f="py" type="number" step="0.1" value="'+(s.point?s.point[1]:1)+'"></label>'+
 num('HP',s.hp!=null?s.hp:100,'hp')+num('Урон',s.damagePerHit!=null?s.damagePerHit:20,'dmg')+
 num('Уклон %',Math.round((s.dodge!=null?s.dodge:0.28)*100),'dodge')+num('Хитбокс %',Math.round((s.hitbox!=null?s.hitbox:1.3)*100),'hb')+
 num('Выползание с',s.emerge!=null?s.emerge:1.4,'em',0.1)+num('Прятки каждые с',s.hideInterval!=null?s.hideInterval:6,'hi',0.5)+num('Прятки длит. с',s.hideTime!=null?s.hideTime:1.4,'ht',0.1)+
 '</div><label>Загадка<input f="riddle" value="'+(s.riddle||'')+'"></label>';}
function bossHTML(b){return '<div class="rowhead"><span class="lft"><strong>Босс (охраняет клад)</strong></span><span><button class="test" type="button">Тест боя</button></span></div><div class="grid2">'+
 '<label>Имя<input f="bname" value="'+(b.name||'Босс')+'"></label>'+
 num('HP',b.hp!=null?b.hp:300,'bhp')+num('Урон',b.damagePerHit!=null?b.damagePerHit:25,'bdmg')+
 num('Уклон %',Math.round((b.dodge!=null?b.dodge:0.4)*100),'bdodge')+num('Хитбокс %',Math.round((b.hitbox!=null?b.hitbox:1.1)*100),'bhb')+
 '</div><label>Реплика перед боем<input f="bintro" value="'+(b.intro||'')+'"></label>';}
function fallbackCv(cv,big,small){var g=cv.getContext('2d');g.fillStyle='#fff';g.fillRect(0,0,cv.width,cv.height);g.fillStyle='#0f172a';g.textAlign='center';g.textBaseline='middle';g.font='bold 92px sans-serif';g.fillText(String(big),cv.width/2,cv.height/2-18);g.font='bold 18px monospace';g.fillText(String(small||''),cv.width/2,cv.height/2+58);}
function printMarkers(){
  try{collect();polish(Q);}catch(e){}
  var area=$('printArea');area.innerHTML='';var stages=Q.stages||[];
  if(!stages.length){alert('Нет этапов для печати. Сначала добавь этапы.');return;}
  var tasks=[];
  function addCard(title, subtitle, payload, bigText){
    var card=document.createElement('div');card.className='mcard';
    card.innerHTML='<h3>'+title+'</h3><p>'+subtitle+'</p><canvas width="240" height="240"></canvas><div class="mc">'+payload+'</div>';
    area.appendChild(card);var cv=card.querySelector('canvas');
    tasks.push(makeQR(cv,payload));
  }
  addCard('СТАРТ КВЕСТА','Наведи камеру, не трогая карточку','THSTART','START');
  stages.forEach(function(s,i){
    addCard('Кусок карты '+(i+1),(s.zone||'')+' — '+(s.riddle||''),'THMARK:'+(i+1),String(i+1));
  });
  var go=function(){try{window.print();}catch(e){alert('Печать: нажми Ctrl+P вручную.');}};
  Promise.all(tasks).then(go).catch(go);
}
