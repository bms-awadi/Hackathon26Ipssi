import shutil
import os

def store_curated():
    os.makedirs("data/curated", exist_ok=True)

    shutil.copy("data/clean/data.json", "data/curated/data.json")

    print(" Stored in curated zone")