/** Reproduce the existing pipeline first; only verified generated extras are removed. */
import fs from 'node:fs';import path from 'node:path';import {fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';import {spawnSync} from 'node:child_process';
const root=path.dirname(fileURLToPath(import.meta.url)),output=path.join(root,'.public-release');
const review=JSON.parse(fs.readFileSync(path.join(root,'kakao-map-review.json'),'utf8'));
for(const [name,hash] of Object.entries(review.assets)){
 const dest=path.resolve(output,name);if(!dest.startsWith(output+path.sep)||!/^assets\/kakao-(?:directions|frame|maps|traffic|options)[./]/.test(name))throw Error('Unsafe generated map path');
 if(fs.existsSync(dest)){const bytes=fs.readFileSync(dest),raw=createHash('sha256').update(bytes).digest('hex'),lf=createHash('sha256').update(bytes.toString('utf8').replaceAll('\r\n','\n')).digest('hex');if(raw!==hash&&lf!==hash)throw Error('Generated map resource changed '+name);fs.unlinkSync(dest);}
}
for(const step of ['favicon-build.mjs','kakao-map-build.mjs']){const r=spawnSync(process.execPath,[step],{cwd:root,stdio:'inherit'});if(r.error)throw r.error;if(r.status!==0)process.exit(r.status??1);}
