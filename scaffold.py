#!/usr/bin/env python3
import sys, subprocess, shutil
from pathlib import Path
ROOT = Path.cwd()

def check_js(src, name):
    stack=[]; i=0; n=len(src); line=1
    in_s=None; in_lc=False; in_bc=False
    pairs={'}':'{', ')':'(', ']':'['}
    while i<n:
        c=src[i]
        if c=='\n': line+=1
        if in_lc:
            if c=='\n': in_lc=False
            i+=1; continue
        if in_bc:
            if c=='*' and i+1<n and src[i+1]=='/': in_bc=False; i+=2; continue
            i+=1; continue
        if in_s:
            if c=='\\': i+=2; continue
            if c==in_s: in_s=None
            i+=1; continue
        if c=='/' and i+1<n and src[i+1]=='/': in_lc=True; i+=2; continue
        if c=='/' and i+1<n and src[i+1]=='*': in_bc=True; i+=2; continue
        if c in '"\'`': in_s=c; i+=1; continue
        if c in '{([': stack.append((c,line)); i+=1; continue
        if c in '})]':
            if not stack: return f'{name}:{line}: лишняя закрывающая {c}'
            op,ln=stack.pop()
            if pairs[c]!=op: return f'{name}:{line}: {c} закрывает {op} (открыта на строке {ln})'
            i+=1; continue
        i+=1
    if stack:
        op,ln=stack[-1]
        return f'{name}: НЕЗАКРЫТАЯ {op} открыта на строке {ln}'
    return None

def validate_and_write(rel, content):
    content=content.lstrip('\n')
    if rel.endswith('.js'):
        err=check_js(content, rel)
        if err:
            print('SYNTAX FAIL ->', err); sys.exit(1)
        if shutil.which('node'):
            p=ROOT/rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding='utf-8')
            r=subprocess.run(['node','--check',str(p)], capture_output=True, text=True)
            if r.returncode!=0:
                print('NODE SYNTAX FAIL ->', r.stderr.strip()); sys.exit(1)
    p=ROOT/rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')
    print('created', rel)

def write(rel, content):
    validate_and_write(rel, content)

# ============================== index.html ==============================
write('index.html', r"""
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover"/>
<title>Voxel Treasure Hunt</title>
<link rel="manifest" href="./manifest.webmanifest"/>
<meta name="theme-color" content="#111827"/>
<link rel="icon" href="./public/icons/icon.svg" type="image/svg+xml"/>
<link rel="stylesheet" href="./styles.css"/>
<script src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js" defer></script>
</head>
<body>
<script>
(function(){
  var b=document.createElement('div'); b.id='diag';
  b.style.cssText='position:fixed;top:4px;left:4px;z-index:99999;background:rgba(0,0,0,.74);color:#86efac;font:11px/1.35 ui-monospace,Monaco,Consolas,monospace;padding:3px 7px;border-radius:6px;pointer-events:none;max-width:62vw;white-space:pre-wrap;box-shadow:0 2px 8px rgba(0,0,0,.45)';
  b.textContent='BOOT...'; document.body.appendChild(b);
  function set(t,c){ b.textContent=String(t); b.style.color=c||'#86efac'; }
  window.__diag=set;
  window.addEventListener('error',function(e){ set('ERR: '+(e.message||e.type)+(e.filename?(' @'+String(e.filename).split('/').pop()+':'+e.lineno):''),'#fca5a5'); });
  window.addEventListener('unhandledrejection',function(e){ var r=e.reason; set('REJ: '+((r&&(r.message||r.toString()))||r),'#fca5a5'); });
  document.addEventListener('pointerdown',function(e){ var t=(e.target&&e.target.closest)?e.target.closest('[data-action]'):null; if(t) set('TAP v '+t.getAttribute('data-action'),'#fde047'); },true);
  document.addEventListener('click',function(e){ var t=(e.target&&e.target.closest)?e.target.closest('[data-action]'):null; if(!t)return; var a=t.getAttribute('data-action'); set('CLICK > '+a,'#93c5fd'); if(window.TH&&window.TH.handleAction){ try{ window.TH.handleAction(a); }catch(err){ set('ACTION ERR ['+a+']: '+((err&&err.message)||err),'#fca5a5'); } } else { set('CLICK > '+a+'  (main.js не загрузился)','#fca5a5'); } });
  setTimeout(function(){ if(!window.TH) set('main.js НЕ инициализирован. Красный текст выше - причина.','#fca5a5'); },1200);
})();
</script>

<video id="camera" playsinline muted autoplay></video>
<canvas id="battle-canvas"></canvas>
<div id="inputLayer"></div>
<div id="damage-layer"></div>
<div id="reticle"><div id="chargeRing"></div><div class="cross-h"></div><div class="cross-v"></div></div>

<div id="scanOverlay" class="hidden">
  <div class="scan-top">
    <button data-action="map">Карта</button>
    <strong>AR-скан</strong>
    <button data-action="scan">Выключить</button>
  </div>
  <p class="scan-tip">Наведи камеру на QR-карточку, не трогая её. Скелет появится поверх реального фона.</p>
</div>

<div id="ui">
  <section id="menu" class="panel active">
    <h1>Voxel Treasure Hunt</h1>
    <p>Наведи телефон на стартовую карточку, найди маркеры, победи скелетов-лучников, собери карту сокровищ и открой клад.</p>
    <div class="buttons">
      <button data-action="scan">AR-скан / начать по карточке</button>
      <button data-action="map">Карта квартиры</button>
      <button data-action="mapCard">Карта сокровищ</button>
      <button data-action="collection">Коллекция скелетов</button>
      <button data-action="puzzleGo" id="btnPuzzle" class="hidden">Собрать пазл руками</button>
      <button data-action="bossGo" id="btnBoss" class="hidden">Бой с боссом</button>
      <button data-action="admin">Админка / настройки</button>
      <button data-action="reset">Сбросить прогресс</button>
    </div>
    <div class="small">Куски карты: <span id="fragmentCount">0/0</span> · Коллекция: <span id="collectionCount">0/0</span> · Режим: <span id="modeLabel">ребёнок 7 лет</span></div>
  </section>

  <section id="mapPanel" class="panel">
    <div class="panel-header">
      <button data-action="back">&larr; Меню</button>
      <strong>Карта квартиры</strong>
      <button data-action="scan" id="scanToggle">Скан: выкл</button>
      <button data-action="scanView">AR-вид</button>
    </div>
    <div id="mapViewport"><div id="mapWrap"><img id="mapImg" src="./quests/default/map.svg" alt="План"/><div id="mapDots"></div></div></div>
    <p id="riddle"></p>
    <p id="scanHint">Наведи телефон на QR-карточку, не трогая её. Скелет появится поверх камеры.</p>
  </section>

  <section id="mapCardPanel" class="panel">
    <div class="panel-header"><button data-action="back">&larr; Меню</button><strong>Карта сокровищ</strong>
      <button data-action="puzzleGo" id="mcPuzzle" class="hidden">Собрать пазл руками</button>
      <button data-action="bossGo" id="mcBoss" class="hidden">Бой с боссом</button>
    </div>
    <div id="treasureGrid"></div>
    <p id="mapCardInfo"></p>
  </section>

  <section id="collectionPanel" class="panel">
    <div class="panel-header"><button data-action="back">&larr; Меню</button><strong>Коллекция скелетов</strong></div>
    <div id="collectionGrid"></div>
    <p id="collectionInfo"></p>
  </section>

  <section id="puzzlePanel" class="panel">
    <div class="panel-header"><button data-action="mapCard">&larr; Карта</button><strong>Пазл карты</strong><button data-action="puzzleHint">Подсказка</button></div>
    <div id="puzzleBoard"></div>
    <div id="puzzleTray"></div>
    <p id="puzzleInfo">Перетащи куски в правильные клетки.</p>
  </section>

  <section id="treasurePanel" class="panel">
    <div class="panel-header"><button data-action="back">&larr; Меню</button><strong>Клад!</strong></div>
    <canvas id="fx-canvas"></canvas>
    <div id="treasureBox">
      <h2 id="treasureTitle">Карта собрана! Ищи ключ</h2>
      <p id="treasureKey" class="keyclue"></p>
      <p id="treasureHint"></p>
      <p id="treasureCode" class="code"></p>
      <button data-action="back">В меню</button>
    </div>
  </section>
</div>

<div id="battleHud">
  <div class="hp-wrap"><div id="stageLabel"></div><div class="hp-bar"><div id="hpFill"></div></div><div id="hpText"></div></div>
  <div id="playerHpWrap" class="hidden"><div class="phbar"><div id="playerHpFill"></div></div><span id="playerHpText"></span></div>
  <div id="enemyTag"><div class="ename" id="enemyName">Костяш</div><div class="ehp"><div id="enemyHpFill"></div></div></div>
  <div id="phaseLabel"></div>
  <div id="combo"></div>
  <div id="battleHint"></div>
  <button id="attackBtn">ДЕРЖИ / БРОСАЙ</button>
</div>

<div id="toast"></div>
<script src="./src/main.js"></script>
</body>
</html>
""")

# ============================== admin.html ==============================
write('admin.html', r"""
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Админка — Voxel Treasure Hunt</title>
<link rel="stylesheet" href="./admin.css"/>
<script src="https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js"></script>
</head>
<body>
<header><h1>Админка квеста</h1><div class="hrow"><button id="saveBtn">Сохранить (в браузер)</button><button id="exportBtn">Скачать quest.json</button><label class="filebtn">Импортировать<input type="file" id="importFile" accept="application/json" hidden></label><button id="printBtn">Печать QR-карточек</button><button id="openGameBtn">Открыть игру</button></div></header>
<main>
  <section class="card"><h2>Общее</h2>
    <label>Название квеста <input id="qTitle"></label>
    <label>Режим возраста
      <select id="qAge"><option value="kid">Ребёнок 7 лет (мягко)</option><option value="teen">Подросток 14 (сложнее)</option><option value="hard">Хардкор (урон игроку)</option></select>
    </label>
    <label><input type="checkbox" id="qTts"> Озвучка загадок и реплик (TTS)</label>
    <p class="note">Печатаются: стартовая карточка THSTART и карточки этапов THMARK:1..N. Кусков = числу этапов. Последний этап автоматически становится МИНИ-БОССом.</p>
    <label>Подсказка, где клад / сундук <input id="qHint"></label>
    <label>Финальная подсказка: где ключ / книга <textarea id="qKeyHint" rows="3"></textarea></label>
    <label>Код сундука <input id="qCode"></label>
  </section>
  <section class="card"><h2>Этапы (скелеты)</h2><div id="stages"></div><button id="addStage">+ добавить этап</button></section>
  <section class="card"><h2>Босс</h2><div id="bossBox"></div></section>
</main>
<div id="printArea"></div>
<script src="./src/admin.js"></script>
</body>
</html>
""")

