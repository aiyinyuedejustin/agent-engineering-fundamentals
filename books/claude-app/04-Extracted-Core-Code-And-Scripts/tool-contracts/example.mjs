import {auditAdapterLoss, exampleSchemas, ToolRouter} from './contract-lab.mjs';

console.log('Potential contract losses:', auditAdapterLoss(exampleSchemas.tap));
const effects = [];
const router = new ToolRouter([{
  name: 'canvas.tap', schema: exampleSchemas.tap, capability: 'canvas.write',
  run: input => { effects.push(input); return {recorded: input.point}; }
}], {readGrants: () => new Set(['canvas.write'])});

console.log('Valid call:', await router.call('canvas.tap', {point: [20, 40], count: 2}));
try { await router.call('canvas.tap', {point: [20.5, 40], count: 4}); }
catch (error) { console.log('Rejected before dispatch:', error.message); }
console.log('Recorded effects:', effects.length); // Only the valid example reaches run.
