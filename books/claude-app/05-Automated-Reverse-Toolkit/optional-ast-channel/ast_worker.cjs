/* Original static adapter. Target bytes are never eval/import/require inputs. */
'use strict';
const crypto = require('node:crypto');
const {TextDecoder} = require('node:util');

const RULES = {
  flag_calls: ['checkGate','check_gate','getFeatureFlag','get_feature_flag','isFeatureEnabled','isEnabled','useFeatureFlag','useGate'],
  tool_calls: ['registerTool','defineTool','register_tool','define_tool'],
  telemetry_calls: ['track','trackEvent','capture','logEvent','emitEvent'],
  schema_keys: ['input_schema','output_schema','inputSchema','outputSchema','parameters'],
  event_keys: ['event_key','event_name','eventName','telemetry_event'],
};
const CONFIG = JSON.parse(process.argv[2]);
const LIMITS = CONFIG.limits;
let data = Buffer.alloc(0), source = '', parserVersion = null;
const metrics = {tokens:0,node_allocations:0,visited_nodes:0,max_ast_depth:0};
class Rejected extends Error {
  constructor(code, position = null) { super(code); this.code = code; this.position = position; }
}
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
function byteAt(pos) {
  if (!Number.isInteger(pos)) return null;
  pos = Math.max(0, Math.min(pos, source.length));
  return Buffer.byteLength(source.slice(0,pos), 'utf8');
}
function policy() {
  return {
    adapter:'original-acorn-ast-candidate/v1', source_type:CONFIG.source_type,
    ecma_version:2025, rules:RULES, limits:LIMITS,
    dependency:{name:'acorn',version:parserVersion,source:CONFIG.dependency.kind,
      sha256:CONFIG.dependency.sha256 || null,testing_only:CONFIG.dependency.kind === 'node-internal-test-only'},
    runtime:{name:'node',version:process.version},
    token_count_basis:'Acorn parser tokens excluding EOF; not comparable to legacy lexical token counts',
  };
}
function result(status, records, diagnostic = null) {
  return {
    schema:'original-ast-candidate-snapshot/v1',
    analysis_kind:'ast_syntax_candidate_inventory',semantic_completeness_proven:false,
    input:{name:CONFIG.source_name,identity_available:true,bytes:data.length,sha256:digest(data)},
    status,policy:policy(),metrics,
    coverage:{complete_within_ast_declared_scope:status === 'scanned',
      legacy_coverage_modified:false,issues:diagnostic ? [diagnostic] : []},
    records,
    limitations:[
      'AST syntax candidates only; no binding, reachability, runtime registry or behavior is proven.',
      'Legacy snapshots, statuses and counts are not modified or merged with this channel.',
      'No target JavaScript is executed/imported; trusted parser dependency code itself is loaded.',
      'No alias/data-flow recovery, dynamic names, JSX/TypeScript plugins or fallback parsing.',
      'Outputs can contain private literal names. Keep snapshots private.',
    ],
  };
}
function rejectResult(code, pos = null) {
  const diagnostic = {code,phase:'ast-candidate-channel',input_validity:'not-determined'};
  const byte = byteAt(pos);
  if (byte !== null) diagnostic.byte_offset = byte;
  return result('scan-incomplete',[],diagnostic);
}
function emit(value) {
  let encoded = JSON.stringify(value);
  if (Buffer.byteLength(encoded,'utf8') + 1 > LIMITS.max_output_bytes) {
    encoded = JSON.stringify(rejectResult('ast-output-bound-exceeded'));
  }
  process.stdout.write(encoded + '\n');
}
function staticString(node, maxLength) {
  let value;
  if (node.type === 'Literal' && typeof node.value === 'string') value = node.value;
  else if (node.type === 'TemplateLiteral' && node.expressions.length === 0) value = node.quasis[0].value.raw;
  else return null;
  if (value.length > maxLength * 2 || [...value].length > maxLength) return null;
  const raw = source.slice(node.start,node.end);
  if (raw.includes('\\') || raw.slice(1,-1) !== value) return null;
  return value;
}
function plainPropertyName(node) {
  if (node.type === 'Identifier' && source.slice(node.start,node.end) === node.name) return node.name;
  return staticString(node,128);
}
function callName(callee) {
  if (callee.type === 'Identifier' && source.slice(callee.start,callee.end) === callee.name) return callee.name;
  if (callee.type === 'MemberExpression' && !callee.computed && callee.property.type === 'Identifier' &&
      source.slice(callee.property.start,callee.property.end) === callee.property.name) return callee.property.name;
  return null;
}
function secondLiteral(node) {
  const text = staticString(node,512);
  if (text !== null) return {present:true,value:text};
  if (node.type !== 'Literal' || node.regex || node.bigint) return {present:false};
  if (node.value === null || typeof node.value === 'boolean') return {present:true,value:node.value};
  if (typeof node.value === 'number') {
    if (!Number.isFinite(node.value)) throw new Rejected('ast-nonfinite-candidate-literal',node.start);
    const raw = source.slice(node.start,node.end);
    if (/^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?$/.test(raw)) return {present:true,value:node.value};
  }
  return {present:false};
}
function addRecord(records, state, node, category, key, value, kind) {
  const record = {category,key,scope:[],value,kind,confidence:'ast-syntactic-candidate',
    _start:node.start,_end:node.end};
  state.bytes += Buffer.byteLength(JSON.stringify(record),'utf8') + 128;
  if (state.bytes > LIMITS.max_output_bytes - 4096) throw new Rejected('ast-output-bound-exceeded',node.start);
  if (records.length >= LIMITS.max_records) throw new Rejected('ast-record-bound-exceeded',node.start);
  records.push(record);
}
function byteAnchors(records) {
  const inputDigest = digest(data);
  const points = [...new Set(records.flatMap(r=>[r._start,r._end]))].sort((a,b)=>a-b);
  const mapped = new Map();
  let i=0, bytes=0, line=1, previousCR=false;
  for (const point of points) {
    while (i < point) {
      const cp=source.codePointAt(i), width=cp>0xffff?2:1;
      if (i+width>point) throw new Rejected('ast-invalid-position');
      bytes += cp<=0x7f?1:cp<=0x7ff?2:cp<=0xffff?3:4;
      // ECMAScript line terminators; CRLF counts as one, even across points.
      if (cp===13 || cp===0x2028 || cp===0x2029 || (cp===10 && !previousCR)) line++;
      previousCR=cp===13;
      i += width;
    }
    mapped.set(point,{byte:bytes,line});
  }
  for (const record of records) {
    const start=mapped.get(record._start),end=mapped.get(record._end);
    record.source={sha256:inputDigest,byte_start:start.byte,byte_end:end.byte,line:start.line};
    delete record._start;delete record._end;
  }
}
function analyze(acorn) {
  class BoundedParser extends acorn.Parser {
    startNode() {
      if (++metrics.node_allocations > LIMITS.max_nodes) throw new Rejected('ast-node-bound-exceeded',this.start);
      return super.startNode();
    }
    startNodeAt(pos,loc) {
      if (++metrics.node_allocations > LIMITS.max_nodes) throw new Rejected('ast-node-bound-exceeded',pos);
      return super.startNodeAt(pos,loc);
    }
    copyNode(node) {
      // Acorn 8.17.0 uses a direct Node allocation for shorthand properties.
      if (++metrics.node_allocations > LIMITS.max_nodes) throw new Rejected('ast-node-bound-exceeded',node.start);
      return super.copyNode(node);
    }
  }
  const ast=BoundedParser.parse(source,{ecmaVersion:2025,sourceType:CONFIG.source_type,
    onToken:token=>{
      if(token.type.label!=='eof' && ++metrics.tokens>LIMITS.max_tokens)
        throw new Rejected('ast-token-bound-exceeded',token.start);
    }});
  const records=[],state={bytes:0};
  const calls = new Map();
  for(const [rule,category] of [['flag_calls','flags'],['tool_calls','tool_contracts'],['telemetry_calls','telemetry']])
    for(const name of RULES[rule]) calls.set(name,category);
  const stack=[{node:ast,depth:0,parent:null}];
  while(stack.length) {
    const {node,depth,parent}=stack.pop();
    metrics.visited_nodes++;
    if(metrics.visited_nodes>LIMITS.max_nodes) throw new Rejected('ast-node-bound-exceeded',node.start);
    metrics.max_ast_depth=Math.max(metrics.max_ast_depth,depth);
    if(depth>LIMITS.max_depth) throw new Rejected('ast-depth-bound-exceeded',node.start);
    if(node.type==='CallExpression') {
      const name=callName(node.callee);
      if(calls.has(name) && node.arguments.length) {
        const argument=node.arguments[0],key=staticString(argument,256);
        if(key!==null) {
          const value={call_spelling:name,call_form:node.callee.type==='Identifier'?'identifier':'member',optional:!!node.optional};
          if(node.arguments.length>1) {const second=secondLiteral(node.arguments[1]);if(second.present)value.second_literal=second.value;}
          addRecord(records,state,argument,calls.get(name),key,value,'ast-call-first-literal');
        }
      }
    }
    if(node.type==='Property' && parent && parent.type==='ObjectExpression' && node.kind==='init' && !node.method && !node.computed && !node.shorthand) {
      const name=plainPropertyName(node.key);
      if(RULES.schema_keys.includes(name))
        addRecord(records,state,node.key,'tool_contracts','schema-marker:'+name,{schema_key:name},'ast-unassociated-schema-marker');
      if(RULES.event_keys.includes(name)) {
        const key=staticString(node.value,256);
        if(key!==null)addRecord(records,state,node.value,'telemetry',key,{field:name},'ast-unassociated-event-field');
      }
    }
    // Only actual AST child nodes. String/regex values and template raw text
    // are never re-tokenized; template interpolation nodes remain traversable.
    for(const value of Object.values(node)) {
      if(Array.isArray(value)) {
        for(let j=value.length-1;j>=0;j--) if(value[j] && typeof value[j].type==='string') stack.push({node:value[j],depth:depth+1,parent:node});
      } else if(value && typeof value==='object' && typeof value.type==='string') stack.push({node:value,depth:depth+1,parent:node});
    }
  }
  byteAnchors(records);
  records.sort((a,b)=>{const left=JSON.stringify(a),right=JSON.stringify(b);return left<right?-1:left>right?1:0;});
  return result('scanned',records);
}