# ============================== styles.css ==============================
write('styles.css', r"""
:root{--panel:rgba(15,23,42,.92);--text:#f8fafc;--accent:#38bdf8;--sb:env(safe-area-inset-bottom,0px);--st:env(safe-area-inset-top,0px)}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent;user-select:none;-webkit-user-select:none}
html{background:#0f172a}
html,body{margin:0;height:100%;overflow:hidden;color:var(--text);font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;touch-action:manipulation}
body{background:transparent}
#camera{position:fixed;inset:0;width:100%;height:100%;object-fit:cover;z-index:1;background:#05070d}
#battle-canvas{position:fixed;inset:0;width:100%;height:100%;z-index:2;touch-action:none;display:block;background:transparent}
#inputLayer{position:fixed;inset:0;z-index:3;display:none;touch-action:none}#inputLayer.active{display:block}
#battleHud{position:fixed;inset:0;z-index:4;display:none;pointer-events:none;padding:calc(12px + var(--st)) 12px calc(16px + var(--sb))}#battleHud.active{display:block}
#reticle{position:fixed;z-index:5;width:92px;height:92px;transform:translate(-50%,-50%);pointer-events:none;display:none;left:50%;top:50%}#reticle.active{display:block}
#damage-layer{position:fixed;inset:0;z-index:6;pointer-events:none}
#scanOverlay{position:fixed;inset:0;z-index:8;display:flex;flex-direction:column;justify-content:space-between;padding:calc(12px + var(--st)) 12px calc(16px + var(--sb));pointer-events:none;background:transparent}
#scanOverlay.hidden{display:none!important}
.scan-top{display:flex;justify-content:space-between;align-items:center;gap:8px;background:rgba(15,23,42,.76);border:2px solid rgba(255,255,255,.18);border-radius:16px;padding:8px 10px;pointer-events:auto}
.scan-top strong{font-size:15px}
.scan-top button{min-height:40px;padding:9px 12px;border-radius:12px;background:#e2e8f0;color:#0f172a;font-weight:900}
.scan-tip{align-self:center;max-width:min(92vw,560px);background:rgba(15,23,42,.76);border:2px solid rgba(255,255,255,.18);border-radius:16px;padding:10px 14px;pointer-events:auto;text-align:center;font-weight:800}
#chargeRing{position:absolute;inset:0;border-radius:50%;background:conic-gradient(from -90deg,#38bdf8 calc(var(--charge,0)*360deg),rgba(255,255,255,.12) 0);-webkit-mask:radial-gradient(farthest-side,transparent calc(100% - 10px),#000 calc(100% - 9px));mask:radial-gradient(farthest-side,transparent calc(100% - 10px),#000 calc(100% - 9px));opacity:0;transition:opacity .12s}#chargeRing.active{opacity:1}
.cross-h,.cross-v{position:absolute;background:rgba(255,255,255,.92);box-shadow:0 0 10px rgba(0,0,0,.9)}.cross-h{left:20px;right:20px;top:50%;height:3px;transform:translateY(-50%)}.cross-v{top:20px;bottom:20px;left:50%;width:3px;transform:translateX(-50%)}
.panel{position:fixed;inset:0;z-index:10;display:none;flex-direction:column;padding:calc(16px + var(--st)) 16px calc(16px + var(--sb));background:var(--panel);backdrop-filter:blur(8px);overflow:auto}.panel.active{display:flex}
#menu{align-items:center;justify-content:center;text-align:center;gap:18px}
h1{margin:0;font-size:clamp(28px,7vw,54px);line-height:1.05}p{margin:0;font-size:clamp(15px,4vw,22px);opacity:.9;max-width:680px}
.buttons{display:grid;gap:12px;width:min(100%,460px)}
button{appearance:none;border:0;border-radius:18px;padding:16px 18px;font:inherit;font-weight:800;color:#0f172a;background:var(--accent);box-shadow:0 8px 24px rgba(0,0,0,.25);min-height:56px;cursor:pointer}button:disabled{opacity:.45}.small{opacity:.75;font-size:14px}
.panel-header{display:flex;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap}.panel-header button{width:auto;min-height:44px;padding:10px 14px;background:#e2e8f0}
#mapViewport{width:100%;overflow:hidden;border:2px solid rgba(255,255,255,.18);border-radius:18px;background:rgba(255,255,255,.06)}#mapWrap{position:relative;transform-origin:top left}#mapImg{display:block;width:100%;height:auto;border-radius:16px}#mapDots{position:absolute;inset:0}
.map-dot{position:absolute;width:38px;height:38px;border-radius:50%;transform:translate(-50%,-50%);display:grid;place-items:center;padding:0;font-weight:900;background:#fbbf24;color:#111827;border:3px solid #fff;box-shadow:0 4px 12px rgba(0,0,0,.35);overflow:visible}
.map-dot.current{animation:pulse 1.2s infinite}
.map-dot.done{background:#475569;color:rgba(255,255,255,.30);border-color:#94a3b8;animation:none}
.map-dot.done::before,.map-dot.done::after{content:"";position:absolute;left:50%;top:50%;width:78%;height:16%;background:#ef4444;border-radius:4px;box-shadow:0 0 0 2px rgba(0,0,0,.35);pointer-events:none}
.map-dot.done::before{transform:translate(-50%,-50%) rotate(45deg)}
.map-dot.done::after{transform:translate(-50%,-50%) rotate(-45deg)}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(251,191,36,.7)}70%{box-shadow:0 0 0 16px rgba(251,191,36,0)}100%{box-shadow:0 0 0 0 rgba(251,191,36,0)}}
#riddle{margin-top:12px;font-weight:700;text-align:center}
#scanHint{margin-top:8px;opacity:.85;text-align:center;font-size:14px}
.hidden{display:none!important}
#treasureGrid{display:grid;gap:8px;width:min(100%,560px);margin:0 auto;aspect-ratio:3/2;border:3px solid rgba(255,255,255,.2);border-radius:14px;padding:8px;background:rgba(0,0,0,.25)}
.tcell{position:relative;border-radius:8px;overflow:hidden;border:2px dashed rgba(255,255,255,.22);background:rgba(255,255,255,.04);display:grid;place-items:center}
.tcell.filled{border-style:solid;border-color:#22c55e;background-size:100% 100%;background-position:center}
.tcell .tnum{font-weight:900;font-size:clamp(18px,5vw,30px);color:rgba(255,255,255,.4)}
.tcell .tlock{position:absolute;bottom:4px;right:6px;font-size:14px;opacity:.7}
.tcell.pop{animation:tilePop .6s cubic-bezier(.2,1.4,.4,1)}
@keyframes tilePop{0%{transform:scale(.2) rotate(-12deg);opacity:0;filter:brightness(2)}60%{transform:scale(1.12) rotate(3deg);opacity:1}100%{transform:scale(1) rotate(0);filter:brightness(1)}}
#mapCardInfo{text-align:center;font-weight:800;margin-top:10px}
#collectionGrid{display:grid;gap:10px;width:min(100%,680px);margin:0 auto;grid-template-columns:repeat(auto-fit,minmax(130px,1fr))}
.ccell{border:2px solid rgba(255,255,255,.18);border-radius:14px;padding:10px;text-align:center;background:rgba(255,255,255,.05);min-height:130px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px}
.ccell.done{border-color:#22c55e;box-shadow:0 0 18px rgba(34,197,94,.25)}
.csil{font-size:34px;line-height:1}
.cname{font-weight:900;font-size:14px}
.ctype{font-size:12px;opacity:.75}
#collectionInfo{text-align:center;font-weight:800;margin-top:10px}
#puzzleBoard{position:relative;width:min(100%,560px);margin:0 auto;border:3px solid rgba(255,255,255,.2);border-radius:14px;background:rgba(255,255,255,.04);touch-action:none}
.pcell{position:absolute;border:2px dashed rgba(255,255,255,.25);border-radius:8px;overflow:hidden}
.pcell .ghost{position:absolute;inset:0;opacity:.18;background-size:100% 100%}
.pcell.target{border-color:#fde047;box-shadow:0 0 0 3px rgba(253,224,71,.4) inset;animation:pulse 1s infinite}
.pcell.filled{border-style:solid;border-color:#22c55e}
.ppiece{border-radius:8px;background-size:100% 100%;box-shadow:0 4px 12px rgba(0,0,0,.4);cursor:grab;touch-action:none;border:2px solid rgba(255,255,255,.3)}
.ppiece.drag{cursor:grabbing;z-index:50;box-shadow:0 10px 30px rgba(0,0,0,.6)}
.ppiece.placed{cursor:default;border-color:#22c55e}
#puzzleTray{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-top:12px;min-height:90px;padding:8px;border:2px dashed rgba(255,255,255,.2);border-radius:14px}
#puzzleTray .ppiece{width:84px;height:56px}
#puzzleInfo{text-align:center;font-weight:700;margin-top:8px}
#treasurePanel{align-items:center;justify-content:center}#fx-canvas{position:fixed;inset:0;z-index:9;pointer-events:none}
#treasureBox{position:relative;z-index:11;text-align:center;display:grid;gap:14px;max-width:680px}#treasureBox h2{font-size:clamp(26px,7vw,44px);margin:0;color:#fde047}.keyclue{font-size:clamp(18px,5.2vw,30px);font-weight:900;color:#fde047;text-transform:uppercase;line-height:1.25;word-break:break-word;text-shadow:0 2px 10px rgba(0,0,0,.65)}#treasureBox .code{font-size:clamp(18px,4.5vw,26px);letter-spacing:2px;font-weight:900;color:#4ade80;word-break:break-word}
.hp-wrap{width:min(100%,620px);margin:0 auto;background:rgba(15,23,42,.72);border:2px solid rgba(255,255,255,.18);border-radius:18px;padding:10px 14px;text-align:center}
#stageLabel{font-weight:900;margin-bottom:6px}.hp-bar{height:18px;border-radius:999px;background:rgba(255,255,255,.18);overflow:hidden}#hpFill{height:100%;width:100%;background:#22c55e;transition:width .18s,background .18s}#hpText{margin-top:4px;font-variant-numeric:tabular-nums;font-weight:800}
#playerHpWrap{width:min(100%,360px);margin:8px auto 0;display:flex;align-items:center;gap:8px;justify-content:center}.phbar{flex:1;height:12px;border-radius:999px;background:rgba(255,255,255,.18);overflow:hidden}#playerHpFill{height:100%;width:100%;background:#38bdf8}#playerHpText{font-weight:800;font-size:13px}
#enemyTag{position:fixed;z-index:5;transform:translate(-50%,-100%);pointer-events:none;background:rgba(15,23,42,.78);border:2px solid rgba(255,255,255,.2);border-radius:14px;padding:6px 10px;text-align:center;display:none}#enemyTag.show{display:block}.ename{font-weight:900;font-size:14px;margin-bottom:4px}.ehp{width:92px;height:8px;border-radius:999px;background:rgba(255,255,255,.18);overflow:hidden}#enemyHpFill{height:100%;width:100%;background:#ef4444;transition:width .15s,background .15s}
#phaseLabel{position:fixed;left:50%;top:calc(150px + var(--st));transform:translateX(-50%);z-index:5;font-weight:900;font-size:clamp(14px,4vw,20px);color:#fde047;text-shadow:0 2px 6px #000;pointer-events:none;opacity:0;transition:opacity .2s}#phaseLabel.show{opacity:1}
#combo{position:fixed;right:16px;top:calc(88px + var(--st));z-index:5;font-weight:900;font-size:clamp(20px,5vw,34px);color:#fde047;text-shadow:0 0 8px #000,0 3px 0 #7c2d12;opacity:0;transform:scale(.8);transition:opacity .15s,transform .15s;pointer-events:none}#combo.show{opacity:1;transform:scale(1)}
#battleHint{position:fixed;left:50%;bottom:calc(118px + var(--sb));transform:translateX(-50%);z-index:5;pointer-events:none;font-weight:800;text-shadow:0 2px 8px #000;opacity:.92;text-align:center;width:min(92vw,560px)}
#attackBtn{position:absolute;left:50%;bottom:calc(24px + var(--sb));transform:translateX(-50%);pointer-events:auto;width:min(78vw,420px);min-height:76px;font-size:clamp(20px,5.5vw,32px);border-radius:28px;background:linear-gradient(180deg,#f97316,#dc2626);color:#fff;border:4px solid rgba(255,255,255,.85)}
.damage-number{position:absolute;transform:translate(-50%,-50%);font-size:clamp(30px,8vw,58px);font-weight:900;color:#fde047;text-shadow:0 0 6px #000,0 3px 0 #7c2d12,0 0 18px rgba(239,68,68,.65);animation:dmg 0.9s ease-out forwards;text-align:center;line-height:.95}.damage-number small{display:block;font-size:.45em;color:#fff;margin-top:2px}.damage-number.crit{color:#fb7185;font-size:clamp(36px,10vw,72px)}.damage-number.reflect{color:#4ade80}.damage-number.miss{color:#94a3b8;font-size:clamp(22px,6vw,40px)}
@keyframes dmg{0%{opacity:0;transform:translate(-50%,-35%) scale(.6)}15%{opacity:1;transform:translate(-50%,-55%) scale(1.18)}100%{opacity:0;transform:translate(-50%,-135%) scale(.9)}}
#toast{position:fixed;left:50%;bottom:calc(120px + var(--sb));transform:translateX(-50%);z-index:20;max-width:min(92vw,560px);padding:12px 16px;border-radius:16px;background:rgba(15,23,42,.92);border:2px solid rgba(255,255,255,.18);opacity:0;pointer-events:none;transition:opacity .2s,transform .2s;text-align:center;font-weight:700}#toast.show{opacity:1;transform:translateX(-50%) translateY(-6px)}
@media(min-width:760px){.map-dot{width:44px;height:44px}#battleHint{bottom:calc(126px + var(--sb))}}
""")

# ============================== admin.css ==============================
write('admin.css', r"""
*{box-sizing:border-box}body{margin:0;font-family:system-ui,Arial,sans-serif;background:#0f172a;color:#f8fafc}
header{position:sticky;top:0;background:#111827;border-bottom:2px solid #1f2937;padding:12px 16px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;z-index:5}
header h1{font-size:20px;margin:0}.hrow{display:flex;gap:8px;flex-wrap:wrap}
button,.filebtn{border:0;border-radius:12px;padding:10px 14px;font-weight:800;background:#38bdf8;color:#0f172a;cursor:pointer;font-size:14px}.filebtn{display:inline-block}
.note{font-size:13px;color:#94a3b8;margin:6px 0}
main{padding:16px;display:grid;gap:16px;max-width:1100px;margin:0 auto}
.card{background:#111827;border:2px solid #1f2937;border-radius:16px;padding:16px}
.card h2{margin:0 0 12px;font-size:18px}
label{display:block;margin:8px 0;font-size:14px}
input,select,textarea{width:100%;padding:10px;border-radius:10px;border:2px solid #334155;background:#0b1220;color:#f8fafc;font:inherit;margin-top:4px}
textarea{resize:vertical;min-height:70px}
input[type=checkbox]{width:auto}
.stage-row,.boss-row{border:2px solid #334155;border-radius:12px;padding:12px;margin-bottom:12px;background:#0b1220}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}
.rowhead{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;gap:8px;flex-wrap:wrap}
.rowhead .lft{display:flex;align-items:center;gap:8px}
.del{background:#ef4444;color:#fff;padding:6px 10px;border-radius:8px;font-size:12px}
.test{background:#22c55e;color:#06281a;padding:6px 10px;border-radius:8px;font-size:12px}
.swatch{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:middle;margin-right:6px;border:1px solid rgba(255,255,255,.3)}
#printArea{display:none}
@media print{header,main{display:none}#printArea{display:block}.mcard{width:105mm;height:148mm;border:2px dashed #999;border-radius:10px;padding:8mm;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;page-break-after:always;background:white;color:#111}.mcard h3{margin:0 0 6px}.mcard p{margin:0 0 10px;color:#334155;font-size:13px}.mcard canvas{display:block;width:58mm;height:58mm;background:#fff;border:1px solid #ddd;image-rendering:pixelated}.mcard .mc{margin-top:8px;font-family:monospace;font-size:11px;color:#64748b}}
""")

