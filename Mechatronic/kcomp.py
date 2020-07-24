# ----------------------------------------------------------------------------
# -- Component Constants
# -- comps library
# -- Constants about different components, materials, parts and 3D printer
# --   settings
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- October-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

# ---------------------- Tolerance in mm
TOL = 0.4
STOL = TOL / 2.0       # smaller tolerance

# height of the layer to print. To make some supports, ie: bolt's head
LAYER3D_H = 0.3  

# ---------------------- linear Bearings

#external diameter of the bearing 
LMUU_D = { 6: 12., 8: 15., 10: 19.0, 12: 21.0, 20: 42. };
#Length of the bearing
LMUU_L = { 6: 19., 8: 24., 10: 29.0, 12: 30.0, 20: 32. }; 

#diamenter of the bearing 
LMEUU_D = {        8: 16., 10: 19.0, 12: 22.0, 20: 32. };
#Length of the bearing
LMEUU_L = {        8: 25., 10: 29.0, 12: 32.0, 20: 45. };

# Large version:
LMELUU_L = {                   12: 57.0 }; #the length of the bearing
LMELUU_D = { 8: 16., 10: 19.0, 12: 22.0 }; #diamenter of the bearing 


LM6UU = {
         'Di' : 6,  # interior diameter
         'De' : LMUU_D[6], # exterior diameter
         'L' : LMUU_L[6] # length
           }

LM8UU = {
         'Di' : 8,  # interior diameter
         'De' : LMUU_D[8], # exterior diameter
         'L' : LMUU_L[8] # length
           }

LM10UU = {
         'Di' : 10,  # interior diameter
         'De' : LMUU_D[10], # exterior diameter
         'L' : LMUU_L[10] # length
           }


LM12UU = {
         'Di' : 12,  # interior diameter
         'De' : LMUU_D[12], # exterior diameter
         'L' : LMUU_L[12] # length
           }

LM20UU = {
         'Di' : 20,  # interior diameter
         'De' : LMUU_D[20], # exterior diameter
         'L' : LMUU_L[20] # length
           }

LME8UU = {
         'Di' : 8,  # interior diameter
         'De' : LMEUU_D[8], # exterior diameter
         'L' : LMEUU_L[8] # length
           }


LME10UU = {
         'Di' : 10,  # interior diameter
         'De' : LMEUU_D[10], # exterior diameter
         'L' : LMEUU_L[10] # length
           }

LME12UU = {
         'Di' : 12,  # interior diameter
         'De' : LMEUU_D[12], # exterior diameter
         'L' : LMEUU_L[12] # length
           }

LME20UU = {
         'Di' : 20,  # interior diameter
         'De' : LMEUU_D[20], # exterior diameter
         'L' : LMEUU_L[20] # length
           }


LME12LUU = {
         'Di' : 12,  # interior diameter
         'De' : LMELUU_D[12], # exterior diameter
         'L' : LMELUU_L[12] # length
           }


LMUU = {
          6 : LM6UU,
          8 : LM8UU,
         10 : LM10UU,  # same as LMEUU
         12 : LM12UU,
         20 : LM12UU
        }


LMEUU = {
          8 : LME8UU,
         10 : LME10UU,
         12 : LME12UU,
         20 : LME20UU
        }

LMELUU = {
         12 : LME12LUU
        }



# E3D V6 extrusor dimensions
"""
    ___________
   |           |   outup
    -----------
      |     |
      |     |      in
    ___________
   |           |   outbot
    -----------
"""

E3DV6_IN_DIAM = 12.0
E3DV6_IN_H = 6.0
E3DV6_OUT_DIAM = 16.0
E3DV6_OUTUP_H = 3.7
E3DV6_OUTBOT_H = 3.0

# separation of the extruders.
# with the fan, the extruder are about 30mm wide. So 15mm from the center.
# giving 10mm separation, results in 40mm separation
# and total length of 70mm
extrud_sep = 40.0

# DIN-912 bolt dimmensions
# head: the index is the M, i.e: M3, M4, ..., the value is the diameter of the head of the bolt
D912_HEAD_D = {2: 3.8,  2.5:4.5,
               3: 5.5,  4: 7.0,  5:  8.5,
               6:10.0,  8:13.0,  10:18.0} 
# length: the index is the M, i.e: M3, M4, ..., the value is the length of the head of the bolt
# well, it is the same as the M, never mind...
D912_HEAD_L =  {2: 2.,  2.5: 2.5,
                3: 3.0, 4: 4.0,  5: 5.0,
                6: 6.0, 8:8.0,  10:10.0} 

# 2 x apotheme of the hex socket
D912_2AP =  {2: 1.5,  2.5: 2.,
             3: 2.5,    4: 3.,  5: 4.,
             6: 5.,     8: 6., 10: 8.} 


# max threaded part of the shank, if shank length is smaller, it will be
# all threated
D912_THREAD = {2: 16., 2.5: 17.,
               3: 18.,   4: 20.,  5: 22.,
               6: 24.,   8: 28., 10: 32.}

M3_HEAD_R = D912_HEAD_D[3] / 2.0
M3_HEAD_L = D912_HEAD_L[3]
M3_HEAD_L_TOL = D912_HEAD_L[3] + TOL
M3_HEAD_R_TOL = M3_HEAD_R + TOL/2.0 # smaller TOL, because it's small
M3_SHANK_R_TOL = 3 / 2.0 + TOL/2.0
M3_2AP = D912_2AP[3]  # 2xapotheme of the hex socket

# typical length of DIN912 bolts
D912_M2_5_L = [6,   8, 10, 12, 14, 16, 20]
            

D912_M3_L = [6,   8, 10, 12, 14, 16, 20,
             25, 30, 35, 40]
D912_M4_L = [6,   8, 10, 12, 14, 16, 20,
             25, 30, 35, 40, 45, 50, 55,
             60, 65, 70, 100]
D912_M5_L = [6,     8,  10,  12,  14,  16,  18,  20,  22,
             25,   30,  35,  40,  45,  50,  55,
             60,   65,  70,  80,  90,
             100, 110, 120, 130 ]
D912_M6_L = [6,     8,  10,  12,  14,  16,  20,  22,
             25,   30,  35,  40,  45,  50,  55,
             60,   65,  70,  80,  90,
             100, 110, 120, 150 ]
D912_M8_L = [                12,  14,  16,  20,  22,
             25,   30,  35,  40,  45,  50,  55,
             60,   65,  70,  75,  80,  90,
             100, 110, 120, 130, 140, 150, 160, 170, 200 ]

D912_L = {  2.5: D912_M2_5_L,
            3: D912_M3_L,
            4: D912_M4_L,
            5: D912_M5_L,
            6: D912_M6_L,
            8: D912_M8_L
          }

