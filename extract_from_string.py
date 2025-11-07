#!/usr/bin/env python3
"""
Quick script to extract SVGs from a string/clipboard content
Usage: python extract_from_string.py
"""

from svg_extractor import SVGExtractor


def main():
    print("="*60)
    print("SVG Extractor - Paste HTML content")
    print("="*60)
    print("Paste your HTML content below.")
    print("When done, press Ctrl+D (Linux/Mac) or Ctrl+Z (Windows) then Enter")
    print("-"*60)

    # Read multiline input
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    html_content = '\n'.join(lines)

    if not html_content.strip():
        print("\nNo content provided. Exiting.")
        return

    print("\n" + "="*60)
    print("Processing...")
    print("="*60 + "\n")

    # Extract SVGs
    extractor = SVGExtractor(html_content)
    svgs = extractor.extract_svgs()

    if not svgs:
        print("No SVG elements found in the provided content.")
        return

    # Print summary
    extractor.print_summary()

    # Ask if user wants to save
    print("="*60)
    save = input("Save SVGs to files? (y/n): ").lower().strip()

    if save == 'y':
        output_dir = input("Output directory (default: output): ").strip() or "output"
        prefix = input("Filename prefix (default: svg): ").strip() or "svg"

        saved_files = extractor.save_svgs(output_dir, prefix)
        print(f"\nSaved {len(saved_files)} SVG files:")
        for filepath in saved_files:
            print(f"  - {filepath}")
    else:
        print("\nNot saving files.")

    # Ask if user wants to see the SVGs
    print("\n" + "="*60)
    show = input("Display extracted SVGs? (y/n): ").lower().strip()

    if show == 'y':
        print("\n" + "="*60)
        print("EXTRACTED SVGs")
        print("="*60 + "\n")

        for idx, svg in enumerate(svgs, 1):
            print(f"--- SVG #{idx} ---")
            print(svg)
            print()


if __name__ == '__main__':
    main()
