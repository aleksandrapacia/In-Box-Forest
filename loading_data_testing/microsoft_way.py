import pystac
import planetary_computer as pc
import rasterio
import matplotlib.pyplot as plt
import numpy as np

item_url = "https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2C_MSIL2A_20261028T095121_R079_T34UCA_20261028T132804"
fill_url = "https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a/items/S2B_MSIL2A_20261023T095049_R079_T34UCA_20261023T134641"
# Load the individual item metadata
item = pystac.Item.from_file(item_url) # metadata
fill_item = pystac.Item.from_file(fill_url)

""" ITEM """
# Open one of the data assets (other asset keys to use: 'B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B11', 'B12', 'B8A', 'SCL', 'WVP', 'visual')
# AOT - air above the place, how much dust and haze was in the air 
# visual - a photo made for eyes, true-color image (0,255) pixels
asset = pc.sign(item).assets["visual"].href # sign returns a copy of it
fill_asset = pc.sign(fill_item).assets["visual"].href
# Read the asset from storage and print the metadata
with rasterio.open(asset) as src:
	# outshape = (band, rows, columns)
	img = src.read(out_shape=(3,800,800))
	print(src.count)
	print(src.dtypes)
	print(src.descriptions)

# Identifying bands in asset
for key, asset in item.assets.items():
	print(key, "-", asset.title)

""" FILL ITEM """
fill_asset = pc.sign(item).assets["visual"].href 
print(" >>> FILL ITEM <<<")
with rasterio.open(fill_asset) as src:
	img = src.read(out_shape=(3,800,800))
	print(src.count)
	print(src.dtypes)
	print(src.descriptions)



""" Calculations """
# Giving permission to read GeoTIFF
signed = pc.sign(item)
signed_fill = pc.sign(fill_item)

# Retrieving important bands
with rasterio.open(signed.assets["B04"].href) as src:
    red = src.read(1, out_shape=(800, 800)).astype("float32") / 10000
with rasterio.open(signed.assets["B08"].href) as src:
    nir = src.read(1, out_shape=(800, 800)).astype("float32") / 10000
with rasterio.open(signed.assets["B11"].href) as src:
    swir = src.read(1, out_shape=(800, 800)).astype("float32") / 10000
with rasterio.open(signed.assets["SCL"].href) as src:
    scl = src.read(1, out_shape=(800, 800))
with rasterio.open(signed_fill.assets["visual"].href) as src: # visual band for filling
    visual_fill = src.read(out_shape=(3, 800, 800))
# Fill bands 
with rasterio.open(signed_fill.assets["B04"].href) as src:
    red_fill = src.read(1, out_shape=(800, 800)).astype("float32") / 10000
with rasterio.open(signed_fill.assets["B08"].href) as src:
    nir_fill = src.read(1, out_shape=(800, 800)).astype("float32") / 10000
with rasterio.open(signed_fill.assets["B11"].href) as src:
    swir_fill = src.read(1, out_shape=(800, 800)).astype("float32") / 10000
with rasterio.open(signed_fill.assets["SCL"].href) as src:
    scl_fill = src.read(1, out_shape=(800, 800))
with rasterio.open(signed_fill.assets["visual"].href) as src:
    visual_fill = src.read(out_shape=(3, 800, 800))

# Calculating NDBI
ndbi = (swir - nir) / (swir + nir)

# Calculating NDVI
# Healthy green pixel is about 0.45 in NIR and 0.04 in Red
ndvi = (nir - red) / (nir + red)
print(f"NDVI values : min : max : mean -->{ndvi.min()}: {ndvi.max()}: {ndvi.mean()}")

# Classes 
cloud = np.isin(scl, [0, 1, 3, 8, 9, 10, 11])
ndvi = np.where(cloud, np.nan, ndvi)
ndbi = np.where(cloud, np.nan, ndbi)
print(np.nanmin(ndvi), np.nanmax(ndvi), np.nanmean(ndvi))

rgb = img.transpose(1, 2, 0).copy()
rgb[cloud] = 255

# Filling 
cloud_fill = np.isin(scl_fill, [0, 1, 3, 8, 9, 10, 11])
ndvi_fill = (nir_fill - red_fill) / (nir_fill + red_fill)
ndbi_fill = (swir_fill - nir_fill) / (swir_fill + nir_fill)
ndvi_fill[cloud_fill] = np.nan
ndbi_fill[cloud_fill] = np.nan
ndvi[cloud] = ndvi_fill[cloud]
ndbi[cloud] = ndbi_fill[cloud]

rgb_fill = visual_fill.transpose(1, 2, 0)
rgb[cloud] = rgb_fill[cloud]
rgb[cloud & cloud_fill] = 255

# Graph
fig, axes = plt.subplots(
    1, 5,
    figsize=(18, 6),
    gridspec_kw={"width_ratios": [1, 1, 0.04, 1, 0.04]},
)
axes[0].imshow(img.transpose(1, 2, 0))
axes[0].imshow(rgb)
axes[0].set_title("True color")
axes[0].axis("off")
ndvi_image = axes[1].imshow(ndvi, cmap="RdYlGn", vmin=-0.2, vmax=0.9)
axes[1].set_title("NDVI")
axes[1].axis("off")
fig.colorbar(ndvi_image, cax=axes[2])
ndbi_image = axes[3].imshow(ndbi, cmap="RdBu_r", vmin=-0.4, vmax=0.4)
axes[3].set_title("NDBI")
axes[3].axis("off")
fig.colorbar(ndbi_image, cax=axes[4])
plt.tight_layout()
plt.savefig('no_cloud.png')
plt.show()


