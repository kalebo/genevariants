import os
import re


class GatherConservationData:
    """
    This script is used to combine the chromosome positions with conservation data to the rs numbers so that
    we can use the rs number we have in the ClinVar data to retrieve the conservation data for each mutation
    """

    data1 = []
    data2 = []
    def write_combine_cons_data_to_one_file(self, genefamily):
        """
        Combines the conservation data to one file for the family.
        :param data1: first gene conservation file
        :param data2: second gene conservation file
        :param genefamily: gene family
        :return:
        """
        outfile = open("data/conservation_data_" + genefamily + "_family.txt", "w")
        outfile.write("#rsNum\tChromStart\tConservation\n")
        for line in self.data1:
            if line[0] != '#':
                outfile.write(line)
        for line in self.data2:
            if line[0] != '#':
                outfile.write(line)
        print("files combined")

    def write_rs_chrom_cons_to_file(self, rs_to_chrom, chrom_to_cons, geneName, time):
        """
        Maps the rs number to the appropriate conservation value and writes it to the file.
        :param rs_to_chrom: dictionary of rs number to chromosome position
        :param chrom_to_cons: dictionary of chromosome position to conservation value
        :return:
        """
        outfile = open("data/conservation_data_" + geneName + ".txt", "w")
        outfile.write("#rsNum\tChromStart\tConservation\n")
        count = 0
        for rs, chrom in rs_to_chrom.items():
            if chrom in chrom_to_cons:
                conservation = chrom_to_cons[chrom]
                outfile.write(str(rs) + "\t" + str(chrom) + "\t" + str(conservation) + "\n")
                if time == 1:
                    self.data1.append(str(rs) + "\t" + str(chrom) + "\t" + str(conservation) + "\n")
                else:
                    self.data2.append(str(rs) + "\t" + str(chrom) + "\t" + str(conservation) + "\n")
            else:
                count += 1
        print("this many keys missing: " + str(count))

    def load_files(self, geneName, time):
        """
        Loads the chrom start position with rs number file and the conservation by chrom position file so that
        we can combine the two.
        """
        chrm_rs_path_name = os.path.join("data", "chrom_start_with_rs_" + geneName + ".txt")
        chromPos_rsNum_file = open(chrm_rs_path_name, "r")
        
        chrm_cons_path_name = os.path.join("data", "conservation_by_chrom_pos_" + geneName + ".txt")
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

        self.write_rs_chrom_cons_to_file(rs_to_chrom, chrom_to_cons, geneName, time)
        print("finished writing to file.")


    def main(self):
        #change gene name to load a different gene family's conservation data. Currently the only other one stored is TTN.
        self.load_files("BRCA1", 1)
        self.load_files("BRCA2", 2)
        self.write_combine_cons_data_to_one_file("BRC")


if __name__ == '__main__':
    GatherConservationData().main()
