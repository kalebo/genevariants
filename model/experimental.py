import pandas as pd
import numpy as np 

import pdb

from keras.models import Sequential
from keras.optimizers import SGD
from keras.layers import Dense, Dropout
from keras.utils import to_categorical

from sklearn.model_selection import StratifiedKFold

ordered_labels_full = [
                    'Benign', 
                    'Benign/Likely benign',
                    'Likely benign',
                    'Conflicting interpretations of pathogenicity',
                    'Likely pathogenic',
                    'Pathogenic/Likely pathogenic',
                    'Pathogenic'
]

reduced_labels_mapping = {
                    'Benign': 'Benign',
                    'Benign/Likely benign': 'Benign',
                    'Likely benign': 'Benign',
                    'Conflicting interpretations of pathogenicity': 'Pathogenic',
                    'Likely pathogenic': 'Pathogenic',
                    'Pathogenic/Likely pathogenic': 'Pathogenic' ,
                    'Pathogenic': 'Pathogenic'
}

ordered_labels_reduced = [
                    'Benign', 
                    'Pathogenic'
]

tweak_to_hot = lambda df,col: to_categorical(df[col].astype("category").cat.codes)

def load_and_process(filename):
    data = pd.read_csv(filename)

    inputdata = data[['Conservation', 'PALJ810102', 'CHOP780216',
                    'ONEK900102', 'BIOV880101', 'FUKS010108', 'CEDJ970102', 'CHAM820101',
                    'FAUJ880107', 'MAXF760104', 'ZIMJ680104', 'GEIM800109', 'GEOR030106',
                    'KARS160111', 'DIGM050101', 'WERD780103', 'QIAN880115']]


    # Convert categorical column to one hot
    unmut  = (tweak_to_hot(data, "Unmutated AA"))
    mut = (tweak_to_hot(data, "Mutated AA"))

    train = np.c_[unmut, inputdata.values, mut]

    # Reduce labels (from 7 to 3)
    reduced_labels = data["Clinical Significance"].replace(reduced_labels_mapping)

    # Convert label to ordered category
    label_cat = pd.Categorical(reduced_labels, categories=ordered_labels_reduced, ordered=True)

    # convert label_cat to one hot encoding
    labels = to_categorical(pd.Series(label_cat).cat.codes)

    return train, labels

def create_model(input_feature_count, label_count):

    # Older model
    # model.add(Dense(units=20, activation='relu', input_dim=train.shape[1]))
    # model.add(Dense(units=20, activation='relu'))
    # model.add(Dense(units=20, activation='relu'))
    # model.add(Dense(units=7, activation='softmax'))
    # 
    # model.compile(loss='categorical_crossentropy',
    #               optimizer='sgd',
    #               metrics=['accuracy'])
    # 
    model = Sequential()
    model.add(Dropout(0.4, input_shape=(input_feature_count,) ))
    model.add(Dense(120, kernel_initializer='normal', activation='relu'))
    model.add(Dense(120, kernel_initializer='normal', activation='relu'))
    model.add(Dense(label_count, kernel_initializer='normal', activation='softmax'))

    sgd = SGD(lr=0.10, momentum=0.9, decay=0.0, nesterov=False)
    if label_count == 2:
        model.compile(loss='binary_crossentropy', optimizer=sgd, metrics=['accuracy'])
    else:
        model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

    return model

def train_and_evaluate_model(model, train, train_label, test, test_label):
    model.fit(train, train_label, epochs=30, batch_size=40, verbose=0)

    loss_and_metrics_train = np.array(model.evaluate(train, train_label, batch_size=128))
    loss_and_metrics_test = np.array(model.evaluate(test, test_label, batch_size=128))
    return loss_and_metrics_train, loss_and_metrics_test

if __name__ == "__main__":
    n_folds = 10
    data, labels  = load_and_process("./data/BRC_full.csv")

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True)
    train_stats = np.zeros((n_folds, 2))
    test_stats = np.zeros((n_folds, 2))

    i = 0
    for train_index, test_index in skf.split(data, labels[:,0]): # Silly munging of shape
            print("Running Fold", i+1, "/", n_folds)
            model = None # Clearing the NN.
            model = create_model(data.shape[1], labels.shape[1])
            train_stats[i],test_stats[i] = train_and_evaluate_model(model, data[train_index], labels[train_index], data[test_index], labels[test_index])
            i+=1

    train_mean = train_stats.mean(axis=0)
    train_std = train_stats.std(axis=0)

    test_mean = test_stats.mean(axis=0)
    test_std = test_stats.std(axis=0)

    result_str = """
    Training Accuracy Mean = {:1.4f} ± {:1.4f}
    Training Loss Mean = {:1.4f} ± {:1.4f}

    Test Accuracy Mean = {:.4f} ± {:1.4f}
    Test Loss Mean = {:1.4f} ± {:1.4f}
    """.format(train_mean[1], train_std[1], train_mean[0], train_std[0], test_mean[1], test_std[1], test_mean[0], test_std[0])
    print(result_str)