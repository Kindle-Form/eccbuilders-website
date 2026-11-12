# Easypanel proxy redirects

Add these in the Easypanel domain **Redirects** panel (they run at the proxy, before the static app). One permanent rule per row after you have verified the target.

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

Replace the host in **Replacement** with your production domain when it is live.
