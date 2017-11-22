#!/usr/bin/env python3

import aaindex

import numpy as np
import pandas as pd
import re


import pdb

NEG_INF = float('-inf')

def get_feature_list(filename):
    with open(filename) as f:
        raw = f.read()

    return raw.strip().split()

class Preprocessor:
    '''
    Handles fetching the additional features from aaindex files, and
    region conservation data.
    '''

    one_letter ={'VAL':'V', 'ILE':'I', 'LEU':'L', 'GLU':'E', 'GLN':'Q', \
    'ASP':'D', 'ASN':'N', 'HIS':'H', 'TRP':'W', 'PHE':'F', 'TYR':'Y',   \
    'ARG':'R', 'LYS':'K', 'SER':'S', 'THR':'T', 'MET':'M', 'ALA':'A',   \
    'GLY':'G', 'PRO':'P', 'CYS':'C'}

    default_columns = [
        "HGVS Expression",
        "Gene Symbol", 
        "Reference SNP Identifier",
        "Nucleotide Mutation Location", 
        "Protein Mutation Location", 
        "Unmutated AA", 
        "Mutated AA", 
        "Clinical Significance"] 
    # we will add columns for AADiffs for each feature and if the mutation falls
    # in a highly conserved region. We can also try adding the protein family

    def __init__(self, aaindex, datafile: str):
        self.aaindex = aaindex
        self.load_datafile(datafile)
    
    def load_datafile(self, datafile: str):
        '''
        Assume that the data is split rows from the cleaned variant file.
        '''
        hvgs_extract = re.compile(r':c\.([0-9]+).+ \(p\.([A-Za-z]{3})([0-9]+)([A-Za-z]{3}|=)\)')
        f = open(datafile, 'r')
        f.readline() # read in the header and discard
        data = []
        for line in f:
            hgvs, symbol, label, rsnum = line.strip().split("\t")
            try:
                nloc, preaa, ploc, postaa = hvgs_extract.search(hgvs).groups()
                if postaa == "=":
                    pastaa = preaa
            except AttributeError:
                print(line.split('\t'))
            data.append([hgvs, symbol, rsnum, nloc, ploc, preaa, postaa, label])
            self.data = pd.DataFrame(data)
            self.data.columns = self.default_columns

    def add_conservation_data(self, datafile):

        with open(datafile) as f:
            columns = f.readline()
            data = f.read()
        
        self.conservation = {}
        for row in data.strip().split("\n"):
            rsnum, _, conservation = row.split()
            self.conservation[rsnum] = conservation

        #self.conservation = pd.DataFrame(data.strip().split(), column=columns.split()).reshape(-1, 3)

        conservation_column = []
        for rsnum in self.data["Reference SNP Identifier"]:
            try:
                conservation_column.append(float(self.conservation["rs"+rsnum]))
            except KeyError:
                conservation_column.append(0)

        self.data["Conservation"] = pd.Series(conservation_column)

    def preprocess(self, feature_list):
        for feature in feature_list:
            self.add_feature(feature)

    def add_feature(self, aaindex_key):
        feature_col = []
        aarecord = aaindex.get(aaindex_key)

        # for Ter codon we set it to -1
        col_max = 0
        col_min = 0

        for i, ori, mut in self.data[["Unmutated AA", "Mutated AA"]].itertuples():
            mut = ori if mut == "=" else mut
            pre = aarecord[self.one_letter[ori.upper()]] 
            post = aarecord[self.one_letter[mut.upper()]] if mut != "Ter" else -np.inf

            # TODO: consider if using absolute value of diff here instead 
            diff = post - pre

            if diff > col_max and diff != -np.inf: col_max = diff
            if diff < col_min and diff != -np.inf: col_min = diff

            feature_col.append(diff)


        self.data[aaindex_key] = pd.Series(feature_col)
        self.data[aaindex_key] = 2*(self.data[aaindex_key] - col_min)/(col_max- col_min) - 1

        # N.B., we set Ter codons to -1 not inf
        self.data.replace(-np.inf, -1, inplace=True)
        
if __name__ == '__main__':
        aaindex.init_from_file("data/aaindex1")
        feature_list = get_feature_list("data/features.txt")

        pr = Preprocessor(aaindex, "data/BRC_variants.txt")
        pr.add_conservation_data("data/conservation_data_BRC_family.txt")
        pr.preprocess(feature_list)



