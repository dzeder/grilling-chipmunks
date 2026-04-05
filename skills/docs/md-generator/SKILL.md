# Markdown Generator Skill

## Purpose

Generate markdown documentation files in MkDocs-compatible format. All internal documentation at Ohanafy uses MkDocs with Material theme. This skill ensures consistent formatting, navigation structure, and metadata.

## Constraints

- **MkDocs format** -- all markdown follows MkDocs Material theme conventions.
- **Front matter required** -- every document includes YAML front matter with title, description, and tags.
- **Navigation**: Documents must be registered in `mkdocs.yml` nav section.
- **Admonitions**: Use MkDocs admonition syntax for notes, warnings, and tips.
- **Code blocks**: Always specify language for syntax highlighting.
- **Links**: Use relative paths for internal links. Never use absolute URLs for internal docs.
- **Images**: Store in `docs/assets/` with descriptive filenames.

## Supported Operations

- `generate` -- Generate a new markdown document.
- `update` -- Update an existing markdown document section.
- `validate` -- Validate markdown against MkDocs standards.
- `generate_nav` -- Generate navigation entry for mkdocs.yml.

## Inputs

- `title`: Document title.
- `description`: Brief description for front matter.
- `sections`: List of section headings and content.
- `tags`: List of tags for categorization.
- `output_path`: Relative path under `docs/`.

## Outputs

- `markdown_content`: The generated markdown string.
- `file_path`: Path where the document was written.
- `nav_entry`: Navigation entry for mkdocs.yml.
- `validation_errors`: Any formatting issues found.

## Error Handling

Validation errors list specific line numbers and issues. See `error-codes.md` for details.

## Dependencies

- MkDocs and mkdocs-material must be installed for local preview.
