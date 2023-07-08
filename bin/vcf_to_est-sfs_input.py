import sys
import argparse
from pysam import VariantFile


def map_to_dict(sample_map, outgroup_id):
    sample_dict = {}
    pop_dict = {"focal":[]}
    outgroup_list = []
    with open(outgroup_id) as source:
        for line in source:
            line = line.rstrip().split()
            pop_dict[line[0]] = []
            outgroup_list.append(line[0])
    with open(sample_map) as source:
        for line in source:
            line = line.rstrip().split()
            if line[1] in outgroup_list:
                sample_dict[line[0]] = line[1]
                pop_dict[line[1]].append(line[0])
            else:
                sample_dict[line[0]] = "focal"
                pop_dict["focal"].append(line[0])
    return sample_dict, pop_dict


def find_consensus_base_outgroup(base_dict):
    max_idx = list(base_dict.values()).index(max(base_dict.values()))
    cons_list = [ 1 if i==max_idx else 0 for i in range(4) ]
    return cons_list


def vcf_to_est_sfs(chrom, vcf_in, sample_map, outgroup_id, model, n_random):
    sample_dict, pop_dict = map_to_dict(sample_map, outgroup_id)
    vcf_pntr = VariantFile(vcf_in)
    dest_m = open(chrom+"_major_alleles.map","w")
    with open(chrom+"_data.txt","w") as dest_d:
        for rec in vcf_pntr.fetch():
            missing = 0
            snps = [rec.ref[0].upper(), rec.alts[0].upper()]
            pop_base_dict = {}
            for pop in pop_dict:
                pop_base_dict[pop] = {"A":0,"C":0,"G":0,"T":0}
            for sample in sample_dict:
                gt = rec.samples[sample]["GT"]
                if gt == (None, None):
                    missing = 1
                    break
                elif gt == (0, 0):
                    pop_base_dict[sample_dict[sample]][snps[0]]+=2
                elif gt == (1, 1):
                    pop_base_dict[sample_dict[sample]][snps[1]]+=2
                elif gt == (0, 1) or gt == (1, 0):
                    pop_base_dict[sample_dict[sample]][snps[0]]+=1
                    pop_base_dict[sample_dict[sample]][snps[1]]+=1
                else:
                    print("invalid genotypes at "+str(rec.pos)+"\n")
                    sys.exit(1)
            w_line = ""
            for k in pop_base_dict:
                if missing == 0:
                    if k == "focal":
                        w_line += ",".join(map(str, pop_base_dict[k].values()))+ " "
                    else:
                        base_count_list = find_consensus_base_outgroup(pop_base_dict[k])
                        w_line += ",".join(map(str,base_count_list)) + " "
                else:
                    w_line += "0,0,0,0 "
            w_line.rstrip()
            dest_d.write(w_line+"\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="convert vcf to input of sweepfinder2",
        epilog="author: Maulik Upadhyay (Upadhyaya.maulik@gmail.com)",
    )
    parser.add_argument(
        "-c", "--chrom", metavar="Str", help="chromosome string", required=True
    )
    parser.add_argument(
        "-V", "--vcf", metavar="File", help="input vcf file", required=True
    )
    parser.add_argument(
        "-M",
        "--map",
        metavar="File",
        help="map file with first column as sample and second column as pop",
        required=True
    )
    parser.add_argument(
        "-o", "--outgroup", metavar="File", help="file containing outgroup sample ids", required=True
    )
    parser.add_argument(
        "-m",
        "--Model",
        metavar="Str",
        help="model",
        default="all",
        required=False,
    )
    parser.add_argument(
        "-n",
        "--seed",
        metavar="Int",
        help="random_integer",
        default=123456,
        required=False,
    )
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    else:
        vcf_to_est_sfs(
            args.chrom,
            args.vcf,
            args.map,
            args.outgroup,
            args.Model,
            args.seed,
        )