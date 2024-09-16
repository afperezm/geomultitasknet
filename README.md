This repository contains code for the paper:

GeoMultiTaskNet: remote sensing unsupervised domain adaptation using geographical coordinates. Earth Vision Workshop. CVPR 2023.

## Requirements

- Python 3.10
- PyTorch 2.4 >=
- PyTorch Lightning 2.4 >=

## Usage

Generate train lists

````shell
find flair_aerial_train -name *.tif | sort | grep -E 'D006_|D008_|D013|D017_|D023_|D029_|D033_|D058_|D067_|D074_' > sub_train_imgs.txt
find flair_labels_train -name *.tif | sort | grep -E 'D006_|D008_|D013|D017_|D023_|D029_|D033_|D058_|D067_|D074_' > sub_train_masks.txt
````

Generate test lists

```shell
find flair_1_aerial_test -name *.tif | sort | grep -E 'D064_|D068_|D071_' > sub_test_imgs.txt
find flair_1_labels_test -name *.tif | sort | grep -E 'D064_|D068_|D071_' > sub_test_masks.txt
```
