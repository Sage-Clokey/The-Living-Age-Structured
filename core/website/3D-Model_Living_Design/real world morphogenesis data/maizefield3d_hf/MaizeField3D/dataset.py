import os
from pathlib import Path

# Metadata and dataset folder paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "datasets"

def get_dataset_info():
    """Print information about available datasets."""
    datasets = {
        "Raw Point Clouds": [
            "FielGrwon_ZeaMays_RawPCD_100k.zip",
            "FielGrwon_ZeaMays_RawPCD_50k.zip",
            "FielGrwon_ZeaMays_RawPCD_10k.zip",
        ],
        "Segmented Point Clouds": [
            "FielGrwon_ZeaMays_SegmentedPCD_100k.zip",
            "FielGrwon_ZeaMays_SegmentedPCD_50k.zip",
            "FielGrwon_ZeaMays_SegmentedPCD_10k.zip",
        ],
    }
    return datasets

def download_dataset(dataset_name, target_dir):
    """
    Extract the specified dataset to the target directory.
    """
    import zipfile
    dataset_path = DATASET_DIR / dataset_name

    if not dataset_path.exists():
        raise FileNotFoundError(f"{dataset_name} not found in datasets folder.")

    with zipfile.ZipFile(dataset_path, 'r') as zip_ref:
        zip_ref.extractall(target_dir)
    print(f"Dataset {dataset_name} extracted to {target_dir}.")
