import test from 'node:test';
import assert from 'node:assert/strict';
import {ConversationBranches,ROOT} from '../branch-manager.mjs';
const messages=()=>[
 {uuid:'h0',sender:'human',parent_message_uuid:ROOT,text:'start'},
 {uuid:'a0',sender:'assistant',parent_message_uuid:'h0',text:'answer'},
 {uuid:'waiting',sender:'human',parent_message_uuid:'a0',text:'not answered'},
];
const state=t=>structuredClone({messages:[...t.messageByUuid],parents:[...t.parentByChildUuid],children:[...t.childrenByParentUuid],selection:[...t.selectedChildByUuid],leaf:t.currentLeaf,dangling:t.danglingHumanMessages});
const human=id=>({uuid:id,sender:'human',parent_message_uuid:'a0',content:[]});
function rejectsAtomically(action){const t=new ConversationBranches(messages());const before=state(t);assert.throws(()=>action(t),/Duplicate or reserved UUID/);assert.deepEqual(state(t),before);}
test('隐藏待答消息仍占UUID，append不能复用',()=>rejectsAtomically(t=>t.append([human('waiting')])));
test('批量append后项撞隐藏UUID时整批拒绝',()=>rejectsAtomically(t=>t.append([human('fresh'),human('waiting')])));
test('editHuman的新human不能占用隐藏UUID',()=>rejectsAtomically(t=>t.editHuman('h0','edit',{humanUuid:'waiting',assistantUuid:'new-a'})));
test('editHuman的新assistant不能占用隐藏UUID',()=>rejectsAtomically(t=>t.editHuman('h0','edit',{humanUuid:'new-h',assistantUuid:'waiting'})));
test('retryAssistant不能占用隐藏UUID',()=>rejectsAtomically(t=>t.retryAssistant('a0','waiting')));
test('不同身份可追加，原隐藏记录继续保留',()=>{
 const t=new ConversationBranches(messages());t.append([human('fresh')]);assert.equal(t.currentLeaf,'fresh');assert.equal(t.danglingHumanMessages[0].uuid,'waiting');
 assert.equal(new Set([...t.messageByUuid.keys(),...t.danglingHumanMessages.map(m=>m.uuid)]).size,4);
});
test('拒绝隐藏父节点不等于静默恢复隐藏消息',()=>{
 const t=new ConversationBranches(messages()),before=state(t);
 assert.throws(()=>t.append([{uuid:'answer-hidden',sender:'assistant',parent_message_uuid:'waiting'}]),/Parent UUID is missing/);
 assert.deepEqual(state(t),before);
});
test('显式includeDanglingHumans仍可保留完整树',()=>{
 const t=new ConversationBranches(messages(),{includeDanglingHumans:true});assert.equal(t.messageByUuid.has('waiting'),true);assert.equal(t.danglingHumanMessages.length,0);
 assert.throws(()=>t.append([human('waiting')]),/Duplicate or reserved UUID/);
});
