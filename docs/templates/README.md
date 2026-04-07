# Ohanafy HTML Templates

## Brand Template (`demo-template.html`)

The standard Ohanafy 2025 brand template for all external-facing HTML artifacts. Zero dependencies, ~30KB overhead.

### Usage

Copy the template and replace the two placeholders:
- `$title$` — Page title (appears in `<title>` and `.doc-title`)
- `$body$` — Page content (HTML inside `.content` div)

### CSS Variables (Color Palette)

| Variable | Hex | Usage |
|----------|-----|-------|
| `--true-black` | `#000000` | Text, high-contrast elements |
| `--true-white` | `#FFFFFF` | Backgrounds, reversed text |
| `--mellow` | `#E4F223` | Primary accent, CTA highlights (use sparingly) |
| `--cork` | `#F4F2F0` | Neutral backgrounds, cards |
| `--dark-denim` | `#4A5F80` | Secondary UI, headers, borders |
| `--light-denim` | `#B1C7EB` | Subtle accents, hover states |
| `--dark-grey` | `#545454` | Body text, secondary text |

### Typography

Font: **Geist** (loaded from Google Fonts). Falls back to system sans-serif.

### Structure

```html
<div class="brand-header">   <!-- Black banner with mellow/white tagline -->
<div class="doc-nav">         <!-- Dark denim nav bar (customize links) -->
<div class="content">          <!-- White content area, max-width 900px -->
<div class="brand-footer">    <!-- Centered footer with tagline -->
```

### Built-in Classes

- `.time-tracking` — Styled callout box for metrics
- `.highlight-inline` / `<mark>` — Mellow highlight
- `blockquote` — Mellow left-border callout
- `pre` — Cork background code block with denim border
- Tables — Denim headers, cork rows, denim hover

### When to Use

- Integration documentation HTML
- Case study pages
- Demo artifacts
- Any external-facing page that will eventually be hosted on Vercel

### Brand Skill

For full brand guidelines (voice, messaging, logo rules), invoke `/ohanafy-brand` or read `skills/ohanafy/ohanafy-brand/SKILL.md`.
