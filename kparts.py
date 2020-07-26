# ----------------------------------------------------------------------------
# -- Constants for the parts to be printed
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- January-2017
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------


# Taking the same axis as the 3D printer:
#
#    Z   Y
#    | /               
#    |/___ X
#


import kcomp

# Separation from the end of the linear bearing to the end of the piece
# on the Heigth dimension (Z)

OUT_SEP_H = 2. # Originally 3.

# Minimum separation between the bearings, on the slide direction
MIN_BEAR_SEP = 3.0


# Radius to fillet the sides
FILLT_R = 3.0 # larger to 2.0

# Space for the sliding rod, to be added to its radius, and to be cut
ROD_SPACE = 1.5
ROD_SPACE_MIN = 1.

# tolerance on their length for the bearings. Larger because the holes
# usually are too tight and it doesn't matter how large is the hole
#TOL_BEARING_L = 2.0 # printed in black and was too loose
TOL_BEARING_L = 1.0 # reduced, good

#MTOL = kcomp.TOL - 0.1 # reducing the tolrances, it was too tolerant
#MLTOL = kcomp.TOL - 0.05 # reducing the tolrances, it was too tolerant :)
MTOL = kcomp.TOL # too tight for reducing the tolrances, it was too tolerant
MLTOL = kcomp.TOL - 0.05 # reducing the tolrances, it was too tolerant :)

# default values for exporting to STL
LIN_DEFL = 0.1
ANG_DEFL = 0.523599 # 30 degree