async function main() {
  try {
    const chunks=[];let size=0;
    for await(const chunk of process.stdin) {
      size+=chunk.length;
      if(size>LIMITS.max_input_bytes)throw new Rejected('ast-input-byte-bound-exceeded');
      chunks.push(chunk);
    }
    data=Buffer.concat(chunks);
    try {source=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(data);}
    catch {throw new Rejected('ast-input-not-utf8');}
    // This is a trusted TOOL dependency selected by the caller, never target
    // input or a target-tree inferred module. Internal mode is tests only.
    const acorn=CONFIG.dependency.kind==='node-internal-test-only'
      ? require('internal/deps/acorn/acorn/dist/acorn') : require(CONFIG.dependency.module_path);
    parserVersion=acorn.version;
    if(parserVersion!=='8.17.0' || typeof acorn.Parser!=='function') throw new Rejected('ast-parser-version-unsupported');
    emit(analyze(acorn));
  } catch(error) {
    if(error instanceof Rejected) emit(rejectResult(error.code,error.position));
    else if(error instanceof SyntaxError) emit(rejectResult('ast-syntax-rejected',error.pos));
    else if(error instanceof RangeError) emit(rejectResult('ast-parser-recursion-or-memory-bound'));
    else emit(rejectResult('ast-parser-or-dependency-failed'));
  }
}
main().catch(()=>{process.exitCode=2;});
