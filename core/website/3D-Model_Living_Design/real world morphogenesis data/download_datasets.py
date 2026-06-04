"""
Download real-world plant morphogenesis 3D scan datasets.

Datasets:
  1. Chickpea 3D (Zenodo 4018242)       ~1.7 GB   PLY point clouds + meshes
  2. Pheno4D maize + tomato (Uni Bonn)  unknown   labelled point clouds, 440M pts
  3. Crops3D 8-crop dataset (Figshare)  unknown   point clouds, 8 species
  4. MaizeField3D (HuggingFace)         large     1,045 field scans, multi-res

NOT downloaded here (requires registration form):
  - UNL-3DPPD: https://plantvision.unl.edu/datasets/download-3d-plant-phenotyping-dataset-unl-3dppd/

Run:
  pip install requests tqdm
  python download_datasets.py
"""

import os
import requests
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def download_file(url, dest_path, label):
    print(f"\n[{label}] Downloading to: {dest_path}")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    if os.path.exists(dest_path):
        print(f"  Already exists, skipping.")
        return

    try:
        r = requests.get(url, stream=True, timeout=60)
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(dest_path, "wb") as f, tqdm(
            desc=label,
            total=total,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))
        print(f"  Done.")
    except Exception as e:
        print(f"  FAILED: {e}")


def download_chickpea():
    """
    Chickpea 3D photogrammetric reconstructions — 6 genotypes across development stages.
    PLY format (point clouds + meshed models). ~1.7 GB total.
    Source: https://zenodo.org/records/4018242
    """
    dest = os.path.join(BASE_DIR, "chickpea_3D_zenodo", "chickpea_3D.zip")
    download_file(
        url="https://zenodo.org/api/records/4018242/files-archive",
        dest_path=dest,
        label="Chickpea 3D (Zenodo)",
    )
    print("  Unzip to: chickpea_3D_zenodo/")
    print("  Contains: PLY point clouds + meshes for 6 chickpea genotypes")


def download_pheno4d():
    """
    Pheno4D — time-series maize and tomato point clouds.
    7 maize plants (84 clouds, ~90M pts) + 7 tomato plants (140 clouds, ~350M pts).
    Includes organ-level labels.
    Source: https://www.ipb.uni-bonn.de/data/pheno4d/
    """
    dest = os.path.join(BASE_DIR, "pheno4d_maize_tomato", "Pheno4D.zip")
    download_file(
        url="https://www.ipb.uni-bonn.de/html/projects/Pheno4D/Pheno4D.zip",
        dest_path=dest,
        label="Pheno4D (Uni Bonn)",
    )
    print("  Unzip to: pheno4d_maize_tomato/")
    print("  Contains: labelled time-series point clouds for maize + tomato")


def download_crops3d():
    """
    Crops3D — 8 crop species (cabbage, cotton, maize, potato, rapeseed, rice, tomato, wheat).
    1,230 samples. Instance segmentation + organ segmentation labels.
    License: CC BY 4.0
    Source: https://springernature.figshare.com/articles/dataset/27313272
    """
    dest = os.path.join(BASE_DIR, "crops3d_8species", "Crops3D.zip")
    download_file(
        url="https://springernature.figshare.com/ndownloader/files/50027964",
        dest_path=dest,
        label="Crops3D (Figshare)",
    )
    print("  Unzip to: crops3d_8species/")
    print("  Contains: 1,230 point clouds across 8 crop species")


def download_maizefield3d():
    """
    MaizeField3D — 1,045 field-grown maize point clouds from TLS (terrestrial laser scanner).
    Multi-resolution: 100k, 50k, 10k points per cloud. Organ annotations included.
    Source: https://huggingface.co/datasets/BGLab/MaizeField3D

    Requires huggingface_hub:
      pip install huggingface_hub
    """
    try:
        from huggingface_hub import snapshot_download
        dest = os.path.join(BASE_DIR, "maizefield3d_hf")
        print(f"\n[MaizeField3D (HuggingFace)] Downloading to: {dest}")
        if os.path.exists(dest) and os.listdir(dest):
            print("  Already exists, skipping.")
            return
        snapshot_download(
            repo_id="BGLab/MaizeField3D",
            repo_type="dataset",
            local_dir=dest,
        )
        print("  Done.")
    except ImportError:
        print("\n[MaizeField3D] SKIPPED — install huggingface_hub first:")
        print("  pip install huggingface_hub")
    except Exception as e:
        print(f"\n[MaizeField3D] FAILED: {e}")


def print_manual_steps():
    print("\n" + "=" * 60)
    print("MANUAL STEPS REQUIRED")
    print("=" * 60)
    print("""
UNL-3DPPD (maize, multi-genotype):
  Requires registration at:
  https://plantvision.unl.edu/datasets/download-3d-plant-phenotyping-dataset-unl-3dppd/
  Fill out the form and download will be provided.

After downloading zips, extract in place:
  python -c "import zipfile, os; [zipfile.ZipFile(f).extractall(os.path.dirname(f)) for f in ['chickpea_3D_zenodo/chickpea_3D.zip', 'pheno4d_maize_tomato/Pheno4D.zip', 'crops3d_8species/Crops3D.zip'] if os.path.exists(f)]"
""")


if __name__ == "__main__":
    print("Plant Morphogenesis 3D Dataset Downloader")
    print("=" * 60)
    print(f"Output folder: {BASE_DIR}\n")

    download_chickpea()
    download_pheno4d()
    download_crops3d()
    download_maizefield3d()
    print_manual_steps()
