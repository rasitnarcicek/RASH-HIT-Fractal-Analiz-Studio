#!/usr/bin/env node
/**
 * RASH-HIT Fractal Studio — npm CLI entry point (`rash-hit`).
 *
 * The single install path is npm:
 *   npm install -g rash-hit-fractal-studio     (or: npm link / npm i -g .)
 *   rash-hit                                    # opens the interactive TUI menu
 *
 * Responsibilities:
 *   1. Locate a Python interpreter (env RASH_HIT_PYTHON, then python/python3).
 *   2. Verify the Python runtime dependencies; on the FIRST run they are
 *      installed automatically from requirements.txt (pip), so a fresh user
 *      only ever runs npm. Use `rash-hit --no-install` to skip this step.
 *   3. Spawn the real launcher (launcher.py) in the project root and forward
 *      its exit code — the TUI menu then lets the user pick Web Dashboard,
 *      Terminal Analysis, Diagnostics, or the Test Suite.
 *
 * Flags:
 *   --version        print package version and exit
 *   --check          environment diagnostics only (python + deps), no launch
 *   --setup          install Python dependencies and exit
 *   --no-install     skip the automatic pip bootstrap on launch
 *   --python <path>  explicit Python interpreter (same as RASH_HIT_PYTHON)
 */
'use strict';

const { spawn, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '..');
const PKG = JSON.parse(fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8'));
const REQS = path.join(ROOT, 'requirements.txt');

// Dependencies verified before launching (mirrors launcher.py diagnostics).
const DEPS = ['numpy', 'shapely', 'openpyxl', 'fitz', 'PIL', 'tinycss2', 'defusedxml', 'rich'];

const argv = process.argv.slice(2);
const FLAGS = {
  version: argv.includes('--version') || argv.includes('-v'),
  check: argv.includes('--check'),
  setup: argv.includes('--setup'),
  noInstall: argv.includes('--no-install'),
};
const explicitPython = (() => {
  const i = argv.indexOf('--python');
  if (i !== -1 && argv[i + 1]) return argv[i + 1];
  return process.env.RASH_HIT_PYTHON || null;
})();

function out(msg) { process.stdout.write(msg + '\n'); }
function err(msg) { process.stderr.write('[rash-hit] ' + msg + '\n'); }
function fail(msg) { err(msg); process.exit(1); }

/** Resolve a usable Python interpreter (Windows `py -3` / `python`, POSIX `python3`). */
function findPython() {
  if (explicitPython) return explicitPython;
  const candidates = process.platform === 'win32' ? ['py -3', 'python'] : ['python3', 'python'];
  for (const cand of candidates) {
    const [cmd, ...args] = cand.split(' ');
    const r = spawnSync(cmd, [...args, '-c', 'import sys; print(sys.version.split()[0])'], { encoding: 'utf8' });
    if (r.status === 0 && r.stdout && r.stdout.trim()) return cand;
  }
  return null;
}

function splitCmd(cmd) {
  return cmd.split(' ');
}

function checkDeps(python) {
  const [cmd, ...args] = splitCmd(python);
  const r = spawnSync(cmd, [...args, '-c', 'import ' + DEPS.join(', ')], { encoding: 'utf8' });
  return r.status === 0;
}

function installDeps(python) {
  const [cmd, ...args] = splitCmd(python);
  out('Installing Python dependencies (pip install -r requirements.txt)…');
  const r = spawnSync(cmd, [...args, '-m', 'pip', 'install', '-r', REQS], { stdio: 'inherit', cwd: ROOT });
  if (r.status !== 0) {
    fail('pip install failed. Run manually: ' + python + ' -m pip install -r requirements.txt');
  }
  out('Python dependencies ready.');
}

function runDiagnostics(python) {
  const [cmd, ...args] = splitCmd(python);
  out('\n  RASH-HIT Fractal Studio v' + PKG.version);
  out('  Python        : ' + python);
  const v = spawnSync(cmd, [...args, '--version'], { encoding: 'utf8' });
  out('  Python ver    : ' + (v.stdout || v.stderr || '').trim());
  out('  Project root  : ' + ROOT);
  out('  Dependencies  : ' + (checkDeps(python) ? 'OK' : 'MISSING (run `rash-hit --setup`)'));
  out('');
}

function launch(python) {
  const [cmd, ...args] = splitCmd(python);
  const child = spawn(cmd, [...args, 'launcher.py'], {
    cwd: ROOT,
    stdio: 'inherit',
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
  });
  child.on('exit', (code) => process.exit(code == null ? 1 : code));
}

// ---------------------------------------------------------------- main
if (FLAGS.version) {
  out(PKG.version);
  process.exit(0);
}

const python = findPython();
if (!python) {
  fail('Python not found. Install Python 3.9+ and ensure it is on PATH (or set RASH_HIT_PYTHON).');
}

if (FLAGS.check) {
  runDiagnostics(python);
  process.exit(0);
}

if (FLAGS.setup) {
  installDeps(python);
  process.exit(0);
}

// First-run bootstrap: auto-install deps unless the user opted out.
if (!FLAGS.noInstall && !checkDeps(python)) {
  out('\n  RASH-HIT Fractal Studio — first run setup\n');
  installDeps(python);
}

launch(python);
