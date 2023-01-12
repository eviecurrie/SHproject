import time
import wsipipe.datasets.camelyon17 as camelyon17
from wsipipe.datasets.dataset_utils import sample_dataset
from wsipipe.utils import np_to_pil
from wsipipe.load.annotations import visualise_annotations
from wsipipe.preprocess.tissue_detection import TissueDetectorGreyScale
from wsipipe.preprocess.tissue_detection import SimpleClosingTransform, SimpleOpeningTransform, GaussianBlur
from wsipipe.preprocess.tissue_detection import visualise_tissue_detection_for_slide
from wsipipe.preprocess.patching import GridPatchFinder, make_patchset_for_slide
from wsipipe.preprocess.patching import GridPatchFinder, make_patchset_for_slide
from wsipipe.preprocess.patching import make_patchsets_for_dataset
from wsipipe.preprocess.patching import make_and_save_patchsets_for_dataset
from wsipipe.preprocess.patching import GridPatchFinder, make_patchset_for_slide
from wsipipe.preprocess.patching import visualise_patches_on_slide
from sklearn.model_selection import train_test_split
from wsipipe.load.datasets.registry import register_loader
from wsipipe.load.datasets.camelyon17 import Camelyon17Loader


data = camelyon17.training(cam17_path='/data/ec259/camelyon17/raw')
register_loader(Camelyon17Loader)

# split train and test 80/20
train_dset, test_dset = train_test_split(data, test_size=0.2)
dset_loader = Camelyon17Loader()

# split training into train and validate (80/20)
train_dset, validate_dset = train_test_split(train_dset, test_size=0.2)
row = train_dset.iloc[0]

# View slide
with dset_loader.load_slide(row.slide) as slide:
    thumb = slide.get_thumbnail(5)

np_to_pil(thumb)

labelled_image = visualise_annotations(
    row.annotation,
    row.slide,
    dset_loader,
    5,
    row.label
)
np_to_pil(labelled_image * 100)

# -- BACKGROUND SUBTRACTION --

tisdet = TissueDetectorGreyScale(grey_level=0.85)
tissmask = tisdet(thumb)
np_to_pil(tissmask)

prefilt = GaussianBlur(sigma=2)
morph = [SimpleOpeningTransform(), SimpleClosingTransform()]
tisdet = TissueDetectorGreyScale(
    grey_level=0.75,
    morph_transform=morph,
    pre_filter=prefilt
)
tissmask = tisdet(thumb)
np_to_pil(tissmask)

visualise_tissue_detection_for_slide(row.slide, dset_loader, 5, tisdet)

# -- PATCH EXTRACTION --

patchfinder = GridPatchFinder(patch_level=1, patch_size=512, stride=512, labels_level=5)
pset = make_patchset_for_slide(row.slide, row.annotation, row.label, dset_loader, tisdet, patchfinder)

print("STARTING PATCH EXTRACTION: ")
start = time.time()

# Patches for the whole dataset:
psets_for_dset = make_and_save_patchsets_for_dataset(
    dataset=train_dset,
    loader=dset_loader,
    tissue_detector=tisdet,
    patch_finder=patchfinder,
    output_dir='/data/ec259/camelyon17/raw/patches'
)

print("FINISHED PATCH EXTRACTION: " + str(time.time() - start))

def get_train_dset():
    return train_dset

def get_test_dset():
    return test_dset

def get_validate_dset():
    return validate_dset

# ----------- Patches for a single slide ----------------
# patchfinder = GridPatchFinder(patch_level=1, patch_size=512, stride=512, labels_level=5)
# pset = make_patchset_for_slide(row.slide, row.annotation, dset_loader, tisdet, patchfinder)
# visualise_patches_on_slide(pset, vis_level=5)
