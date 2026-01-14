import os, json, pickle
import numpy as np
from skimage.io import imread
from skimage.transform import resize
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score


# Prepare Data
input_dir = r'Data\clf-data'
categories = ['empty', 'not_empty']

data_dir = r'Data\model\data.npy'
labels_dir = r'Data\model\labels.npy'

if os.path.exists(data_dir) and os.path.exists(labels_dir):
    data = np.load(data_dir)
    labels = np.load(labels_dir)
else:
    data = []
    labels = []
    for category_index, category in enumerate(categories):
        category_path = os.path.join(input_dir, category)
        for file in os.listdir(category_path):
            img_path = os.path.join(category_path, file)
            img = imread(img_path)
            img = resize(img, (15, 15))
            data.append(img.flatten())
            labels.append(category_index)

    # Save as .npy files
    np.save(data_dir, data)
    np.save(labels_dir, labels)

data = np.asarray(data)
labels = np.asarray(labels)

# Train / Test split
x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, stratify=labels)

# Train classifier
classifier = SVC()

parameters = [
    {
        'gamma': [0.01, 0.001, 0.0001],
        'C': [1, 10, 100, 1000]
    }
]

grid_search = GridSearchCV(classifier, parameters)

grid_search.fit(x_train, y_train)

# Test performance

best_estimator = grid_search.best_estimator_

y_prediction = best_estimator.predict(x_test)

score = accuracy_score(y_prediction, y_test)

print(f'{score*100}% of samples were correctly classified!')

model_path = r'Data\model\model.p'

# Create the directory if it doesn't exist
os.makedirs(os.path.dirname(model_path), exist_ok=True)

if not os.path.exists(model_path):
    with open(model_path, 'wb') as file:
        pickle.dump(best_estimator, file)