# Webscraping Guide for Solomon-Sophia (S.IO)

This guide explains how to use the webscraping functionality to collect spiritual texts and add them to your database.

## Overview

The webscraping system can collect texts from various online sources including:

- **Bible**: Bible Gateway, Bible Hub
- **Quran**: Quran.com, Tanzil.net  
- **Hindu Texts**: Bhagavad Gita, Upanishads
- **Buddhist Texts**: Dhammapada, Buddhist suttas

## Quick Start

### Basic Scraping

Scrape default texts (Bible, Quran, Bhagavad Gita):

```bash
solomon scrape
```

### Scrape Specific Text Types

```bash
solomon scrape --types bible quran --verbose
```

### Scrape with Custom Parameters

```bash
solomon scrape \
  --types bible \
  --bible-books genesis exodus matthew john \
  --bible-versions NIV ESV KJV \
  --min-quality 0.5 \
  --max-texts 50 \
  --output scraped_data.json
```

## CLI Commands

### `solomon scrape`

Main scraping command with extensive options:

**Text Type Options:**
- `--types`: Text types to scrape (bible, quran, bhagavad_gita, upanishads, dhammapada)

**Bible Options:**
- `--bible-books`: Specific Bible books to scrape
- `--bible-versions`: Bible versions (NIV, ESV, KJV, etc.)

**Quran Options:**
- `--quran-surahs`: Specific surahs to scrape (numbers)
- `--arabic/--no-arabic`: Include/exclude Arabic text

**Hindu Text Options:**
- `--gita-chapters`: Bhagavad Gita chapters to scrape
- `--sanskrit/--no-sanskrit`: Include/exclude Sanskrit text

**Buddhist Text Options:**
- `--dhammapada-chapters`: Dhammapada chapters to scrape
- `--pali/--no-pali`: Include/exclude Pali text

**Quality & Output Options:**
- `--min-quality`: Minimum quality score (0.0-1.0)
- `--max-texts`: Maximum texts per type
- `--output`: Export scraped data to JSON file
- `--verbose`: Detailed output

### `solomon scrape-status`

Check current database status:

```bash
solomon scrape-status
```

Shows:
- Total texts in database
- Texts by type
- Recent additions
- Supported text types

### `solomon scrape-specific`

Scrape based on detailed configuration file:

```bash
solomon scrape-specific examples/scraping_config.json --verbose
```

## Configuration Files

For complex scraping scenarios, use JSON configuration files.

### Example Configuration

```json
{
  "requests": [
    {
      "text_type": "bible",
      "passage": {
        "book": "genesis",
        "chapter": 1,
        "verse_start": 1,
        "verse_end": 10,
        "version": "NIV"
      }
    },
    {
      "text_type": "quran",
      "verses": {
        "surah": 1,
        "verse_start": 1,
        "verse_end": 7,
        "translations": ["en.sahih"],
        "include_arabic": true
      }
    }
  ]
}
```

### Configuration Structure

Each request in the `requests` array should have:

**Bible Requests:**
```json
{
  "text_type": "bible",
  "passage": {
    "book": "book_name",
    "chapter": 1,
    "verse_start": 1,
    "verse_end": 10,
    "version": "NIV"
  }
}
```

**Quran Requests:**
```json
{
  "text_type": "quran", 
  "verses": {
    "surah": 1,
    "verse_start": 1,
    "verse_end": 7,
    "translations": ["en.sahih", "en.pickthall"],
    "include_arabic": true
  }
}
```

**Bhagavad Gita Requests:**
```json
{
  "text_type": "bhagavad_gita",
  "verses": {
    "chapter": 2,
    "verse_start": 1,
    "verse_end": 10,
    "include_sanskrit": true,
    "include_commentary": false
  }
}
```

## Text Processing

All scraped texts undergo automatic processing:

### Quality Assessment
- **Length validation**: Minimum word count
- **Structure validation**: Proper verse/chapter structure  
- **Content quality**: Complete sentences, proper formatting
- **Metadata completeness**: Author, translator, source info
- **Source reliability**: Trusted source verification

