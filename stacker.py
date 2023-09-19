import sys
import tifffile
import numpy as np
from pathlib import Path

import re

def sort_key(path):
    # Extract numbers from the path using regular expression
    numbers = re.findall(r'\d+', str(path))
    
    # Convert extracted numbers to integers and return them as sorting key
    return [int(num) for num in numbers]

root = sys.argv[1]
divider = sys.argv[2] if len(sys.argv) > 2 else 1

paths = sorted(list(Path(root).glob("*.tif")), key=sort_key)

ordered_image_files = []
for img in paths:
    ordered_image_files.append(tifffile.imread(img))

img = np.stack(ordered_image_files, axis=-1)

tifffile.imwrite(f"{paths[0].parent}.tif", img // divider, photometric='rgb')
