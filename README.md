# Quran Kareem Ramadan Website

This is a lightweight static website for Ramadan Kareem with Quran reflection and checklist features.

## GitHub Testing

Automated tests run on every push and pull request using **GitHub Actions**.

Workflow file: `.github/workflows/test.yml`

It runs:
1. `node -c script.js` for JavaScript syntax validation.
2. `npm test` for repository checks in `tests/site.test.mjs`.
