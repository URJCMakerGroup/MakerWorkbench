# ----------------------------------------------------------------------------
# -- Filter holder
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m/freecad_filter_stage
# -- February-2018
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------
#
#                     axis_h
#                        :
#                        :
#         ___    ___     :     ___    ___       ____
#        |   |  |   |    :    |   |  |   |     | || |
#        |...|__|___|____:____|___|__|...|     |_||_|
#        |         _           _         |     |  ..|
#        |        |o|         |o|        |     |::  |
#        |        |o|         |o|        |     |::  |
#        |                               |     |  ..|
#        |                               |     |  ..|
#        |      (O)             (O)      |     |::  |
#        |                               |     |  ..|
#        |                               |     |  ..|
#        |  (O)   (o)   (O)   (o)   (O)  |     |::  |
#        |_______________________________|     |  ..|
#        |_______________________________|     |     \_________________
#        |  :.........................:  |     |       :............:  |
#        |   :                       :   |     |        :          :   |
#        |___:___________x___________:___|     x________:__________:___|.>axis_d
#
#
#         _______________x_______________ ......> axis_w
#        |____|                     |____|
#        |____   <  )          (  >  ____|
#        |____|_____________________|____|
#        |_______________________________|
#        |  ___________________________  |
#        | | ......................... | |
#        | | :                       : | |
#        | | :                       : | |
#        | | :                       : | |
#        | | :.......................: | |
#        | |___________________________| |
#         \_____________________________/
#                        :
#                        :
#                        :
#                      axis_d
#
#




# the filter is referenced on 3 perpendicular axis:
# - axis_d: depth
# - axis_w: width
# - axis_h: height
#
# The reference position is marked with a x in the drawing

import os
import sys
import inspect
import logging
import math
import FreeCAD
import FreeCADGui
import Part
import DraftVecUtils

# to get the current directory. Freecad has to be executed from the same
# directory this file is
filepath = os.getcwd()
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath) 
#sys.path.append(filepath + '/' + 'comps')
sys.path.append(filepath + '/../../' + 'comps')

# path to save the FreeCAD files
fcad_path = filepath + '/../freecad/'

# path to save the STL files
stl_path = filepath + '/../stl/'

