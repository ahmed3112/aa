import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync('index.html', 'utf8');
const css = readFileSync('styles.css', 'utf8');
const js = readFileSync('script.js', 'utf8');

test('homepage contains Cisco backup workflow sections', () => {
  assert.match(html, /Cisco Switch Backup Tool/);
  assert.match(html, /id="backupForm"/);
  assert.match(html, /id="payloadPreview"/);
  assert.match(html, /id="historyRows"/);
});

test('styles include modern card layout and responsive rule', () => {
  assert.match(css, /\.layout/);
  assert.match(css, /\.card\.wide/);
  assert.match(css, /@media \(max-width: 900px\)/);
});

test('script includes storage and config download behavior', () => {
  assert.match(js, /const storageKey = 'ciscoBackupHistory'/);
  assert.match(js, /function downloadConfig\(entry\)/);
  assert.match(js, /localStorage\.setItem\(storageKey/);
});
