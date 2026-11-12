# East Coast Construction

Static website for East Coast Construction (ECC Builders), Boca Raton. Florida CGC #CGC1525184.

This repository is **static HTML only**: push to Easypanel (Nixpacks static / nginx). There is no build step. Do not add a root `package.json`, or top-level `public/`, `dist/`, or `index/` — Nixpacks would treat the repo as a different app type.

## Local preview

Serve the repo root with any static file server, for example:

```bash
npx --yes serve -p 8765
```

Open `http://127.0.0.1:8765/`. Content changes are edits to the HTML (and shared assets) in this tree.

## Deploy

- `Staticfile` — Nixpacks serves from the repo root; missing URLs return `/404.html`.
- **Redirects** from the old eccbuilders.com paths — configure in Easypanel domain **Redirects** (`deploy/easypanel-redirects.md`). Test temporary rules before making them permanent (301s cache hard).
- **Forms** — set webhook URLs in `assets/js/config.js` (see below).

## Routes

| URL | Page |
| --- | --- |
| `/` | Home |
| `/services/` and `/services/…` | Services |
| `/work/` and `/work/…` | Projects |
| `/process/`, `/delivery-methods/`, `/about/`, `/reviews/`, `/faq/`, `/building-code/` | Info |
| `/service-area/` and city pages | South Florida |
| `/trade-partners/`, `/careers/`, `/contact/` | Lead gen |
| `/privacy/`, `/terms/` | Legal drafts |
| `/404.html` | Not found |

`sitemap.xml` and `robots.txt` list the public URLs.

## Quote, trade, and careers forms

Forms validate in the browser, use honeypot field `company_website`, and `POST` `multipart/form-data` to URLs in `assets/js/config.js`:

```js
window.ECC_CONFIG = {
  quoteEndpoint: "https://formspree.io/f/your-id",
  tradeEndpoint: "",
  careersEndpoint: ""
};
```

Leave `tradeEndpoint` / `careersEndpoint` empty to use `quoteEndpoint`. Field `form_type` is `quote`, `trade`, or `careers`. Do not commit URLs that embed secrets.

If an endpoint is empty, the form shows an error and the phone number. The endpoint must allow browser `POST` from this origin (CORS).

## Owner content still needed

Search the HTML for `placeholder-badge` to find every **Placeholder** block. Do not invent license numbers, people, or reviews.

See git history or prior README for the full checklist (legal name, GA4, South Florida project photos, counsel review of `/privacy/` and `/terms/`, etc.).

## Facts used

Copy is limited to the public eccbuilders.com audit (November 2026) and the pages in this repo. Office email on the site: `avirzi@eccbuilders.com`.