M4_HEAD_R = D912_HEAD_D[4] / 2.0
M4_HEAD_L = D912_HEAD_L[4]
M4_HEAD_L_TOL = D912_HEAD_L[4] + TOL
M4_HEAD_R_TOL = M4_HEAD_R + TOL/2.0 # smaller TOL, because it's small
M4_SHANK_R_TOL = 4 / 2.0 + TOL/2.0
M4_2AP = D912_2AP[4]  # 2xapotheme of the hex socket

M6_HEAD_R = D912_HEAD_D[6] / 2.0
M6_HEAD_L = D912_HEAD_L[6]
M6_HEAD_L_TOL = D912_HEAD_L[6] + TOL
M6_HEAD_R_TOL = M6_HEAD_R + TOL/2.0 # smaller TOL, because it's small
M6_SHANK_R_TOL = 6 / 2.0 + TOL/2.0
M6_2AP = D912_2AP[6]  # 2 x apotheme of the hex socket

D912_M2_5 = {
            'd': 2.5,  # diameter of the shank
            'shank_r_tol'  :  2.5 / 2. + TOL/2.,
            'head_r'       :  D912_HEAD_D[2.5]/2.,
            'head_r_tol'   :  D912_HEAD_D[2.5]/2. + TOL/2.,
            'head_l'       :  D912_HEAD_L[2.5],
            'head_l_tol'   :  D912_HEAD_L[2.5]+TOL,
            'thread'       :  D912_THREAD[2.5],
            'shank_l_list' :  D912_L[2.5], # list of possible shank lengths
            'ap2' :  D912_2AP[2.5], # s: 2 x apotheme of the socket
           }


D912_M3 = {
            'd': 3.,  # diameter of the shank
            'shank_r_tol'  :  3 / 2. + TOL/2.,
            'head_r'       :  M3_HEAD_R,
            'head_r_tol'   :  M3_HEAD_R_TOL,
            'head_l'       :  M3_HEAD_L,
            'head_l_tol'   :  M3_HEAD_L_TOL,
            'thread'       :  D912_THREAD[3],
            'shank_l_list' :  D912_L[3], # list of possible shank lengths
            'ap2' :  M3_2AP, # s: 2 x apotheme of the socket
           }

D912_M4 = {
            'd': 4.,  # diameter of the shank
            'shank_r_tol' :  4 / 2. + TOL/2.,
            'head_r' :  M4_HEAD_R,
            'head_r_tol' :  M4_HEAD_R_TOL,
            'head_l' :  M4_HEAD_L,
            'head_l_tol' :  M4_HEAD_L_TOL,
            'thread'     :  D912_THREAD[4],
            'shank_l_list' :  D912_L[4], # list of possible shank lengths
            'ap2' :  M4_2AP, # s: 2 x apotheme of the socket
           }

D912_M5 = {
            'd': 5.,  # diameter of the shank
            'shank_r_tol'  :  5 / 2. + TOL/2.,
            'head_r'       :  D912_HEAD_D[5]/2.,
            'head_r_tol'   :  D912_HEAD_D[5]/2. + TOL/2.,
            'head_l'       :  D912_HEAD_L[5],
            'head_l_tol'   :  D912_HEAD_L[5] + TOL,
            'thread'       :  D912_THREAD[5],
            'shank_l_list' :  D912_L[5], # list of possible shank lengths
            'ap2'          :  D912_2AP[5], # s: 2 x apotheme of the socket
           }

D912_M6 = {
            'd': 6.,  # diameter of the shank
            'shank_r_tol'  :  6 / 2. + 1.5*TOL/2., # mult 1.5 to have more tol
            'head_r'       :  M6_HEAD_R,
            'head_r_tol'   :  M6_HEAD_R_TOL,
            'head_l'       :  M6_HEAD_L,
            'head_l_tol'   :  M6_HEAD_L_TOL,
            'thread'       :  D912_THREAD[6],
            'shank_l_list' :  D912_L[6], # list of possible shank lengths
            'ap2'          :  M6_2AP, # s: 2 x apotheme of the socket
           }


D912 = { 2.5: D912_M2_5,
         3: D912_M3,
         4: D912_M4,
         5: D912_M5,
         6: D912_M6 }


# Nut DIN934 dimensions
"""
       ___     _
      /   \    |   s_max: double the apothem
      \___/    |_

   r is the circumradius,  usually called e_min
"""

# the circumdiameter, min value
NUT_D934_D =  {
               1.6: 3.41,
               2:   4.32,
               2.5: 5.45,
               3:   6.01,
               4:   7.66,
               5:   8.79,
               6:  11.05}
# double the apotheme, max value
NUT_D934_2A = {
               1.6: 3.2,
               2:   4.,
               2.5: 5.,
               3:   5.5,
               4:   7.0,
               5:   8.0,
               6:   10.0}
# the heigth, max value
NUT_D934_L  = {
               1.6:  1.3,
               2:    1.6,
               2.5:  2.,
               3:    2.4,
               4:    3.2,
               5:    4.0,
               6:    5.0}

M3_NUT_R = NUT_D934_D[3] / 2.0
M3_NUT_L = NUT_D934_L[3] + TOL
#  1.5 TOL because diameter values are minimum, so they may be larger
M3_NUT_R_TOL = M3_NUT_R + 1.5*TOL

# constant related to inserted nuts. For example, to make a leadscrew
# The nut height multiplier to have enough space to introduce it
NUT_HOLE_MULT_H = 1.8 
M3NUT_HOLE_H = NUT_HOLE_MULT_H * M3_NUT_L  

#M3_2APOT_TOL = NUT_D934_2A[3] +  TOL
# Apotheme is: R * cos(30) = 0.866
APOT_R = 0.866
M3_2APOT_TOL = 2* M3_NUT_R_TOL * APOT_R

M4_NUT_R = NUT_D934_D[4] / 2.0
M4_NUT_L = NUT_D934_L[4] + TOL
#  1.5 TOL because diameter values are minimum, so they may be larger
M4_NUT_R_TOL = M4_NUT_R + 1.5*TOL

D934_M2 = {
            'in_d': 2.,  # inner diameter of the shank
            'circ_d' : NUT_D934_D[2], #circumdiameter, min value
            'circ_r' : NUT_D934_D[2]/2., #circumradius, min value
            'circ_r_tol' : NUT_D934_D[2]/2. +  1.5*TOL , #circumradius + tol
            'a2' :  NUT_D934_2A[2], #double of apotheme, max value
            'l' :  NUT_D934_L[2], # height, max value
            'l_tol' :  NUT_D934_L[2] + TOL #height with tolerance
           }


