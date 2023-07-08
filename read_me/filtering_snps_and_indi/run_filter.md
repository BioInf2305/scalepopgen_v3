﻿## scalepopgen: Filter

Filtering data is the introductory step before conducting main analyses. The scalepopgen tool offers sample filtering, which can be carried out with the argument ```apply_indi_filters = true```, and SNP based filtering that can be launch with the argument ```apply_snp_filters = true```. The filtering process depends on the format of the input files. The processes of sample and site filtering will be done in [PLINK](https://www.cog-genomics.org/plink/2.0/), if the provided inputs are in program´s binaries. This is only partially true for the VCF inputs, where for the site filtering we implemented [VCFtools](https://vcftools.github.io/index.html), instead. 

For the sample filtering user has the following options:
 - removing samples according to the threshold of calculated kinship coefficient  
 - removing samples according to the amount of missing genotypes
 - removing user-defined samples

The site filtering options depend on the input format as mentioned before. For the VCF input all listed options are available, while in the case of PLINK input just the first four of them:
 - filtering based on minor allele frequency threshold
 - filtering according to the Hardy-Weinberg equilibrium exact test
 - filtering SNPs according to the amount of missing information 
 - removing user-defined SNPs
 - filtering SNPs based on min and max average depths
 - filtering SNPS according to the base quality limit

		!Here will be the workflow picture!
## Description of the parameters:
```king_cutoff```: pair with relationship coefficient greater than this will be removed;
```rem_indi```:  the name of text file containing individuals to be removed;
```mind```: samples with missing genotypes greater than threshold selected here will be removed;

```remove_snps```: the name of text file containing the SNPs to be removed;
```maf```: SNPs with minor allele frequencies less than specified here will be removed;
```min_meanDP```: SNPs with average depth (across the samples) less than the number specified here will be removed (only for the VCF input);
```max_meanDP```: SNPs with average depth (across the samples) greater than the number specified here will be removed (only for the VCF input);
```hwe```: SNPs with p-value of calculated HWE less than specified here will be removed;
```max_missing```: SNPs which proportion of missing genotypes will exceeded the threshold selected here will be removed;
```minQ```: SNPs with base quality less than specified here will be removed (only for the VCF input)
## Description of the output files generated by this sub-workflow:
The scheme of output files differs according to the input formats. Lets take a look of the output structure for the VCF input. If the pipeline has completed successfully, it will generate three different output folders. 
->**\${output directory}/plink/**:
---->**./merged_bed/**: VCF converted to PLINK and merged
--------> **\*.bim, \*bed, \*.fam**: converted PLINK files
---->**./indi_filtered/**: sample-based filtering
-------->**\*.king.cutoff.in.id**: list of unrelated samples that will remain
-------->**\*.king.cutoff.out.id**: list of related samples that will be excluded
-------->**\*.smiss**: sample-based missing data report
-------->**\*.vmiss**: variant-based missing data report
-------->**\*.bim, \*bed, \*.fam**: filtered PLINK format files 
-------->**indi_kept.map**: sample map file with individual and population IDs
-------->**indi_kept.txt**: 

->**\${output directory}/vcftools/**:
---->**./indi_filtered/**: sample filtering with VCFtools based on list (indi_kept.txt) generated before
-------->**\*_filt_samples.vcf.gz**: sample filtered VCF files
---->**./sites_filtered/**: site-based filtering
-------->**\*_filt_samples.vcf_filt_sites.vcf.gz**: sample and site filtered VCF files

->**\${output directory}/tabix/**:
---->**\*_filt_samples.vcf_filt_sites.vcf.gz.tbi**: indexed sample and site filtered VCF files

If your input is in PLINK format, the filtered files will be stored in a folder **\${output directory}/plink/**. Similar as with VCF, inside you will find a subfolder **./indi_filtered/**, in which is the same content as specified above. In addition, there is also a subfolder **./sites_filtered/**, where you will find final sample and site filtered PLINK binary files:
-**\*_indi_kept_filt_sites.bed**
-**\*_indi_kept_filt_sites.bim**
-**\*_indi_kept_filt_sites.fam**

> **Note:** The output folders also contains the  **\*.log** file of the programs PLINK and VCFtools.


## Validation of the sub-workflow:
### 1. Required input data files
For workflow validation, we have downloaded publicly available samples with whole genome sequences from NCBI database. We included domestic goats (*Capra hircus*) represented by various breeds from Morocco and Switzerland (geo_map). In addition to them, we also included some wild *Capra* members that are: Alpine ibex (*C. ibex*), Iberian ibex (*C. pyrenaica*) and Siberian ibex (*C. sibirica*). Since we need an outgroup when performing some analyses, we also added Urial sheep (*Ovis vignei*). We will use variants from chromosome 28 and 29 of, all together, 39 animals.

The input data should be in the **VCF** or **PLINK binary** format files. 

All VCF files need to be splitted by the chromosomes and indexed with tabix. You will have to prepare csv list of those files. Each row is corresponding to one chromosome and each row has three different information separated by the comma. Like in example below, the first information in each row is chromosome name, next is path/to/the/file.vcf.gz and the last is path/to/the/file.vcf.gz.tbi.  
```
Chr28,/data/trial/NC_030835.1.vcf.gz,/data/trial/NC_030835.1.vcf.gz.tbi
Chr29,/data/trial/NC_030836.1.vcf.gz,/data/trial/NC_030836.1.vcf.gz.tbi
```
In addition to the VCF input format, it is also necessary to prepare a sample map file of individuals and populations. Sample map has two tab-delimited columns: in the first column are individual IDs and in the second are population IDs as demonstrated on the example below.
```
AfrGoat10 AfricaGoat
AfrGoat1 AfricaGoat
AfrGoat2 AfricaGoat
AfrGoat3 AfricaGoat
AfrGoat4 AfricaGoat
AfrGoat5 AfricaGoat
AfrGoat6 AfricaGoat
AfrGoat7 AfricaGoat
AfrGoat8 AfricaGoat
AfrGoat9 AfricaGoat
AlpIbex1 AlpineIbex
AlpIbex2 AlpineIbex
AlpIbex3 AlpineIbex
AlpIbex4 AlpineIbex
AlpIbex5 AlpineIbex
AlpIbex6 AlpineIbex
AlpIbex7 AlpineIbex
AlpIbex8 AlpineIbex
AlpIbex9 AlpineIbex
IbrIbex1 IberianIbex
IbrIbex2 IberianIbex
IbrIbex3 IberianIbex
IbrIbex4 IberianIbex
SibIbex1 SiberianIbex
SibIbex2 SiberianIbex
SwiGoat10 SwissGoat
SwiGoat11 SwissGoat
SwiGoat12 SwissGoat
SwiGoat1 SwissGoat
SwiGoat2 SwissGoat
SwiGoat3 SwissGoat
SwiGoat4 SwissGoat
SwiGoat5 SwissGoat
SwiGoat6 SwissGoat
SwiGoat7 SwissGoat
SwiGoat8 SwissGoat
SwiGoat9 SwissGoat
UriShep1 Urial
UriShep2 Urial
```
For the Plink binary input, you need to specified the path to the BED/BIM/FAM files in the section of general parameters:
```input= "path/to/the/files/*.{bed,bim,fam}"```
### 2. Optional input data files
This module allows you to remove samples that you want to exclude in given analyses (```rem_indi```). You have to prepare a space/tab-delimited text file with family IDs in the first column and within-family IDs in the second column as stated by [PLINK](https://www.cog-genomics.org/plink/2.0/filter#sample) (option --remove):
```
SwissGoat	SwiGoat11
SwissGoat	SwiGoat12
```
Similarly, you can also prepare a file with the SNPs that should be removed. The appearance of the file depends on the input formats. For the VCF input, we used option ```--exclude-positions``` of [VCFtools](https://vcftools.sourceforge.net/man_latest.html), which expect a text file with a tab-separated chromosome and position of the SNP in each line:
```
NC_030835.1	1443
NC_030835.1	1498
NC_030835.1	1542
NC_030835.1	2140
NC_030835.1	2158
NC_030836.1	282
NC_030836.1	389
NC_030836.1	414
NC_030836.1	1510
NC_030836.1	1525
```
In the case of PLINK binary input, we use the program´s option ```--exclude``` that accepts a text file with variant IDs (usually one per line):

### 3. Setting the parameters
At the beginning of the parameter file ***/parameters/scale_popgen.config**, we have to specified some of the general things first. 
```input```: name of the .csv input file for the VCF format or names of the PLINK binary files
```outDir```: the name of the output folder
```prefix```: prefix of the output files
```sample_map```: the name of the file with individuals and populations as addition to VCF input
```fasta```: the name of the reference genome fasta file that will be used for converting from VCF to PLINK format 
 ```allow_extra_chrom```: set to true if the input contains chromosome name in the form of string
```max_chrom```: maximum number of chromosomes
```outgroup```: the population ID of the outgroup (optimal)
```cm_to_bp```: the number of base pairs that corresponds to one centimorgan (optimal)

After that, there are two parts dedicated to the sample and site filtering. 

**// general parameters**

    input                     = "/data/trial/input.csv"
    outDir                    = "${baseDir}/../FilterVCF/"
    prefix                    = "filter"
    sample_map                = "/data/trial/sample.map"
    fasta                     = "none"
    chrm_map                  = "none"
    allow_extra_chrom         = true 
    max_chrom                 = 2
    outgroup                  = "Urial"
    cm_to_bp                   = 0

**//sample filtering parameters**

    apply_indi_filters     = true
    king_cutoff            = 0.25
    rem_indi               = "/data/trial/remove_vcf_samples.txt"
    mind                   = 0.1

**//sites filtering parameters**

    apply_snp_filters      = true
    remove_snps            = "/data/trial/remove_vcf_snps.txt"
    maf                    = 0.025
    min_meanDP             = 10
    max_meanDP             = 30
    hwe                    = 0.001
    max_missing            = 0.1
    minQ                   = 30

When we set all the parameter, we can run the tool.  In our case we used conda configuration profile and set maximum 10 processes that can be executed in parallel by each executor. The command looks like this:
```
nextflow run scale_popgen.nf -qs 10 -profile conda
```
You can check all the other command options by running the help option:
```
nextflow run scale_popgen.nf -help
```
After the filtering is done successfully, the command line output is looking like this:
```
N E X T F L O W  ~  version 23.04.1
Launching `scale_popgen.nf` [jolly_stone] DSL2 - revision: c7f30377b6
executor >  slurm (10)
[59/5bc6e5] process > CONVERT_VCF_TO_PLINK:CONVERT_VCF_TO_BED (converting_vcf_to_bed_NC_030836.1)               [100%] 2 of 2 ✔
[62/5ab879] process > CONVERT_VCF_TO_PLINK:MERGE_BED (merging_bed_merged_all_chrom_NC_030835.1.vcf)             [100%] 1 of 1 ✔
[be/e53c4f] process > PREPARE_KEEP_INDI_LIST:GET_KEEP_INDI_LIST (calc_missing_merged_all_chrom_NC_030835.1.vcf) [100%] 1 of 1 ✔
[66/bede0b] process > FILTER_VCF:KEEP_INDI (keep_indi_NC_030836.1)                                              [100%] 2 of 2 ✔
[26/bf3618] process > FILTER_VCF:FILTER_SITES (filter_sites_NC_030836.1)                                        [100%] 2 of 2 ✔
[89/7197c3] process > FILTER_VCF:INDEX_VCF (index_vcf_NC_030836.1)                                              [100%] 2 of 2 ✔
Completed at: 20-Jun-2023 16:27:05
Duration    : 11m 47s
CPU hours   : 0.3
Succeeded   : 10

```
## References
Please cite the following papers if you use this sub-workflow in your study:

[1] Danecek, P., Auton, A., Abecasis, G., Albers, C. A., Banks, E., DePristo, M. A., Handsaker, R. E., Lunter, G., Marth, G. T., Sherry, S. T., McVean, G., Durbin, R., & 1000 Genomes Project Analysis Group (2011). The variant call format and VCFtools. _Bioinformatics (Oxford, England)_, _27_(15), 2156–2158. https://doi.org/10.1093/bioinformatics/btr330

[2] Purcell, S., Neale, B., Todd-Brown, K., Thomas, L., Ferreira, M. A., Bender, D., Maller, J., Sklar, P., de Bakker, P. I., Daly, M. J., & Sham, P. C. (2007). PLINK: a tool set for whole-genome association and population-based linkage analyses. _American journal of human genetics_, _81_(3), 559–575. https://doi.org/10.1086/519795
## License

MIT

