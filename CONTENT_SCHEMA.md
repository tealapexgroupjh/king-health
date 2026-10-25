# content.json schema (shared contract between the copywriter and the builder)

File: `_build/content.json`. Note: the example values below are from the first draft; the live values in content.json are the source of truth. UTF-8 JSON. Every string obeys
the copy rules in SPEC_KING_HEALTH_V2_SUMMIT.md (no em or en dashes, no numerals except the phone
placeholder, no number words used as counts, no emoji, "we" voice, full sentences, warm and elevated).

```json
{
  "site": {
    "name": "King Health",
    "tagline": "Insurance Advisory You Can Trust",
    "owner": "Javon King",
    "phone": "(555) 010-0100",
    "email": "hello@kinghealth.example",
    "hours": "string",
    "footer_blurb": "one or two sentences",
    "disclosure": "compliance paragraph (coverage subject to underwriting and carrier approval, licensing placeholder lines are rendered by the builder)"
  },
  "home": {
    "hero_heading": "string", "hero_lede": "one sentence",
    "category_intro": {"heading": "string", "text": "string"},
    "why": {"heading": "string", "items": [{"title": "string", "text": "string"}]},
    "about_strip": {"heading": "string", "text": "string"},
    "chart": {"title": "string", "caption": "string"},
    "form_intro": {"heading": "string", "text": "string"}
  },
  "categories": {
    "senior-benefits": {
      "nav_label": "Senior Benefits",
      "title": "page title", "heading": "banner heading", "lede": "one sentence",
      "card_text": "one sentence for the home page card",
      "overview": ["paragraph", "paragraph"],
      "help": {"heading": "string", "items": [{"title": "string", "text": "string"}]},
      "form_intro": {"heading": "string", "text": "string"}
    },
    "individual-benefits": {}, "group-benefits": {}, "retirement": {}
  },
  "products": {
    "medicare": {
      "nav_label": "Medicare",
      "category": "senior-benefits",
      "title": "string", "heading": "string", "lede": "one sentence",
      "card_text": "one sentence for the category page card",
      "at_a_glance": ["paragraph", "paragraph"],
      "designed_for": ["paragraph"],
      "how_it_works": ["paragraph", "paragraph"],
      "faq": [{"q": "string", "a": "string"}, {"q": "string", "a": "string"}, {"q": "string", "a": "string"}]
    }
  },
  "about": {
    "heading": "string", "lede": "string",
    "mission_heading": "Our mission",
    "mission": "the mission statement, a short heartfelt paragraph",
    "story_heading": "string", "story": ["paragraph", "paragraph"],
    "values_heading": "string", "values": [{"title": "string", "text": "string"}],
    "service_note": "string"
  },
  "carriers": {"heading": "string", "lede": "string", "intro": "string", "note": "string",
    "sections": ["Medicare", "Final Expense", "Individual Health", "Individual Life", "Dental and Vision", "Group Benefits", "Retirement"]},
  "contact": {"heading": "string", "lede": "string", "next_heading": "string",
    "next": [{"title": "string", "text": "string"}]},
  "privacy": {"heading": "string", "body": ["paragraph"]},
  "accessibility": {"heading": "string", "body": ["paragraph"]}
}
```

Products keys (all required): medicare, final-expense, ancillary (category "shared": write it for seniors,
individuals and employers), individual-health, whole-life, term-life, dental-vision, group-health,
group-life, group-dental-vision, annuities, indexed-universal-life. Category of each per the sitemap
table in the spec.
