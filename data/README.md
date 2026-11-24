# IT Helpdesk Sample Knowledge Base

Contains 15 fictional, short IT helpdesk documents for a RAG proof of concept.

- `documents/`: one Markdown file per document.
- `document_manifest.csv`: metadata index.
- Each Markdown file includes YAML front matter with a stable document ID, title, category, last-updated date, and source type.

Suggested ingestion: parse the front matter, chunk the document body, and retain the document ID, title, category, and date as metadata on every chunk. Return the title and ID when citing retrieved content.

All company names, portals, network names, and procedures are illustrative. Replace them with approved customer procedures before production use. These are not authoritative IT or security instructions.
