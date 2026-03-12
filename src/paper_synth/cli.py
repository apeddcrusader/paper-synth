"""paper-synth CLI."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from paper_synth.core import format_markdown, load_abstracts, synthesize
from paper_synth.utils import write_output


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="paper-synth",
        description=(
            "Offline-first literature synthesis tool for aggregating "
            "findings across research abstracts"
        ),
    )
    parser.add_argument("--version", action="version", version="0.1.0")

    sub = parser.add_subparsers(dest="command")

    # -- synthesize sub-command --
    syn = sub.add_parser(
        "synthesize",
        help="Read abstract JSONs and produce a synthesis report",
    )
    syn.add_argument(
        "--input-dir",
        required=True,
        type=Path,
        help="Directory containing abstract JSON files",
    )
    syn.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path (default: stdout)",
    )
    syn.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        dest="fmt",
        help="Output format (default: markdown)",
    )

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return

    if args.command == "synthesize":
        _run_synthesize(args)


def _run_synthesize(args: argparse.Namespace) -> None:
    """Execute the synthesize sub-command."""
    abstracts = load_abstracts(args.input_dir)
    if not abstracts:
        print(
            f"No JSON abstracts found in {args.input_dir}",
            file=sys.stderr,
        )
        sys.exit(1)

    report = synthesize(abstracts)

    if args.fmt == "json":
        content = json.dumps(asdict(report), indent=2, ensure_ascii=False)
    else:
        content = format_markdown(report)

    if args.output:
        write_output(content, args.output)
        print(f"Report written to {args.output}")
    else:
        print(content)


if __name__ == "__main__":
    main()
