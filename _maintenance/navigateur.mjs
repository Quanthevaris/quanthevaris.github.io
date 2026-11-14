/* Navigateur des outils de maintenance : Linux, ou CHROME_EXECUTABLE explicite. */
import { chromium } from 'playwright-core';
import binary from '@sparticuz/chromium';
import { existsSync, createReadStream, mkdirSync } from 'node:fs';
import { createServer } from 'node:http';
import { resolve, sep, extname } from 'node:path';
import { brotliDecompressSync } from 'node:zlib';
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';

export const root = fileURLToPath(new URL('../', import.meta.url)).replace(/\/$/, '');
export async function navigateur() {
  if (process.env.CHROME_EXECUTABLE) {
    return chromium.launch({executablePath: process.env.CHROME_EXECUTABLE, headless: true});
  }
  if (process.platform !== 'linux') throw new Error('Utiliser Linux ou définir CHROME_EXECUTABLE vers Chrome/Chromium installé.');
  // Le pack inclut les bibliothèques NSS absentes de certains conteneurs.
  const archive = fileURLToPath(new URL('./node_modules/@sparticuz/chromium/bin/al2023.tar.br', import.meta.url));
  if (!existsSync(resolve(tmpdir(), 'al2023/lib/libnspr4.so'))) {
    const destination = resolve(tmpdir(), 'al2023');
    mkdirSync(destination, {recursive: true});
    execFileSync('tar', ['-xf', '-', '-C', destination], {input: brotliDecompressSync(readFileSync(archive))});
  }
  return chromium.launch({args: binary.args, executablePath: await binary.executablePath(), headless: true,
    env: {...process.env, LD_LIBRARY_PATH: resolve(tmpdir(), 'al2023/lib') + (process.env.LD_LIBRARY_PATH ? ':' + process.env.LD_LIBRARY_PATH : '')}});
}

export async function servir() {
  const types = {'.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript',
    '.woff2': 'font/woff2', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.pdf': 'application/pdf', '.json': 'application/json'};
  const server = createServer((req, res) => {
    let file;
    try {file = resolve(root, '.' + decodeURIComponent(new URL(req.url, 'http://local').pathname));}
    catch {res.writeHead(400).end(); return;}
    if (file === root) file += '/index.html';
    if (!file.startsWith(root + sep)) {res.writeHead(403).end(); return;}
    const stream = createReadStream(file);
    stream.on('error', () => {if (!res.headersSent) res.writeHead(404);res.end();});
    stream.once('open', () => {res.setHeader('Content-Type', types[extname(file)] || 'application/octet-stream');stream.pipe(res);});
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  return {server, url: 'http://127.0.0.1:' + server.address().port};
}