D934_M2_5 = {
            'in_d': 2.5,  # inner diameter of the shank
            'circ_d' : NUT_D934_D[2.5], #circumdiameter, min value
            'circ_r' : NUT_D934_D[2.5]/2., #circumradius, min value
            'circ_r_tol' : NUT_D934_D[2.5]/2. +  1.5*TOL , #circumradius + tol
            'a2' :  NUT_D934_2A[2.5], #double of apotheme, max value
            'l' :  NUT_D934_L[2.5], # height, max value
            'l_tol' :  NUT_D934_L[2.5] + TOL #height with tolerance
           }

D934_M3 = {
            'in_d': 3.,  # inner diameter of the shank
            'circ_d' : NUT_D934_D[3], #circumdiameter, min value
            'circ_r' : NUT_D934_D[3]/2, #circumradius, min value
            'circ_r_tol' : NUT_D934_D[3]/2 +  1.5*TOL , #circumradius + tol
            'a2' :  NUT_D934_2A[3], #double of apotheme, max value
            'l' :  NUT_D934_L[3], # height, max value
            'l_tol' :  NUT_D934_L[3] + TOL #height with tolerance
           }


D934_M4 = {
            'in_d': 4.,  # inner diameter of the shank
            'circ_d' : NUT_D934_D[4], #circumdiameter, min value
            'circ_r' : NUT_D934_D[4]/2, #circumradius, min value
            'circ_r_tol' : NUT_D934_D[4]/2 +  1.5*TOL , #circumradius + tol
            'a2' :  NUT_D934_2A[4], #double of apotheme, max value
            'l' :  NUT_D934_L[4], # height, max value
            'l_tol' :  NUT_D934_L[4] + TOL #height with tolerance
           }

D934_M5 = {
            'in_d': 5.,  # inner diameter of the shank
            'circ_d' : NUT_D934_D[5], #circumdiameter, min value
            'circ_r' : NUT_D934_D[5]/2, #circumradius, min value
            'circ_r_tol' : NUT_D934_D[5]/2 +  1.5*TOL , #circumradius + tol
            'a2' :  NUT_D934_2A[5], #double of apotheme, max value
            'l' :  NUT_D934_L[5], # height, max value
            'l_tol' :  NUT_D934_L[5] + TOL #height with tolerance
           }

D934_M6 = {
            'in_d': 6.,  # inner diameter of the shank
            'circ_d' : NUT_D934_D[6], #circumdiameter, min value
            'circ_r' : NUT_D934_D[6]/2, #circumradius, min value
            'circ_r_tol' : NUT_D934_D[6]/2 +  1.5*TOL , #circumradius + tol
            'a2' :  NUT_D934_2A[6], #double of apotheme, max value
            'l' :  NUT_D934_L[6], # height, max value
            'l_tol' :  NUT_D934_L[6] + TOL #height with tolerance
           }
           
           
D934 = {
         2.5: D934_M2_5,
         3: D934_M3,
         4: D934_M4,
         5: D934_M5,
         6: D934_M6 }


# tightening bolt with added tolerances:
# Bolt's head radius
#tbolt_head_r = (tol * d912_head_d[sk_12['tbolt']])/2 
# Bolt's head lenght
#tbolt_head_l = tol * d912_head_l[sk_12['tbolt']] 
# Mounting bolt radius with added tolerance
#mbolt_r = tol * sk_12['mbolt']/2

# ------------- DIN 125 Washers (small) -----------------------

# The Index reffers to the Metric (M3,...
# Inner Diameter (of the hole). Minimum diameter.
WASH_D125_DI = {
                  2:    2.2,
                  2.5:  2.7,
                  3:    3.2,
                  4:    4.3,
                  5:    5.3,
                  6:    6.4,
                  7:    7.4,
                  8:    8.4,
                 10:   10.5 }

# Outer diameter (maximum size)
WASH_D125_DO = {
                  2:    5.0,
                  2.5:  6.0,
                  3:    7.0,
                  4:    9.0,
                  5:   10.0,
                  6:   12.0,
                  7:   14.0,
                  8:   16.0,
                 10:   20.0 }

# Thickness (Height) of the washer. there is tolerance
WASH_D125_T  = {
                  2:   0.3,  #0.25 to 0.35
                  2.5: 0.5,  #0.45 to 0.55
                  3:   0.5,  #0.45 to 0.55
                  4:   0.8,  #0.7 to 0.8
                  5:   1.0,
                  6:   1.6,
                  7:   1.6,
                  8:   1.6,
                 10:   2.0 }

D125 = {} # empty dictionary
for (k_di, di), (k_do, do), (k_t, t) in zip(WASH_D125_DI.items(),
                                            WASH_D125_DO.items(),
                                            WASH_D125_T.items()):
    # creation of a 2 dimension dictionary
    # for example: 
    #              D125[4]['do']
    # will give the outer diameter of the M4 DIN125 washer

    # k_di, k_do, k_t should have the same value in each iteration
    # these 2 sentences are equivalent
    #D125[k_di] = dict([('di',di),('do',do), ('t',t)])
    D125[k_di] = dict(di=di, do=do, t=t)
    if not ((k_di == k_do) and (k_di == k_t)):
        logger.error('Keys are not ordered')


# ------------- DIN 9021 Washers (wide) -----------------------

# The Index reffers to the Metric (M3,...
# Inner Diameter of the hole. Minimum diameter.
WASH_D9021_DI = {
                  3:  3.2,
                  4:  4.3,
                  5:  5.3,
                  6:  6.4,
                  7:  7.4,
                  8:  8.4,
                 10: 10.5 }

# Outer diameter (maximum size)
WASH_D9021_DO = {
                  3:   9.0,
                  4:  12.0,
                  5:  15.0,
                  6:  18.0,
                  7:  22.0,
                  8:  24.0,
                 10:  30.0 }

# Height of the washer (thickness)
WASH_D9021_T  = {
                  3:   0.8,
                  4:   1.0,
                  5:   1.2,
                  6:   1.6,
                  7:   2.0,
                  8:   2.0,
                 10:   2.5 }

D9021 = {} # empty dictionary
for (k_di, di), (k_do, do), (k_t, t) in zip(WASH_D9021_DI.items(),
                                            WASH_D9021_DO.items(),
                                            WASH_D9021_T.items()):
    # creation of a 2 dimension dictionary
    # for example: 
    #              D9021[4]['do']
    # will give the outer diameter of the M4 DIN9021 washer

    # k_di, k_do, k_t should have the same value in each iteration
    # these 2 sentences are equivalent
    #D9021[k_di] = dict([('di',di),('do',do), ('t',t)])
    D9021[k_di] = dict(di=di, do=do, t=t)
    if not ((k_di == k_do) and (k_di == k_t)):
        logger.error('Keys are not ordered')

