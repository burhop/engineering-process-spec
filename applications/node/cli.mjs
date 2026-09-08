#!/usr/bin/env node
import {spawn,execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {readFile,writeFile,mkdir,readdir,lstat,chmod,copyFile,realpath} from 'node:fs/promises';
import {createWriteStream} from 'node:fs';
import {randomUUID} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {VERSION,PROFILE,IMPLEMENTATION,jsonFile,writeJSON,sha256,schemaCheck,diagnostic,fail,pointer,deepEqual,strictJSON,SCHEMA_ROOT} from './base.mjs';
import {loadPackage,inspectPackage,preserve,UNITS} from './package.mjs';
import {openBinding} from './mcp.mjs';
import {replaceBinding} from './replacement.mjs';

export async function preflight(pkg,bindingsFile) {
  const configuration=await jsonFile(bindingsFile);await schemaCheck(configuration,'bindings.schema.json','BIND-002');
  const observations=[];const diagnostics=[];
  for(const reference of Object.keys(pkg.requirements.bindings)) {
    let connection;
    try{connection=await openBinding(pkg,configuration,reference,path.dirname(path.resolve(bindingsFile)));observations.push({binding:reference,status:'available',intendedProvider:connection.intended,observedProvider:connection.observed,resources:connection.resources});}
    catch(error){diagnostics.push(diagnostic(error));observations.push({binding:reference,status:'unavailable'});}
    finally{if(connection)await connection.client.close();}
  }
  return {format:'epx-preflight',version:VERSION,packageMetadataSha256:pkg.metadataSha256,status:diagnostics.length?'unavailable':'available',observations,diagnostics,engineeringCalls:0};
}

export async function evaluateAcceptance(pkg,calls,runDirectory) {
  const criteria=[];
  for(const criterion of pkg.requirements.acceptance) {
    const relevant=calls.filter(call=>call.node===criterion.node);const call=relevant.find(call=>call.status==='succeeded');
    if(!call){criteria.push({id:criterion.id,node:criterion.node,status:'not-run',reason:'No successful matching call evidence.'});continue;}
    try {
      if(relevant.length!==1||call.runId!==calls[0].runId||call.packageMetadataSha256!==pkg.metadataSha256||!call.artifact||call.binding!==pkg.requirements.operations[criterion.node].binding)
        throw new Error('Call provenance does not identify exactly one successful run operation.');
      const resultBytes=await readFile(path.join(runDirectory,call.artifact.path));
      if(sha256(resultBytes)!==call.artifact.sha256||!deepEqual(strictJSON(resultBytes),call.result))throw new Error('Persisted result differs from observed evidence.');
      const quantity=pointer(call.result,criterion.quantityPointer);const value=pointer(call.result,criterion.valuePointer);const unit=pointer(call.result,criterion.unitPointer);
      if(quantity!==criterion.quantity)throw new Error('Observed quantity meaning is incompatible.');
      if(typeof value!=='number'||!Number.isFinite(value)||!UNITS[unit]||UNITS[unit][0]!==criterion.quantity)throw new Error('Observed quantity value/unit is unsupported or dimensionally incompatible.');
      const factor=UNITS[unit][1]/UNITS[criterion.unit][1];
      const converted=value*factor;
      if(!Number.isFinite(converted))throw new Error('Observed quantity cannot be represented finitely in the criterion unit.');
      const pass=criterion.expected!==undefined?Math.abs(converted-criterion.expected)<=criterion.absoluteTolerance:converted>=criterion.minimum&&converted<=criterion.maximum;
      criteria.push({id:criterion.id,node:criterion.node,status:pass?'pass':'fail',quantity,observed:{value,unit},compared:{value:converted,unit:criterion.unit},expected:criterion.expected,absoluteTolerance:criterion.absoluteTolerance,minimum:criterion.minimum,maximum:criterion.maximum,evidence:{runId:call.runId,binding:call.binding,provider:call.observedProvider,artifact:call.artifact}});
    }catch(error){criteria.push({id:criterion.id,node:criterion.node,status:'indeterminate',reason:error.message});}
  }
  const status=criteria.some(c=>c.status==='fail')?'fail':criteria.every(c=>c.status==='pass')?'pass':criteria.every(c=>c.status==='not-run')?'not-run':'indeterminate';
  return {status,criteria};
}

export async function verifyEngineOutputs(pkg,calls,runDirectory) {
  const observed=await jsonFile(path.join(runDirectory,'engine.stdout.json'));
  const root=await realpath(path.join(runDirectory,'engine-output'));
  const verified=[];
  for(const [name,definition] of Object.entries(pkg.main.outputs)) {
    const value=observed[name];
    if(value?.class!=='File')throw new Error(`Required workflow output ${name} is not an observed File.`);
    const source=definition.outputSource;
    if(typeof source!=='string')throw new Error(`Workflow output ${name} requires an unsupported composite source.`);
    const sourceNode=`main/${source.split('/')[0]}`;const matching=calls.filter(call=>call.node===sourceNode&&call.status==='succeeded');
    if(matching.length!==1||!matching[0].artifact)throw new Error(`Workflow output ${name} lacks unique successful producing-call evidence.`);
    let filename;
    if(typeof value.location==='string'&&value.location.startsWith('file:'))filename=fileURLToPath(value.location);
    else if(typeof value.path==='string'&&path.isAbsolute(value.path))filename=value.path;
    else throw new Error(`Workflow output ${name} has no readable local File location.`);
    const resolved=await realpath(filename);if(!resolved.startsWith(root+path.sep))throw new Error(`Workflow output ${name} escapes the retained engine output directory.`);
    if(!(await lstat(resolved)).isFile())throw new Error(`Workflow output ${name} is not an ordinary file.`);
    const bytes=await readFile(resolved);const digest=sha256(bytes);
    if(digest!==matching[0].artifact.sha256)throw new Error(`Workflow output ${name} differs from its producing call's observed result.`);
    verified.push({path:path.relative(runDirectory,resolved).split(path.sep).join('/'),sha256:digest,durability:'persistent',mediaType:'application/json',workflowOutput:name,node:sourceNode,outputSource:source});
  }
  return verified;
}

function executeEngine(arguments_,cwd,env,stdoutPath,stderrPath) {
  return new Promise(resolve=>{
    const out=createWriteStream(stdoutPath);const err=createWriteStream(stderrPath);
    const child=spawn(process.env.EPX_PYTHON??'python',arguments_,{cwd,env,shell:false,stdio:['ignore','pipe','pipe']});
    child.stdout.pipe(out);child.stderr.pipe(err);
    let launchError;child.on('error',error=>{launchError=error.message;});
    child.on('close',code=>{out.end();err.end();resolve({code,error:launchError});});
  });
}

export async function runPackage(pkg,bindingsFile,outDirectory,engine='streamflow') {
  if(engine!=='streamflow')fail('EPX_ENGINE_UNSUPPORTED','unsupported','CWL-001','The independent Node path uses StreamFlow.');
  const runDirectory=path.resolve(outDirectory);await mkdir(runDirectory,{recursive:true});
  if((await readdir(runDirectory)).length)fail('EPX_OUTPUT_NOT_EMPTY','invalid','OUT-001','Select an empty output directory to retain previous run evidence.');
  const runId=randomUUID();const report={format:'epx-run',version:VERSION,profile:PROFILE,implementation:IMPLEMENTATION,runtime:{node:process.version},runId,process:pkg.requirements.process,packageMetadataSha256:pkg.metadataSha256,inputSha256:sha256(pkg.jobBytes),execution:{status:'blocked'},acceptance:{status:'not-run',criteria:pkg.requirements.acceptance.map(c=>({id:c.id,status:'not-run'}))},approval:'not-requested',calls:[],outputs:[],diagnostics:[],engine:{name:'StreamFlow',exitCode:null}};
  try {
    const {stdout}=await promisify(execFile)(process.env.EPX_PYTHON??'python',['-c','from importlib.metadata import version; print(version("streamflow"))'],{timeout:15000,maxBuffer:4096});
    report.engine.version=stdout.trim();if(report.engine.version!=='0.2.0rc2')fail('EPX_ENGINE_VERSION_MISMATCH','unavailable','CORE-003','Installed StreamFlow differs from the pinned execution baseline.',{expected:'0.2.0rc2',observed:report.engine.version});
  }catch(error){report.diagnostics=[error.diagnostic??{code:'EPX_ENGINE_UNAVAILABLE',category:'unavailable',requirement:'CWL-001',message:'Install the pinned StreamFlow runtime; engine identity could not be verified.'}];await writeJSON(path.join(runDirectory,'report.json'),report);return report;}
  const bindings=path.resolve(bindingsFile);const ready=await preflight(pkg,bindings);report.preflight=ready;
  if(ready.status!=='available'){report.diagnostics=ready.diagnostics;await writeJSON(path.join(runDirectory,'report.json'),report);return report;}
  try {
    const work=path.join(runDirectory,'work');await mkdir(work);const sourceRoot=path.join(work,'source');await preserve(pkg.root,sourceRoot);const derivedRoot=path.join(work,'package');await preserve(sourceRoot,derivedRoot);
    const cwl=structuredClone(pkg.cwl);const main=cwl.$graph.find(item=>item.id==='#main');
    delete main.requirements['epx:ExchangeRequirement'];delete main.requirements['urn:engineering-process-spec:profile:ExchangeRequirement'];
    const derivedBytes=Buffer.from(JSON.stringify(cwl,null,2)+'\n');const derivedPath=path.join(derivedRoot,pkg.filename);await writeFile(derivedPath,derivedBytes);
    report.transformation={sourceSha256:sha256(pkg.workflowBytes),derivedSha256:sha256(derivedBytes),operation:'Consume implemented epx:ExchangeRequirement in an ephemeral CWL execution copy.'};
    const contextFile=path.join(work,'context.json');
    await writeJSON(contextFile,{format:'epx-run-context',version:VERSION,package:sourceRoot,bindings,runId,runDirectory,implementation:IMPLEMENTATION,packageMetadataSha256:pkg.metadataSha256});
    const job=structuredClone(pkg.job);job.epx_context={class:'File',location:pathToFileURL(contextFile).href};
    const jobFile=path.join(derivedRoot,pkg.requirements.job);await writeJSON(jobFile,job);
    const bin=path.join(work,'bin');await mkdir(bin);const adapter=fileURLToPath(new URL('./mcp-call.mjs',import.meta.url));
    if(process.platform==='win32') {
      await writeFile(path.join(bin,'epx-mcp-call.cmd'),`@echo off\r\n"${process.execPath}" "${adapter}" %*\r\n`);
    } else {
      const quote=value=>"'"+value.replaceAll("'","'\\''")+"'";
      const launcher=path.join(bin,'epx-mcp-call');await writeFile(launcher,`#!/bin/sh\nexec ${quote(process.execPath)} ${quote(adapter)} "$@"\n`);await chmod(launcher,0o755);
    }
    const engineOut=path.join(runDirectory,'engine-output');await mkdir(engineOut);
    const env={...process.env,PATH:bin+path.delimiter+process.env.PATH,EPX_SCHEMA_ROOT:SCHEMA_ROOT};
    const outcome=await executeEngine(['-c','from streamflow.cwl.runner import run; run()','--outdir',engineOut,derivedPath+'#main',jobFile],work,env,path.join(runDirectory,'engine.stdout.json'),path.join(runDirectory,'engine.stderr.log'));
    report.engine.exitCode=outcome.code;
    if(outcome.error)report.diagnostics.push({code:'EPX_ENGINE_UNAVAILABLE',category:'unavailable',requirement:'CWL-001',message:'StreamFlow could not be started.',cause:outcome.error});
    const callsDirectory=path.join(runDirectory,'calls');
    try{for(const file of (await readdir(callsDirectory)).sort())if(file.endsWith('.json'))report.calls.push(await jsonFile(path.join(callsDirectory,file)));}catch(error){if(error.code!=='ENOENT')throw error;}
    for(const call of report.calls){report.diagnostics.push(...call.diagnostics);if(call.artifact)report.outputs.push(call.artifact);}
    const allNodes=new Set(Object.keys(pkg.requirements.operations));const completed=report.calls.filter(call=>call.status==='succeeded');
    const exact=completed.length===allNodes.size&&new Set(completed.map(c=>c.node)).size===allNodes.size&&completed.every(c=>allNodes.has(c.node));
    let finalOutputs=false;
    try{report.outputs.push(...await verifyEngineOutputs(pkg,report.calls,runDirectory));finalOutputs=true;}
    catch(error){report.diagnostics.push({code:'EPX_ENGINE_OUTPUT_INVALID',category:'execution-failed',requirement:'CWL-005',message:'Required workflow outputs were not materialized with matching observed call bytes.',cause:error.message});}
    report.execution.status=report.calls.some(c=>c.status==='unknown')?'unknown':outcome.code===0&&exact&&finalOutputs&&report.calls.every(c=>c.status==='succeeded')?'succeeded':'failed';
    if(outcome.code!==0&&!report.diagnostics.length)report.diagnostics.push({code:'EPX_ENGINE_FAILED',category:'execution-failed',requirement:'CWL-001',message:'CWL engine did not finish successfully; inspect the retained engine log.'});
    if(outcome.code===0&&!exact)report.diagnostics.push({code:'EPX_REQUIRED_OUTPUT_MISSING',category:'execution-failed',requirement:'CWL-005',message:'Engine exit does not establish successful evidence from every required node.'});
    report.acceptance=await evaluateAcceptance(pkg,report.calls,runDirectory);
  } catch(error){report.diagnostics.push(diagnostic(error));report.execution.status=report.calls.some(c=>c.status==='unknown')?'unknown':'failed';}
  await schemaCheck(report,'run.schema.json','OUT-001');await writeJSON(path.join(runDirectory,'report.json'),report);return report;
}

function parseCLI(args) {
  const [command,source,...rest]=args;const options={};for(let i=0;i<rest.length;i+=2){if(!rest[i]?.startsWith('--')||rest[i+1]===undefined)throw new Error('Options require --name VALUE pairs.');options[rest[i].slice(2)]=rest[i+1];}
  if(!['inspect','validate','preserve','preflight','run','replace'].includes(command)||!source)throw new Error('Usage: epx-node inspect|validate|preserve|preflight|run|replace PACKAGE [--bindings FILE] [--engine streamflow] [--out DIRECTORY]');return {command,source,options};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  try {
    const {command,source,options}=parseCLI(process.argv.slice(2));let result;
    if(command==='preserve'){if(!options.out)throw new Error('preserve requires --out');result=await preserve(source,options.out);}
    else if(command==='replace'){for(const name of ['binding','with','revision','out'])if(!options[name])throw new Error(`replace requires --${name}`);result=await replaceBinding(source,{binding:options.binding,replacementFile:options.with,revision:options.revision,outDirectory:options.out});}
    else {
      const pkg=await loadPackage(source);
      if(command==='inspect'||command==='validate')result=inspectPackage(pkg);
      else {if(!options.bindings)throw new Error(`${command} requires --bindings`);result=command==='preflight'?await preflight(pkg,options.bindings):await runPackage(pkg,options.bindings,options.out??'epx-node-run',options.engine??'streamflow');}
    }
    process.stdout.write(JSON.stringify(result,null,2)+'\n');
    if(result.status==='unavailable'||(result.execution&&result.execution.status!=='succeeded')||(command==='run'&&result.acceptance?.status!=='pass'))process.exitCode=1;
  } catch(error){process.stdout.write(JSON.stringify({valid:false,diagnostics:[diagnostic(error)]},null,2)+'\n');process.exitCode=1;}
}
