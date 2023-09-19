# Satellite Land Use Segmentation

This repository contains scripts for downloading Sentinel-2 satellite imagery and
pre-processing it for the 
[ibm-nasa-geospatial/Prithvi-100M-multi-temporal-crop-classification](https://huggingface.co/ibm-nasa-geospatial/Prithvi-100M-multi-temporal-crop-classification) model.

It also contains an Apptainer container recipe providing a software environment for
running the model locally.

# Usage

## Downloading imagery

``` sh
python download_images.py coords.json
```
`coords.json` is a mandatory positional argument. It should be a JSON document where each key represents a location name, and its corresponding value is a list of latitude/longitude pairs that define the desired polygon for that location.

## Pre-processing imagery

``` sh
(cd <input_dir>; unzip \*.zip)
python stacker.py <input_dir> [<value_divisor>]
```

`value_divisor` is an optional argument that divides the input pixel values, which may
improve model performance. It defaults to 1, which does not change the pixel values.

## Running the model

Upload the `.tif` file to the model's demo [space](https://huggingface.co/spaces/ibm-nasa-geospatial/Prithvi-100M-multi-temporal-crop-classification-demo) and click submit.
