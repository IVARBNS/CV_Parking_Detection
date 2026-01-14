```markdown
# Parking Spot Classifier Training

This module trains an SVM (Support Vector Machine) classifier to detect whether parking spots are empty or occupied.

## Dataset Structure
```

Data/
└── clf-data/
├── empty/ # Images of empty parking spots
│ ├── img1.jpg
│ ├── img2.jpg
│ └── ...
└── not_empty/ # Images of occupied parking spots
├── img1.jpg
├── img2.jpg
└── ...

````

## Usage

### 1. Prepare your dataset
- Collect images of empty and occupied parking spots
- Place them in the appropriate folders under `Data/clf-data/`
- Recommended: At least 100+ images per category

### 2. Configure training parameters
Edit `config.py` to adjust:
- Image size
- Train/test split ratio
- SVM hyperparameters
- Data paths

### 3. Train the model
```bash
cd train_model
python main.py
````

## Output

The training process will generate:

- `Data/model/data.npy` - Preprocessed image data
- `Data/model/labels.npy` - Image labels
- `Data/model/model.p` - Trained SVM model

## Training Process

1. **Data Loading**: Loads images from `clf-data` directory
2. **Preprocessing**: Resizes images to 15x15 pixels and flattens
3. **Train/Test Split**: 80% training, 20% testing (stratified)
4. **Grid Search**: Finds optimal SVM hyperparameters (C and gamma)
5. **Evaluation**: Tests model on held-out test set
6. **Saving**: Saves the best model for inference

## Model Performance

After training, you'll see:

- Overall accuracy
- Classification report (precision, recall, F1-score)
- Confusion matrix

## Tips for Better Accuracy

1. **Balanced Dataset**: Equal number of empty and occupied images
2. **Diverse Conditions**: Include various lighting, weather, angles
3. **Quality Images**: Clear, well-framed parking spots
4. **Sufficient Data**: More training data = better generalization
5. **Consistent Framing**: Similar crop sizes and perspectives

## Retraining

To retrain from scratch:

```python
# In config.py
FORCE_RETRAIN = True
```

This will ignore cached preprocessed data and reprocess all images.

```

```
