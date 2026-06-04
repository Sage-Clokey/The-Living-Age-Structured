from setuptools import setup, find_packages

setup(
    name="AgriField3D",  # Package name
    version="1.0.0",  # Initial version
    description="AgriField3D: A curated 3D point cloud dataset of field-grown maize plants",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://huggingface.co/datasets/BGLab/AgriField3D/tree/main/datasets",  
    author="Mozhgan Hadadi",
    author_email="mozhganh@iastate.edu",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
        "open3d",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)