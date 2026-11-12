#!/usr/bin/env python3
"""Generate the static East Coast Construction site.

The host serves these files as-is (Easypanel / nginx). Run this script when
copy changes, then commit the HTML it writes.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from site_data import (  # noqa: E402
    ADDRESS_LINES,
    CLIENTS,
    DEVITO_QUOTE,
    EMAIL,
    FAQS,
    GEO,
    GIAMBALVO_QUOTE,
    HOUZZ,
    INSTAGRAM,
    LASTMOD,
    LICENSE,
    LINKEDIN,
    ORIGIN,
    PHONE_DISPLAY,
    PHONE_TEL,
    PROJECTS,
    PROJECTS_BY_SLUG,
    SERVICES,
)

ROOT = Path(__file__).resolve().parents[1]
META_DESCRIPTION = (
    "A Florida-licensed commercial and residential general contractor, serving "
    "South Florida from West Palm Beach to the greater Miami area. End-to-end "
    "construction and construction management — with a practice that began in 1985."
)
FEATURED = [
    "lake-rodgers",
    "hauppauge-office-park",
    "huntington-terrace",
    "bridgeview-tower",
    "st-john-the-evangelist",
    "allstate-farmingville",
    "plaza-100",
]
NAV = [
    ("Work", "/work/", "work"),
    ("Services", "/services/", "services"),
    ("Process", "/process/", "process"),
    ("About", "/about/", "about"),
    ("Contact", "/contact/", "contact"),
]
DBPR = "https://www.myfloridalicense.com/wl11.asp"
PAGES: list[dict] = []


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def ph(text: str) -> str:
    return (
        '<p class="placeholder-note"><span class="placeholder-badge">Placeholder</span> '
        + esc(text)
        + "</p>"
    )


def paras(items: list[str]) -> str:
    return "\n".join(f"<p>{esc(item)}</p>" for item in items)


def phone_svg() -> str:
    return (
        '<svg class="w-4 h-4 text-brand" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
        '<path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1.1-.3 1.2.4 2.5.6 3.8.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.6.6 3.8.1.4 0 .8-.3 1.1L6.6 10.8z"/>'
        "</svg>"
    )


def field(label: str, control: str) -> str:
    return (
        f'<label class="block text-sm font-medium">{esc(label)}{control}</label>'
    )


def text_input(name: str, autocomplete: str, required: bool = True, input_type: str = "text") -> str:
    req = " required" if required else ""
    return (
        f'<input{req} type="{input_type}" name="{name}" autocomplete="{autocomplete}" '
        'class="mt-1 w-full h-11 px-3 bg-white border border-stone rounded-sm">'
    )


def honeypot() -> str:
    return (
        '<div class="hp-field" aria-hidden="true">'
        '<label>Company website <input type="text" name="company_website" tabindex="-1" autocomplete="off" value=""></label>'
        "</div>"
    )


def form_status() -> str:
    return (
        '<div data-form-error class="form-error" tabindex="-1" role="alert" hidden></div>'
        '<div data-form-success tabindex="-1" role="status" hidden class="mt-4 border border-stone bg-white p-5 rounded-sm">'
        '<h3 class="font-serif text-2xl tracking-tighter2">Request sent</h3>'
        '<p class="mt-2 text-sm leading-relaxed">The delivery address configured for this form accepted the submission. '
        f'If you do not hear back, call <a class="font-semibold text-brand" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> '
        f'or email <a class="font-semibold text-brand" href="mailto:{EMAIL}">{EMAIL}</a>.</p>'
        "</div>"
    )


def quote_form(intro: str) -> str:
    options = [
        ("", "Select a project type"),
        ("Luxury residence", "Luxury residence"),
        ("Luxury renovation", "Luxury renovation"),
        ("Commercial", "Commercial"),
        ("Tenant improvement", "Tenant improvement"),
        ("House of worship", "House of worship"),
        ("Owner’s representation", "Owner’s representation"),
        ("Not sure", "Not sure"),
    ]
    option_html = "\n".join(
        f'<option value="{esc(value)}"{" disabled selected" if not value else ""}>{esc(label)}</option>'
        for value, label in options
    )
    return f"""
    <form id="quote-form" data-form="quote" method="post" enctype="multipart/form-data" novalidate class="bg-paper text-ink rounded-sm p-5 sm:p-8 relative border border-stone/60">
      {honeypot()}
      <div data-form-heading>
        <h2 class="font-serif text-2xl tracking-tighter2">Request a quote</h2>
      </div>
      <p data-form-intro class="text-sm text-muted mt-1">{esc(intro)}</p>
      <div data-form-fields>
        <div class="mt-6 grid sm:grid-cols-2 gap-4">
          {field("First name", text_input("first_name", "given-name"))}
          {field("Last name", text_input("last_name", "family-name"))}
          {field("Phone", text_input("phone", "tel", input_type="tel"))}
          {field("Email", text_input("email", "email", input_type="email"))}
          <label class="block text-sm font-medium sm:col-span-2">Project type
            <select required name="project_type" class="mt-1 w-full h-11 px-3 bg-white border border-stone rounded-sm">{option_html}</select>
          </label>
          <label class="block text-sm font-medium sm:col-span-2">Details
            <textarea required name="details" rows="4" placeholder="Project type, location, square footage, specific requests." class="mt-1 w-full px-3 py-2 bg-white border border-stone rounded-sm placeholder:text-muted/70"></textarea>
          </label>
          <div class="sm:col-span-2 text-sm">
            <label class="font-medium" for="project_files">Show us your project <span class="font-normal text-muted">(optional, up to 3 files — PDF, JPEG, JPG, or PNG, 10 MB each)</span></label>
            <input id="project_files" type="file" name="project_files" accept=".pdf,.jpeg,.jpg,.png,application/pdf,image/jpeg,image/png" multiple class="mt-2 block w-full text-sm text-muted file:mr-3 file:py-2 file:px-3 file:rounded-sm file:border file:border-stone file:bg-sand file:text-ink file:font-medium">
          </div>
          <fieldset class="sm:col-span-2 text-sm">
            <legend class="font-medium">Contact me by</legend>
            <div class="mt-2 flex flex-wrap gap-5">
              <label class="inline-flex items-center gap-2"><input type="checkbox" name="contact_by" value="Phone" class="accent-brand"> Phone</label>
              <label class="inline-flex items-center gap-2"><input type="checkbox" name="contact_by" value="Email" class="accent-brand"> Email</label>
            </div>
          </fieldset>
        </div>
        <button type="submit" class="mt-6 inline-flex items-center justify-center bg-brand hover:bg-brand-dark text-white font-semibold px-6 h-12 rounded-sm w-full sm:w-auto">Request a quote</button>
        <p class="mt-3 text-xs text-muted leading-relaxed">Sending this form shares the details with the address configured for the site, so the office can respond. Read the <a class="font-semibold text-brand" href="/privacy/">draft privacy policy</a>.</p>
      </div>
      {form_status()}
    </form>
    """


def trade_form() -> str:
    yn = (
        '<option value="" disabled selected>Select</option>'
        '<option>Yes</option><option>No</option><option>I will explain in the notes</option>'
    )
    return f"""
    <form id="trade-form" data-form="trade" method="post" enctype="multipart/form-data" novalidate class="bg-white border border-stone/70 rounded-sm p-5 sm:p-8 relative">
      {honeypot()}
      <div data-form-heading>
        <h2 class="font-serif text-2xl tracking-tighter2">Join the bid list</h2>
      </div>
      <p data-form-intro class="text-sm text-muted mt-1">The form sends your company information to the configured address. East Coast Construction has not published insurance minimums, and a submission is not a promise of work.</p>
      <div data-form-fields>
        <div class="mt-6 grid sm:grid-cols-2 gap-4">
          {field("Company", text_input("company", "organization"))}
          {field("Your name", text_input("contact_name", "name"))}
          {field("Email", text_input("email", "email", input_type="email"))}
          {field("Phone", text_input("phone", "tel", input_type="tel"))}
          {field("Trade", text_input("trade", "organization-title"))}
          <label class="block text-sm font-medium">Florida license number <span class="font-normal text-muted">(if you have one)</span>
            <input name="license_number" autocomplete="off" class="mt-1 w-full h-11 px-3 bg-paper border border-stone rounded-sm">
          </label>
          <label class="block text-sm font-medium">General liability in force
            <select required name="general_liability" class="mt-1 w-full h-11 px-3 bg-paper border border-stone rounded-sm">{yn}</select>
          </label>
          <label class="block text-sm font-medium">Workers’ compensation in force
            <select required name="workers_comp" class="mt-1 w-full h-11 px-3 bg-paper border border-stone rounded-sm">{yn}</select>
          </label>
          <label class="block text-sm font-medium sm:col-span-2">Notes
            <textarea name="notes" rows="4" placeholder="Coverage limits, the counties you work, or anything the office should know." class="mt-1 w-full px-3 py-2 bg-paper border border-stone rounded-sm"></textarea>
          </label>
        </div>
        <button type="submit" class="mt-6 inline-flex items-center justify-center bg-brand hover:bg-brand-dark text-white font-semibold px-6 h-12 rounded-sm w-full sm:w-auto">Submit company information</button>
        <p class="mt-3 text-xs text-muted leading-relaxed">Read the <a class="font-semibold text-brand" href="/privacy/">draft privacy policy</a> and the <a class="font-semibold text-brand" href="/terms/">draft terms</a>.</p>
      </div>
      {form_status()}
    </form>
    """


def careers_form() -> str:
    return f"""
    <form id="careers-form" data-form="careers" method="post" enctype="multipart/form-data" novalidate class="bg-white border border-stone/70 rounded-sm p-5 sm:p-8 relative">
      {honeypot()}
      <div data-form-heading>
        <h2 class="font-serif text-2xl tracking-tighter2">Send your interest</h2>
      </div>
      <p data-form-intro class="text-sm text-muted mt-1">No open role is published. This form only tells the office you would like to be considered when one is.</p>
      <div data-form-fields>
        <div class="mt-6 grid sm:grid-cols-2 gap-4">
          {field("Name", text_input("name", "name"))}
          {field("Email", text_input("email", "email", input_type="email"))}
          {field("Phone", text_input("phone", "tel", input_type="tel"))}
          {field("Trade or role", text_input("role", "organization-title"))}
          <label class="block text-sm font-medium sm:col-span-2">Note
            <textarea required name="note" rows="4" placeholder="Where you work now, and the kind of work you want." class="mt-1 w-full px-3 py-2 bg-paper border border-stone rounded-sm"></textarea>
          </label>
        </div>
        <button type="submit" class="mt-6 inline-flex items-center justify-center bg-brand hover:bg-brand-dark text-white font-semibold px-6 h-12 rounded-sm">Send</button>
        <p class="mt-3 text-xs text-muted">Read the <a class="font-semibold text-brand" href="/privacy/">draft privacy policy</a>.</p>
      </div>
      {form_status()}
    </form>
    """


def project_card(project: dict) -> str:
    href = f"/work/{project['slug']}/"
    size = project["size"] or "Size not published"
    if project.get("card_image"):
        media = f"""
        <div class="relative aspect-[4/3] overflow-hidden rounded-sm bg-sand">
          <img src="{esc(project['card_image'])}" alt="{esc(project['card_alt'])}" class="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-500">
          <div class="absolute top-3 left-3"><span class="bg-white/95 text-ink text-[11px] font-semibold uppercase tracking-wider px-2 py-1 rounded-sm">{esc(project['region_label'])}</span></div>
        </div>"""
    else:
        media = f"""
        <div class="relative aspect-[4/3] overflow-hidden rounded-sm bg-ink text-paper flex items-end p-4">
          <p class="text-sm pr-16">{esc(project.get("card_fallback") or "Photograph not published.")}</p>
          <div class="absolute top-3 left-3"><span class="bg-white/95 text-ink text-[11px] font-semibold uppercase tracking-wider px-2 py-1 rounded-sm">{esc(project['region_label'])}</span></div>
        </div>"""
    return f"""
    <article class="group" data-project-card data-region="{esc(project['region'])}" data-type="{esc(project['type_slug'])}">
      <a href="{href}" class="block rounded-sm">
        {media}
        <div class="pt-3">
          <p class="text-[11px] uppercase tracking-wider text-muted">{esc(project['type_label'])} · {esc(size)}</p>
          <h3 class="font-serif text-xl mt-0.5 group-hover:text-brand">{esc(project['name'])}</h3>
          <p class="text-sm text-muted">{esc(project['place'])}</p>
        </div>
      </a>
    </article>"""


def filter_buttons(group: str, items: list[tuple[str, str]]) -> str:
    buttons = []
    for index, (value, label) in enumerate(items):
        pressed = "true" if index == 0 else "false"
        buttons.append(
            f'<button type="button" data-filter-group="{group}" data-filter="{esc(value)}" aria-pressed="{pressed}" '
            f'class="filter-btn px-3 h-9 text-sm font-medium rounded-sm border border-stone bg-transparent hover:border-ink">{esc(label)}</button>'
        )
    return "\n".join(buttons)


def business_node() -> dict:
    return {
        "@type": ["GeneralContractor", "LocalBusiness"],
        "@id": ORIGIN + "/#business",
        "name": "East Coast Construction",
        "alternateName": "East Coast Construction Group",
        "slogan": "Always Be Building",
        "url": ORIGIN + "/",
        "image": ORIGIN + "/assets/images/residence-2.jpg",
        "logo": ORIGIN + "/assets/images/logo.png",
        "telephone": "+1-561-245-5044",
        "email": EMAIL,
        "foundingDate": "1985",
        "founder": {"@type": "Person", "name": "Thomas Virzi", "jobTitle": "President"},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "7700 Congress Avenue, Suite 1139",
            "addressLocality": "Boca Raton",
            "addressRegion": "FL",
            "postalCode": "33487",
            "addressCountry": "US",
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": GEO["lat"],
            "longitude": GEO["lon"],
        },
        "areaServed": [
            {"@type": "City", "name": "West Palm Beach"},
            {"@type": "City", "name": "Boca Raton"},
            {"@type": "AdministrativeArea", "name": "Greater Miami area"},
        ],
        "identifier": {
            "@type": "PropertyValue",
            "propertyID": "Florida Certified General Contractor",
            "value": LICENSE,
        },
        "sameAs": [INSTAGRAM, HOUZZ],
        "description": META_DESCRIPTION,
    }


def json_ld(nodes: list[dict]) -> str:
    payload = {"@context": "https://schema.org", "@graph": nodes}
    raw = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    return f'<script type="application/ld+json">{raw}</script>'


def header(nav_key: str) -> str:
    links = []
    mobile = []
    for label, href, key in NAV:
        current = ' aria-current="page"' if key == nav_key else ""
        links.append(
            f'<a href="{href}" data-nav="{key}" class="hover:text-brand"{current}>{esc(label)}</a>'
        )
        mobile.append(
            f'<a href="{href}" data-nav="{key}" class="py-2 border-b border-sand"{current}>{esc(label)}</a>'
        )
    mobile.append(
        f'<a href="tel:{PHONE_TEL}" class="mt-3 py-2 font-semibold">{PHONE_DISPLAY}</a>'
    )
    return f"""
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="sticky top-0 z-40 bg-paper/95 backdrop-blur border-b border-stone/60">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between gap-3 h-[72px]">
          <a href="/" class="shrink-0 flex items-center" aria-label="East Coast Construction, home">
            <img src="/assets/images/logo.png" alt="East Coast Construction Group" class="h-11 sm:h-[52px] w-auto" width="180" height="52">
          </a>
          <nav class="hidden lg:flex items-center gap-7 text-[13.5px] font-medium text-ink/80" aria-label="Primary">
            {''.join(links)}
          </nav>
          <div class="flex items-center gap-2 sm:gap-3">
            <a href="tel:{PHONE_TEL}" class="hidden sm:inline-flex items-center gap-2 text-sm font-semibold tracking-tight hover:text-brand">{phone_svg()}{PHONE_DISPLAY}</a>
            <a href="tel:{PHONE_TEL}" class="sm:hidden inline-flex items-center justify-center w-10 h-10 rounded-sm border border-stone text-brand" aria-label="Call {PHONE_DISPLAY}">{phone_svg().replace('w-4 h-4', 'w-5 h-5')}</a>
            <a href="/contact/#quote-form" class="inline-flex items-center justify-center bg-brand hover:bg-brand-dark text-white text-[13px] sm:text-sm font-semibold px-3 sm:px-4 h-10 rounded-sm">
              <span class="sm:hidden">Quote</span><span class="hidden sm:inline">Request a quote</span>
            </a>
            <button type="button" id="menu-btn" class="lg:hidden inline-flex items-center justify-center w-10 h-10 rounded-sm border border-stone" aria-expanded="false" aria-controls="mobile-nav" aria-label="Open menu">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
            </button>
          </div>
        </div>
      </div>
      <div id="mobile-nav" class="lg:hidden border-t border-stone/60 bg-paper px-4 py-4" aria-hidden="true">
        <nav class="flex flex-col gap-1 text-base font-medium" aria-label="Mobile">
          {''.join(mobile)}
          <a href="/reviews/" class="py-2 border-b border-sand">Reviews</a>
          <a href="/faq/" class="py-2 border-b border-sand">FAQ</a>
          <a href="/service-area/" class="py-2 border-b border-sand">Service area</a>
          <a href="/trade-partners/" class="py-2">Trade partners</a>
        </nav>
      </div>
    </header>
    """


def footer() -> str:
    explore = [
        ("Work", "/work/"),
        ("Services", "/services/"),
        ("Process", "/process/"),
        ("Delivery methods", "/delivery-methods/"),
        ("About", "/about/"),
        ("Reviews", "/reviews/"),
        ("FAQ", "/faq/"),
        ("Contact", "/contact/"),
    ]
    practice = [(service["name"], f"/services/{service['slug']}/") for service in SERVICES]
    company = [
        ("Service area", "/service-area/"),
        ("Florida Building Code", "/building-code/"),
        ("Trade partners", "/trade-partners/"),
        ("Careers", "/careers/"),
        ("Privacy", "/privacy/"),
        ("Terms", "/terms/"),
    ]

    def col(title: str, links: list[tuple[str, str]]) -> str:
        items = "\n".join(
            f'<li><a class="hover:text-white" href="{href}">{esc(label)}</a></li>' for label, href in links
        )
        return f"""
        <div>
          <p class="text-[11px] uppercase tracking-[0.16em] text-stone font-semibold mb-3">{esc(title)}</p>
          <ul class="space-y-2 text-sm">{items}</ul>
        </div>"""

    return f"""
    <footer class="bg-[#111] text-paper/80">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 grid sm:grid-cols-2 lg:grid-cols-4 gap-10">
        <div>
          <img src="/assets/images/logo-white.png" alt="East Coast Construction Group" class="h-11 w-auto" width="160" height="44">
          <p class="mt-4 text-sm">Florida-licensed general contractor · Boca Raton, FL · CGC #{LICENSE}</p>
          <p class="mt-2 text-sm"><a class="text-white hover:text-stone" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
          <p class="mt-1 text-sm"><a class="text-white hover:text-stone" href="mailto:{EMAIL}">{EMAIL}</a></p>
          <p class="mt-3 text-sm">{esc(ADDRESS_LINES[0])}<br>{esc(ADDRESS_LINES[1])}</p>
        </div>
        {col("Explore", explore)}
        {col("Services", practice)}
        <div>
          {col("Company", company)}
          <p class="text-[11px] uppercase tracking-[0.16em] text-stone font-semibold mb-3 mt-8">Follow</p>
          <ul class="space-y-2 text-sm">
            <li><a class="hover:text-white" href="{INSTAGRAM}" target="_blank" rel="noopener noreferrer">Instagram</a></li>
            <li><a class="hover:text-white" href="{HOUZZ}" target="_blank" rel="noopener noreferrer">Houzz</a></li>
            <li><a class="hover:text-white" href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn — Anthony Virzi</a></li>
          </ul>
        </div>
      </div>
      <div class="border-t border-white/10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5 flex flex-col sm:flex-row gap-2 sm:items-center sm:justify-between text-xs text-paper/50">
          <p>© 2026 East Coast Construction. Always Be Building.</p>
          <p>Florida CGC #{LICENSE} · {esc(ADDRESS_LINES[0])}, {esc(ADDRESS_LINES[1])}</p>
        </div>
      </div>
    </footer>
    """


def crumbs(items: list[tuple[str, str]]) -> str:
    parts = []
    for index, (label, href) in enumerate(items):
        if index == len(items) - 1:
            parts.append(f'<li aria-current="page">{esc(label)}</li>')
        else:
            parts.append(
                f'<li><a class="hover:text-brand" href="{href}">{esc(label)}</a><span aria-hidden="true" class="mx-2 text-stone">/</span></li>'
            )
    return (
        '<nav aria-label="Breadcrumb" class="text-sm text-muted mb-6"><ol class="flex flex-wrap items-center">'
        + "".join(parts)
        + "</ol></nav>"
    )


def page_hero(eyebrow: str, h1: str, lede: str) -> str:
    lede_html = f'<p class="mt-5 max-w-3xl text-base sm:text-lg text-white/80 leading-relaxed">{esc(lede)}</p>' if lede else ""
    return f"""
    <section class="bg-ink text-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
        <p class="text-[11px] uppercase tracking-[0.18em] text-white/70 font-semibold mb-3">{esc(eyebrow)}</p>
        <h1 class="font-serif font-medium text-4xl sm:text-5xl tracking-tighter2 max-w-4xl">{esc(h1)}</h1>
        {lede_html}
      </div>
    </section>
    """


def cta_band() -> str:
    return f"""
    <section class="bg-ink text-paper">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div>
          <h2 class="font-serif text-3xl text-white tracking-tighter2">Ready to start the next project?</h2>
          <p class="mt-3 text-paper/80 max-w-xl">Tell us the project type, location, and square footage. Or call {PHONE_DISPLAY}.</p>
        </div>
        <div class="flex flex-wrap gap-3">
          <a href="/contact/#quote-form" class="inline-flex items-center justify-center bg-brand hover:bg-brand-dark text-white font-semibold px-5 h-12 rounded-sm">Request a quote</a>
          <a href="tel:{PHONE_TEL}" class="inline-flex items-center justify-center border border-white/70 text-white font-semibold px-5 h-12 rounded-sm">Call {PHONE_DISPLAY}</a>
        </div>
      </div>
    </section>
    """


def add_page(**kwargs) -> None:
    PAGES.append(kwargs)


def render(page: dict) -> str:
    canonical = ORIGIN + page["url"]
    image = ORIGIN + page.get("image", "/assets/images/residence-2.jpg")
    image_alt = page.get("image_alt", "Lake Rodgers Waterfront Estate, Boca Raton, seen from the water")
    robots = page.get("robots", "index,follow")
    nodes = [
        {
            "@type": "WebSite",
            "@id": ORIGIN + "/#website",
            "url": ORIGIN + "/",
            "name": "East Coast Construction",
            "publisher": {"@id": ORIGIN + "/#business"},
        },
        business_node(),
        {
            "@type": "WebPage",
            "@id": canonical + "#webpage",
            "url": canonical,
            "name": page["title"],
            "description": page["description"],
            "isPartOf": {"@id": ORIGIN + "/#website"},
            "about": {"@id": ORIGIN + "/#business"},
            "inLanguage": "en-US",
            "primaryImageOfPage": image,
        },
    ]
    crumbs_data = page.get("breadcrumbs") or []
    if crumbs_data:
        nodes.append(
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": index + 1,
                        "name": label,
                        "item": ORIGIN + href,
                    }
                    for index, (label, href) in enumerate(crumbs_data)
                ],
            }
        )
    nodes.extend(page.get("extra_jsonld") or [])
    draft = ""
    if page.get("draft"):
        draft = (
            '<div class="draft-banner">'
            '<p class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 text-sm leading-relaxed">'
            '<span class="placeholder-badge">Placeholder</span> '
            "Draft for the owner and for legal review. This is a generic policy written for this website. It is not a law firm’s advice, and it is not in effect until the owner adopts it."
            "</p></div>"
        )
    hero = ""
    if not page.get("home") and not page.get("bare"):
        hero = page_hero(page.get("eyebrow", ""), page["h1"], page.get("lede", ""))
    crumb_html = ""
    if crumbs_data and not page.get("home"):
        crumb_html = f'<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">{crumbs(crumbs_data)}</div>'
    main_class = "" if page.get("home") else ""
    return f"""<!doctype html>
