/** Original policy simulations. No native modules, clipboard or actual key registration. */
export function sameEditTarget(before,after) {
  return !!before && !!after && after.verdict==='ready' &&
    before.windowId===after.windowId && before.processId===after.processId &&
    typeof before.elementId==='string' && before.elementId.length>0 &&
    before.elementId===after.elementId && after.editable===true &&
    (before.selection??'')===(after.selection??'');
}
export class SnapshotAuthority {
  #items=new Map();
  save({sessionId,appId,windowId,captureId,grantVersion,expiresAt,elements}) {
    if(!sessionId||!appId||!captureId||!Number.isFinite(expiresAt)||!Array.isArray(elements))throw new TypeError('Incomplete snapshot');
    const key=JSON.stringify([sessionId,appId,windowId]);
    this.#items.set(key,{captureId,grantVersion,expiresAt,elements:structuredClone(elements)});
  }
  resolve({sessionId,appId,windowId,captureId,grantVersion,index,now}) {
    const snapshot=this.#items.get(JSON.stringify([sessionId,appId,windowId]));
    if(!Number.isFinite(now)||!snapshot||snapshot.captureId!==captureId||snapshot.grantVersion!==grantVersion||now>=snapshot.expiresAt)
      throw new Error('Snapshot is absent, stale or outside its authority');
    if(!Number.isInteger(index)||index<0||index>=snapshot.elements.length)throw new RangeError('Unknown element index');
    return structuredClone(snapshot.elements[index]);
  }
}
export class ShortcutLease {
  constructor(registry,callback){this.registry=registry;this.callback=callback;this.active=null;}
  replace(accelerator) {
    const old=this.active;
    if(old!==null)this.registry.unregister(old);
    this.active=null;
    if(accelerator===null)return {ok:true,active:null};
    let registered=false;
    try{registered=this.registry.register(accelerator,this.callback)===true;}catch{}
    if(registered){this.active=accelerator;return {ok:true,active:accelerator};}
    let restored=false;
    if(old!==null){try{restored=this.registry.register(old,this.callback)===true;}catch{}}
    if(restored)this.active=old;
    return {ok:false,active:this.active,rollback:old===null?'unneeded':restored?'restored':'failed'};
  }
  close(){if(this.active!==null)this.registry.unregister(this.active);this.active=null;}
}
export function connectorOwner(configuration) {
  switch(configuration.kind){
    case 'account-remote': return {connectionOrigin:'provider-cloud',configurationOwner:'account'};
    case 'desktop-local': return {connectionOrigin:'desktop-host',configurationOwner:'local-installation'};
    case 'session-remote': return {connectionOrigin:configuration.host,configurationOwner:'session'};
    default: throw new TypeError('Specify the actual route; client or plugin names are insufficient');
  }
}
