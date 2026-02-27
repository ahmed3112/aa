# Quran Kareem - 604 Page Viewer

A modern Arabic web experience for reading the full Mushaf (604 pages), listening to recitations, and viewing prayer times.

## Features

- Full page navigation with saved progress in `localStorage`.
- Multi-source image fallback to reduce page-load failures.
- Reciter selection + quick surah audio playback.
- Prayer times from Aladhan API using geolocation.
- Responsive design with optional light/dark theme.

## Run locally

```bash
python3 -m http.server 4173
```

Then open `http://localhost:4173`.

## Tests

```bash
node -c script.js
npm test
```
