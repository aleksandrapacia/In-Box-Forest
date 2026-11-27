Datasets used to download scenes
================================

Platform: Microsoft Planetary Computer
Catalog:  https://planetarycomputer.microsoft.com/api/stac/v1
Docs:     https://planetarycomputer.microsoft.com/docs/quickstarts/reading-stac/

Download only the window inside the user polygon (max 40 km^2).
Do not download a full Sentinel scene.

1. Sentinel-2 Level-2A
----------------------
Collection id: sentinel-2-l2a
Dataset page:  https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a
Product:       surface reflectance (L2A), not L1C
What it is:    optical scenes for the vegetation indices

Search filters:
- intersects the drawn polygon
- one leaf-on season (Europe: May-September)
- the same month one year earlier, for change
- cloud cover below about 20%
- keep the least-cloudy scene in each period

Assets to read:
- B02  blue            10 m   used in EVI
- B04  red             10 m   used in NDVI and EVI
- B05  red edge        20 m   used in NDRE
- B08  NIR             10 m   used in NDVI, NDMI, NBR, EVI
- B8A  narrow NIR      20 m   used in NDRE
- B11  SWIR            20 m   used in NDMI
- B12  SWIR            20 m   used in NBR
- SCL  scene class     20 m   cloud, shadow, cirrus, snow mask

Reflectance is stored as integers. Divide B02, B04, B05, B08, B8A, B11, B12 by 10000 before any index.
NDRE, NDMI, and NBR use 20 m bands. Compute those at 20 m.

Indices from this dataset:
- NDVI  (B08, B04)
- EVI   (B08, B04, B02)
- NDMI  (B08, B11)
- NDRE  (B8A, B05)
- NBR   (B08, B12)

2. Sentinel-1 RTC
-----------------
Collection id: sentinel-1-rtc
Dataset page:  https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc
Product:       radiometrically terrain corrected GRD
What it is:    radar scenes for canopy structure (works through cloud)

Search filters:
- intersects the drawn polygon
- same month as the chosen Sentinel-2 scene
- IW mode
- polarizations VV and VH
- about 3 to 5 dates, then average them
- do not use a single date (speckle)

Assets to read:
- vv   co-polarized backscatter
- vh   cross-polarized backscatter

If the values are in dB, convert to linear power before the ratio:
linear = 10 ** (dB / 10)

Index from this dataset:
- RVI = 4 * VH / (VV + VH)   on linear power, after the monthly mean

Not a scene (do not treat this as a download of satellite scenes)
-----------------------------------------------------------------
ESA WorldCover is a land-cover map, used only as a forest mask.
Collection id: esa-worldcover
Dataset page:  https://planetarycomputer.microsoft.com/dataset/esa-worldcover
Class 10 = trees. Compute index means on class 10 pixels only.