import kcomp   # import material constants and other constants
import fcfun   # import my functions for freecad. FreeCad Functions
import shp_clss # import my TopoShapes classes 
import fc_clss # import my freecad classes 
import comps   # import my CAD components
import partgroup 

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ShpFilterHolder (shp_clss.Obj3D):
    """ Creates the filter holder shape


                               beltpost_l = 3*lr_beltpost_r + sm_beltpost_r
       pos_h         axis_h   :   :
       |                 :    :    clamp_post_dist
       v pos_w           :    :   ....
       9 7___6  5___4    :    :___:  :___ 
       8 |   |  |   |    :    |   |  |   |
       7 |...|__|___|____:____|___|__|...|...
         |         _           _         |   2 * bolt_linguide_head_r_tol
       6 |        |o|         |o|        |-----------------------
       5 |        |o|         |o|        |--------------------  +boltrow1_4_dist
         |                               |                   :  :
         |                               |                   +boltrow1_3_dist
       4 |      (O)             (O)      |--:                :  :
         |                               |  +boltrow1_2_dist :  :
         |                               |  :                :  :
       3 | (O)    (o)   (O)   (o)    (O) |--:----------------:--:
         |_______________________________|  + boltrow1_h
       2 |_______________________________|..:..................
       1 |  :.........................:  |..: filt_hole_h  :
         |   :                       :   |                 + base_h
       0 |___:___________x___________:___|.................:........axis_w
                         :     : :    :
                         :.....: :    :
                         : + boltcol1_dist
                         :       :    :
                         :.......:    :
                         : + boltcol2_dist
                         :            :
                         :............:
                            boltcol3_dist

             3     21    0     pos_w (position of the columns)
         7  6  5   4           pos_w (position of the belt clamps)

                                     beltclamp_l
                clamp_post          ..+...
                  V                 :    :
          _______________x__________:____:......................> axis_w
         |____|                     |____|.. beltclamp_blk_t  :
         |____   <  )          (  >  ____|..: beltclamp_t     :+ hold_d
         |____|_____________________|____|....................:
         |_______________________________|
         |  ___________________________  |.................
         | | ......................... | |..filt_supp_in   :
         | | :                       : | |  :              :
         | | :                       : | |  :              :+filt_hole_d
         | | :                       : | |  + filt_supp_d  :
         | | :.......................: | |..:              :
         | |___________________________| |.................:
          \_____________________________/.....filt_rim
         : : :                       : : :
         : : :                       : : :
         : : :                       :+: :
         : : :            filt_supp_in : :
         : : :                       : : :
         : : :.... filt_supp_w ......: : :
         : :                           : :
         : :                           : :
         : :...... filt_hole_w   ......: :
         :                             :+:
         :                      filt_rim :
         :                               :
         :....... tot_w .................:



               0123  pos_d
               0 45  pos_d 
                ____...............................
               | || |   + beltclamp_h             :
               |_||_|...:................         :
               |  ..|                   :         :
               |::  |                   :         :
               |::  |                   :         :
               |  ..|                   :         :
               |  ..|                   :         :+ tot_h
               |::  |                   :         :
               |  ..|                   :+hold_h  :
               |  ..|                   :         :
               |::  |                   :         :
               |  ..|                   :         :
               |     \________________  :         :
               |       :...........:  | :         :
               |        :         :   | :         :
               x________:_________:___|.:.........:...>axis_d
               :             :        :
               :.............:        :
               : filt_cen_d           :
               :                      :
               :...... tot_d .........:

       pos_d:  0    6  78    9    1011 12
 
 


        pos_o (origin) is at pos_d=0, pos_w=0, pos_h=0, It marked with x

    Parameters:
    -----------
    filter_l : float
        length of the filter (it will be along axis_w). Larger dimension
    filter_w : float
        width of the filter (it will be along axis_d). Shorter dimension
    filter_t : float
        thickness/height of the filter (it will be along axis_h). Very short
    base_h : float
        height of the base
    hold_d : float
        depth of the holder (just the part that holds)
    filt_supp_in : float
        how much the filter support goes inside from the filter hole
    filt_cen_d : float
        distance from the filter center to the beginning of the filter holder
        along axis_d
        0: it will take the minimum distance
           or if it is smaller than the minimum distance
    filt_rim : float
        distance from the filter to the edge of the base
    fillet_r : float
        radius of the fillets
    boltcol1_dist : float
        distance to the center along axis_w of the first column of bolts
    boltcol2_dist : float
        distance to the center along axis_w of the 2nd column of bolts
    boltcol3_dist : float
        distance to the center along axis_w of the 3rd column of bolts
        This column could be closer to the center than the 2nd, if distance
        is smaller
    boltrow1_h : float
        distance from the top of the filter base to the first row of bolts
        0: the distance will be the largest head diameter in the first row
           in any case, it has to be larger than this
    boltrow1_2_dist : float
        distance from the first row of bolts to the second
    boltrow1_3_dist : float
        distance from the first row of bolts to the third
    boltrow1_4_dist : float
        distance from the first row of bolts to the 4th
    bolt_cen_mtr : integer (could be float: 2.5)
        diameter (metric) of the bolts at the center or at columns other than
        2nd column
    bolt_linguide_mtr : integer (could be float: 2.5)
        diameter (metric) of the bolts at the 2nd column, to attach to a
        linear guide
    beltclamp_t : float
        thickness of the hole for the belt. Inside de belt clamp blocks
        (along axis_d)
    beltclamp_l : float
        length of the belt clamp (along axis_w)
    beltclamp_h : float
        height of the belt clamp: belt width + 2
        (along axis_h)
    clamp_post_dist : float
        distance from the belt clamp to the belt clamp post
    sm_beltpost_r : float
        small radius of the belt post


    tol : float
        Tolerances to print
    axis_d : FreeCAD.Vector
        length/depth vector of coordinate system
    axis_w : FreeCAD.Vector
        width vector of coordinate system
        if V0: it will be calculated using the cross product: axis_d x axis_h
    axis_h : FreeCAD.Vector
        height vector of coordinate system
    pos_d : int
        location of pos along the axis_d (0,1,2,3,4,5), see drawing
        0: at the back of the holder
        1: at the end of the first clamp block
        2: at the center of the holder
        3: at the beginning of the second clamp block
        4: at the beginning of the bolt head hole for the central bolt
        5: at the beginning of the bolt head hole for the linguide bolts
        6: at the front side of the holder
        7: at the beginning of the hole for the porta
        8: at the inner side of the porta thruhole
        9: at the center of the porta
        10: at the outer side of the porta thruhole
        11: at the end of the porta
        12: at the end of the piece
    pos_w : int
        location of pos along the axis_w (0-7) symmetrical
        0: at the center of symmetry
        1: at the first bolt column
        2: at the second bolt column
        3: at the third bolt column
        4: at the inner side of the clamp post (larger circle)
        5: at the outer side of the clamp post (smaller circle)
        6: at the inner side of the clamp rails
        7: at the end of the piece
    pos_h : int
        location of pos along the axis_h (0-8)
        0: at the bottom (base)
        1: at the base for the porta
        2: at the top of the base
        3: first row of bolts
        4: second row of bolts
        5: third row of bolts
        6: 4th row of bolts
        7: at the base of the belt clamp
        8: at the middle of the belt clamp
        9: at the top of the piece
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes:
    -----------
    All the parameters and attributes of parent class SinglePart

    Dimensional attributes:
    filt_hole_d : float
        depth of the hole for the filter (for filter_w)
    filt_hole_w : float
        width of the hole for the filter (for filter_l)
    filt_hole_h : float
        height of the hole for the filter (for filter_t)

    beltclamp_blk_t : float
        thickness (along axis_d) of each of the belt clamp blocks
    beltpost_l : float
        length of the belt post (that has a shap of 2 circles and the tangent
    lr_beltpost_r : float
        radius of the larger belt post (it has a belt shape)
    clamp_lrbeltpostcen_dist : float
        distance from the center of the larger belt post cylinder to the clamp
        post

    prnt_ax : FreeCAD.Vector
        Best axis to print (normal direction, pointing upwards)
    d0_cen : int
    w0_cen : int
    h0_cen : int
        indicates if pos_h = 0 (pos_d, pos_w) is at the center along
        axis_h, axis_d, axis_w, or if it is at the end.
        1 : at the center (symmetrical, or almost symmetrical)
        0 : at the end



                  lr_beltpost_r  clamp_lrbeltpostcen_dist
                              + ..+..
       pos_h         axis_h   ::     :
       |                 :    ::   clamp_post_dist
                              ::   .+.
                              ::  :  :
                              ::  :  : beltclamp_l
       v pos_w           :    ::  :  :.+..
       9 7___6  5___4    :    ::__:  :___: 
       8 |   |  |   |    :    |   |  |   |
       7 |...|__|___|____:____|___|__|...|...
         |         _           _         |   2 * bolt_linguide_head_r_tol
       6 |        |o|         |o|        |-----------------------

    """
    def __init__(self,
                 filter_l = 60.,
                 filter_w = 25.,
                 filter_t = 2.5,
                 base_h = 6.,
                 hold_d = 12.,
                 filt_supp_in = 2.,
                 filt_rim = 3.,
                 filt_cen_d = 0,
                 fillet_r = 1.,
                 # linear guides SEBLV16 y SEBS15, y MGN12H:
                 boltcol1_dist = 20/2.,
                 boltcol2_dist = 12.5, #thorlabs breadboard distance
                 boltcol3_dist = 25,
                 boltrow1_h = 0,
                 boltrow1_2_dist = 12.5,
                 # linear guide MGN12H
                 boltrow1_3_dist = 20.,
                 # linear guide SEBLV16 and SEBS15
                 boltrow1_4_dist = 25.,

                 bolt_cen_mtr = 4, 
                 bolt_linguide_mtr = 3, # linear guide bolts

                 beltclamp_t = 3., #2.8,
                 beltclamp_l = 12.,
                 beltclamp_h = 8.,
                 clamp_post_dist = 4.,
                 sm_beltpost_r = 1.,

                 tol = kcomp.TOL,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0):
        
        shp_clss.Obj3D.__init__(self, axis_d, axis_w, axis_h)


        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

        # calculation of the dimensions:
        # hole for the filter, including tolerances:
        # Note that now the dimensions width and length are changed.
        # to depth and width
        # they are relative to the holder, not to the filter
        # no need to have the tolerances here:
        self.filt_hole_d = filter_w # + tol # depth
        self.filt_hole_w = filter_l # + tol # width in holder axis
        self.filt_hole_h = filter_t # + tol/2. # 0.5 tolerance for height

        # The hole under the filter to let the light go through
        # and big enough to hold the filter
        # we could take filter_hole dimensions or filter dimensiones
        # just the tolerance difference
        self.filt_supp_d = self.filt_hole_d - 2 * filt_supp_in
        self.filt_supp_w = self.filt_hole_w - 2 * filt_supp_in

        # look for the largest bolt head in the first row:
        # dictionary of the center bolt and 2nd and 3rd column
        self.bolt_cen_dict = kcomp.D912[bolt_cen_mtr]
        self.bolt_cen_head_r_tol = self.bolt_cen_dict['head_r_tol']
        self.bolt_cen_r_tol = self.bolt_cen_dict['shank_r_tol']
        self.bolt_cen_head_l_tol = self.bolt_cen_dict['head_l_tol']

        # dictionary of the 1st column bolts (for the linear guide)
        self.bolt_linguide_dict = kcomp.D912[bolt_linguide_mtr]
        self.bolt_linguide_head_r_tol = self.bolt_linguide_dict['head_r_tol']
        self.bolt_linguide_r_tol = self.bolt_linguide_dict['shank_r_tol']
        self.bolt_linguide_head_l_tol = self.bolt_linguide_dict['head_l_tol']

        max_row1_head_r_tol = max(self.bolt_linguide_head_r_tol,
                                  self.bolt_cen_head_r_tol)

        if boltrow1_h == 0:
            self.boltrow1_h = 2* max_row1_head_r_tol
        elif boltrow1_h < 2 * max_row1_head_r_tol:
            self.boltrow1_h = 2* max_row1_head_r_tol
            msg1 = 'boltrow1_h smaller than bolt head diameter'
            msg2 = 'boltrow1_h will be bolt head diameter' 
            logger.warning(msg1 + msg2 + str(self.boltrow1_h))
        # else # it will be as it is

        self.hold_h = (base_h + self.boltrow1_h + boltrow1_4_dist
                       + 2 * self.bolt_linguide_head_r_tol)
        self.tot_h = self.hold_h + beltclamp_h

        self.beltclamp_blk_t = (hold_d - beltclamp_t)/2.

        #self.clamp2cenpost = clamp_post_dist + s_beltclamp_r_sm


        # the large radius of the belt post
        self.lr_beltpost_r = (hold_d - 3) / 2.

        min_filt_cen_d = hold_d + filt_rim + filter_w/2.
        if filt_cen_d == 0: 
            filt_cen_d = hold_d + filt_rim + filter_w/2.
        elif filt_cen_d < min_filt_cen_d:
            filt_cen_d = hold_d + filt_rim + filter_w/2.
            msg =  'filt_cen_d is smaller than needed, taking: '
            logger.warning(msg + str(filt_cen_d))
        self.filt_cen_d = filt_cen_d

        self.tot_d = self.filt_cen_d + filter_w/2. + filt_rim 

        # find out if the max width if given by the filter or the holder
        base_w = filter_l + 2 * filt_rim
        hold_w = 2 * boltcol3_dist + 4 * self.bolt_cen_head_r_tol
        self.tot_w = max(base_w, hold_w)


        self.beltpost_l = (3*self.lr_beltpost_r) + sm_beltpost_r
        self.clamp_lrbeltpostcen_dist = (  self.beltpost_l
                                         - self.lr_beltpost_r
                                         + self.clamp_post_dist)




        self.d0_cen = 0
        self.w0_cen = 1 # symmetrical
        self.h0_cen = 0

        self.d_o[0] = V0
        self.d_o[1] = self.vec_d(self.beltclamp_blk_t)
        self.d_o[2] = self.vec_d(hold_d/2.)
        self.d_o[3] = self.vec_d(hold_d - self.beltclamp_blk_t)
        # at the beginning of the bolt head hole for the central bolt
        self.d_o[4] = self.vec_d(hold_d - self.bolt_cen_head_l_tol)
        self.d_o[5] = self.vec_d(hold_d - self.bolt_linguide_head_l_tol)
        self.d_o[6] = self.vec_d(hold_d)
        # at the beginning of the hole of the porta (no tolerance):
        self.d_o[7] = self.vec_d(self.filt_cen_d - filter_w/2.)
        # inner side of porta thruhole
        self.d_o[8] = self.d_o[7] + self.vec_d(filt_supp_in)
        # at the center of the porta:
        self.d_o[9] = self.vec_d(self.filt_cen_d)
        # outer side of porta thruhole
        self.d_o[10] = self.vec_d(self.filt_cen_d + filter_w/2. - filt_supp_in)
        # at the end of the hole of the porta (no tolerance):
        self.d_o[11] = self.vec_d(self.filt_cen_d + filter_w/2.)
        self.d_o[12] = self.vec_d(self.tot_d)

        # these are negative because actually the pos_w indicates a negative
        # position along axis_w

        self.w_o[0] = V0
        #1: at the first bolt column
        self.w_o[1] = self.vec_w(-boltcol1_dist)
        #2: at the second bolt column
        self.w_o[2] = self.vec_w(-boltcol2_dist)
        #3: at the third bolt column
        self.w_o[3] = self.vec_w(-boltcol3_dist)

        #7: at the end of the piece
        self.w_o[7] = self.vec_w(-self.tot_w/2.)
        #6: at the inner side of the clamp rails
        # add belt_clamp because  w_o are negative
        self.w_o[6] = self.w_o[7] + self.vec_w(beltclamp_l)
        #5: at the outer side of the clamp post (smaller circle)
        self.w_o[5] = self.w_o[6] + self.vec_w(clamp_post_dist)
        #4: at the inner side of the clamp post (larger circle)
        self.w_o[4] = self.w_o[5] + self.vec_w(self.beltpost_l)


        #0: at the bottom (base)
        self.h_o[0] = V0
        #1: at the base for the porta
        self.h_o[1] = self.vec_h(base_h - self.filt_hole_h)
        #2: at the top of the base
        self.h_o[2] = self.vec_h(base_h)
        #3: first row of bolts
        self.h_o[3] = self.vec_h(base_h + self.boltrow1_h)
        #4: second row of bolts
        self.h_o[4] = self.h_o[3] + self.vec_h(boltrow1_2_dist)
        #5: third row of bolts, taking self.h_o[3]
        self.h_o[5] = self.h_o[3] + self.vec_h(boltrow1_3_dist)
        #6: 4th row of bolts
        self.h_o[6] = self.h_o[3] + self.vec_h(boltrow1_4_dist)
        #7: at the base of the belt clamp
        self.h_o[7] = self.vec_h(self.hold_h)
        #8: at the middle of the belt clamp
        self.h_o[8] = self.vec_h(self.hold_h + self.beltclamp_h/2.)
        #9: at the top of the piece
        self.h_o[9] = self.vec_h(self.tot_h)

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        # -------- building of the piece
        # the base
        shp_base = fcfun.shp_box_dir (box_w = self.tot_w,
                                      box_d = self.tot_d,
                                      box_h = base_h,
                                      fc_axis_w = self.axis_w,
                                      fc_axis_d = self.axis_d,
                                      fc_axis_h = self.axis_h,
                                      cw = 1, cd = 0, ch = 0,
                                      pos = self.pos_o)


        shp_base = fcfun.shp_filletchamfer_dir (shp_base, self.axis_h,
                                                fillet = 1, radius = fillet_r)
        shp_base = shp_base.removeSplitter()

        # the holder to attach to a linear guide

        shp_holder = fcfun.shp_boxdir_fillchmfplane (
                                        box_w = self.tot_w,
                                        box_d = hold_d,
                                        box_h = self.hold_h,
                                        axis_d = self.axis_d,
                                        axis_h = self.axis_h,
                                        cw = 1, cd = 0, ch = 0,
                                        fillet = 1,
                                        radius = fillet_r,
                                        plane_fill = self.axis_d.negative(),
                                        both_planes = 0,
                                        edge_dir = self.axis_h,
                                        pos = self.pos_o)

        #shp_holder = fcfun.shp_box_dir (box_w = self.tot_w,
                                        #box_d = hold_d,
                                        #box_h = self.hold_h,
                                        #fc_axis_w = self.axis_w,
                                        #fc_axis_d = self.axis_d,
                                        #fc_axis_h = self.axis_h,
                                        #cw = 1, cd = 0, ch = 1,
                                        #pos = self.pos_o)
        #shp_base = fcfun.shp_filletchamfer_dir (shp_base, self.axis_h,
                                                #fillet = 1, radius = fillet_r)
        shp_base = shp_base.removeSplitter()

        shp_l = shp_base.fuse(shp_holder)
        shp_l = shp_l.removeSplitter()
        # pos (6,0,2): position at the corner of the L
        shp_l = fcfun.shp_filletchamfer_dirpt (shp_l,
                                            fc_axis= self.axis_w,
                                            fc_pt = self.get_pos_dwh(6,0,2),
                                            fillet = 0, radius = fillet_r)
        shp_l = shp_l.removeSplitter()
        # now we have the L shape with its chamfers and fillets

        # ------------------- Holes for the filter
        # include tolerances, along nh: only half of it, along h= 1 to make
        # the cut
        # pos (9,0,1) position at the center of the porta, at its bottom
        shp_filter_hole = fcfun.shp_box_dir_xtr (box_w = self.filt_hole_w,
                                             box_d = self.filt_hole_d,
                                             box_h = self.filt_hole_h,
                                             fc_axis_h = self.axis_h,
                                             fc_axis_d = self.axis_d,
                                             cw = 1, cd = 1, ch = 0,
                                             xtr_h = 1, xtr_nh = tol/2.,
                                             xtr_d = tol, xtr_nd = tol,
                                             xtr_w = tol, xtr_nw = tol,
                                             pos = self.get_pos_dwh(9,0,1))
        # pos (9,0,0) position at the center of the porta, at the bottom of the
        # piece
        # no extra on top because it will be fused with shp_filter_hole
        shp_filter_thruhole = fcfun.shp_box_dir_xtr (box_w = self.filt_supp_w,
                                             box_d = self.filt_supp_d,
                                             box_h = base_h,
                                             fc_axis_h = self.axis_h,
                                             fc_axis_d = self.axis_d,
                                             cw = 1, cd = 1, ch = 0,
                                             xtr_h = 0, xtr_nh = 1,
                                             xtr_d = tol, xtr_nd = tol,
                                             xtr_w = tol, xtr_nw = tol,
                                             pos = self.get_pos_dwh(9,0,0))
        shp_fuse_filter_hole = shp_filter_hole.fuse(shp_filter_thruhole)
        shp_l = shp_l.cut(shp_fuse_filter_hole)
        shp_l = shp_l.removeSplitter()
        # the L with the hole in the base is done

        # ---------------- Holes for the bolts

        bolt_list = []

        shp_cen_bolt = fcfun.shp_bolt_dir (r_shank = self.bolt_cen_r_tol,
                                           l_bolt = hold_d,
                                           r_head = self.bolt_cen_head_r_tol,
                                           l_head = self.bolt_cen_head_l_tol,
                                           xtr_head = 1,
                                           xtr_shank = 1,
                                           support = 0, #not at printing directi
                                           fc_normal = self.axis_d.negative(),
                                           pos_n = 2,
                                           pos = self.get_pos_dwh(0,0,3))
        bolt_list.append (shp_cen_bolt)
        # the rest of the bolts come in pairs:
        for w_side in [-1,1]:
            # the wider bolts (although can be smaller)
            for cen_col, cen_row in zip([2,3], [4,3]):
                boltpos = self.get_pos_dwh(0,w_side*cen_col, cen_row)
                shp_cen_bolt = fcfun.shp_bolt_dir ( 
                                           r_shank = self.bolt_cen_r_tol,
                                           l_bolt = hold_d,
                                           r_head = self.bolt_cen_head_r_tol,
                                           l_head = self.bolt_cen_head_l_tol,
                                           xtr_head = 1,
                                           xtr_shank = 1,
                                           support = 0, #not at printing directi
                                           fc_normal = self.axis_d.negative(),
                                           pos_n = 2,
                                           pos = boltpos)
                bolt_list.append (shp_cen_bolt)
            # the smaller bolts (although can be larger). Linear guide
            # first row:
            boltpos = self.get_pos_dwh(0,w_side*1, 3)
            shp_lin_bolt = fcfun.shp_bolt_dir ( 
                                       r_shank = self.bolt_linguide_r_tol,
                                       l_bolt = hold_d,
                                       r_head = self.bolt_linguide_head_r_tol,
                                       l_head = self.bolt_linguide_head_l_tol,
                                       xtr_head = 1,
                                       xtr_shank = 1,
                                       support = 0, #not at printing directi
                                       fc_normal = self.axis_d.negative(),
                                       pos_n = 2,
                                       pos = boltpos)
            bolt_list.append (shp_lin_bolt)
            # 3rd and 4th row. Just 2 shanks and a stadium per side
            for linrow in [5, 6]:
                boltpos = self.get_pos_dwh(0,w_side*1, linrow)
                shp_lin_shank = fcfun.shp_cylcenxtr ( 
                                       r = self.bolt_linguide_r_tol,
                                       h = hold_d,
                                       normal = self.axis_d,
                                       ch = 0,
                                       xtr_top = 0, #no need: stadium
                                       xtr_bot = 1,
                                       pos = boltpos)
                bolt_list.append (shp_lin_shank)
            # the stadium for both bolts head (they are too close)
            stadpos = self.get_pos_dwh(6,w_side*1, 5)
            shp_stad = fcfun.shp_stadium_dir (
                                 length = boltrow1_4_dist - boltrow1_3_dist,
                                 radius = self.bolt_linguide_head_r_tol,
                                 height = self.bolt_linguide_head_l_tol,
                                 fc_axis_h = self.axis_d.negative(),
                                 fc_axis_l = self.axis_h,
                                 ref_l = 2,
                                 ref_h = 2,
                                 xtr_h = 0, xtr_nh = 1,
                                 pos = stadpos)
            bolt_list.append (shp_stad)
                                 
        shp_bolts = fcfun.fuseshplist(bolt_list)
        shp_l = shp_l.cut(shp_bolts)

        # ---------------- Belt clamps
        # at both sides
        clamp_list = []
        for w_side in [-1,1]:
            clamp_pos = self.get_pos_dwh(0, w_side*7,7)
            if w_side == 1:
                clamp_axis_w = self.axis_w.negative()
            else:
                clamp_axis_w = self.axis_w
            shp_clamp = fcfun.shp_box_dir_xtr (
                                      box_w = beltclamp_l,
                                      box_d = self.beltclamp_blk_t,
                                      box_h = beltclamp_h,
                                      fc_axis_h = self.axis_h,
                                      fc_axis_d = self.axis_d,
                                      fc_axis_w = clamp_axis_w,
                                      cw = 0, cd = 0, ch = 0,
                                      xtr_nh = 1,
                                      pos = clamp_pos)


            # fillet the corner
            shp_clamp = fcfun.shp_filletchamfer_dirpt (shp_clamp, self.axis_h,
                                               fc_pt = clamp_pos,
                                               fillet = 1, radius = fillet_r)
            shp_clamp = shp_clamp.removeSplitter()
            clamp_list.append (shp_clamp)

            # the other clamp, with no fillet
            clamp_pos = self.get_pos_dwh(6, w_side*7,7)
            shp_clamp = fcfun.shp_box_dir_xtr (
                                      box_w = beltclamp_l,
                                      box_d = self.beltclamp_blk_t,
                                      box_h = beltclamp_h,
                                      fc_axis_h = self.axis_h,
                                      fc_axis_d = self.axis_d.negative(),
                                      fc_axis_w = clamp_axis_w,
                                      cw = 0, cd = 0, ch = 0,
                                      xtr_nh = 1,
                                      pos = clamp_pos)
            clamp_list.append (shp_clamp)

            # the belt post
            beltpost_pos = self.get_pos_dwh(2, w_side*5,7)
            shp_beltpost = fcfun.shp_belt_dir(
                                       center_sep = 2 * self.lr_beltpost_r,
                                       rad1 = sm_beltpost_r,
                                       rad2 = self.lr_beltpost_r,
                                       height = beltclamp_h,
                                       fc_axis_h = self.axis_h,
                                       fc_axis_l = clamp_axis_w,
                                       ref_l = 3,
                                       ref_h = 2,
                                       xtr_h = 0, xtr_nh = 1,
                                       pos = beltpost_pos)
            
            clamp_list.append (shp_beltpost)
        shp_filterholder = shp_l.multiFuse(clamp_list)
        shp_filterholder = shp_filterholder.removeSplitter()
        #Part.show (shp_filterholder)
            
        
        self.shp = shp_filterholder


