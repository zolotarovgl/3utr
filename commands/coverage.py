import logging
import os
import subprocess

logger = logging.getLogger('3utr.coverage')

def run_command(command, logger):
    logger.info(f"Executing: {command}")
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            logger.error(f"Command failed with error:\n{stderr.decode()}")
            raise Exception(f"Command failed with error:\n{stderr.decode()}\nCheck log.")
        return stdout.decode()
    except Exception as e:
        logger.error(f"Failed to execute command: {command}. Error: {e}")
        raise

def index_bam(bam_file, logger):
    bam_index_file = f"{bam_file}.bai"
    if not os.path.exists(bam_index_file):
        logger.info(f"BAM index file {bam_index_file} not found. Indexing BAM file...")
        index_command = f"samtools index {bam_file}"
        run_command(index_command, logger)
        logger.info("BAM file indexed successfully.")
    else:
        logger.info(f"BAM index file {bam_index_file} found. Skipping indexing.")

def bam_coverage(bam_file, outputfile, cpu_count, strand, logger):
    if not strand:
        logger.info("computing unstranded coverage.")
        bam_coverage_command = (
            f"bamCoverage --skipNonCoveredRegions -b {bam_file} "
            f"--outFileFormat bedgraph -p {cpu_count} -o {outputfile}"
        )
        run_command(bam_coverage_command, logger)
        logger.info("bamCoverage executed successfully.")
    else:
        logger.info(f"compuring coverage strand: {strand}")
        bam_coverage_command = (
            f"bamCoverage --skipNonCoveredRegions -b {bam_file} --filterRNAstrand {strand} "
            f"--outFileFormat bedgraph -p {cpu_count} -o {outputfile}"
        )
        
        # add strand info
        logger.info('adding strands to bedgraphs')
        tmpname = outputfile + '_tmp'
        if strand == 'forward':
            str_value = '+'
        elif strand == 'reverse':
            str_value = '-'
        else:
            raise(NotImplementedError(f'Unknown strand value {strand}'))
        add_strand_command = "awk 'BEGIN{OFS=@\\t@}{print $1,$2,$3,NR,$4,@\%s@}' %s > %s; mv %s %s" % (str_value,outputfile,tmpname,tmpname,outputfile)
        add_strand_command = add_strand_command.replace('@','"')
        #print(bam_coverage_command)
        #print(add_strand_command)
        #quit()
        run_command(bam_coverage_command, logger)
        run_command(add_strand_command,logger)
        

def merge_strands(for_bed, rev_bed ,outfile):
    command = 'cat %s %s > %s' % (for_bed, rev_bed,outfile)
    run_command(command, logger)

def check_temp(temp, logger):
    if not os.path.exists(temp):
        logger.info(f'Creating temporary directory: {temp}')
        os.makedirs(temp)
    else:
        logger.info(f'Temporary directory found: {temp}')

def filter_and_merge(bedgraph, outfile, cov_threshold,strand,logger):
    if strand == 'unstranded':
        merge_sub = '-c 4 -o sum'
    elif strand == 'stranded':
        merge_sub = '-c 4,5,6 -o distinct,sum,distinct'

    filter_and_merge_command = f"awk '$4>={cov_threshold}' {bedgraph}  | bedtools merge -i - {merge_sub} > {outfile}"
    run_command(filter_and_merge_command, logger)

    if is_file_empty(outfile):
        logger.info(f'ERROR: {outfile} is empty!')
        quit()
    logger.info(f"Filtered and merged bedgraph to {outfile} successfully.")

def is_file_empty(file_path):
        return os.path.exists(file_path) and os.path.getsize(file_path) == 0

def coverage_main(args):
    bam_file = args.bam
    strand = args.strand
    cpu_count = args.cpu
    temp = args.temp

    logger.info(" --".join([f"{key} : {value}" for key, value in args.__dict__.items()]))

    try:
        coverage_thr = 2
        check_temp(temp, logger)
        # Index BAM file
        index_bam(bam_file, logger)
        
        # Execute bamCoverage
        bedgraph_file = os.path.join(temp, 'cov.bedgraph')
        filtered_bed = os.path.join(temp, 'cov.reg.bed')
        
        if strand == 'unstranded':
            bam_coverage(bam_file, bedgraph_file, cpu_count, None, logger)
            filter_and_merge(bedgraph_file, filtered_bed, coverage_thr, strand, logger)
        else:
            for_bedgraph_file = os.path.join(temp, 'for.bedgraph')
            for_filtered_bed = os.path.join(temp,'for.reg.bed')
            rev_bedgraph_file = os.path.join(temp, 'rev.bedgraph')
            rev_filtered_bed = os.path.join(temp,'rev.reg.bed')

            if not os.path.exists(for_bedgraph_file): 
                bam_coverage(bam_file, for_bedgraph_file, cpu_count, 'forward', logger)
            else:
                logger.info(f'{for_bedgraph_file} found')
            if not os.path.exists(for_filtered_bed): 
                filter_and_merge(for_bedgraph_file,for_filtered_bed,coverage_thr, strand, logger)
            else: logger.info(f'{for_filtered_bed} exists')
            if not os.path.exists(rev_bedgraph_file): 
                bam_coverage(bam_file, rev_bedgraph_file, cpu_count, 'reverse', logger)
            else:
                logger.info(f'{rev_bedgraph_file} exists.')
            if not os.path.exists(rev_filtered_bed): 
                filter_and_merge(rev_bedgraph_file,rev_filtered_bed,coverage_thr, strand, logger)
            else:
                logger.info(f'{rev_filtered_bed} exists.')
            if not os.path.exists(filtered_bed):
                merge_strands(for_bed = for_filtered_bed,rev_bed = rev_filtered_bed,outfile = filtered_bed)
            else:
                logger.info(f'{filtered_bed} exists.')
    except Exception as e:
        logger.error(f"An error occurred during coverage processing: {e}")

