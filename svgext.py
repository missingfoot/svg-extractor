#!/usr/bin/env python3
"""
SVG Extractor - Extract all SVG elements from HTML markup
"""

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup


class SVGExtractor:
    """Extract SVG elements from HTML markup"""

    def __init__(self, html_content):
        """
        Initialize the SVG extractor

        Args:
            html_content (str): The HTML markup to parse
        """
        self.html_content = html_content
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.svgs = []
        self.svg_contexts = []

    def extract_svgs(self):
        """
        Extract all SVG elements from the HTML

        Returns:
            list: List of SVG elements as strings
        """
        svg_elements = self.soup.find_all('svg')
        self.svgs = [str(svg) for svg in svg_elements]
        return self.svgs

    def _get_text_excluding_svg(self, element):
        """
        Extract text from an element while excluding SVG elements and their contents

        Args:
            element: BeautifulSoup element to extract text from

        Returns:
            str: Extracted text with SVG content excluded
        """
        texts = []

        # Recursively walk through all text nodes
        for text_node in element.find_all(string=True, recursive=True):
            # Check if this text node is inside an svg element
            parent = text_node.parent
            inside_svg = False

            while parent:
                if hasattr(parent, 'name') and parent.name == 'svg':
                    inside_svg = True
                    break
                parent = parent.parent

            # Only include text that's not inside an svg
            if not inside_svg:
                text = text_node.strip()
                if text:
                    texts.append(text)

        return ' '.join(texts)

    def _extract_context_from_element(self, svg_element):
        """
        Extract contextual information from an SVG element and its parents

        Args:
            svg_element: BeautifulSoup SVG element

        Returns:
            dict: Context information including name, purpose, and location
        """
        context = {
            'name': None,
            'purpose': None,
            'button_text': None,
            'aria_label': None,
            'title': None,
            'data_attrs': {},
            'parent_type': None,
            'nearby_text': None
        }

        # Check SVG's own attributes
        if svg_element.get('aria-label'):
            context['aria_label'] = svg_element.get('aria-label')
        if svg_element.get('title'):
            context['title'] = svg_element.get('title')

        # Check for title element inside SVG
        title_tag = svg_element.find('title')
        if title_tag and title_tag.get_text(strip=True):
            context['title'] = title_tag.get_text(strip=True)

        # Walk up the parent tree
        current = svg_element.parent
        levels_checked = 0
        max_levels = 5  # Don't go too far up

        while current and levels_checked < max_levels:
            # Check for button with text
            if current.name == 'button':
                context['parent_type'] = 'button'
                # Get button text (excluding SVG elements and their contents)
                text = self._get_text_excluding_svg(current)
                if text and len(text) > 0 and len(text) < 50:
                    context['button_text'] = text
                # Check for aria-label on button
                if current.get('aria-label'):
                    context['aria_label'] = current.get('aria-label')
                break

            # Check for link with text
            if current.name == 'a':
                context['parent_type'] = 'link'
                # Get link text (excluding SVG elements and their contents)
                text = self._get_text_excluding_svg(current)
                if text and len(text) > 0 and len(text) < 50:
                    context['button_text'] = text
                if current.get('aria-label'):
                    context['aria_label'] = current.get('aria-label')
                if current.get('href'):
                    context['data_attrs']['href'] = current.get('href')
                break

            # Check for list item with data attributes
            if current.name == 'li':
                for attr, value in current.attrs.items():
                    if attr.startswith('data-'):
                        context['data_attrs'][attr] = value

            # Check for any element with helpful data attributes
            for attr, value in current.attrs.items():
                if attr.startswith('data-') and attr not in context['data_attrs']:
                    context['data_attrs'][attr] = value

            # Look for sibling text elements
            if not context['nearby_text']:
                for sibling in current.find_all(['span', 'label', 'p', 'div'], recursive=False):
                    text = self._get_text_excluding_svg(sibling)
                    if text and len(text) > 0 and len(text) < 50:
                        context['nearby_text'] = text
                        break

            current = current.parent
            levels_checked += 1

        # Generate a descriptive name based on context
        context['name'] = self._generate_name_from_context(context)
        context['purpose'] = self._generate_purpose_from_context(context)

        return context

    def _is_element_hidden(self, element):
        """
        Check if an element or any of its parents is hidden

        Args:
            element: BeautifulSoup element to check

        Returns:
            bool: True if element is hidden, False otherwise
        """
        current = element
        max_levels = 10  # Check up to 10 parent levels
        levels_checked = 0

        while current and levels_checked < max_levels:
            # Check if inside a template tag (template content is not rendered)
            if hasattr(current, 'name') and current.name == 'template':
                return True

            # Check for hidden class
            classes = current.get('class', [])
            if 'hidden' in classes:
                return True

            # Check for display: none or visibility: hidden in style
            style = current.get('style', '')
            if 'display:none' in style.replace(' ', '') or 'display: none' in style:
                return True
            if 'visibility:hidden' in style.replace(' ', '') or 'visibility: hidden' in style:
                return True

            current = current.parent
            levels_checked += 1

        return False

    def _normalize_svg_for_comparison(self, svg_element):
        """
        Normalize SVG for comparison (remove variable attributes like IDs)

        Args:
            svg_element: BeautifulSoup SVG element

        Returns:
            str: Normalized SVG content for comparison
        """
        # Clone the SVG to avoid modifying original
        svg_str = str(svg_element)

        # Remove clip-path IDs and references that might vary
        svg_str = re.sub(r'clip-path="url\(#[^)]+\)"', '', svg_str)
        svg_str = re.sub(r'id="[^"]*"', '', svg_str)
        svg_str = re.sub(r'aria-labelledby="[^"]*"', '', svg_str)

        # Normalize whitespace
        svg_str = re.sub(r'\s+', ' ', svg_str)

        return svg_str.strip()

    def _get_svg_hash(self, svg_element):
        """
        Generate a hash for an SVG element based on its normalized content

        Args:
            svg_element: BeautifulSoup SVG element

        Returns:
            str: MD5 hash of normalized SVG content
        """
        normalized = self._normalize_svg_for_comparison(svg_element)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    def _generate_name_from_context(self, context):
        """Generate a descriptive name from context"""
        max_name_length = 30  # Maximum length for generated names

        # Priority order for naming
        if context['button_text']:
            # Clean up button text
            text = context['button_text'].strip()
            # Limit length before processing
            text = text[:max_name_length]
            # Remove extra whitespace
            text = re.sub(r'\s+', '_', text)
            # Remove special characters
            text = re.sub(r'[^\w\s-]', '', text)
            # Convert to lowercase
            text = text.lower()
            # Ensure it's not empty after cleaning
            if text:
                return text

        if context['aria_label']:
            text = context['aria_label'].strip()[:max_name_length]
            text = re.sub(r'\s+', '_', text.lower())
            text = re.sub(r'[^\w\s-]', '', text)
            if text:
                return text

        if context['title']:
            text = context['title'].strip()[:max_name_length]
            text = re.sub(r'\s+', '_', text.lower())
            text = re.sub(r'[^\w\s-]', '', text)
            if text:
                return text

        # Check data attributes for naming hints
        if 'data-sidebar-item' in context['data_attrs']:
            return context['data_attrs']['data-sidebar-item'][:max_name_length]

        if 'data-item-name' in context['data_attrs']:
            return context['data_attrs']['data-item-name'][:max_name_length]

        if context['nearby_text']:
            text = context['nearby_text'].strip()[:max_name_length]
            text = re.sub(r'\s+', '_', text.lower())
            text = re.sub(r'[^\w\s-]', '', text)
            if text:
                return text

        return 'unnamed_icon'

    def _generate_purpose_from_context(self, context):
        """Generate a purpose description from context"""
        parts = []

        if context['parent_type']:
            parts.append(f"Used in {context['parent_type']}")

        if context['button_text']:
            parts.append(f'labeled "{context["button_text"]}"')
        elif context['aria_label']:
            parts.append(f'labeled "{context["aria_label"]}"')
        elif context['title']:
            parts.append(f'titled "{context["title"]}"')

        if context['data_attrs'].get('href'):
            parts.append(f"linking to {context['data_attrs']['href']}")

        if parts:
            return ' '.join(parts)

        return "Icon element"

    def extract_svgs_with_context(self, skip_hidden=True, deduplicate=True):
        """
        Extract SVG elements with contextual information

        Args:
            skip_hidden (bool): Skip SVGs in hidden elements (default: True)
            deduplicate (bool): Remove duplicate SVGs based on content (default: True)

        Returns:
            list: List of tuples (svg_string, context_dict)
        """
        svg_elements = self.soup.find_all('svg')
        self.svg_contexts = []
        seen_hashes = set()

        for svg in svg_elements:
            # Skip hidden elements if requested
            if skip_hidden and self._is_element_hidden(svg):
                continue

            # Deduplicate if requested
            if deduplicate:
                svg_hash = self._get_svg_hash(svg)
                if svg_hash in seen_hashes:
                    continue
                seen_hashes.add(svg_hash)

            context = self._extract_context_from_element(svg)
            self.svg_contexts.append({
                'svg': str(svg),
                'context': context
            })

        return self.svg_contexts

    def get_svg_info(self):
        """
        Get detailed information about extracted SVGs

        Returns:
            list: List of dictionaries containing SVG information
        """
        svg_elements = self.soup.find_all('svg')
        svg_info = []

        for idx, svg in enumerate(svg_elements, 1):
            info = {
                'index': idx,
                'width': svg.get('width'),
                'height': svg.get('height'),
                'viewBox': svg.get('viewBox'),
                'fill': svg.get('fill'),
                'stroke': svg.get('stroke'),
                'xmlns': svg.get('xmlns'),
                'has_paths': len(svg.find_all('path')) > 0,
                'path_count': len(svg.find_all('path')),
                'has_groups': len(svg.find_all('g')) > 0,
                'group_count': len(svg.find_all('g')),
                'svg_content': str(svg)
            }
            svg_info.append(info)

        return svg_info

    def save_svgs(self, output_dir='output', prefix='svg'):
        """
        Save extracted SVGs to individual files

        Args:
            output_dir (str): Directory to save SVG files
            prefix (str): Prefix for SVG filenames

        Returns:
            list: List of saved file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        saved_files = []
        svg_elements = self.soup.find_all('svg')

        for idx, svg in enumerate(svg_elements, 1):
            filename = f"{prefix}_{idx:03d}.svg"
            filepath = output_path / filename

            # Ensure the SVG has proper namespace
            if not svg.get('xmlns'):
                svg['xmlns'] = 'http://www.w3.org/2000/svg'

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(svg))

            saved_files.append(str(filepath))

        return saved_files

    def export_as_code_blocks(self, output_file=None):
        """
        Export SVGs as code blocks with descriptive comments

        Args:
            output_file (str): Optional file path to save output

        Returns:
            str: Formatted code blocks with comments
        """
        svg_contexts = self.extract_svgs_with_context()
        output_lines = []

        output_lines.append("=" * 80)
        output_lines.append("EXTRACTED SVG ICONS WITH CONTEXT")
        output_lines.append("=" * 80)
        output_lines.append("")

        for idx, item in enumerate(svg_contexts, 1):
            context = item['context']
            svg_code = item['svg']

            # Add comment header
            output_lines.append(f"# Icon {idx}: {context['name']}")
            output_lines.append(f"# Purpose: {context['purpose']}")

            # Add additional context if available
            if context.get('data_attrs'):
                attrs = ', '.join([f"{k}={v}" for k, v in context['data_attrs'].items()])
                output_lines.append(f"# Attributes: {attrs}")

            output_lines.append("")
            output_lines.append(svg_code)
            output_lines.append("")
            output_lines.append("-" * 80)
            output_lines.append("")

        output_text = '\n'.join(output_lines)

        # Save to file if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_text)

        return output_text

    def save_svgs_with_context(self, output_dir='output'):
        """
        Save extracted SVGs to individual files with contextual names

        Args:
            output_dir (str): Directory to save SVG files

        Returns:
            list: List of saved file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        svg_contexts = self.extract_svgs_with_context()
        saved_files = []

        # Track names to avoid duplicates
        name_counts = {}

        for idx, item in enumerate(svg_contexts, 1):
            context = item['context']
            svg_code = item['svg']

            # Get base name
            base_name = context['name']

            # Handle duplicates
            if base_name in name_counts:
                name_counts[base_name] += 1
                filename = f"{base_name}_{name_counts[base_name]}.svg"
            else:
                name_counts[base_name] = 1
                filename = f"{base_name}.svg"

            filepath = output_path / filename

            # Parse SVG to ensure proper namespace
            svg_soup = BeautifulSoup(svg_code, 'html.parser')
            svg_element = svg_soup.find('svg')
            if svg_element and not svg_element.get('xmlns'):
                svg_element['xmlns'] = 'http://www.w3.org/2000/svg'
                svg_code = str(svg_element)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"<!-- {context['purpose']} -->\n")
                f.write(svg_code)

            saved_files.append(str(filepath))

        return saved_files

    def print_summary(self):
        """Print a summary of extracted SVGs"""
        svg_info = self.get_svg_info()

        print(f"\n{'='*60}")
        print(f"SVG EXTRACTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total SVGs found: {len(svg_info)}")
        print(f"{'='*60}\n")

        for info in svg_info:
            print(f"SVG #{info['index']}:")
            print(f"  Dimensions: {info['width']}x{info['height']}")
            print(f"  ViewBox: {info['viewBox']}")
            print(f"  Paths: {info['path_count']}")
            print(f"  Groups: {info['group_count']}")
            print()

    def print_context_summary(self):
        """Print a summary of extracted SVGs with context"""
        svg_contexts = self.extract_svgs_with_context()

        print(f"\n{'='*60}")
        print(f"SVG EXTRACTION SUMMARY (WITH CONTEXT)")
        print(f"{'='*60}")
        print(f"Total SVGs found: {len(svg_contexts)}")
        print(f"{'='*60}\n")

        for idx, item in enumerate(svg_contexts, 1):
            context = item['context']
            print(f"SVG #{idx}: {context['name']}")
            print(f"  Purpose: {context['purpose']}")
            if context['parent_type']:
                print(f"  Parent: {context['parent_type']}")
            if context['button_text']:
                print(f"  Text: \"{context['button_text']}\"")
            print()


