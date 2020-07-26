# ----------------------------------------------------------------------------
# -- Component Constants
# -- comps library
# -- Constants about different optical components
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- July-2017
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

import kcomp 



INCH = 25.4  # how many mm are one inch

# diameter of a SM2 thread
SM2_D =  2.035*INCH  # SM2 (2.035"-40): d=51.689 mm
SM1_D =  1.035*INCH  # SM1 (1.035"-40): d=26.289 mm

CAGE_CUBE_60 = {
           'L'             :  76.2 ,  # Length of each side (3 inch)
           'thru_hole_d'   :  63.5 ,  # both sides, thru, not threaded
                                      # Thru, 4 sides
           'thru_thread_d' :  SM2_D ,  # SM2 (2.035"-40): d=51.689 mm
           'thru_rod_d'    :  6. ,    # 4 places, 2 sides, thru, on SM2 side
           'thru_rod_sep'  :  60. ,   # Separation between the rods
           # thread of the rods that can be tapped on the sides other than
           # the rod thru-holes: 
           'rod_thread_d'  :  kcomp.UNC_D['4'] ,  #4-40
           'rod_thread_l'  :  1.5 ,  # depth of the thread for the rods
           # aditional taps to connect accesories
           'tap_d'  :  kcomp.UNC_D['8'] ,  #8-32
           'tap_l'  :  3.0 ,  # depth of the #8-32 tap (I don't know)
           'tap_sep_l': 66.,   # separation of the #8_32 tap, large
           'tap_sep_s': 35.8   # separation of the #8_32 tap, short
                 }


# Faces of the cage cubes:
ROD_SCREWS = 1
THRU_RODS = 2
THRU_HOLE = 3


CAGE_CUBE_HALF_60 = {
           # 76.2 Length of each side (3 inch)
           'L'              : CAGE_CUBE_60['L'],
           # Thru, 2 sides
           # 2.035*INCH ,  # SM2 (2.035"-40): d=51.689 mm
           'thread_d'   : CAGE_CUBE_60['thru_thread_d'],
           # internal hole after the SM2 thread
           'thru_hole_d'     : 41.9,
           # distance from the edge that the internal hole starts after
           # the SM2 thread
           'thru_hole_depth' : 8.9,
           # Hole for the lens at 45 degrees
           # to the center, for 2inch optics (50.8mm)
           'lenshole_45_d'   :  49.3,  
           'rod_d'    :  6. ,    # 4 places, 2 sides,  perpendicular sides
           'rod_sep'  :  60. ,   # Separation between the rods
           'rod_depth':  6.4 ,   # how deep are the holes
           # taps to mount to posts, on the to triangular sides
           # to diferenciate the sides, the perpendicular sides are named
           # axis_1 and axis_2, so 12 will be the cross product of
           # axis_1 x axis_2, and the other 21 will be axis_2 x axis_1
           'tap12_d' :  4. ,  #M4x0.7 diameter
           'tap12_l' :  6.4 ,  # length: depth of the M4x0.7 tap
           'tap21_d' :  6. ,  #M6x1 diameter
           'tap21_l' :  8.9 , # length: depth of the M6x1.0 tap
           # the distance to the center in direction to the right angle
           # see picture below
           'tap_dist':  10.2  # The dis
                 }

#
#                 /|
#               /  |
#             /    |
#           /      |
#         /   0    |---
#       /     :    |  + 27.9 
#     /____________|...
#     :       :    :
#     :       :----:
#     :         27.9
#     :.. 76.2 ....:  -> 76.2/2 = 38.3
#           :      :
#           :.38.3.:  -> the center
#           : :
#           : : -------> 10.2: distance to the center: 48.3-27.9 


# LB2C plate dimensions

