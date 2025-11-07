# SVG Extractor

A Python tool to extract SVG elements from HTML markup. Perfect for processing large blocks of HTML and extracting all embedded SVG graphics with intelligent context detection.

## Features

- 🎯 Extract all SVG elements from HTML markup
- 🧠 **Smart Context Detection** - Automatically names SVGs based on their usage (buttons, links, labels)
- 💾 Save SVGs to individual files with meaningful names
- 📋 **Code Blocks Export** - Generate a list of SVG code blocks with descriptive comments
- ⚡ **Inline Processing** - Paste HTML directly or pipe from clipboard (no files needed!)
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

**Extract from a file:**

```bash
python svg_extractor.py input.html
```

This will:
- Extract all SVG elements
- Save them to the `output/` directory as `svg_001.svg`, `svg_002.svg`, etc.
- Print a summary of extracted SVGs

**🆕 Extract from inline HTML (no file needed!):**

Simply paste your HTML and press `Ctrl+D` (Linux/Mac) or `Ctrl+Z` then `Enter` (Windows):

```bash
python svg_extractor.py --with-context
# Paste your HTML markup here
# Press Ctrl+D when done
```

**Or pipe HTML directly:**

```bash
# Using echo
echo '<button>Search<svg>...</svg></button>' | python svg_extractor.py --with-context

# Using here-doc (multiline)
python svg_extractor.py --with-context << 'EOF'
<div>
  <button>Download
    <svg width="24" height="24">...</svg>
  </button>
</div>
EOF

# Copy from clipboard (macOS)
pbpaste | python svg_extractor.py --code-blocks icons.txt

# Copy from clipboard (Linux with xclip)
xclip -o | python svg_extractor.py --with-context
```

### 🆕 Context-Aware Extraction (Recommended!)

Extract SVGs with intelligent naming based on their usage:

```bash
python svg_extractor.py input.html --with-context
```

This will:
- Analyze each SVG's parent elements (buttons, links, etc.)
- Extract button text, aria-labels, and other contextual information
- Save files with meaningful names like `search.svg`, `home.svg`, `patients.svg`
- Add HTML comments describing the SVG's purpose

**Example Output:**
```
SVG #1: search
  Purpose: Used in button labeled "Search"
  Parent: button
  Text: "Search"

Saved: output/search.svg
```

### 🆕 Code Blocks Export

Export all SVGs as a single text file with descriptive comments:

```bash
python svg_extractor.py input.html --code-blocks icons.txt
```

**Output Format:**
```
# Icon 1: search
# Purpose: Used in button labeled "Search"

<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24">
  <!-- SVG content -->
</svg>

--------------------------------------------------------------------------------

# Icon 2: home
# Purpose: Used in link labeled "Home" linking to /dashboard
# Attributes: href=/dashboard

<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16">
  <!-- SVG content -->
</svg>
```

### Advanced Options

**Specify output directory:**
```bash
python svg_extractor.py input.html -o my_svgs --with-context
```

**Custom filename prefix (without context):**
```bash
python svg_extractor.py input.html -p icon
# Creates: icon_001.svg, icon_002.svg, etc.
```

**Export as JSON:**
```bash
python svg_extractor.py input.html --json output.json --with-context
```

**Summary only (don't save files):**
```bash
python svg_extractor.py input.html --summary-only --with-context
```

**Quiet mode:**
```bash
python svg_extractor.py input.html --quiet
```

## How Context Detection Works

When using `--with-context`, the tool intelligently analyzes each SVG's surrounding HTML to determine its purpose:

1. **Checks Parent Elements**: Looks at buttons, links, and other parent containers
2. **Extracts Text Content**: Finds button labels, link text, and adjacent text
3. **Reads Attributes**: Checks `aria-label`, `title`, `data-*` attributes
4. **Generates Names**: Creates clean, descriptive filenames from the context

**What it looks for:**
- Button text: `<button>Search</button>` → `search.svg`
- Link text: `<a href="/home">Home</a>` → `home.svg`
- Aria labels: `aria-label="Close dialog"` → `close_dialog.svg`
- Data attributes: `data-sidebar-item="settings"` → `settings.svg`
- Adjacent text: Nearby `<span>` or `<label>` elements

## Examples

### Example 1: Basic Extraction

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

Saved 3 SVG files to 'output/' directory
  - output/svg_001.svg
  - output/svg_002.svg
  - output/svg_003.svg
```

### Example 2: Context-Aware Extraction

```bash
python svg_extractor.py test_input.html --with-context
```

Output:
```
============================================================
SVG EXTRACTION SUMMARY (WITH CONTEXT)
============================================================
Total SVGs found: 3
============================================================

SVG #1: search
  Purpose: Used in button labeled "Search"
  Parent: button
  Text: "Search"

SVG #2: home
  Purpose: Used in link labeled "Home" linking to /dashboard
  Parent: link
  Text: "Home"

SVG #3: patients
  Purpose: Used in link labeled "Patients" linking to /patients
  Parent: link
  Text: "Patients"

Saved 3 SVG files with contextual names to 'output/'
  - output/search.svg
  - output/home.svg
  - output/patients.svg
```

## Python API

You can also use the SVGExtractor class in your Python code:

### Basic Usage

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

### Context-Aware Extraction

```python
from svg_extractor import SVGExtractor

# Read HTML content
with open('input.html', 'r') as f:
    html_content = f.read()

# Create extractor
extractor = SVGExtractor(html_content)

# Extract with context
svg_contexts = extractor.extract_svgs_with_context()

# Print context information
for item in svg_contexts:
    context = item['context']
    print(f"Name: {context['name']}")
    print(f"Purpose: {context['purpose']}")
    print(f"Parent: {context['parent_type']}")
    print()

# Save with contextual names
saved_files = extractor.save_svgs_with_context('output')
print(f"Saved: {saved_files}")

# Export as code blocks
output_text = extractor.export_as_code_blocks('icons.txt')
print("Exported code blocks")
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
