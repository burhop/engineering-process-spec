#!/usr/bin/env node
import path from 'node:path';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {randomUUID} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {VERSION,IMPLEMENTATION,jsonFile,schemaCheck,strictJSON,sha256,writeJSON,validateSchema,diagnostic,fail,Failure,object} from './base.mjs';
import {loadPackage} from './package.mjs';
import {openBinding} from './mcp.mjs';

export async function invoke(options) {
  const context=await jsonFile(options.context);
  if(context.format!=='epx-run-context'||context.version!==VERSION||!path.isAbsolute(context.package)||!path.isAbsolute(context.bindings)||!path.isAbsolute(context.runDirectory)||typeof context.runId!=='string')
    fail('EPX_CONTEXT_INVALID','invalid','CWL-004','Execution context is incomplete or unsupported.');
  const pkg=await loadPackage(context.package);
  if(context.packageMetadataSha256!==pkg.metadataSha256)fail('EPX_CONTEXT_STALE','invalid','CWL-004','Execution context package digest is stale.');
  const operation=pkg.requirements.operations[options.node];
  if(!operation||operation.binding!==options.binding||operation.tool!==options.tool)fail('EPX_INVOCATION_MISMATCH','invalid','CWL-003','Invocation does not match its declared node, binding and tool.',{node:options.node});
  const uid=randomUUID();const label=options.node.replace(/[^A-Za-z0-9_-]/g,'_')+'-'+uid;
  const record={format:'epx-call',version:VERSION,runId:context.runId,implementation:IMPLEMENTATION,packageMetadataSha256:pkg.metadataSha256,inputSha256:sha256(options.arguments_json),node:options.node,binding:options.binding,tool:options.tool,effect:operation.effect,status:'blocked',diagnostics:[],intendedProvider:pkg.requirements.bindings[options.binding],startedAt:new Date().toISOString()};
  let connection;let submitted=false;
  try {
    const argumentsObject=strictJSON(options.arguments_json);
    validateSchema(argumentsObject,pkg.contracts[operation.toolContract].inputSchema);
    const config=await jsonFile(context.bindings);await schemaCheck(config,'bindings.schema.json','BIND-002');
    connection=await openBinding(pkg,config,options.binding,path.dirname(context.bindings));
    record.observedProvider=connection.observed;record.resources=connection.resources;
    submitted=true;
    let result;
    try{result=await connection.client.request('tools/call',{name:options.tool,arguments:argumentsObject});}
    finally{record.request=connection.client.lastRequest;}
    record.result=result;
    const resultBytes=Buffer.from(JSON.stringify(result)+'\n');
    const relative=`artifacts/${label}.json`;await mkdir(path.join(context.runDirectory,'artifacts'),{recursive:true});await writeFile(path.join(context.runDirectory,relative),resultBytes,{flag:'wx'});
    record.artifact={path:relative,sha256:sha256(resultBytes),durability:'persistent',mediaType:'application/json'};record.resultSha256=record.artifact.sha256;
    if(!object(result)||!Array.isArray(result.content)||(result.isError!==undefined&&typeof result.isError!=='boolean'))fail('EPX_RESULT_INVALID','execution-failed','OUT-003','Malformed MCP CallToolResult.');
    if(result.isError===true)fail('EPX_TOOL_ERROR','execution-failed','OUT-003','MCP tool returned isError.',{cause:result});
    try{validateSchema(result.structuredContent,pkg.contracts[operation.toolContract].outputSchema);}catch(error){fail('EPX_OUTPUT_INVALID','execution-failed','OUT-003','Structured tool output failed its pinned contract.',{cause:diagnostic(error)});}
    await writeFile(path.join(process.cwd(),'result.json'),resultBytes);
    record.status='succeeded';
  }catch(error) {
    if(submitted&&(!(error instanceof Failure)||error.diagnostic.code==='EPX_RPC_INVALID')) {
      record.status=operation.effect==='mutation'?'unknown':'failed';
      record.diagnostics.push({code:operation.effect==='mutation'?'EPX_MUTATION_OUTCOME_UNKNOWN':'EPX_TRANSPORT_LOST',category:operation.effect==='mutation'?'outcome-unknown':'execution-failed',requirement:'RES-003',message:operation.effect==='mutation'?'A submitted mutation may have occurred; inspect before any explicit retry.':'Tool response was lost.',node:options.node,cause:error.message});
    }else{
      const detail=diagnostic(error);record.diagnostics.push({...detail,node:options.node});record.status=submitted?'failed':'blocked';
    }
  }finally {
    if(connection)await connection.client.close();record.completedAt=new Date().toISOString();
    await writeJSON(path.join(context.runDirectory,'calls',label+'.json'),record);
  }
  return record;
}

function flags(args) {
  const values={};for(let i=0;i<args.length;i+=2){if(!args[i]?.startsWith('--')||args[i+1]===undefined)throw new Error('Expected --context FILE --node NODE --binding REF --tool NAME --arguments-json JSON');values[args[i].slice(2).replaceAll('-','_')]=args[i+1];}
  for(const key of ['context','node','binding','tool','arguments_json'])if(typeof values[key]!=='string')throw new Error(`Missing --${key.replaceAll('_','-')}`);return values;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  try{const record=await invoke(flags(process.argv.slice(2)));if(record.status!=='succeeded'){process.stderr.write(JSON.stringify(record.diagnostics)+'\n');process.exitCode=1;}}
  catch(error){process.stderr.write(JSON.stringify(diagnostic(error))+'\n');process.exitCode=1;}
}