# ============================== src/main.js ==============================
write('src/main.js', r"""
'use strict';
var LS_QUEST='th_quest_v9', LS_PROG='th_prog_v9', LS_TEST='th_test_battle_v9';
var els={
  video:document.getElementById('camera'),canvas:document.getElementById('battle-canvas'),
  inputLayer:document.getElementById('inputLayer'),damageLayer:document.getElementById('damage-layer'),
  reticle:document.getElementById('reticle'),chargeRing:document.getElementById('chargeRing'),
  scanOverlay:document.getElementById('scanOverlay'),
  menu:document.getElementById('menu'),mapPanel:document.getElementById('mapPanel'),
  mapCardPanel:document.getElementById('mapCardPanel'),collectionPanel:document.getElementById('collectionPanel'),
  puzzlePanel:document.getElementById('puzzlePanel'),treasurePanel:document.getElementById('treasurePanel'),
  battleHud:document.getElementById('battleHud'),
  hpFill:document.getElementById('hpFill'),hpText:document.getElementById('hpText'),
  stageLabel:document.getElementById('stageLabel'),riddle:document.getElementById('riddle'),
  scanHint:document.getElementById('scanHint'),
  mapDots:document.getElementById('mapDots'),mapWrap:document.getElementById('mapWrap'),
  mapViewport:document.getElementById('mapViewport'),mapImg:document.getElementById('mapImg'),
  treasureGrid:document.getElementById('treasureGrid'),mapCardInfo:document.getElementById('mapCardInfo'),
  collectionGrid:document.getElementById('collectionGrid'),collectionInfo:document.getElementById('collectionInfo'),
  mcPuzzle:document.getElementById('mcPuzzle'),mcBoss:document.getElementById('mcBoss'),
  puzzleBoard:document.getElementById('puzzleBoard'),puzzleTray:document.getElementById('puzzleTray'),
  puzzleInfo:document.getElementById('puzzleInfo'),fxCanvas:document.getElementById('fx-canvas'),
  treasureTitle:document.getElementById('treasureTitle'),treasureKey:document.getElementById('treasureKey'),
  treasureHint:document.getElementById('treasureHint'),treasureCode:document.getElementById('treasureCode'),
  attackBtn:document.getElementById('attackBtn'),
  scanToggle:document.getElementById('scanToggle'),fragmentCount:document.getElementById('fragmentCount'),
  collectionCount:document.getElementById('collectionCount'),
  modeLabel:document.getElementById('modeLabel'),btnPuzzle:document.getElementById('btnPuzzle'),
  btnBoss:document.getElementById('btnBoss'),enemyTag:document.getElementById('enemyTag'),
  enemyName:document.getElementById('enemyName'),enemyHpFill:document.getElementById('enemyHpFill'),
  phaseLabel:document.getElementById('phaseLabel'),combo:document.getElementById('combo'),
  battleHint:document.getElementById('battleHint'),playerHpWrap:document.getElementById('playerHpWrap'),
  playerHpFill:document.getElementById('playerHpFill'),playerHpText:document.getElementById('playerHpText'),
  toast:document.getElementById('toast')
};
var ctx=els.canvas.getContext('2d');
var fxx=els.fxCanvas.getContext('2d');
var dpr=1,VW=0,VH=0,audioCtx=null,audioMaster=null,wakeLock=null,scanCanvas=null,scanCtx=null,scanFrame=0,scanCooldown=0;
var scanW=320,scanH=240;
var toastTimer=0,comboTimer=0,phaseTimer=0;
var CHARGE_TIME=850,ATTACK_CD=0.30,TEX_W=96,TEX_H=155;
var DODGE_OUT=0.55,DODGE_BACK=0.35,DODGE_AMP=0.9,DODGE_SQUASH=0.55;
var REVEAL_W=150,REVEAL_H=112;
var state={quest:null,stages:[],progress:{collected:[],puzzle:false,boss:false,types:[],defeated:0},scanner:false,battle:null,mode:'menu',cameraReady:false,lastTs:0,mobFrames:0,err:''};
var input={charging:false,pointerId:null,aimX:0,aimY:0,chargeStart:0,charge:0,fromButton:false,lastHit:0,combo:0};
var TTS=true, skelCache={}, TILES=[], TILE_IMG=[], GRID={cols:2,rows:2,n:0}, TILES_N=-1, TREASURE_IMG=null;
var jsQRLoadPromise=null;
function diag(t){ try{ if(window.__diag) window.__diag(t); }catch(e){} }

function DEFAULT_QUEST(){return{
  title:'Тайна хрущёвки',
  settings:{age:'kid',tts:true,playerDamage:false,haptics:true},
  map:{scale:60,width:6,height:5},
  stages:[
    {zone:'Прихожая',point:[0.8,0.8],riddle:'Где живут куртки и пахнет улицей',name:'Костяш',type:'bone',hp:100,damagePerHit:20,dodge:0.28,hitbox:1.3,emerge:1.4,hideInterval:6,hideTime:1.4},
    {zone:'Кухня',point:[3.2,1.0],riddle:'Там, где холодно и гудит',name:'Мшистый',type:'moss',hp:110,damagePerHit:20,dodge:0.3,hitbox:1.3,emerge:1.4,hideInterval:5.5,hideTime:1.3},
    {zone:'Комната',point:[3.5,3.2],riddle:'Где игрушки спят по ночам',name:'Ледяной',type:'azure',hp:120,damagePerHit:20,dodge:0.28,hitbox:1.3,emerge:1.5,hideInterval:6,hideTime:1.4},
    {zone:'Санузел',point:[0.8,2.2],riddle:'Где полотенца и вода',name:'Уголёк',type:'ember',hp:130,damagePerHit:22,dodge:0.26,hitbox:1.3,emerge:1.6,hideInterval:7,hideTime:1.2},
    {zone:'Коридор',point:[2.0,1.8],riddle:'Высокий тайник над головой',name:'Сумрак',type:'violet',hp:130,damagePerHit:22,dodge:0.32,hitbox:1.25,emerge:1.5,hideInterval:5,hideTime:1.3},
    {zone:'Комната',point:[5.0,4.0],riddle:'Финальный страж спрятался у окна',name:'Страж Врат',type:'armored',hp:220,damagePerHit:30,dodge:0.3,hitbox:1.25,emerge:1.6,hideInterval:6,hideTime:1.4,sizeMul:1.3,miniBoss:true}
  ],
  boss:{name:'Хранитель Клада',type:'boss',hp:360,damagePerHit:30,dodge:0.4,hitbox:1.1,sizeMul:1.35,intro:'Клад мой, никто не пройдёт!'},
  treasure:{hint:'Красный крест на карте - антресоль в коридоре. Там сундук.',keyHint:'КЛЮЧ К КАРТЕ НАХОДИТСЯ В УЧЕБНИКЕ «ОКРУЖАЮЩИЙ МИР»',code:'4-1-9-3-7-2'}
};}

function init(){ try{ window.TH={handleAction:handleAction}; }catch(e){ diag('TH fail: '+e.message); } boot(); }
async function boot(){
  try{ await loadQuest(); }catch(e){ diag('quest: '+e.message); setQuest(DEFAULT_QUEST()); }
  try{ loadProgress(); }catch(e){}
  try{ TTS=!!(state.quest.settings&&state.quest.settings.tts); }catch(e){}
  try{ ensureTiles(); }catch(e){ diag('tiles: '+e.message); }
  try{ buildMap(); }catch(e){ diag('map: '+e.message); }
  try{ bindBattleInput(); }catch(e){ diag('input: '+e.message); }
  try{ if(els.mapImg) els.mapImg.addEventListener('load',layoutMap); }catch(e){}
  try{ await startCamera(); }catch(e){}
  try{ resize(); }catch(e){ diag('resize: '+e.message); }
  try{ requestWakeLock(); }catch(e){}
  try{ state.lastTs=performance.now(); requestAnimationFrame(loop); }catch(e){ diag('loop: '+e.message); }
  try{ refreshMenu(); renderMapCard(); renderCollection(); }catch(e){ diag('menu: '+e.message); }
  try{ maybeTestBattle(); }catch(e){}
  diag('READY stages='+N()+' mode='+state.mode+' cam='+(state.cameraReady?'ON':'OFF'));
}
function setQuest(q){ ensureQuestPolish(q); state.quest=q; state.stages=(q&&q.stages)||[]; }
function ensureQuestPolish(q){
  ensureBossPolish(q);
  if(!q.treasure) q.treasure={};
  if(!q.treasure.keyHint) q.treasure.keyHint=q.treasure.hint||'КЛЮЧ К КАРТЕ НАХОДИТСЯ В УЧЕБНИКЕ «ОКРУЖАЮЩИЙ МИР»';
}
function ensureBossPolish(q){
  if(!q||!Array.isArray(q.stages))return;
  var L=q.stages.length;
  if(L>0){ var s=q.stages[L-1]; s.miniBoss=true; s.sizeMul=Math.max(s.sizeMul||1,1.3); }
  if(q.boss){ q.boss.sizeMul=Math.max(q.boss.sizeMul||1,1.35); }
}
async function loadQuest(){
  try{var s=localStorage.getItem(LS_QUEST);if(s){var q=JSON.parse(s);if(q&&Array.isArray(q.stages)&&q.stages.length>0){setQuest(q);return;}}}catch(e){}
  try{var r=await fetch('./quests/default/quest.json',{cache:'no-store'});if(r.ok){var fq=await r.json();if(fq&&Array.isArray(fq.stages)&&fq.stages.length>0){setQuest(fq);return;}}}catch(e){}
  setQuest(DEFAULT_QUEST());
}
function loadProgress(){
  try{
    var s=localStorage.getItem(LS_PROG);
    if(s){
      var p=JSON.parse(s);
      state.progress.collected=p.collected||[];
      state.progress.puzzle=!!p.puzzle;
      state.progress.boss=!!p.boss;
      state.progress.types=p.types||[];
      state.progress.defeated=p.defeated||0;
    }
  }catch(e){}
}
function saveProgress(){try{localStorage.setItem(LS_PROG,JSON.stringify(state.progress));}catch(e){}}
function N(){return (state.stages&&state.stages.length)||1;}
function ageMode(){return (state.quest&&state.quest.settings&&state.quest.settings.age)||'kid';}
function isKid(){return ageMode()==='kid';}
function playerDamageOn(){return ageMode()==='hard';}
function uniqueStageTypes(){var seen={},n=0;for(var i=0;i<state.stages.length;i++){var t=state.stages[i].type||'bone';if(!seen[t]){seen[t]=1;n++;}}return n||1;}
function maybeTestBattle(){try{var t=localStorage.getItem(LS_TEST);if(!t)return;localStorage.removeItem(LS_TEST);setTimeout(function(){if(t==='boss'){startBattle(state.quest.boss,true,-1,null);}else{var i=parseInt(t,10);if(state.stages[i])startBattle(state.stages[i],false,i,null);}},350);}catch(e){}}

function loadScript(src){ return new Promise(function(resolve,reject){ var s=document.createElement('script'); s.async=true; s.src=src; s.onload=function(){resolve();}; s.onerror=function(){reject(new Error('load '+src));}; document.head.appendChild(s); }); }
function ensureJsQR(){ if(typeof jsQR!=='undefined') return Promise.resolve(); if(!jsQRLoadPromise){ jsQRLoadPromise=loadScript('https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js').then(function(){ if(typeof jsQR==='undefined') throw new Error('jsQR not global'); }); } return jsQRLoadPromise; }

function startCamera(){if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){state.cameraReady=false;return Promise.resolve();}return navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:'environment'},width:{ideal:1280},height:{ideal:720}},audio:false}).then(function(st){els.video.srcObject=st;return els.video.play();}).then(function(){state.cameraReady=els.video.videoWidth>0;}).catch(function(){state.cameraReady=false;});}
function resize(){dpr=Math.min(window.devicePixelRatio||1,2);VW=window.innerWidth;VH=window.innerHeight;els.canvas.width=Math.round(VW*dpr);els.canvas.height=Math.round(VH*dpr);els.canvas.style.width=VW+'px';els.canvas.style.height=VH+'px';ctx.setTransform(dpr,0,0,dpr,0,0);els.fxCanvas.width=Math.round(VW*dpr);els.fxCanvas.height=Math.round(VH*dpr);els.fxCanvas.style.width=VW+'px';els.fxCanvas.style.height=VH+'px';fxx.setTransform(dpr,0,0,dpr,0,0);layoutMap();updateReticle();}

function palette(type){var P={bone:['#e8e1cf','#b3aa95','#3a352c'],moss:['#9ec98a','#5f8f57','#234018'],azure:['#9fd0ef','#5b8fb0','#163a52'],ember:['#f0a878','#b5623a','#5a2410'],violet:['#c9a8ef','#8a63b0','#3a1f55'],gold:['#f3d98a','#b08a3a','#5a4410'],armored:['#cdd6e4','#8a97ad','#2b3548'],boss:['#e8c87a','#8a6320','#3a2a08']};return P[type]||P.bone;}
function makeSkeletonCanvas(released,type){
  var c=document.createElement('canvas');c.width=TEX_W;c.height=TEX_H;var g=c.getContext('2d');g.imageSmoothingEnabled=false;
  function px(x,y,w,h,col){g.fillStyle=col;g.fillRect(x,y,w,h);}
  var pal=palette(type),B=pal[0],BD=pal[1],OUT=pal[2],CRK='#7a7263',WOOD='#7a4a28',WOOD_L='#a9683a',STRING='#d8c27a',SHAFT='#b98a4a',TIP='#cfd8dc',FEATHER='#b03a3a';
  var eyeCol=(type==='boss')?'#ff5a5a':(type==='ember'?'#ffb347':(type==='azure'?'#7dd3fc':(type==='violet'?'#c084fc':(type==='armored'?'#ff8a8a':OUT))));
  px(34,6,28,24,B);px(34,6,28,3,BD);px(32,10,2,16,B);px(62,10,2,16,B);
  px(40,14,6,7,eyeCol);px(50,14,6,7,eyeCol);px(46,22,4,4,CRK);
  var i;
  for(i=0;i<6;i++)px(38+i*4,27,3,3,i%2?BD:B);px(52,8,2,10,CRK);px(54,12,2,6,CRK);
  if(type==='moss'){px(32,2,32,5,BD);px(30,7,4,4,BD);px(62,7,4,4,BD);px(26,40,4,6,BD);px(66,40,4,6,BD);}
  if(type==='azure'){px(30,30,4,8,B);px(62,30,4,8,B);px(28,28,3,4,TIP);px(65,28,3,4,TIP);}
  if(type==='ember'){px(40,0,4,6,'#ff7a3c');px(48,-2,4,8,'#ffb347');px(54,0,4,6,'#ff7a3c');px(34,30,3,5,'#ff7a3c');px(59,30,3,5,'#ffb347');}
  if(type==='violet'){px(20,42,12,3,BD);px(16,46,10,3,BD);px(64,42,12,3,BD);px(70,46,10,3,BD);}
  if(type==='gold'){px(36,0,4,6,BD);px(44,-2,4,8,BD);px(52,0,4,6,BD);px(34,4,28,3,BD);}
  if(type==='armored'){px(32,2,32,6,BD);px(30,6,4,6,BD);px(62,6,4,6,BD);px(36,-2,4,6,BD);px(44,-4,4,8,BD);px(52,-2,4,6,BD);px(34,2,28,3,BD);}
  if(type==='boss'){px(32,-4,4,8,'#ffd700');px(42,-6,4,10,'#ffd700');px(52,-6,4,10,'#ffd700');px(60,-4,4,8,'#ffd700');px(30,2,36,4,'#b8860b');px(24,40,8,40,BD);px(64,40,8,40,BD);}
  px(46,30,4,4,BD);for(i=0;i<6;i++)px(45,34+i*4,6,3,i%2?B:BD);
  var ribs=[[36,40,24],[34,46,28],[36,52,24],[38,58,20]];
  ribs.forEach(function(r,idx){var x=r[0],y=r[1],w=r[2];px(x,y,w,3,B);px(x,y,3,3,BD);px(x+w-3,y,3,3,BD);if(idx<2){px(x-3,y+1,3,2,BD);px(x+w,y+1,3,2,BD);}});
  if(type==='armored'||type==='boss'||type==='gold'){px(40,42,16,18,BD);px(44,46,8,10,B);}
  px(40,64,16,4,BD);px(30,38,6,4,B);px(60,38,6,4,B);
  px(64,40,16,3,B);px(78,40,3,12,BD);px(32,40,4,12,B);px(30,50,6,3,BD);px(28,44,4,8,B);
  px(42,68,4,40,B);px(50,68,4,40,B);px(40,70,2,36,BD);px(54,70,2,36,BD);px(38,108,8,3,B);px(50,108,8,3,B);px(36,110,4,2,BD);px(56,110,4,2,BD);
  var bow=[[84,24],[88,34],[90,46],[90,58],[88,70],[84,80]];
  bow.forEach(function(b,idx){px(b[0],b[1],4,8,idx%2?WOOD:WOOD_L);});px(82,22,4,4,WOOD_L);px(82,80,4,4,WOOD_L);
  g.strokeStyle=STRING;g.lineWidth=1;
  if(!released){g.beginPath();g.moveTo(84,24);g.lineTo(30,50);g.lineTo(84,82);g.stroke();px(30,49,56,2,SHAFT);px(84,47,4,6,TIP);px(28,47,4,2,FEATHER);px(28,51,4,2,FEATHER);}
  else{g.beginPath();g.moveTo(84,24);g.lineTo(84,82);g.stroke();}
  return c;
}
function skelTex(t){var k='d'+t;if(!skelCache[k])skelCache[k]=makeSkeletonCanvas(false,t);return skelCache[k];}
function skelRelTex(t){var k='r'+t;if(!skelCache[k])skelCache[k]=makeSkeletonCanvas(true,t);return skelCache[k];}
function makeArrowCanvas(){var c=document.createElement('canvas');c.width=64;c.height=16;var g=c.getContext('2d');g.fillStyle='#b98a4a';g.fillRect(8,7,44,2);g.fillStyle='#cfd8dc';g.beginPath();g.moveTo(52,2);g.lineTo(62,8);g.lineTo(52,14);g.fill();g.fillStyle='#b03a3a';g.fillRect(4,4,6,2);g.fillRect(4,10,6,2);g.fillRect(8,7,4,2);return c;}
function makeSnowCanvas(){var c=document.createElement('canvas');c.width=32;c.height=32;var g=c.getContext('2d');g.fillStyle='#fff';g.beginPath();g.arc(16,16,13,0,7);g.fill();g.fillStyle='#bae6fd';g.beginPath();g.arc(12,12,4,0,7);g.fill();return c;}
function makeTreasureCanvas(){var c=document.createElement('canvas');c.width=REVEAL_W;c.height=REVEAL_H;var g=c.getContext('2d');g.fillStyle='#b8860b';g.fillRect(8,30,REVEAL_W-16,REVEAL_H-40);g.fillStyle='#d4a017';g.fillRect(8,30,REVEAL_W-16,18);g.strokeStyle='#5a3a08';g.lineWidth=4;g.strokeRect(8,30,REVEAL_W-16,REVEAL_H-40);g.fillStyle='#7a4a12';g.fillRect(REVEAL_W/2-10,44,20,26);g.fillStyle='#ffd700';g.beginPath();g.arc(REVEAL_W/2,52,6,0,7);g.fill();g.fillStyle='#3b2412';g.fillRect(REVEAL_W/2-2,52,4,10);g.fillStyle='#ffe08a';g.font='bold 14px sans-serif';g.textAlign='center';g.fillText('СОКРОВИЩЕ',REVEAL_W/2,24);return c;}
function loadTreasureImg(){if(TREASURE_IMG)return TREASURE_IMG;var c=makeTreasureCanvas();var im=new Image();im.src=c.toDataURL();TREASURE_IMG=im;return im;}
var arrowCv=makeArrowCanvas(),snowCv=makeSnowCanvas();

function gridFor(n){var opts=[[2,2],[2,3],[3,3],[2,4],[3,4],[4,4],[3,5],[4,5]],best=opts[0];for(var i=0;i<opts.length;i++){var o=opts[i];if(o[0]*o[1]===n)return o;if(Math.abs(o[0]*o[1]-n)<Math.abs(best[0]*best[1]-n))best=o;}return best;}
function mulberry(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function drawFullMap(g,W,H,seed){var rnd=mulberry(seed);g.fillStyle='#d9b877';g.fillRect(0,0,W,H);g.strokeStyle='rgba(107,68,35,0.25)';g.lineWidth=2;var i;for(i=0;i<40;i++){g.beginPath();g.moveTo(rnd()*W,0);g.lineTo(rnd()*W,H);g.stroke();}g.fillStyle='#bfe3c0';g.beginPath();g.moveTo(0,H*0.7);g.quadraticCurveTo(W*0.3,H*0.5,W*0.5,H*0.75);g.quadraticCurveTo(W*0.7,H*0.95,W,H*0.7);g.lineTo(W,H);g.lineTo(0,H);g.closePath();g.fill();g.fillStyle='#7fb069';for(i=0;i<8;i++){var x=rnd()*W,y=H*0.75+rnd()*H*0.2;g.beginPath();g.arc(x,y,8+rnd()*10,0,7);g.fill();}g.strokeStyle='#6b4423';g.lineWidth=4;g.strokeRect(6,6,W-12,H-12);var cx=W*0.62,cy=H*0.42;g.strokeStyle='#c0392b';g.lineWidth=8;g.beginPath();g.moveTo(cx-22,cy);g.lineTo(cx+22,cy);g.moveTo(cx,cy-22);g.lineTo(cx,cy+22);g.stroke();g.fillStyle='#3b2412';g.font='bold '+Math.round(H*0.07)+'px serif';g.textAlign='center';g.fillText('СОКРОВИЩЕ',W*0.5,H*0.16);}
function ensureTiles(){var n=N();if(TILES_N===n&&TILES.length)return;TILES_N=n;TILE_IMG=[];var g=gridFor(n),cols=g[0],rows=g[1];GRID={cols:cols,rows:rows,n:n};var full=document.createElement('canvas');full.width=cols*160;full.height=rows*120;drawFullMap(full.getContext('2d'),full.width,full.height,12345);TILES=[];for(var r=0;r<rows;r++)for(var c=0;c<cols;c++){var pc=document.createElement('canvas');pc.width=160;pc.height=120;pc.getContext('2d').drawImage(full,c*160,r*120,160,120,0,0,160,120);var url=pc.toDataURL();var idx=r*cols+c;TILES[idx]=url;var im=new Image();im.src=url;TILE_IMG[idx]=im;}}
function renderMapCard(){ensureTiles();els.treasureGrid.style.gridTemplateColumns='repeat('+GRID.cols+',1fr)';els.treasureGrid.innerHTML='';for(var i=0;i<GRID.n;i++){var cell=document.createElement('div');cell.className='tcell';cell.dataset.i=i;if(state.progress.collected.indexOf(i)>=0){cell.classList.add('filled');cell.style.backgroundImage='url('+TILES[i]+')';}else{cell.innerHTML='<span class="tnum">'+(i+1)+'</span><span class="tlock">🔒</span>';}els.treasureGrid.appendChild(cell);}updateMapCardInfo();}
function insertTileAnim(i){ensureTiles();var cell=els.treasureGrid.querySelector('.tcell[data-i="'+i+'"]');if(!cell)return;cell.classList.add('filled');cell.style.backgroundImage='url('+TILES[i]+')';cell.innerHTML='';cell.classList.remove('pop');void cell.offsetWidth;cell.classList.add('pop');sfx('chime');updateMapCardInfo();}
function updateMapCardInfo(){var got=state.progress.collected.length,total=N();els.mapCardInfo.textContent='Собрано кусков: '+got+' / '+total;if(got>=total&&!state.progress.puzzle){els.mapCardInfo.textContent='Все куски на месте! Жми Собрать пазл руками.';}else if(state.progress.puzzle&&!state.progress.boss){els.mapCardInfo.textContent='Карта собрана! Впереди Босс.';}els.mcPuzzle.classList.toggle('hidden',!(got>=total&&!state.progress.puzzle));els.mcBoss.classList.toggle('hidden',!(state.progress.puzzle&&!state.progress.boss));}
function renderCollection(){
  els.collectionGrid.innerHTML='';
  state.stages.forEach(function(s,i){
    var done=state.progress.collected.indexOf(i)>=0;
    var pal=palette(s.type||'bone');
    var cell=document.createElement('div');
    cell.className='ccell'+(done?' done':'');
    if(done) cell.style.background='linear-gradient(180deg,'+pal[0]+','+pal[1]+')';
    cell.innerHTML='<div class="csil">'+(done?'💀':'🔒')+'</div><div class="cname">'+(done?(s.name||('Скелет '+(i+1))):'Не найден')+'</div><div class="ctype">'+(done?(s.type||'bone'):'???')+'</div>';
    els.collectionGrid.appendChild(cell);
  });
  els.collectionInfo.textContent='Побеждено скелетов: '+(state.progress.defeated||0)+' / '+N()+' · Уникальных видов: '+(state.progress.types||[]).length+' / '+uniqueStageTypes();
}

function bindBattleInput(){
  els.attackBtn.addEventListener('pointerdown',function(e){e.preventDefault();beginCharge(VW/2,VH*0.5,true);});
  els.attackBtn.addEventListener('pointerup',function(e){e.preventDefault();releaseCharge();});
  els.attackBtn.addEventListener('pointercancel',releaseCharge);
  els.inputLayer.addEventListener('pointerdown',onPointerDown);els.inputLayer.addEventListener('pointermove',onPointerMove);els.inputLayer.addEventListener('pointerup',onPointerUp);els.inputLayer.addEventListener('pointercancel',onPointerUp);
  window.addEventListener('pointermove',function(e){if(state.mode==='battle'&&e.pointerType==='mouse'){input.aimX=e.clientX;input.aimY=e.clientY;updateReticle();}});
  window.addEventListener('pointerup',function(){if(input.charging&&input.fromButton)releaseCharge();});
  window.addEventListener('keydown',function(e){if(e.code==='Space'&&!e.repeat){e.preventDefault();beginCharge(VW/2,VH*0.5,true);}});
  window.addEventListener('keyup',function(e){if(e.code==='Space'){e.preventDefault();releaseCharge();}});
  document.addEventListener('pointerdown',resumeAudio,{once:true});
  window.addEventListener('resize',resize);window.addEventListener('orientationchange',function(){setTimeout(resize,250);});
  document.addEventListener('visibilitychange',function(){if(document.visibilityState==='visible'&&state.mode==='battle')requestWakeLock();});
}
function handleAction(a){resumeAudio();
  if(a==='map')setMode('map');
  else if(a==='mapCard'){ensureTiles();renderMapCard();setMode('mapCard');}
  else if(a==='collection'){renderCollection();setMode('collection');}
  else if(a==='back')setMode('menu');
  else if(a==='scan')toggleScanner();
  else if(a==='scanView'){ if(!state.scanner){ toggleScanner(); } else { setMode('scan'); } }
  else if(a==='admin')window.location.href='./admin.html';
  else if(a==='reset'){if(window.confirm('Сбросить прогресс ребёнка?')){state.progress={collected:[],puzzle:false,boss:false,types:[],defeated:0};saveProgress();refreshMenu();buildMap();renderMapCard();renderCollection();toast('Прогресс сброшен');}}
  else if(a==='puzzleGo'){ if(!state.stages.length){toast('Нет этапов');return;} openPuzzle(); }
  else if(a==='bossGo'){ if(!state.quest||!state.quest.boss){toast('Нет босса');return;} startBattle(state.quest.boss,true,-1,null); }
  else if(a==='puzzleHint')puzzleHint();
}
function setMode(m){state.mode=m;
  els.menu.classList.toggle('active',m==='menu');els.mapPanel.classList.toggle('active',m==='map');els.mapCardPanel.classList.toggle('active',m==='mapCard');els.collectionPanel.classList.toggle('active',m==='collection');els.puzzlePanel.classList.toggle('active',m==='puzzle');els.treasurePanel.classList.toggle('active',m==='treasure');
  els.battleHud.classList.toggle('active',m==='battle');els.inputLayer.classList.toggle('active',m==='battle');els.reticle.classList.toggle('active',m==='battle');
  els.scanOverlay.classList.toggle('hidden',m!=='scan');
  if(m!=='battle'){input.charging=false;input.fromButton=false;updateChargeUI(0);els.enemyTag.classList.remove('show');els.combo.classList.remove('show');els.phaseLabel.classList.remove('show');}
  else{input.aimX=VW/2;input.aimY=VH*0.45;updateReticle();}
  if(m==='map')layoutMap();if(m==='mapCard')renderMapCard();if(m==='collection')renderCollection();if(m==='treasure')startConfetti();else stopConfetti();
}
function refreshMenu(){
  els.fragmentCount.textContent=state.progress.collected.length+'/'+N();
  els.collectionCount.textContent=(state.progress.types||[]).length+'/'+uniqueStageTypes();
  els.modeLabel.textContent=ageMode()==='kid'?'ребёнок 7 лет':(ageMode()==='hard'?'хардкор':'подросток 14');
  var all=state.progress.collected.length>=N();
  els.btnPuzzle.classList.toggle('hidden',!(all&&!state.progress.puzzle));
  els.btnBoss.classList.toggle('hidden',!(state.progress.puzzle&&!state.progress.boss));
}
function toggleScanner(){
  if(state.scanner){
    state.scanner=false;
    els.scanToggle.textContent='Скан: выкл';
    if(state.mode==='scan') setMode('menu');
    toast('AR-скан выключен.');
    return;
  }
  if(!state.cameraReady){ startCamera(); }
  if(typeof jsQR==='undefined'){
    toast('Загружаю QR-сканер...');
    ensureJsQR().then(function(){
      state.scanner=true;
      els.scanToggle.textContent='Скан: вкл';
      setMode('scan');
      toast('AR-скан включён. Наведи на QR-карточку.');
      speak('Сканер включён. Наведи телефон на карточку.');
    }).catch(function(){
      toast('QR-сканер не загрузился. Проверь интернет/HTTPS.');
    });
    return;
  }
  state.scanner=true;
  els.scanToggle.textContent='Скан: вкл';
  setMode('scan');
  toast('AR-скан включён. Наведи на QR-карточку.');
  speak('Сканер включён. Наведи телефон на карточку.');
}

function buildMap(){if(!state.quest||!state.quest.map)return;els.mapDots.innerHTML='';var sc=state.quest.map.scale||60;els.mapWrap.style.width=(state.quest.map.width*sc)+'px';els.mapWrap.style.height=(state.quest.map.height*sc)+'px';
  state.stages.forEach(function(s,i){var d=document.createElement('button');d.className='map-dot';d.type='button';d.textContent=String(i+1);var pt=s.point||[1,1];d.style.left=(pt[0]*sc)+'px';d.style.top=(pt[1]*sc)+'px';d.addEventListener('click',function(){if(state.progress.collected.indexOf(i)>=0)toast('Кусок уже собран');else startBattle(s,false,i,null);});els.mapDots.appendChild(d);});
  updateMapDots();updateRiddle();layoutMap();
}
function layoutMap(){if(!els.mapViewport||!els.mapWrap)return;var av=els.mapViewport.clientWidth,na=els.mapWrap.offsetWidth||1,k=Math.min(1,av/na);els.mapWrap.style.transform='scale('+k+')';els.mapViewport.style.height=(els.mapWrap.offsetHeight*k)+'px';}
function updateMapDots(){var nx=nextUncollected();Array.prototype.forEach.call(els.mapDots.children,function(d,i){d.classList.toggle('done',state.progress.collected.indexOf(i)>=0);d.classList.toggle('current',i===nx&&state.progress.collected.indexOf(i)<0);});}
function updateRiddle(){
  var i=nextUncollected(),s=state.stages[i];
  if(s){
    els.riddle.textContent='Кусок '+(i+1)+': '+s.riddle;
    els.scanHint.textContent='Иди к этой зоне, наведи телефон на карточку THMARK:'+(i+1)+'. Не трогай карточку. Для прозрачного AR нажми «AR-вид».';
  } else {
    els.riddle.textContent='Все куски собраны!';
    els.scanHint.textContent='Открой карту сокровищ и собери пазл.';
  }
}
function nextUncollected(){for(var i=0;i<state.stages.length;i++){if(state.progress.collected.indexOf(i)<0)return i;}return 0;}

function normToScreen(nx,ny){
  if(!state.cameraReady||!els.video.videoWidth){return{x:VW*nx,y:VH*ny};}
  var vw=els.video.videoWidth, vh=els.video.videoHeight;
  var scale=Math.max(VW/vw,VH/vh);
  var dw=vw*scale, dh=vh*scale;
  var ox=(VW-dw)/2, oy=(VH-dh)/2;
  return{x:ox+nx*dw,y:oy+ny*dh};
}
function poseFromLoc(loc){
  if(!loc)return null;
  var pts=[[loc.topLeftX,loc.topLeftY],[loc.topRightX,loc.topRightY],[loc.bottomRightX,loc.bottomRightY],[loc.bottomLeftX,loc.bottomLeftY]];
  var minX=1e9,minY=1e9,maxX=-1e9,maxY=-1e9;
  for(var i=0;i<pts.length;i++){
    var nx=pts[i][0]/scanW, ny=pts[i][1]/scanH;
    var s=normToScreen(nx,ny);
    if(s.x<minX)minX=s.x; if(s.x>maxX)maxX=s.x;
    if(s.y<minY)minY=s.y; if(s.y>maxY)maxY=s.y;
  }
  var w=maxX-minX, h=maxY-minY;
  if(w<10||h<10)return null;
  return{x:(minX+maxX)/2,y:(minY+maxY)/2,w:w,h:h};
}
function setBattlePose(pose){
  var b=state.battle; if(!b||!pose)return;
  var now=performance.now();
  if(!b.pose){
    b.pose={valid:true,x:pose.x,y:pose.y,w:pose.w,h:pose.h,tx:pose.x,ty:pose.y,tw:pose.w,th:pose.h,lastUpdate:now,fade:1,lost:0};
  } else {
    b.pose.valid=true;
    b.pose.tx=pose.x; b.pose.ty=pose.y; b.pose.tw=pose.w; b.pose.th=pose.h;
    b.pose.lastUpdate=now;
  }
}
function handleStartMarker(){
  if(state.battle){toast('Сначала закончи текущий бой');return;}
  state.scanner=true;
  els.scanToggle.textContent='Скан: вкл';
  setMode('map');
  updateMapDots();
  updateRiddle();
  toast('Старт принят. Иди к точке 1 и наведи камеру на карточку. Для AR нажми «AR-вид».');
  speak('Квест начат. Ищи первую карточку.');
}

function curScale(){var b=state.battle;return (b&&b.params&&b.params.sizeMul)||1;}
function mobMetrics(){
  var b=state.battle;
  if(b && b.pose && b.pose.valid && b.pose.fade>0.02){
    var base=Math.max(90,b.pose.w);
    var th=clamp(base*2.6,190,VH*0.68)*(b.params.sizeMul||1);
    var tw=th*(TEX_W/TEX_H);
    var cx=b.pose.x;
    var cy=b.pose.y + b.pose.h*0.5 - th*0.5;
    return {cx:cx,cy:cy,tw:tw,th:th,baseY:b.pose.y+b.pose.h*0.5,fade:b.pose.fade};
  }
  var th2=Math.max(240,Math.min(VH*0.55,560))*curScale();
  return {cx:VW/2,cy:VH*0.46,tw:th2*(TEX_W/TEX_H),th:th2,baseY:VH*0.46+th2*0.5,fade:1};
}
function stageParams(s){var kid=isKid();
  return{hp:s.hp||100,dmg:s.damagePerHit||20,type:s.type||'bone',name:s.name||'Костяш',
    sizeMul:s.sizeMul||1, miniBoss:!!s.miniBoss,
    emerge:s.emerge!=null?s.emerge:1.4,
    hideInterval:s.hideInterval!=null?s.hideInterval:(kid?6:4.5),
    hideTime:s.hideTime!=null?s.hideTime:1.4,
    dodge:s.dodge!=null?s.dodge:(kid?0.28:0.5),
    hitbox:s.hitbox!=null?s.hitbox:(kid?1.3:1.0)};
}
function startBattle(stage,isBoss,index,pose){if(!stage){toast('Нет данных этапа');return;}clearBattle();var p=stageParams(stage);
  state.battle={stage:stage,isBoss:!!isBoss,index:index,params:p,hp:p.hp,maxHp:p.hp,playerHp:100,playerMax:100,
    sub:'emerging',t:0,cd:0,flash:0,stagger:0,kbx:0,kby:0,
    dodgePhase:'none',dodgeTimer:0,dodgeDir:1,dodgeOff:0,idleDodge:1.6+Math.random()*1.6,
    hideT:0,hideTimer:p.hideInterval,smokeAcc:0,vulnWin:0,
    arrows:[],arrowTimer:2.6,drewBow:0,snow:[],boom:[],imp:[],dust:[],smoke:[],
    deathParts:[],fire:[],smoke2:[],sparks:[],bang:0,reveal:null,deathT:0,pose:null,
    lootSpawned:false,autoCollect:0,collectT:0,shake:0,shakeMag:0,flashCol:null,flashT:0,deathBlur:0,
    texDraw:skelTex(p.type),texRel:skelRelTex(p.type)};
  if(pose) setBattlePose(pose);
  input.combo=0;input.lastHit=0;els.combo.classList.remove('show');state.mobFrames=0;
  setMode('battle');updateHUD();els.enemyName.textContent=p.name;els.playerHpWrap.classList.toggle('hidden',!playerDamageOn());
  spawnDust();sfx('spawn');var line=isBoss?(stage.intro||'Босс охраняет клад!'):(p.miniBoss?(stage.riddle||'Страж не пропустит!'):(stage.riddle||'Бой начался'));toast(line);speak(line);
  var tag=isBoss?'БОСС!':(p.miniBoss?'МИНИ-БОСС!':'Вылезает...');showPhase(tag);
  if(isBoss||p.miniBoss)sfx('roar');requestWakeLock();
}
function clearBattle(){var b=state.battle;if(!b)return;input.charging=false;input.fromButton=false;updateChargeUI(0);state.battle=null;}
function updateHUD(){var b=state.battle;if(!b)return;
  els.stageLabel.textContent=b.isBoss?'БОСС':(b.params.miniBoss?('МИНИ-БОСС · '+(b.params.name||'')):('Кусок '+(b.index+1)+'/'+N()));
  var pc=clamp01(b.hp/b.maxHp)*100;els.hpFill.style.width=pc+'%';els.hpFill.style.background=hpColor(pc);els.hpText.textContent=Math.max(0,Math.ceil(b.hp))+' / '+b.maxHp;els.attackBtn.disabled=b.sub!=='combat';
  if(playerDamageOn()){var pp=clamp01(b.playerHp/b.playerMax)*100;els.playerHpFill.style.width=pp+'%';els.playerHpText.textContent='Ты: '+Math.max(0,Math.ceil(b.playerHp));}
  var hint='';
  if(b.sub==='emerging') hint='Скелет выползает из карточки...';
  else if(b.sub==='combat') hint=(b.pose && b.pose.fade<0.65) ? 'Держи карточку в кадре!' : 'Держи кнопку / прицел — бросай в голову';
  else if(b.sub==='hiding') hint='Спрятался в дым — жди, он вылезет';
  else if(b.sub==='dying') hint='Разваливается!';
  else if(b.sub==='loot') hint='Тапни по куску карты';
  else if(b.sub==='collected') hint='Кусок улетает на карту';
  els.battleHint.textContent=hint;
}
function hpColor(p){return p>60?'#22c55e':p>30?'#eab308':'#ef4444';}
function clamp01(v){return Math.max(0,Math.min(1,v));}
function showPhase(t){els.phaseLabel.textContent=t;els.phaseLabel.classList.add('show');clearTimeout(phaseTimer);phaseTimer=setTimeout(function(){els.phaseLabel.classList.remove('show');},1200);}

function bodyRectRaw(){var b=state.battle,m=mobMetrics(),hs=b.params.hitbox;var ox=m.cx+b.kbx,oy=m.cy+b.kby;var w=m.tw*hs,h=m.th*hs;return{x:ox-w/2,y:oy-h/2,w:w,h:h};}
function currentBodyRect(){var b=state.battle,m=mobMetrics(),hs=b.params.hitbox;if(b.dodgePhase==='out')hs*=DODGE_SQUASH;var ox=m.cx+b.kbx+b.dodgeOff,oy=m.cy+b.kby;var w=m.tw*hs,h=m.th*hs;return{x:ox-w/2,y:oy-h/2,w:w,h:h,ox:ox,oy:oy};}
function zoneIn(rect,px,py){if(px<rect.x||px>rect.x+rect.w||py<rect.y||py>rect.y+rect.h)return'miss';var rel=(py-rect.y)/rect.h;if(rel<0.3)return'head';if(rel>0.72)return'legs';return'torso';}
function zoneAt(px,py){return zoneIn(currentBodyRect(),px,py);}

function onPointerDown(e){e.preventDefault();resumeAudio();var b=state.battle;if(!b)return;
  if(b.sub==='loot'){collectLoot();return;}
  if(b.sub==='combat'&&tryReflectArrow(e.clientX,e.clientY))return;
  if(b.sub!=='combat'||b.cd>0)return;
  input.pointerId=e.pointerId;els.inputLayer.setPointerCapture(e.pointerId);input.charging=true;input.fromButton=false;input.chargeStart=performance.now();input.aimX=e.clientX;input.aimY=e.clientY;updateReticle();}
function onPointerMove(e){if(e.pointerType==='mouse'){input.aimX=e.clientX;input.aimY=e.clientY;updateReticle();return;}if(!input.charging||e.pointerId!==input.pointerId)return;input.aimX=e.clientX;input.aimY=e.clientY;updateReticle();}
function onPointerUp(e){if(input.charging&&(e.pointerId===input.pointerId||e.type==='pointercancel'))releaseCharge();input.pointerId=null;}
function beginCharge(x,y,fb){var b=state.battle;if(!b||b.sub!=='combat'||b.cd>0)return;resumeAudio();input.charging=true;input.fromButton=!!fb;input.chargeStart=performance.now();input.aimX=x;input.aimY=y;updateReticle();}
function releaseCharge(){if(!input.charging)return;var ch=clamp01((performance.now()-input.chargeStart)/CHARGE_TIME);input.charging=false;input.fromButton=false;input.charge=0;updateChargeUI(0);throwSnow(ch);}
function updateReticle(){if(state.mode!=='battle')return;input.aimX=clamp(input.aimX,24,VW-24);input.aimY=clamp(input.aimY,90,VH-130);els.reticle.style.left=input.aimX+'px';els.reticle.style.top=input.aimY+'px';}
function updateChargeUI(c){els.chargeRing.style.setProperty('--charge',String(c));els.chargeRing.classList.toggle('active',c>0.02);}

function triggerDodge(b){b.dodgePhase='out';b.dodgeTimer=DODGE_OUT;b.dodgeDir=Math.random()<0.5?-1:1;sfx('swoosh');}
function throwSnow(ch){var b=state.battle;if(!b||b.sub!=='combat')return;b.cd=ATTACK_CD;
  if(Math.random()<b.params.dodge)triggerDodge(b);
  var aimed=zoneIn(bodyRectRaw(),input.aimX,input.aimY)!=='miss';
  b.snow.push({sx:VW/2,sy:VH+20,tx:input.aimX,ty:input.aimY,arc:120+ch*90,ch:ch,t:0,dur:0.34+ch*0.12,aimed:aimed});
  sfx('throw',ch);haptic(Math.round(8+ch*14));}
function snowPos(s){var x=s.t,inv=1-x;return{px:inv*inv*s.sx+2*inv*x*((s.sx+s.tx)/2)+x*x*s.tx,py:inv*inv*s.sy+2*inv*x*(Math.min(s.sy,s.ty)-s.arc)+x*x*s.ty};}
function updateSnow(b,dt){for(var i=b.snow.length-1;i>=0;i--){var s=b.snow[i];s.t+=dt/s.dur;if(s.t>=1){b.snow.splice(i,1);resolveHit(b,s);}}}
function resolveHit(b,s){
  if(b.sub==='emerging'){addImp(s.tx,s.ty,'#94a3b8',8);showDmg(s.tx,s.ty,0,'КОКОН','miss');sfx('miss');return;}
  if(b.sub==='hiding'){addImp(s.tx,s.ty,'#cbd5e1',10);showDmg(s.tx,s.ty,0,'СПРЯТАЛСЯ','miss');sfx('miss');return;}
  var zone=zoneAt(s.tx,s.ty);
  if(zone==='miss'){
    if(s.aimed&&b.dodgePhase!=='none'){addImp(s.tx,s.ty,'#fde047',12);showDmg(s.tx,s.ty,0,'УКЛОН!','miss');sfx('swoosh');input.combo=0;return;}
    addImp(s.tx,s.ty,'#94a3b8',10);showDmg(s.tx,s.ty,0,'МИМО','miss');sfx('miss');input.combo=0;return;
  }
  var base=b.params.dmg,mult=1,tag='';
  if(zone==='head'){mult*=1.6;tag='ГОЛОВА!';}else if(zone==='legs'){mult*=0.85;}
  if(b.vulnWin>0){mult*=1.5;tag=(tag?tag+' ':'')+'УЯЗВИМ!';}
  if(s.ch>=0.92){mult*=1.2;tag=(tag?tag+' ':'')+'МЕГА!';}
  var now=performance.now();input.combo=(now-input.lastHit<2500)?Math.min(12,input.combo+1):1;input.lastHit=now;
  var dmg=Math.max(3,Math.round(base*mult+Math.min(12,(input.combo-1)*2)));
  applyDamage(b,s.tx,s.ty,dmg,tag,zone==='head'?'#fde047':'#bae6fd');
}
function applyDamage(b,x,y,dmg,tag,color){b.hp-=dmg;b.flash=0.16;b.stagger=0.16;b.kbx+=(Math.random()-0.5)*6;b.kby-=4;showDmg(x,y,dmg,tag,tag?'crit':'');addImp(x,y,color,28);
  if(tag&&tag.indexOf('ГОЛОВА')>=0)sfx('crack');else sfx('thunk');haptic(28);
  if(input.combo>1){els.combo.textContent='x'+input.combo;els.combo.classList.add('show');clearTimeout(comboTimer);comboTimer=setTimeout(function(){els.combo.classList.remove('show');},1800);}
  b.flashCol='rgba(125,211,252,0.18)';b.flashT=0.10;updateHUD();if(b.hp<=0)die(b);}
function showDmg(x,y,a,tag,cls){var el=document.createElement('div');el.className='damage-number'+(cls?' '+cls:'');el.innerHTML=(a?a:'')+(tag?'<small>'+tag+'</small>':'');el.style.left=x+'px';el.style.top=y+'px';els.damageLayer.appendChild(el);setTimeout(function(){el.remove();},900);}

function updateArrows(b,dt){if(b.sub!=='combat')return;
  if(b.drewBow>0){b.drewBow-=dt;if(b.drewBow<=0)fireArrow(b);}else{b.arrowTimer-=dt;if(b.arrowTimer<=0){b.drewBow=0.5;b.arrowTimer=2.2+Math.random()*1.2;}}
  for(var i=b.arrows.length-1;i>=0;i--){var a=b.arrows[i];a.t+=dt/a.dur;if(a.t>=1){b.arrows.splice(i,1);arrowHit(b);}}}
function fireArrow(b){var m=mobMetrics();b.arrows.push({x0:m.cx+m.tw*0.42,y0:m.cy-m.th*0.05,x1:VW/2+(Math.random()-0.5)*VW*0.3,y1:VH*0.92,t:0,dur:1.15});sfx('loose');}
function arrowXY(a){var x=a.t,inv=1-x,cx=(a.x0+a.x1)/2,cy=Math.min(a.y0,a.y1)-60;return{px:inv*inv*a.x0+2*inv*x*cx+x*x*a.x1,py:inv*inv*a.y0+2*inv*x*cy+x*x*a.y1,sc:0.6+x*1.6,ang:Math.atan2(a.y1-a.y0,a.x1-a.x0)};}
function tryReflectArrow(sx,sy){var b=state.battle;if(!b||!b.arrows.length)return false;for(var i=b.arrows.length-1;i>=0;i--){var a=b.arrows[i],p=arrowXY(a);if(Math.hypot(p.px-sx,p.py-sy)<90){b.arrows.splice(i,1);input.combo=Math.min(12,input.combo+1);input.lastHit=performance.now();applyDamage(b,p.px,p.py,15+Math.round(input.combo*1.5),'ОТРАЖЕНО!','#4ade80');showDmg(p.px,p.py,0,'ОТРАЖЕНО!','reflect');return true;}}return false;}
function arrowHit(b){b.shake=0.3;b.shakeMag=10;b.flashCol='rgba(251,146,60,0.28)';b.flashT=0.16;sfx('whoosh');
  if(playerDamageOn()){b.playerHp-=12;updateHUD();var m=mobMetrics();showDmg(m.cx,m.cy-m.th*0.1,12,'ТЕБЯ!','crit');sfx('hurt');if(b.playerHp<=0)playerLose(b);}
  else{var m2=mobMetrics();showDmg(m2.cx,m2.cy-m2.th*0.1,0,'УКЛОН','miss');}}
function playerLose(b){toast('Тебя подловили! Пробуем ещё раз.');speak('Ничего, попробуем ещё раз');var st=b.stage,ib=b.isBoss,ix=b.index;setTimeout(function(){startBattle(st,ib,ix,null);},900);}

function die(b){b.sub='dying';b.t=0;b.deathT=0;b.lootSpawned=false;b.deathBlur=0.7;input.charging=false;updateChargeUI(0);spawnDeath(b);sfx('explode');haptic(80);updateHUD();showPhase(b.isBoss?'БОСС ПОВЕРЖЕН!':(b.params.miniBoss?'СТРАЖ ПОВЕРЖЕН!':'ПОБЕДА!'));if(b.isBoss)sfx('victory');}
function spawnDeath(b){
  var m=mobMetrics(),cx=m.cx,cy=m.cy,tw=m.tw,th=m.th,i;
  b.bang=1;b.shake=0.45;b.shakeMag=16;b.flashCol='rgba(255,210,120,0.55)';b.flashT=0.22;
  var defs=[
    ['skull',0,-0.34,0.16,0.16],
    ['rib',-0.06,-0.06,0.14,0.05],['rib',0.06,-0.02,0.14,0.05],['rib',-0.05,0.03,0.13,0.05],['rib',0.05,0.07,0.12,0.05],
    ['spine',0,-0.13,0.05,0.16],
    ['limb',-0.24,-0.02,0.05,0.16],['limb',0.24,-0.02,0.05,0.16],
    ['limb',-0.09,0.30,0.05,0.18],['limb',0.09,0.30,0.05,0.18],
    ['foot',-0.11,0.43,0.08,0.04],['foot',0.11,0.43,0.08,0.04],
    ['bow',0.30,-0.04,0.06,0.20],['arrow',0.12,-0.10,0.18,0.03]
  ];
  b.deathParts=[];
  for(i=0;i<defs.length;i++){
    var d=defs[i],ox=d[1]*tw,oy=d[2]*th,ang=Math.atan2(oy,ox)+(Math.random()-0.5)*0.8,sp=240+Math.random()*260;
    b.deathParts.push({shape:d[0],x:cx+ox,y:cy+oy,vx:Math.cos(ang)*sp,vy:Math.sin(ang)*sp-220,rot:Math.random()*6.3,rv:(Math.random()-0.5)*12,w:d[3]*tw,h:d[4]*th,life:0,ttl:1.1+Math.random()*0.6});
  }
  b.fire=[];
  for(i=0;i<6;i++){var fa=Math.random()*6.28,fd=Math.random()*tw*0.25;b.fire.push({x:cx+Math.cos(fa)*fd,y:cy+Math.sin(fa)*fd*0.6,r:18+Math.random()*22,vr:90+Math.random()*70,vy:-(60+Math.random()*90),life:0,ttl:0.5+Math.random()*0.4});}
  b.smoke2=[];
  for(i=0;i<9;i++){var sa=Math.random()*6.28,sd=Math.random()*tw*0.4;b.smoke2.push({x:cx+Math.cos(sa)*sd,y:cy+Math.sin(sa)*sd*0.5,r:14+Math.random()*16,vr:40+Math.random()*40,vx:(Math.random()-0.5)*40,vy:-(30+Math.random()*50),life:0,ttl:1.2+Math.random()*0.7});}
  b.sparks=[];
  for(i=0;i<46;i++){var pa=Math.random()*6.28,ps=160+Math.random()*340;b.sparks.push({x:cx,y:cy,vx:Math.cos(pa)*ps,vy:Math.sin(pa)*ps-120,life:0,ttl:0.4+Math.random()*0.5,col:Math.random()<0.5?'#ffd24a':'#ff7a1a'});}
  var img=b.isBoss?loadTreasureImg():(TILE_IMG[b.index]||null);
  b.reveal={img:img,ready:false,scale:0,rot:-0.6,t:0,x:cx,y:cy,label:b.isBoss?'СОКРОВИЩЕ!':('КУСОК КАРТЫ +'+(b.index+1))};
}
function updateDeath(b,dt){
  b.deathT+=dt;
  if(b.bang>0)b.bang=Math.max(0,b.bang-dt*4.5);
  var i,p;
  for(i=b.deathParts.length-1;i>=0;i--){p=b.deathParts[i];p.life+=dt;p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=980*dt;p.rot+=p.rv*dt;if(p.life>=p.ttl)b.deathParts.splice(i,1);}
  for(i=b.fire.length-1;i>=0;i--){p=b.fire[i];p.life+=dt;p.r+=p.vr*dt;p.y+=p.vy*dt;p.vy*=0.92;if(p.life>=p.ttl)b.fire.splice(i,1);}
  for(i=b.smoke2.length-1;i>=0;i--){p=b.smoke2[i];p.life+=dt;p.r+=p.vr*dt;p.x+=p.vx*dt;p.y+=p.vy*dt;if(p.life>=p.ttl)b.smoke2.splice(i,1);}
  for(i=b.sparks.length-1;i>=0;i--){p=b.sparks[i];p.life+=dt;p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=520*dt;if(p.life>=p.ttl)b.sparks.splice(i,1);}
  if(b.reveal){
    var rv=b.reveal;rv.t+=dt;
    if(!rv.ready&&rv.img&&rv.img.complete&&rv.img.naturalWidth>0)rv.ready=true;
    if(rv.t>0.12){var k=clamp01((rv.t-0.12)/0.5);rv.scale=easeOutBack(k);rv.rot=-0.6*(1-k);}
    if(b.sub==='collected'){rv.y-=dt*420;rv.scale=Math.max(0,rv.scale-dt*2.2);rv.rot+=dt*5;}
  }
}
function drawBonePart(g,p){
  var a=clamp01(1-p.life/p.ttl);g.globalAlpha=a;g.translate(p.x,p.y);g.rotate(p.rot);
  var w=p.w,h=p.h,L='#ece5d3',D='#b3aa95',O='#2a2620';
  if(p.shape==='skull'){g.fillStyle=L;g.beginPath();g.ellipse(0,0,w*0.5,h*0.5,0,0,7);g.fill();g.strokeStyle=O;g.lineWidth=2;g.stroke();g.fillStyle=O;g.beginPath();g.ellipse(-w*0.16,-h*0.08,w*0.12,h*0.14,0,0,7);g.fill();g.beginPath();g.ellipse(w*0.16,-h*0.08,w*0.12,h*0.14,0,0,7);g.fill();g.fillStyle=D;g.fillRect(-w*0.18,h*0.28,w*0.36,h*0.12);}
  else if(p.shape==='rib'){g.strokeStyle=L;g.lineWidth=Math.max(3,h*0.5);g.lineCap='round';g.beginPath();g.arc(0,0,w*0.5,0.2,Math.PI-0.2);g.stroke();g.strokeStyle=D;g.lineWidth=1;g.stroke();}
  else if(p.shape==='spine'){g.fillStyle=L;for(var s=0;s<3;s++){g.fillRect(-w*0.4,-h*0.4+s*h*0.3,w*0.8,h*0.22);}g.strokeStyle=O;g.lineWidth=1;g.strokeRect(-w*0.4,-h*0.4,w*0.8,h*0.8);}
  else if(p.shape==='limb'){g.fillStyle=L;g.fillRect(-w*0.3,-h*0.5,w*0.6,h);g.strokeStyle=O;g.lineWidth=1.5;g.strokeRect(-w*0.3,-h*0.5,w*0.6,h);g.fillStyle=D;g.beginPath();g.arc(0,-h*0.5,w*0.4,0,7);g.fill();g.beginPath();g.arc(0,h*0.5,w*0.4,0,7);g.fill();}
  else if(p.shape==='foot'){g.fillStyle=L;g.beginPath();g.ellipse(0,0,w*0.5,h*0.5,0,0,7);g.fill();g.strokeStyle=O;g.lineWidth=1.5;g.stroke();}
  else if(p.shape==='bow'){g.strokeStyle='#8a5a2a';g.lineWidth=Math.max(3,w*0.4);g.beginPath();g.arc(0,0,h*0.5,-1.1,1.1);g.stroke();g.strokeStyle='#d8c27a';g.lineWidth=1.5;g.beginPath();g.moveTo(Math.cos(-1.1)*h*0.5,Math.sin(-1.1)*h*0.5);g.lineTo(Math.cos(1.1)*h*0.5,Math.sin(1.1)*h*0.5);g.stroke();}
  else if(p.shape==='arrow'){g.fillStyle='#b98a4a';g.fillRect(-w*0.5,-h*0.3,w,h*0.6);g.fillStyle='#cfd8dc';g.beginPath();g.moveTo(w*0.5,-h*1.2);g.lineTo(w*0.7,0);g.lineTo(w*0.5,h*1.2);g.fill();g.fillStyle='#b03a3a';g.fillRect(-w*0.5,-h*0.8,w*0.18,h*1.6);}
  g.setTransform(dpr,0,0,dpr,0,0);
}
function drawBossAura(ox,oy,m,now){
  var pulse=0.5+0.5*Math.sin(now*5);
  ctx.save();ctx.globalCompositeOperation='lighter';
  var g=ctx.createRadialGradient(ox,oy,m.th*0.2,ox,oy,m.th*0.7);
  g.addColorStop(0,'rgba(120,20,40,0)');
  g.addColorStop(0.7,'rgba(180,30,60,'+(0.12+0.10*pulse)+')');
  g.addColorStop(1,'rgba(80,10,30,0)');
  ctx.fillStyle=g;ctx.beginPath();ctx.ellipse(ox,oy,m.tw*0.8,m.th*0.7,0,0,7);ctx.fill();
  ctx.globalAlpha=0.4+0.4*pulse;ctx.lineWidth=3;ctx.strokeStyle='#fb7185';
  ctx.beginPath();ctx.ellipse(ox,oy,m.tw*0.78,m.th*0.66,0,0,7);ctx.stroke();
  ctx.restore();
}
function drawDeath(b,now){
  var i,p,a,rv=b.reveal;
  ctx.save();
  for(i=0;i<b.smoke2.length;i++){p=b.smoke2[i];a=clamp01(1-p.life/p.ttl)*0.45;ctx.globalAlpha=a;var sg=ctx.createRadialGradient(p.x,p.y,1,p.x,p.y,p.r);sg.addColorStop(0,'rgba(120,120,130,0.9)');sg.addColorStop(1,'rgba(60,60,70,0)');ctx.fillStyle=sg;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,7);ctx.fill();}
  ctx.restore();
  for(i=0;i<b.deathParts.length;i++){ctx.save();drawBonePart(ctx,b.deathParts[i]);ctx.restore();}
  ctx.save();ctx.globalCompositeOperation='lighter';
  for(i=0;i<b.fire.length;i++){p=b.fire[i];a=clamp01(1-p.life/p.ttl);var fg=ctx.createRadialGradient(p.x,p.y,1,p.x,p.y,p.r);fg.addColorStop(0,'rgba(255,255,235,'+a+')');fg.addColorStop(0.35,'rgba(255,200,70,'+(a*0.9)+')');fg.addColorStop(0.7,'rgba(255,110,20,'+(a*0.6)+')');fg.addColorStop(1,'rgba(180,30,0,0)');ctx.fillStyle=fg;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,7);ctx.fill();}
  for(i=0;i<b.sparks.length;i++){p=b.sparks[i];a=clamp01(1-p.life/p.ttl);ctx.globalAlpha=a;ctx.fillStyle=p.col;ctx.fillRect(p.x-1.5,p.y-1.5,3,3);}
  if(b.bang>0.02){var br=(1-b.bang)*Math.max(VW,VH)*0.7+40;var bg=ctx.createRadialGradient(rv?rv.x:VW/2,rv?rv.y:VH/2,1,rv?rv.x:VW/2,rv?rv.y:VH/2,br);bg.addColorStop(0,'rgba(255,255,255,'+(b.bang*0.9)+')');bg.addColorStop(0.4,'rgba(255,200,90,'+(b.bang*0.6)+')');bg.addColorStop(1,'rgba(255,120,20,0)');ctx.globalAlpha=1;ctx.fillStyle=bg;ctx.beginPath();ctx.arc(rv?rv.x:VW/2,rv?rv.y:VH/2,br,0,7);ctx.fill();}
  ctx.restore();
  if(rv&&rv.scale>0.02){
    ctx.save();ctx.translate(rv.x,rv.y);ctx.rotate(rv.rot);ctx.scale(rv.scale,rv.scale);
    var pulse=0.5+0.5*Math.sin(now*7);
    ctx.shadowColor='rgba(255,180,60,'+(0.6+0.4*pulse)+')';ctx.shadowBlur=24+10*pulse;
    ctx.strokeStyle='rgba(253,224,71,'+(0.5+0.5*pulse)+')';ctx.lineWidth=3;ctx.beginPath();ctx.arc(0,0,REVEAL_W*0.72,0,7);ctx.stroke();
    if(rv.ready&&rv.img){ctx.imageSmoothingEnabled=false;ctx.drawImage(rv.img,-REVEAL_W/2,-REVEAL_H/2,REVEAL_W,REVEAL_H);}
    else{ctx.fillStyle='#d4a017';ctx.fillRect(-REVEAL_W/2,-REVEAL_H/2,REVEAL_W,REVEAL_H);ctx.strokeStyle='#5a3a08';ctx.lineWidth=4;ctx.strokeRect(-REVEAL_W/2,-REVEAL_H/2,REVEAL_W,REVEAL_H);}
    ctx.shadowBlur=0;ctx.restore();
    ctx.save();ctx.globalAlpha=clamp01(rv.scale);ctx.fillStyle='#fde047';ctx.font='bold 16px system-ui,sans-serif';ctx.textAlign='center';ctx.strokeStyle='rgba(0,0,0,0.8)';ctx.lineWidth=3;ctx.strokeText(rv.label,rv.x,rv.y+REVEAL_H/2*rv.scale+22);ctx.fillText(rv.label,rv.x,rv.y+REVEAL_H/2*rv.scale+22);ctx.restore();
  }
}

function spawnDust(){var b=state.battle,m=mobMetrics();if(!b)return;for(var i=0;i<38;i++)b.dust.push({x:m.cx+(Math.random()-0.5)*m.tw,y:m.baseY-10,vx:(Math.random()-0.5)*60,vy:-(40+Math.random()*90),life:0,ttl:0.95});}
function updateDust(b,dt){for(var i=b.dust.length-1;i>=0;i--){var p=b.dust[i];p.life+=dt;p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=60*dt;if(p.life>=p.ttl)b.dust.splice(i,1);}}
function addImp(x,y,col,n){var b=state.battle;if(!b)return;for(var i=0;i<n;i++){var a=Math.random()*6.28,sp=60+Math.random()*180;b.imp.push({x:x,y:y,vx:Math.cos(a)*sp,vy:Math.sin(a)*sp-60,life:0,ttl:0.45,col:col});}}
function updateImp(b,dt){for(var i=b.imp.length-1;i>=0;i--){var p=b.imp[i];p.life+=dt;p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=500*dt;if(p.life>=p.ttl)b.imp.splice(i,1);}}
function spawnSmoke(b,n){var m=mobMetrics();if(!b.smoke)b.smoke=[];for(var i=0;i<(n||6);i++){b.smoke.push({x:m.cx+(Math.random()-0.5)*m.tw*0.8,y:m.baseY-m.th*0.15+Math.random()*m.th*0.25,vx:(Math.random()-0.5)*30,vy:-(20+Math.random()*40),r:8+Math.random()*10,life:0,ttl:1.1+Math.random()*0.6});}}
function updateSmoke(b,dt){if(!b.smoke)return;for(var i=b.smoke.length-1;i>=0;i--){var p=b.smoke[i];p.life+=dt;p.x+=p.vx*dt;p.y+=p.vy*dt;p.r+=14*dt;if(p.life>=p.ttl)b.smoke.splice(i,1);}}

function collectLoot(){var b=state.battle;if(!b||b.sub!=='loot')return;b.sub='collected';b.collectT=0;
  if(b.index>=0&&state.progress.collected.indexOf(b.index)<0){
    state.progress.collected.push(b.index);
    state.progress.defeated=(state.progress.defeated||0)+1;
    var ty=b.params.type||'bone';
    if(!state.progress.types) state.progress.types=[];
    if(state.progress.types.indexOf(ty)<0) state.progress.types.push(ty);
    saveProgress();
  }
  sfx('collect');haptic(35);refreshMenu();updateMapDots();updateRiddle();renderCollection();
}

function tickTimers(b,dt){
  b.cd=Math.max(0,b.cd-dt);
  if(b.flash>0)b.flash-=dt;
  if(b.stagger>0)b.stagger-=dt;
  if(b.shake>0)b.shake-=dt;
  if(b.flashT>0)b.flashT-=dt;
  if(b.deathBlur>0)b.deathBlur-=dt;
  if(b.vulnWin>0)b.vulnWin-=dt;
  b.kbx*=Math.exp(-8*dt);
  b.kby*=Math.exp(-8*dt);
}
function tickDodge(b,dt){
  if(b.dodgePhase==='out'){
    b.dodgeTimer-=dt;
    b.dodgeOff=b.dodgeDir*mobMetrics().tw*DODGE_AMP;
    if(b.dodgeTimer<=0){b.dodgePhase='back';b.dodgeTimer=DODGE_BACK;}
    return;
  }
  if(b.dodgePhase==='back'){
    b.dodgeTimer-=dt;
    var k=clamp01(b.dodgeTimer/DODGE_BACK);
    b.dodgeOff=b.dodgeDir*mobMetrics().tw*DODGE_AMP*k;
    if(b.dodgeTimer<=0){b.dodgePhase='none';b.dodgeOff=0;}
    return;
  }
  b.dodgeOff=0;
}
function phaseMachine(b,dt){
  if(b.sub==='emerging'){
    b.t+=dt; b.hp=b.maxHp;
    if(b.t>=b.params.emerge){b.sub='combat';b.t=0;b.vulnWin=0.8;showPhase('В БОЮ!');sfx('shimmer');}
    return;
  }
  if(b.sub==='combat'){
    b.idleDodge-=dt;
    if(b.idleDodge<=0){triggerDodge(b);b.idleDodge=1.8+Math.random()*1.8;}
    b.hideTimer-=dt;
    if(b.hideTimer<=0){b.sub='hiding';b.hideT=b.params.hideTime;b.hideTimer=b.params.hideInterval+Math.random()*1.5;b.smokeAcc=0;spawnSmoke(b,14);showPhase('СПРЯТАЛСЯ');sfx('poof');}
    return;
  }
  if(b.sub==='hiding'){
    b.hideT-=dt;
    b.hp=Math.min(b.maxHp,b.hp+b.maxHp*0.4*dt);
    b.smokeAcc-=dt;
    if(b.smokeAcc<=0){spawnSmoke(b,4);b.smokeAcc=0.2;}
    if(b.hideT<=0){b.sub='combat';b.vulnWin=0.8;showPhase('ВЫЛЕЗ!');sfx('shimmer');}
    return;
  }
  if(b.sub==='dying'){
    b.t+=dt;
    if(b.t>0.55){b.sub='loot';b.autoCollect=0;}
    return;
  }
  if(b.sub==='loot'){
    b.autoCollect+=dt;
    var lim=b.isBoss?1.0:3.0;
    if(b.autoCollect>lim)collectLoot();
    return;
  }
  if(b.sub==='collected'){
    b.collectT+=dt;
    if(b.collectT>0.5)finishBattle(b);
    return;
  }
}
function finishBattle(b){
  var wasBoss=b.isBoss, idx=b.index;
  clearBattle();
  if(wasBoss){state.progress.boss=true;saveProgress();openTreasure();return;}
  if(idx>=0)insertTileAnim(idx);
  renderMapCard();refreshMenu();setMode('mapCard');
  if(state.progress.collected.length>=N()){toast('Все куски собраны! Собирай пазл.');speak('Все куски карты собраны. Теперь собери пазл!');}
  else{toast('Кусок вставлен в карту. Следующая точка.');}
}
function updateBattle(dt){
  var b=state.battle; if(!b) return;
  tickTimers(b,dt);
  tickDodge(b,dt);
  if(b.pose && b.pose.valid){
    var now=performance.now();
    b.pose.lost=(now-b.pose.lastUpdate)/1000;
    b.pose.fade = b.pose.lost < 2 ? 1 : Math.max(0, 1 - (b.pose.lost-2)/2);
    b.pose.x += (b.pose.tx-b.pose.x)*0.18;
    b.pose.y += (b.pose.ty-b.pose.y)*0.18;
    b.pose.w += (b.pose.tw-b.pose.w)*0.18;
    b.pose.h += (b.pose.th-b.pose.h)*0.18;
  }
  if(input.charging){input.charge=clamp01((performance.now()-input.chargeStart)/CHARGE_TIME);updateChargeUI(input.charge);}
  updateSnow(b,dt);updateArrows(b,dt);updateImp(b,dt);updateDust(b,dt);updateSmoke(b,dt);
  phaseMachine(b,dt);
  if(b.sub==='dying'||b.sub==='loot'||b.sub==='collected')updateDeath(b,dt);
  updateHUD();updateEnemyTag(b);
}
function updateEnemyTag(b){if(b.sub==='dying'||b.sub==='loot'||b.sub==='collected'){els.enemyTag.classList.remove('show');return;}var m=mobMetrics();var pc=clamp01(b.hp/b.maxHp)*100;els.enemyTag.classList.add('show');els.enemyTag.style.left=m.cx+'px';els.enemyTag.style.top=(m.cy-m.th/2-6)+'px';els.enemyHpFill.style.width=pc+'%';els.enemyHpFill.style.background=hpColor(pc);}

var PZ={cells:[],pieces:[],cw:0,ch:0};
function openPuzzle(){setMode('puzzle');ensureTiles();var n=N(),cols=GRID.cols,rows=GRID.rows;els.puzzleBoard.innerHTML='';els.puzzleTray.innerHTML='';PZ.cells=[];PZ.pieces=[];var bw=els.puzzleBoard.clientWidth||540,ratio=(rows*120)/(cols*160);els.puzzleBoard.style.height=Math.round(bw*ratio)+'px';var cw=bw/cols,ch=(bw*ratio)/rows;PZ.cw=cw;PZ.ch=ch;
  for(var r=0;r<rows;r++)for(var c=0;c<cols;c++){var cell=document.createElement('div');cell.className='pcell';cell.style.left=(c*cw)+'px';cell.style.top=(r*ch)+'px';cell.style.width=cw+'px';cell.style.height=ch+'px';var gh=document.createElement('div');gh.className='ghost';gh.style.backgroundImage='url('+TILES[r*cols+c]+')';cell.appendChild(gh);els.puzzleBoard.appendChild(cell);PZ.cells.push({el:cell,idx:r*cols+c,cx:c*cw+cw/2,cy:r*ch+ch/2});}
  var order=[];for(var k=0;k<n;k++)order.push(k);for(var i=order.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var tmp=order[i];order[i]=order[j];order[j]=tmp;}
  order.forEach(function(pi){var el=document.createElement('div');el.className='ppiece';el.style.backgroundImage='url('+TILES[pi]+')';els.puzzleTray.appendChild(el);var p={el:el,idx:pi,placed:false};PZ.pieces.push(p);wirePiece(p);});
  els.puzzleInfo.textContent='Осталось кусков: '+n;
}
function wirePiece(p){var drag=false,ox=0,oy=0;
  p.el.addEventListener('pointerdown',function(e){if(p.placed)return;e.preventDefault();drag=true;p.el.classList.add('drag');p.el.setPointerCapture(e.pointerId);var rc=p.el.getBoundingClientRect();ox=e.clientX-rc.left;oy=e.clientY-rc.top;p.el.style.position='fixed';p.el.style.left=rc.left+'px';p.el.style.top=rc.top+'px';p.el.style.width=rc.width+'px';p.el.style.height=rc.height+'px';document.body.appendChild(p.el);highlightTarget(p.idx);sfx('pickup');});
  p.el.addEventListener('pointermove',function(e){if(!drag)return;p.el.style.left=(e.clientX-ox)+'px';p.el.style.top=(e.clientY-oy)+'px';});
  p.el.addEventListener('pointerup',function(e){if(!drag)return;drag=false;p.el.classList.remove('drag');var rc=p.el.getBoundingClientRect();var cx=rc.left+rc.width/2,cy=rc.top+rc.height/2;var br=els.puzzleBoard.getBoundingClientRect();var cell=PZ.cells[p.idx];var tcx=br.left+cell.cx,tcy=br.top+cell.cy;var snap=Math.max(PZ.cw,PZ.ch)*0.6;if(Math.hypot(cx-tcx,cy-tcy)<snap){placePiece(p,cell);sfx('place');afterPlace();}else{returnToTray(p);}unhighlight();});
  p.el.addEventListener('pointercancel',function(){drag=false;p.el.classList.remove('drag');returnToTray(p);unhighlight();});
}
function placePiece(p,cell){p.placed=true;p.el.classList.add('placed');p.el.style.position='absolute';p.el.style.left='0';p.el.style.top='0';p.el.style.width=PZ.cw+'px';p.el.style.height=PZ.ch+'px';cell.el.appendChild(p.el);cell.el.classList.add('filled');}
function returnToTray(p){p.el.style.position='relative';p.el.style.left='';p.el.style.top='';p.el.style.width='84px';p.el.style.height='56px';els.puzzleTray.appendChild(p.el);}
function highlightTarget(idx){var c=PZ.cells[idx];if(c)c.el.classList.add('target');}
function unhighlight(){PZ.cells.forEach(function(c){c.el.classList.remove('target');});}
function afterPlace(){var left=PZ.pieces.filter(function(p){return !p.placed;}).length;els.puzzleInfo.textContent='Осталось кусков: '+left;if(left===0){state.progress.puzzle=true;saveProgress();refreshMenu();sfx('fanfare');setTimeout(function(){toast('Карта собрана! Впереди Босс.');renderMapCard();setMode('mapCard');},900);}}
function puzzleHint(){var un=PZ.pieces.filter(function(p){return !p.placed;});if(!un.length)return;highlightTarget(un[0].idx);toast('Подсвечена клетка для выбранного куска');setTimeout(unhighlight,1500);}

function openTreasure(){
  setMode('treasure');
  var t=(state.quest&&state.quest.treasure)||{};
  var key=t.keyHint||t.hint||'КЛЮЧ К КАРТЕ НАХОДИТСЯ В УЧЕБНИКЕ «ОКРУЖАЮЩИЙ МИР»';
  els.treasureTitle.textContent='Карта собрана! Ищи ключ';
  els.treasureKey.textContent=key;
  els.treasureHint.textContent=t.hint||'';
  els.treasureCode.textContent=t.code?('Код сундука: '+t.code):'';
  sfx('victory');
  speak(key+(t.hint?(' '+t.hint):''));
}
var confetti=[],confettiOn=false;
function startConfetti(){confettiOn=true;confetti=[];for(var i=0;i<120;i++)confetti.push({x:Math.random()*VW,y:-Math.random()*VH,vy:80+Math.random()*120,vx:(Math.random()-0.5)*60,r:4+Math.random()*6,col:['#fde047','#4ade80','#38bdf8','#fb7185','#c084fc'][i%5],rot:Math.random()*6.3});}
function stopConfetti(){confettiOn=false;fxx.clearRect(0,0,VW,VH);}
function drawConfetti(dt){if(!confettiOn)return;fxx.clearRect(0,0,VW,VH);for(var i=0;i<confetti.length;i++){var c=confetti[i];c.y+=c.vy*dt;c.x+=c.vx*dt;c.rot+=dt*4;if(c.y>VH+20){c.y=-20;c.x=Math.random()*VW;}fxx.save();fxx.translate(c.x,c.y);fxx.rotate(c.rot);fxx.fillStyle=c.col;fxx.fillRect(-c.r/2,-c.r/2,c.r,c.r*0.6);fxx.restore();}}

function loop(ts){requestAnimationFrame(loop);var dt=Math.min((ts-state.lastTs)/1000||0,0.05);state.lastTs=ts;
  try{updateBattle(dt);}catch(e){state.err='update: '+e.message;console.error(e);}
  try{updateScanner();}catch(e){}try{drawConfetti(dt);}catch(e){}
  try{draw(ts/1000);}catch(e){state.err='draw: '+e.message;console.error(e);}
}
function draw(now){ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,VW,VH);var b=state.battle;
  try{if(!state.cameraReady)drawArena();}catch(e){ctx.fillStyle='#16203a';ctx.fillRect(0,0,VW,VH);state.err='bg: '+e.message;}
  if(!b){drawStatus();return;}
  ctx.save();if(b.shake>0){var k=b.shake/0.3*b.shakeMag;ctx.translate((Math.random()-0.5)*k,(Math.random()-0.5)*k);}
  try{drawDust(b);}catch(e){}try{drawSmoke(b);}catch(e){}
  try{drawMob(b,now);state.mobFrames++;}catch(e){state.err='mob: '+e.message;ctx.fillStyle='#ff5a5a';ctx.font='bold 20px sans-serif';ctx.fillText('MOB ERR',VW/2-40,VH/2);}
  try{if(b.sub==='dying'||b.sub==='loot'||b.sub==='collected')drawDeath(b,now);}catch(e){state.err='death: '+e.message;}
  try{drawArrows(b);}catch(e){}try{drawSnow(b);}catch(e){}try{drawImp(b);}catch(e){}
  ctx.restore();
  try{if(b.flashT>0&&b.flashCol){ctx.fillStyle=b.flashCol;ctx.fillRect(0,0,VW,VH);}}catch(e){}
  drawStatus();
}
function drawStatus(){ctx.save();ctx.font='12px monospace';ctx.fillStyle=state.err?'#ff6b6b':'rgba(255,255,255,0.5)';ctx.fillText((state.err?('ERR '+state.err):('cam:'+(state.cameraReady?'ON':'OFF')+' mob:'+(state.battle?'Y':'N')+' stages:'+N()+' scan:'+(state.scanner?'ON':'OFF')+' f:'+state.mobFrames)),8,VH-8);ctx.restore();}
function drawArena(){var g=ctx.createLinearGradient(0,0,0,VH);g.addColorStop(0,'#2b3548');g.addColorStop(1,'#161d2b');ctx.fillStyle=g;ctx.fillRect(0,0,VW,VH);ctx.fillStyle='rgba(255,255,255,0.03)';for(var x=0;x<VW;x+=26)ctx.fillRect(x,0,1,VH);var lg=ctx.createRadialGradient(VW/2,VH*0.4,20,VW/2,VH*0.4,VW*0.6);lg.addColorStop(0,'rgba(125,211,252,0.16)');lg.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=lg;ctx.fillRect(0,0,VW,VH);ctx.fillStyle='#0c111b';ctx.fillRect(0,VH*0.86,VW,VH*0.14);}
function drawSmoke(b){if(!b.smoke)return;ctx.save();for(var i=0;i<b.smoke.length;i++){var p=b.smoke[i];var a=Math.max(0,1-p.life/p.ttl)*0.5;ctx.globalAlpha=a;var gg=ctx.createRadialGradient(p.x,p.y,1,p.x,p.y,p.r);gg.addColorStop(0,'rgba(203,213,225,0.9)');gg.addColorStop(1,'rgba(148,163,184,0)');ctx.fillStyle=gg;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,7);ctx.fill();}ctx.restore();}
function drawMob(b,now){
  if(b.sub==='loot'||b.sub==='collected')return;
  var m=mobMetrics(); var fade=(m.fade==null?1:m.fade); if(fade<=0.02)return;
  var hpR=clamp01(b.hp/b.maxHp);
  var cv=(b.sub==='combat'&&b.drewBow>0)?b.texRel:b.texDraw;
  var dying=(b.sub==='dying');
  var ox=m.cx+b.kbx+b.dodgeOff,oy=m.cy+b.kby+Math.sin(now*4)*4;
  if(!dying&&b.stagger>0)ox+=Math.sin(b.stagger*60)*6;
  if(b.sub==='emerging'){var pe=clamp01(b.t/b.params.emerge);oy+=(1-easeOutBack(pe))*m.th*0.9;}
  if(b.sub==='hiding'){var ph=clamp01(1-b.hideT/b.params.hideTime);oy+=ph*m.th*0.9;}
  ctx.save();
  var hg=ctx.createRadialGradient(ox,oy,m.th*0.08,ox,oy,m.th*0.78);
  hg.addColorStop(0,'rgba(0,0,0,'+(0.38*fade)+')');
  hg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=hg; ctx.beginPath(); ctx.ellipse(ox,oy,m.tw*0.95,m.th*0.85,0,0,7); ctx.fill();
  ctx.restore();
  if(!dying){ctx.save();ctx.fillStyle='rgba(0,0,0,0.45)';ctx.beginPath();ctx.ellipse(ox,m.baseY-4,m.tw*0.42,m.th*0.05,0,0,7);ctx.fill();ctx.restore();}
  if((b.params.miniBoss||b.isBoss)&&!dying)drawBossAura(ox,oy,m,now);
  if(b.sub==='emerging'||b.sub==='hiding'){
    var emerg=(b.sub==='emerging');var pulse=0.5+0.5*Math.sin(now*6);
    ctx.save();
    var cg=ctx.createRadialGradient(ox,oy,4,ox,oy,m.th*0.62);
    if(emerg){cg.addColorStop(0,'rgba(56,189,248,0.0)');cg.addColorStop(0.6,'rgba(56,189,248,'+(0.30+0.12*pulse)+')');cg.addColorStop(1,'rgba(56,189,248,0)');}
    else{cg.addColorStop(0,'rgba(167,139,250,0.0)');cg.addColorStop(0.6,'rgba(148,163,184,'+(0.30+0.12*pulse)+')');cg.addColorStop(1,'rgba(148,163,184,0)');}
    ctx.fillStyle=cg;ctx.beginPath();ctx.ellipse(ox,oy,m.tw*0.72,m.th*0.62,0,0,7);ctx.fill();
    ctx.globalAlpha=0.5+0.4*pulse;ctx.lineWidth=3;ctx.strokeStyle=emerg?'#38bdf8':'#a78bfa';ctx.beginPath();ctx.ellipse(ox,oy,m.tw*0.72,m.th*0.62,0,0,7);ctx.stroke();
    ctx.restore();
  }
  if(b.vulnWin>0&&b.sub==='combat'){ctx.save();ctx.globalAlpha=0.4+0.3*Math.sin(now*20);ctx.strokeStyle='#fde047';ctx.lineWidth=4;var r=currentBodyRect();ctx.strokeRect(r.x,r.y,r.w,r.h*0.3);ctx.restore();}
  if(dying){
    var da=clamp01(b.deathBlur/0.7)*fade;
    if(da>0.01){
      var copies=4;for(var i=0;i<copies;i++){ctx.save();ctx.globalAlpha=da*0.5*(1-i/copies);if(ctx.filter!==undefined)ctx.filter='blur('+(2+i)+'px)';ctx.imageSmoothingEnabled=false;ctx.drawImage(cv,ox-m.tw/2+(Math.random()-0.5)*12,oy-m.th/2+(Math.random()-0.5)*12,m.tw,m.th);ctx.restore();}
      ctx.save();ctx.imageSmoothingEnabled=false;ctx.globalAlpha=da;ctx.drawImage(cv,ox-m.tw/2,oy-m.th/2,m.tw,m.th);ctx.restore();
    }
    return;
  }
  var ghost=(hpR<0.3&&b.sub==='combat');
  if(ghost){for(var j=0;j<3;j++){ctx.save();ctx.globalAlpha=0.32*(1-j/3)*fade;if(ctx.filter!==undefined)ctx.filter='blur('+(2+j)+'px)';ctx.imageSmoothingEnabled=false;ctx.drawImage(cv,ox-m.tw/2+(Math.random()-0.5)*10,oy-m.th/2+(Math.random()-0.5)*10,m.tw,m.th);ctx.restore();}}
  ctx.save();ctx.imageSmoothingEnabled=false;ctx.globalAlpha=(hpR<0.3?0.92:1)*fade;ctx.drawImage(cv,ox-m.tw/2,oy-m.th/2,m.tw,m.th);
  if(b.flash>0){ctx.globalAlpha=clamp01(b.flash/0.16)*0.55*fade;ctx.fillStyle='#fff';ctx.fillRect(ox-m.tw/2,oy-m.th/2,m.tw,m.th);}ctx.restore();
}
function drawArrows(b){ctx.save();ctx.imageSmoothingEnabled=false;for(var i=0;i<b.arrows.length;i++){var a=b.arrows[i],p=arrowXY(a);ctx.save();ctx.translate(p.px,p.py);ctx.rotate(p.ang);ctx.scale(p.sc,p.sc);ctx.drawImage(arrowCv,-32,-8,64,16);ctx.restore();}ctx.restore();}
function drawSnow(b){ctx.save();ctx.imageSmoothingEnabled=false;for(var i=0;i<b.snow.length;i++){var s=b.snow[i],p=snowPos(s),r=10+s.ch*8;ctx.globalAlpha=0.9;ctx.drawImage(snowCv,p.px-r,p.py-r,r*2,r*2);}ctx.restore();}
function drawImp(b){ctx.save();for(var i=0;i<b.imp.length;i++){var p=b.imp[i];ctx.globalAlpha=Math.max(0,1-p.life/p.ttl);ctx.fillStyle=p.col;ctx.fillRect(p.x-2,p.y-2,4,4);}ctx.restore();}
function drawDust(b){ctx.save();ctx.fillStyle='#d1d5db';for(var i=0;i<b.dust.length;i++){var p=b.dust[i];ctx.globalAlpha=Math.max(0,0.9*(1-p.life/p.ttl));ctx.fillRect(p.x-2,p.y-2,4,4);}ctx.restore();}

function updateScanner(){
  if(!state.scanner||typeof jsQR==='undefined'||!els.video||els.video.readyState<2)return;
  if(!scanCanvas){scanCanvas=document.createElement('canvas');scanCanvas.width=scanW;scanCanvas.height=scanH;scanCtx=scanCanvas.getContext('2d',{willReadFrequently:true});}
  if(++scanFrame%4!==0)return;
  scanCtx.drawImage(els.video,0,0,scanW,scanH);
  var img=scanCtx.getImageData(0,0,scanW,scanH);
  var code=jsQR(img.data,scanW,scanH);
  if(!code)return;
  var now=performance.now();
  if(now-scanCooldown<800)return;
  scanCooldown=now;
  var pose=poseFromLoc(code.location);
  var txt=String(code.data||'');
  if(state.battle){
    var mm=txt.match(/THMARK:(\d+)/);
    if(mm && state.battle.index===parseInt(mm[1],10)-1 && pose){ setBattlePose(pose); }
    return;
  }
  if(/THSTART/.test(txt)){ handleStartMarker(); return; }
  var m=txt.match(/THMARK:(\d+)/);
  if(m){
    var idx=parseInt(m[1],10)-1;
    var s=state.stages[idx];
    if(!s){toast('Неизвестный маркер');return;}
    if(state.progress.collected.indexOf(idx)>=0){toast('Кусок '+(idx+1)+' уже собран');updateRiddle();return;}
    startBattle(s,false,idx,pose);
  } else {
    toast('Нужен QR: THSTART или THMARK:n');
  }
}

function speak(t){if(!TTS||!('speechSynthesis'in window))return;try{var u=new SpeechSynthesisUtterance(t);u.lang='ru-RU';u.rate=0.95;u.pitch=1.05;speechSynthesis.cancel();speechSynthesis.speak(u);}catch(e){}}
function resumeAudio(){
  if(!audioCtx){var AC=window.AudioContext||window.webkitAudioContext;if(AC)audioCtx=new AC();}
  if(audioCtx && !audioMaster){audioMaster=audioCtx.createGain();audioMaster.gain.value=1.75;audioMaster.connect(audioCtx.destination);}
  if(audioCtx&&audioCtx.state==='suspended')audioCtx.resume();
}
function tone(type,f0,f1,dur,vol,t1,delay){if(!audioCtx||!audioMaster)return;vol=Math.min(0.22,Math.max(0.0002,(vol||0.04)*1.75));var n=audioCtx.currentTime+(delay||0),o=audioCtx.createOscillator(),g=audioCtx.createGain();o.connect(g);g.connect(audioMaster);o.type=type;o.frequency.setValueAtTime(f0,n);if(t1)o.frequency.exponentialRampToValueAtTime(t1,n+dur*0.5);o.frequency.exponentialRampToValueAtTime(f1,n+dur);g.gain.setValueAtTime(0.0001,n);g.gain.exponentialRampToValueAtTime(vol,n+0.01);g.gain.exponentialRampToValueAtTime(0.0001,n+dur);o.start(n);o.stop(n+dur+0.02);}
function noise(dur,vol,hp){if(!audioCtx||!audioMaster)return;vol=Math.min(0.22,Math.max(0.0002,(vol||0.03)*1.75));var n=audioCtx.currentTime,len=Math.floor(audioCtx.sampleRate*dur),buf=audioCtx.createBuffer(1,len,audioCtx.sampleRate),d=buf.getChannelData(0);for(var i=0;i<len;i++)d[i]=(Math.random()*2-1)*(1-i/len);var src=audioCtx.createBufferSource();src.buffer=buf;var g=audioCtx.createGain();g.gain.value=vol;var f=audioCtx.createBiquadFilter();f.type='highpass';f.frequency.value=hp||600;src.connect(f);f.connect(g);g.connect(audioMaster);src.start(n);}
function seq(notes,gap,type,vol,delay){notes.forEach(function(fr,i){tone(type||'triangle',fr,fr*0.9,gap*0.9,vol||0.04,null,(delay||0)+i*gap);});}
function sfx(name,i){i=i||1;if(!audioCtx)return;
  if(name==='spawn'){tone('sawtooth',110,360,0.42,0.05);noise(0.2,0.02,300);}
  else if(name==='throw'){tone('triangle',420+320*i,180,0.17,0.025+0.025*i);noise(0.06,0.01,1200);}
  else if(name==='thunk'){tone('square',150+Math.random()*40,70,0.12,0.045);noise(0.05,0.02,400);}
  else if(name==='crack'){tone('sawtooth',760,300,0.10,0.05,1250);tone('square',520,180,0.16,0.04,null,0.06);noise(0.08,0.03,800);}
  else if(name==='miss'){tone('sine',300,120,0.12,0.02);}
  else if(name==='swoosh'){tone('triangle',900+Math.random()*200,200,0.18,0.03);noise(0.12,0.02,900);}
  else if(name==='shimmer'){seq([660,880,1100,1320],0.06,'sine',0.03);}
  else if(name==='poof'){noise(0.25,0.04,200);tone('sine',200,60,0.3,0.03);}
  else if(name==='loose'){tone('triangle',900,300,0.18,0.03);noise(0.05,0.01,1500);}
  else if(name==='whoosh'){tone('sine',600,200,0.2,0.025);noise(0.1,0.02,700);}
  else if(name==='hurt'){tone('square',220,80,0.2,0.05);noise(0.1,0.03,300);}
  else if(name==='explode'){tone('sawtooth',190,38,0.55,0.075);noise(0.4,0.05,150);seq([120,90,60],0.05,'square',0.04);}
  else if(name==='loot'){seq([523,659,784],0.08,'sine',0.04);}
  else if(name==='collect'){tone('triangle',680,1180,0.2,0.04);}
  else if(name==='chime'){seq([784,988,1319],0.09,'sine',0.05);tone('sine',1568,1568,0.3,0.03,null,0.27);}
  else if(name==='pickup'){tone('sine',440,660,0.08,0.03);}
  else if(name==='place'){tone('square',330,220,0.08,0.04);noise(0.04,0.02,500);}
  else if(name==='fanfare'){seq([523,659,784,1046,784,1046],0.12,'triangle',0.05);}
  else if(name==='roar'){tone('sawtooth',70,40,0.9,0.08);tone('square',90,50,0.8,0.05,null,0.05);noise(0.6,0.04,120);}
  else if(name==='victory'){seq([523,659,784,1046],0.14,'sawtooth',0.05);seq([659,784,1046,1318],0.14,'triangle',0.04,0.2);}
}
function haptic(ms){if(navigator.vibrate&&!(state.quest&&state.quest.settings&&state.quest.settings.haptics===false))navigator.vibrate(Math.max(1,Math.round(ms)));}
function toast(m){els.toast.textContent=m;els.toast.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(function(){els.toast.classList.remove('show');},2500);}
function requestWakeLock(){try{if('wakeLock'in navigator&&!wakeLock)navigator.wakeLock.request('screen').then(function(w){wakeLock=w;}).catch(function(){});}catch(e){}}
function clamp(v,a,b){return Math.max(a,Math.min(b,v));}
function easeOutBack(x){var c1=1.70158,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2);}
init();
""")

