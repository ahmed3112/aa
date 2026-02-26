import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync('index.html', 'utf8');
const css = readFileSync('styles.css', 'utf8');
const js = readFileSync('script.js', 'utf8');

test('homepage has main Ramadan and Quran sections', () => {
  assert.match(html, /Quran Kareem \| Ramadan Kareem/);
  assert.match(html, /Welcome to a Quran Kareem space for Ramadan/);
  assert.match(html, /Daily Quran Reflection/);
  assert.match(html, /Ramadan Checklist/);
});

test('styles include responsive grid and themed palette', () => {
  assert.match(css, /--accent:/);
  assert.match(css, /grid-template-columns: repeat\(auto-fit, minmax\(240px, 1fr\)\)/);
  assert.match(css, /\.hero/);
});

test('script updates page title from checklist progress', () => {
  assert.match(js, /document\.title = `Quran Kareem \(\$\{done\}\/\$\{checkboxes\.length\} done\)`/);
});