# ------------- UNC Unified Coarse Thread
# USA and Canada Standard Threads from Unified Thread Standard UTS
# starts on #0 to #12 and then 1/4, 5/16, ... to 7/8, 1
# First number is related to the diameter, the other to the pitch
# for exampple #4-40 is 2.8448mm major diam. 40 tpi pitch
# https://en.wikipedia.org/wiki/Unified_Thread_Standard

# Major diameter in mm of a UNC thread

UNC_D = {
            '0' : 1.5240,  # #0
            '1' : 1.8542,  # #1
            '2' : 2.1844,
            '3' : 2.5146,
            '4' : 2.8448,
            '5' : 3.1750,
            '6' : 3.5052,
            '8' : 4.1656
         } # it continues to #12 and then 1/4, ...




# ------------- Ball Bearings           -----------------------

# Inner diameter
BEAR_DI = {
            603:  3.0,
            673:  3.0,
            624:  4.0,
            608:  8.0
          }

# Outer diameter
BEAR_DO = {
            603:  9.0,
            673:  6.0,
            624: 13.0,
            608: 22.0
          }

# Thickness (Height)
BEAR_T  = {
            603:  5.0,
            673:  2.5,
            624:  5.0,
            608:  7.0
          }

BEARING = {} # empty dictionary
for (k_ndi, di), (k_ndo, do), (k_nt, t) in zip(BEAR_DI.items(),
                                               BEAR_DO.items(),
                                               BEAR_T.items()):
    # creation of a 2 dimension dictionary
    # for example: 
    #              BEARING[603]['do']
    # will give the outer diameter of the 603 bearing

    # the keys: k_ndi, k_ndo, k_nt should have the same value in each iteration
    # these 2 sentences are equivalent
    #BEARING[k_ndi] = dict([('di',di),('do',do), ('t',t)])
    BEARING[k_ndi] = dict(di=di, do=do, t=t)
    if not ((k_ndi == k_ndo) and (k_ndi == k_nt)):
        logger.error('Keys are not ordered')



# to acces more easily to the dimensions of objects that are just
# a hollow cylinder, such as washers and bearings
# Arguments:
# part: 'bearing' or 'washer'
# size: metric size for the washers, and model (608, 624) for bearings
# kind: 'regular' or 'large' for washers

class HollowCyl(object):

    def __init__ (self, part, size, kind = 'regular'):

        self.part = part
        self.size = size
        self.kind = kind
        if part == 'washer':
            if kind == 'large': # DIN 9021
                self.model = 'DIN9021'
                self.d_in  = WASH_D9021_DI[size]  # inner diameter
                self.d_out  = WASH_D9021_DO[size]  # outer diameter
                self.thick  = WASH_D9021_T[size]   # thickness
            elif kind == 'regular': # DIN 125
                self.model = 'DIN125'
                self.d_in   = WASH_D125_DI[size]
                self.d_out  = WASH_D125_DO[size]
                self.thick  = WASH_D125_T[size]
            else:
                logger.error('Unkowon kind: HollowCyl')
        elif part == 'bearing':
            self.model  = size
            self.d_in   = BEAR_DI[size]
            self.d_out  = BEAR_DO[size]
            self.thick  = BEAR_T[size]
        self.r_in   = self.d_in/2.   # inner radius
        self.r_out  = self.d_out/2.   # outer radius

# ----------------------------- Idler pulley components --------
# this may be an error, it is not a name list, is a objects list
# this is a name list from botton to top that shows the component
# order to make an idler pulley out of washers and bearings

"""
idler pulley with the one for the bolt

     with dots goes the bolt head, not in the group
             .....
           _:_____:_        bolt head
       ___|_________|___    regular washer
      |_________________|   large washer
          |_________|       regular washer
          |         |       bearing
          |_________|   
       ___|_________|___    regular washer
      |_________________|   large washer

 
"""


#idlepull_name_list = [
idpull4_nlist = [
        HollowCyl (part = 'washer', size = 6, kind= 'large'), #bottom
        HollowCyl (part = 'washer', size = 4, kind= 'regular'),
        HollowCyl (part = 'bearing', size = 624), # 624ZZ
        HollowCyl (part = 'washer', size = 4, kind= 'regular'),
        HollowCyl (part = 'washer', size = 6, kind= 'large'),
        HollowCyl (part = 'washer', size = 4, kind= 'large') #top for the bolt
              ]

idpull3_nlist = [
        HollowCyl (part = 'washer', size = 4, kind= 'large'),
        HollowCyl (part = 'washer', size = 3, kind= 'regular'),
        HollowCyl (part = 'bearing', size = 603), # 603ZZ
        HollowCyl (part = 'washer', size = 3, kind= 'regular'),
        HollowCyl (part = 'washer', size = 4, kind= 'large'),
        HollowCyl (part = 'washer', size = 3, kind= 'large') #top for the bolt
           ]

# idler pulley list will be different depending on the size of the bolt that
# holds them

idpull_dict = { 3: idpull3_nlist, 4: idpull4_nlist }

"""
idler pulley without the washer for the bolt because it is between a holder,
The holder is in dots, not in the group
            .......
  ..........:.....:........     bolt head
                           :    Holder for the pulley group
  ....._________________...:
      |_________________|       large washer
          |_________|           regular washer
          |         |           bearing
          |_________|   
       ___|_________|___        regular washer
  ....|_________________|..     large washer
                           :
  .........................:    Holder for the pulley group
            :.....:             nut
              :.:               bolt shank
 
So it is symmetrical from bottom to top
"""

idpull4min_list = [
        HollowCyl (part = 'washer', size = 6, kind= 'large'), #bottom
        HollowCyl (part = 'washer', size = 4, kind= 'regular'),
        HollowCyl (part = 'bearing', size = 624), # 624ZZ
        HollowCyl (part = 'washer', size = 4, kind= 'regular'),
        HollowCyl (part = 'washer', size = 6, kind= 'large'),
        HollowCyl (part = 'washer', size = 4, kind= 'large') #top for the bolt
              ]

idpull3min_list = [
        HollowCyl (part = 'washer', size = 4, kind= 'large'), #bottom
        HollowCyl (part = 'washer', size = 3, kind= 'regular'),
        HollowCyl (part = 'bearing', size = 603), # 603ZZ
        HollowCyl (part = 'washer', size = 3, kind= 'regular'),
        HollowCyl (part = 'washer', size = 4, kind= 'large') # top
           ]


idpullmin_dict = { 3: idpull3min_list, 4: idpull4min_list }


# from an idlepull_name_list, returns the maximum diameter of its bearings
# check that it is the same as getmaxbeardiam in partgroup.py

def get_idlepull_maxbear_d (idlepull_list):
    d_maxbear = 0
    for ind, elem in enumerate(idlepull_list):
        if elem.part == 'bearing':
            if d_maxbear < elem.d_out :
                d_maxbear = elem.d_out
    return d_maxbear
    

