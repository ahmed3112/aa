import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync('index.html', 'utf8');
const css = readFileSync('styles.css', 'utf8');
const js = readFileSync('script.js', 'utf8');

test('homepage has fleet booking form and bookings table', () => {
  assert.match(html, /FleetFlow/);
  assert.match(html, /id="bookingForm"/);
  assert.match(html, /id="tripType"/);
  assert.match(html, /id="bookingRows"/);
});

test('styles include core layout and responsive rules', () => {
  assert.match(css, /--primary:/);
  assert.match(css, /\.layout/);
  assert.match(css, /\.email-btn/);
  assert.match(css, /@media \(max-width: 700px\)/);
});

test('script includes driver catalog, storage key and email composition', () => {
  assert.match(js, /const STORAGE_KEY = 'fleetflow_bookings_v1'/);
  assert.match(js, /const drivers = \[/);
  assert.match(js, /function createEmailLink\(booking, driver\)/);
  assert.match(js, /mailto:/);
});