LB2C_PLATE = {
           'L' : CAGE_CUBE_60['L'], # 76.2, 
           'thick'  : 7.6,
           'thruhole_d' : CAGE_CUBE_60['thru_thread_d'],
           'sym_hole_d' : kcomp.UNC_D['4'] ,  #4-40
           'sym_hole_sep' :  CAGE_CUBE_60['thru_rod_sep'],
           'cbore_hole_d'  :  kcomp.UNC_D['8'],  #8-32,
           'cbore_hole_head_d' : 6.9, #taken from a socket cap bolt
           'cbore_hole_head_l' : 4.2, #taken from a socket cap bolt
           'cbore_hole_sep_l' : CAGE_CUBE_60['tap_sep_l'],
           'cbore_hole_sep_s' : CAGE_CUBE_60['tap_sep_s']
           }



# Thorlabs LB1C/M plate dimensions

LB1CM_PLATE = {
           'L' : CAGE_CUBE_60['L'], # 76.2, 
           'thick'  : 7.6,
           'mhole_d' : 6., # mounting hole M6
           'mhole_depth' : 5.1, # mounting hole M6
           'seal_ring_d' : 67.5, # O-ring for tight seal
           'seal_ring_thick' : 2., # Thickness of the ring, not defined
           'sym_hole_d' : kcomp.UNC_D['4'] ,  #4-40
           'sym_hole_sep' :  CAGE_CUBE_60['thru_rod_sep'],
           'cbore_hole_d'  :  kcomp.UNC_D['8'],  #8-32,
           'cbore_hole_head_d' : 6.9, #taken from a socket cap bolt
           'cbore_hole_head_l' : 4.2, #taken from a socket cap bolt
           'cbore_hole_sep_l' : CAGE_CUBE_60['tap_sep_l'],
           'cbore_hole_sep_s' : CAGE_CUBE_60['tap_sep_s']
           }


# LCP01M plate dimensions

LCP01M_PLATE = {
           'L' : 2.8*INCH, # 71.12mm, 
           'thick'  : 0.5*INCH, # 12.7mm
           'thruhole_d' : CAGE_CUBE_60['thru_thread_d'],
           'mhole_d' : 4., # mounting hole M4
           'mhole_depth' : 6.5, # mounting hole M4
           'sym_hole_d' : 6. ,  #ER Rods
           'sym_hole_sep' :  CAGE_CUBE_60['thru_rod_sep'],
           'chamfer_r' : 2., #aprox
           }

# LCPB1M_BASE  mounting plate dimensions

#mounting base, Thorlabs LCPB1_M
#
#                   fc_axis_h
#                       :
#            ___________:____________ ....                _.........
#           |________________________|...:h_lip        ..| |___    :
#           |                        |            h_sup+ |     |   + h_tot
#     ______|                        |______...        : |_____|   :
#    |_|__|____________________________|__|_|.:h_slot  :.|_____|...:..>fc_axis_d
#
#        
#
#                s_mholes_dist (small mounting holes)
#                 .....+......
#                :            :      
#     ___________:____________:_____________....................... fc_axis_w
#    |      |________________________|      |...: d_lip :d_mount   :
#    |  /\  |    o    (O)     o      |  /\  |-----------:         + d_tot
#    |_|  |_|________________________|_|  |_|.....................:
#    :  :   :        l_mhole         :   :  :
#    :  :   :                        :   :  :
#    :  :   :                        :   :  :
#    :  :   :........ w_sup .........:   :  :
#    :  :                                :  :
#    :  :........... slot_dist ..........:  :
#    :                                      :
#    :............... w_tot ................:
#

LCPB1M_BASE = {
           'w_tot'        : 120.7,
           'd_tot'        :  15.2,
           'h_tot'        :  10.8,
           'h_slot'       :   3.8,
           'slot_dist'    : 100.,
           'd_mount'       :   8.9, # all mounting holes are at the same d
           'slot_d'       :   6.0,  # diameter of the slot. M6 plus TOL
           'w_sup'        :  82.6,
           'h_sup'        :   8.9,
           'd_lip'        :   2.5,
           's_mholes_dist':  50.0,
           's_mholes_d'   :   3.0,   # diam M3 plus TOL
           'l_mbolt_d'    :   4.0    # diam M4 plus TOL, counterbored
            }