def main():
    """Main function to run the SVG extractor"""
    parser = argparse.ArgumentParser(
        description='Extract SVG elements from HTML markup with smart context detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Simple Examples:
  # Paste HTML and get list in terminal
  svgext.py --inline --list

  # Read file and extract as SVG files
  svgext.py example.html --svg

  # Read file and show list in terminal
  svgext.py example.html --list

  # Paste HTML and save as SVG files
  svgext.py --inline --svg

Advanced Examples:
  # Pipe HTML and get list
  echo '<button>Save<svg>...</svg></button>' | svgext.py --list

  # Multiline paste with file output
  svgext.py --inline --svg << 'EOF'
  <div>
    <button>Download<svg>...</svg></button>
  </div>
  EOF

  # Custom output directory
  svgext.py input.html --svg -o icons/

  # Export as JSON
  svgext.py input.html --json output.json

  # No context detection (basic numbering)
  svgext.py input.html --svg --no-context
        """
    )

    parser.add_argument(
        'input_file',
        nargs='?',
        help='Input HTML file to parse'
    )

    # Input modes
    parser.add_argument(
        '--inline',
        action='store_true',
        help='Read from stdin (paste your HTML)'
    )

    # Output modes
    parser.add_argument(
        '--list',
        action='store_true',
        help='Print SVG list to terminal with comments'
    )

    parser.add_argument(
        '--svg',
        action='store_true',
        help='Extract as individual SVG files'
    )

    parser.add_argument(
        '--json',
        metavar='FILE',
        help='Save SVG information as JSON file'
    )

    # Options
    parser.add_argument(
        '-o', '--output-dir',
        default='output',
        help='Output directory for SVG files (default: output)'
    )

    parser.add_argument(
        '--no-context',
        action='store_true',
        help='Disable context detection (use basic numbering)'
    )

    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='Print summary only without saving files'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress output messages'
    )

    # Legacy flags (hidden, for backwards compatibility)
    parser.add_argument(
        '--stdin',
        action='store_true',
        help=argparse.SUPPRESS
    )

    parser.add_argument(
        '--with-context',
        action='store_true',
        help=argparse.SUPPRESS
    )

    parser.add_argument(
        '--code-blocks',
        metavar='FILE',
        help=argparse.SUPPRESS
    )

    parser.add_argument(
        '-p', '--prefix',
        default='svg',
        help=argparse.SUPPRESS
    )

    args = parser.parse_args()

    # Determine if we should use context (default: yes, unless --no-context)
    use_context = not args.no_context

    # Handle legacy --with-context flag
    if args.with_context:
        use_context = True

    # Read input - either from file or stdin
    if args.inline or args.stdin or not args.input_file:
        # Read from stdin
        if not args.quiet and sys.stdin.isatty():
            print("=" * 60, file=sys.stderr)
            print("Paste your HTML below", file=sys.stderr)
            print("Press Enter twice (empty line) when done", file=sys.stderr)
            print("=" * 60, file=sys.stderr)

        try:
            lines = []
            empty_line_count = 0

            # Check if stdin is being piped (not interactive)
            if not sys.stdin.isatty():
                # Piped input - read everything
                html_content = sys.stdin.read()
            else:
                # Interactive mode - read until double Enter
                while True:
                    try:
                        line = input()
                        if line.strip() == '':
                            empty_line_count += 1
                            if empty_line_count >= 2:
                                # Two empty lines in a row - done
                                break
                            lines.append(line)
                        else:
                            empty_line_count = 0
                            lines.append(line)
                    except EOFError:
                        # Ctrl+D or Ctrl+Z was pressed
                        break

                html_content = '\n'.join(lines)

            if not html_content.strip():
                print("\nError: No input provided", file=sys.stderr)
                sys.exit(1)
        except KeyboardInterrupt:
            print("\n\nCancelled by user", file=sys.stderr)
            sys.exit(0)
        except Exception as e:
            print(f"Error reading from stdin: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from file
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.input_file}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)

    # Extract SVGs
    extractor = SVGExtractor(html_content)

    # Determine output mode
    # If no output mode specified, default to --svg (save files)
    if not args.list and not args.svg and not args.json and not args.summary_only and not args.code_blocks:
        args.svg = True

    # Handle --list mode (print to terminal)
    if args.list or args.code_blocks:
        output_file = args.code_blocks if args.code_blocks else None
        output_text = extractor.export_as_code_blocks(output_file)

        if args.list:
            # Print to stdout (terminal)
            print(output_text)
        elif args.code_blocks:
            # Legacy mode - save to file
            if not args.quiet:
                print(f"\nExported SVGs as code blocks to '{args.code_blocks}'")
                print(f"Total SVGs: {len(extractor.svg_contexts)}")

        # Exit if only listing
        if args.list and not args.svg and not args.json:
            sys.exit(0)

    # Handle --svg mode (save files) or --summary-only
    if args.svg or args.summary_only:
        if use_context:
            svg_contexts = extractor.extract_svgs_with_context()
            if not svg_contexts:
                print("No SVG elements found in the input", file=sys.stderr)
                sys.exit(0)

            # Print context summary
            if not args.quiet:
                extractor.print_context_summary()

            # Save files if not summary-only
            if not args.summary_only and args.svg:
                saved_files = extractor.save_svgs_with_context(args.output_dir)
                if not args.quiet:
                    print(f"Saved {len(saved_files)} SVG files to '{args.output_dir}/'")
                    for filepath in saved_files:
                        print(f"  - {filepath}")

        else:
            # Basic extraction without context
            svgs = extractor.extract_svgs()
            if not svgs:
                print("No SVG elements found in the input", file=sys.stderr)
                sys.exit(0)

            # Print summary
            if not args.quiet:
                extractor.print_summary()

            # Save files if not summary-only
            if not args.summary_only and args.svg:
                saved_files = extractor.save_svgs(args.output_dir, 'svg')
                if not args.quiet:
                    print(f"Saved {len(saved_files)} SVG files to '{args.output_dir}/'")
                    for filepath in saved_files:
                        print(f"  - {filepath}")

    # Handle --json mode
    if args.json:
        if use_context:
            svg_contexts = extractor.extract_svgs_with_context()
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump(svg_contexts, f, indent=2)
        else:
            svg_info = extractor.get_svg_info()
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump(svg_info, f, indent=2)

        if not args.quiet:
            print(f"\nSaved SVG information to '{args.json}'")


if __name__ == '__main__':
    main()
