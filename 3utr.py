import argparse
import logging
from commands.utrs import utrs_main
from commands.coverage import coverage_main
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('3utr')

def main():
    try:
        parser = argparse.ArgumentParser(description="3utr command line tool")
        subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

        # Subcommand: get utr
        parser_utrs = subparsers.add_parser("utrs", help="Extend functionality")
        parser_utrs.add_argument('--cov', type=str, required=True, help='Coverage bed computed with 3utr.py coverage')
        parser_utrs.add_argument('--stop', type=str, required=True, help='Bed file containing stop codons')
        parser_utrs.add_argument('--out', type=str, required=True, help='Output file name')
        parser_utrs.set_defaults(func=utrs_main)

        # Subcommand: coverage
        parser_coverage = subparsers.add_parser("coverage", help="Coverage functionality")
        parser_coverage.add_argument('--bam', type=str, required=True, help='BAM file for coverage calculation')
        parser_coverage.add_argument('--strand', type=str, choices=['unstranded', 'stranded'], required=False, default='unstranded', help='Strand information for coverage calculation')
        parser_coverage.add_argument('--cpu', type=int, required=True, help='Number of CPU cores to use')
        parser_coverage.add_argument('--temp', type=str, required=False, help='Name of temporary directory', default='tmp')
        parser_coverage.set_defaults(func=coverage_main)

        # Parse and execute
        args = parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()
    except Exception as e:
        logger.error(f"An error occurred in the main function: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