#shp = ShpFilterHolder(
#                 filter_l = 60.,
#                 filter_w = 25.,
#                 filter_t = 2.5,
#                 base_h = 6.,
#                 hold_d = 12.,
#                 filt_supp_in = 2.,
#                 filt_rim = 3.,
#                 filt_cen_d = 0,
#                 fillet_r = 1.,
#                 # linear guides SEBLV16 y SEBS15, y MGN12H:
#                 boltcol1_dist = 20/2.,
#                 boltcol2_dist = 12.5, #thorlabs breadboard distance
#                 boltcol3_dist = 25,
#                 boltrow1_h = 0,
#                 boltrow1_2_dist = 12.5,
#                 # linear guide MGN12H
#                 boltrow1_3_dist = 20.,
#                 # linear guide SEBLV16 and SEBS15
#                 boltrow1_4_dist = 25.,

#                 bolt_cen_mtr = 4, 
#                 bolt_linguide_mtr = 3, # linear guide bolts

#                 beltclamp_t = 3.,
#                 beltclamp_l = 12.,
#                 beltclamp_h = 8.,
#                 clamp_post_dist = 4.,
#                 sm_beltpost_r = 1.,

#                 tol = kcomp.TOL,
#                 axis_d = VX,
#                 axis_w = VY,
#                 axis_h = VZ,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos_h = 0,
#                 pos = V0)





