import {spawn} from 'node:child_process';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
import {randomUUID} from 'node:crypto';
import {strictJSON, sha256, fail, Failure, object, deepEqual, VERSION} from './base.mjs';

export const PROTOCOL='2025-11-25';
const LIMIT=4*1024*1024;
const META='engineering-process-provider';

export class MCPClient {
  constructor(transport,{directory=process.cwd(),timeout=15000}={}) {
    this.transport=transport;this.directory=directory;this.timeout=timeout;this.pending=new Map();this.closed=false;this.session=null;
  }
  async start() {
    if(this.transport.kind==='http')return;
    if(this.transport.kind!=='stdio')fail('EPX_TRANSPORT_UNSUPPORTED','unsupported','BIND-002','Unsupported MCP transport.');
    this.child=spawn(this.transport.command,this.transport.arguments??[],{cwd:this.directory,shell:false,stdio:['pipe','pipe','pipe'],env:process.env});
    this.child.stderr.resume(); // Provider stderr may contain secrets; do not put it in public reports.
    let buffer='';
    this.child.stdout.setEncoding('utf8');
    this.child.stdout.on('data',chunk=>{
      buffer+=chunk;
      if(Buffer.byteLength(buffer)>LIMIT){this.abort(new Error('MCP message exceeds bounded size.'));return;}
      for(;;){const end=buffer.indexOf('\n');if(end<0)break;const line=buffer.slice(0,end);buffer=buffer.slice(end+1);if(!line.trim())continue;
        let message;try{message=strictJSON(line);}catch(error){this.abort(error);return;}
        if(!object(message)||message.jsonrpc!=='2.0'){this.abort(new Error('Invalid JSON-RPC response envelope.'));return;}
        if(!Object.hasOwn(message,'id'))continue;
        const pending=this.pending.get(message.id);if(!pending)continue;
        this.pending.delete(message.id);clearTimeout(pending.timer);pending.resolve(message);
      }
    });
    this.child.on('error',error=>this.abort(error));
    this.child.on('exit',()=>{this.closed=true;this.abort(new Error('MCP transport closed before a response.'));});
  }
  abort(error) {
    for(const {reject,timer} of this.pending.values()){clearTimeout(timer);reject(error);}this.pending.clear();
  }
  async exchange(message) {
    if(this.transport.kind==='http') {
      const headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream','MCP-Protocol-Version':PROTOCOL};
      if(this.session)headers['Mcp-Session-Id']=this.session;
      if(this.transport.tokenEnv){const value=process.env[this.transport.tokenEnv];if(!value)throw new Error('Configured credential environment variable is unavailable.');headers.Authorization=`Bearer ${value}`;}
      const response=await fetch(this.transport.url,{method:'POST',headers,body:JSON.stringify(message),signal:AbortSignal.timeout(this.timeout),redirect:'error'});
      if(response.headers.has('mcp-session-id'))this.session=response.headers.get('mcp-session-id');
      if(!response.ok)throw new Failure('EPX_HTTP_FAILED','unavailable','BIND-002','MCP HTTP transport rejected the request.',{cause:{status:response.status}});
      if(!Object.hasOwn(message,'id')){await response.arrayBuffer();return null;}
      if(!response.headers.get('content-type')?.includes('application/json'))fail('EPX_HTTP_STREAM_UNSUPPORTED','unsupported','BIND-002','This adapter supports MCP HTTP JSON responses; negotiated SSE is unsupported.');
      const text=await response.text();if(Buffer.byteLength(text)>LIMIT)throw new Error('MCP response exceeds bounded size.');
      return strictJSON(text);
    }
    if(this.closed||!this.child?.stdin.writable)throw new Error('MCP transport is unavailable.');
    if(!Object.hasOwn(message,'id')){this.child.stdin.write(JSON.stringify(message)+'\n');return null;}
    return await new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>{this.pending.delete(message.id);reject(new Error('MCP response timed out.'));},this.timeout);
      this.pending.set(message.id,{resolve,reject,timer});
      this.child.stdin.write(JSON.stringify(message)+'\n',error=>{if(error){const item=this.pending.get(message.id);if(item){clearTimeout(item.timer);this.pending.delete(message.id);item.reject(error);}}});
    });
  }
  async request(method,params={}) {
    const request={jsonrpc:'2.0',id:randomUUID(),method,params};
    this.lastRequest=request;
    const response=await this.exchange(request);
    this.lastResponse=response;
    if(!object(response)||response.jsonrpc!=='2.0'||response.id!==request.id||Object.hasOwn(response,'result')===Object.hasOwn(response,'error'))
      fail('EPX_RPC_INVALID','execution-failed','OUT-003','MCP response is not the matching JSON-RPC result/error envelope.');
    if(response.error)fail('EPX_RPC_ERROR','execution-failed','OUT-003','MCP returned a JSON-RPC error.',{cause:response.error});
    return response.result;
  }
  async initialize() {
    await this.start();
    const result=await this.request('initialize',{protocolVersion:PROTOCOL,capabilities:{},clientInfo:{name:'epx-node',version:VERSION}});
    if(result?.protocolVersion!==PROTOCOL)fail('EPX_PROTOCOL_MISMATCH','unavailable','BIND-003','MCP protocol negotiation does not match the declared revision.',{expected:PROTOCOL,observed:result?.protocolVersion});
    if(!object(result.capabilities?.tools))fail('EPX_TOOLS_UNAVAILABLE','unavailable','BIND-003','Provider does not advertise MCP tools capability.');
    await this.exchange({jsonrpc:'2.0',method:'notifications/initialized'});
    return result;
  }
  async close() {
    this.abort(new Error('MCP session closed.'));
    this.child?.stdin.end();this.child?.kill();this.closed=true;
    // HTTP DELETE is session cleanup only; it never retries engineering operations.
    if(this.transport.kind==='http'&&this.session) {
      const headers={'Mcp-Session-Id':this.session,'MCP-Protocol-Version':PROTOCOL};
      if(this.transport.tokenEnv&&process.env[this.transport.tokenEnv])headers.Authorization=`Bearer ${process.env[this.transport.tokenEnv]}`;
      try{await fetch(this.transport.url,{method:'DELETE',headers,signal:AbortSignal.timeout(1000),redirect:'error'});}catch{/* Unknown cleanup cannot authorize replay. */}
    }
  }
}

