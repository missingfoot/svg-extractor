#!/usr/bin/env python3
"""
SVG Extractor - Extract all SVG elements from HTML markup
"""

import argparse
import json
import os
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

    def extract_svgs(self):
        """
        Extract all SVG elements from the HTML

        Returns:
            list: List of SVG elements as strings
        """
        svg_elements = self.soup.find_all('svg')
        self.svgs = [str(svg) for svg in svg_elements]
        return self.svgs

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


def main():
    """Main function to run the SVG extractor"""
    parser = argparse.ArgumentParser(
        description='Extract SVG elements from HTML markup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from file
  python svg_extractor.py input.html

  # Extract and save to directory
  python svg_extractor.py input.html -o my_svgs

  # Extract and save as JSON
  python svg_extractor.py input.html --json output.json

  # Print summary only
  python svg_extractor.py input.html --summary-only
        """
    )

    parser.add_argument(
        'input_file',
        help='Input HTML file to parse'
    )

    parser.add_argument(
        '-o', '--output-dir',
        default='output',
        help='Output directory for SVG files (default: output)'
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

    # Read input file
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
