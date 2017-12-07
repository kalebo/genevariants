import pandas as pd
import numpy as np 

from keras.models import Sequential
from keras.optimizers import SGD
from keras.layers import Dense, Dropout
from keras.utils import to_categorical

ordered_labels_full = ['Benign', 
                    'Benign/Likely benign',
                    'Likely benign',
                    'Conflicting interpretations of pathogenicity',
                    'Likely pathogenic',
                    'Pathogenic/Likely pathogenic',
                    'Pathogenic']

ordered_labels_reduced = [
                    'Benign', 
                    'Indeterminant'
                    'Pathogenic']

tweak_to_hot = lambda df,col: to_categorical(df[col].astype("category").cat.codes)

data = pd.read_csv("./data/BRC_full.csv")
inputdata = data[['Conservation', 'PALJ810102', 'CHOP780216',
                'ONEK900102', 'BIOV880101', 'FUKS010108', 'CEDJ970102', 'CHAM820101',
                'FAUJ880107', 'MAXF760104', 'ZIMJ680104', 'GEIM800109', 'GEOR030106',
                'KARS160111', 'DIGM050101', 'WERD780103', 'QIAN880115']]


# Convert categorical column to one hot
unmut  = (tweak_to_hot(data, "Unmutated AA"))
mut = (tweak_to_hot(data, "Mutated AA"))

train = np.c_[unmut, inputdata.values, mut]


# Convert label to ordered category
label_cat = pd.Categorical(data["Clinical Significance"], categories=ordered_labels, ordered=True)

# convert label_cat to one hot encoding
labels = to_categorical(pd.Series(label_cat).cat.codes)

model = Sequential()

model.add(Dropout(0.4, input_shape=(train.shape[1],) ))
model.add(Dense(100, kernel_initializer='normal', activation='relu'))
model.add(Dense(60, kernel_initializer='normal', activation='relu'))
model.add(Dense(30, kernel_initializer='normal', activation='relu'))
model.add(Dense(7, kernel_initializer='normal', activation='sigmoid'))

sgd = SGD(lr=0.10, momentum=0.9, decay=0.0, nesterov=False)
#model.compile(loss='binary_crossentropy', optimizer=sgd, metrics=['accuracy'])
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

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
model.fit(train, labels, epochs=30, batch_size=40)

loss_and_metrics = model.evaluate(train, labels, batch_size=128)
print(loss_and_metrics)