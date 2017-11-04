
class CleanFile:
    def count_benign_vs_pathogenic(self):
        infile = open("data/cleaned_variants_win_smaller.txt", "r")
        path = 0
        ben = 0
        for line in infile:
            if "Pathogenic" in line:
                path += 1
            if "Benign" in line or "benign" in line:
                ben += 1

        print("number of pathogenic: " + str(path))
        print("number of benign: " + str(ben))

    def main(self):
        self.remove_unknown_data()
        #self.count_benign_vs_pathogenic()

    def remove_unknown_data(self):
        infile = open("data/cleaned_variants.txt", "r")
        outfile = open("data/cleaned_variants_win_smaller.txt", "w")
        for line in infile:
            if not "not provided" in line and not "Uncertain significance" in line:
                outfile.write(line)


if __name__ == '__main__':
    CleanFile().main()