# 2inch diameter stackabel lens tubes> SM2LXX
#
#                     ______________
#                   _|..............|
#                  | :              |
#     SM2 external | :              |   SM2 (2 inch) internal thread
#       thread     | :              |
#                  |_:..............|
#                    |______________|
#                  : :              :
#                  :3:    Lext      :
#                  :                :
#                  :...... L1 ......:
#
#
#

SM1L_Lint = 3.
SM2L_Lint = 3.

# External diameter of a SM1 tube lens
SM1_TLENS_D = 30.5
SM2_TLENS_D = 55.9


# Length exterior (L), so when threaded, the interior length of 3mm doesnt count


SM2L_Lext = {      # L1
              3 : 11.4 - SM2L_Lint, #SM2L03
              5 : 16.5 - SM2L_Lint, #SM2L05
             10 : 29.2 - SM2L_Lint, #SM2L10
             15 : 41.9 - SM2L_Lint, #SM2L15
             20 : 54.6 - SM2L_Lint, #SM2L20
             30 : 80.0 - SM2L_Lint  #SM2L30
             }


SM1L_Lext = {      # L1
              3 :  11.4 - SM1L_Lint, #SM1L03
              5 :  16.5 - SM1L_Lint, #SM1L05
             10 :  29.2 - SM1L_Lint, #SM1L10
             15 :  41.9 - SM1L_Lint, #SM1L15
             20 :  54.6 - SM1L_Lint, #SM1L20
             30 :  80.0 - SM1L_Lint, #SM1L30
             35 :  92.7 - SM1L_Lint, #SM1L35
             40 : 105.4 - SM1L_Lint  #SM1L40
             }


#                                 SM1A2        SM2T2
#
#                  lens tube         __            locking rings: 2.8mm each
#                                   | .|       _H_H_
#     LED            SM1LXX         |: |      |.....|
#     _____       ______________    |: |      |     |
#        __|    _|..............|  _|: |      |     |
#       |      | :              | |  : |      |     |
#       |      | :    SM1       | |  : | SM2  |     |
#       |      | :              | |  : |      |     |
#       |__    |_:..............| |_ : |      |     |
#     _____|     |______________|   |: |      |     |
#              : :              :   |: |      |.....|
#              :3:    Lext      :   |:.|      |_____|
#                                   |__|        H H
#                                   ::            
#                                   0.7 mm

# So, joining the lens tube SM1LXX + SM1A2 + SM2T2
# we have something like this, is approximate, also because it can be adjusted
# differently. NOT DRAWING THE THREADS, just the length as it were threaded in
#
#                                    .........................
#                  lens tube     _HH ...........             :
#                               ||..|          :             :
#  LED               SM1LXX     ||  |          :             :
#  _____    ..... ______________||  |          :             :
#     __|   :   _|..............||  |          :             :
#    |      :  | :            : ||  |          :             :
#    |  30.5+  | :    SM1     : ||  |          +55.9         + 57.2
#    |      :  | :            : ||  |          :SM2_TLENS_D  :
#    |__    :  |_:............:.||  |          :             :
#  _____|   :....|______________||  |          :             :
#              : :              ||  |          :             :
#              :3:    Lext      ||..|          :             :
#                               ||__|..........:             :
#   SM1_TLENS_D=30.5              HH ........................:
#                             0.7: 5.6


SM1L_2_SM2 = {
              'sm1_d' : SM1_TLENS_D, # SM1 lens diameter
              'sm1_l' : SM1L_Lext,   # dictionary to the length of the SM1 part
              'sm2_d' : SM2_TLENS_D, # SM2 lens diameter
              'sm2_l' : 0.7, # height (length) of the SM2 part
              'ring_d' : 57.2, # diameter of the ring
              'ring_l' : 5.6,  # height (length) of the ring
              'thick' : ((SM1_TLENS_D - SM1_D) / 2.)  # approximate thickness
             }


