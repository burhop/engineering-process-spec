// Build-only synchronization: root schemas are the sole hand-edited authority.
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import path from 'node:path';
const source=fileURLToPath(new URL('../../../schemas/',import.meta.url));
const target=fileURLToPath(new URL('../schemas/',import.meta.url));
const files=['bindings.schema.json','requirements.schema.json','run.schema.json'];
const check=process.argv.includes('--check');
const hashes={};
for(const filename of files) {
  const canonical=await readFile(path.join(source,filename));
  hashes[filename]=createHash('sha256').update(canonical).digest('hex');
  if(check) {
    let bundled;try{bundled=await readFile(path.join(target,filename));}catch{throw new Error(`Bundled ${filename} is missing. Run npm run build.`);}
    if(!canonical.equals(bundled))throw new Error(`Bundled ${filename} differs from the authoritative root schema. Run npm run build.`);
  }else{await mkdir(target,{recursive:true});await writeFile(path.join(target,filename),canonical);}
}
const manifest={format:'epx-generated-schema-manifest',version:'0.1.0-draft.1',source:'../../../schemas',sha256:hashes};
const bytes=Buffer.from(JSON.stringify(manifest,null,2)+'\n');
if(check){if(!bytes.equals(await readFile(path.join(target,'manifest.json'))))throw new Error('Schema manifest drift; run npm run build.');}
else await writeFile(path.join(target,'manifest.json'),bytes);
console.log(`${check?'Verified':'Copied'} ${files.length} canonical schemas and generated digest manifest.`);
