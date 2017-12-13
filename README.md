# Genevariants

This is a class project for CS478: Intro to Machine Learning and CS418: Bioinformatics at BYU.
It explores the learnability of SNP pathogenicity.

See also the associated paper.

*Note:* all the python code is expecting to be run from the root of the repository. It will not find the datafiles if run from another directory.

## Data
The data for this project was derived from the the ClinVar database of gene variants.
Additional features were added from AAindex and UCSC genome browser.

## Preprocessing and feature extraction 
Note: this preprocessing has already been done for the BRC family, so the data is ready to go in the BRC_full.csv file. 
You only need to run these steps if you want to regenerate the files, run it on more data, or run the Neural Net on a new
Protein family or gene, like TTN.
1. Run FindProteinFamilies.py to gather genes from BRC family to one file
``` 
$ python FindProteinFamilies.py
```
2. Run GatherConservationData.py to gather the conservation data for the gene family.
``` 
$ python GatherConservationData.py
```
3. Run preprocessing.py to gather all the amino acid features and conservation data to one file.
 ``` 
$ python preprocessing.py
```
4. Now the data is ready to run through the Neural Network!
## Running the Neural Network

1. Create a python virtual environment in the (model/) directory
``` 
$ virtualenv -p python3 model/venv
```
2. Enter the environment
```
$ . ./model/venv/bin/activate
```

3. Install the requirements
```
$ pip install -r model/requirements.txt
```

4. Run the neural network 
```
$ python model/genevariants.py
```

5. When finished leave the venv
```
$ deactivate
```