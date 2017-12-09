import pandas as pd
import numpy as np 

import pdb

from keras.models import Sequential
from keras.optimizers import SGD
from keras.layers import Dense, Dropout
from keras.utils import to_categorical

from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, classification_report

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

    # EXCLUDE THE MUTATIONS THAT RESULT IN EARLY TERMINATION
    data = data[data["Mutated AA"] != "Ter"]

    inputdata = data[['Conservation', 'CHOP780216',
                    'ONEK900102', 'BIOV880101', 'FUKS010108', 
                      'WERD780103' ]]


    # Convert categorical column to one hot
    unmut  = (tweak_to_hot(data, "Unmutated AA"))
    mut = (tweak_to_hot(data, "Mutated AA"))

    # INCLUDE OR NOT THE MUTATED AA
    train = np.c_[unmut, inputdata.values, mut]

    # Reduce labels (from 7 to 3)
    reduced_labels = data["Clinical Significance"].replace(reduced_labels_mapping)

    # Write out comparable csv
    csvout = inputdata.join(data["Unmutated AA"]).join(data["Mutated AA"]).join(reduced_labels)
    csvout.to_csv("pout.csv")

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

    predictions = model.predict(test)
    auc_score = roc_auc_score(test_label, predictions)
    report = classification_report(np.argmax(test_label, axis=1), np.argmax(predictions, axis=1), target_names=ordered_labels_reduced)
    # Ugly hack to get precsion, recall, f1, support
    pr_scores = np.array(list(map(float, report.strip().split('\n')[-1].split()[3:])))
    print(report)

    return loss_and_metrics_train, loss_and_metrics_test, auc_score, pr_scores

if __name__ == "__main__":
    n_folds = 10
    data, labels  = load_and_process("./data/BRC_full.csv")

    skf = StratifiedKFold(n_splits=n_folds, shuffle=True)
    train_stats = np.zeros((n_folds, 2))
    test_stats = np.zeros((n_folds, 2))
    roc_stats = np.zeros((n_folds,))
    pr_stats = np.zeros((n_folds, 4))

    i = 0
    for train_index, test_index in skf.split(data, labels[:,0]): # Silly munging of shape
            print("Running Fold", i+1, "/", n_folds)
            model = None # Clearing the NN.
            model = create_model(data.shape[1], labels.shape[1])
            train_stats[i],test_stats[i],roc_stats[i],pr_stats[i] = train_and_evaluate_model(model, data[train_index], labels[train_index], data[test_index], labels[test_index])
            i+=1

    train_mean = train_stats.mean(axis=0)
    train_std = train_stats.std(axis=0)

    test_mean = test_stats.mean(axis=0)
    test_std = test_stats.std(axis=0)

    roc_mean = roc_stats.mean()
    roc_std = roc_stats.std()

    pr_mean = pr_stats.mean(axis=0)
    pr_std = pr_stats.std(axis=0)

    result_str = """
    Training Accuracy Mean = {:1.4f} ± {:1.4f}
    Training Loss Mean = {:1.4f} ± {:1.4f}

    Test Accuracy Mean = {:.4f} ± {:1.4f}
    Test Loss Mean = {:1.4f} ± {:1.4f}
    Test ROC Area = {:1.4f} ± {:1.4f} 
    Test Precision Mean = {:1.4f} ± {:1.4f}  
    Test Recall Mean = {:1.4f} ± {:1.4f} 

    """.format(train_mean[1], train_std[1], train_mean[0], train_std[0], \
               test_mean[1], test_std[1], test_mean[0], test_std[0], \
               roc_mean, roc_std, \
               pr_mean[0], pr_std[0], pr_mean[1], pr_std[1])
    print(result_str)