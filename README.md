# East Coast Construction

Website for East Coast Construction (ECC Builders), Boca Raton. Florida CGC #CGC1525184. Tagline: Always Be Building.

The public pages are static HTML. Easypanel is already serving this repository with nginx, and that path still works: push the files, and `/`, `/services/`, `/work/…`, and the rest resolve because each route is a folder with `index.html`. There is no Node build and no `package.json`. Do not add a root `package.json`, or a top-level `public/`, `dist/`, or `index/` directory. Nixpacks would treat those as a different kind of app, or as the only folder to publish.

## Preview

```bash
python3 -m http.server 8765
```

Open `http://127.0.0.1:8765/`.

Page copy lives in `scripts/site_data.py` and `scripts/build_site.py`. Regenerate, then commit the HTML:

```bash
python3 scripts/build_site.py
```

The script checks that every internal link points at a real page.

## Routes

| URL | Page |
| --- | --- |
| `/` | Home |
| `/services/` and `/services/…` | Services, including owner’s representation and preconstruction |
| `/work/` and `/work/…` | Project index and one page per published project |
| `/process/` | Preconstruction through closeout |
| `/delivery-methods/` | General contract, construction management, design-build |
| `/about/` | History, leadership, license, insurance and safety slots |
| `/reviews/` | The two published letters |
| `/faq/` | FAQ |
| `/building-code/` | Florida Building Code and coastal construction |
| `/service-area/` and four city pages | West Palm Beach through greater Miami |
| `/trade-partners/` | Bid-list signup |
| `/careers/` | No open roles are published |
| `/contact/` | Quote form, phone, email, map |
| `/privacy/`, `/terms/` | Drafts for the owner and for counsel |
| `/404.html` | Not-found page |

`sitemap.xml` and `robots.txt` list the same pages. Every page has its own title, description, canonical URL, Open Graph tags, and JSON-LD (`GeneralContractor` + `LocalBusiness`, plus breadcrumbs and an FAQ graph on `/faq/`).

Northeast projects are labeled heritage. They are prior track record, not Florida work. The only published Florida project is Lake Rodgers Waterfront Estate in Boca Raton.

## Quote, trade, and careers forms

The three forms validate in the browser, ignore a hidden honeypot field named `company_website`, and `POST` `multipart/form-data` to an endpoint you configure. Nothing in git is a secret. A field named `form_type` is `quote`, `trade`, or `careers`.

If the endpoint is empty, the form does not pretend to send. It shows an error and the phone number. A filled honeypot is treated as success and is not posted. Files on the quote form are optional, limited to 3, and limited to PDF, JPEG, JPG, or PNG at 10 MB each. That size cap is only a limit of this form.

The endpoint has to accept a browser `POST` from this site (CORS: `Access-Control-Allow-Origin` for the site origin, and an `OPTIONS` response if the browser preflights). Formspree, Getform, Basin, an n8n webhook, or a Make.com webhook are all enough. Point it at a URL that does not embed a secret, or use the environment-variable path below so the URL never lands in git.

### Static / Nixpacks deploy (what is live now)

Edit `assets/js/config.js`:

```js
window.ECC_CONFIG = {
  quoteEndpoint: "https://formspree.io/f/your-id",
  tradeEndpoint: "",
  careersEndpoint: ""
};
```

Leave `tradeEndpoint` and `careersEndpoint` empty to send those forms to `quoteEndpoint` as well. `form_type` tells them apart. Do not commit a URL that contains a token. If the URL is a secret, use the Docker path instead and keep these strings empty.

### Dockerfile deploy (env vars, no secrets in git)

`Dockerfile` serves the same files with nginx 1.24, writes the config from the environment on startup, and 301-redirects the old eccbuilders.com paths. Easypanel uses a Dockerfile automatically only when the service has no saved builder. If this service is already saved as Nixpacks, leave that builder alone and the HTML still deploys. Switch the builder to Dockerfile only when you want the redirects and the env injection.

Set these service environment variables:

