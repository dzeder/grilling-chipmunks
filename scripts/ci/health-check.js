#!/usr/bin/env node
/**
 * Health check script for Ohanafy AI Ops.
 * Verifies all required files, configs, and services are accessible.
 *
 * Usage: node ci-cd/scripts/health-check.js
 */

const fs = require('fs');
const path = require('path');

const checks = [];

function check(name, fn) {
  try {
    const result = fn();
    checks.push({ name, status: 'PASS', detail: result });
    console.log(`  ✓ ${name}`);
  } catch (e) {
    checks.push({ name, status: 'FAIL', detail: e.message });
    console.log(`  ✗ ${name}: ${e.message}`);
  }
}

console.log('Ohanafy AI Ops — Health Check\n');

// File existence checks
check('CLAUDE.md exists', () => {
  if (!fs.existsSync('CLAUDE.md')) throw new Error('Missing CLAUDE.md');
  return 'OK';
});

check('requirements.txt exists', () => {
  if (!fs.existsSync('requirements.txt')) throw new Error('Missing requirements.txt');
  return 'OK';
});

check('watchers/repos.yaml exists', () => {
  if (!fs.existsSync('watchers/repos.yaml')) throw new Error('Missing watchers/repos.yaml');
  return 'OK';
});

check('registry/content-sources.yaml exists', () => {
  if (!fs.existsSync('registry/content-sources.yaml')) throw new Error('Missing registry/content-sources.yaml');
  return 'OK';
});

check('All CI/CD pipelines exist', () => {
  const required = ['main.yml', 'pr.yml', 'staging.yml', 'sf-deploy.yml', 'aws-deploy.yml', 'watchers.yml', 'content-watcher.yml'];
  const missing = required.filter(f => !fs.existsSync(path.join('ci-cd/pipelines', f)));
  if (missing.length) throw new Error(`Missing: ${missing.join(', ')}`);
  return `${required.length} pipelines OK`;
});

// Summary
const passed = checks.filter(c => c.status === 'PASS').length;
const failed = checks.filter(c => c.status === 'FAIL').length;
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
