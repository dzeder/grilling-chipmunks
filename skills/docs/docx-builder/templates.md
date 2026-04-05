# DOCX Builder -- Templates

## Template Structure

Each template is a `.docx` file in `skills/docs/docx-builder/templates/` with placeholder markers that are replaced at generation time.

### Placeholder Syntax

Placeholders use double curly braces: `{{placeholder_name}}`.

### Brand Styling

All templates include pre-configured styles:

| Style Name | Font | Size | Color |
|-----------|------|------|-------|
| Heading 1 | Calibri Bold | 24pt | `#0A2342` |
| Heading 2 | Calibri Bold | 18pt | `#0A2342` |
| Heading 3 | Calibri Bold | 14pt | `#0A2342` |
| Body Text | Calibri | 11pt | `#333333` |
| Accent | Calibri Bold | 11pt | `#E8833A` |
| Caption | Calibri Italic | 9pt | `#666666` |

## Available Templates

### proposal
For client-facing proposals. Sections: title, executive_summary, scope, timeline, pricing.

### report
For internal reports. Sections: title, summary, findings, recommendations, appendix.

### invoice
For billing documents. Sections: client_name, invoice_number, line_items, total, payment_terms.

### letter
For formal correspondence. Sections: recipient, subject, body, closing.

## Creating New Templates

1. Create a `.docx` file with Ohanafy brand styling.
2. Insert placeholder text using `{{placeholder_name}}` syntax.
3. Save to `skills/docs/docx-builder/templates/`.
4. Update this file with the template description and required sections.

## Color Reference

- Primary (navy): `#0A2342` -- RGB(10, 35, 66)
- Accent (orange): `#E8833A` -- RGB(232, 131, 58)
- Body text: `#333333` -- RGB(51, 51, 51)
- Light gray: `#F5F5F5` -- RGB(245, 245, 245)
