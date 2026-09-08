import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,readFile,writeFile} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {strictJSON,sha256,jsonFile,writeJSON} from '../base.mjs';
import {loadPackage,preserve,inspectPackage,validateDefaultJob} from '../package.mjs';
import {replaceBinding} from '../replacement.mjs';

const fixture=fileURLToPath(new URL('../../../examples/calculation',import.meta.url));
const temporary=()=>mkdtemp(path.join(os.tmpdir(),'epx-node-test-'));
async function modified(change) {
  const root=path.join(await temporary(),'package');await preserve(fixture,root);
  const required=await jsonFile(path.join(root,'requirements.json'));change(required);
  await writeJSON(path.join(root,'requirements.json'),required);
  const metadata=await jsonFile(path.join(root,'ro-crate-metadata.json'));
  metadata['@graph'].find(entity=>entity['@id']==='requirements.json').sha256=sha256(await readFile(path.join(root,'requirements.json')));
  await writeJSON(path.join(root,'ro-crate-metadata.json'),metadata);return root;
}
test('strict JSON rejects duplicate identities, invalid whitespace and non-finite numeric values',()=>{
  for(const text of ['{"a":1,"a":2}','{"a":{"x":1,"x":2}}','{"x":1e999}','[NaN]','\v{}','{"x":1,}','{} trailing'])assert.throws(()=>strictJSON(text));
  assert.equal(strictJSON('{"safe": [true,null,-1.25e2]}').safe[2],-125);
});
test('reader validates the public calculation without provider calls',async()=>{
  const report=inspectPackage(await loadPackage(fixture));assert.equal(report.engineeringCalls,0);assert.deepEqual(report.steps.map(step=>step.node),['main/volume','main/mass']);
});
test('successful public inspect and validate commands exit zero with unevaluated acceptance criteria',()=>{
  const cli=fileURLToPath(new URL('../cli.mjs',import.meta.url));
  for(const command of ['inspect','validate']) {
    const result=spawnSync(process.execPath,[cli,command,fixture],{encoding:'utf8',timeout:15000});
    assert.equal(result.status,0,result.stderr||result.stdout);
    const report=JSON.parse(result.stdout);assert.equal(report.valid,true);assert.equal(report.engineeringCalls,0);
    assert.ok(Array.isArray(report.acceptance));
  }
});
test('no-op save preserves unknown optional content and every byte',async()=>{
  const root=await modified(required=>required.extensions={'urn:test:future':{opaque:['leave',17]}});
  const target=path.join(await temporary(),'saved');await preserve(root,target);
  const before=await loadPackage(root);const after=await loadPackage(target);
  assert.equal(before.metadataSha256,after.metadataSha256);
  for(const file of before.files)assert.deepEqual(await readFile(path.join(root,file)),await readFile(path.join(target,file)));
});
test('unknown required feature is unsupported and remains preservable',async()=>{
  const root=await modified(required=>required.requiredFeatures.push('future-approval'));
  await assert.rejects(loadPackage(root),error=>error.diagnostic?.category==='unsupported');
  const saved=path.join(await temporary(),'saved');await preserve(root,saved);
  assert.deepEqual(await readFile(path.join(root,'requirements.json')),await readFile(path.join(saved,'requirements.json')));
});
test('changed bytes cannot pass the package inventory or rewrite acceptance',async()=>{
  const root=path.join(await temporary(),'package');await preserve(fixture,root);await writeFile(path.join(root,'inputs/job.json'),'{}\n');
  await assert.rejects(loadPackage(root),error=>error.diagnostic?.code==='EPX_PAYLOAD_DIGEST_MISMATCH');
});
test('RO-Crate mandatory descriptive metadata rejects absent or impossible dates and unresolved license entities',async()=>{
  for(const change of [root=>delete root.datePublished,root=>root.datePublished='2026-02-30',root=>root.datePublished='2026',root=>root.license={'@id':'#absent-license'},root=>root.name='']) {
    const root=path.join(await temporary(),'package');await preserve(fixture,root);
    const metadata=await jsonFile(path.join(root,'ro-crate-metadata.json'));change(metadata['@graph'].find(entity=>entity['@id']==='./'));
    await writeJSON(path.join(root,'ro-crate-metadata.json'),metadata);
    await assert.rejects(loadPackage(root),error=>error.diagnostic?.code==='EPX_CRATE_INVALID');
  }
  const root=path.join(await temporary(),'package');await preserve(fixture,root);
  const metadata=await jsonFile(path.join(root,'ro-crate-metadata.json'));metadata['@graph'].find(entity=>entity['@id']==='./').datePublished='2024-02-29';
  await writeJSON(path.join(root,'ro-crate-metadata.json'),metadata);assert.equal(inspectPackage(await loadPackage(root)).valid,true);
});
test('unknown unqualified CWL fields are invalid while namespaced optional metadata survives',async()=>{
  for(const qualified of [false,true]) {
    const root=path.join(await temporary(),'package');await preserve(fixture,root);
    const workflow=await jsonFile(path.join(root,'workflow.cwl.json'));
    workflow.$graph.find(entry=>entry.id==='#main')[qualified?'epx:review-note':'notAStandardCwlField']=42;
    await writeJSON(path.join(root,'workflow.cwl.json'),workflow);
    const metadata=await jsonFile(path.join(root,'ro-crate-metadata.json'));
    metadata['@graph'].find(entity=>entity['@id']==='workflow.cwl.json').sha256=sha256(await readFile(path.join(root,'workflow.cwl.json')));
    await writeJSON(path.join(root,'ro-crate-metadata.json'),metadata);
    if(qualified)assert.equal(inspectPackage(await loadPackage(root)).valid,true);
    else await assert.rejects(loadPackage(root),error=>error.diagnostic?.code==='EPX_CWL_INVALID');
  }
});
test('invalid operation binding and dimension remain distinct known violations',async()=>{
  for(const change of [required=>required.operations['main/mass'].binding='undeclared',required=>required.acceptance[0].unit='kg']) {
    const root=await modified(change);await assert.rejects(loadPackage(root),error=>error.diagnostic?.category==='invalid');
  }
});
test('required CWL input record fields and scalar types reject before provider use',async()=>{
  for(const change of [job=>delete job.length.quantity,job=>delete job.width.unit,job=>job.thickness.value='2.5']) {
    const root=path.join(await temporary(),'package');await preserve(fixture,root);
    const job=await jsonFile(path.join(root,'inputs/job.json'));change(job);await writeJSON(path.join(root,'inputs/job.json'),job);
    const metadata=await jsonFile(path.join(root,'ro-crate-metadata.json'));
    metadata['@graph'].find(entity=>entity['@id']==='inputs/job.json').sha256=sha256(await readFile(path.join(root,'inputs/job.json')));
    await writeJSON(path.join(root,'ro-crate-metadata.json'),metadata);
    await assert.rejects(loadPackage(root),error=>error.diagnostic?.code==='EPX_CWL_INPUT_INVALID'&&error.diagnostic.category==='invalid');
  }
});
test('CWL default-job checks preserve nullable/default values and nested list/map records',()=>{
  const inputs={epx_context:'File',count:{type:'int',default:3},note:'string?',entries:{type:{type:'array',items:{type:'record',name:'entry',fields:{value:'double',unit:{type:{type:'enum',name:'units',symbols:['mm','m']}},label:{type:['null','string']},enabled:{type:'boolean',default:true}}}}}};
  const job={count:null,entries:[{value:2.5,unit:'mm'}]};const before=JSON.stringify(job);
  validateDefaultJob(inputs,job);assert.equal(JSON.stringify(job),before);
  for(const record of [{value:'2.5',unit:'mm'},{value:2.5,unit:'kg'}])assert.throws(()=>validateDefaultJob(inputs,{entries:[record]}),error=>error.diagnostic?.category==='invalid');
});
test('explicit provider replacement preserves source, graph and prior authoritative requirements',async()=>{
  const work=await temporary();const pkg=await loadPackage(fixture);const before=await readFile(path.join(fixture,'requirements.json'));
  const replacement=structuredClone(pkg.requirements.bindings.engineering);replacement.application.id='urn:engineering-process-spec:mock-other-engineering';
  const withFile=path.join(work,'replacement.json');await writeJSON(withFile,replacement);
  const out=path.join(work,'revised');const result=await replaceBinding(fixture,{binding:'engineering',replacementFile:withFile,revision:'2',outDirectory:out});
  assert.equal(result.status,'valid');assert.equal(result.engineeringCalls,0);assert.equal(result.change.providerEquivalenceClaimed,false);
  assert.equal(result.change.previousResultsReusable,false);assert.deepEqual(result.change.impactedAcceptance,['volume-quantity','mass-quantity']);
  const revised=await loadPackage(out);assert.equal(revised.requirements.process.revision,'2');assert.equal(revised.requirements.bindings.engineering.application.id,replacement.application.id);
  assert.deepEqual(await readFile(path.join(out,pkg.filename)),pkg.workflowBytes);
  assert.deepEqual(await readFile(path.join(fixture,'requirements.json')),before);
  assert.deepEqual(await readFile(path.join(out,result.change.previousRequirements.path)),before);
  await assert.rejects(replaceBinding(fixture,{binding:'engineering',replacementFile:withFile,revision:'1',outDirectory:path.join(work,'stale')}),error=>error.diagnostic?.code==='EPX_REPLACEMENT_REVISION_INVALID');
});
