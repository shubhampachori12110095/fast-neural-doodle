from sklearn.cluster import KMeans
import scipy
import numpy as np
import h5py
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--n_colors', type=int, help='How many distinct colors does mask have.')
parser.add_argument('--style_image', help='Path to style image.')
parser.add_argument('--style_mask', help='Path to mask for style.')
parser.add_argument('--target_mask', help='Path to target mask.')
parser.add_argument('--out_hdf5', default='masks.hdf5', help='Where to store hdf5 file.')

args = parser.parse_args()

# Load style
img_style = scipy.misc.imread(args.style_image)

# Load masks
mask_style = scipy.misc.imread(args.style_mask)
mask_target = scipy.misc.imread(args.target_mask)

# Save shapes
style_shape = mask_style.shape
target_shape = mask_target.shape

# Run K-Means to get rid of possible intermediate colors
style_flatten = mask_style.reshape(style_shape[0]*style_shape[1], -1)
target_flatten = mask_target.reshape(target_shape[0]*target_shape[1], -1)

kmeans = KMeans(n_clusters=args.n_colors, random_state=0).fit(style_flatten)

# Predict masks
labels_style = kmeans.predict(style_flatten.astype(float))
labels_target = kmeans.predict(target_flatten.astype(float))

style_kval = labels_style.reshape(style_shape[0], style_shape[1])
target_kval = labels_target.reshape(target_shape[0], target_shape[1])

# Dump
f = h5py.File(args.out_hdf5, 'w')

for i in range(args.n_colors):
    f['style_mask_%d' % i] = (style_kval == i).astype(float)
    f['target_mask_%d' % i] = (target_kval == i).astype(float)

# Torch style image save
f['style_img'] = img_style.transpose(2, 0, 1).astype(float)/255.
f['n_colors'] = np.array([args.n_colors]) # Toch do not want to read just number

f.close()

print ('Done!')