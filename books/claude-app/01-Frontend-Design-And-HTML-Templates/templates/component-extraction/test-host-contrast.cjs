'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const source=path.resolve(process.env.ATELIER_COMPONENT_SOURCE||__dirname);
const css=fs.readFileSync(path.join(source,'demo-host.css'),'utf8');
function rules(selector){const escaped=selector.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');return [...css.matchAll(new RegExp(escaped+'\\s*\\{([^}]+)\\}','g'))].map(m=>Object.fromEntries(m[1].split(';').filter(x=>x.includes(':')).map(x=>{const i=x.indexOf(':');return [x.slice(0,i).trim(),x.slice(i+1).trim()];})));}
function rule(selector){const list=rules(selector);assert.ok(list.length,selector+' missing');return Object.assign({},...list);}
function luminance(hex){assert.match(hex,/^#[0-9a-f]{3}(?:[0-9a-f]{3})?$/i);const h=hex.slice(1),expanded=h.length===3?[...h].map(c=>c+c).join(''):h;const rgb=[0,2,4].map(i=>parseInt(expanded.slice(i,i+2),16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722;}
function contrast(a,b){const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
const host=rule('.demo-host');
// 当前宿主全部显式前景色：背景未声明的文字继承宿主底色。
const textSelectors=['.demo-host','.demo-eyebrow','.demo-lede','.demo-local','.demo-step','.demo-number','.demo-panel-mark','.demo-namespace','.demo-actions-note','.demo-button','.demo-button-primary','.demo-footnote'];
for(const selector of textSelectors)test(selector+' text has at least 4.5:1 against its actual background',()=>{const r=rule(selector),bg=r.background||host.background;const ratio=contrast(r.color,bg);assert.ok(ratio>=4.5,selector+' '+r.color+' / '+bg+' = '+ratio.toFixed(3));});
for(const [base,hover] of [['.demo-button','.demo-button:hover'],['.demo-button-primary','.demo-button-primary:hover']])test(hover+' text has at least 4.5:1',()=>{const r={...rule(base),...rule(hover)};const ratio=contrast(r.color,r.background);assert.ok(ratio>=4.5,hover+' = '+ratio.toFixed(3));});
test('all explicit host text color declarations have an audited role',()=>{
 const selectors=[...css.matchAll(/(\.demo-[a-z-]+(?::hover)?)\s*\{([^}]+)\}/g)].filter(m=>/(?:^|;)\s*color\s*:/.test(m[2])).map(m=>m[1]);assert.deepEqual([...new Set(selectors)].sort(),textSelectors.slice().sort());
 // 标题与说明标签无额外前景色，实际继承 demo-host 已测组合。
 for(const selector of ['.demo-title','.demo-panel-title','.demo-actions-title'])assert.equal(rule(selector).color,undefined);
});
for(const selector of ['.demo-local','.demo-namespace','.demo-footnote'])test(selector+' stays at least 12px in every declared breakpoint',()=>{for(const r of rules(selector)){const size=r['font-size']||r.font?.match(/^([\d.]+px)\//)?.[1];if(size){assert.match(size,/px$/);assert.ok(parseFloat(size)>=12,selector+' '+size);}}});
