import os
import re


class FindProteinFamilies:
    def create_variant_file_by_family(self, data, family):
        outfile = open("data/" + family + "_variants.txt", "w")
        for line in data:
            features = re.split(r'\t+', line.rstrip('\t'))
            gene_name = features[1]
            gene_name = gene_name[:3]         #grab 1st three chars
            if (gene_name == family):
                outfile.write(line)

    def write_families_to_file(self, large_families):
        outfile = open("data/large_families.txt", "w")
        outfile.write("FamilyName\tCount\n")
        for gene, count in large_families.items():
            outfile.write(gene + "\t" + str(count) + "\n")

    def find_large_families(self, protein_families):
        family = "none"
        max = 0
        num_of_large_families = 0
        large_families = dict()
        for gene, count in protein_families.items():
            if count > max:
                family = gene
                max = count
            if count > 1000:
                large_families[gene] = count
                num_of_large_families +=1

        print("found max")
        return large_families

    def organize_protein_families(self):
        working_directory = os.getcwd()
        fileNames = os.listdir("data")
        path_name = os.path.join("data", "cleaned_variants_win_smaller.txt")
        infile = open(path_name, "r")
        protein_families = dict()
        data = []

        for line in infile:
            data.append(line)
            #features = [s.strip() for s in line.splitlines()]
        #     features = re.split(r'\t+', line.rstrip('\t'))
        #     gene_name = features[1]
        #     gene_name = gene_name[:3]         #grab 1st three chars
        #     if (gene_name in protein_families):
        #         protein_families[gene_name] += 1
        #     else:
        #         protein_families[gene_name] = 1
        #
        # large_families = self.find_large_families(protein_families)
        # self.write_families_to_file(large_families)
        self.create_variant_file_by_family(data, "COL") #change the gene name to create a new family file
        self.create_variant_file_by_family(data, "TTN") #change the gene name to create a new family file
        print("break point")

    def main(self):
        self.organize_protein_families()


if __name__ == '__main__':
    FindProteinFamilies().main()