---

## 🌐 Source-specific Scraping Rules

### 🛒 IKEA

- **Search URL pattern**:  
  `https://www.ikea.com/pl/pl/search/?q=QUERY`
  
- **Search behavior**:  
  Loads search results via standard HTML (no JavaScript required).

- **Selector to extract**:
  - Title: `.pip-header-section__title`
  - Link: Product cards have `<a>` with `href` inside `.pip-product-compact`
  - Description: If available, extract from `.pip-product-compact__rating-text` or skip.

- **Result normalization**:
  - Prefix relative URLs with `https://www.ikea.com`
  - Clean up whitespace and special characters from product titles

- **Dummy Data Rules**:
  - Use real product series (e.g., BILLY, MALM, POÄNG)
  - Include 3 variants per product series
  - Follow IKEA's URL pattern: `/pl/pl/p/PRODUCT-NAME-MODEL/`
  - Use real model numbers (e.g., 00263850 for BILLY)
  - Include descriptive snippets about product features
  - Group related products together (e.g., all BILLY variants)

### 📘 Manualslib

- **Search URL pattern**:  
  `https://www.manualslib.com/QUERY_FIRST_LETTER/QUERY.html`  
  (e.g., search for "Canon" → `https://www.manualslib.com/C/Canon.html`)

- **Search behavior**:  
  Loads pure HTML, no JavaScript required.

- **Selector to extract**:
  - Title: `.mdl-left h3 a`
  - Link: `href` from inside those `<a>` tags
  - Description: Use sibling `<div>` or skip if not available

- **Result normalization**:
  - Ensure links are full (prefix with `https://www.manualslib.com` if relative)
  - Use `query[0].upper()` to determine the letter folder in the URL

- **Dummy Data Rules**:
  - Use real product brands (e.g., Canon, Samsung, Sony)
  - Include 3 types of manuals per product:
    1. User Manual (complete documentation)
    2. Quick Start Guide (basic setup)
    3. Troubleshooting/Safety Guide
  - Follow ManualLib's URL pattern: `/BRAND-FIRST-LETTER/BRAND-PRODUCT.html`
  - Use real model numbers (e.g., EOS R5, SM-G991B)
  - Include descriptive snippets about manual content
  - Group related manuals together (e.g., all Canon EOS R5 guides)

## Test Mode Guidelines
- Each scraper should implement a test mode
- Test mode should return realistic dummy data
- Dummy data should follow the same structure as real data
- Include multiple product series/variants
- Use real URLs and model numbers
- Group related items together
- Include descriptive snippets
- Follow the source website's URL patterns
- Maintain consistent data format across all scrapers
