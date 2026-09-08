import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,readFile} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {evaluateAcceptance} from '../cli.mjs';
import {sha256,writeJSON,strictJSON} from '../base.mjs';

async function evidence(quantity,unit,target) {
  const runDirectory=await mkdtemp(path.join(os.tmpdir(),'epx-node-quantity-'));
  const result={structuredContent:{quantity,unit,value:1e308}};
  await writeJSON(path.join(runDirectory,'result.json'),result);
  const artifact={path:'result.json',sha256:sha256(await readFile(path.join(runDirectory,'result.json')))};
  const criterion={id:'finite-measurement',node:'main/test',quantity,unit:target,valuePointer:'/structuredContent/value',quantityPointer:'/structuredContent/quantity',unitPointer:'/structuredContent/unit',expected:1e308,absoluteTolerance:0};
  const pkg={metadataSha256:'unit-test-package',requirements:{acceptance:[criterion],operations:{'main/test':{binding:'engineering'}}}};
  const call={node:'main/test',binding:'engineering',status:'succeeded',runId:'unit-test-run',packageMetadataSha256:pkg.metadataSha256,artifact,result};
  return evaluateAcceptance(pkg,[call],runDirectory);
}

test('finite same-unit density avoids unnecessary intermediate overflow',async()=>{
  const acceptance=await evidence('density','g/cm3','g/cm3');
  assert.equal(acceptance.status,'pass');
  assert.equal(acceptance.criteria[0].compared.value,1e308);
});
test('unrepresentable unit conversion is indeterminate with finite JSON evidence',async()=>{
  const acceptance=await evidence('mass','kg','g');
  assert.equal(acceptance.status,'indeterminate');
  assert.equal(acceptance.criteria[0].status,'indeterminate');
  assert.equal(acceptance.criteria[0].compared,undefined);
  assert.equal(strictJSON(JSON.stringify(acceptance)).status,'indeterminate');
});
