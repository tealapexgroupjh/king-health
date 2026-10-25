# King Health: GoHighLevel form setup

This one page sheet describes how to build the GoHighLevel form that matches the universal form on every page of the King Health site, and how to place it in each page.

## Field keys and order

Create these fields in GoHighLevel in this order. The query key column is the custom field key (or standard field) the site and the bridge script use, and it must match exactly.

| Order | Label on the site | Query key | Type | Required |
| --- | --- | --- | --- | --- |
| A | First name | `first_name` | Standard: First Name | Yes |
| A | Last name | `last_name` | Standard: Last Name | Yes |
| B | Phone | `phone` | Standard: Phone | Yes |
| B | Email | `email` | Standard: Email | Yes |
| C | How can we help? | `category` | Custom: Single option dropdown | Yes |
| D | Coverage of interest | `coverage` | Custom: Single option dropdown | Yes, when shown |
| E | Anything you would like us to know | `message` | Custom: Multi line text | No |
| F | Contact consent | `consent_contact` | Checkbox (or GoHighLevel terms and conditions element) | Yes |
| F | SMS consent | `consent_sms` | Checkbox, unchecked by default | No |
| G | Honeypot | `company_website` | Hidden or omitted (GoHighLevel has its own spam protection) | No |

## Option lists (copy exactly, including capitalization)

`category`: Senior Benefits, Individual Benefits, Group Benefits, Retirement, General Inquiry

`coverage`, one list per category, each ending with "All or unsure":

- Senior Benefits: Medicare, Final Expense, Ancillary, All or unsure
- Individual Benefits: Individual Health, Whole Life, Term Life, Ancillary, Dental and Vision, All or unsure
- Group Benefits: Group Health, Group Life, Group Ancillary, Group Dental and Vision, All or unsure
- Retirement: Annuities, Indexed Universal Life, All or unsure
- General Inquiry: no coverage field

## Conditional logic (preferred)

GoHighLevel conditional logic shows a field based on another field's answer. Build four separate coverage dropdowns rather than one:

1. Create `coverage_senior`, `coverage_individual`, `coverage_group` and `coverage_retirement`, each holding its own list above.
2. On each one, add the rule: show this field when `category` is equal to its category (for example, show `coverage_senior` when `category` is Senior Benefits).
3. With General Inquiry selected, none of them is shown.
4. In the workflow that receives the submission, add an action that copies whichever of the four has a value into one contact field named `coverage`, so reporting stays in one column.

When this approach is used, give each of the four dropdowns the query key `coverage` if GoHighLevel allows a shared key; if it does not, the bridge's `coverage` parameter will prefill nothing and the visitor simply chooses. The `category` preset still applies.

## Fallback: one grouped dropdown

If conditional logic is not available on the plan, use one dropdown with key `coverage` and these options, written so each is unambiguous on its own:

Senior Benefits: Medicare; Senior Benefits: Final Expense; Senior Benefits: Ancillary; Senior Benefits: All or unsure; Individual Benefits: Individual Health; Individual Benefits: Whole Life; Individual Benefits: Term Life; Individual Benefits: Ancillary; Individual Benefits: Dental and Vision; Individual Benefits: All or unsure; Group Benefits: Group Health; Group Benefits: Group Life; Group Benefits: Group Ancillary; Group Benefits: Group Dental and Vision; Group Benefits: All or unsure; Retirement: Annuities; Retirement: Indexed Universal Life; Retirement: All or unsure; General Inquiry

Keep `category` as its own required field. With this fallback, the URL preset fills `category` reliably. It fills `coverage` only if the option text equals the passed value, so either accept that the visitor confirms coverage, or rename the options to the plain names in the lists above and rely on the category to tell the duplicate Ancillary entries apart.

## Consent wording (paste as written)

Contact consent: I agree that King Health may contact me about my request by phone, email or text message.

SMS consent: By checking this box, I agree to receive text messages from King Health about my inquiry, including follow up and appointment reminders, at the phone number provided. Message frequency varies. Message and data rates may apply. Reply STOP to opt out or HELP for help. Consent to receive text messages is not a condition of purchase. See our privacy policy. (Link "privacy policy" to the site's privacy.html page.)

## Pasting the embed into each page

1. In GoHighLevel, open the form, choose Integrate, and copy the embed code (an `iframe` followed by a `script` tag).
2. On every page, find the `div` with class `kh-form-slot` and the HTML comment that begins `GOHIGHLEVEL FORM EMBED SLOT`. Paste the embed code directly below that comment, inside the same `div`. Do not delete the native form below it; it hides itself automatically once an iframe is present and returns if the embed is ever removed.
3. Because the site is generated, the durable place to paste is the build, not each HTML file: in `_build/build.py`, the `universal_form` function holds the slot, so pasting the embed there once and re-running `python3 _build/build.py` places it on all twenty two pages. Pasting into individual HTML files also works, but the next build overwrites it.
4. If the site goes live with the native form instead of the embed, set `ghlWebhookUrl` in `site/assets/site.js` (source: `_build/src/site.js`) to the GoHighLevel inbound webhook URL. While it is empty the form runs in demo mode: it validates, shows the success state and notes that nothing was transmitted.

## How the URL preset works

Each page's form carries `data-preset-category` and `data-preset-coverage`, for example Senior Benefits and Medicare on medicare.html, or Senior Benefits and All or unsure on senior-benefits.html. Home, About and Contact carry no preset.

The site resolves the effective preset in this order:

1. URL parameters `?category=` and `?coverage=` on the page address. These accept the option text or a lowercase, hyphenated form, so `?category=retirement&coverage=annuities` and `?category=Retirement&coverage=Annuities` behave the same. They are useful for ads and emails.
2. On the shared Ancillary page, `?from=senior` or `?from=individual` sets the category, the second navigation bar and the banner kicker. Senior is the default. Group ancillary has its own page, group-ancillary.html, and `?from=group` forwards there.
3. Otherwise, the page's own data attributes apply.

The `kh-ghl-bridge` script (`assets/kh-ghl-bridge.js`) then appends the resolved values to the GoHighLevel iframe `src` as `category` and `coverage` parameters. GoHighLevel prefills a field from a URL parameter whose name matches the field's query key, so the embedded form opens with the same selections. The bridge also watches the slot, so it works when GoHighLevel's script inserts the iframe after the page loads.

## Test after setup

Open medicare.html and confirm the embedded form shows Senior Benefits and Medicare. Open group-ancillary.html and confirm Group Benefits and Group Ancillary. Choose General Inquiry and confirm no coverage field shows. Submit a test entry and confirm the contact, both consent values and the `coverage` value land in GoHighLevel.
