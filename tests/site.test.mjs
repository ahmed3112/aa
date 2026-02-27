import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync('index.html', 'utf8');
const css = readFileSync('styles.css', 'utf8');
const js = readFileSync('script.js', 'utf8');

test('homepage has Quran viewer controls and prayer section', () => {
  assert.match(html, /المصحف الشريف – 604 صفحة كاملة/);
  assert.match(html, /id="moshafPage"/);
  assert.match(html, /id="reciter"/);
  assert.match(html, /id="prayerTimes"/);
});

test('styles include global theme variables and responsive controls', () => {
  assert.match(css, /--accent:/);
  assert.match(css, /\.controls\s*\{/);
  assert.match(css, /@media \(max-width: 900px\)/);
});

test('script includes image fallback providers and state persistence', () => {
  assert.match(js, /const pageSources = \[/);
  assert.match(js, /quran\.ksu\.edu\.sa\/png_big/);
  assert.match(js, /localStorage\.setItem\('lastPage'/);
  assert.match(js, /setupPrayerTimes\(\);/);
});