# ------------------------- Linear bearing housing
# Similar to SC10UU, but without many the details, just the main dimensions
#
#          bolt_d
#         : : 
#         _______________                   ..... ________________
#        |: :   ___   : :|                  :    |.:.:........:.:.|
#        |: :  /   \  : :|                H +    | : :        : : |
#        |----|-----|----|----              :    | : :        : : |
#        |: :  \___/  : :|   + axis_h       :    |.:.:........:.:.| 
#        |:_:_________:_:|...:              :....|_:_:________:_:_|      
#        : :           : :                       :  :          :  :
#        : :...........: :                       :  :..........:  :
#        :   bolt_sep_w  :                       :   bolt_sep_l   :
#        :...... W ......:                       :......L.........:
#
#
#         _____________ 
#        | 0 :     : 0 |
#        |   :     :   |
#        |   :     :   |
#        |   :     :   |
#        |   :     :   |
#        |_0_:_____:_0_|
#


SC8UU = {
        'L'          : 30.,
        'W'          : 34.,
        'H'          : 22.,
        'axis_h'     : 11.,
        'bolt_sep_l' : 18.,
        'bolt_sep_w' : 24.,
        'bolt_d'     : 4.,  # M4
        'lbear'      : LM8UU  #dictionary with linear bearging dim.
        }

SC10UU = {
        'L'          : 35.,
        'W'          : 40.,
        'H'          : 26.,
        'axis_h'     : 13.,
        'bolt_sep_l' : 21.,
        'bolt_sep_w' : 28.,
        'bolt_d'     : 5.,  # M5
        'lbear'      : LM10UU  #dictionary with linear bearging dim.
        }

SC12UU = {
        'L'          : 40., # they say 36, but it is too small
        'W'          : 42.,
        'H'          : 28.,
        'axis_h'     : 15.,
        'bolt_sep_l' : 26.,
        'bolt_sep_w' : 30.5,
        'bolt_d'     : 5.,  # M5
        'lbear'      : LM12UU  #dictionary with linear bearging dim.
        }

SCE20UU = {
        'L'          : 53.,
        'W'          : 54.,
        'H'          : 41.,
        'axis_h'     : 21.,
        'bolt_sep_l' : 40.,
        'bolt_sep_w' : 40.,
        'bolt_d'     : 6.,  # M6
        'lbear'      : LME20UU  #dictionary with linear bearging dim.
        }

# modified version to print
SC8UU_Pr = {
        'L'          : 30.,
        'W'          : 34.,
        'H'          : 22.,
        'axis_h'     : 11.,
        'bolt_sep_l' : 18.,
        'bolt_sep_w' : 24.,
        'bolt_d'     : 3.,  # M3: changed from M4 to M3
        'lbear'      : LME8UU  #dictionary with linear bearging dim.
        }

SC10UU_Pr = {
        'L'          : 35.,
        'W'          : 40.,
        'H'          : 26.,
        'axis_h'     : 13.,
        'bolt_sep_l' : 21.,
        'bolt_sep_w' : 28.,
        'bolt_d'     : 3.,  # M3: changed from M5 to M3
        'lbear'      : LME10UU  #dictionary with linear bearging dim.
        }

SC12UU_Pr = {
        'L'          : 36.,
        'W'          : 42.,
        'H'          : 28.,
        'axis_h'     : 15.,
        'bolt_sep_l' : 26.,
        'bolt_sep_w' : 30.5,
        'bolt_d'     : 3.,  # M3: changed from M5 to M3
        'lbear'      : LME12UU  #dictionary with linear bearging dim.
        }

SCE20UU_Pr30 = {    # to print with 30x30 profiles sep_l = 60
        'L'          : 74.,
        'W'          : 54.,
        'H'          : 41.,
        'axis_h'     : 21.,
        'bolt_sep_l' : 60.,
        'bolt_sep_w' : 40.,
        'bolt_d'     : 6.,  # M6
        'lbear'      : LME20UU  #dictionary with linear bearging dim.
        }

SCE20UU_Pr30b = {    # to print with 30x30 profiles sep_l = 30
        'L'          : 53.,
        'W'          : 54.,
        'H'          : 41.,
        'axis_h'     : 21.,
        'bolt_sep_l' : 30.,
        'bolt_sep_w' : 40.,
        'bolt_d'     : 6.,  # M6
        'lbear'      : LME20UU  #dictionary with linear bearging dim.
        }


SCUU = {
         8: SC8UU,
        10: SC10UU,
        12: SC12UU
       }

SCUU_Pr = {
         8: SC8UU_Pr,
        10: SC10UU_Pr,
        12: SC12UU_Pr
       }

SCEUU_Pr = {
        20: SCE20UU_Pr30
}



# ----------------------------- NEMA motor dimensions --------

# width of the motor (both dimensions: it is a square) in mm
NEMA_W  = {
             8:   20.2,
             11:  28.2,
             14:  35.2,
             17:  42.3,
             23:  56.4,
             34:  86.0,
             42: 110.0 }

# Separation of the holes for the bolts 
NEMA_BOLT_SEP  = {
             8:   16.0,
             11:  23.0,
             14:  26.0,
             17:  31.0,
             23:  47.1,
             34:  69.6,
             42:  89.0 }

# Diameter of the shaft
NEMA_SHAFT_D  = {
             8:    4.0,
             11:   5.0,
             14:   5.0,
             17:   5.0,
             23:   6.35,
             34:  14.0,
             42:  19.0 }

# Bolt diameter
NEMA_BOLT_D  = {
              8:   2.0,  # M2
             11:   2.5,  # M2.5
             14:   3.0,  # M3
             17:   3.0,  # M3
             23:   5.5,
             34:   5.5,
             42:   8.5 }

#        _______ .....................................  
#       |  ___  |                                     :
#       | / d.\.|.................                    :
#       | \___/ |  __            :                    + H
#     __|       |__ /| ...       + h                  :
#    |_____________|/ ...+L......:....................:
#    :             :
#    :......W......:
#
#       ....I....
#       :_______:      _______________________________  
#       |  ___  |                                     :
#       | /   \ |      __________                     :
#       | \___/ |                :                    + H
#    ___|       |___ ......       + h                  :
#   |_:___________:_|.....+g ____:____________________:
#     :           :
#     :......B....: S: diameter of the 2 thruholes

# ----------------------------- shaft holder SK dimensions --------
# there are different brands, and are not all the same,
# Also valid for dold SH
# A is not necessary, it is just the half of W
# b is not necessary, it is just (W-B)/2
# mbolt: is the metric of the mounting bolt
# tbolt: is the metric of the tightening bolt