function providerMetadata(response,intended,dependency) {
  const observed=response?._meta?.[META];
  const expected={implementation:intended.implementation.id,revision:intended.implementation.revision,application:intended.application.id,applicationVersion:intended.application.version};
  if(!object(observed))fail('EPX_IDENTITY_UNVERIFIABLE','unavailable','BIND-003','Provider identity metadata is unavailable.',{dependency});
  for(const [key,value] of Object.entries(expected))if(observed[key]!==value)fail('EPX_PROVIDER_MISMATCH','unavailable','BIND-005','Observed provider identity/version does not match the intended dependency.',{dependency,expected,observed});
  if(!intended.executionPlatforms.includes(observed.executionPlatform))fail('EPX_PLATFORM_UNAVAILABLE','unavailable','BIND-005','Execution target platform is incompatible.',{dependency,expected:intended.executionPlatforms,observed:observed.executionPlatform});
  return observed;
}

export async function openBinding(pkg,configuration,reference,configDirectory) {
  const intended=pkg.requirements.bindings[reference];
  const local=configuration.bindings?.[reference];
  if(!intended)fail('EPX_BINDING_INVALID','invalid','BIND-001','Unknown logical binding.',{dependency:reference});
  if(!local)fail('EPX_PROVIDER_UNAVAILABLE','unavailable','BIND-005','Configure access to the intended provider.',{dependency:reference});
  if(!deepEqual(local.implementation,{id:intended.implementation.id,revision:intended.implementation.revision})||!deepEqual(local.application,intended.application))
    fail('EPX_BINDING_MISMATCH','unavailable','BIND-002','Local binding names another implementation or application.',{dependency:reference});
  if(intended.protocolVersion!==PROTOCOL)fail('EPX_PROTOCOL_UNSUPPORTED','unavailable','BIND-003','The declared MCP dependency revision is unavailable to this adapter.',{dependency:reference,expected:PROTOCOL,observed:intended.protocolVersion});
  const transport=structuredClone(local.transport);
  if(transport.kind==='stdio') {
    if(local.trust?.kind!=='launcher-sha256')fail('EPX_TRUST_UNVERIFIABLE','unavailable','BIND-002','Stdio fixture requires explicit launcher digest evidence.',{dependency:reference});
    const launcher=path.resolve(configDirectory,local.trust.path);
    let digest;try{digest=sha256(await readFile(launcher));}catch{fail('EPX_PROVIDER_UNAVAILABLE','unavailable','BIND-002','The intended launcher file is unavailable.',{dependency:reference});}
    if(digest!==local.trust.sha256||digest!==intended.implementation.artifactSha256)fail('EPX_LAUNCHER_MISMATCH','unavailable','BIND-002','Launcher bytes do not match intended and configured identity evidence.',{dependency:reference,expected:intended.implementation.artifactSha256,observed:digest});
    const invocation=[transport.command,...(transport.arguments??[])];
    if(!invocation.some(argument=>path.resolve(configDirectory,argument)===launcher))fail('EPX_TRUST_UNVERIFIABLE','unavailable','BIND-002','Verified launcher is absent from the explicit invocation.',{dependency:reference});
  } else if(transport.kind==='http') {
    if(local.trust?.kind!=='configured-service'||local.trust.subject!==intended.implementation.id||!local.trust.description)
      fail('EPX_TRUST_UNVERIFIABLE','unavailable','BIND-002','HTTP requires a configured intended service trust boundary.',{dependency:reference});
    let url;try{url=new URL(transport.url);}catch{fail('EPX_ENDPOINT_INVALID','unavailable','BIND-002','Configured HTTP endpoint is invalid.',{dependency:reference});}
    if(!['http:','https:'].includes(url.protocol)||url.username||url.password)fail('EPX_ENDPOINT_INVALID','unavailable','BIND-002','Endpoint must be HTTP(S) with credentials supplied separately.',{dependency:reference});
  }
  const client=new MCPClient(transport,{directory:configDirectory});
  try {
    const initialized=await client.initialize();
    const observed=providerMetadata(initialized,intended,reference);
    const tools=[];let cursor;const cursors=new Set();
    do{
      const listed=await client.request('tools/list',cursor?{cursor}:{});providerMetadata(listed,intended,reference);
      if(!Array.isArray(listed.tools))fail('EPX_TOOLS_INVALID','unavailable','BIND-004','Provider tools/list is malformed.',{dependency:reference});
      tools.push(...listed.tools);cursor=listed.nextCursor;
      if(cursor){if(cursors.has(cursor)||cursors.size>=100)fail('EPX_TOOLS_INVALID','unavailable','BIND-004','Provider tool pagination did not terminate.',{dependency:reference});cursors.add(cursor);}
    }while(cursor);
    const names=tools.map(t=>t.name);if(new Set(names).size!==names.length)fail('EPX_TOOLS_INVALID','unavailable','BIND-004','Provider advertised duplicate tool names.',{dependency:reference});
    for(const op of Object.values(pkg.requirements.operations).filter(o=>o.binding===reference)) {
      const pinned=pkg.contracts[op.toolContract];const discovered=tools.find(tool=>tool.name===op.tool);
      if(!discovered)fail('EPX_TOOL_UNAVAILABLE','unavailable','BIND-004','The exact intended tool is unavailable.',{dependency:reference,expected:op.tool});
      if(!deepEqual({name:discovered.name,inputSchema:discovered.inputSchema,outputSchema:discovered.outputSchema},{name:pinned.name,inputSchema:pinned.inputSchema,outputSchema:pinned.outputSchema}))
        fail('EPX_TOOL_CONTRACT_MISMATCH','unavailable','BIND-004','Discovered tool schema differs from its pinned descriptor.',{dependency:reference,expected:op.tool});
    }
    const resources=[];
    for(const [id,resource] of Object.entries(pkg.requirements.resources).filter(([,r])=>r.binding===reference)) {
      if(!object(initialized.capabilities?.resources))fail('EPX_RESOURCE_UNAVAILABLE','unavailable','RES-001','Provider does not advertise resources capability.',{dependency:id});
      let response;
      try{response=await client.request('resources/read',{uri:resource.uri});}catch(error){
        const cause=error.diagnostic?.cause;
        const code=cause?.code===-32002?'EPX_RESOURCE_ABSENT':cause?.code===-32003?'EPX_RESOURCE_DENIED':'EPX_RESOURCE_UNAVAILABLE';
        fail(code,'unavailable','RES-002','Required resource cannot be verified; configure access to the intended object.',{dependency:id,cause:cause??error.message});
      }
      const content=response?.contents?.find(c=>c.uri===resource.uri&&typeof c.text==='string');let identity;
      try{identity=strictJSON(content.text);}catch{fail('EPX_RESOURCE_UNVERIFIABLE','unavailable','RES-001','Resource did not supply its declared JSON identity evidence.',{dependency:id});}
      if(identity.id!==resource.uri||identity.provider!==intended.application.id)fail('EPX_RESOURCE_MISMATCH','unavailable','RES-001','Observed resource identity is not the intended object/provider.',{dependency:id,observed:identity});
      if(identity.revision!==resource.revision)fail('EPX_RESOURCE_REVISION_MISMATCH','unavailable','RES-001','Required resource revision is unavailable.',{dependency:id,expected:resource.revision,observed:identity.revision});
      resources.push({id,uri:identity.id,provider:identity.provider,revision:identity.revision});
    }
    return {client,intended,observed,resources,tools};
  }catch(error){await client.close();if(error instanceof Failure)throw error;fail('EPX_PROVIDER_UNAVAILABLE','unavailable','BIND-005','Provider preflight could not complete.',{dependency:reference,cause:error.message});}
}
