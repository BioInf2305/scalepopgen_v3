process CONVERT_BED_TO_VCF{

    tag { "convert_plink_bed_to_vcf" }
    label "oneCpu"
    conda "${baseDir}/environment.yml"
    container "maulik23/scalepopgen:0.1.1"
    publishDir("${params.outDir}/plink/bed_to_vcf/", mode:"copy")

    input:
        file(bed)

    output:
        path("${prefix}.vcf"), emit:vcf
        path("sample_family.map"), emit: sample_map

    when:
     task.ext.when == null || task.ext.when

    script:
        prefix = bed[0].baseName
        def opt_arg = ""
        def fasta = params.fasta
        def chrm_map = params.chrm_map
        opt_arg = opt_arg + " --chr-set "+ params.max_chrom
	if( params.allow_extra_chrom ){
                
            opt_arg = opt_arg + " --allow-extra-chr "

            }

        if( params.fasta != "none"){
            opt_arg = opt_arg + " --ref-from-fa --fa "+fasta
        }
        
        opt_arg = opt_arg + " --recode vcf --out plink"
        
        
        """
	plink2 --bfile ${prefix} ${opt_arg}

        awk '{print \$1"_"\$2,\$1}' ${prefix}.fam > sample_family.map

        if [[ "$fasta" == "none" ]]
            then
            awk 'NR==FNR{chrm_len[\$1]=\$2;next}{if(\$0~/^##contig/){match(\$0,/(##contig=<ID=)([^>]+)(>)/,a);print a[1]a[2]",length="chrm_len[a[2]]a[3];next}else{print}}' ${chrm_map} plink.vcf > ${prefix}.vcf
        else
            mv plink.vcf ${prefix}.vcf
        fi

        """ 
}