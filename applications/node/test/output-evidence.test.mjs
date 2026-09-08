import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {sha256,writeJSON} from '../base.mjs';
import {verifyEngineOutputs} from '../cli.mjs';
test('engine exit or successful calls cannot substitute for real matching workflow outputs',async()=>{
  const root=await mkdtemp(path.join(os.tmpdir(),'epx-node-output-'));const outputs=path.join(root,'engine-output');await mkdir(outputs);
  const bytes=Buffer.from('{"structuredContent":{"value":0.157}}\n');const filename=path.join(outputs,'result.json');await writeFile(filename,bytes);
  const pkg={main:{outputs:{mass:{type:'File',outputSource:'mass/result'}}}};
  const calls=[{node:'main/mass',status:'succeeded',artifact:{sha256:sha256(bytes)}}];
  await writeJSON(path.join(root,'engine.stdout.json'),{mass:{class:'File',location:pathToFileURL(filename).href}});
  assert.equal((await verifyEngineOutputs(pkg,calls,root))[0].sha256,sha256(bytes));
  await writeFile(filename,'{"unrelated":true}\n');await assert.rejects(verifyEngineOutputs(pkg,calls,root),/differs/);
  await writeJSON(path.join(root,'engine.stdout.json'),{});await assert.rejects(verifyEngineOutputs(pkg,calls,root),/not an observed File/);
});
