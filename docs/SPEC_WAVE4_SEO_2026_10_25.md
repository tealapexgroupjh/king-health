---
title: King Health Wave 4, search engine optimization
created: 2026-10-25
owner: Teal Apex Group LLC (client build)
type: build-spec
status: frozen
---

# Wave 4: SEO (applies identically to all nine King Health builds, after Wave 3)

Goal: rank for local insurance searches in the client's core market (Washington DC metro and New Jersey, East Coast) while staying discoverable nationally, without inventing facts and without breaking insurance marketing rules (an agent may only market in states where he is licensed).

## A. Configuration in content.json (all data driven)
Add a `seo` block:
- `base_url`: "" (the live domain, for example https://kinghealth.com; required for canonicals, sitemap and Open Graph; release lint FAILS if empty).
- `service_areas`: ["Washington, DC", "Maryland", "Virginia", "New Jersey"] with a `_comment`: "Confirm against licensed states before launch. Only list states where Javon is licensed."
- `primary_city`: "Washington, DC"
- `business_type`: "InsuranceAgency"
- `default_og_image`: a 1200x630 JPG generated at build time from a home photo with the King Health lockup (place in site/assets/og/).
- `google_site_verification`: "" (Search Console HTML tag token; emitted only when filled).
- `gbp_url`: "" (Google Business Profile URL; added to sameAs when filled).
- Per page `seo_title` and `seo_description` for every page (22 core + Wave 2 pages + articles), written now.

## B. Page level tags (every page)
- Unique `<title>` of 60 characters or fewer, pattern "<Topic> | King Health" with locality on the money pages, for example "Medicare Plans in Washington DC and New Jersey | King Health". Home: "King Health | Independent Insurance Advisor, Washington DC and New Jersey".
- Unique meta description of 150 to 160 characters, written in the house voice, with the service and the area, ending with a reason to call. No numerals except where unavoidable in a brand name (the copy rule applies to visible copy; meta may not contain dashes either).
- `<link rel="canonical">` (absolute, from base_url).
- Open Graph and Twitter card tags (title, description, url, image, site_name, type: website or article).
- `<html lang="en-US">`, `<meta name="viewport">` already present; theme-color meta from the signature theme.
- Exactly one h1 per page (verify; fix any page with zero or two).
- Every content image has meaningful alt (already true, verify), width and height attributes to prevent layout shift, and loading="lazy" below the fold; the hero poster or LCP image gets fetchpriority="high" and is not lazy.
- Fonts: preconnect to fonts.googleapis.com and fonts.gstatic.com, display=swap.

## C. Structured data (JSON-LD, one script per page, validated)
- Every page: `Organization` + `WebSite` (with name, url, logo, sameAs from site.social and seo.gbp_url, contactPoint with telephone and email).
- Home and Contact: `InsuranceAgency` (subtype of LocalBusiness) with name, url, logo, image, telephone, email, priceRange omitted, areaServed listing each service area as a State or City, founder or employee `Person` Javon King with jobTitle "Independent Insurance Advisor", openingHoursSpecification only if hours are structured (otherwise omit), and NO street address unless the client supplies one (service area business). `aggregateRating` is NEVER emitted from placeholders; only from the live review source if one is added later.
- Category and product pages: `BreadcrumbList` (Home > Category > Product) and `Service` (serviceType = the product, provider = the agency, areaServed = service areas).
- Product pages with the three FAQ items: `FAQPage` built from the exact visible Q and A text.
- Blog article: `Article` (headline, description, image, author Person, publisher Organization, mainEntityOfPage). No datePublished while drafts; add only when a real date exists.
- Reviews page: `CollectionPage` only.

## D. Crawl files
- `site/robots.txt`: release build allows all and points to the sitemap; REVIEW build disallows all (so drafts and placeholders never get indexed).
- `site/sitemap.xml`: release build only, every visible page (respecting site.hidden_pages), absolute URLs, lastmod = build date.
- Review build: every page also gets `<meta name="robots" content="noindex,nofollow">`. Release build: index,follow.
- A plain `site/404.html` in the house style with links home and to contact.

## E. Local SEO content (visible, small, within the house voice)
- A "Service areas" line in the footer legal row or contact aside, generated from seo.service_areas: "Serving families and employers across Washington, DC, Maryland, Virginia and New Jersey." Hidden when service_areas is empty.
- Contact page: the same areas as a short list under hours.
- Do NOT generate thin location pages or doorway pages. Recommend real area pages later only with genuine local content.

## F. Release lint additions (release_check.py)
FAIL on: empty base_url, missing or duplicate titles or descriptions, title over 60 or description outside 120 to 165 characters, pages with zero or multiple h1, invalid JSON-LD (parse each block), sitemap listing a hidden or missing page, review build without noindex, release build with noindex.
WARN on: empty gbp_url, empty google_site_verification, service_areas not confirmed.

## G. Verification per site
Build review and release modes. Parse every JSON-LD block as JSON and check required fields; confirm one h1 per page; confirm unique titles and descriptions and their lengths; confirm canonicals; confirm robots and noindex per mode; confirm sitemap content against generated pages and hidden_pages; Lighthouse-style checks with Playwright: no layout shift from images without dimensions, LCP image not lazy. All Wave 1 to 3 tests still pass. Leave the site in REVIEW mode with base_url set to "https://kinghealth.example" as a visible placeholder.

## H. Addendum, real business facts (2026-10-25, overrides A, C and E where they differ)
Source of truth: `BUSINESS_FACTS_KING_HEALTH.json` (already applied to every content.json as site.phone, site.hours, site.hours_structured, site.address, site.legal_name, site.social, reviews.profile_url).
- `seo.base_url`: "https://kinghealthdirect.com" (his current domain; `_comment`: "He may move to a different website later. Change this one value and rebuild."). The site stays in REVIEW mode (noindex) so this is safe.
- `seo.primary_city`: "Newark, NJ". `seo.service_areas`: ["Newark, NJ", "New Jersey", "Washington, DC", "Maryland", "Virginia"]; `seo.service_areas_confirmed`: ["Newark, NJ", "New Jersey"]; WARN in release lint while any listed area is unconfirmed. Visible line: "Serving families and employers in Newark and across New Jersey, Washington, DC, Maryland and Virginia."
- `seo.gbp_url`: the Google profile URL from reviews.profile_url (https://www.google.com/maps?cid=9265971853131828090). Add to sameAs with Facebook and Instagram.
- `InsuranceAgency` now INCLUDES `address` (PostalAddress: streetAddress "Elizabeth Avenue", addressLocality "Newark", addressRegion "NJ", postalCode "07112", addressCountry "US"), `geo` (40.7072735, -74.2028628), `hasMap` = gbp_url, and `openingHoursSpecification` from site.hours_structured (Mo to Fr 08:30 to 18:00, Sa 08:30 to 17:00).
- No email is published: omit email everywhere in JSON-LD (contactPoint has telephone, contactType "customer service", areaServed, availableLanguage "en").
- Titles: money pages use "in New Jersey and DC" (for example "Medicare Plans in New Jersey and DC | King Health"); home: "King Health | Independent Insurance Advisor in Newark, NJ" (60 chars or fewer). Descriptions mention Newark or New Jersey first.
- Never emit aggregateRating or the 4.9 / 41 reviews figure.
