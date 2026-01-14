import os

class TrainingConfig:
    """Configuration for model training"""
    
    # Data paths
    INPUT_DIR = r'Data\clf-data'
    DATA_DIR = r'Data\model\data.npy'
    LABELS_DIR = r'Data\model\labels.npy'
    MODEL_PATH = r'Data\model\model.p'
    
    # Categories
    CATEGORIES = ['empty', 'not_empty']
    
    # Image preprocessing
    IMAGE_SIZE = (15, 15)  # Resize images to 15x15
    
    # Train/test split
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    SHUFFLE = True
    STRATIFY = True  # Maintain class distribution
    
    # SVM parameters for grid search
    SVM_PARAMETERS = [
        {
            'gamma': [0.01, 0.001, 0.0001],
            'C': [1, 10, 100, 1000]
        }
    ]
    
    # Training options
    FORCE_RETRAIN = False  # Set to True to force retraining
    SAVE_PREPROCESSED = True  # Save preprocessed data as .npy files