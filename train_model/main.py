import os
import pickle
import numpy as np
from skimage.io import imread
from skimage.transform import resize
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from config import TrainingConfig

def load_or_preprocess_data(config):
    """Load preprocessed data or process raw images"""
    
    if (os.path.exists(config.DATA_DIR) and 
        os.path.exists(config.LABELS_DIR) and 
        not config.FORCE_RETRAIN):
        
        print("Loading preprocessed data...")
        data = np.load(config.DATA_DIR)
        labels = np.load(config.LABELS_DIR)
        print(f"Loaded {len(data)} samples from cache")
        
    else:
        print("Processing raw images...")
        data = []
        labels = []
        
        for category_index, category in enumerate(config.CATEGORIES):
            category_path = os.path.join(config.INPUT_DIR, category)
            
            if not os.path.exists(category_path):
                raise FileNotFoundError(f"Category path not found: {category_path}")
            
            files = os.listdir(category_path)
            print(f"Processing {len(files)} images from '{category}' category...")
            
            for file in files:
                img_path = os.path.join(category_path, file)
                try:
                    img = imread(img_path)
                    img = resize(img, config.IMAGE_SIZE)
                    data.append(img.flatten())
                    labels.append(category_index)
                except Exception as e:
                    print(f"Error processing {img_path}: {e}")
                    continue
        
        data = np.asarray(data)
        labels = np.asarray(labels)
        
        # Save preprocessed data
        if config.SAVE_PREPROCESSED:
            os.makedirs(os.path.dirname(config.DATA_DIR), exist_ok=True)
            np.save(config.DATA_DIR, data)
            np.save(config.LABELS_DIR, labels)
            print(f"Saved preprocessed data to {config.DATA_DIR}")
    
    return data, labels


def train_model(config):
    """Train the SVM classifier"""
    
    print("\n" + "="*70)
    print("PARKING SPOT CLASSIFIER TRAINING")
    print("="*70)
    
    # Load or preprocess data
    data, labels = load_or_preprocess_data(config)
    
    print(f"\nDataset statistics:")
    print(f"  Total samples: {len(data)}")
    print(f"  Feature dimensions: {data.shape[1]}")
    print(f"  Empty spots: {np.sum(labels == 0)}")
    print(f"  Occupied spots: {np.sum(labels == 1)}")
    
    # Train/test split
    x_train, x_test, y_train, y_test = train_test_split(
        data, 
        labels, 
        test_size=config.TEST_SIZE,
        shuffle=config.SHUFFLE,
        stratify=labels if config.STRATIFY else None,
        random_state=config.RANDOM_STATE
    )
    
    print(f"\nTrain/test split:")
    print(f"  Training samples: {len(x_train)}")
    print(f"  Testing samples: {len(x_test)}")
    
    # Train classifier with grid search
    print("\nTraining SVM classifier with grid search...")
    print(f"Parameters: {config.SVM_PARAMETERS}")
    
    classifier = SVC()
    grid_search = GridSearchCV(
        classifier, 
        config.SVM_PARAMETERS,
        cv=5,  # 5-fold cross-validation
        verbose=2,
        n_jobs=-1  # Use all available cores
    )
    
    grid_search.fit(x_train, y_train)
    
    print(f"\nBest parameters found: {grid_search.best_params_}")
    print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
    
    # Test performance
    best_estimator = grid_search.best_estimator_
    y_prediction = best_estimator.predict(x_test)
    
    accuracy = accuracy_score(y_test, y_prediction)
    print(f"\n{'='*70}")
    print(f"TEST SET ACCURACY: {accuracy*100:.2f}%")
    print(f"{'='*70}")
    
    # Detailed classification report
    print("\nClassification Report:")
    print(classification_report(
        y_test, 
        y_prediction, 
        target_names=config.CATEGORIES
    ))
    
    # Confusion matrix
    print("Confusion Matrix:")
    cm = confusion_matrix(y_test, y_prediction)
    print(f"                Predicted")
    print(f"                Empty  Occupied")
    print(f"Actual Empty    {cm[0][0]:5d}  {cm[0][1]:5d}")
    print(f"       Occupied {cm[1][0]:5d}  {cm[1][1]:5d}")
    
    # Save model
    os.makedirs(os.path.dirname(config.MODEL_PATH), exist_ok=True)
    
    with open(config.MODEL_PATH, 'wb') as file:
        pickle.dump(best_estimator, file)
    
    print(f"\n✓ Model saved to {config.MODEL_PATH}")
    print("="*70)
    
    return best_estimator, accuracy


def main():
    """Main training function"""
    config = TrainingConfig()
    
    try:
        model, accuracy = train_model(config)
        print(f"\n✓ Training completed successfully!")
        print(f"✓ Final accuracy: {accuracy*100:.2f}%")
        
    except Exception as e:
        print(f"\n✗ Training failed: {e}")
        raise


if __name__ == "__main__":
    main()