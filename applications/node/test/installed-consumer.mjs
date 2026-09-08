// Copy this file into the fresh consuming project before executing it.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {loadPackage,inspectPackage,preserve,VERSION} from 'epx-node-adopter';
assert.equal(process.env.EPX_SCHEMA_ROOT,undefined,'Ordinary installed use must need no schema override.');
const resolution=import.meta.resolve('epx-node-adopter');
assert.ok(resolution.startsWith(pathToFileURL(path.join(process.cwd(),'node_modules')).href),'API must resolve inside the fresh consumer installation.');
const schemaManifest=JSON.parse(await readFile(new URL('./schemas/manifest.json',resolution)));
for(const [filename,expected] of Object.entries(schemaManifest.sha256))assert.equal(createHash('sha256').update(await readFile(new URL('./schemas/'+filename,resolution))).digest('hex'),expected);
const pkg=await loadPackage('received');const inspected=inspectPackage(pkg);
assert.equal(inspected.valid,true);assert.equal(inspected.steps.length,2);assert.equal(inspected.engineeringCalls,0);
await preserve('received','saved');const saved=await loadPackage('saved');assert.equal(saved.metadataSha256,pkg.metadataSha256);
const report={format:'epx-installed-consumer-evidence',version:VERSION,node:process.version,api:'epx-node-adopter',resolvedInsideConsumer:true,schemaOverride:false,bundledSchemas:Object.keys(schemaManifest.sha256),receivedPackageMetadataSha256:pkg.metadataSha256,steps:inspected.steps.map(step=>step.node),preservedMetadataSha256:saved.metadataSha256,engineeringCalls:0,status:'pass'};
await writeFile('installed-consumer-report.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
