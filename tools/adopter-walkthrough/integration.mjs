// This consuming application's only project import is the installed public package.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {loadPackage,inspectPackage,preflight,runPackage} from 'epx-node-adopter';
const callCount=async()=>((await readFile('/consumer/provider-audit.jsonl','utf8')).trim().split('\n').filter(Boolean).map(JSON.parse).filter(event=>event.method==='tools/call').length);
assert.equal(process.env.EPX_SCHEMA_ROOT,undefined);
const processDefinition=await loadPackage('/consumer/package');
assert.equal(inspectPackage(processDefinition).engineeringCalls,0);
const beforePreflight=await callCount();
const readiness=await preflight(processDefinition,'/consumer/local-bindings.json');
assert.equal(readiness.status,'available');
assert.equal(readiness.engineeringCalls,0);
assert.equal(await callCount(),beforePreflight);
const report=await runPackage(processDefinition,'/consumer/local-bindings.json','/consumer/run-node-api','streamflow');
assert.equal(report.execution.status,'succeeded');
assert.equal(report.acceptance.status,'pass');
assert.equal(report.calls.length,2);
assert.equal(report.approval,'not-requested');
console.log(JSON.stringify({scope:'installed public API',status:'passed',engine:'streamflow',calls:2}));
