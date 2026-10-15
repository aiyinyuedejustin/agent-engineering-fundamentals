import test from 'node:test';
import assert from 'node:assert/strict';
import {validate, auditAdapterLoss, ToolRouter, exampleSchemas as s} from '../contract-lab.mjs';
const valid = (schema, input) => assert.deepEqual(validate(schema, input), []);
const invalid = (schema, input) => assert.ok(validate(schema, input).length > 0);

test('required is separate from a field description', () => invalid(s.tap, {}));
test('coordinate length is checked rather than inferred from prose', () => invalid(s.tap, {point: [1]}));
test('extra coordinate cannot silently survive', () => invalid(s.tap, {point: [1, 2, 3]}));
test('integer is stronger than number', () => invalid(s.tap, {point: [1.25, 2]}));
test('numeric enum is enforced', () => invalid(s.tap, {point: [1, 2], count: 4}));
test('valid point and repeated tap shape', () => valid(s.tap, {point: [1, 2], count: 2}));
test('unknown field rejected by original model policy', () => invalid(s.tap, {point: [1, 2], typo: true}));
test('NaN and infinity fail numeric input', () => {
  invalid({type: 'number'}, Infinity); invalid({type: 'number'}, NaN);
});
test('type-array union permits each declared branch', () => {
  for (const selection of ['File', ['File', 'Export'], null]) valid(s.menu, {selection});
});
test('type-array union rejects other branches', () => invalid(s.menu, {selection: false}));
test('union array items retain their own validation', () => invalid(s.menu, {selection: ['File', 8]}));
test('string does not coerce a number in this teaching model', () => invalid(s.clipboard, {text: 123}));
test('boolean does not coerce textual true', () => invalid({type: 'boolean'}, 'true'));
test('a default annotation does not silently satisfy required here', () => invalid({type:'object', required:['x'], properties:{x:{type:'string',default:'a'}}}, {}));
test('projection audit identifies integer, enum, and tuple length risks', () => {
  const issues = auditAdapterLoss(s.tap);
  for (const keyword of ['type', 'enum', 'minItems', 'maxItems', 'additionalProperties']) assert.ok(issues.some(x=>x.keyword===keyword));
});
test('projection audit preserves string enum and numeric inclusive limits', () => {
  assert.deepEqual(auditAdapterLoss({type:'string',enum:['up','down']}), []);
  assert.deepEqual(auditAdapterLoss({type:'number',minimum:0,maximum:10}), []);
});
test('projection audit flags type-array union without guessing its semantics', () => assert.ok(auditAdapterLoss(s.menu).some(x=>x.keyword==='type')));
test('shape validation happens before grant lookup and execution', async () => {
  let checks=0,effects=0;
  const router=new ToolRouter([{name:'canvas.tap',schema:s.tap,capability:'canvas.write',run:()=>effects++}],{readGrants:()=>{checks++;return new Set(['canvas.write']);}});
  await assert.rejects(router.call('canvas.tap',{point:[1]}),/array too short/);
  assert.equal(checks,0);assert.equal(effects,0);
});
test('valid schema never grants permission by itself', async () => {
  const router=new ToolRouter([{name:'canvas.tap',schema:s.tap,capability:'canvas.write',run:()=>assert.fail('effect forbidden')}],{readGrants:()=>new Set()});
  await assert.rejects(router.call('canvas.tap',{point:[1,2]}),/capability denied/);
});
test('semantic refinement is a separate contract layer', async () => {
  const router=new ToolRouter([{name:'menu.open',schema:s.menu,capability:'menu.read',refine:x=>x.selection===null?'menu not chosen':undefined,run:()=>1}],{readGrants:()=>new Set(['menu.read'])});
  await assert.rejects(router.call('menu.open',{selection:null}),/menu not chosen/);
});
test('unknown names cannot fall through to a native executor', async () => {
  const router=new ToolRouter([],{readGrants:()=>new Set()});
  await assert.rejects(router.call('invented.command',{}),/unknown tool/);
});
test('batch preflights every shape before effects in this original model', async () => {
  let effects=0;const router=new ToolRouter([{name:'canvas.tap',schema:s.tap,capability:'canvas.write',run:()=>effects++}],{readGrants:()=>new Set(['canvas.write'])});
  await assert.rejects(router.batch([{name:'canvas.tap',input:{point:[1,2]}},{name:'canvas.tap',input:{point:[2]}}]),/array too short/);
  assert.equal(effects,0);
});
test('batch refreshes permission and does not claim rollback', async () => {
  let grants=new Set(['canvas.write']),effects=0;
  const router=new ToolRouter([{name:'canvas.tap',schema:s.tap,capability:'canvas.write',run:()=>{effects++;grants.clear();}}],{readGrants:()=>grants});
  await assert.rejects(router.batch([{name:'canvas.tap',input:{point:[1,2]}},{name:'canvas.tap',input:{point:[2,3]}}]),/capability denied/);
  assert.equal(effects,1);
});
test('input is cloned so caller mutations cannot change prepared command', () => {
  const router=new ToolRouter([{name:'canvas.tap',schema:s.tap,capability:'canvas.write',run:x=>x}],{readGrants:()=>new Set()});
  const input={point:[1,2]};const prepared=router.prepare('canvas.tap',input);input.point[0]=99;assert.equal(prepared.input.point[0],1);
});
