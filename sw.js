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