# ============================== src/admin.js ==============================
write('src/admin.js', r"""
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
""")

# ============================== quest.json / map.svg ==============================
write('quests/default/quest.json', r"""
{
  "title": "Тайна хрущёвки",
  "settings": { "age": "kid", "tts": true, "playerDamage": false, "haptics": true },
  "map": { "scale": 60, "width": 6, "height": 5 },
  "stages": [
    { "zone": "Прихожая", "point": [0.8, 0.8], "riddle": "Где живут куртки и пахнет улицей", "name": "Костяш", "type": "bone", "hp": 100, "damagePerHit": 20, "dodge": 0.28, "hitbox": 1.3, "emerge": 1.4, "hideInterval": 6, "hideTime": 1.4 },
    { "zone": "Кухня", "point": [3.2, 1.0], "riddle": "Там, где холодно и гудит", "name": "Мшистый", "type": "moss", "hp": 110, "damagePerHit": 20, "dodge": 0.3, "hitbox": 1.3, "emerge": 1.4, "hideInterval": 5.5, "hideTime": 1.3 },
    { "zone": "Комната", "point": [3.5, 3.2], "riddle": "Где игрушки спят по ночам", "name": "Ледяной", "type": "azure", "hp": 120, "damagePerHit": 20, "dodge": 0.28, "hitbox": 1.3, "emerge": 1.5, "hideInterval": 6, "hideTime": 1.4 },
    { "zone": "Санузел", "point": [0.8, 2.2], "riddle": "Где полотенца и вода", "name": "Уголёк", "type": "ember", "hp": 130, "damagePerHit": 22, "dodge": 0.26, "hitbox": 1.3, "emerge": 1.6, "hideInterval": 7, "hideTime": 1.2 },
    { "zone": "Коридор", "point": [2.0, 1.8], "riddle": "Высокий тайник над головой", "name": "Сумрак", "type": "violet", "hp": 130, "damagePerHit": 22, "dodge": 0.32, "hitbox": 1.25, "emerge": 1.5, "hideInterval": 5, "hideTime": 1.3 },
    { "zone": "Комната", "point": [5.0, 4.0], "riddle": "Финальный страж спрятался у окна", "name": "Страж Врат", "type": "armored", "hp": 220, "damagePerHit": 30, "dodge": 0.3, "hitbox": 1.25, "emerge": 1.6, "hideInterval": 6, "hideTime": 1.4, "sizeMul": 1.3, "miniBoss": true }
  ],
  "boss": { "name": "Хранитель Клада", "type": "boss", "hp": 360, "damagePerHit": 30, "dodge": 0.4, "hitbox": 1.1, "sizeMul": 1.35, "intro": "Клад мой, никто не пройдёт!" },
  "treasure": {
    "hint": "Красный крест на карте - антресоль в коридоре. Там сундук.",
    "keyHint": "КЛЮЧ К КАРТЕ НАХОДИТСЯ В УЧЕБНИКЕ «ОКРУЖАЮЩИЙ МИР»",
    "code": "4-1-9-3-7-2"
  }
}
""")
write('quests/default/map.svg', r"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 300" width="360" height="300">
  <rect width="360" height="300" fill="#f8fafc" stroke="#0f172a" stroke-width="4"/>
  <rect x="0" y="0" width="90" height="90" fill="#e2e8f0" stroke="#0f172a" stroke-width="3"/><text x="45" y="50" text-anchor="middle" font-size="14" fill="#0f172a">Прихожая</text>
  <rect x="0" y="90" width="90" height="90" fill="#bae6fd" stroke="#0f172a" stroke-width="3"/><text x="45" y="140" text-anchor="middle" font-size="14" fill="#0f172a">Санузел</text>
  <rect x="90" y="0" width="60" height="180" fill="#fde68a" stroke="#0f172a" stroke-width="3"/><text x="120" y="95" text-anchor="middle" font-size="14" fill="#0f172a" transform="rotate(-90 120 95)">Коридор</text>
  <rect x="150" y="0" width="120" height="120" fill="#fecaca" stroke="#0f172a" stroke-width="3"/><text x="210" y="65" text-anchor="middle" font-size="14" fill="#0f172a">Кухня</text>
  <rect x="150" y="120" width="210" height="180" fill="#bbf7d0" stroke="#0f172a" stroke-width="3"/><text x="255" y="215" text-anchor="middle" font-size="14" fill="#0f172a">Комната</text>
  <rect x="90" y="180" width="60" height="120" fill="#ddd6fe" stroke="#0f172a" stroke-width="3"/><text x="120" y="245" text-anchor="middle" font-size="12" fill="#0f172a">Балкон</text>
  <circle cx="300" cy="240" r="7" fill="#dc2626" stroke="#fff" stroke-width="3"/>
</svg>
""")

# ============================== manifest / sw / icon ==============================
write('manifest.webmanifest', r"""
{"name":"Voxel Treasure Hunt","short_name":"Treasure AR","start_url":"./index.html","display":"standalone","background_color":"#0f172a","theme_color":"#111827","icons":[{"src":"./public/icons/icon.svg","sizes":"any","type":"image/svg+xml","purpose":"any"},{"src":"./public/icons/icon.svg","sizes":"192x192","type":"image/svg+xml","purpose":"maskable"}]}
""")
write('sw.js', r"""
var CACHE='voxel-treasure-v9';
var CODE=['./index.html','./admin.html','./styles.css','./admin.css','./src/main.js','./src/admin.js','./manifest.webmanifest','./quests/default/quest.json'];
var STATIC=['./public/icons/icon.svg','./quests/default/map.svg','https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js','https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js'];
self.addEventListener('install',function(e){e.waitUntil((async function(){var c=await caches.open(CACHE);await Promise.allSettled(STATIC.map(function(u){return c.add(u);}));await self.skipWaiting();})());});
self.addEventListener('activate',function(e){e.waitUntil((async function(){var keys=await caches.keys();await Promise.all(keys.filter(function(k){return k!==CACHE;}).map(function(k){return caches.delete(k);}));await self.clients.claim();})());});
self.addEventListener('fetch',function(e){if(e.request.method!=='GET')return;var url=e.request.url;
  e.respondWith((async function(){
    var isCode=CODE.some(function(p){return url.indexOf(p)>=0;})||url.endsWith('/');
    if(isCode){try{var net=await fetch(e.request,{cache:'no-store'});var c=await caches.open(CACHE);c.put(e.request,net.clone());return net;}catch(err){var ca=await caches.match(e.request);if(ca)return ca;throw err;}}
    var ca2=await caches.match(e.request);if(ca2)return ca2;
    try{var r=await fetch(e.request);var c2=await caches.open(CACHE);c2.put(e.request,r.clone());return r;}catch(err2){var f=await caches.match('./index.html');if(f)return f;throw err2;}
  })());
});
""")
write('public/icons/icon.svg', r"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512"><rect width="512" height="512" rx="96" fill="#111827"/><rect x="144" y="128" width="224" height="160" fill="#f3f4f6"/><rect x="184" y="176" width="40" height="40" fill="#111827"/><rect x="288" y="176" width="40" height="40" fill="#111827"/><rect x="208" y="304" width="96" height="32" fill="#f3f4f6"/><rect x="120" y="360" width="272" height="32" rx="12" fill="#38bdf8"/></svg>
""")