| Variable | Required | Purpose |
| --- | --- | --- |
| `QUOTE_FORM_ENDPOINT` | Yes, for delivery | URL for quote, trade, and careers posts |
| `TRADE_FORM_ENDPOINT` | No | Overrides the trade form only |
| `CAREERS_FORM_ENDPOINT` | No | Overrides the careers form only |
| `PORT` | No | Listen port. Defaults to 80. Match the Easypanel domain’s target port. |

The container listens on `PORT`. The domain in Easypanel must target that same port.

## Redirects from the old site

These permanent redirects match the paths on the audited eccbuilders.com site:

| Old path | New path |
| --- | --- |
| `/about-us` | `/about/` |
| `/luxury-residences` | `/services/luxury-residences/` |
| `/commercial` | `/services/commercial/` |
| `/tenant-improvements` | `/services/tenant-improvements/` |
| `/luxury-renovations` | `/services/luxury-renovations/` |
| `/houses-of-worship` | `/services/houses-of-worship/` |
| `/testimonials` | `/reviews/` |
| `/contact-us` | `/contact/` |

They are in `nginx.conf` for the Dockerfile. On the current Nixpacks/static host, nginx will not read that file. Add the same rules in the Easypanel domain’s Redirects panel (they run at the proxy, before the app). Copy-paste patterns are in `deploy/easypanel-redirects.md`. Test a rule as temporary before marking it permanent, because browsers cache a 301.

`Staticfile` tells Nixpacks to use `/404.html` for missing URLs when that provider is the one running nginx.

## Owner content still needed

Anything the public site did not say is marked **Placeholder** on the page. Do not fill those with guessed numbers, people, or reviews. Search the HTML for `placeholder-badge` to find every one.

- Legal name for the footer and contracts. The public record uses East Coast Construction, East Coast Construction Group, and East Coast Construction Group, Inc.
- Confirm the Boca Raton office, the Great River, New York office (no street was published), the service area from West Palm Beach to greater Miami, and license #CGC1525184.
- Office hours, and any reply-time the office actually keeps.
- Who receives form submissions, which vendor stores them, and how long messages and files are kept.
- Whether Google Analytics 4 (`G-4SNM9CYPCP` on the old site) should come back. It is not installed. If it returns, the privacy draft and a cookie notice have to say so.
- Counsel’s review of `/privacy/` and `/terms/` before they are treated as adopted. A governing-law sentence was deliberately left out.
- More South Florida projects: name, city, type, size, schedule, delivery method, and photographs with permission. Lake Rodgers is the only Florida project on file. Its completion date, price, architect, permit office, and wind-design facts are not published.
- Per-project gaps already marked on each case study (schedule, role, size, photos).
- The Extended Stay photograph is not labeled Philadelphia or Edison. Do not caption it as one of them until someone who knows the job does.
- Confirm published spellings and place names: “Bleeker,” “517 West 46 Street,” “Gaggeneau,” Huntington versus Melville, and whether “$30 million or less” still describes the work.
- Anthony Virzi’s title, and whether he should appear on About. A portrait of Thomas Virzi. Anyone else who should be listed. No title was published for Anthony.
- Whether owner’s representation is still offered, and the fee or process in the firm’s words.
- Whether design-build is offered. It is not named on the public site.
- Preconstruction deliverables, who files the permit, the update cadence, and the closeout checklist (punch list, warranties, as-builts).
- Insurance limits, bonding, a safety program or EMR, OSHA or LEED credentials, any other licenses, and any award after BuildZoom 2021.
- Newer testimonials, and permission before quoting Google, Houzz, or BuildZoom.
- Insurance minimums before a trade partner is invited to bid.
- Real job openings, if any. The careers page lists none.
- A vector logo and any newer photo library.

## Facts used

Copy is limited to the public eccbuilders.com audit of 12 November 2026 and the pages already in this repo. The office email `avirzi@eccbuilders.com` is the address already published on this site. The map pin is the geocoded street address, not a claim about other tenants in the building.