class PartFilterHolder (fc_clss.SinglePart, ShpFilterHolder):
    """ Integration of a ShpFilterHolder object into a PartFilterHolder
    object, so it is a FreeCAD object that can be visualized in FreeCAD
    """

    def __init__(self,
                 filter_l = 60.,
                 filter_w = 25.,
                 filter_t = 2.5,
                 base_h = 6.,
                 hold_d = 12.,
                 filt_supp_in = 2.,
                 filt_rim = 3.,
                 filt_cen_d = 0,
                 fillet_r = 1.,
                 # linear guides SEBLV16 y SEBS15, y MGN12H:
                 boltcol1_dist = 20/2.,
                 boltcol2_dist = 12.5, #thorlabs breadboard distance
                 boltcol3_dist = 25,
                 boltrow1_h = 0,
                 boltrow1_2_dist = 12.5,
                 # linear guide MGN12H
                 boltrow1_3_dist = 20.,
                 # linear guide SEBLV16 and SEBS15
                 boltrow1_4_dist = 25.,

                 bolt_cen_mtr = 4, 
                 bolt_linguide_mtr = 3, # linear guide bolts

                 beltclamp_t = 3.,
                 beltclamp_l = 12.,
                 beltclamp_h = 8.,
                 clamp_post_dist = 4.,
                 sm_beltpost_r = 1.,

                 tol = kcomp.TOL,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0,
                 model_type = 0, # exact
                 name = ''):

        default_name = 'filter_holder'
        self.set_name (name, default_name, change = 0)
        # First the shape is created
        ShpFilterHolder.__init__(self,
                 filter_l = filter_l,
                 filter_w = filter_w,
                 filter_t = filter_t,
                 base_h = base_h,
                 hold_d = hold_d,
                 filt_supp_in = filt_supp_in,
                 filt_rim = filt_rim,
                 filt_cen_d = filt_cen_d,
                 fillet_r = fillet_r,
                 boltcol1_dist = boltcol1_dist,
                 boltcol2_dist = boltcol2_dist,
                 boltcol3_dist = boltcol3_dist,
                 boltrow1_h = boltrow1_h,
                 boltrow1_2_dist = boltrow1_2_dist,
                 boltrow1_3_dist = boltrow1_3_dist,
                 boltrow1_4_dist = boltrow1_4_dist,

                 bolt_cen_mtr = bolt_cen_mtr, 
                 bolt_linguide_mtr = bolt_linguide_mtr,

                 beltclamp_t = beltclamp_t,
                 beltclamp_l = beltclamp_l,
                 beltclamp_h = beltclamp_h,
                 clamp_post_dist = clamp_post_dist,
                 sm_beltpost_r = sm_beltpost_r,

                 tol = tol,
                 axis_d = axis_d,
                 axis_w = axis_w,
                 axis_h = axis_h,
                 pos_d = pos_d,
                 pos_w = pos_w,
                 pos_h = pos_h,
                 pos = pos)


        # Then the Part
        fc_clss.SinglePart.__init__(self)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])



