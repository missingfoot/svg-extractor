# SVG Extractor

A Python tool to extract SVG elements from HTML markup. Perfect for processing large blocks of HTML and extracting all embedded SVG graphics.

## Features

- 🎯 Extract all SVG elements from HTML markup
- 💾 Save SVGs to individual files
- 📊 Generate detailed reports about extracted SVGs
- 📝 Export SVG information as JSON
- 🔍 View SVG statistics (dimensions, paths, groups, etc.)
- 🚀 Handle large HTML files efficiently

## Installation

1. Clone this repository or download the files

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Extract SVGs from an HTML file:

```bash
python svg_extractor.py input.html
```

This will:
- Extract all SVG elements
- Save them to the `output/` directory as `svg_001.svg`, `svg_002.svg`, etc.
- Print a summary of extracted SVGs

### Advanced Options

**Specify output directory:**
```bash
python svg_extractor.py input.html -o my_svgs
```

**Custom filename prefix:**
```bash
python svg_extractor.py input.html -p icon
# Creates: icon_001.svg, icon_002.svg, etc.
```

**Export as JSON:**
```bash
python svg_extractor.py input.html --json output.json
```

**Summary only (don't save files):**
```bash
python svg_extractor.py input.html --summary-only
```

**Quiet mode:**
```bash
python svg_extractor.py input.html --quiet
```

## Example

Given an HTML file with embedded SVGs:

```bash
python svg_extractor.py test_input.html
```

Output:
```
============================================================
SVG EXTRACTION SUMMARY
============================================================
Total SVGs found: 3
============================================================

SVG #1:
  Dimensions: 24x24
  ViewBox: 0 0 24 24
  Paths: 2
  Groups: 1

SVG #2:
  Dimensions: 16x16
  ViewBox: 0 0 16 16
  Paths: 1
  Groups: 1

SVG #3:
  Dimensions: 24x24
  ViewBox: 0 0 24 24
  Paths: 1
  Groups: 0

Saved 3 SVG files to 'output/' directory
  - output/svg_001.svg
  - output/svg_002.svg
  - output/svg_003.svg
```

## Python API

You can also use the SVGExtractor class in your Python code:

```python
from svg_extractor import SVGExtractor

# Read HTML content
with open('input.html', 'r') as f:
    html_content = f.read()

# Create extractor
extractor = SVGExtractor(html_content)

# Extract SVGs
svgs = extractor.extract_svgs()
print(f"Found {len(svgs)} SVGs")

# Get detailed information
svg_info = extractor.get_svg_info()
for info in svg_info:
    print(f"SVG {info['index']}: {info['width']}x{info['height']}")

# Save to files
saved_files = extractor.save_svgs('output', 'svg')
print(f"Saved: {saved_files}")
```

## Output Format

### Individual SVG Files
Each SVG is saved as a standalone file with proper XML namespace:
```xml
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
  <!-- SVG content -->
</svg>
```

### JSON Export
When using `--json`, you get detailed information about each SVG:
```json
[
  {
    "index": 1,
    "width": "24",
    "height": "24",
    "viewBox": "0 0 24 24",
    "fill": "none",
    "stroke": "currentColor",
    "xmlns": "http://www.w3.org/2000/svg",
    "has_paths": true,
    "path_count": 2,
    "has_groups": true,
    "group_count": 1,
    "svg_content": "<svg>...</svg>"
  }
]
```

## Requirements

- Python 3.6+
- beautifulsoup4
- lxml

## License

MIT License - Feel free to use this tool for any purpose!

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## Tips

1. **Large files**: The tool handles large HTML files efficiently by using BeautifulSoup's streaming parser
2. **Malformed HTML**: BeautifulSoup is forgiving with malformed HTML, so the tool should work even with messy markup
3. **Nested SVGs**: The tool extracts all SVG elements, including nested ones
4. **Inline styles**: All inline styles and attributes are preserved in the extracted SVGs

## Troubleshooting

**No SVGs found?**
- Make sure your HTML file contains `<svg>` tags
- Check that the file encoding is UTF-8

**Import errors?**
- Run `pip install -r requirements.txt` to install dependencies

**File not found?**
- Use the full path to your input file
- Make sure you're in the correct directory
