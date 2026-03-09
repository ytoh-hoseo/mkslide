import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mkslide",
        description="Convert Markdown to Beamer PDF slides (Hoseo University)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  mkslide week01.md
  mkslide week01.md --output-dir /tmp/slides
  mkslide week01.md --logo /path/to/logo.pdf
  mkslide clean
  mkslide clean --all
""",
    )

    parser.add_argument(
        "input",
        help="Markdown file to build, or 'clean' to remove build artifacts",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        metavar="DIR",
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "--logo",
        default=None,
        metavar="PDF",
        help="Path to logo PDF (default: bundled school-mark.pdf)",
    )
    parser.add_argument(
        "--all",
        dest="remove_all",
        action="store_true",
        help="With 'clean': also remove generated PDFs",
    )

    args = parser.parse_args()

    if args.input == "clean":
        from mkslide.build import clean
        clean(output_dir=args.output_dir, remove_pdfs=args.remove_all)
    else:
        from mkslide.build import build
        build(args.input, output_dir=args.output_dir, logo=args.logo)


if __name__ == "__main__":
    main()
