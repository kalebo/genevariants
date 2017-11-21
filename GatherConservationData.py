import os
import re


class GatherConservationData:

    def write_rs_chrom_cons_to_file(self, rs_to_chrom, chrom_to_cons):
        outfile = open("data/conservation_data_BRCA2.txt", "w")
        outfile.write("#rsNum\tChromStart\tConservation\n")
        count = 0
        for rs, chrom in rs_to_chrom.items():
            if chrom in chrom_to_cons:
                conservation = chrom_to_cons[chrom]
                outfile.write(str(rs) + "\t" + str(chrom) + "\t" + str(conservation) + "\n")
            else:
                count += 1
        print("this many keys missing: " + str(count))

    def load_files(self):
        chrm_rs_path_name = os.path.join("data", "chrom_start_with_rs_BRCA2.txt")
        chromPos_rsNum_file = open(chrm_rs_path_name, "r")
        
        chrm_cons_path_name = os.path.join("data", "conservation_by_chrom_pos.txt")
        chromPos_conservation_file = open(chrm_cons_path_name, "r")
        
        rs_to_chrom = dict()        #key: rs number, value: chromosome start position
        chrom_to_cons = dict()        #key: chromosome start position, value: conservation value
        data = []

        for line in chromPos_rsNum_file:
            if line[0] != '#':
                line = line.rstrip()  #remove trailing whitespace and newline chars
                features = re.split(r'\t+', line.rstrip('\t'))
                rs_to_chrom[features[1]] = features[0]

        for line in chromPos_conservation_file:
            if line[0] != '#':
                line = line.rstrip()  #remove trailing whitespace and newline chars
                features = re.split(r'\t+', line.rstrip('\t'))
                chrom_to_cons[features[0]] = features[1]

        self.write_rs_chrom_cons_to_file(rs_to_chrom, chrom_to_cons)
        print("finished writing to file.")


    def main(self):
        self.load_files()


if __name__ == '__main__':
    GatherConservationData().main()