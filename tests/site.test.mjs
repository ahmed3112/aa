import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync('index.html', 'utf8');
const css = readFileSync('styles.css', 'utf8');
const js = readFileSync('script.js', 'utf8');

test('homepage has quran page viewer and text reading section', () => {
  assert.match(html, /المصحف الشريف – 604 صفحة كاملة/);
  assert.match(html, /id="moshafPage"/);
  assert.match(html, /id="textSurah"/);
  assert.match(html, /id="quranTextContainer"/);
});

test('styles include controls, text panel and responsive rules', () => {
  assert.match(css, /--accent:/);
  assert.match(css, /\.controls/);
  assert.match(css, /\.quran-text/);
  assert.match(css, /@media \(max-width: 900px\)/);
});

test('script includes image fallbacks and text quran setup', () => {
  assert.match(js, /const pageSources = \[/);
  assert.match(js, /quran\.ksu\.edu\.sa\/png_big/);
  assert.match(js, /function setupTextQuran\(\)/);
  assert.match(js, /localStorage\.setItem\('lastTextSurah'/);
});