SK6 =  { 'd':6.0,  'H':32.8, 'W':42.0, 'L':14.0, 'B':32.0, 'S':5.5,
         'h':20.0,
         #'A':21.0,
         #'b': 5.0,
         'g':6.0,
         'I':18.0,
         'mbolt': 5,
         'tbolt': 4} 


SK8 =  { 'd':8.0,  'H':32.8, 'W':42.0, 'L':14.0, 'B':32.0, 'S':5.5,
         'h':20.0,
         #'A':21.0,
         #'b': 5.0,
         'g':6.0,
         'I':18.0,
         'mbolt': 5,
         'tbolt': 4} 

# to make with the same height of a pillow block
# H: just 6.8 less
PILLOW_SK8 =  { 'd':8.0,  'H':26., 'W':42.0, 'L':14.0, 'B':32.0, 'S':5.5,
         'h':15.0,
         #'A':21.0,
         #'b': 5.0,
         'g':6.0,
         'I':18.0,
         'mbolt': 5,
         'tbolt': 4} 


SK10 = { 'd':10.0, 'H':32.8, 'W':42.0, 'L':14.0, 'B':32.0, 'S':5.5,
         'h':20.0,
         #'A':21.0,
         #'b': 5.0,
         'g': 6.0,
         'I': 18.0,
         'mbolt': 5,
         'tbolt': 4} 

SK12 = { 'd':12.0, 'H':36, 'W':71.0, 'L':14.0, 'B':32.0, 'S':5.5,
         'h':23.0,
         #'A':21.0,
         #'b': 5.0,
         'g': 6.0,
         'I': 20.0,
         'mbolt': 5,  
         'tbolt': 4} 

# add tolerances L= 12 + 4 (bearing). Just approximate, the shape is not the
# same
PILLOW_SK12 =  { 'd':12.3,  'H':26., 'W':42.0, 'L':16.0, 'B':56.0, 'S':7.,
         'h':18.0,
         #'A':21.0,
         #'b': 5.0,
         'g':6.0,
         'I':20.0,
         'mbolt': 5,
         'tbolt': 4} 

#SH20
SK20 = { 'd':20.0, 'H':51., 'W':60.0, 'L':20.0, 'B':45.0, 'S':6.6,
         'h':31.0,
         #'A':
         #'b':
         'g': 10.,
         'I': 30.0,
         'mbolt': 6,  
         'tbolt': 5} 


SK = {
          6: SK6,
          8: SK8,
         10: SK10,
         12: SK12,
         20: SK20 }

PILLOW_SK = {
          8: PILLOW_SK8,
          12: PILLOW_SK12
            }


# ------------------------- T8 Nut for leadscrew ---------------------
#   
#  1.5|3.5| 10  | 
#      __  _____________________________ d_ext: 22
#     |__|
#     |__|   bolt_d: 0.35  --- d_bolt_pos: 16
#    _|  |______     ________ d_shaft_ext: 10.2
#   |___________|    --- d_T8 (threaded) 
#   |___________|    ---   
#   |_    ______|    ________
#     |__|
#     |__|  -------------------
#     |__|  ____________________________
#
#   
#      10  |3.5| 1.5
#           __  _____________________________ d_flan: 22
#          |__|
#          |__|   bolt_d: 0.35  --- d_bolt_pos: 16
#    ______|  |_    ________ d_shaft_ext: 10.2
#   |___________|    ___ d_T8 (threaded) 
#   |___________|    ___   
#   |_______   _|    ________
#          |__|
#          |__|  -------------------
#          |__|  ____________________________
#
#          |  | nut_shaft_out
#           nut_flan_l: 3.5
#   |  nut_l:15  |
#
#              | |
#               T8NUT_SHAFT_OUT: 1.5

T8N_BOLT_D      = 3.5
T8N_D_FLAN      = 22.0
T8N_D_BOLT_POS  = 16.0
T8N_D_SHAFT_EXT = 10.2
T8N_D_T8        = 8.0
T8N_L           = 15.0
T8N_FLAN_L      = 3.5
T8N_SHAFT_OUT   = 1.5



# ---------- CompactLeadScrewNut ----------------------
# L = lead                             :.flan_cut.
#                                      :         :
#           __ ..... flan_d            : _______ :
#          |..|                        :/       \:
#          |..| ---- bolt_pos_d        | O     O |  bolt_d
#    ______|  | .... sh_ext_d          |   ___   |
#   |......|..| ....                   |  /   \  | 
#   |......|..| .... T (thread_d)      | |     | |
#   |______|  |                        |  \___/  |
#   :      |..|                        |         |
#   :      |..|                        | O     O |
#   :      |__|......                  .\ _____ /.                       
#   :      :  :                       .     :     .
#   :      :  :                      .      :      .
#   :      :  :                     .       :       .
#   :      :  :                    .        :        .
#   :      :  :                             :bolt_ang .
#   :      :  :
#   :      :  +------ this is the zero. Plane YZ=0
#   :      :  :
#   :      :..:
#   :       + flan_h
#   :...H.....:
#
# Misumi Miniature Lead Screw. compact nut: MSSR
#
MIS_LSCRNUT_C_L1_T4 = {
           'L'         :  1. ,  # lead
           'T'         :  4. ,  # thread diameter
           'sh_ext_d'  : 10. ,  # exterior diameter of the nut shaft
           'flan_d'    : 23. ,  # diameter of flange
           'H'         : 11.5,  # height (or length) of the nut
           'flan_h'    :  3.5,  # height (or length) of the flange
           'flan_cut'  : 15. ,  # Cut of the flange (compact nut)
           'bolt_pos_d': 15. ,  # Diameter of the position of the bolt holes
           'bolt_d'    :  2.9,  # Diameter of the bolt holes
           'bolt_ang'  : 30.    # Angle of the bolts, referred to the vertical
                       }

MIS_LSCRNUT_C_L1_T6 = {
           'L'         :  1. ,  # lead
           'T'         :  6. ,  # thread
           'sh_ext_d'  : 12. ,  # exterior diameter of the nut shaft
           'flan_d'    : 26. ,  # diameter of flange
           'H'         : 14.5,  # height (or length) of the nut
           'flan_h'    :  3.5,  # height (or length) of the flange
           'flan_cut'  : 17. ,  # Cut of the flange (compact nut)
           'bolt_pos_d': 18. ,  # Diameter of the position of the bolt holes
           'bolt_d'    :  3.4,  # Diameter of the position of the bolt holes
           'bolt_ang'  : 30.    # Angle of the bolts, referred to the vertical
                       }

MIS_LSCRNUT_C_L1_T8 = {
           'L'         :  1. ,  # lead
           'T'         :  8. ,  # thread
           'sh_ext_d'  : 14. ,  # exterior diameter of the nut shaft
           'flan_d'    : 29. ,  # diameter of flange
           'H'         : 18. ,  # height (or length) of the nut
           'flan_h'    :  4. ,  # height (or length) of the flange
           'flan_cut'  : 18. ,  # Cut of the flange (compact nut)
           'bolt_pos_d': 21. ,  # Diameter of the position of the bolt holes
           'bolt_d'    :  3.4,  # Diameter of the position of the bolt holes
           'bolt_ang'  : 30.    # Angle of the bolts, referred to the vertical
                       }