<html lang="en-US">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page['title'])}</title>
  <meta name="description" content="{esc(page['description'])}">
  <meta name="robots" content="{esc(robots)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta name="theme-color" content="#d91b23">
  <meta property="og:site_name" content="East Coast Construction">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="en_US">
  <meta property="og:title" content="{esc(page['title'])}">
  <meta property="og:description" content="{esc(page['description'])}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(image)}">
  <meta property="og:image:alt" content="{esc(image_alt)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(page['title'])}">
  <meta name="twitter:description" content="{esc(page['description'])}">
  <meta name="twitter:image" content="{esc(image)}">
  <link rel="icon" type="image/png" href="/assets/images/favicon.png">
  <link rel="apple-touch-icon" href="/assets/images/favicon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Libre+Franklin:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/site.css">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            brand: "#D91B23",
            "brand-dark": "#B4161D",
            ink: "#1A1A1A",
            paper: "#F6F3EE",
            stone: "#C8BEB3",
            muted: "#5C574F",
            sand: "#EFE8DD"
          }},
          fontFamily: {{
            serif: ["Fraunces", "Palatino", "Georgia", "serif"],
            sans: ["Libre Franklin", "Helvetica Neue", "Arial", "sans-serif"]
          }},
          letterSpacing: {{ tighter2: "-0.03em" }}
        }}
      }}
    }};
  </script>
  {json_ld(nodes)}
