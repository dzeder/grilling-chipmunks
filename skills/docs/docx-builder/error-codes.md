# DOCX Builder Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `DXB-001` | Template not found | Verify template name and check `templates/` directory. |
| `DXB-002` | Missing required content placeholder | Provide all required content sections for the template. |
| `DXB-003` | Content exceeds section limit | Reduce content length for the specified section. |
| `DXB-004` | Image missing alt text | Add alt text to all images for accessibility. |
| `DXB-005` | Generated file exceeds 10 MB | Reduce content or compress images. |
| `DXB-006` | Invalid metadata | Check author, subject, and keywords format. |
| `DXB-007` | python-docx error | Check python-docx installation and template file integrity. |
| `DXB-008` | Table missing header row | All tables must have a defined header row. |