# MIS: Misumi
# LSCRNUT: LeadScrew Nue
# C: Compact
# Index: Thread diameter
MIS_LSCRNUT_C  = {
              4: MIS_LSCRNUT_C_L1_T4,
              6: MIS_LSCRNUT_C_L1_T6,
              8: MIS_LSCRNUT_C_L1_T8
                 }


# ------------------------- T8 Nut Housing ---------------------

# Box dimensions:
T8NH_L = 30.0
T8NH_W = 34.0
T8NH_H = 28.0

# separation between the screws that attach to the moving part
T8NH_BoltLSep  = 18.0
T8NH_BoltWSep =  24.0

# separation between the screws to the end
T8NH_BoltL2end = (T8NH_L - T8NH_BoltLSep)/2.0
T8NH_BoltW2end = (T8NH_W - T8NH_BoltWSep)/2.0

# Boltew dimensions, that attach to the moving part: M4 x 7
T8NH_BoltD = 4.0
T8NH_BoltR = T8NH_BoltD / 2.0
T8NH_BoltL = 7.0

# Bolt dimensions, that attach to the Nut Flange: M3 x 10
T8NH_FlanBoltD = 3.0
T8NH_FlanBoltL = 10.0

# ---------------- flexible shaft coupler --------------------------

# rb: 2 Nm. Referred to diameter of the coupled shafts


# coupler diameter
FLEXSC_RB_D = {
                (3, 8):20.,
                (4, 6):18.,
                (4, 8):20.,
                (5, 6):18.,
                (5, 8):19., #check
                (5,10):20.
              }

# coupler length
FLEXSC_RB_L = {
                (3, 8):25.,
                (4, 6):25.,
                (4, 8):25.,
                (5, 6):25.,
                (5, 8):25., #check
                (5,10):25.
              }

# KFL Pillow Block
#             
#            _____     ____ L
#           / ___ \     _
#         /  /   \  \
#       ( O (     ) 0 )
#         \  \___/  /   
#           \_____/    ____
#          
#         |--- J ---|
#       |----- H -----|
#

# Housing: FL(08)
# Bearing Number: SU(08)

# ------------------------ Aluminum Extrusion Profiles
# Values and shape may be approximate
#      :----- width ----:
#      :       slot     :
#      :      :--:      :
#      :______:  :______:
#      |    __|  |__    |
#      | |\ \      / /| |
#      |_| \ \____/ / |_| ...........
#          |        | ......        insquare
#          |  (  )  | ......indiam  :
#       _  |  ____  | ..............:
#      | | / /    \ \ | |
#      | |/ /_    _\ \| | .... 
#      |______|  |______| ....thick
#
#
# width:  w:    the Width of the profile, it is squared
# thick:  t:   the thickness of the side
# slot:   slot: the width of the rail 
# insquare: insq: the width of the inner square
# indiam:   ind :the diameter of the inner hole

ALU_MOTEDIS_40I8 = {'w'    : 40.,
                    't'    : 4.5, # aprox, depending
                    'slot' : 8., 
                    'insq' : 15.5,
                    'indiam' : 6.8 } # aprox?

ALU_MOTEDIS_30B8 = {'w'    : 30.,
                    't'    : 2.5, # aprox
                    'slot' : 8., 
                    'insq' : 12, # 30 - 18
                    'indiam' : 7.3 }


ALU_MOTEDIS_20I5 = {'w'    : 20.,
                    't'    : 1.8, # aprox measured
                    'slot' : 5., 
                    'insq' : 7.30, # 20 - 2*6.35
                    'indiam' : 4.3 }

# Makerbeam XL. The section differs a lot from the figure
# Openbeam is also 15, but also very different, even more
ALU_MAKERBEAM_15 = {'w'    : 15.,
                    't'    : 1.1, 
                    'slot' : 3., 
                    'insq' : 5.7, # It has an inner square of 3
                    'indiam' : 2.55 }

ALU_MAKERBEAM_10 = {'w'    : 10.,
                    't'    : 1., 
                    'slot' : 3., 
                    'insq' : 4., # 10 - 2*3.
                    'indiam' : 2.5 }

# NanoBeam 5. The section differs a lot from the figure
# and it has no inner circle.
# Maybe later I will make good one, but not for now
ALU_OPENBEAM_5 = {'w'    : 5.,
                  't'    : 0.44,  # actually is a triangle (2.479 - 1.605)/2
                  'slot' : 1.605, 
                  'insq' : 1.8, # 5 - 2*1.583
                  'indiam' : 0 }  # No inner circle

# Selection of the profile depending on the width

ALU_PROF = {
              5: ALU_OPENBEAM_5,
             10: ALU_MAKERBEAM_10,
             15: ALU_MAKERBEAM_15,
             20: ALU_MOTEDIS_20I5,
             30: ALU_MOTEDIS_30B8,
             40: ALU_MOTEDIS_40I8
          }

# ------------------------ Linear Guides 


#RAIL DIMENSIONS

# rw: Rail Width
# rh: Rail Height
# boltlsep: Bolt separation on the length dimension
# boltwsep: Bolt separation on the width dimension, if 0, just one on a line
# boltd: Bolt hole diameter
# bolthd: Bolt head hole diameter
# bolthh: Bolt head hole height
# bolend_sep: separation of the first bolt to the end

# ------------------ Misumi SEBWM16 
SEBWM16_R = { 'rw'     : 42., 'rh': 9.5,
              'boltlsep': 40., 'boltwsep' : 23.,
              'boltd'   : 4.5, 'bolthd'   : 8. , 'bolthh': 4.5,
              'boltend_sep' : 15.,
              'name' : 'Misumi_SEBWM16'
            }

# ------------------ NB SEBS15A
SEB15A_R = { 'rw'     : 15., 'rh': 9.5,
              'boltlsep': 40., 'boltwsep' : 0,
              'boltd'   : 3.5, 'bolthd'   : 6. , 'bolthh': 4.5,
              'boltend_sep' : 15.,
              'name' : 'NB_SEB15A'
           }

# ------------------ Misumi SEB8
SEB8_R = { 'rw': 7.,  # W1
           'rh': 4.7, # H1
           'boltlsep' : 15.,  # F
           'boltwsep' : 0,   # in case there are 2 bolt holes
           'boltd'    : 2.4, # d1
           'bolthd'   : 4.2, # d2
           'bolthh'   : 2.3, # h
           'boltend_sep': 5., #G
           'name' : 'Misumi_SEB8'
         }

