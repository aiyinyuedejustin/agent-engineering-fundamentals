import test from 'node:test';
import assert from 'node:assert/strict';
import { ConversationBranches, ROOT } from '../branch-manager.mjs';
test('late hidden identity collision preserves exact public references and payloads', () => {
  const tree = new ConversationBranches([
    {uuid:'h',sender:'human',parent_message_uuid:ROOT},
    {uuid:'a',sender:'assistant',parent_message_uuid:'h'},
    {uuid:'waiting',sender:'human',parent_message_uuid:'a',content:[{type:'text',text:'original'}]},
  ]);
  const fields=['messageByUuid','parentByChildUuid','childrenByParentUuid','selectedChildByUuid','danglingHumanMessages'];
  const refs=fields.map(k=>tree[k]);
  const before=structuredClone(tree);
  assert.throws(()=>tree.append([
    {uuid:'fresh',sender:'human',parent_message_uuid:'a'},
    {uuid:'waiting',sender:'assistant',parent_message_uuid:'fresh'},
  ]), /Duplicate/);
  fields.forEach((k,i)=>assert.strictEqual(tree[k],refs[i]));
  assert.deepEqual(structuredClone(tree),before);
  new ConversationBranches([...tree.messageByUuid.values(),...tree.danglingHumanMessages],{includeDanglingHumans:true});
});
