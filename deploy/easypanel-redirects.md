# Easypanel proxy redirects

The current Easypanel service is a static nginx site. Redirect rules in the Easypanel domain settings run before traffic hits the app. Add one permanent rule per row. The same map is in `nginx.conf` for the optional Dockerfile.

Test as temporary first if you want to avoid a cached mistake, then switch to permanent (301).

| Regex | Replacement |
| --- | --- |
| `^/about-us/?$` | `https://ecc-website-eccbuilders-website.umoqsr.easypanel.host/about/` |
| `^/luxury-residences/?$` | `https://ecc-website-eccbuilders-website.umoqsr.easypanel.host/services/luxury-residences/` |
| `^/commercial/?$` | `https://ecc-website-eccbuilders-website.umoqsr.easypanel.host/services/commercial/` |
| `^/tenant-improvements/?$` | `https://ecc-website-eccbuilders-website.umoqsr.easypanel.host/services/tenant-improvements/` |
| `^/luxury-renovations/?$` | `https://ecc-website-eccbuilders-website.umoqsr.easypanel.host/services/luxury-renovations/` |
| `^/houses-of-worship/?$` | `https://ecc-website-eccbuilders-website.umoqsr.easypanel.host/services/houses-of-worship/` |
| `^/testimonials/?$` | `https://ecc-website-eccbuilders-website.umoqsr.easypanel.host/reviews/` |
| `^/contact-us/?$` | `https://ecc-website-eccbuilders-website.umoqsr.easypanel.host/contact/` |
