import {readFile,writeFile,mkdir,lstat} from 'node:fs/promises';
import path from 'node:path';
import {VERSION,PROFILE,SCHEMA_ROOT,jsonFile,strictJSON,validateSchema,writeJSON,sha256,fail,deepEqual} from './base.mjs';
import {loadPackage,preserve} from './package.mjs';

// Deliberate binding revision only. This does not translate tools, graph or units.
export async function replaceBinding(source,{binding,replacementFile,revision,outDirectory}) {
  const pkg=await loadPackage(source);const prior=pkg.requirements.bindings[binding];
  if(!prior)fail('EPX_BINDING_INVALID','invalid','BIND-006','Replacement references an undeclared logical binding.',{dependency:binding});
  if(typeof revision!=='string'||!revision.trim()||revision===pkg.requirements.process.revision)fail('EPX_REPLACEMENT_REVISION_INVALID','invalid','BIND-006','Explicit replacement requires a fresh process revision.');
  const replacement=await jsonFile(replacementFile);const schema=await jsonFile(path.join(SCHEMA_ROOT,'requirements.schema.json'));
  validateSchema(replacement,{$schema:schema.$schema,$ref:'#/$defs/binding',$defs:schema.$defs},'BIND-006');
  if(deepEqual(replacement,prior))fail('EPX_REPLACEMENT_UNCHANGED','invalid','BIND-006','The supplied binding is unchanged; configure a receiving connection without editing the process.');
  const out=path.resolve(outDirectory);
  const previousBytes=pkg.payload['requirements.json'].bytes;const previousSha=sha256(previousBytes);
  const previousPath=`provenance/requirements-${previousSha}.json`;
  const reportPath=`provenance/replacement-${previousSha}-${sha256(revision).slice(0,16)}.json`;
  if(pkg.files.includes(previousPath)||pkg.files.includes(reportPath))fail('EPX_REPLACEMENT_PROVENANCE_CONFLICT','invalid','BIND-006','The intended provenance path already exists; preserve it and select another output revision.');
  const requirements=structuredClone(pkg.requirements);requirements.process.revision=revision;requirements.bindings[binding]=replacement;
  const impactedNodes=Object.entries(requirements.operations).filter(([,op])=>op.binding===binding).map(([node])=>node);
  const direct=new Set(impactedNodes);const affected=new Set(direct);const main=pkg.main;
  // Impact analysis only. CWL still owns dataflow execution and connections remain unchanged.
  for(let changed=true;changed;) {
    changed=false;
    for(const [name,step] of Object.entries(main.steps)) {
      const node=`main/${name}`;if(affected.has(node))continue;
      const sources=Object.values(step.in??{}).flatMap(input=>{const raw=typeof input==='string'?input:input.source;return raw===undefined?[]:Array.isArray(raw)?raw:[raw];});
      if(sources.some(source=>typeof source==='string'&&source.includes('/')&&affected.has(`main/${source.split('/')[0]}`))){affected.add(node);changed=true;}
    }
  }
  const change={format:'epx-binding-replacement',version:VERSION,profile:PROFILE,processId:requirements.process.id,previousRevision:pkg.requirements.process.revision,revision,binding,previousPackageMetadataSha256:pkg.metadataSha256,previousRequirements:{path:previousPath,sha256:previousSha},previousBinding:prior,replacementBinding:replacement,directlyImpactedNodes:impactedNodes,impactedNodes:[...affected].sort(),impactedAcceptance:requirements.acceptance.filter(c=>affected.has(c.node)).map(c=>c.id),impactedResources:Object.entries(requirements.resources).filter(([,r])=>r.binding===binding).map(([id])=>id),toolContractsChanged:false,graphChanged:false,resourceMappingsChanged:false,providerEquivalenceClaimed:false,previousResultsReusable:false,humanApprovalsReusable:false,execution:'not-run',nextAction:'Validate receiving identity/resources and execute new acceptance evidence; broader tool/resource mapping changes require explicit authoring.'};
  await preserve(pkg.root,out);await mkdir(path.join(out,'provenance'),{recursive:true});await writeFile(path.join(out,previousPath),previousBytes);await writeJSON(path.join(out,reportPath),change);await writeJSON(path.join(out,'requirements.json'),requirements);
  const metadata=structuredClone(pkg.metadata);const root=metadata['@graph'].find(entity=>entity['@id']==='./');
  const parts=Array.isArray(root.hasPart)?root.hasPart:[root.hasPart];root.hasPart=parts;
  for(const filename of ['requirements.json',previousPath,reportPath]) {
    const bytes=await readFile(path.join(out,filename));let entity=metadata['@graph'].find(entity=>entity['@id']===filename);
    if(!entity){entity={'@id':filename,'@type':'File'};metadata['@graph'].push(entity);root.hasPart.push({'@id':filename});}
    entity.sha256=sha256(bytes);entity.contentSize=String(bytes.length);
  }
  await writeJSON(path.join(out,'ro-crate-metadata.json'),metadata);
  const validated=await loadPackage(out);
  for(const filename of pkg.files.filter(filename=>!['requirements.json','ro-crate-metadata.json'].includes(filename)))if(!Buffer.from(await readFile(path.join(out,filename))).equals(await readFile(path.join(pkg.root,filename))))fail('EPX_REPLACEMENT_PRESERVATION_FAILED','execution-failed','BIND-006','Replacement changed an unaffected artifact.',{dependency:filename});
  return {format:'epx-replacement-result',version:VERSION,status:'valid',process:validated.requirements.process,packageMetadataSha256:validated.metadataSha256,change,changeReport:reportPath,engineeringCalls:0};
}
