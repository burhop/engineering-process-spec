import {readFile,writeFile,lstat,readdir,mkdir,mkdtemp,copyFile,realpath} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import yauzl from 'yauzl';
import {PROFILE,VERSION,portablePath,jsonFile,parseCWL,strictJSON,schemaCheck,sha256,fail,Failure,object,own,deepEqual} from './base.mjs';

const FEATURES=new Set(['cwl-mcp-core','quantity-acceptance','resource-revisions']);
const CWL_FEATURES=new Set(['InlineJavascriptRequirement','StepInputExpressionRequirement','MultipleInputFeatureRequirement','urn:engineering-process-spec:profile:ExchangeRequirement','epx:ExchangeRequirement']);
const CWL_DOCUMENT_FIELDS=new Set(['cwlVersion','$graph','$namespaces','$schemas','$base','id']);
const CWL_WORKFLOW_FIELDS=new Set(['id','label','doc','inputs','outputs','requirements','hints','cwlVersion','intent','class','steps','$namespaces','$schemas','$base']);
const CWL_TOOL_FIELDS=new Set(['id','label','doc','inputs','outputs','requirements','hints','cwlVersion','intent','class','baseCommand','arguments','stdin','stderr','stdout','successCodes','temporaryFailCodes','permanentFailCodes','$namespaces','$schemas','$base']);
const CWL_STEP_FIELDS=new Set(['id','label','doc','in','out','requirements','hints','run','when','scatter','scatterMethod']);
function cwlFields(value,allowed,location) {
  if(!object(value))fail('EPX_CWL_INVALID','invalid','CWL-001','CWL declarations must be objects.',{dependency:location});
  if(own(value,'$base'))fail('EPX_CWL_FEATURE_UNSUPPORTED','unsupported','CWL-001','A base-URI override is outside this package-local resolution profile.',{dependency:location+'/$base'});
  if(own(value,'cwlVersion')&&value.cwlVersion!=='v1.2')fail('EPX_CWL_UNSUPPORTED','unsupported','CWL-001','Only CWL v1.2 is implemented.',{dependency:location,expected:'v1.2',observed:value.cwlVersion});
  for(const field of Object.keys(value))if(!allowed.has(field)&&!field.includes(':'))
    fail('EPX_CWL_INVALID','invalid','CWL-001','Unknown unqualified CWL field.',{dependency:`${location}/${field}`,observed:field});
}
export const UNITS={m:['length',1],mm:['length',0.001],kg:['mass',1],g:['mass',0.001],m3:['volume',1],mm3:['volume',1e-9],'kg/m3':['density',1],'g/cm3':['density',1000]};
export function validateDefaultJob(inputs,job) {
  const invalid=(message,location)=>fail('EPX_CWL_INPUT_INVALID','invalid','CWL-001',message,{dependency:location});
  const unsupported=(type,location)=>fail('EPX_CWL_FEATURE_UNSUPPORTED','unsupported','CWL-001','Input type meaning is outside this reader’s supported CWL types.',{dependency:location,observed:type});
  if(!object(inputs)||!object(job))invalid('Workflow inputs and the default job must be named objects.','inputs');
  const names=new Map();
  function collect(value) {
    if(Array.isArray(value)){value.forEach(collect);return;}
    if(!object(value))return;
    if(['record','enum'].includes(value.type)&&typeof value.name==='string') {
      names.set(value.name,value);names.set(value.name.split(/[#/]/).at(-1),value);
    }
    Object.values(value).forEach(collect);
  }
  collect(inputs);
  function nullable(type,depth=0) {
    if(depth>150)return false;
    if(Array.isArray(type))return type.some(item=>nullable(item,depth+1));
    if(object(type))return nullable(type.type,depth+1);
    return type==='null'||(typeof type==='string'&&type.endsWith('?'));
  }
  function check(type,value,location,depth=0) {
    if(depth>150)unsupported(type,location);
    if(Array.isArray(type)) {
      const errors=[];
      for(const option of type)try{check(option,value,location,depth+1);return;}catch(error){errors.push(error);}
      throw errors.find(error=>error.diagnostic?.category==='unsupported')??errors[0]??new Error('Empty CWL type union.');
    }
    if(object(type)) {
      if(type.type==='record') {
        if(!object(value))invalid('Input value must be a CWL record.',location);
        const fields=Array.isArray(type.fields)?type.fields:object(type.fields)?Object.entries(type.fields).map(([name,definition])=>object(definition)?{...definition,name}:{name,type:definition}):null;
        if(!fields)invalid('CWL record fields must be a named map or field list.',location);
        for(const field of fields) {
          if(!object(field)||typeof field.name!=='string')invalid('CWL record field declaration is invalid.',location);
          const name=field.name.split(/[#/]/).at(-1);const item=own(value,name)?value[name]:own(field,'default')?field.default:undefined;
          if(item===undefined){if(!nullable(field.type))invalid('Required CWL record field is missing.',location+'/'+name);}
          else check(field.type,item,location+'/'+name,depth+1);
        }
        return;
      }
      if(type.type==='array') {
        if(!Array.isArray(value))invalid('Input value must be a CWL array.',location);
        value.forEach((item,index)=>check(type.items,item,location+'/'+index,depth+1));return;
      }
      if(type.type==='enum') {
        if(typeof value!=='string'||!Array.isArray(type.symbols)||!type.symbols.includes(value))invalid('Input value is not a declared CWL enum symbol.',location);return;
      }
      check(type.type,value,location,depth+1);return;
    }
    if(typeof type!=='string')invalid('CWL input type declaration is missing or invalid.',location);
    if(type.endsWith('?')){check(['null',type.slice(0,-1)],value,location,depth+1);return;}
    if(type.endsWith('[]')){check({type:'array',items:type.slice(0,-2)},value,location,depth+1);return;}
    if(names.has(type)){check(names.get(type),value,location,depth+1);return;}
    const valid=type==='Any'?value!==null:type==='null'?value===null:type==='boolean'?typeof value==='boolean':type==='string'?typeof value==='string':
      ['int','long'].includes(type)?typeof value==='number'&&Number.isFinite(value)&&Number.isInteger(value):
      ['float','double'].includes(type)?typeof value==='number'&&Number.isFinite(value):
      ['File','Directory'].includes(type)?object(value)&&value.class===type:undefined;
    if(valid===undefined)unsupported(type,location);
    if(!valid)invalid('Input value does not match its declared CWL type.',location);
  }
  for(const [name,parameter] of Object.entries(inputs)) {
    if(name==='epx_context')continue;
    const type=object(parameter)?parameter.type:parameter;
    const supplied=own(job,name)?job[name]:undefined;
    const value=(supplied===undefined||supplied===null)&&object(parameter)&&own(parameter,'default')?parameter.default:supplied;
    if(value===undefined){if(!nullable(type))invalid('Required CWL workflow input is missing.','inputs/'+name);}
    else check(type,value,'inputs/'+name);
  }
}
const typeHas=(value,kind)=>value===kind||(Array.isArray(value)&&value.includes(kind));
const idOf=ref=>object(ref)?ref['@id']:ref;
const asArray=value=>value===undefined?[]:Array.isArray(value)?value:[value];
const nonemptyText=value=>typeof value==='string'&&value.trim().length>0;
function isoPublished(value) {
  if(typeof value!=='string')return false;
  const match=/^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if(!match)return false;
  const [,year,month,day]=match;
  if(Number(year)<1||Number(month)<1||Number(month)>12)return false;
  const y=Number(year);const days=[31,(y%4===0&&(y%100!==0||y%400===0))?29:28,31,30,31,30,31,31,30,31,30,31];
  return Number(day)>=1&&Number(day)<=days[Number(month)-1];
}

async function filesIn(root,current='',result=[]) {
  for(const entry of await readdir(path.join(root,current),{withFileTypes:true})) {
    const relative=current?`${current}/${entry.name}`:entry.name;portablePath(relative);
    const stat=await lstat(path.join(root,relative));
    if(stat.isSymbolicLink()||(!stat.isDirectory()&&!stat.isFile()))fail('EPX_PATH_INVALID','invalid','PKG-001','Package contains a symlink or special file.',{dependency:relative});
    if(stat.isDirectory())await filesIn(root,relative,result);else {if(stat.size>32*1024*1024)fail('EPX_PACKAGE_LIMIT','unsupported','PKG-001','Payload exceeds this reader’s 32 MiB limit.',{dependency:relative});result.push(relative);}
    if(result.length>10000)fail('EPX_PACKAGE_LIMIT','unsupported','PKG-001','Package exceeds this reader’s file limit.');
  }
  return result;
}

async function extractZip(filename) {
  const root=await mkdtemp(path.join(os.tmpdir(),'epx-node-import-'));
  await new Promise((resolve,reject)=>yauzl.open(filename,{lazyEntries:true,strictFileNames:true},(error,zip)=>{
    if(error){reject(error);return;}
    const names=new Set();let total=0;
    const stop=error=>{zip.close();reject(error);};
    zip.on('error',stop);zip.on('end',resolve);
    zip.on('entry',async entry=>{
      try{
        const directory=entry.fileName.endsWith('/');const name=directory?entry.fileName.slice(0,-1):entry.fileName;portablePath(name);
        if(names.has(name))fail('EPX_ZIP_DUPLICATE','invalid','PKG-001','Archive contains duplicate members.',{dependency:name});names.add(name);
        if(((entry.externalFileAttributes>>>16)&0xf000)===0xa000)fail('EPX_PATH_INVALID','invalid','PKG-001','Archive symlinks are invalid.',{dependency:name});
        total+=entry.uncompressedSize;if(total>128*1024*1024||names.size>10000)fail('EPX_PACKAGE_LIMIT','unsupported','PKG-001','Archive exceeds bounded import size.');
        const destination=path.join(root,name);
        if(directory){await mkdir(destination,{recursive:true});zip.readEntry();return;}
        zip.openReadStream(entry,async(error,stream)=>{
          if(error){stop(error);return;}
          try{const chunks=[];for await(const chunk of stream)chunks.push(chunk);await mkdir(path.dirname(destination),{recursive:true});await writeFile(destination,Buffer.concat(chunks),{flag:'wx'});zip.readEntry();}catch(error){stop(error);}
        });
      }catch(error){stop(error);}
    });zip.readEntry();
  }));
  return root;
}

export async function preserve(source,destination) {
  const stat=await lstat(source);
  if(stat.isSymbolicLink())fail('EPX_PATH_INVALID','invalid','PKG-001','Cannot preserve a symlink as a package.');
  if(stat.isFile()) {await mkdir(path.dirname(path.resolve(destination)),{recursive:true});await copyFile(source,destination,1);return {sourceSha256:sha256(await readFile(source)),savedSha256:sha256(await readFile(destination)),files:1};}
  const root=await realpath(source);const dest=path.resolve(destination);
  if(dest===root||dest.startsWith(root+path.sep))fail('EPX_PRESERVE_DESTINATION','invalid','PKG-004','Preservation destination must be outside the source package.');
  await mkdir(dest,{recursive:false});
  const files=await filesIn(root);const digests={};
  for(const file of files){await mkdir(path.dirname(path.join(dest,file)),{recursive:true});await copyFile(path.join(root,file),path.join(dest,file),1);const before=sha256(await readFile(path.join(root,file)));const after=sha256(await readFile(path.join(dest,file)));if(before!==after)fail('EPX_PRESERVE_FAILED','execution-failed','PKG-004','Preserved bytes changed during copy.');digests[file]=after;}
  return {files:files.length,digests};
}

export async function loadPackage(source) {
  try{return await readPackage(source);}catch(error){if(error instanceof Failure)throw error;fail('EPX_PACKAGE_INVALID','invalid','PKG-001','Package could not be read as a bounded complete exchange.',{cause:error.message});}
}
async function readPackage(source) {
  const stat=await lstat(source);
  if(stat.isSymbolicLink())fail('EPX_PATH_INVALID','invalid','PKG-001','Package root is a symlink.');
  const root=stat.isDirectory()?await realpath(source):await extractZip(source);
  const files=await filesIn(root);const bytes=await readFile(path.join(root,'ro-crate-metadata.json'));const metadata=strictJSON(bytes);
  if(!asArray(metadata['@context']).includes('https://w3id.org/ro/crate/1.2/context'))fail('EPX_CRATE_INVALID','invalid','PKG-002','Metadata must use the RO-Crate1.2 context.');
  if(!Array.isArray(metadata['@graph']))fail('EPX_CRATE_INVALID','invalid','PKG-002','Metadata requires an entity graph.');
  const entities=new Map();for(const entity of metadata['@graph']){if(!object(entity)||typeof entity['@id']!=='string'||entities.has(entity['@id']))fail('EPX_CRATE_INVALID','invalid','PKG-002','Metadata entity IDs must be unique.');entities.set(entity['@id'],entity);}
  const dataset=entities.get('./');const descriptor=entities.get('ro-crate-metadata.json');
  if(!typeHas(dataset?.['@type'],'Dataset')||!typeHas(descriptor?.['@type'],'CreativeWork')||idOf(descriptor?.about)!=='./'||!asArray(dataset.conformsTo).some(ref=>idOf(ref)===PROFILE))
    fail('EPX_CRATE_INVALID','invalid','PKG-002','Metadata root/descriptor/profile references do not match the core.');
  if(!nonemptyText(dataset.name)||!nonemptyText(dataset.description)||!isoPublished(dataset.datePublished))
    fail('EPX_CRATE_INVALID','invalid','PKG-002','RO-Crate root requires name, description and a YYYY-MM-DD datePublished string.');
  const licenseEntity=object(dataset.license)?entities.get(idOf(dataset.license)):undefined;
  if(!nonemptyText(dataset.license)&&!(licenseEntity&&nonemptyText(licenseEntity.name)&&nonemptyText(licenseEntity.description)))
    fail('EPX_CRATE_INVALID','invalid','PKG-002','RO-Crate license requires nonempty text or a described entity reference.');
  const payload={};
  for(const [id,entity] of entities)if(typeHas(entity['@type'],'File')&&id!=='ro-crate-metadata.json') {
    portablePath(id);if(!files.includes(id))fail('EPX_PAYLOAD_MISSING','invalid','PKG-002','Inventoried package payload is missing.',{dependency:id});
    const content=await readFile(path.join(root,id));const digest=sha256(content);
    if(entity.sha256!==digest)fail('EPX_PAYLOAD_DIGEST_MISMATCH','invalid','PKG-002','Payload bytes differ from inventory.',{dependency:id,expected:entity.sha256,observed:digest});
    payload[id]={sha256:digest,bytes:content};
  }
  const requireFile=relative=>{portablePath(relative);if(!payload[relative])fail('EPX_PAYLOAD_UNDECLARED','invalid','PKG-002','Required local payload is absent from the hashed File inventory.',{dependency:relative});return payload[relative].bytes;};
  const requirements=strictJSON(requireFile('requirements.json'));
  if(requirements.version!==VERSION||requirements.profile!==PROFILE)fail('EPX_PROFILE_UNSUPPORTED','unsupported','CORE-003','Unsupported required profile/version.',{expected:PROFILE,observed:requirements.profile});
  await schemaCheck(requirements,'requirements.schema.json');
  if(!asArray(dataset.hasPart).some(ref=>idOf(ref)==='requirements.json'))fail('EPX_CRATE_INVALID','invalid','PKG-002','Requirements must be included in root hasPart.');
  for(const feature of requirements.requiredFeatures)if(!FEATURES.has(feature))fail('EPX_FEATURE_UNSUPPORTED','unsupported','PKG-003','Required feature is not implemented.',{dependency:feature});
  if([...FEATURES].some(feature=>!requirements.requiredFeatures.includes(feature)))fail('EPX_FEATURE_INVALID','invalid','PKG-003','A mandatory core feature group is missing.',{expected:[...FEATURES],observed:requirements.requiredFeatures});
  const filename=requirements.process.entrypoint.split('#')[0];
  if(/\.ya?ml$/i.test(filename))fail('EPX_CWL_UNSUPPORTED','unsupported','CWL-001','This core uses packed CWL JSON; YAML serialization is outside its supported profile.',{dependency:filename});
  if(idOf(dataset.mainEntity)!==filename&&idOf(dataset.mainEntity)!==requirements.process.entrypoint)fail('EPX_ENTRYPOINT_INVALID','invalid','PKG-003','CWL entrypoint conflicts with metadata mainEntity.');
  const workflowBytes=requireFile(filename);const cwl=parseCWL(workflowBytes);
  cwlFields(cwl,CWL_DOCUMENT_FIELDS,filename);
  if(cwl.cwlVersion!=='v1.2')fail('EPX_CWL_UNSUPPORTED','unsupported','CWL-001','Only CWL v1.2 is implemented.');
  if(!Array.isArray(cwl.$graph))fail('EPX_CWL_UNSUPPORTED','unsupported','CWL-001','This core requires a packed #main workflow.');
  const graph=new Map();for(const entry of cwl.$graph){if(graph.has(entry.id))fail('EPX_CWL_INVALID','invalid','CWL-001','Duplicate CWL graph IDs.');graph.set(entry.id,entry);}
  const main=graph.get('#main');if(main?.class!=='Workflow')fail('EPX_CWL_INVALID','invalid','CWL-001','Entrypoint must be #main Workflow.');
  for(const entry of cwl.$graph) {
    if(entry.class==='Workflow') {
      cwlFields(entry,CWL_WORKFLOW_FIELDS,entry.id);
      if(entry.id!=='#main')fail('EPX_CWL_FEATURE_UNSUPPORTED','unsupported','CWL-001','Only the main workflow is supported in this fixed MCP core.',{dependency:entry.id});
    }
    else if(entry.class==='CommandLineTool')cwlFields(entry,CWL_TOOL_FIELDS,entry.id);
    else fail('EPX_CWL_FEATURE_UNSUPPORTED','unsupported','CWL-001','Packed process class is outside the fixed MCP workflow core.',{dependency:entry.id,observed:entry.class});
  }
  if({...cwl.$namespaces,...main.$namespaces}.epx!=='urn:engineering-process-spec:profile:')fail('EPX_EXCHANGE_INVALID','invalid','CWL-002','Required epx namespace mapping is absent.');
  if(!object(main.requirements))fail('EPX_CWL_FEATURE_UNSUPPORTED','unsupported','CWL-001','This core requires the named requirements-map representation.');
  if(!deepEqual(main.requirements?.['epx:ExchangeRequirement'],{manifest:'requirements.json'})&&!deepEqual(main.requirements?.['urn:engineering-process-spec:profile:ExchangeRequirement'],{manifest:'requirements.json'}))
    fail('EPX_EXCHANGE_INVALID','invalid','CWL-002','Main workflow must require the exchange contract.');
  for(const entry of cwl.$graph)for(const feature of Object.keys(entry.requirements??{}))if(!CWL_FEATURES.has(feature))fail('EPX_CWL_FEATURE_UNSUPPORTED','unsupported','CWL-001','Required CWL feature is outside this core.',{dependency:feature});
  const inputs=main.inputs??{};if(!(inputs.epx_context==='File'||inputs.epx_context?.type==='File'))fail('EPX_CONTEXT_INVALID','invalid','CWL-004','Workflow requires reserved File input epx_context.');
  const steps=main.steps;if(!object(steps)||!Object.keys(steps).length)fail('EPX_CWL_INVALID','invalid','CWL-001','Main workflow requires named steps.');
  const nodeIds=new Set(Object.keys(steps).map(key=>`main/${key}`));
  const contracts={};
  for(const [node,op] of Object.entries(requirements.operations)) {
    if(!nodeIds.has(node)||!own(requirements.bindings,op.binding))fail('EPX_OPERATION_INVALID','invalid','CWL-003','Operation refers to missing node or binding.',{node,dependency:op.binding});
    const contract=strictJSON(requireFile(op.toolContract));
    if(contract.name!==op.tool||!object(contract.inputSchema)||!object(contract.outputSchema))fail('EPX_CONTRACT_INVALID','invalid','BIND-004','Tool descriptor lacks the exact operation name or input/output schema.',{node});contracts[op.toolContract]=contract;
  }
  const dependencies={};
  for(const [name,step] of Object.entries(steps)) {
    const node=`main/${name}`;
    cwlFields(step,CWL_STEP_FIELDS,node);
    if(!requirements.operations[node])fail('EPX_OPERATION_UNDECLARED','invalid','CWL-003','Every core node needs a declared MCP operation.',{node});
    if(step.scatter!==undefined||step.scatterMethod!==undefined||step.when!==undefined)fail('EPX_CWL_FEATURE_UNSUPPORTED','unsupported','CWL-001','Scatter and conditional tasks are outside this execution core.',{node});
    if(Object.keys(step.requirements??{}).length)fail('EPX_CWL_FEATURE_UNSUPPORTED','unsupported','CWL-001','Step-local requirements require a separately declared profile.',{node});
    if(typeof step.run!=='string'||!step.run.startsWith('#')||!graph.has(step.run))fail('EPX_CWL_FEATURE_UNSUPPORTED','unsupported','CWL-001','Core steps refer to packed CommandLineTool declarations.',{node,dependency:step.run});
    const tool=graph.get(step.run);
    if(tool?.class==='Workflow'||tool?.class==='ExpressionTool')fail('EPX_CWL_FEATURE_UNSUPPORTED','unsupported','CWL-001','Subworkflows and expression tools require another declared profile.',{node});
    if(tool?.class!=='CommandLineTool'||!(['epx-mcp-call'].includes(tool.baseCommand)||(Array.isArray(tool.baseCommand)&&tool.baseCommand.length===1&&tool.baseCommand[0]==='epx-mcp-call')))
      fail('EPX_ADAPTER_INVALID','invalid','CWL-003','Core operation must invoke the declared epx-mcp-call adapter.',{node});
    cwlFields(tool,CWL_TOOL_FIELDS,node+'/run');
    if(['stdin','stdout','stderr','successCodes','temporaryFailCodes','permanentFailCodes'].some(field=>own(tool,field))||['arguments','requirements','hints'].some(field=>tool[field]!==undefined&&Object.keys(tool[field]??{}).length))fail('EPX_ADAPTER_UNSUPPORTED','unsupported','CWL-003','Tool-level invocation overrides require a separately declared profile.',{node});
    const invocationFields=['context','node','binding','tool','arguments_json'];
    if(!object(tool.inputs)||Object.keys(tool.inputs).length!==invocationFields.length||Object.keys(tool.inputs).some(field=>!invocationFields.includes(field)))fail('EPX_ADAPTER_INVALID','invalid','CWL-003','The core adapter requires exactly its five declared inputs.',{node});
    for(const field of invocationFields) {
      const definition=tool.inputs[field];const binding=definition.inputBinding;const prefix='--'+field.replaceAll('_','-');
      if(definition.type!==(field==='context'?'File':'string')||!object(binding)||binding.prefix!==prefix||own(binding,'valueFrom'))
        fail('EPX_ADAPTER_INVALID','invalid','CWL-003','Adapter input types, prefixes or overrides differ from the fixed invocation contract.',{node,dependency:field});
    }
    if(tool.outputs?.result?.type!=='File'||tool.outputs.result.outputBinding?.glob!=='result.json')fail('EPX_ADAPTER_INVALID','invalid','CWL-005','Adapter result output must expose its observed result.json File.',{node});
    if(step.in?.context!=='epx_context'&&(!object(step.in?.context)||step.in.context.source!=='epx_context'||Object.keys(step.in.context).length!==1))fail('EPX_CONTEXT_INVALID','invalid','CWL-004','Every step must pass the reserved context source unchanged.',{node});
    const op=requirements.operations[node];
    for(const [field,value] of Object.entries({node,binding:op.binding,tool:op.tool}))if(step.in?.[field]?.default!==value||Object.keys(step.in[field]).length!==1)fail('EPX_OPERATION_INVALID','invalid','CWL-003','Task invocation identity conflicts with operation requirements.',{node,dependency:field,expected:value,observed:step.in?.[field]});
    for(const output of asArray(step.out))if(!own(tool.outputs??{},typeof output==='string'?output:output.id))fail('EPX_HANDOFF_INVALID','invalid','CWL-005','Step declares an output absent from its CommandLineTool.',{node});
    dependencies[name]=new Set();
    for(const input of Object.values(step.in??{}))for(const source of asArray(typeof input==='string'?input:input.source)) {
      if(typeof source!=='string')fail('EPX_CWL_INVALID','invalid','CWL-005','Invalid source reference.',{node});
      const [sourceStep,output,...rest]=source.split('/');
      if(output){if(rest.length||!steps[sourceStep]||!asArray(steps[sourceStep].out).some(o=>(typeof o==='string'?o:o.id)===output))fail('EPX_HANDOFF_INVALID','invalid','CWL-005','Connection references missing node output.',{node,dependency:source});dependencies[name].add(sourceStep);}
      else if(!own(inputs,sourceStep))fail('EPX_HANDOFF_INVALID','invalid','CWL-005','Connection references missing workflow input.',{node,dependency:source});
    }
  }
  const ready=new Set();while(ready.size<nodeIds.size){const next=Object.keys(steps).filter(k=>!ready.has(k)&&[...dependencies[k]].every(d=>ready.has(d)));if(!next.length)fail('EPX_CYCLE_INVALID','invalid','CWL-005','CWL dataflow contains a cycle.');next.forEach(k=>ready.add(k));}
  for(const [id,resource] of Object.entries(requirements.resources))if(!own(requirements.bindings,resource.binding))fail('EPX_RESOURCE_INVALID','invalid','RES-001','Resource refers to an undeclared binding.',{dependency:id});
  const criteria=new Set();for(const criterion of requirements.acceptance){if(criteria.has(criterion.id)||!nodeIds.has(criterion.node))fail('EPX_ACCEPTANCE_INVALID','invalid','ACC-001','Acceptance IDs must be unique and nodes must resolve.');criteria.add(criterion.id);if(!UNITS[criterion.unit])fail('EPX_UNIT_UNSUPPORTED','unsupported','ACC-001','Acceptance unit is unsupported.',{dependency:criterion.id,observed:criterion.unit});if(UNITS[criterion.unit][0]!==criterion.quantity||criterion.minimum>criterion.maximum)fail('EPX_ACCEPTANCE_INVALID','invalid','ACC-001','Acceptance dimensions/bounds are inconsistent.',{dependency:criterion.id});}
  if(!object(main.outputs)||!Object.keys(main.outputs).length)fail('EPX_HANDOFF_INVALID','invalid','CWL-005','Workflow must declare materialized outputs.');
  for(const output of Object.values(main.outputs)) {
    if(output.type!=='File'||typeof output.outputSource!=='string')fail('EPX_CWL_FEATURE_UNSUPPORTED','unsupported','CWL-005','This core materializes one File per workflow output.');
    for(const source of asArray(output.outputSource)) {
    const [step,key,...rest]=String(source).split('/');if(rest.length||!steps[step]||!asArray(steps[step].out).some(o=>(typeof o==='string'?o:o.id)===key))fail('EPX_HANDOFF_INVALID','invalid','CWL-005','Workflow output references missing task output.',{dependency:source});
    }
  }
  const jobBytes=requireFile(requirements.job);const job=strictJSON(jobBytes);if(own(job,'epx_context'))fail('EPX_CONTEXT_INVALID','invalid','CWL-004','Shared input job cannot supply receiving execution context.');
  validateDefaultJob(inputs,job);
  const references=value=>{if(!object(value)&&!Array.isArray(value))return;if(value.class==='File')requireFile(value.location??value.path);for(const [key,item] of Object.entries(value)){if(['$include','$import'].includes(key))requireFile(item);else references(item);}};
  references(cwl);references(job);
  return {root,files,metadata,metadataSha256:sha256(bytes),payload,requirements,cwl,main,contracts,job,jobBytes,workflowBytes,filename};
}

export function inspectPackage(pkg) {
  return {format:'epx-inspection',version:VERSION,profile:PROFILE,valid:true,process:pkg.requirements.process,packageMetadataSha256:pkg.metadataSha256,requiredFeatures:pkg.requirements.requiredFeatures,steps:Object.entries(pkg.requirements.operations).map(([node,operation])=>({node,...operation})),bindings:pkg.requirements.bindings,resources:pkg.requirements.resources,acceptance:pkg.requirements.acceptance,files:Object.fromEntries(Object.entries(pkg.payload).map(([name,value])=>[name,value.sha256])),engineeringCalls:0};
}
