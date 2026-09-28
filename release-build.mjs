/** Keep the full reviewed pipeline behind Vercel's short build-command entrypoint. */
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

const root = path.dirname(fileURLToPath(import.meta.url));
const steps = [
  ['release-public-build.mjs'],
  ['seo-content-improvements.mjs', '--root=.public-release'],
  ['seo-course-improvements.mjs', '--root=.public-release'],
  ['seo-math-improvements.mjs', '--root=.public-release'],
  ['wawa-analytics-build.mjs', 'wawa-13', '.public-release'],
  ['seo-descriptions.mjs', '--root=.public-release'],
];

for (const args of steps) {
  const result = spawnSync(process.execPath, args, {cwd: root, stdio: 'inherit'});
  if (result.error) {
    console.error(result.error.message);
    process.exit(1);
  }
  if (result.status !== 0) process.exit(result.status ?? 1);
}
