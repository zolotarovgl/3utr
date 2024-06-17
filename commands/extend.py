import logging
logger = logging.getLogger('3utr.extend')

def extend_main(args):
    input_file = args.input
    output_file = args.output
    length = args.length
    
    logger.info(f"Extend functionality executed with input: {input_file}, output: {output_file}, length: {length}")
