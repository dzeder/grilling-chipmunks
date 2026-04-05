# DOCX Builder Skill

## Purpose

Generate DOCX documents from templates using python-docx. All external-facing documents follow Ohanafy brand guidelines with consistent styling, colors, and typography.

## Brand Guidelines

- **Primary color**: `#0A2342` (dark navy) -- headings, borders, and emphasis.
- **Accent color**: `#E8833A` (warm orange) -- highlights, callouts, and CTAs.
- **Font**: Calibri for body text, Calibri Bold for headings.
- **Logo**: Placed in the header of every document.
- **Footer**: Includes document title, page number, and "Confidential" marking.

## Constraints

- **python-docx** is the only supported library for DOCX generation.
- **Templates** -- all documents start from a template in `skills/docs/docx-builder/templates/`.
- **No manual formatting** -- all styles are defined in the template. Content is injected programmatically.
- **Accessibility** -- all images must have alt text. Tables must have header rows.
- **File size** -- generated documents must be under 10 MB.

## Supported Operations

- `generate` -- Generate a DOCX from a template with provided content.
- `list_templates` -- List available document templates.
- `validate` -- Validate content against template requirements.

## Inputs

- `template_name`: Name of the template to use.
- `content`: Dictionary of content sections keyed by placeholder name.
- `output_filename`: Desired output filename.
- `metadata`: Document metadata (author, subject, keywords).

## Outputs

- `file_path`: Path to the generated DOCX file.
- `page_count`: Estimated page count.
- `file_size_bytes`: File size in bytes.

## Dependencies

- python-docx library.
- Template files in `skills/docs/docx-builder/templates/`.
