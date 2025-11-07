#!/usr/bin/env python3
"""
SVG Extractor - Extract all SVG elements from HTML markup
"""

import argparse
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
                # Get button text (excluding SVG)
                button_text = current.get_text(separator=' ', strip=True)
                if button_text:
                    context['button_text'] = button_text
                # Check for aria-label on button
                if current.get('aria-label'):
                    context['aria_label'] = current.get('aria-label')
                break

            # Check for link with text
            if current.name == 'a':
                context['parent_type'] = 'link'
                link_text = current.get_text(separator=' ', strip=True)
                if link_text:
                    context['button_text'] = link_text
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
                    text = sibling.get_text(strip=True)
                    if text and len(text) > 0 and len(text) < 50:
                        context['nearby_text'] = text
                        break

            current = current.parent
            levels_checked += 1

        # Generate a descriptive name based on context
        context['name'] = self._generate_name_from_context(context)
        context['purpose'] = self._generate_purpose_from_context(context)

        return context

    def _generate_name_from_context(self, context):
        """Generate a descriptive name from context"""
        # Priority order for naming
        if context['button_text']:
            # Clean up button text
            text = context['button_text'].strip()
            # Remove extra whitespace
            text = re.sub(r'\s+', '_', text)
            # Remove special characters
            text = re.sub(r'[^\w\s-]', '', text)
            # Convert to lowercase
            text = text.lower()
            return text

        if context['aria_label']:
            text = re.sub(r'\s+', '_', context['aria_label'].strip().lower())
            text = re.sub(r'[^\w\s-]', '', text)
            return text

        if context['title']:
            text = re.sub(r'\s+', '_', context['title'].strip().lower())
            text = re.sub(r'[^\w\s-]', '', text)
            return text

        # Check data attributes for naming hints
        if 'data-sidebar-item' in context['data_attrs']:
            return context['data_attrs']['data-sidebar-item']

        if 'data-item-name' in context['data_attrs']:
            return context['data_attrs']['data-item-name']

        if context['nearby_text']:
            text = re.sub(r'\s+', '_', context['nearby_text'].strip().lower())
            text = re.sub(r'[^\w\s-]', '', text)
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

    def extract_svgs_with_context(self):
        """
        Extract SVG elements with contextual information

        Returns:
            list: List of tuples (svg_string, context_dict)
        """
        svg_elements = self.soup.find_all('svg')
        self.svg_contexts = []

        for svg in svg_elements:
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
        description='Extract SVG elements from HTML markup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from file with basic naming
  python svg_extractor.py input.html

  # Extract with context-aware naming
  python svg_extractor.py input.html --with-context

  # Export as code blocks with comments
  python svg_extractor.py input.html --code-blocks output.txt

  # Read from stdin (paste HTML and press Ctrl+D)
  python svg_extractor.py --with-context

  # Pipe HTML content directly
  echo '<div><svg>...</svg></div>' | python svg_extractor.py --with-context

  # Use here-string (bash)
  python svg_extractor.py --code-blocks output.txt <<< '<html>...</html>'

  # Use here-doc for multiline
  python svg_extractor.py --with-context << 'EOF'
  <div>
    <button>Search<svg>...</svg></button>
  </div>
  EOF

  # Extract and save to directory
  python svg_extractor.py input.html -o my_svgs --with-context

  # Extract and save as JSON
  python svg_extractor.py input.html --json output.json

  # Print summary only
  python svg_extractor.py input.html --summary-only --with-context
        """
    )

    parser.add_argument(
        'input_file',
        nargs='?',
        help='Input HTML file to parse (omit to read from stdin)'
    )

    parser.add_argument(
        '-o', '--output-dir',
        default='output',
        help='Output directory for SVG files (default: output)'
    )

    parser.add_argument(
        '--stdin',
        action='store_true',
        help='Read HTML content from stdin instead of file'
    )

    parser.add_argument(
        '-p', '--prefix',
        default='svg',
        help='Prefix for output SVG filenames (default: svg)'
    )

    parser.add_argument(
        '--json',
        help='Save SVG information as JSON file'
    )

    parser.add_argument(
        '--with-context',
        action='store_true',
        help='Extract with contextual information (names from buttons, labels, etc.)'
    )

    parser.add_argument(
        '--code-blocks',
        metavar='FILE',
        help='Export as code blocks with comments to specified file'
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

    args = parser.parse_args()

    # Read input - either from file or stdin
    if args.stdin or not args.input_file:
        # Read from stdin
        if not args.quiet:
            if sys.stdin.isatty():
                print("Reading HTML from stdin... (Paste content and press Ctrl+D when done)", file=sys.stderr)
        try:
            html_content = sys.stdin.read()
            if not html_content.strip():
                print("Error: No input provided", file=sys.stderr)
                sys.exit(1)
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

    # Handle code blocks export mode
    if args.code_blocks:
        output_text = extractor.export_as_code_blocks(args.code_blocks)
        if not args.quiet:
            print(f"\nExported SVGs as code blocks to '{args.code_blocks}'")
            print(f"Total SVGs: {len(extractor.svg_contexts)}")
        # Exit after code blocks export
        sys.exit(0)

    # Regular extraction
    if args.with_context:
        svg_contexts = extractor.extract_svgs_with_context()
        if not svg_contexts:
            print("No SVG elements found in the input file", file=sys.stderr)
            sys.exit(0)

        # Print context summary
        if not args.quiet:
            extractor.print_context_summary()

        # Save files if not summary-only
        if not args.summary_only:
            saved_files = extractor.save_svgs_with_context(args.output_dir)
            if not args.quiet:
                print(f"Saved {len(saved_files)} SVG files with contextual names to '{args.output_dir}/'")
                for filepath in saved_files:
                    print(f"  - {filepath}")

        # Save JSON with context if requested
        if args.json:
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump(svg_contexts, f, indent=2)
            if not args.quiet:
                print(f"\nSaved SVG information with context to '{args.json}'")

    else:
        # Basic extraction without context
        svgs = extractor.extract_svgs()
        if not svgs:
            print("No SVG elements found in the input file", file=sys.stderr)
            sys.exit(0)

        # Print summary
        if not args.quiet:
            extractor.print_summary()

        # Save files if not summary-only
        if not args.summary_only:
            saved_files = extractor.save_svgs(args.output_dir, args.prefix)
            if not args.quiet:
                print(f"Saved {len(saved_files)} SVG files to '{args.output_dir}/' directory")
                for filepath in saved_files:
                    print(f"  - {filepath}")

        # Save JSON if requested
        if args.json:
            svg_info = extractor.get_svg_info()
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump(svg_info, f, indent=2)
            if not args.quiet:
                print(f"\nSaved SVG information to '{args.json}'")


if __name__ == '__main__':
    main()
