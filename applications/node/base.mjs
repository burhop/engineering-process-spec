import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import Ajv2020 from 'ajv/dist/2020.js';

export const VERSION = '0.1.0-draft.1';
export const PROFILE = `urn:engineering-process-spec:core:${VERSION}`;
export const IMPLEMENTATION = 'epx-node';
export const SCHEMA_ROOT = process.env.EPX_SCHEMA_ROOT ?? fileURLToPath(new URL('./schemas/', import.meta.url));
export const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
export const own = (object, key) => Object.hasOwn(object, key);
export const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);

export class Failure extends Error {
  constructor(code, category, requirement, message, fields={}) {
    super(message);
    this.diagnostic = {code, category, requirement, message, ...fields};
  }
}
export const fail = (code, category, requirement, message, fields) => { throw new Failure(code, category, requirement, message, fields); };
export const diagnostic = error => error instanceof Failure ? error.diagnostic : {code:'EPX_INTERNAL',category:'execution-failed',requirement:'DIAG-001',message:error.message};

// Independent strict JSON parser: JSON.parse alone silently accepts duplicate keys.
export function strictJSON(bytes) {
  const text = typeof bytes === 'string' ? bytes : new TextDecoder('utf-8', {fatal:true}).decode(bytes);
  let i=0;
  const error = () => fail('EPX_JSON_INVALID','invalid','PKG-001',`Invalid finite JSON or duplicate object key at offset ${i}.`);
  const white = () => { while (/[ \t\r\n]/.test(text[i] ?? '') && i < text.length) i++; };
  const string = () => {
    const start=i++;
    while (i<text.length) {
      if(text[i]==='\\') {i+=2;continue;}
      if(text[i++]==='"') {try{return JSON.parse(text.slice(start,i));}catch{error();}}
    }
    error();
  };
  const parse = (depth=0) => {
    if(depth>150) error();
    white();
    if(text[i]==='"') return string();
    if(text[i]==='{') {
      i++;white();const result=Object.create(null);
      if(text[i]==='}') {i++;return result;}
      for(;;) {
        white();if(text[i]!=='"') error();const key=string();
        if(own(result,key)) error();white();if(text[i++]!==':') error();
        result[key]=parse(depth+1);white();const separator=text[i++];
        if(separator==='}')return result;if(separator!==',')error();
      }
    }
    if(text[i]==='[') {
      i++;white();const result=[];if(text[i]===']'){i++;return result;}
      for(;;){result.push(parse(depth+1));white();const separator=text[i++];if(separator===']')return result;if(separator!==',')error();}
    }
    for(const [literal,value] of [['true',true],['false',false],['null',null]]) {
      if(text.slice(i,i+literal.length)===literal){i+=literal.length;return value;}
    }
    const match=text.slice(i).match(/^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/);
    if(!match)error();i+=match[0].length;const result=Number(match[0]);if(!Number.isFinite(result))error();return result;
  };
  const result=parse();white();if(i!==text.length)error();return result;
}

export function parseCWL(bytes) {
  return strictJSON(bytes);
}
export const jsonFile = async filename => strictJSON(await readFile(filename));
export const writeJSON = async (filename,value) => {await mkdir(path.dirname(filename),{recursive:true});await writeFile(filename,JSON.stringify(value,null,2)+'\n');};
export function deepEqual(a,b) {
  if(typeof a!==typeof b || a===null || b===null)return a===b;
  if(Array.isArray(a)||Array.isArray(b))return Array.isArray(a)&&Array.isArray(b)&&a.length===b.length&&a.every((x,i)=>deepEqual(x,b[i]));
  if(typeof a==='object')return Object.keys(a).length===Object.keys(b).length&&Object.keys(a).every(k=>own(b,k)&&deepEqual(a[k],b[k]));
  return a===b;
}
export async function schemaCheck(value,filename,requirement='PKG-003') {
  const schema=await jsonFile(path.join(SCHEMA_ROOT,filename));
  validateSchema(value,schema,requirement);
}
export function validateSchema(value,schema,requirement='BIND-004') {
  const ajv=new Ajv2020({strict:false,allErrors:true,validateFormats:false});
  let validate;
  try{validate=ajv.compile(schema);}catch(error){fail('EPX_SCHEMA_UNSUPPORTED','unsupported',requirement,'Cannot interpret declared JSON schema.',{cause:error.message});}
  if(!validate(value))fail('EPX_SCHEMA_INVALID','invalid',requirement,'Value violates its JSON Schema.',{cause:validate.errors});
}
export function portablePath(relative) {
  if(typeof relative!=='string'||!relative||relative.includes('\\')||relative.includes('\0')||relative.startsWith('/')||relative.includes(':')||relative.split('/').some(v=>v==='..'||v===''||v==='.')||relative.includes('#'))
    fail('EPX_PATH_INVALID','invalid','PKG-001','Payload paths must remain relative to their package.',{dependency:relative});
  return relative;
}
export function pointer(value,p) {
  if(p==='')return value;
  if(typeof p!=='string'||!p.startsWith('/'))throw new Error('Invalid JSON Pointer');
  for(const token of p.slice(1).split('/')) {
    const key=token.replaceAll('~1','/').replaceAll('~0','~');
    if(value===null||typeof value!=='object'||!own(value,key))throw new Error('JSON Pointer does not resolve');
    value=value[key];
  }
  return value;
}
