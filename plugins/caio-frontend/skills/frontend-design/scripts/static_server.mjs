import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';

const MIME = {
  '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8', '.js': 'text/javascript',
  '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp',
  '.avif': 'image/avif', '.ico': 'image/x-icon', '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf',
  '.otf': 'font/otf', '.mp4': 'video/mp4', '.webm': 'video/webm', '.txt': 'text/plain; charset=utf-8',
  '.wasm': 'application/wasm', '.map': 'application/json',
};

export function serveDirectory(dir) {
  const root = fs.realpathSync(dir);
  if (!fs.statSync(root).isDirectory()) throw new Error(`--serve directory not found: ${dir}`);
  const insideRoot = (target) => target === root || target.startsWith(root + path.sep);
  const server = http.createServer((req, res) => {
    let pathname;
    try {
      pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    } catch {
      res.writeHead(400).end();
      return;
    }
    const lexical = path.resolve(root, `.${pathname}`);
    if (!insideRoot(lexical)) {
      res.writeHead(403).end();
      return;
    }
    let file = lexical;
    try {
      if (fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    } catch {
      if (!path.extname(pathname)) file = path.join(root, 'index.html');
    }
    try {
      file = fs.realpathSync(file);
    } catch {
      res.writeHead(404).end('Not found');
      return;
    }
    if (!insideRoot(file) || !fs.statSync(file).isFile()) {
      res.writeHead(403).end();
      return;
    }
    res.writeHead(200, { 'content-type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => resolve({ server, origin: `http://127.0.0.1:${server.address().port}` }));
  });
}
