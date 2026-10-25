# King Health website

The website for King Health LLC (Javon King, independent insurance advisor, Newark NJ), built by Teal Apex Solutions LLC as plain HTML with no framework, so it is fast, stable and inexpensive to host.

## Folders

| Folder | Purpose |
| --- | --- |
| `_build/` | The generator. `content.json` holds every word, link, phone number and setting; `photos.json` maps photos to pages; `hero_slides/` holds the home slideshow masters; `reviews_google.json` holds the Google review snapshot. |
| `site/` | Review build for previewing on this Mac. It is hidden from search engines and refreshes itself after every rebuild. |
| `public/` | Launch build. This is the only folder Cloudflare Pages serves. |
| `brand/` | Logo and emblem masters. |
| `docs/` | Design direction and the search optimization specification. |

## Everyday workflow

1. Edit `_build/content.json` (text, links, hours, license, service areas) or swap photos.
2. Double click `BUILD.terminal`. It rebuilds `site/` for review and `public/` for launch, then runs the checks.
3. Double click `PUSH_TO_GITHUB.terminal`. It shows the changes, asks for approval, commits and pushes. Cloudflare Pages publishes the new version automatically within a minute or two.

## Cloudflare Pages settings

Framework preset: None. Build command: leave empty. Build output directory: `public`. Production branch: `main`.

## Hiding a page

Add its key to `site.hidden_pages` in `_build/content.json` and rebuild. Keys: reviews, join-the-team, blog, terms, carriers, about. Blog and Join the Team are hidden today.

## Before pointing kinghealthdirect.com here

Keep the domain's email (MX) records exactly as they are, so Javon@kinghealthdirect.com keeps working. Change only the website records.