#doc = FreeCAD.newDocument()

#fco = PartFilterHolder(
#                 filter_l = 60.,
#                 filter_w = 25.,
#                 filter_t = 2.5,
#                 base_h = 6.,
#                 hold_d = 12.,
#                 filt_supp_in = 2.,
#                 filt_rim = 3.,
#                 filt_cen_d = 30,
#                 fillet_r = 1.,
#                 # linear guides SEBLV16 y SEBS15, y MGN12H:
#                 boltcol1_dist = 20/2.,
#                 boltcol2_dist = 12.5, #thorlabs breadboard distance
#                 boltcol3_dist = 25,
#                 boltrow1_h = 0,
#                 boltrow1_2_dist = 12.5,
#                 # linear guide MGN12H
#                 boltrow1_3_dist = 20.,
#                 # linear guide SEBLV16 and SEBS15
#                 boltrow1_4_dist = 25.,

#                 bolt_cen_mtr = 4, 
#                 bolt_linguide_mtr = 3, # linear guide bolts

#                 beltclamp_t = 3.,
#                 beltclamp_l = 12.,
#                 beltclamp_h = 8.,
#                 clamp_post_dist = 4.,
#                 sm_beltpost_r = 1.,

#                 tol = kcomp.TOL,
#                 axis_d = VX,
#                 axis_w = VY,
#                 axis_h = VZ,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos_h = 0,
#                 pos = V0)

#fco.set_color(fcfun.ORANGE_08)



#doc.recompute()