# ============================== github / meta ==============================
write('.github/workflows/deploy.yml', r"""
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: true
jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: '.'
      - id: deployment
        uses: actions/deploy-pages@v4
""")
write('package.json', r"""
{ "name": "voxel-treasure-hunt", "private": true, "version": "0.9.4", "scripts": { "dev": "npx --yes serve -l 5173 .", "start": "npx --yes serve -l 5173 ." }, "license": "MIT" }
""")
write('.gitignore', "node_modules\ndist\n.DS_Store\nThumbs.db\n")
write('.nojekyll', "")
write('LICENSE', "MIT License\n\nCopyright (c) 2026 Voxel Treasure Hunt contributors\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the Software), to deal in the Software without restriction.\n\nTHE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND.\n")
write('LICENSE-ASSETS', "Original game assets generated for this project are licensed under CC BY 4.0. See https://creativecommons.org/licenses/by/4.0/\n")
write('README.md', r"""
# Voxel Treasure Hunt

PWA/AR-квест для детей: QR-карточки, скелеты поверх камеры, карта сокровищ, пазл, коллекция, финальная подсказка про книгу/ключ, клад.

## v9.4
- Исправлена печать QR: `QRCode.toCanvas` вызывается через callback + Promise + таймаут; если библиотека недоступна, используется динамическая загрузка и запасной онлайн-генератор QR.
- Добавлено поле админки: «Финальная подсказка: где ключ / книга».
- После победы над боссом на экране клада показывается крупный текст, например: `КЛЮЧ К КАРТЕ НАХОДИТСЯ В УЧЕБНИКЕ «ОКРУЖАЮЩИЙ МИР»`.
- Добавлен прозрачный AR-режим скана: камера не перекрывается панелями; кнопки `Карта` и `Выключить`.
- На карте квартиры добавлена кнопка `AR-вид`.
- Коллекция скелетов и звуки сохранены.

## Запуск
```bash
python -m http.server 8080
```
Игра `http://localhost:8080`, админка `http://localhost:8080/admin.html`.

## Важно для телефона
Камера требует HTTPS. Для теста с телефона публикуй на GitHub Pages или используй HTTPS-туннель. `http://192.168...` может блокировать getUserMedia.

## Карточки
QR-код = ключ. Не нужен спрайт скелета на карточке.
- THSTART — старт;
- THMARK:1..N — этап.
Печатай крупно, матово, с белыми полями вокруг QR.
""")

print('\nProject generated (v9.4). Run: python -m http.server 8080')
print('Game:  http://localhost:8080   Admin: http://localhost:8080/admin.html')
print('Если скаффолд дошёл до этой строки - синтаксис JS чист.')