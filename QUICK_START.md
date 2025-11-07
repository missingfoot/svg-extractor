# Quick Start Guide

Simple, intuitive commands for SVG extraction.

## Installation

```bash
pip install -r requirements.txt
```

## Your Custom Commands

### 1. Paste HTML → Get List in Terminal

```bash
python svgext.py --inline --list
```

Or shorter:
```bash
python svgext.py --list
# Paste your HTML
# Press Enter twice (empty line) to submit
```

### 2. Read File → Extract as SVG Files

```bash
python svgext.py example.html --svg
```

Files saved to `output/` with smart names like `search.svg`, `download.svg`, etc.

### 3. Read File → Show List in Terminal

```bash
python svgext.py example.html --list
```

### 4. Paste HTML → Save as SVG Files

```bash
python svgext.py --inline --svg
```

## All Options

| Flag | What It Does |
|------|--------------|
| `--inline` | Read from stdin (paste mode) |
| `--list` | Print SVG list to terminal |
| `--svg` | Extract as individual SVG files |
| `--no-context` | Disable smart naming (use svg_001.svg, etc.) |
| `-o DIR` | Output directory (default: output/) |
| `--json FILE` | Save metadata as JSON |
| `--quiet` | Suppress messages |

## Real-World Examples

### Copy HTML from browser, get list

```bash
# Copy HTML snippet from dev tools
python svgext.py --list
# Paste
# Ctrl+D
# Done!
```

### Pipe from clipboard (macOS)

```bash
pbpaste | python svgext.py --list
```

### Pipe from clipboard (Linux)

```bash
xclip -o | python svgext.py --list
```

### Process and save

```bash
echo '<button>Download<svg>...</svg></button>' | python svgext.py --svg -o icons/
```

### Multiline paste

```bash
python svgext.py --inline --list << 'EOF'
<div>
  <button>Save<svg>...</svg></button>
  <button>Cancel<svg>...</svg></button>
</div>
EOF
```

## How Context Detection Works

The tool automatically detects:
- Button text: `<button>Save</button>` → `save.svg`
- Link text: `<a href="/home">Home</a>` → `home.svg`
- Aria labels: `aria-label="Close"` → `close.svg`
- Data attributes: `data-icon="settings"` → `settings.svg`

Disable with `--no-context` for basic numbering.

## Make It Even Shorter (Optional)

### Create an alias (add to ~/.bashrc or ~/.zshrc):

```bash
alias svgext='python /path/to/svgext.py'
```

Then use:
```bash
svgext --inline --list
svgext example.html --svg
```

### Or make it executable:

```bash
chmod +x svgext.py
# Add shebang at top of file (already there!)
```

Then use:
```bash
./svgext.py --inline --list
```

### Or add to PATH:

```bash
# Move to a directory in your PATH
sudo cp svgext.py /usr/local/bin/svgext
sudo chmod +x /usr/local/bin/svgext
```

Then use anywhere:
```bash
svgext --inline --list
svgext myfile.html --svg
```

## Quick Reference

```
# Paste → List
svgext.py --list

# Paste → Files
svgext.py --svg

# File → List
svgext.py file.html --list

# File → Files
svgext.py file.html --svg

# Pipe → List
echo '<svg>...</svg>' | svgext.py --list

# No smart naming
svgext.py file.html --svg --no-context
```

That's it! 🚀
