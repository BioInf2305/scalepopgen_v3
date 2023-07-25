process CALC_INDIV_SUMMARY{

    tag { "calculating_chromosomewise_summary_${chrom}" }
    label "oneCpu"
    container "maulik23/scalepopgen:0.1.2"
    conda "${baseDir}/environment.yml"
    publishDir("${params.outDir}/summary_stats/indiv_stats/", mode:"copy")

    input:
        tuple val(chrom), path(vcf), path(vcf_idx), path(sample_map)

    output:
        path("${chrom}_sample_summary.scount"), emit: samplesummary
        path("${chrom}*.idepth"), emit: sampledepthinfo
        
    
    script:

        def opt_args = ""
        opt_args = opt_args + " --chr-set "+ params.max_chrom
	if( params.allow_extra_chrom ){
                
            opt_args = opt_args + " --allow-extra-chr "

            }
        opt_args = opt_args + " --out "+chrom+"_sample_summary"

        """
        plink2 --vcf ${vcf} --threads ${task.cpus} --nonfounders --sample-counts ${opt_args}

        vcftools --gzvcf ${vcf} --depth --out ${chrom}_depth_info

        """ 
}