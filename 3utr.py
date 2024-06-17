import argparse
import logging
from commands.extend import extend_main
from commands.coverage import coverage_main

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('3utr')

def main():
    parser = argparse.ArgumentParser(description="3utr command line tool")
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    # Subcommand: extend
    parser_extend = subparsers.add_parser("extend", help="Extend functionality")
    parser_extend.add_argument('--input', type=str, required=True, help='Input file for extending genes')
    parser_extend.add_argument('--output', type=str, required=True, help='Output file for results')
    parser_extend.add_argument('--length', type=int, required=False, default=1000, help='Length to extend')
    parser_extend.set_defaults(func=extend_main)

    # Subcommand: coverage
    parser_coverage = subparsers.add_parser("coverage", help="Coverage functionality")
    parser_coverage.add_argument('--bam', type=str, required=True, help='BAM file for coverage calculation')
    parser_coverage.add_argument('--strand', type=str, choices=['unstranded', 'stranded'], required=False, default='unstranded', help='Strand information for coverage calculation')
    parser_coverage.set_defaults(func=coverage_main)

    # Parse and execute
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

