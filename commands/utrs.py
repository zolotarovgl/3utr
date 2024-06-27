import subprocess
import os 
import logging
logger = logging.getLogger('3utr.utrs')

# Should allow calling the 3'-utrs from the coverage bed


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

def slice_regs(coverage_regions,stop_bed,output,strand,logger):
    if strand == "unstranded":
        command = f"""bedtools intersect -a {coverage_regions} -b {stop_bed} -wa -wb | \
awk 'BEGIN{{OFS="\\t"}}{{if($10=="+"){{print $1,$6,$3,$8,0,$10}}else{{print $1,$2,$7,$8,0,$10}}}}' | \
awk '$3>$2' > {output}"""
    elif strand == "stranded":
        command = f"""bedtools intersect -a {coverage_regions} -b {stop_bed} -wa -wb -s | \
awk 'BEGIN{{OFS="\\t"}}{{if($6=="+"){{print $1,$8,$3,$4":"$10,0,$6}}else{{print $1,$2,$8,$4":"$10,0,$6}}}}' | \
awk '$2>0&&$3>$2' > {output}"""
    run_command(command,logger)

def outersect_with_genes(bed,genes_bed,output,tmp_ids,strand,logger):
    command = f"""
    # create a list of UTRs overlapping more than one gene.
    bedtools intersect -a {bed} -b {genes_bed} -wa -wb -s | \
    awk '{{print $4"\\t"$10}}' | cut -f 1 | sort | uniq -c | \
    awk '$1>1 {{print $2}}' > {tmp_ids}

	if [ -s {tmp_ids} ]; then
        # The file is not-empty.
    	awk 'BEGIN{{OFS="\\t"}} FNR==NR {{o[$1]=$1;next}}{{if(!($4 in o)){{print $0}}}}' {tmp_ids} {bed} > {output}
	else
        echo "No offending utrs found!"
		cp {bed} {output}
	fi

    """
    run_command(command,logger)


def utrs_main(args):
    input_cov = args.cov
    input_stop = args.stop
    genes_bed = args.genes 
    strand = args.strand 
    output_file = args.out
    temp = args.temp
    
    init_3utrs = os.path.join(temp,'3utrs.bed')
    tmp_ids = os.path.join(temp,'ids.txt')
    slice_regs(input_cov,input_stop,init_3utrs,strand,logger)
    outersect_with_genes(init_3utrs,genes_bed,output_file,tmp_ids,strand,logger)



#GENES=Avaga.genes.bed
#bedtools intersect -a 3utr.bed -b Avaga.genes.bed -s -v > 3utr.noov.bed
# create a list of utrs overlapping more than one gene.
#bedtools intersect -a 3utr.bed -b $GENES -wa -wb -s | awk '{print $4"\t"$10}' | cut -f 1 | sort | uniq -c  | awk '$1>1 {print $2}' > offending.txt
#awk 'BEGIN{OFS="\t"} FNR==NR {o[$1]=$1;next}{if($4 in o == 0){print $0}}' offending.txt 3utr.bed   > 3utr.noov.bed

