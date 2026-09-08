// Maintainer smoke recipe; executes only the explicitly identified mock provider.
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {readFile,mkdir} from 'node:fs/promises';
import {sha256,VERSION,writeJSON} from './base.mjs';
import {loadPackage} from './package.mjs';
import {runPackage} from './cli.mjs';
const repository=fileURLToPath(new URL('../../',import.meta.url));
const work=path.resolve(process.argv[2]??path.join(repository,'.work','node-smoke'));
await mkdir(work,{recursive:true});
const launcher=path.join(repository,'tests','providers','mock_mcp_server.py');
const config={format:'epx-bindings',version:VERSION,bindings:{engineering:{implementation:{id:'urn:engineering-process-spec:mock-mcp',revision:VERSION},application:{id:'urn:engineering-process-spec:mock-engineering',version:VERSION},transport:{kind:'stdio',command:process.env.EPX_PYTHON??'python',arguments:[launcher]},trust:{kind:'launcher-sha256',path:launcher,sha256:sha256(await readFile(launcher))}}}};
const configFile=path.join(work,'bindings.json');await writeJSON(configFile,config);
const source=process.argv[3]??path.join(repository,'examples','calculation');
const report=await runPackage(await loadPackage(source),configFile,path.join(work,'run'));
console.log(JSON.stringify({execution:report.execution,acceptance:report.acceptance.status,calls:report.calls.length,diagnostics:report.diagnostics}));
if(report.execution.status!=='succeeded'||report.acceptance.status!=='pass')process.exitCode=1;
