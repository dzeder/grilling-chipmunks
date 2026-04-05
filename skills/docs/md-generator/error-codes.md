# Markdown Generator Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `MDG-001` | Title is empty | Provide a non-empty title. |
| `MDG-002` | No sections provided | Add at least one section to the document. |
| `MDG-003` | Invalid heading level | Heading level must be between 1 and 6. |
| `MDG-004` | Output path outside docs/ | Output path must be relative to the docs/ directory. |
| `MDG-005` | Front matter YAML invalid | Check title and description for special YAML characters. |
| `MDG-006` | Broken internal link | Linked document not found at the specified relative path. |
| `MDG-007` | Image not found in docs/assets/ | Ensure referenced images exist in the assets directory. |
| `MDG-008` | Code block missing language | Specify language after opening triple backticks. |
