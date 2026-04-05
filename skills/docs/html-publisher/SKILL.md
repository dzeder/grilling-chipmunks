# HTML Publisher Skill

## Purpose

Publish HTML documentation via Docusaurus for external-facing documentation. Internal docs use MkDocs (see `md-generator`); external docs use Docusaurus for richer interactivity and branding.

## Constraints

- **Docusaurus** is the only supported static site generator for external docs.
- **MDX format** -- pages are written in MDX (Markdown + JSX) for Docusaurus compatibility.
- **Versioning** -- documentation is versioned alongside product releases.
- **SEO** -- every page includes meta title, description, and Open Graph tags.
- **Sidebar** -- navigation is auto-generated from directory structure with manual overrides via `sidebars.js`.
- **Deployment** -- published to S3 + CloudFront. No direct server hosting.
- **Assets** -- images and static files stored in `static/` directory.

## Supported Operations

- `generate_page` -- Generate an MDX page for Docusaurus.
- `build` -- Run `docusaurus build` to generate static HTML.
- `publish` -- Deploy built site to S3 + CloudFront.
- `validate` -- Validate MDX syntax and link integrity.

## Inputs

- `page_title`: Page title.
- `content`: MDX content string.
- `slug`: URL slug for the page.
- `category`: Documentation category (guides, api, tutorials).
- `operation`: The operation to perform.

## Outputs

- `file_path`: Path to the generated MDX file.
- `build_status`: Build success or failure.
- `publish_url`: Public URL after publishing.
- `validation_errors`: Any issues found during validation.

## Error Handling

Build failures return the full Docusaurus error output. Broken links are detected during the build step. See `error-codes.md` for details.

## Dependencies

- Node.js 20+ and Docusaurus CLI.
- `s3-manager` skill for deployment to S3.
- `cdk-deploy` skill for CloudFront distribution management.