# ------------------ Misumi SEB10
SEB10_R = {'rw': 5.,  # W1
           'rh': 5.5, # H1
           'boltlsep' : 20.,  # F
           'boltwsep' : 0,   # in case there are 2 bolt holes
           'boltd'    : 3.5, # d1
           'bolthd'   : 6.0, # d2
           'bolthh'   : 3.5, # h
           'boltend_sep': 7.5, #G
           'name'     : 'Misumi_SEB10'
         }


#BLOCK DIMENSIONS

# bl: block Length
# bls: block Length, the inner part (smaller)
# bw: block Width, the larger
# bws: block Width, the smaler part at the ends
# bh: block Height, just the block
# lh: linear guide Height: together the rail and the block
# boltlsep: Bolt separation on the length dimension
# boltwsep: Bolt separation on the length dimension
# boltd: Bolt diameter
# boltl: Bolt length. if 0 it is through hole

# ------------------ Misumi SEBWM16 
SEBWM16_B = { 'bl'  : 55.,
              'bls' : 40.,
              'bw'  : 74.,
              'bws' : 60.,  # not on the specifications
              'bh'  : 13.,  # block height, just the block
              'lh'  : 16.,  # linear guide height, with the rail
              'boltlsep' : 20.,  # Bolt separation on the length dimension
              'boltwsep' : 65.,  # Bolt separation on the width dimension
              'boltd'  : 5.,  # Bolt diameter M5
              'boltl'  : 0,  # Thru-hole
              'name' : 'Misumi_SEBWM16'
            }

# ------------------ NB SEBS15A
SEB15A_B = {  'bl'  : 42.,
              'bls' : 29.5,
              'bw'  : 32.,
              'bws' : 32.,  # the same
              'bh'  : 12.,  # block height, just the block
              'lh'  : 16.,  # linear guide height, with the rail
              'boltlsep' : 20.,  # Bolt separation on the length dimension
              'boltwsep' : 25.,  # Bolt separation on the width dimension
              'boltd'  : 3.,  # Bolt diameter M3
              'boltl'  : 4.,  # 
              'name' : 'NB_SEB15A'
            }

# ------------------ Misumi SEB8 
SEB8_B = { 'bl'  : 23.6,    # L1
           'bls' : 13.6, # L2
           'bw'  : 17.,  # W
           'bws' : 17.,  # not on the specifications
           'bh'  : 6.5,  # K: block height, just the block
           'lh'  : 8.,   # H: linear guide height, with the rail
           'boltlsep' : 8.,  # C: Bolt separation on the length dimension
           'boltwsep' : 12.,  # B: Bolt separation on the width dimension
           'boltd'  : 2.,  # S: Bolt diameter M2
           'boltl'  : 2.5,  # l 
           'name' : 'Misumi_SEB8'
            }

# ------------------ Misumi SEB10 
SEB10_B = { 'bl'  : 30.,  # L1
            'bls' : 19.,  # L2
            'bw'  : 20.,  # W
            'bws' : 20.,  # not on the specifications
            'bh'  : 7.8,  # K: block height, just the block
            'lh'  : 10.,  # H: linear guide height, with the rail
            'boltlsep' : 10.,  # C: Bolt separation on the length dimension
            'boltwsep' : 15.,  # B: Bolt separation on the width dimension
            'boltd'  : 3.,  # S: Bolt diameter M2
            'boltl'  : 3.,   # l 
            'name' : 'Misumi_SEB10'
            }


SEBWM16 = { 'rail'  : SEBWM16_R,
            'block' : SEBWM16_B}

SEB15A = { 'rail'  : SEB15A_R,
           'block' : SEB15A_B}

SEB8 = { 'rail'  : SEB8_R,
         'block' : SEB8_B}

SEB10 = { 'rail'  : SEB10_R,
          'block' : SEB10_B}

# mechanical end stop dimensions
#
#                   /
#                /
#             /         ____ ..................
#          /               /                   + D: 6.9 
#      _/_________________/ .............................
#     |                   |                  :          :
#     |                   |                  + H: 10    :
#     |      O     O      | ....BOLT_H: 2.5  :          + HT
#     |___________________| ..................          :
#        |      |      |                     + 4        :
#        |      |      |    .............................
#     :      :     :      :
#     :      :     :      :
#     :      : 9.5 :      :
#     :     BOLT_SEP      :
#     :                   :
#     :......L:19.6.......:
#              

ENDSTOP_A = { 'L': 19.6,
            'H': 10.0,
            'D':  6.9,
            'HT': 14.0,
            'BOLT_SEP' : 9.5,
            'BOLT_H' : 2.5,
            'BOLT_D' : 2.5 }

ENDSTOP_B = { 'L': 12.7,
            'H': 6.4,
            'D':  5.6,
            'HT': 9.5,
            'BOLT_SEP' : 6.5,
            'BOLT_H' : 1.5,
            'BOLT_D' : 1.6 }

# d3v-162-1c25
# the bolt holes are not aligned
# mechanical end stop dimensions
#
#                   /
#                /
#             /         ____ ..................
#          /               /                   + D: 6.9 
#      _/_________________/ .............................
#     |               O   |...BOLT_TOP_H     :          :
#     |                   |                  + H: 10    :
#     |    O              | ....BOLT_H: 2.5  :          + HT
#     |___________________| ..................          :
#        |      |      |                     + 4        :
#        |      |      |    .............................
#     :      :     :      :
#     :      :     :      :
#     :      : 9.5 :      :
#     :     BOLT_SEP      :
#     :                   :
#     :......L:19.6.......:


ENDSTOP_D3V = { 'L': 37.8,
              'H': 15.9,
              'D': 10.3,
              'HT': 18.8,
              'BOLT_SEP' : 22.2,
              'BOLT_H' : 15.9- 2.8 - 10.3,  # lower one
              'BOLT_TOP_H' : 2.8, # the second bolt
              'BOLT_D' : 3 }


# GT2 Belt dimensions
#
#
#      _   _   _   _ ...............................
#    _/ \_/ \_/ \_/ \_....:+ tooth_height: 0.75    + belt_height: 1.38        
#                     ....:+ PLD: 0.254            :            
#    _________________.............................:
#      :   :
#      :...:
#        + tooth separation 2mm (pitch)
#
#
#    PLD: Pitch Line Distance (I think), where the tensile cord is
#         when the belt is on a pulley, that would be the distance added
#         to the outside diameter of the belt. What is called the pitch
#         diameter: for a GT2 is 
#

GT2 = { 'BELT_H'  : 1.38, # total height
        'TOOTH_H' : 0.75, # tooth height
        'PLD'     : 0.254 # pitch line distance
      }


GT = {
          2 : GT2
     }

        