</head>
<body class="bg-paper text-ink font-sans antialiased{main_class}" data-page="{esc(page.get('nav') or '')}">
  {header(page.get('nav') or '')}
  {draft}
  <main id="main">
    {hero}
    {crumb_html}
    {page['body']}
  </main>
  {footer()}
  <script src="/assets/js/config.js"></script>
  <script src="/assets/js/site.js"></script>
  <noscript>
    <p class="max-w-7xl mx-auto px-4 py-4 text-sm">Menus and forms on this site use JavaScript. You can still call {PHONE_DISPLAY} or email {EMAIL}.</p>
  </noscript>
</body>
</html>
"""


def section_open(extra: str = "") -> str:
    return f'<section class="{extra}"><div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">'


def section_close() -> str:
    return "</div></section>"


def build_home() -> None:
    slides = [
        ("/assets/images/residence-2.jpg", "object-[50%_60%]"),
        ("/assets/images/residence-1.jpg", "object-center"),
        ("/assets/images/hauppauge.jpg", "object-center"),
        ("/assets/images/broadway.jpg", "object-top"),
        ("/assets/images/lobby.jpg", "object-center"),
    ]
    slide_html = []
    for index, (src, fit) in enumerate(slides):
        active = " is-active" if index == 0 else ""
        slide_html.append(
            f'<img src="{src}" alt="" class="hero-slide{active} {fit}" decoding="async">'
        )
    service_cards = []
    for service in SERVICES:
        if service["slug"] in {"preconstruction"}:
            continue
        if service["image"]:
            visual = (
                f'<div class="aspect-[16/10] overflow-hidden"><img src="{esc(service["image"])}" alt="{esc(service["alt"])}" class="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-500"></div>'
            )
        else:
            visual = (
                '<div class="aspect-[16/10] bg-ink text-paper flex items-end p-5"><p class="font-serif text-2xl leading-tight tracking-tighter2">Construction management, as owner’s representative.</p></div>'
            )
        service_cards.append(
            f"""
            <a href="/services/{service['slug']}/" class="group bg-paper border border-stone/60 rounded-sm overflow-hidden flex flex-col hover:border-ink">
              {visual}
              <div class="p-5 flex-1 flex flex-col">
                <h3 class="font-serif text-xl mb-2 group-hover:text-brand">{esc(service['name'])}</h3>
                <p class="text-sm text-muted leading-relaxed flex-1">{esc(service['summary'])}</p>
              </div>
            </a>"""
        )
    cards = "\n".join(project_card(PROJECTS_BY_SLUG[slug]) for slug in FEATURED)
    steps = [
        ("1", "Tell us the project", "Type, place, and size — the same facts the quote form asks for."),
        ("2", "Preconstruction", "Budgeting, and the value engineering the firm has already documented."),
        ("3", "Build", "Staffing, on-site organization, and the handiwork the firm describes."),
        ("4", "Close out", "Through the local building department. The firm’s own closeout checklist is not published."),
    ]
    step_html = "\n".join(
        f"""
        <li class="bg-white border border-stone/60 rounded-sm p-5">
          <p class="text-[11px] uppercase tracking-[0.16em] text-brand font-semibold">{num}</p>
          <h3 class="font-serif text-xl mt-2">{esc(title)}</h3>
          <p class="text-sm text-muted mt-2 leading-relaxed">{esc(text)}</p>
        </li>"""
        for num, title, text in steps
    )
    clients = "\n".join(
        f'<li class="after:content-[\'·\'] after:mx-2 after:text-stone last:after:content-[\'\']">{esc(name)}</li>'
        for name in CLIENTS
    )
    body = f"""
    <section class="relative min-h-[86vh] flex items-end text-white overflow-hidden" aria-label="Introduction">
      <div id="hero-carousel" class="hero-carousel absolute inset-0" aria-hidden="true">{''.join(slide_html)}</div>
      <div class="hero-scrim absolute inset-0 z-[1]"></div>
      <div class="hero-copy relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-10 sm:pb-14">
        <p class="text-[11px] sm:text-xs uppercase tracking-[0.18em] text-white/80 font-medium mb-4">East Coast Construction · Boca Raton, Florida</p>
        <h1 class="font-serif font-medium text-[2.75rem] sm:text-6xl lg:text-7xl leading-[1.05] tracking-tighter2 max-w-4xl">Always Be Building</h1>
        <p class="mt-5 max-w-2xl text-base sm:text-lg text-white/90 leading-relaxed">A Florida-licensed commercial and residential general contractor, serving South Florida from West Palm Beach to the greater Miami area. End-to-end construction and construction management — with a practice that began in 1985.</p>
        <div class="mt-8 flex flex-wrap items-center gap-3">
          <a href="/contact/#quote-form" class="inline-flex items-center justify-center bg-brand hover:bg-brand-dark text-white font-semibold px-5 h-12 rounded-sm">Request a quote</a>
          <a href="/work/" class="inline-flex items-center justify-center border border-white/80 bg-white/10 hover:bg-white hover:text-ink text-white font-semibold px-5 h-12 rounded-sm">See our work</a>
        </div>
        <ul class="mt-8 flex flex-wrap gap-x-5 gap-y-2 text-[12px] sm:text-[13px] text-white/85">
          <li class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-brand"></span>FL CGC #{LICENSE}</li>
          <li class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-brand"></span>CMAA member</li>
          <li class="flex items-center gap-2"><span class="w-1 h-1 rounded-full bg-brand"></span>2021 BuildZoom Top 5 General Contractors in Boca Raton</li>
        </ul>
      </div>
    </section>
    <section class="bg-paper border-b border-stone/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20 grid lg:grid-cols-12 gap-10 lg:gap-16">
        <div class="lg:col-span-5">
          <p class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold mb-3">The practice</p>
          <h2 class="font-serif text-3xl sm:text-4xl leading-tight tracking-tighter2">An end-to-end client experience, from first budget to finished work.</h2>
        </div>
        <div class="lg:col-span-7 text-[16.5px] leading-relaxed text-ink/85 space-y-5">
          <p>We offer an end-to-end client experience that includes seamless communication, budgeting, staffing, on-site organization, and solid, quality handiwork every time.</p>
          <p>Bring our project-management skill and construction experience to the next residence, renovation, commercial building, or house of worship — as general contractor or as owner’s representative.</p>
          <p><a class="font-semibold text-brand" href="/delivery-methods/">How a general contract compares with construction management</a></p>
        </div>
      </div>
    </section>
    <section class="bg-white border-b border-stone/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
        <div class="flex items-end justify-between gap-6 mb-10">
          <div>
            <p class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold mb-3">Services</p>
            <h2 class="font-serif text-3xl sm:text-4xl tracking-tighter2">What we build</h2>
          </div>
          <a href="/services/" class="hidden sm:inline-flex text-sm font-semibold text-brand">All services</a>
        </div>
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">{''.join(service_cards)}</div>
      </div>
    </section>
    <section class="bg-paper border-b border-stone/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
        <div class="flex items-end justify-between gap-6 mb-8">
          <div>
            <p class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold mb-3">Process</p>
            <h2 class="font-serif text-3xl sm:text-4xl tracking-tighter2">From the first conversation through closeout</h2>
          </div>
          <a href="/process/" class="text-sm font-semibold text-brand shrink-0">Full process</a>
        </div>
        <ol class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">{step_html}</ol>
      </div>
    </section>
    <section class="bg-white border-b border-stone/50" data-filter-root>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
        <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-6 mb-4">
          <div>
            <p class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold mb-3">Selected work</p>
            <h2 class="font-serif text-3xl sm:text-4xl tracking-tighter2">Projects with a name and a place</h2>
          </div>
          <div class="flex flex-wrap gap-2" role="group" aria-label="Filter featured projects">
            {filter_buttons("region", [("all", "All"), ("florida", "South Florida"), ("heritage", "Heritage · Northeast")])}
          </div>
        </div>
        <p class="text-sm text-muted mb-4 max-w-2xl">One Florida project is published: Lake Rodgers in Boca Raton. The rest of this grid is Northeast work, labeled as prior track record.</p>
        <p data-filter-count class="text-sm font-medium mb-6">Showing 7 projects</p>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">{cards}</div>
        <p data-filter-empty class="hidden mt-6 text-sm" role="status">No featured projects in that filter. <a class="font-semibold text-brand" href="/work/">See the full index</a>.</p>
        <p class="mt-8"><a class="font-semibold text-brand" href="/work/">All published projects</a></p>
      </div>
    </section>
    <section class="bg-paper border-b border-stone/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
        <p class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold mb-3">Reviews</p>
        <h2 class="font-serif text-3xl sm:text-4xl tracking-tighter2 max-w-2xl">Clients, in their own words</h2>
        <p class="mt-3 text-sm text-muted max-w-2xl">Two letters are published, from February 2002 and May 2010. Dates are shown so the record stays honest.</p>
        <div class="mt-10 grid md:grid-cols-2 gap-4">
          <blockquote class="bg-white border border-stone/60 rounded-sm p-6 sm:p-7 flex flex-col">
            <p class="font-serif text-lg leading-snug">“{esc(DEVITO_QUOTE)}”</p>
            <footer class="mt-5 pt-5 border-t border-stone/60 text-sm">
              <div class="font-semibold">Ronald J. DeVito</div>
              <div class="text-muted">Melville Gardens, LLC</div>
              <div class="text-muted mt-1">$36 million, 188,000-square-foot Huntington Terrace facility · completed February 2002</div>
            </footer>
          </blockquote>
          <blockquote class="bg-white border border-stone/60 rounded-sm p-6 sm:p-7 flex flex-col">
            <p class="font-serif text-lg leading-snug">“{esc(GIAMBALVO_QUOTE)}”</p>
            <footer class="mt-5 pt-5 border-t border-stone/60 text-sm">
              <div class="font-semibold">Robert Giambalvo, CPA</div>
              <div class="text-muted">Giambalvo, Giammarese &amp; Stalzer, P.C.</div>
              <div class="text-muted mt-1">Corporate interior · completed May 2010</div>
            </footer>
          </blockquote>
        </div>
        <p class="mt-6"><a class="font-semibold text-brand" href="/reviews/">Read the letters</a></p>
        <h3 class="mt-12 text-[11px] uppercase tracking-[0.16em] text-muted font-semibold mb-4">Partial client list, as published</h3>
        <ul class="flex flex-wrap gap-y-2 text-sm text-ink/80">{clients}</ul>
      </div>
    </section>
    <section class="bg-white border-b border-stone/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 grid lg:grid-cols-12 gap-10">
        <div class="lg:col-span-7">
          <p class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold mb-3">About</p>
          <h2 class="font-serif text-3xl sm:text-4xl tracking-tighter2">A construction practice that began in 1985.</h2>
          <div class="mt-6 space-y-4 text-[16px] leading-relaxed">
            <p>Thomas Virzi, President of East Coast Construction, founded East Coast Construction Management in Garden City, New York, in 1985. He is a member of the Construction Management Association of America. The company later expanded into general contracting. The Florida office is in Boca Raton. The site says northeast operations run from Great River, New York.</p>
            <p><a class="font-semibold text-brand" href="/about/">History, license, and leadership</a></p>
          </div>
        </div>
        <aside class="lg:col-span-5 bg-paper border border-stone/60 rounded-sm p-6">
          <p class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold">Where the work is</p>
          <p class="mt-3 leading-relaxed">South Florida, from West Palm Beach to the greater Miami area, is the market named on the site. The office is in Boca Raton. Published projects outside Florida are labeled heritage.</p>
          <p class="mt-4"><a class="font-semibold text-brand" href="/service-area/">Service-area pages</a> · <a class="font-semibold text-brand" href="/building-code/">Florida Building Code</a></p>
        </aside>
      </div>
    </section>
    <section class="bg-ink text-paper" id="quote">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20 grid lg:grid-cols-12 gap-12">
        <div class="lg:col-span-5">
          <p class="text-[11px] uppercase tracking-[0.16em] text-stone font-semibold mb-3">Contact</p>
          <h2 class="font-serif text-3xl sm:text-4xl tracking-tighter2 text-white">Ready to start the next project?</h2>
          <p class="mt-5 text-paper/80 leading-relaxed">East Coast Construction is a state-licensed commercial and residential contractor serving South Florida from West Palm Beach to the greater Miami area.</p>
          <dl class="mt-8 space-y-5 text-sm">
            <div><dt class="text-[11px] uppercase tracking-[0.16em] text-stone">Phone</dt><dd class="mt-1"><a class="text-xl font-semibold text-white" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></dd></div>
            <div><dt class="text-[11px] uppercase tracking-[0.16em] text-stone">Email</dt><dd class="mt-1"><a class="text-lg font-semibold text-white" href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
            <div><dt class="text-[11px] uppercase tracking-[0.16em] text-stone">Office</dt><dd class="mt-1">{esc(ADDRESS_LINES[0])}<br>{esc(ADDRESS_LINES[1])}</dd></div>
            <div><dt class="text-[11px] uppercase tracking-[0.16em] text-stone">License</dt><dd class="mt-1">Florida CGC #{LICENSE}</dd></div>
          </dl>
        </div>
        <div class="lg:col-span-7">
          {quote_form("Tell us the project type, location, and square footage. The same questions the previous quote form asked.")}
        </div>
      </div>
    </section>
    """
    add_page(
        path="index.html",
        url="/",
        title="East Coast Construction | General Contractor in Boca Raton, FL",
        description=META_DESCRIPTION,
        nav="home",
        home=True,
        h1="Always Be Building",
        body=body,
        breadcrumbs=[("Home", "/")],
    )


def build_work() -> None:
    cards = "\n".join(project_card(project) for project in PROJECTS)
    body = f"""
    {section_open("bg-paper")}
      <div data-filter-root>
        <div class="flex flex-col gap-4 mb-6">
          <div class="flex flex-wrap gap-2" role="group" aria-label="Filter by market">{filter_buttons("region", [("all", "All markets"), ("florida", "South Florida"), ("heritage", "Heritage · Northeast")])}</div>
          <div class="flex flex-wrap gap-2" role="group" aria-label="Filter by type">{filter_buttons("type", [("all", "All types"), ("residence", "Residences"), ("renovation", "Renovations"), ("commercial", "Commercial"), ("ti", "Tenant improvements"), ("worship", "Worship")])}</div>
        </div>
        <p data-filter-count class="text-sm font-medium mb-6">Showing {len(PROJECTS)} projects</p>
        <p class="text-sm text-muted mb-8 max-w-3xl">South Florida is listed first. Northeast, New Jersey, and Pennsylvania projects stay in the index because they are published work. Each of those pages says it is prior track record, not a Florida project.</p>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">{cards}</div>
        <p data-filter-empty class="hidden mt-8 text-sm" role="status">Nothing in the index matches both filters.</p>
      </div>
      {ph("More South Florida projects — name, city, type, size, schedule, and photographs the owner is willing to publish — are the largest missing piece of this index.")}
    {section_close()}
    {cta_band()}
    """
    add_page(
        path="work/index.html",
        url="/work/",
        title="Projects | East Coast Construction",
        description="Published projects from East Coast Construction. Lake Rodgers Waterfront Estate in Boca Raton is the Florida project. Northeast work is labeled as prior track record.",
        nav="work",
        eyebrow="Work",
        h1="Published projects",
        lede="Every project on the previous public site is here, with the facts that were actually written down.",
        breadcrumbs=[("Home", "/"), ("Work", "/work/")],
        body=body,
    )


def build_project_pages() -> None:
    for project in PROJECTS:
        facts = [
            ("Location", project["place"]),
            ("Type", project["type_label"]),
            ("Size", project["size"] or None),
            ("Schedule", project["schedule_label"] or None),
        ]
        fact_html = []
        for label, value in facts:
            if value:
                shown = esc(value)
            else:
                shown = '<span class="placeholder-badge">Placeholder</span> Not published'
            fact_html.append(
                f'<div class="fact-card bg-white border border-stone/60 rounded-sm p-4"><dt>{esc(label)}</dt><dd>{shown}</dd></div>'
            )
        photos = []
        for photo in project["photos"]:
            photos.append(
                f"""
                <figure class="bg-white border border-stone/60 rounded-sm overflow-hidden">
                  <img src="{esc(photo['src'])}" alt="{esc(photo['alt'])}" class="w-full aspect-[4/3] object-cover">
                  <figcaption class="p-4 text-sm text-muted">{esc(photo['caption'])}</figcaption>
                </figure>"""
            )
        if not photos:
            photos.append(
                '<div class="bg-sand border border-stone/70 rounded-sm p-6">'
                + ph("No photograph of this project is in the published library.")
                + "</div>"
            )
        service = next(item for item in SERVICES if item["slug"] == project["service"])
        if project["region"] == "florida":
            banner = (
                '<p class="border-l-4 border-brand pl-4 text-ink">This is the Florida project published on the site. It is in Boca Raton.</p>'
            )
        else:
            banner = (
                '<p class="border-l-4 border-brand pl-4">This project is part of East Coast Construction’s published Northeast record. '
                "It is prior track record. It is not a South Florida project, and it is not labeled as one.</p>"
            )
        notes = "".join(f"<p>{esc(note)}</p>" for note in project["notes"])
        placeholders = "".join(ph(item) for item in project["placeholders"])
        image = project["photos"][0]["src"] if project["photos"] else "/assets/images/logo.png"
        image_alt = project["photos"][0]["alt"] if project["photos"] else "East Coast Construction Group"
        body = f"""
        {section_open("bg-paper pt-0")}
          <div class="grid lg:grid-cols-12 gap-10">
            <div class="lg:col-span-7 prose-ecc text-[16.5px] leading-relaxed">
              {banner}
              <div class="mt-6 space-y-4">{paras(project['scope'])}{notes}</div>
              {placeholders}
              <p class="mt-6"><a href="/services/{service['slug']}/">Back to {esc(service['name'])}</a></p>
            </div>
            <div class="lg:col-span-5">
              <dl class="grid sm:grid-cols-2 lg:grid-cols-1 gap-3">{''.join(fact_html)}</dl>
            </div>
          </div>
          <div class="mt-10 grid md:grid-cols-2 gap-4">{''.join(photos)}</div>
        {section_close()}
        {cta_band()}
        """
        add_page(
            path=f"work/{project['slug']}/index.html",
            url=f"/work/{project['slug']}/",
            title=project["seo_title"],
            description=project["description"],
            nav="work",
            eyebrow=project["region_label"] + " · " + project["type_label"],
            h1=project["name"],
            lede=project["place"],
            image=image,
            image_alt=image_alt,
            breadcrumbs=[
                ("Home", "/"),
                ("Work", "/work/"),
                (project["name"], f"/work/{project['slug']}/"),
            ],
            body=body,
        )


def build_services() -> None:
    cards = []
    for service in SERVICES:
        cards.append(
            f"""
            <a href="/services/{service['slug']}/" class="block bg-white border border-stone/60 rounded-sm p-6 hover:border-ink">
              <h2 class="font-serif text-2xl">{esc(service['name'])}</h2>
              <p class="mt-3 text-sm text-muted leading-relaxed">{esc(service['summary'])}</p>
            </a>"""
        )
    body = f"""
    {section_open("bg-paper")}
      <div class="prose-ecc max-w-3xl text-[16.5px] leading-relaxed">
        <p>Six services were named on the previous site: luxury residences, luxury renovations, commercial, tenant improvements, houses of worship, and owner’s representation. Preconstruction is collected here from the budgeting and value-engineering work already published. It was not its own page before.</p>
        <p>How those services sit next to a lump-sum contract or a construction-management agreement is on the <a href="/delivery-methods/">delivery methods</a> page. The step-by-step path is on <a href="/process/">Process</a>.</p>
      </div>
      <div class="mt-10 grid md:grid-cols-2 gap-4">{''.join(cards)}</div>
    {section_close()}
    """
    add_page(
        path="services/index.html",
        url="/services/",
        title="Construction Services in South Florida | East Coast Construction",
        description="Luxury residences, renovations, commercial work, tenant improvements, houses of worship, owner’s representation, and preconstruction. East Coast Construction, Boca Raton.",
        nav="services",
        eyebrow="Services",
        h1="What we do",
        lede="General contracting and construction management, as the public site has described them since the last published version.",
        breadcrumbs=[("Home", "/"), ("Services", "/services/")],
        body=body,
    )
    for service in SERVICES:
        related = [PROJECTS_BY_SLUG[slug] for slug in service["project_slugs"]]
        cards_html = "\n".join(project_card(project) for project in related)
        extra = ""
        if service["slug"] == "owners-representation":
            extra = ph(
                "Confirm that owner’s representation is still offered, and replace this summary with the process the firm actually uses."
            )
        if service["slug"] == "preconstruction":
            extra = (
                paras(
                    [
                        "Tenant improvements are described as work done in coordination with architects and designers. That coordination belongs in preconstruction when the drawings are still moving.",
                        "Nothing on the public site sets a preconstruction fee, a duration, or a list of deliverables such as a schedule or a bid package.",
                    ]
                )
                + ph("The owner should add the preconstruction deliverables the firm actually issues, if this is a service they want named on its own.")
            )
        body = f"""
        {section_open("bg-paper")}
          <div class="prose-ecc max-w-3xl text-[16.5px] leading-relaxed">{paras(service['intro'])}{extra}</div>
          <h2 class="font-serif text-3xl mt-12 mb-6">Published projects</h2>
          <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4" data-filter-root>{cards_html}</div>
        {section_close()}
        {cta_band()}
        """
        add_page(
            path=f"services/{service['slug']}/index.html",
            url=f"/services/{service['slug']}/",
            title=service["seo_title"],
            description=service["description"],
            nav="services",
            eyebrow="Services",
            h1=service["name"],
            lede=service["summary"],
            image=service["image"] or "/assets/images/residence-2.jpg",
            image_alt=service["alt"] or "Lake Rodgers Waterfront Estate, Boca Raton, seen from the water",
            breadcrumbs=[
                ("Home", "/"),
                ("Services", "/services/"),
                (service["name"], f"/services/{service['slug']}/"),
            ],
            body=body,
        )


def build_process() -> None:
    steps = [
        (
            "1. The first conversation",
            [
                "The quote form asks for your name, phone, email, project type, and a description that should include location and square footage. You can also call (561) 245-5044 or email avirzi@eccbuilders.com.",
                "Optional files — up to three PDFs or images — match the previous quote form.",
            ],
            ["A reply time is not published. Do not read this page as a promise of a same-day or next-business-day response."],
        ),
        (
            "2. Preconstruction",
            [
                "Budgeting is part of the published client experience. Value engineering is documented, not just claimed: Ronald J. DeVito’s letter credits East Coast Construction with more than $4 million in construction-cost savings on the $36 million Huntington Terrace project.",
                "Tenant-improvement work is described as coordination with architects and designers. Owner’s representation is described as coordination with design and engineering teams.",
            ],
            [
                "Who prepares the estimate, who submits the permit, and what a preconstruction fee covers are not published.",
                "Design-build — one contract for design and construction — is not named as a service. See Delivery methods.",
            ],
        ),
        (
            "3. Construction",
            [
                "The published construction language is staffing, on-site organization, and quality handiwork, with communication running through the job.",
                "On Huntington Terrace, the letter says the work finished inside the time in the construction contract, in February 2002. On the Giambalvo interior, the letter says May 2010, on time and under budget.",
            ],
            ["A standing update rhythm — weekly meetings, photo reports, or a client portal — is not published. Add it here only if that is what the office actually does."],
        ),
        (
            "4. Closeout and the certificate of occupancy",
            [
                "A permitted Florida project is closed by the local building official. For a property in the City of Boca Raton, that official is the city’s building department. The document at the end of many new buildings and substantial alterations is a certificate of occupancy, or a certificate of completion where that is what the permit calls for.",
                "That is how Florida permitting works. It is not a description of an East Coast Construction closeout binder, warranty, or punch-list form, because none of those are published.",
            ],
            ["Add the firm’s closeout steps — punch list, attic stock, warranties, as-builts — when the owner writes them down."],
        ),
    ]
    blocks = []
    for title, paragraphs, placeholders in steps:
        blocks.append(
            f"""
            <li class="bg-white border border-stone/60 rounded-sm p-6 sm:p-8">
              <h2 class="font-serif text-2xl tracking-tighter2">{esc(title)}</h2>
              <div class="mt-4 prose-ecc text-[16.5px] leading-relaxed">{paras(paragraphs)}{''.join(ph(item) for item in placeholders)}</div>
            </li>"""
        )
    body = f"""
    {section_open("bg-paper")}
      <div class="prose-ecc max-w-3xl mb-10 text-[16.5px] leading-relaxed">
        <p>This is the path from the first call through a certificate of occupancy, using only the services East Coast Construction already describes. Steps the office has not published are marked.</p>
        <p>Compare contract types on <a href="/delivery-methods/">delivery methods</a>. Permit geography is on the <a href="/building-code/">Florida Building Code</a> page.</p>
      </div>
      <ol class="space-y-4 max-w-3xl">{''.join(blocks)}</ol>
    {section_close()}
    {cta_band()}
    """
    add_page(
        path="process/index.html",
        url="/process/",
        title="Our Process, from Preconstruction to Certificate of Occupancy | East Coast Construction",
        description="How an East Coast Construction project moves from the first call through preconstruction, construction, and closeout with the local building department. Unpublished steps are marked.",
        nav="process",
        eyebrow="Process",
        h1="How a project actually moves",
        lede="Four steps, from the quote through closeout. Only the parts the firm has published are stated as fact.",
        breadcrumbs=[("Home", "/"), ("Process", "/process/")],
        body=body,
    )


def build_delivery() -> None:
    body = f"""
    {section_open("bg-paper")}
      <div class="prose-ecc max-w-3xl text-[16.5px] leading-relaxed space-y-4">
        <p>Owners usually hire a contractor in one of three ways. East Coast Construction has published two of them. The third is explained so the comparison is complete, and it is marked because the firm has not offered it on the public site.</p>
        <h2 class="font-serif text-3xl pt-4">General contract, often a lump-sum price</h2>
        <p>The owner has drawings. A contractor agrees to build them, often for a lump-sum price, and holds the trade contracts. The residence, renovation, commercial, tenant-improvement, and worship pages are this kind of building work: the firm is presenting projects it constructed or renovated.</p>
        <p>The site does not publish East Coast Construction’s contract form, a sample lump sum, or a statement that every job is lump-sum. Some of the letters describe construction management rather than a lump-sum general contract.</p>
        {ph("Confirm whether a stipulated-sum general contract is the usual offer, and what is included in the price.")}
        <h2 class="font-serif text-3xl pt-4">Construction management and owner’s representation</h2>
        <p>Here the firm is hired to manage the work for the owner: budgeting, value engineering, staffing, on-site organization, and coordination with design and engineering. The previous homepage called this owner’s representation. It did not have its own page.</p>
        <p>The published examples are the two letters. Ronald J. DeVito describes value engineering that saved more than $4 million on a $36 million Huntington Terrace facility, completed in February 2002. Robert Giambalvo describes construction management of a corporate interior, on time and under budget in May 2010.</p>
        <p>An open-book construction-management agreement and a lump-sum general contract answer different risks. The site does not say which one East Coast Construction recommends, or when the honest answer is the simpler lump-sum contract. That judgment belongs to the owner of the firm.</p>
        {ph("Confirm that owner’s representation is still offered, and describe the fee (percentage, fixed, or hourly) if the firm is willing to say so.")}
        <h2 class="font-serif text-3xl pt-4">Design-build</h2>
        <p>In design-build, one contract covers design and construction. The public East Coast Construction site does not use the words design-build, and it does not name an in-house architect.</p>
        {ph("Say whether design-build is offered. If it is not, this section can stay as a comparison and nothing more.")}
        <p>The <a href="/process/">process page</a> is the sequence. The <a href="/services/owners-representation/">owner’s representation</a> page collects the letters.</p>
      </div>
    {section_close()}
    {cta_band()}
    """
    add_page(
        path="delivery-methods/index.html",
        url="/delivery-methods/",
        title="Construction Management, Lump Sum, and Design-Build | East Coast Construction",
        description="How East Coast Construction’s published general contracting and owner’s representation compare with a lump-sum contract and with design-build, which the firm has not advertised.",
        nav="services",
        eyebrow="Delivery methods",
        h1="General contract, construction management, design-build",
        lede="What the firm has actually offered, and what it has not said.",
        breadcrumbs=[("Home", "/"), ("Delivery methods", "/delivery-methods/")],
        body=body,
    )


def build_about() -> None:
    body = f"""
    {section_open("bg-paper")}
      <div class="grid lg:grid-cols-12 gap-12">
        <div class="lg:col-span-7 prose-ecc text-[16.5px] leading-relaxed">
          <p>Thomas Virzi, President, founded East Coast Construction Management in 1985 after serving as Project Manager and Associate at Eastern Construction Management in Great Neck, New York, from 1983 to 1985. The new firm started in Garden City, New York. In 1988 the offices moved to Hauppauge, Long Island. In 1989 East Coast Construction Group was formed and expanded into general contracting, specializing in new building construction and renovation projects of $30 million or less.</p>
          {ph("The “$30 million or less” line is the 1989 description. The site does not say whether that is still the range of work. The older “30 years of experience” line is not reused; the founding year is 1985.")}
          <p>Mr. Virzi is a member of the Construction Management Association of America. The previous About page misspelled the heading “CMMA.” The organization is the CMAA. He is also described as a construction consultant and construction manager. Published project experience covers office buildings, hotels, retail centers, houses of worship, community and public buildings, luxury condominiums and residences, and senior housing.</p>
          <p>The Florida office is 7700 Congress Avenue, Suite 1139, Boca Raton, FL 33487. The About page says the firm currently operates its northeast operations from Great River, New York.</p>
          {ph("Confirm that the Boca Raton office, the Great River office, the service area from West Palm Beach to greater Miami, and license #CGC1525184 are all still current.")}
          <h2 class="font-serif text-3xl pt-6">Names on the public record</h2>
          <p>The website footer has used East Coast Construction. The About page, Instagram, and Houzz use East Coast Construction Group. Houzz lists East Coast Construction Group, Inc. This site uses East Coast Construction in the header, which is the name on the previous footer, and it does not pick a legal name for contracts.</p>
          {ph("Choose the legal name that should appear in the footer, on proposals, and in the schema markup.")}
          <h2 class="font-serif text-3xl pt-6" id="team">Leadership</h2>
          <article class="not-prose bg-white border border-stone/60 rounded-sm p-6 mt-4">
            <h3 class="font-serif text-2xl">Thomas Virzi</h3>
            <p class="text-sm text-muted mt-1">President. Also referred to as Thom Virzi.</p>
            <p class="mt-3 text-sm leading-relaxed">Founder of East Coast Construction Management (1985). Member of the Construction Management Association of America. Described as a construction consultant and construction manager.</p>
            {ph("A portrait is not published. Add a photograph and any biography the owner wants beyond the history above.")}
          </article>
          <article class="not-prose bg-white border border-stone/60 rounded-sm p-6 mt-4">
            <h3 class="font-serif text-2xl">Anthony Virzi</h3>
            <p class="text-sm text-muted mt-1">Named only as the LinkedIn profile in the previous footer. No title is published.</p>
            <p class="mt-3 text-sm"><a class="font-semibold text-brand" href="{LINKEDIN}">LinkedIn profile, as linked from the previous site</a></p>
            {ph("Add Anthony Virzi’s title if he should appear as part of the firm, or remove this block if he should not be on the About page.")}
          </article>
          {ph("No other people are named on the public site. Add them here, with roles, when the owner wants them listed. Do not invent a staff chart.")}
        </div>
        <aside class="lg:col-span-5 space-y-4" id="credentials">
          <div class="bg-white border border-stone/60 rounded-sm p-6">
            <p class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold">Florida license</p>
            <p class="font-serif text-2xl mt-2">Certified General Contractor</p>
            <p class="mt-1 text-lg font-semibold">#{LICENSE}</p>
            <p class="mt-3 text-sm text-muted">Published on the About page. Look up licenses at the <a class="font-semibold text-brand" href="{DBPR}">Florida DBPR portal</a>.</p>
            {ph("Confirm the number is the active license before relying on this page as the system of record.")}
          </div>
          <div class="bg-white border border-stone/60 rounded-sm p-6 flex gap-4 items-center">
            <img src="/assets/images/cmaa.png" alt="Construction Management Association of America" class="h-14 w-auto">
            <p class="text-sm text-muted">Thom Virzi, President, is a member of the Construction Management Association of America.</p>
          </div>
          <div class="bg-white border border-stone/60 rounded-sm p-6 flex gap-4 items-center">
            <img src="/assets/images/buildzoom-badge.png" alt="BuildZoom 2021 badge, Top 5 General Contractors in Boca Raton" class="h-14 w-auto">
            <p class="text-sm text-muted">2021: named among the Top 5 General Contractors in Boca Raton on BuildZoom. The year is part of the credit so it is not read as a current-year award.</p>
          </div>
          <div class="bg-white border border-stone/60 rounded-sm p-6 text-sm">
            <h2 class="font-serif text-xl">Insurance, bonding, and safety</h2>
            <ul class="mt-3 space-y-3 text-muted">
              <li>{ph("Insurance carrier, general-liability limits, and whether certificates are available on request are not published.")}</li>
              <li>{ph("Bonding capacity is not published.")}</li>
              <li>{ph("A safety program, EMR, and OSHA or LEED credentials are not published. Do not add a number until the owner supplies it.")}</li>
              <li>{ph("No New York or other state license is published. Add one only if the owner wants it listed.")}</li>
              <li>{ph("Awards after the 2021 BuildZoom listing are not published.")}</li>
            </ul>
          </div>
        </aside>
      </div>
    {section_close()}
    {cta_band()}
    """
    add_page(
        path="about/index.html",
        url="/about/",
        title="About East Coast Construction | Boca Raton General Contractor",
        description="Thomas Virzi founded East Coast Construction Management in 1985. Florida CGC #CGC1525184. Office in Boca Raton, with northeast operations published in Great River, New York.",
        nav="about",
        eyebrow="About",
        h1="A construction practice that began in 1985.",
        lede="History, the Florida license, and the people the public site actually names.",
        breadcrumbs=[("Home", "/"), ("About", "/about/")],
        body=body,
    )


def build_reviews() -> None:
    clients = "\n".join(f"<li>{esc(name)}</li>" for name in CLIENTS)
    body = f"""
    {section_open("bg-paper")}
      <div class="grid md:grid-cols-2 gap-4">
        <blockquote class="bg-white border border-stone/60 rounded-sm p-6 sm:p-8">
          <p class="font-serif text-xl leading-snug">“{esc(DEVITO_QUOTE)}”</p>
          <footer class="mt-6 pt-5 border-t border-stone/60 text-sm">
            <p class="font-semibold">Ronald J. DeVito, Melville Gardens, LLC</p>
            <p class="text-muted mt-2">Excerpt from the letter published on the testimonials page. The letter describes the Huntington Terrace project: $36 million, 188,000 square feet, more than $4 million saved in value engineering, completed February 2002. It also describes a then-planned $65 million Concordia Senior Communities project, which is not published as a completed job.</p>
            <p class="mt-3"><a class="font-semibold text-brand" href="/work/huntington-terrace/">Huntington Terrace case study</a></p>
          </footer>
        </blockquote>
        <blockquote class="bg-white border border-stone/60 rounded-sm p-6 sm:p-8">
          <p class="font-serif text-xl leading-snug">“{esc(GIAMBALVO_QUOTE)}”</p>
          <footer class="mt-6 pt-5 border-t border-stone/60 text-sm">
            <p class="font-semibold">Robert Giambalvo, CPA, Giambalvo, Giammarese &amp; Stalzer, P.C.</p>
            <p class="text-muted mt-2">Excerpt from the letter published on the testimonials page, about a corporate interior build-out completed on time and under budget in May 2010.</p>
            <p class="mt-3"><a class="font-semibold text-brand" href="/work/cpa-interior/">Interior build-out case study</a></p>
          </footer>
        </blockquote>
      </div>
      {ph("Newer named reviews — with permission to quote them — are not on the public site. Google, Houzz, and BuildZoom reviews are not embedded, because permission to republish them was not found.")}
      <h2 class="font-serif text-3xl mt-12">Partial client list, as published</h2>
      <ul class="mt-4 columns-1 sm:columns-2 gap-8 text-sm leading-8">{clients}</ul>
      <p class="mt-4 text-sm text-muted">Names are printed as text. Client logos are not used.</p>
    {section_close()}
    {cta_band()}
    """
    add_page(
        path="reviews/index.html",
        url="/reviews/",
        title="Client Letters | East Coast Construction",
        description="Two published client letters: Ronald J. DeVito on Huntington Terrace, completed February 2002, and Robert Giambalvo on a corporate interior completed May 2010.",
        nav="about",
        eyebrow="Reviews",
        h1="Two letters, with their dates attached",
        lede="The testimonials page published these excerpts and a partial client list. Nothing newer is added here.",
        breadcrumbs=[("Home", "/"), ("Reviews", "/reviews/")],
        body=body,
    )


def build_faq() -> None:
    items = []
    for faq in FAQS:
        items.append(
            f"""
            <details class="bg-white border border-stone/60 rounded-sm p-5 group">
              <summary class="font-semibold cursor-pointer">{esc(faq['q'])}</summary>
              <p class="mt-3 text-sm leading-relaxed text-ink/85">{esc(faq['a'])}</p>
            </details>"""
        )
    schema = {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq["q"],
                "acceptedAnswer": {"@type": "Answer", "text": faq["a"]},
            }
            for faq in FAQS
            if faq["schema"]
        ],
    }
    body = f"""
    {section_open("bg-paper")}
      <div class="max-w-3xl space-y-3">{''.join(items)}</div>
      <p class="max-w-3xl mt-8 text-sm text-muted">Answers that the public site does not settle — permits, insurance, update cadence — say so in the answer, instead of filling the gap.</p>
    {section_close()}
    {cta_band()}
    """
    add_page(
        path="faq/index.html",
        url="/faq/",
        title="FAQ | East Coast Construction, Boca Raton",
        description="License, service area, pricing, permits, architect coordination, insurance, and how Northeast projects differ from the Boca Raton work. Answers use only published facts.",
        nav="about",
        eyebrow="FAQ",
        h1="Questions owners ask before they call",
        lede="Short answers. Where the firm has not published a fact, the answer says that.",
        breadcrumbs=[("Home", "/"), ("FAQ", "/faq/")],
        extra_jsonld=[schema],
        body=body,
    )


def build_code() -> None:
    body = f"""
    {section_open("bg-paper")}
      <div class="prose-ecc max-w-3xl text-[16.5px] leading-relaxed">
        <p>East Coast Construction holds Florida certified general contractor license #{LICENSE} and keeps an office in Boca Raton. The firm has not published a hurricane portfolio, a wind-mitigation specialty, or an inspector credential. This page is general public context for owners building in South Florida. It is not engineering advice, and it is not a claim that any particular ECC project used a specific product or design pressure.</p>
        <h2 class="font-serif text-3xl pt-4">The Florida Building Code, enforced locally</h2>
        <p>The Florida Building Code is the statewide code. Local building departments review plans and inspect the work. A property inside the City of Boca Raton is reviewed by the city’s building department. Unincorporated Palm Beach County is a different building department. The published Lake Rodgers write-up does not say which official permitted that house.</p>
        {ph("Name the building department that permitted Lake Rodgers, and who filed the application, if the owner wants that on the case study.")}
        <h2 class="font-serif text-3xl pt-4">High Velocity Hurricane Zone, and everywhere else</h2>
        <p>Under the Florida Building Code, the High Velocity Hurricane Zone is Miami-Dade County and Broward County. Boca Raton is in Palm Beach County, so it is outside that zone. Fort Lauderdale and Miami are inside it. The license is a state certified general contractor license, which is the class of license used for work in the HVHZ and outside it. The site does not publish HVHZ project experience.</p>
        <p>Wind-borne debris rules are separate from the HVHZ boundary. In a wind-borne debris region, glazed openings need impact-resistant assemblies or an approved opening-protection system. Whether a given address is inside that region comes from the code maps for the site, not from a brochure. Coastal Palm Beach County, including Boca Raton, is commonly inside a wind-borne debris region. The permit set for the property is what governs.</p>
        <h2 class="font-serif text-3xl pt-4">What the published Florida house does, and does not, say</h2>
        <p>Lake Rodgers is described as a two-story masonry and concrete house with a barrel-tile roof, marble flooring, and 21-foot ceilings, on a deep-water lot. The write-up does not mention impact glass, shutter schedules, design wind speed, or roof-deck fastening. Those facts are not invented here.</p>
        <p><a href="/work/lake-rodgers/">Lake Rodgers case study</a> · <a href="/service-area/boca-raton/">Boca Raton service area</a> · <a href="/process/">Process, including closeout</a></p>
        {ph("If the firm has Florida projects that show impact openings, roof-to-wall connections, or a specific wind design, this is the page for them — with the owner’s photographs and the real project names.")}
      </div>
    {section_close()}
    {cta_band()}
    """
    add_page(
        path="building-code/index.html",
        url="/building-code/",
        title="Florida Building Code and Coastal Construction | East Coast Construction",
        description="How the Florida Building Code, the High Velocity Hurricane Zone, and wind-borne debris regions apply around Boca Raton. General information, not a claim of unpublished ECC credentials.",
        nav="about",
        eyebrow="Florida Building Code",
        h1="Coastal construction, without invented credentials",
        lede="What a Boca Raton owner is actually dealing with under the Florida Building Code, and what this firm has not claimed.",
        breadcrumbs=[("Home", "/"), ("Florida Building Code", "/building-code/")],
        body=body,
    )


def build_service_area() -> None:
    cities = [
        (
            "boca-raton",
            "Boca Raton",
            "The office is here, and so is the one published Florida project.",
            [
                "The published office is 7700 Congress Avenue, Suite 1139, Boca Raton, FL 33487, in Palm Beach County. The phone is (561) 245-5044.",
                "Lake Rodgers Waterfront Estate, a 7,600-square-foot waterfront house, is the Boca Raton project on the site. The 2021 BuildZoom credit is specifically “Top 5 General Contractors in Boca Raton,” and it is a 2021 credit.",
                "Boca Raton is outside the High Velocity Hurricane Zone (Miami-Dade and Broward). Wind-borne debris protection is a separate question and is covered on the building-code page.",
            ],
            False,
        ),
        (
            "west-palm-beach",
            "West Palm Beach",
            "Named as the north end of the published service area. No West Palm Beach project is on the site.",
            [
                "The homepage describes service from West Palm Beach to the greater Miami area. West Palm Beach is the city named at the north end of that sentence.",
                "No project in West Palm Beach is published. There is no second office there. The Great River, New York, note on the About page is a northeast office, not a Palm Beach County office.",
            ],
            True,
        ),
        (
            "fort-lauderdale",
            "Fort Lauderdale",
            "Inside the published corridor, in Broward County. No Fort Lauderdale project or office is published.",
            [
                "Fort Lauderdale sits between West Palm Beach and Miami, the two ends of the service area named on the site. Broward County is inside the High Velocity Hurricane Zone.",
                "No Fort Lauderdale project, client, or office is published. This page exists so the corridor is explained honestly, not because a local portfolio is ready.",
            ],
            True,
        ),
        (
            "miami",
            "Miami",
            "The greater Miami area is the south end of the published service area. No Miami project is on the site.",
            [
                "The site says the firm serves South Florida through the greater Miami area. Miami-Dade County is inside the High Velocity Hurricane Zone.",
                "No Miami project is published. The Manhattan, Brooklyn, and Long Island work is not Miami work, and the project pages say so.",
            ],
            True,
        ),
    ]
    index_cards = []
    for slug, name, lede, _paragraphs, _thin in cities:
        index_cards.append(
            f'<a href="/service-area/{slug}/" class="block bg-white border border-stone/60 rounded-sm p-6 hover:border-ink"><h2 class="font-serif text-2xl">{esc(name)}</h2><p class="mt-2 text-sm text-muted">{esc(lede)}</p></a>'
        )
    body = f"""
    {section_open("bg-paper")}
      <div class="prose-ecc max-w-3xl text-[16.5px] leading-relaxed">
        <p>The published service area is South Florida, from West Palm Beach to the greater Miami area. The office is in Boca Raton. One Florida project is published, and it is in Boca Raton.</p>
        <p>These city pages repeat that geography. They do not invent local jobs, local staff, or local reviews. Northeast projects stay on the <a href="/work/">work index</a>, labeled as heritage.</p>
        {ph("Confirm the firm still takes work across this whole corridor. If the real area is smaller, narrow these pages rather than adding cities.")}
      </div>
      <div class="mt-10 grid md:grid-cols-2 gap-4">{''.join(index_cards)}</div>
    {section_close()}
    """
    add_page(
        path="service-area/index.html",
        url="/service-area/",
        title="South Florida Service Area | East Coast Construction",
        description="East Coast Construction serves South Florida from West Palm Beach to the greater Miami area, with an office in Boca Raton. City pages do not invent local projects.",
        nav="about",
        eyebrow="Service area",
        h1="South Florida, from West Palm Beach to greater Miami",
        lede="The market the site already claims, city by city, without a fake local portfolio.",
        breadcrumbs=[("Home", "/"), ("Service area", "/service-area/")],
        body=body,
    )
    for slug, name, lede, paragraphs, thin in cities:
        extra = ""
        if slug == "boca-raton":
            extra = '<p><a href="/work/lake-rodgers/">Lake Rodgers Waterfront Estate</a></p>'
        if thin:
            extra += ph(f"No {name} project is published. Add one here only when there is a real name, a photograph, and permission to show it.")
        body = f"""
        {section_open("bg-paper")}
          <div class="prose-ecc max-w-3xl text-[16.5px] leading-relaxed">
            {paras(paragraphs)}
            {extra}
            <p>Office for the firm: {esc(ADDRESS_LINES[0])}, {esc(ADDRESS_LINES[1])}. License CGC #{LICENSE}. <a href="/building-code/">Florida Building Code notes</a> · <a href="/contact/">Request a quote</a></p>
          </div>
        {section_close()}
        {cta_band()}
        """
        add_page(
            path=f"service-area/{slug}/index.html",
            url=f"/service-area/{slug}/",
            title=f"General Contractor in {name}, Florida | East Coast Construction",
            description=lede + f" Office at 7700 Congress Avenue, Suite 1139, Boca Raton. Florida CGC #{LICENSE}.",
            nav="about",
            eyebrow="Service area",
            h1=name,
            lede=lede,
            breadcrumbs=[
                ("Home", "/"),
                ("Service area", "/service-area/"),
                (name, f"/service-area/{slug}/"),
            ],
            body=body,
        )


def build_trades_careers() -> None:
    body = f"""
    {section_open("bg-paper")}
      <div class="grid lg:grid-cols-12 gap-10">
        <div class="lg:col-span-5 prose-ecc text-[16.5px] leading-relaxed">
          <p>East Coast Construction does not publish a prequalification portal, a BuildingConnected room, or required insurance limits. This form is a bid-list signup: company, trade, license if you have one, and whether general liability and workers’ compensation are in force.</p>
          <p>Submitting it does not put you under contract and does not promise an invitation to bid.</p>
          {ph("Publish the insurance limits, bond, and license rules the office actually requires before a trade is invited to price work. Until then, the form only asks what a company carries.")}
        </div>
        <div class="lg:col-span-7">{trade_form()}</div>
      </div>
    {section_close()}
    """
    add_page(
        path="trade-partners/index.html",
        url="/trade-partners/",
        title="Trade Partners and Bid List | East Coast Construction",
        description="Subcontractors can send company, trade, license, and insurance information to East Coast Construction. Required coverage limits are not published.",
        nav="contact",
        eyebrow="Trade partners",
        h1="Work with the office",
        lede="A signup for trades. Not a public bid board, and not a list of required limits the firm has not set in print.",
        breadcrumbs=[("Home", "/"), ("Trade partners", "/trade-partners/")],
        body=body,
    )
    body = f"""
    {section_open("bg-paper")}
      <div class="grid lg:grid-cols-12 gap-10">
        <div class="lg:col-span-5 prose-ecc">
          <p>No open positions are published. There is no jobs board, no list of benefits, and no claim that the firm is hiring.</p>
          {ph("When there is a real opening, name the role, the location, and how to apply. Until then this page should stay empty of jobs.")}
        </div>
        <div class="lg:col-span-7">{careers_form()}</div>
      </div>
    {section_close()}
    """
    add_page(
        path="careers/index.html",
        url="/careers/",
        title="Careers | East Coast Construction",
        description="East Coast Construction has not published any open jobs. You can send your interest for when a role is posted.",
        nav="about",
        eyebrow="Careers",
        h1="No open roles are published",
        lede="This page exists so the address does not 404. It does not invent a hiring program.",
        breadcrumbs=[("Home", "/"), ("Careers", "/careers/")],
        body=body,
    )


def build_contact() -> None:
    body = f"""
    {section_open("bg-paper")}
      <div class="grid lg:grid-cols-12 gap-12">
        <div class="lg:col-span-5">
          <dl class="space-y-5 text-sm">
            <div><dt class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold">Phone</dt><dd class="mt-1 text-xl font-semibold"><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></dd></div>
            <div><dt class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold">Email</dt><dd class="mt-1 text-lg font-semibold"><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
            <div><dt class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold">Office</dt><dd class="mt-1">{esc(ADDRESS_LINES[0])}<br>{esc(ADDRESS_LINES[1])}</dd></div>
            <div><dt class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold">License</dt><dd class="mt-1">Florida Certified General Contractor #{LICENSE}</dd></div>
            <div><dt class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold">Service area</dt><dd class="mt-1">South Florida, from West Palm Beach to the greater Miami area, as published. <a class="font-semibold text-brand" href="/service-area/">City pages</a></dd></div>
            <div><dt class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold">Northeast office, as published</dt><dd class="mt-1">Great River, New York. {ph("Confirm this office is still open. No street address was published.")}</dd></div>
            <div><dt class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold">Hours</dt><dd class="mt-1">{ph("Office hours are not published. Add them when the owner confirms the schedule.")}</dd></div>
          </dl>
          <iframe title="Map of 7700 Congress Avenue, Suite 1139, Boca Raton, Florida" class="mt-8 w-full h-72 border border-stone/70 rounded-sm" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://www.openstreetmap.org/export/embed.html?bbox=-80.10837%2C26.41027%2C-80.08237%2C26.42427&amp;layer=mapnik&amp;marker=26.4172735%2C-80.0953701"></iframe>
          <p class="mt-2 text-xs text-muted"><a class="underline" href="https://www.openstreetmap.org/?mlat=26.4172735&amp;mlon=-80.0953701#map=16/26.41727/-80.09537">Open the map</a></p>
        </div>
        <div class="lg:col-span-7">
          {quote_form("The phone, email, and address on this page stay visible even if the form cannot send.")}
        </div>
      </div>
    {section_close()}
    """
    add_page(
        path="contact/index.html",
        url="/contact/",
        title="Request a Quote | East Coast Construction, Boca Raton",
        description="Call (561) 245-5044, email avirzi@eccbuilders.com, or send a quote request. Office: 7700 Congress Avenue, Suite 1139, Boca Raton, FL 33487. CGC #CGC1525184.",
        nav="contact",
        eyebrow="Contact",
        h1="Request a quote",
        lede="Phone, email, the Boca Raton office, and the form. The contact details do not depend on the form.",
        breadcrumbs=[("Home", "/"), ("Contact", "/contact/")],
        body=body,
    )


def build_privacy() -> None:
    body = f"""
    {section_open("bg-paper")}
      <article class="prose-ecc max-w-3xl text-[16.5px] leading-relaxed">
        <p>This draft describes the East Coast Construction website at this domain. The operator to name in a final policy is the legal entity the owner selects. Until then the site uses the published name East Coast Construction, at {esc(ADDRESS_LINES[0])}, {esc(ADDRESS_LINES[1])}, phone {PHONE_DISPLAY}, email {EMAIL}.</p>
        <h2 class="font-serif text-2xl pt-4">What the forms collect</h2>
        <p>The quote form collects first name, last name, phone, email, project type, project details, how you want to be contacted, and up to three optional files (PDF, JPEG, JPG, or PNG). The trade-partner form collects company, contact name, email, phone, trade, an optional license number, whether general liability and workers’ compensation are in force, and notes. The careers form collects name, email, phone, a trade or role, and a note. There are no open jobs behind that form.</p>
        <p>A hidden field labeled “company website” is a spam trap. People using the form leave it blank. It is not used to identify you.</p>
        <h2 class="font-serif text-2xl pt-4">Why it is collected</h2>
        <p>This draft says the information is used to answer the inquiry, to consider a trade for future bids, or to hold a careers note until the owner decides whether to keep it. It is not required to browse the rest of the site.</p>
        {ph("Name the person who receives submissions, how long messages and files are kept, and whether anyone else (an estimator, a partner, a virtual assistant) sees them.")}
        <h2 class="font-serif text-2xl pt-4">Where the form is delivered</h2>
        <p>The page sends the form to an address the owner configures (QUOTE_FORM_ENDPOINT, or the fields in assets/js/config.js). That address may be a form service, an inbox bridge, or an automation tool. This draft does not name the vendor, because none is configured in the repository.</p>
        {ph("Name the form vendor in this paragraph once it is chosen, and link to that vendor’s privacy policy if the vendor stores the data.")}
        <h2 class="font-serif text-2xl pt-4">Cookies and analytics</h2>
        <p>This version of the site does not load Google Analytics and does not set an analytics cookie. The previous eccbuilders.com site used Google Analytics 4, measurement ID G-4SNM9CYPCP, behind an accept-only cookie banner. That tag is not included here. The site still loads typefaces from Google Fonts and the Tailwind script from a CDN, which means those providers receive the usual technical request data (such as IP address) when the page loads.</p>
        {ph("Decide whether GA4, or any other analytics, should be turned back on. If it is, this section and a cookie notice have to be rewritten, and the tag should not load before consent if that is the rule the owner adopts.")}
        <h2 class="font-serif text-2xl pt-4">Selling personal information</h2>
        <p>This draft states that inquiry information is not sold. The owner has to confirm that sentence before the policy is treated as real. The site does not show advertising.</p>
        <h2 class="font-serif text-2xl pt-4">Requests</h2>
        <p>To ask what was submitted, or to ask that a quote, trade, or careers message be deleted, email {EMAIL} or write to the Boca Raton office. The owner should confirm that this inbox is the right place for privacy requests.</p>
        <h2 class="font-serif text-2xl pt-4">Children</h2>
        <p>The site is about construction services for adults. It is not directed at children.</p>
        <h2 class="font-serif text-2xl pt-4">Changes</h2>
        <p>Draft dated 12 November 2026. It is not adopted. Replace this date when the owner signs off, and keep the marked placeholders until the missing facts are filled in.</p>
      </article>
    {section_close()}
    """
    add_page(
        path="privacy/index.html",
        url="/privacy/",
        title="Privacy Policy (Draft) | East Coast Construction",
        description="Draft privacy policy for the East Coast Construction website: quote, trade-partner, and careers forms, files, and the analytics tag that is not currently installed.",
        nav="",
        draft=True,
        eyebrow="Privacy",
        h1="Privacy policy",
        lede="A working draft so the form is not collecting names with no policy at all. Counsel and the owner still have to adopt it.",
        breadcrumbs=[("Home", "/"), ("Privacy", "/privacy/")],
        body=body,
    )


def build_terms() -> None:
    body = f"""
    {section_open("bg-paper")}
      <article class="prose-ecc max-w-3xl text-[16.5px] leading-relaxed">
        <p>These terms cover use of this website and the forms on it. They are a draft. They are not a construction contract, a bid, or a subcontract.</p>
        <h2 class="font-serif text-2xl pt-4">A quote request is not a contract</h2>
        <p>Sending the quote form, calling the office, or emailing {EMAIL} starts a conversation. It does not create a construction agreement, a price, or a start date. Only a written agreement the firm signs does that. Nothing on this site is an offer to do a defined scope for a defined price.</p>
        <h2 class="font-serif text-2xl pt-4">What you send</h2>
        <p>You agree that the contact details and project description you submit are yours to send. Do not include someone else’s confidential drawings unless you have the right to share them. Files are limited by the form to three PDFs or images, 10 MB each. That limit is a limit of this website, not a project rule.</p>
        <h2 class="font-serif text-2xl pt-4">Trade partners</h2>
        <p>The trade-partner form collects company information for a list the office may use when it needs a price. It does not add you to a union, a preferred-vendor program, or a public bid. Insurance minimums are not published. The office can decide not to invite a firm, and it does not owe a reason in this draft.</p>
        <h2 class="font-serif text-2xl pt-4">Careers</h2>
        <p>No job is offered on the careers page. Sending your interest is not an application for a specific role and does not create an employment relationship.</p>
        <h2 class="font-serif text-2xl pt-4">Site content</h2>
        <p>Project pages distinguish Florida work from older Northeast work. Placeholder labels mean the owner has not supplied that fact. Do not treat a placeholder, a draft policy, or the building-code page as professional advice. The building-code page is general public information.</p>
        <h2 class="font-serif text-2xl pt-4">Liability</h2>
        <p>This draft says the website is provided as published information, without a warranty that every older project detail is still current. The license number, address, and phone are the ones on the public site as of 12 November 2026 and should be confirmed with the office.</p>
        {ph("Have counsel add any liability limit, indemnity, or governing-law sentence the owner wants. A Florida governing-law sentence is the obvious candidate and is not written here as if it had been adopted.")}
        <h2 class="font-serif text-2xl pt-4">Contact</h2>
        <p>{esc(ADDRESS_LINES[0])}, {esc(ADDRESS_LINES[1])}. {PHONE_DISPLAY}. {EMAIL}.</p>
      </article>
    {section_close()}
    """
    add_page(
        path="terms/index.html",
        url="/terms/",
        title="Terms of Use (Draft) | East Coast Construction",
        description="Draft terms for the East Coast Construction website. A quote request is not a contract. Trade-partner and careers forms do not promise work.",
        nav="",
        draft=True,
        eyebrow="Terms",
        h1="Terms of use",
        lede="Draft rules for the forms and the pages. Not a substitute for a construction contract.",
        breadcrumbs=[("Home", "/"), ("Terms", "/terms/")],
        body=body,
    )


def build_404() -> None:
    body = f"""
    {section_open("bg-paper")}
      <div class="max-w-xl">
        <p class="text-[11px] uppercase tracking-[0.16em] text-muted font-semibold">404</p>
        <h1 class="font-serif text-4xl sm:text-5xl tracking-tighter2 mt-3">That page is not on this site.</h1>
        <p class="mt-4 text-muted leading-relaxed">The address may have changed. The work, services, and quote form are all still here.</p>
        <div class="mt-8 flex flex-wrap gap-3">
          <a href="/" class="inline-flex items-center justify-center bg-brand text-white font-semibold px-5 h-12 rounded-sm">Home</a>
          <a href="/work/" class="inline-flex items-center justify-center border border-ink font-semibold px-5 h-12 rounded-sm">Projects</a>
          <a href="/contact/" class="inline-flex items-center justify-center border border-ink font-semibold px-5 h-12 rounded-sm">Contact</a>
        </div>
      </div>
    {section_close()}
    """
    add_page(
        path="404.html",
        url="/404.html",
        title="Page not found | East Coast Construction",
        description="This address is not on the East Coast Construction site. Go to the homepage, the project index, or the quote form.",
        nav="",
        bare=True,
        robots="noindex,follow",
        eyebrow="404",
        h1="That page is not on this site.",
        lede="",
        body=body,
    )


def write_sitemap_and_robots() -> None:
    urls = []
    for page in PAGES:
        if page["path"] == "404.html":
            continue
        urls.append(f"  <url><loc>{ORIGIN}{page['url']}</loc><lastmod>{LASTMOD}</lastmod></url>")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    robots = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {ORIGIN}/sitemap.xml\n"
    )
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")


def write_redirect_doc() -> None:
    deploy = ROOT / "deploy"
    deploy.mkdir(exist_ok=True)
    rows = [
        ("/about-us", "/about/"),
        ("/luxury-residences", "/services/luxury-residences/"),
        ("/commercial", "/services/commercial/"),
        ("/tenant-improvements", "/services/tenant-improvements/"),
        ("/luxury-renovations", "/services/luxury-renovations/"),
        ("/houses-of-worship", "/services/houses-of-worship/"),
        ("/testimonials", "/reviews/"),
        ("/contact-us", "/contact/"),
    ]
    lines = [
        "# Easypanel proxy redirects",
        "",
        "The current Easypanel service is a static nginx site. Redirect rules in the Easypanel domain settings run before traffic hits the app. Add one permanent rule per row. The same map is in `nginx.conf` for the optional Dockerfile.",
        "",
        "Test as temporary first if you want to avoid a cached mistake, then switch to permanent (301).",
        "",
        "| Regex | Replacement |",
        "| --- | --- |",
    ]
    for old, new in rows:
        pattern = "^" + old + "/?$"
        target = ORIGIN + new
        lines.append(f"| `{pattern}` | `{target}` |")
    lines.append("")
    (deploy / "easypanel-redirects.md").write_text("\n".join(lines), encoding="utf-8")


def check() -> None:
    targets = {page["url"]: ROOT / page["path"] for page in PAGES}
    missing = []
    hrefs = re.compile(r'href="(/[^"]*)"')
    for page in PAGES:
        text = (ROOT / page["path"]).read_text(encoding="utf-8")
        for href in hrefs.findall(text):
            path = href.split("#", 1)[0]
            if not path or path.startswith("//"):
                continue
            if path in targets or (ROOT / path.lstrip("/")).is_file():
                continue
            folder = ROOT / path.strip("/") / "index.html"
            if folder.is_file():
                continue
            missing.append(f"{page['url']} -> {href}")
    titles = [page["title"] for page in PAGES]
    if len(titles) != len(set(titles)):
        dupes = sorted({title for title in titles if titles.count(title) > 1})
        raise SystemExit("Duplicate titles: " + ", ".join(dupes))
    if missing:
        raise SystemExit("Broken internal links:\n" + "\n".join(missing[:40]))
    print(f"Wrote {len(PAGES)} pages. Internal links resolve.")


def main() -> None:
    build_home()
    build_work()
    build_project_pages()
    build_services()
    build_process()
    build_delivery()
    build_about()
    build_reviews()
    build_faq()
    build_code()
    build_service_area()
    build_trades_careers()
    build_contact()
    build_privacy()
    build_terms()
    build_404()
    for page in PAGES:
        dest = ROOT / page["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        # 404 page hero duplicates the h1. The body also has an h1.
        dest.write_text(render(page), encoding="utf-8")
    write_sitemap_and_robots()
    write_redirect_doc()
    check()


if __name__ == "__main__":
    main()
