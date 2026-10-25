---
title: King Health website, GoHighLevel setup guide
created: 2026-10-25
owner: Teal Apex Solutions LLC (builder) for King Health LLC (client)
type: runbook
status: current
---

# King Health website: GoHighLevel setup guide

This guide explains the ways the King Health website can work with GoHighLevel (GHL), what each one involves, and step by step instructions. GoHighLevel changes its menus often, so where a menu name is given, confirm it against GoHighLevel's own help center (help.gohighlevel.com) before relying on it.

## What you are working with

- The site is 25 plain HTML pages plus folders of styles, scripts and photos. The finished version for visitors is the `public/` folder.
- The pages link to each other and to their photos with **relative paths** (for example `media/photos/medicare.jpg`). This matters, because some GoHighLevel options require full web addresses instead.
- The site is already live on Cloudflare Pages at `https://king-health.pages.dev` and updates automatically from GitHub.

## Your three options at a glance

| Option | How it works | Effort | Main limits |
| --- | --- | --- | --- |
| A. Keep the site on Cloudflare and connect GoHighLevel into it (recommended) | The site stays where it is; GoHighLevel forms, calendar, reviews and chat are embedded into it | Low | None significant; this is how the site was designed |
| B. Rebuild each page inside the GoHighLevel website builder | Each page's HTML is pasted into a Custom Code element on a blank GHL page | High | 25 pages to paste and repaste after every change; styles, scripts and photos must be hosted elsewhere; GHL wraps each page in its own code, so navigation and effects may need rewiring |
| C. GoHighLevel WordPress hosting, Custom HTML Pages | Upload each prebuilt `.html` file to a HighLevel hosted WordPress site | Medium to high | According to GoHighLevel's help article: one `.html` file per upload, 5 MB maximum each, no folder or ZIP upload yet, and images, CSS and JavaScript must use absolute URLs (full web addresses), not relative paths; requires HighLevel WordPress hosting |

Option A keeps one source of truth, costs nothing extra, and lets GoHighLevel do what it is good at (leads, automations, reviews, calendars). Options B and C are possible but turn every future edit into manual repasting.

## Option A (recommended): connect GoHighLevel to the Cloudflare site

### A1. Lead forms into GoHighLevel

**Status (2026-10-25): connected.** The site's own "Request a consultation" form now posts to a GoHighLevel inbound webhook. The published workflow "Website Lead: King Health site form (test)" creates the contact (source Website Lead), tags it `website lead`, creates an opportunity in 1.1 Medicare Marketing Leads at New Lead (unassigned), and emails Javon@kinghealthdirect.com. Details are in section 6a of `AI_HANDOFF_KING_HEALTH.md`. The two approaches below remain for reference:

**Using a GoHighLevel form embed (most complete)**
1. In GoHighLevel, build the form exactly as described in `GHL_FORM_SETUP.md` in this project (field keys, option lists and consent wording are listed there).
2. Open the form, choose the option to integrate or embed it, and copy the embed code.
3. Give the embed code to whoever maintains the site build. It is pasted once in `_build/build.py` (the `universal_form` function) and the site is rebuilt, which places it on every page.
4. Rebuild and push (see `README.md`). Test as described at the end of `GHL_FORM_SETUP.md`.

**Using the site's own form with a GoHighLevel webhook (simpler)**
1. In GoHighLevel, create a workflow with an Inbound Webhook trigger and copy the webhook URL it gives you.
2. Set `ghlWebhookUrl` in `_build/src/site.js` to that URL. The Join the Team form uses `ghlRecruitWebhookUrl`.
3. Rebuild and push, submit a test entry, and confirm the contact appears in GoHighLevel. Then map the fields in the workflow.

### A2. Google reviews widget

1. Connect the Google Business Profile in GoHighLevel. As of 2026-10-25 the Google Business Profile tile under Settings, Integrations was not yet connected for the King Health sub-account, which is why GoHighLevel's existing review widgets showed zero reviews. The person who manages the Google listing must sign in and approve this.
2. Confirm reviews appear under Reputation, Reviews.
3. Under Reputation, Widgets, create or edit a widget and copy its embed code.
4. Add it to the site build as a `widget_embed` value inside `reviews` in `_build/content.json`, rebuild and push. The live widget then replaces the review snapshot on the Home and Reviews pages automatically.
5. The "Share your experience" button already links to the King Health Google review link found in GoHighLevel's Reputation settings: `https://g.page/r/CXrLsKROWJeAEAI/review`.

### A3. Calendar, chat and call tracking (optional)

- **Calendar:** copy a GoHighLevel calendar's embed code and ask the maintainer to place it on the Contact page.
- **Chat widget:** GoHighLevel's chat widget gives a script snippet; it is added once to the site template so it appears on every page. The floating Google rating badge also sits in the lower right corner, so the maintainer should move one of them so they do not overlap.
- **Call tracking:** a GoHighLevel tracking number can replace the displayed phone number in `site.phone` in `content.json` if the owner wants to measure calls from the website.

### A4. Pointing a domain at the Cloudflare site

1. In Cloudflare, open Workers and Pages, the `king-health` project, then Custom domains, and add the domain.
2. Follow Cloudflare's instructions for the DNS records. If the domain's DNS is managed elsewhere (for example GoDaddy), add the records Cloudflare shows there.
3. **Do not change the domain's email (MX, SPF, DKIM, DMARC) records.** Change only the website records, so email keeps working.
4. If the domain currently points at a GoHighLevel funnel or website, decide which GoHighLevel pages still matter and move them to a subdomain (for example `go.yourdomain.com`) under GoHighLevel's domain settings before switching the main domain.
5. Update `seo.base_url` in `_build/content.json` to the new domain, rebuild and push.

## Option B: rebuild pages in the GoHighLevel website builder

Only choose this if the site must live entirely inside GoHighLevel.

1. Upload every photo in `public/media/` and `public/brand/` to GoHighLevel Media Storage and record each file's full web address.
2. Host `public/assets/site.css` and `public/assets/site.js` somewhere they have a full web address (GoHighLevel media storage may not serve these file types reliably; test first).
3. In each HTML file, replace every relative path (photos, styles, scripts, links between pages) with the full addresses from steps 1 and 2 and the GHL page paths you plan to use.
4. In GoHighLevel, create a website with one blank page per HTML file, add a Custom Code element to each, and paste the page's content.
5. Publish, then check every page, link, form and photo on desktop and phone.
6. Repeat steps 3 to 5 for every future content change.

## Option C: GoHighLevel WordPress, Custom HTML Pages

1. Confirm the account has HighLevel WordPress hosting and a mapped domain.
2. Rewrite all relative paths to absolute URLs as in Option B, steps 1 to 3.
3. Upload each `.html` file one at a time from the WordPress site's Pages area (5 MB limit each).
4. To change a page, upload a new version of that file; GoHighLevel keeps the original URL and settings.

## Before going live anywhere

- Forms (A1) are connected through the webhook. Decide whether to keep, rename or extend the test workflow (assignment, SMS alert) before launch.
- Fill in the Terms page effective date and governing state, and have an attorney review it.
- Replace the stock About page portrait with a real photo of Javon.
- Confirm WhatsApp is active on (973) 524-7188, or provide the WhatsApp number.

## Sources

- GoHighLevel help center, WordPress Custom HTML Pages: https://help.gohighlevel.com/support/solutions/articles/155000006571
- This project's `GHL_FORM_SETUP.md` (form fields, option lists, consent wording and testing).