# ---------------------- ThLed30 --------------------------
#   Dimensions of the Thorlabs Led with 30.5 mm Heat Sink diameter
#       The drawing is very rough
#                                
#                         :....35...:
#                         :         :
#                         :         :
#                         :  Cable  :
#                        | | diam ? :
#                        | |        :
#                    ____|_|________:..................
#           ......__|       | | | | |                 :
#           :    |  :       | | | | |                 :
#           :    |  :       | | | | |                 :
#         ? +   C|  0.....  | | | | |                 + 30.5: SM1_TLENS_D
#           :    |          | | | | |                 :
#           :....|__        | | | | |                 :
#               :   |_______________|.................:
#               :   :               :
#               :   :......50.......:
#               :                   :
#               :........60.4.......:
#

THLED30 = { 'ext_l'  : 50., # external length, the other part will be inside
                            # the tubelens
            'tot_l'  : 60.4, # total length
            'ext_d'  : SM1_TLENS_D, # external diameter: 30.5
            'cable_dist': 35., #distance of the center of the cable to the end
            'int_d'  : 24.,  #I dont know the value, but 26.289 is the thread
                            # so it has to be smaller
            'cable_d' : 5. # dont know the value
          }

# ---- Dimensions of a Prizmatix UHP-T-Led 
#       The drawing is very rough, and the original drawing lacks many 
#       dimensions
#
#              ...22....                        ........50.........
#              :       :                        :                 :
#      ........:________________                :_________________:........
#      : 10.5+ |              | |___________    |                 |   :   :
#      :     :.|       O M6   | |           |   |      ____       |   +25 :
#      :       |              | |           |   |     /     \     |   :   :
#      +39.5   |              | |  Fan      |   |    | SM1   |    |...:   :
#      :.......|       O      | |           |   |     \____ /     |       :
#              |              | |           |   |                 |       + 90
#              |              | |___________|   |      KEEP       |       : H
#              |              | |               |      CLEAR      |       :
#              |              | |               |      |  |       |       :
#              |              | |               |      V  V       |       :
#              |              | |               |_________________|       :
#               \_____________|_|               |_________________|.......:
#              :                :
#              :..depth_block...:
#                                                        :
#              :15:                                      :
#              :  :                                      V
#              :__:__________________________         fc_axis_clear
#              |              | |           |          
#              |  O           | |           |
#   fc_axis_led|              | |           |
#         <--- |              | |           |
#              |              | |           | 
#              |              | |           |
#              |  O M6        | |           |
#              |______________|_|___________|
#              :                            :
#              :...........98.75............:
#                   depth_t


PRIZ_UHP_LED = {
               'H' : 90, # height
               'depth_t' : 98.75, # total depth
               'width' : 50., # width
               'depth_block' : 50., # not defined value
               'led_hole_d': SM1_D, 
               'led_hole_depth': 10.,  # value not defined
               'led_hole_dist': 25., # distance from the top
               'fan_w': 50., #fan width, not defined
               'chmf_r' : 8., #chamfer radius, not defined
               'side_thread_depth' : 22., 
               'side_thread1_h' : 10.5, # height of the 1st thread
               'side_thread2_h' : 39.5, # height of the 2st thread
               'top_thread_depth' : 15., 
               'top_thread_sep' : 34.,  # unknown
               'mthread_d' : 6., # mounting thread diamenter
               'mthread_h' : 8. # unknown
               }

# metric bread board constant dimensions:

BREAD_BOARD_M = {
                  'thick'  : 12.7, #thickness of the board
                  'hole_d' : 6., # tapped M6 holes
                  'hole_sep' : 25., # separation between holes
                  'hole_sep_edge' : 12.5, #separation from 1st hole to edge
                  'cbored_hole_d' : 6., # M6 counterbored holes on the corners
                  'cbored_hole_sep' : 25., # distance counterbored holes to edge
                  'cbore_head_d' : 10., # head diameter M6
                  'cbore_head_l' : 10., # head diameter M6
                  'minw_cencbore': 450. # minimum width to have a counter
                                #bored hole at the center
                  }
                

