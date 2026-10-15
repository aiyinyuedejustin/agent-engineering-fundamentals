import {VirtualFS, buildPlan, createApprovalBoundary, decideUrl, prepareSensitiveSave} from './guardrails.mjs';
const fs = new VirtualFS();
const broker = createApprovalBoundary({now: () => 0});
const grants = [fs.grant('/input'), fs.grant('/output', 'write')];
const plan = buildPlan(fs, 'doccopy -- "/input/annual report.md" "/output/annual report.md"', grants);
const approval = broker.trustedUiConfirm(plan);
console.log('1. Exact virtual plan approved:', broker.consume(approval, plan).kind);
console.log('2. Current resources:', plan.resources.every(x => fs.validateTicket(x)));
try { broker.consume(approval, plan); } catch (error) { console.log('3. Replay denied:', error.message); }
fs.link('/input/annual report.md', '/outside/report.md');
try { fs.validateTicket(plan.resources[0]); } catch (error) { console.log('4. Changed resource denied:', error.message); }
console.log('5. Lookalike external origin:', decideUrl('https://docs.example.test.other.test/a', {trustedOrigins: ['https://docs.example.test']}).decision);
console.log('6. Unavailable storage:', prepareSensitiveSave('synthetic-value', {available: false}).status);
console.log('No commands, network requests or real-file operations were performed.');
