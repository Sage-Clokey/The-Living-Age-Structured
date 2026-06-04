---
license: cc-by-nc-4.0
task_categories:
- image-to-3d
library_name:
- open3d
---

# MaizeField3D: A Curated 3D Point Cloud Dataset of Field-Grown Plants From A Maize Diversity Panel

[Paper link](https://huggingface.co/papers/2503.07813) | [Project page](https://baskargroup.github.io/MaizeField3D/)

## Overview
The use of artificial intelligence (AI) in three-dimensional (3D) agricultural research, especially for maize, 
has been limited due to the lack of large-scale, diverse datasets. While 2D image datasets are widely available, 
they fail to capture key structural details like leaf architecture, plant volume, and spatial arrangements—information 
that 3D data can provide. To fill this gap, we present a carefully curated dataset of 3D point clouds representing fully 
field-grown maize plants with diverse genetic backgrounds. This dataset is designed to be AI-ready, offering valuable 
insights for advancing agricultural research.

Our dataset includes over 1,000 high-quality point clouds of maize plants, collected using a Terrestrial Laser Scanner. 
These point clouds encompass various maize varieties, providing a comprehensive and diverse dataset. To enhance usability, 
we applied graph-based segmentation to isolate individual leaves and stalks. Each leaf is consistently color-labeled based 
on its position in the plant (e.g., all first leaves share the same color, all second leaves share another color, and so on). 
Similarly, all stalks are assigned a unique, distinct color.

A rigorous quality control process was applied to manually correct any segmentation or leaf-ordering errors, ensuring 
accurate segmentation and consistent labeling. This process facilitates precise leaf counting and structural analysis. 
In addition, the dataset includes metadata describing point cloud quality, leaf count, and the presence of tassels and maize cobs.

To support a wide range of AI applications, we also provide code that allows users to sub-sample the point clouds, 
creating versions with user-defined resolutions (e.g., 100k, 50k, 10k points) through uniform downsampling. 
Every version of the dataset has been manually quality-checked to preserve plant topology and structure. 
This dataset sets the stage for leveraging 3D data in advanced agricultural research, particularly for maize phenotyping and plant structure studies.

## Dataset Directory Structure

```
MaizeField3D/
├── MaizeField3d/               # Main Python package directory
│    ├── __init__.py            # Initialize the Python package
│    ├── dataset.py             # Python file to define dataset access functions
├── setup.py                    # Package setup configuration
├── README.md                   # Package description
├── requirements.txt            # Dependencies
├── MANIFEST.in                 # Non-Python files to include in the package
├── Metadata.xlsx               # Metadata for your dataset
├── PointCloudDownsampler.py    # Python script for downsampling
└── datasets/                   # Directory for zipped datasets
    ├── FielGrwon_ZeaMays_RawPCD_100k.zip
    ├── FielGrwon_ZeaMays_RawPCD_50k.zip
    ├── FielGrwon_ZeaMays_RawPCD_10k.zip
    ├── FielGrwon_ZeaMays_SegmentedPCD_100k.zip
    ├── FielGrwon_ZeaMays_SegmentedPCD_50k.zip
    ├── FielGrwon_ZeaMays_SegmentedPCD_10k.zip
    ├── FielGrwon_ZeaMays_Reconstructed_Surface_dat.zip
    ├── FielGrwon_ZeaMays_Reconstructed_Surface_stl.zip
```

### Contents of the `.zip` Files
- **`FielGrwon_ZeaMays_RawPCD_100k.zip`**:
  - Contains 1045 `.ply` files. Each file has 100K point cloud representing an entire maize plant.

- **`FielGrwon_ZeaMays_RawPCD_50k.zip`**:
  - Contains 1045 `.ply` files. Each file has 50K point cloud representing an entire maize plant.

- **`FielGrwon_ZeaMays_RawPCD_10k.zip`**:
  - Contains 1045 `.ply` files. Each file has 10K point cloud representing an entire maize plant.
    
- **`FielGrwon_ZeaMays_SegmentedPCD_100k.zip`**:
  - Contains 520 `.ply` files. Each file represents a segmented maize plant by 100K point cloud focusing on specific plant parts.

- **`FielGrwon_ZeaMays_SegmentedPCD_50k.zip`**:
  - Contains 520 `.ply` files. Each file represents a segmented maize plant by 50K point cloud focusing on specific plant parts.

- **`FielGrwon_ZeaMays_SegmentedPCD_10k.zip`**:
  - Contains 520 `.ply` files. Each file represents a segmented maize plant by 10K point cloud focusing on specific plant parts.

- **`FielGrwon_ZeaMays_Reconstructed_Surface_stl.zip`**:
  - Contains 520 `.ply` files. Each file represents the reconstructed surfaces of the maize plant leaves generated from a procedural model.

- **`FielGrwon_ZeaMays_Reconstructed_Surface_dat.zip`**:
  - Contains 520 `.ply` files. Each file represents the reconstructed NURBS surface information including degree, knot vector, and control point values.

**License**
```
CC-BY-NC-4.0
```

### How to Access
1. **Download the `.zip` files**:
   - [FielGrwon_ZeaMays_RawPCD_100k.zip](https://huggingface.co/datasets/BGLab/AgriField3D/blob/main/datasets/FielGrwon_ZeaMays_RawPCD_100k.zip)
   - [FielGrwon_ZeaMays_RawPCD_50k.zip](https://huggingface.co/datasets/BGLab/AgriField3D/blob/main/datasets/FielGrwon_ZeaMays_RawPCD_50k.zip)
   - [FielGrwon_ZeaMays_RawPCD_10k.zip](https://huggingface.co/datasets/BGLab/AgriField3D/blob/main/datasets/FielGrwon_ZeaMays_RawPCD_10k.zip)
   - [FielGrwon_ZeaMays_SegmentedPCD_100k.zip](https://huggingface.co/datasets/BGLab/AgriField3D/blob/main/datasets/FielGrwon_ZeaMays_SegmentedPCD_100k.zip)
   - [FielGrwon_ZeaMays_SegmentedPCD_50k.zip](https://huggingface.co/datasets/BGLab/AgriField3D/blob/main/datasets/FielGrwon_ZeaMays_SegmentedPCD_50k.zip)
   - [FielGrwon_ZeaMays_SegmentedPCD_10k.zip](https://huggingface.co/datasets/BGLab/AgriField3D/blob/main/datasets/FielGrwon_ZeaMays_SegmentedPCD_10k.zip)
2. **Extract the files**:
   ```bash
   unzip FielGrwon_ZeaMays_RawPCD_100k.zip
   unzip FielGrwon_ZeaMays_RawPCD_50k.zip
   unzip FielGrwon_ZeaMays_RawPCD_10k.zip
   unzip FielGrwon_ZeaMays_SegmentedPCD_100k.zip
   unzip FielGrwon_ZeaMays_SegmentedPCD_50k.zip
   unzip FielGrwon_ZeaMays_SegmentedPCD_10k.zip
   ```

3. Use the extracted `.ply` files in tools like:
   - MeshLab
   - CloudCompare
   - Python libraries such as `open3d` or `trimesh`.

### Example Code to Visualize the `.ply` Files in Python
```python
import open3d as o3d

# Load and visualize a PLY file from the dataset
pcd = o3d.io.read_point_cloud("FielGrwon_ZeaMays_RawPCD_100k/0001.ply")
o3d.visualization.draw_geometries([pcd])
```

**Citation**
If you find this dataset useful in your research, please consider citing our paper as follows: 
```
@article{kimara2025AgriField3D,
        title = "AgriField3D: A Curated 3D Point Cloud Dataset of Field-Grown Plants from a Maize Diversity Panel",
        author = "Elvis Kimara, Mozhgan Hadadi, Jackson Godbersen, Aditya Balu, Zaki Jubery, Adarsh Krishnamurthy, Patrick Schnable, Baskar Ganapathysubramanian"
        year = "2025"
}
```