### Theme Extraction
Automatic identification of spiritual themes:
- Love, compassion, mercy
- Wisdom, knowledge, understanding
- Faith, belief, devotion
- Peace, tranquility
- Justice, righteousness
- And many more...

### Language Detection
- Confidence scoring for declared language
- Support for Hebrew, Arabic, Sanskrit, Greek, Latin, English
- Unicode script detection

### Text Enhancement
- HTML tag removal
- Whitespace normalization
- Punctuation standardization
- Copyright notice removal
- URL and email removal

## Supported Sources

### Bible Sources
- **Bible Gateway** (biblegateway.com)
  - Multiple versions (NIV, ESV, KJV, etc.)
  - Verse-by-verse scraping
  - Chapter-level scraping

- **Bible Hub** (biblehub.com)
  - Original language texts
  - Interlinear translations

### Quran Sources
- **Quran.com**
  - Arabic original text
  - Multiple English translations
  - Verse-by-verse access

- **Tanzil.net**
  - High-quality Arabic text
  - Academic standard

### Hindu Text Sources
- **Holy Bhagavad Gita** (holy-bhagavad-gita.org)
  - Sanskrit original
  - English translations
  - Commentary texts

- **Sacred Texts** (sacred-texts.com)
  - Upanishads collection
  - Historical translations

### Buddhist Text Sources
- **Access to Insight** (accesstoinsight.org)
  - Dhammapada translations
  - Pali original texts

- **SuttaCentral** (suttacentral.net)
  - Comprehensive sutta collection
  - Multiple languages

## Best Practices

### Respectful Scraping
- Built-in delays between requests
- Respectful of robots.txt
- User-agent rotation
- Error handling and retries

### Data Quality
- Set appropriate `--min-quality` threshold (0.3-0.8)
- Review scraped data before analysis
- Use `--verbose` for debugging
- Export data for backup

### Performance
- Start with small batches
- Use specific text types rather than scraping everything
- Monitor database size
- Regular cleanup of low-quality texts

## Troubleshooting

### Common Issues

**Connection Errors:**
- Check internet connection
- Some sources may be temporarily unavailable
- Use `--verbose` to see detailed error messages

**No Texts Scraped:**
- Check if source website structure changed
- Verify text type spelling
- Try different quality threshold

**Database Errors:**
- Ensure database is initialized: `solomon init-db`
- Check database connection settings
- Verify write permissions

**Quality Issues:**
- Adjust `--min-quality` parameter
- Review processing statistics
- Check source reliability

### Getting Help

1. Use `--verbose` flag for detailed output
2. Check `solomon scrape-status` for database state
3. Review error messages in output
4. Consult logs for detailed debugging

## Examples

### Scrape Genesis and Matthew
```bash
solomon scrape --types bible --bible-books genesis matthew --bible-versions NIV ESV
```

### Scrape First 5 Quran Surahs
```bash
solomon scrape --types quran --quran-surahs 1 2 3 4 5 --arabic
```

### High-Quality Bhagavad Gita
```bash
solomon scrape --types bhagavad_gita --gita-chapters 1 2 3 --sanskrit --min-quality 0.7
```

### Export All Scraped Data
```bash
solomon scrape --output backup.json --verbose
```

### Specific Verses Configuration
Create `my_config.json`:
```json
{
  "requests": [
    {
      "text_type": "bible",
      "passage": {
        "book": "psalms",
        "chapter": 23,
        "verse_start": 1,
        "verse_end": 6,
        "version": "NIV"
      }
    }
  ]
}
```

Then run:
```bash
solomon scrape-specific my_config.json
```

## Integration with Analysis

Once texts are scraped, use them with Solomon's analysis features:

```bash
# Analyze scraped texts
solomon analyze --text "scraped text content" --type themes

# Use with agents for deeper analysis
solomon analyze --file scraped_data.json --type full --tradition christianity
```

The webscraping system integrates seamlessly with Solomon's AI analysis capabilities, providing a complete pipeline from text collection to spiritual insight.
