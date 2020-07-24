# ----------------------------------------------------------------------------
# -- Set of idler tensioner and its holder
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m/freecad_filter_stage
# -- January-2018
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------


#                           axis_h            axis_h 
#                            :                  :
# ....................... ___:___               :______________
# :                      |  ___  |     pos_h:   |  __________  |---
# :                      | |   | |        3     | |__________| | : |
# :+hold_h              /| |___| |\       1,2   |________      |---
# :                    / |_______| \            |        |    /      
# :             . ____/  |       |  \____       |________|  /
# :..hold_bas_h:.|_::____|_______|____::_|0     |___::___|/......axis_d
#                                               0    1           2: pos_d
#
#
#
#                 .... hold_bas_w ........
#                :        .hold_w.        :
#              aluprof_w :    wall_thick  :
#                :..+....:      +         :
#                :       :     : :        :
#       pos_w:   2__1____:___0_:_:________:........axis_w
#                |    |  | :   : |  |     |    :
#                |  O |  | :   : |  |  O  |    + hold_bas_d
#                |____|__| :   : |__|_____|....:
#                        | :   : |
#                        |_:___:_|
#                          |   |
#                           \_/
#                            :
#                            :
#                           axis_d
#
# min_width = 1 Mininum width
#
#                 .... hold_bas_w ........
#                :        .hold_w.        :
#             washer diam:    wall_thick  :
#                :..+....:      +         :
#                :       :     : :        :
#       pos_w:   2__1____:___0_:_:________:........axis_w
#                |    |  | :   : |  |     |    :
#                |  O |  | :   : |  |  O  |    + hold_bas_d
#                |____|__| :   : |__|_____|....:
#                        | :   : |
#                        |_:___:_|
#                          |   |
#                           \_/
#                            :
#                            :
#                           axis_d


# the tensioner set is referenced on 3 perpendicular axis:
# - axis_d: depth
# - axis_w: width
# - axis_h: height
# There is a position of the piece:
# - that can be in a different point

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
import partset 

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ShpIdlerTensioner (shp_clss.Obj3D):
    """ Creates the idler pulley tensioner shape

                       nut_space 
                       .+..
                       :  :
       nut_holder_thick:  :nut_holder_thick
                      +:  :+
                     : :  : :    pulley_stroke_dist
           :         : :  : :       .+.
           :         : :  : :       : : idler_r_ext
           :         : :  : :       : :.+..
           :         : :  : :       : :   : idler_r_int
           :         : :  : :       : :   :.+...
           :         : :  : :       : :   :    :
        ________     : :__:_:_______:_:___:____:..................
       |___::___|     /       ____     __:_:___|.....+wall_thick :
       |    ....|    |  __   /     \  |            :             + tens_h
       |   ()...|    |:|  |:|       | |            + idler_h     :
       |________|    |  --   \_____/  |________....:             :
       |___::___|     \__________________:_:___|.................:
       :        :    :      :       :          :
       :........:    :      :...+...:          :
           +         :......:  tens_stroke     :
         tens_w      :  +                      :
    (2*idler_r_int)  : nut_holder_tot          :
                     :                         :
                     :.........tens_d..........:


                 pos_h
        ________       ________________________
       |___::___|     /       ____     ___::___|
       |    ....|    |  __   /     \  | 
       |   ()...|  0 o:|  |:|       | |        -----> axis_d
       |________|  1 |  --   \_____/  |________
       |___::___|  2  \___________________::___|
       1   0         0  1   2       3      4   5  : pos_d 
       pos_w

        pos_o (origin) is at pos_d=0, pos_w=0, pos_h=0, It marked with o

    Parameters:
    -----------
    wall_thick : float
        Thickness of the walls
    tens_stroke : float
        Length of the idler tensioner body, the stroke. Not including the pulley
        neither the space for the tensioner bolt
    pulley_stroke_dist : float
        Distance along axis_d from between the end of the pulley and the stroke
        Not including the pulley. See picture dimensions
        if 0: it will be the same as wall_thick
    nut_holder_thick : float
        Length of the space along axis_d above and below the nut, for the bolt
    in_fillet: float
        radius of the inner fillets
    idler_h : float
        height of the idler pulley
    idler_r_in : float
        internal radius of the idler pulley. This is the radius of the surface
        where the belt goes
    idler_r_ext : float
        external radius of the idler pulley. This is the most external part of
        the pulley (for example the radius of the large washer)
    boltidler_mtr : integer (could be float 2.5)
        diameter (metric) of the bolt for the idler pulley
    bolttens_mtr : integer (could be float 2.5)
        diameter (metric) of the bolt for the tensioner
    opt_tens_chmf : int
        1: there is a chamfer at every edge of tensioner, inside the holder
        0: there is a chamfer only at the edges along axis_w, not along axis_h
    tol : float
        Tolerances to print
    axis_d : FreeCAD.Vector
        length vector of coordinate system
    axis_w : FreeCAD.Vector
        width vector of coordinate system
        if V0: it will be calculated using the cross product: axis_d x axis_h
    axis_h : FreeCAD.Vector
        height vector of coordinate system
    pos_d : int
        location of pos along the axis_d (0,1,2,3,4,5), see drawing
        0: at the back of the holder
        1: at the beginning of the hole for the nut (position for the nut)
        2: at the beginning of the tensioner stroke hole
        3: at the end of the tensioner stroke hole
        4: at the center of the idler pulley hole
        5: at the end of the piece
    pos_w : int
        location of pos along the axis_w (0,1) almost symmetrical
        0: at the center of symmetry
        1: at the end of the piece along axis_w at the negative side
    pos_h : int
        location of pos along the axis_h (0,1,2), symmetrical
        0: at the center of symmetry
        1: at the inner base: where the base of the pulley goes
        2: at the bottom of the piece (negative side of axis_h)
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes:
    -----------
    All the parameters and attributes of father class SinglePart

    Dimensional attributes:
    tens_d : float
        total length (depth) of the idler tensioner
    tens_w : float
        total width of the idler tensioner
    tens_h : float
        total height of the idler tensioner
    tens_d_inside : float
        length (depth) of the idler tensioner that can be inside the holder

    prnt_ax : FreeCAD.Vector
        Best axis to print (normal direction, pointing upwards)
    d0_cen : int
    w0_cen : int
    h0_cen : int
        indicates if pos_h = 0 (pos_d, pos_w) is at the center along
        axis_h, axis_d, axis_w, or if it is at the end.
        1 : at the center (symmetrical, or almost symmetrical)
        0 : at the end

    """
    def __init__(self,
                 idler_h ,
                 idler_r_in ,
                 idler_r_ext ,
                 in_fillet = 2.,
                 wall_thick = 5.,
                 tens_stroke = 20. ,
                 pulley_stroke_dist = 0,
                 nut_holder_thick = 4. ,
                 boltidler_mtr = 3,
                 bolttens_mtr = 3,
                 opt_tens_chmf = 1,
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
        if pulley_stroke_dist == 0: # default value
            self.pulley_stroke_dist = wall_thick

        # dictionary of the bolt for the idler pulley
        # din 912 bolts are used:
        self.boltidler_dict = kcomp.D912[boltidler_mtr]
        self.boltidler_r_tol = self.boltidler_dict['shank_r_tol']

        # --- tensioner bolt and nut values
        # dictionary of the bolt tensioner
        self.bolttens_dict = kcomp.D912[bolttens_mtr]
        # the shank radius including tolerance
        self.bolttens_r_tol = self.bolttens_dict['shank_r_tol']
        # dictionary of the nut
        self.nuttens_dict = kcomp.D934[bolttens_mtr]
        self.nut_space = kcomp.NUT_HOLE_MULT_H + self.nuttens_dict['l_tol']
        self.nut_holder_tot = self.nut_space + 2* self.nut_holder_thick
        # circum diameter of the nut
        self.tensnut_circ_d = self.nuttens_dict['circ_d']
        # circum radius of the nut, with tolerance
        self.tensnut_circ_r_tol = self.nuttens_dict['circ_r_tol']
        # the apotheme of the nut
        self.tensnut_ap_tol = (self.nuttens_dict['a2']+tol/2.)/2.

        # --- idler tensioner dimensions
        self.tens_h = self.idler_h + 2*wall_thick
        self.tens_d = (  self.nut_holder_tot
                       + tens_stroke
                       + self.pulley_stroke_dist
                       + idler_r_ext
                       + idler_r_in)

        self.tens_d_inside = (   self.nut_holder_tot
                               + tens_stroke
                               + self.pulley_stroke_dist)

        self.tens_w = max(2 * idler_r_in, self.tensnut_circ_d)

        self.d0_cen = 0
        self.w0_cen = 1 # symmetrical
        self.h0_cen = 1 # symmetrical

        self.d_o[0] = V0
        self.d_o[1] = self.vec_d(nut_holder_thick)
        self.d_o[2] = self.vec_d(self.nut_holder_tot)
        self.d_o[3] = self.vec_d(self.nut_holder_tot + tens_stroke)
        self.d_o[4] = self.vec_d(self.tens_d - idler_r_in)
        self.d_o[5] = self.vec_d(self.tens_d)

        # these are negative because actually the pos_w indicates a negative
        # position along axis_w
        self.w_o[0] = V0
        self.w_o[1] = self.vec_w(-self.tens_w/2.)

        self.h_o[0] = V0
        self.h_o[1] = self.vec_h(-idler_h/2.)
        self.h_o[2] = self.vec_h(-self.tens_h/2.)

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        # ------------- building of the piece --------------------

        #  --------------- step 01-04 ------------------------      
        #  rectangular cuboid with basic dimensions, but chamfered
        #  at the inner end
        # 
        #       axis_h
        #          : .....tens_d.......
        #          : : ________________:
        #          : /               /|
        #           /               / |
        #       .. /_______________/  |.......
        #       : /                |  /     . 
        # tens_h  |                | /     . tens_w
        #       :. \_______________|/......
        #
        #
        #     o: shows the position of the origin: pos_o
        #
        #                axis_h       axis_h
        #                  :            :
        #         .... ____:____        : ______________________
        #         :   |.........|     ch2/                      |
        #         :   |:       :|       |                       |      
        #  tens_h +   |:   o   :|       o                       |-----> axis_d
        #         :   |:.......:|       |                       |
        #         :...|_________|     ch1\______________________|
        #             :         :       :                       :
        #             :.tens_h..:       :...... tens_d .........:
        #
        #              ____o____ ....> axis_w
        #          ch3/_________\ch4
        #             |         |          chamfer ch3 and ch4 are optional
        #             |         |          Depending on opt_tens_chmf
        #             |         |
        #             |         |
        #             |         |
        #             |         |
        #             |.........|
        #             |         |
        #             |         |
        #             |         |
        #             |_________|
        #                  :
        #                  :
        #                  V
        #                 axis_d

        if opt_tens_chmf == 0: # no optional chamfer, only along axis_w
            edge_dir = self.axis_w
        else:
            edge_dir = V0
   
        shp01chmf = fcfun.shp_boxdir_fillchmfplane(
                               box_w = self.tens_w,
                               box_d = self.tens_d,
                               box_h = self.tens_h,
                               axis_d = self.axis_d,
                               axis_h = self.axis_h,
                               cd=0, cw=1, ch=1,
                               # no tolerances, this is the piece
                               fillet = 0, # chamfer
                               radius = 2*in_fillet,
                               plane_fill = self.axis_d.negative(),
                               both_planes = 0,
                               edge_dir = edge_dir,
                               pos = self.pos_o)
        #  --------------- step 02 ---------------------------  
        # Space for the idler pulley
        #    axis_h
        #      :
        #      : ______________________
        #       /               _______|....
        #      |               |           + idler_h
        #      |               |       5   :----------->axis_d
        #      |               |_______....:
        #       \______________________|...wall_thick
        #                      :       :
        #                      :.......:
        #                         +
        #                       2 * idler_r_xtr
        #
        # the position is pos_d = 5
        # maybe should be advisable to have tolerance, but usually, the 
        # washers have tolerances, and usually are less thick than the nominal
        idler_h_hole =  idler_h # + tol
        if idler_h_hole != idler_h:
            self.idler_h_hole = idler_h_hole
        # NO CHAMFER to be able to fit the pulley well
        shp02cut = fcfun.shp_box_dir_xtr(
                               box_w = self.tens_w,
                               box_d = idler_r_in + idler_r_ext,
                               box_h = idler_h_hole,
                               fc_axis_d = self.axis_d.negative(),
                               fc_axis_h = self.axis_h,
                               cd=0, cw=1, ch=1,
                               xtr_w = 1,
                               xtr_nw = 1,
                               xtr_d = tol, # tol to fit the large washer
                               xtr_nd = 1, # extra along axis_d (positive)
                               pos = self.get_pos_d(5))
        shp02 = shp01chmf.cut(shp02cut)
        shp02 = shp02.removeSplitter() # refine shape
        #  --------------- step 03 --------------------------- 
        # Fillets at the idler end:
        #
        #    axis_h
        #      :
        #      :_______________________f2
        #      |                 ______|
        #      |                /      f4
        #      |               |       5    ------> axis_d
        #      |                \______f3...
        #      |_______________________|....+ wall_thick.....> Y
        #      :                       f1
        #      :...... tens_d .........:
        #
        pt_f1 = self.get_pos_d(5) + self.vec_h( -self.tens_h/2.)
        pt_f2 = self.get_pos_d(5) + self.vec_h(  self.tens_h/2.)
        pt_f3 = self.get_pos_d(5) + self.vec_h( -idler_h_hole/2.)
        pt_f4 = self.get_pos_d(5) + self.vec_h(  idler_h_hole/2.)

        if wall_thick/2. <= in_fillet:
            msg1 = 'Radius of fillet is larger than 2 x wall thick'
            msg2 = ' making fillet smaller: '
            wall_fillet_r = self.wall_thick /2. - 0.1
            logger.warning(msg1 + msg2 + str(wall_fillet_r))
        else:
            wall_fillet_r = in_fillet
        shp03 = fcfun.shp_filletchamfer_dirpts (
                                            shp=shp02,
                                            fc_axis=self.axis_w,
                                            fc_pts=[pt_f1,pt_f2, pt_f3, pt_f4],
                                            fillet = 1,
                                            radius=wall_fillet_r)
        #  --------------- step 04 done at step 01 ------------------------ 

        #  --------------- step 05 --------------------------- 
        # Shank hole for the idler pulley:

        #    axis_h                  idler_r_xtr
        #      :                    .+..
        #      : ___________________:__:
        #       /                __:_:_|
        #      |                /             
        #      |               |    4   ----------> axis_d
        #      |                \______
        #       \__________________:_:_|
        #      :                       :
        #      :...... tens_d .........:
        #                     
        # pos_d = 4
        shp05 = fcfun.shp_cylcenxtr (r = self.boltidler_r_tol,
                                     h = self.tens_h,
                                     normal = self.axis_h,
                                     ch = 1, xtr_top = 1, xtr_bot = 1,
                                     pos = self.get_pos_d(4))
        #  --------------- step 06 --------------------------- 
        # Hole for the leadscrew (stroke):

        #    axis_h
        #      :
        #      : ______________________
        #       /      _____     __:_:_|
        #      |    f2/     \f4 /             
        #      |     2       | |        -------> axis_d
        #      |    f1\_____/f3 \______
        #       \__________________:_:_|
        #      :     :       :         :
        #      :     :.......:         :
        #      :     :   +             :
        #      :.....:  tens_stroke    :
        #      :  +                    :
        #      : nut_holder_tot        :
        #      :                       :
        #      :...... tens_d .........:
        # 
        #  pos_d = 2
        shp06a = fcfun.shp_box_dir_xtr(box_w = self.tens_w,
                                       box_d = self.tens_stroke,
                                       box_h = self.idler_h,
                                       fc_axis_h = self.axis_h,
                                       fc_axis_d = self.axis_d,
                                       xtr_w = 1, xtr_nw = 1,
                                       cw=1, cd=0, ch=1,
                                       pos=self.get_pos_d(2))
        shp06 =  fcfun.shp_filletchamfer_dir (shp=shp06a,
                                              fc_axis=self.axis_w,
                                              fillet = 0, radius=self.in_fillet)

        #  --------------- step 07 --------------------------- 
        # Hole for the leadscrew shank at the beginning

        #    axis_h
        #      :
        #      : ______________________
        #       /      _____     __:_:_|
        #      |      /     \   /
        #      |:::::|       | |        ---->axis_d
        #      |      \_____/   \______
        #       \__________________:_:_|
        #      :     :                 :
        #      :     :                 :
        #      :     :                 :
        #      :.....:                 :
        #      :  +                    :
        #      : nut_holder_tot        :
        #      :                       :
        #      :...... tens_d .........:
        #
        shp07 = fcfun.shp_cylcenxtr (r = self.bolttens_r_tol,
                                     h = self.nut_holder_tot,
                                     normal = self.axis_d,
                                     ch = 0, xtr_top = 1, xtr_bot = 1,
                                     pos = self.pos_o)
        #  --------------- step 08 --------------------------- 
        # Hole for the leadscrew nut

        #    axis_h
        #      :
        #      : ______________________
        #       /      _____     __:_:_|
        #      |  _   /     \   /
        #      |:1_|:|       | |       -----> axis_d
        #      |      \_____/   \______
        #       \__________________:_:_|
        #      : :   :                 :
        #      :+    :                 :
        #      :nut_holder_thick       :
        #      :.....:                 :
        #      :  +                    :
        #      : nut_holder_total      :
        #      :                       :
        #      :...... tens_d .........:
        #
        # position at pos_d = 1

        shp08 = fcfun.shp_nuthole (
                               nut_r = self.tensnut_circ_r_tol,
                               nut_h = self.nut_space,
                               hole_h = self.tens_w/2,
                               xtr_nut = 1, xtr_hole = 1, 
                               fc_axis_nut = self.axis_d,
                               fc_axis_hole = self.axis_w,
                               ref_nut_ax = 2, # pos not centered on axis nut 
                               # pos at center of nut on axis hole 
                               ref_hole_ax = 1, 
                               pos = self.get_pos_d(1))

        # --------- step 09:
        # --------- Last step, union and cut of the steps 05, 06, 07, 08
        shp09cut = fcfun.fuseshplist([shp05, shp06, shp07, shp08])
        shp09_final = shp03.cut(shp09cut)

        self.shp = shp09_final

        # normal axes to print without support
        self.prnt_ax = self.axis_w


#shp= ShpIdlerTensioner(idler_h = 10. ,
#                 idler_r_in  = 5,
#                 idler_r_ext = 6,
#                 in_fillet = 2.,
#                 wall_thick = 5.,
#                 tens_stroke = 20. ,
#                 pulley_stroke_dist = 0,
#                 nut_holder_thick = 4. ,
#                 boltidler_mtr = 3,
#                 bolttens_mtr = 3,
#                 opt_tens_chmf = 1,
#                 tol = kcomp.TOL,
#                 axis_d = VX,
#                 axis_w = VY,
#                 axis_h = VZ,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos_h = 0,
#                 pos = V0)

class PartIdlerTensioner (fc_clss.SinglePart, ShpIdlerTensioner):
    """ Integration of a ShpIdlerTensioner object into a PartIlderTensioner
    object, so it is a FreeCAD object that can be visualized in FreeCAD
    """

    def __init__(self,
                 idler_h ,
                 idler_r_in ,
                 idler_r_ext ,
                 in_fillet = 2.,
                 wall_thick = 5.,
                 tens_stroke = 20. ,
                 pulley_stroke_dist = 0,
                 nut_holder_thick = 4. ,
                 boltidler_mtr = 3,
                 bolttens_mtr = 3,
                 opt_tens_chmf = 1,
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

        default_name = 'idler_tensioner'
        self.set_name (name, default_name, change = 0)
        # First the shape is created
        ShpIdlerTensioner.__init__(self,
                                  idler_h = idler_h ,
                                  idler_r_in  = idler_r_in,
                                  idler_r_ext = idler_r_ext,
                                  in_fillet = in_fillet,
                                  wall_thick = wall_thick,
                                  tens_stroke = tens_stroke,
                                  pulley_stroke_dist = pulley_stroke_dist,
                                  nut_holder_thick = nut_holder_thick ,
                                  boltidler_mtr = boltidler_mtr,
                                  bolttens_mtr = bolttens_mtr,
                                  opt_tens_chmf = opt_tens_chmf,
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

#part= PartIdlerTensioner(idler_h = 10. ,
#                 idler_r_in  = 5,
#                 idler_r_ext = 6,
#                 in_fillet = 2.,
#                 wall_thick = 5.,
#                 tens_stroke = 20. ,
#                 pulley_stroke_dist = 0,
#                 nut_holder_thick = 4. ,
#                 boltidler_mtr = 3,
#                 bolttens_mtr = 3,
#                 opt_tens_chmf = 1,
#                 tol = kcomp.TOL,
#                 axis_d = VX,
#                 axis_w = VY,
#                 axis_h = VZ,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos_h = 0,
#                 pos = V0)


class IdlerTensionerSet (fc_clss.PartsSet):
    """ Set composed of the idler pulley and the tensioner

    Parameter:
    ---------
    in_fillet: float
        radius of the inner fillets
    pos_d : int
        location of pos along the axis_d (0,1,2,3,4,5), see drawing
        0: at the back of the holder
        1: at the beginning of the hole for the nut (position for the nut)
        2: at the beginning of the tensioner stroke hole
        3: at the end of the tensioner stroke hole
        4: at the inner end of the bearing. It didnt exist in ShpIdlerTensioner
           Therefore, from this, numbers change compared with ShpIdlerTensioner
        5: at the center of the idler pulley hole
           (it is 4 in ShpIdlerTensioner)
        6: at the end of the piece (it is 5 in ShpIdlerTensioner)
    pos_w : int
        location of pos along the axis_w (0,1) almost symmetrical
        0: at the center of symmetry
        1: at the end of the tensioner along axis_w
        2: at the end of the larger washer along axis_w
    pos_h : int
        location of pos along the axis_h (0,1,2), symmetrical
        0: at the center of symmetry
        1: at the inner base: where the base of the pulley goes
        2: at the bottom of the piece
    pos : FreeCAD.Vector
        position of the piece
    See drawing:

                      nut_holder_thick:  :nut_holder_thick
                                     +:  :+
                                    : :  : :    pulley_stroke_dist
                                    : :  : :       .+.
                                    : :  : :       : :
                                    : :  : :       : :  boltidler_mtr
                                    : :  : :       : :   +
        ________                    : :__:_:_______:_:__:_:___ ....
       |___::___|                    /       ____     __:_:___|....+wall_thick
       |    ....|                   |  __   /     \  |
       |   ()...|     bolttens_mtr::|:|  |:|       | |
       |________|                   |  --   \_____/  |________
       |___::___|                    \__________________:_:___|
                                           :       :
                                           :...+...:
                                              tens_stroke

       origin: pos_o is at point o


          axis_h 
            :                                             pos_h
        ____:____              ____________________________
       |___:_:___|            /       ____     _____:_:____|
      |___________|          |       /     \  ||____:_:____|  large washer
       |_________|           |      |       | |   |_:_:_|     regular wahser
       |     ....|           |  ..  |       | |   | : : |     bearing
       |   :o:   |->axis_w   o::  ::|       | |   | : : |   0 -----> axis_d
       |_________|           |  ..  |       | |   |_:_:_|
       |_________|           |      |       | | __|_:_:_|__ 1
      |___________|          |       \_____/  ||___________|2
       |___:_:___|            \_____________________:_:____|3
      21    0                0  1   2       3     4  5     6 : pos_d 
       pos_w


       tensioner_width is the same as the idler internal diameter


    Attributes:
    -----------
    d0_cen : 0 (int)
    w0_cen : 1 (int)
    h0_cen : 1 (int)
        indicates if pos_h = 0 (pos_d, pos_w) is at the center along
        its axis, or if it is at the end (symmetrical or not)
    tens_d : float
        Depth of the tensioner
    tens_w : float
        width of the tensioner
    tens_h : float
        height of the tensioner
    tens_d_inside : float
        length (depth) of the idler tensioner that can be inside the holder



    """

    def __init__(self, 
                 boltidler_mtr = 3,
                 bolttens_mtr = 3,
                 tens_stroke = 20. ,
                 wall_thick = 5.,
                 in_fillet = 2.,
                 pulley_stroke_dist = 0,
                 nut_holder_thick = 4. ,
                 opt_tens_chmf = 1,
                 tol = kcomp.TOL,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0,
                 group = 0,
                 name = ''):

        default_name = 'idler_tensioner_set'
        self.set_name (name, default_name, change = 0)

        fc_clss.PartsSet.__init__(self, axis_d = axis_d,
                                  axis_w = axis_w, axis_h = axis_h)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])

        # pos_h/w = 0 are at the center, not pos_d
        self.d0_cen = 0
        self.w0_cen = 1
        self.h0_cen = 1

        # before creating the idler_pulley and the tensioner, we dont
        # know their dimensions and positions. We could calculate them
        # here, but it would be to calculate twice. Instead, we create
        # them, and then move them and calculate the vectors h_o, d_o, w_o

        # Creation of the idler pulley, we put it in the center
        pulley = partset.BearWashSet(metric = boltidler_mtr,
                                            axis_h = axis_h, pos_h = 0,
                                            axis_d = axis_d, pos_d = 0,
                                            axis_w = axis_w, pos_w = 0,
                                            pos = pos)
        self.append_part(pulley)
        pulley.parent = self
        #self.pulley_h =  pulley.tot_h
        #self.pulley_r_in =  pulley.r_in
        #self.pulley_r_ext =  pulley.r_ext
        # Creation of the tensioner, with pos_h,d,w = 0 because we dont know
        # the dimensions yet
        idler_tens_part =  PartIdlerTensioner(
                                     idler_h     = pulley.tot_h ,
                                     idler_r_in  = pulley.r_in,
                                     idler_r_ext = pulley.r_ext,
                                     in_fillet   = in_fillet,
                                     wall_thick  = wall_thick,
                                     tens_stroke = tens_stroke ,
                                     pulley_stroke_dist = pulley_stroke_dist,
                                     nut_holder_thick = nut_holder_thick,
                                     boltidler_mtr = boltidler_mtr,
                                     bolttens_mtr  = bolttens_mtr,
                                     opt_tens_chmf = opt_tens_chmf,
                                     tol    = tol,
                                     axis_d = self.axis_d,
                                     axis_w = self.axis_w,
                                     axis_h = self.axis_h,
                                     pos_d  = 0,
                                     pos_w  = 0,
                                     pos_h  = 0,
                                     pos    = pos)
        self.append_part(idler_tens_part)
        idler_tens_part.parent = self

        self.tens_d = idler_tens_part.tens_d
        self.tens_w = idler_tens_part.tens_w
        self.tens_h = idler_tens_part.tens_h
        self.tens_d_inside = idler_tens_part.tens_d_inside
        self.nut_holder_tot = idler_tens_part.nut_holder_tot

        

        # Now we have to move them and calculate the distance vectors h_o,..
        # pos_d, pos_w, pos_w: are different for the components and the set
        #       axis_h 
        #         :                                     pos_h for Pulley-\
        #         :                           pos_h for idlerTensPart-\
        #         :                         pos_h for TensionerSet-\
        #     ____:____              ____________________________   3  2
        #    |___:_:___|            /       ____     _____:_:____|  2  1  3
        #   |___________|          |       /     \  ||____:_:____|        2
        #    |_________|           |      |       | |   |_:_:_|     1     1
        #    |     ....|           |  ..  |       | |   | : : |   
        #    |   :o:   |           o::  ::|       | |   | : : |     0  0  0
        #    |_________|           |  ..  |       | |   |_:_:_|          -1
        #    |_________|           |      |       | | __|_:_:_|__  -1    -2
        #   |___________|          |       \_____/  ||___________| -2 -1 -3
        #    |___:_:___|            \_____________________:_:____| -3 -2
        #  -21    0    12  TensSet 0  1   2       3     4  5     6 : pos_d 
        #   -1    0    1 iTensPart 0  1   2       3        4     5
        #  -32  -101   23   Pulley                  -3 -2-101 2  3  
        #
        #         |-->axis_w       |---> axis_d

        # When pos_d,w,h are centered, d0_cen, w0_cen, h0_cen = 1
        # h_o[1] is the distance from o to -1, or from 1 to o
        self.d_o[0] = V0
        self.d_o[1] = idler_tens_part.d_o[1]
        self.d_o[2] = idler_tens_part.d_o[2]
        self.d_o[3] = idler_tens_part.d_o[3]
        # He have to add them because pulley.d_o is in opposite direction
        # pulley.d_o[2] is the  distance from o to -2, or from 2 to o
        #             pulley axis -->        + axis to pulley r_in  <--
        self.d_o[4] = idler_tens_part.d_o[4] + pulley.d_o[2]
        self.d_o[5] = idler_tens_part.d_o[4]
        self.d_o[6] = idler_tens_part.d_o[5]

        self.w_o[0] = V0
        self.w_o[1] = pulley.w_o[2]
        self.w_o[2] = pulley.w_o[3]

        # h_o[1] is the distance from o to -1, or from 1 to o
        self.h_o[0] = V0
        self.h_o[1] = pulley.h_o[2]
        self.h_o[2] = pulley.h_o[3]
        self.h_o[3] = idler_tens_part.h_o[2]

        # Now we place the idler tensioner according to pos_d,w,h
        # argument 1 means that pos_o wasnt in place and has to be
        # adjusted
        self.set_pos_o(adjust = 1)

        # Now we have the position where the origin is, but:
        # - we havent located the idler_tensioner at pos_o
        # - we havent located the pulley at pos_o + dist to axis

        # we should have call PartIdlerTensioner (pos = self.pos_o)
        # instead, we have it at (pos = self.pos)
        # so we have to move PartIdlerTensioner self.pos_o - self.pos
        self.set_part_place(idler_tens_part)

        self.set_part_place(pulley, self.get_o_to_d(5))

        # the bolt for the pulley
        bolt_length_list = kcomp.D912_L[boltidler_mtr]
        min_pulley_bolt_l = (  self.tens_h
                             + kcomp.D912[boltidler_mtr]['head_l'])
        pulley_bolt = partset.Din912BoltWashSet(metric  = boltidler_mtr,
                                         shank_l = min_pulley_bolt_l,
                                         # larger considering the washer
                                         shank_l_adjust = 2,
                                         axis_h  = self.axis_h.negative(),
                                         pos_h   = 3,
                                         pos_d   = 0,
                                         pos_w   = 0,
                                         pos     = self.get_pos_dwh(5,0,3))
        self.pulley_bolt_l = pulley_bolt.shank_l
        self.append_part(pulley_bolt)
        pulley_bolt.parent = self

        # the nut for the pulley
        pulley_nut = partset.Din934NutWashSet(metric  = boltidler_mtr,
                                              axis_h = self.axis_h.negative(),
                                              pos_h = 0,
                                              pos = self.get_pos_dwh(5,0,-3))
        self.append_part(pulley_nut)
        pulley_nut.parent = self

        # the nut for the leadscrew
        nut = fc_clss.Din934Nut(metric = bolttens_mtr,
                                axis_h = self.axis_d,
                                axis_d = self.axis_w,
                                pos_h = -1,
                                pos = self.get_pos_d(1), name = 'leadscrew_nut')
        self.append_part(nut)
        nut.parent = self
                                   

        self.place_fcos()
        if group == 1:
            self.make_group()

    def get_idler_tensioner(self):
        """gets the idler tensioner"""
        part_list = self.get_parts()
        for part_i in part_list:
            if isinstance(part_i,PartIdlerTensioner):
                return part_i 

    def get_bear_wash_set(self):
        """gets the idler tensioner"""
        part_list = self.get_parts()
        for part_i in part_list:
            if isinstance(part_i,partset.BearWashSet):
                return part_i 



#idlertensioner= IdlerTensionerSet (
#                 boltidler_mtr = 3,
#                 bolttens_mtr = 3,
#                 tens_stroke = 20. ,
#                 wall_thick = 3.,
#                 in_fillet = 1.,
#                 pulley_stroke_dist = 0,
#                 nut_holder_thick = 4. ,
#                 opt_tens_chmf = 1,
#                 tol = kcomp.TOL,
#                 axis_d = VX,
#                 axis_w = VY,
#                 axis_h = VZ,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos_h = 3,
#                 pos = FreeCAD.Vector(3,10,5),
#                 name = 'tensioner_group')




class ShpTensionerHolder (shp_clss.Obj3D):
    """ Creates the idler pulley tensioner shape


                              axis_h            axis_h 
                               :                  :
                            ___:___               :______________
                           |  ___  |              |  __________  |---
                           | |   | |              | |__________| | : |
    .---- belt_pos_h------/| |___| |\             |________      |---
    :                    / |_______| \            |        |    /      
    :             . ____/  |       |  \____       |________|  /
    :..hold_bas_h:.|_::____|_______|____::_|      |___::___|/......>axis_d
   
                                wall_thick
                                  +
                                 : :         
                    _____________:_:________.........>axis_w
                   |    |  | :   : |  |     |    :
                   |  O |  | :   : |  |  O  |    + aluprof_w
                   |____|__| :   : |__|_____|....:
                           | :   : |
                           |_:___:_|
                             |   |
                              \_/
                               :
                               :
                             axis_l

                             axis_h            axis_h 
                               :         pos_h    :
    ....................... ___:___         4     :______________
    :                      |  ___  |              |  __________  |---
    :                      | |   | |        3     | |__________| | : |
    :+hold_h              /| |___| |\       2     |________      |---
    :                    / |_______| \            |        |    /      
    :             . ____/  |       |  \____ 1     |________|  /
    :..hold_bas_h:.|_::____|___o___|____::_|0     o___::___|/......>axis_d
                                                  01   2   3     4: pos_d
   
   
   
                    .... hold_bas_w ........
                   :        .hold_w.        :
                   :       :    wall_thick  :
                   :       :      +         :
                   :       :     : :        :
          pos_w:   4__3____2_1_0_:_:________:........>axis_w
                   |    |  | :   : |  |     |    :
                   |  O |  | :   : |  |  O  |    + hold_bas_l
                   |____|__| :   : |__|_____|....:
                           | :   : |
                           |_:___:_|
                             |   |
                              \_/
                               :
                               :
                             axis_d

        pos_o (origin) is at pos_d=0, pos_w=0, pos_h=0, It's marked with o

    The part is referenced along 3 perpendicular axis
      (cartesian coordinate systems):
      - axis_d: depth
      - axis_w: width
      - axis_h: height
    There is a position of the piece:
      - pos: FreeCAD Vector
    This position of the piece (pos) can be at different locations within
      the piece. These locations are defined by:
      - pos_d: location of pos along the axis_d (0,1,2)
         - 0: at the back of the holder
         - 1: at the place where the tensioner can reach all the way inside
         - 2: at the center of the base along axis_d, where the bolts to attach
              the holder base to the aluminum profile
         - 3: at the end of the base
         - 4: at the end of the holder
      - pos_w: location of pos along the axis_w (0,1,2)
         - 0: at the center of symmetry
         - 1: at the inner walls of the holder
         - 2: at the end of the holder (the top part, where the base starts)
         - 3: at the center of the bolt holes to attach the holder base to the
              aluminum profile
         - 4: at the end of the piece along axis_w
              axes have direction. So if pos_w == 3, the piece will be drawn
              along the positive side of axis_w
      - pos_h: location of pos along the axis_h (0,1,2,3)
         - 0: at the bottom of the holder
         - 1: at the top of the base of the holder (for the bolts)
         - 2: at the bottom of the hole where the idler tensioner goes
         - 3: at the middle point of the hole where the idler tensioner goes
         - 4: at the top of the holder

    Parameters
    ----------
    aluprof_w : float
        Width of the aluminum profile
    belt_pos_h : float
        The position along axis_h where the idler pulley that conveys the belt
        starts. THIS POSITION IS CENTERED at the ilder pulley
    tens_h : float
        height of the ilder tensioner
    tens_w : float
        width of the ilder tensioner
    tens_d_inside : float
        Max length (depth) of the ilder tensioner that is inside the holder
    wall_thick : float
        Thickness of the walls
    in_fillet: float
        radius of the inner fillets
    boltaluprof_mtr : integer (could be float 2.5)
        diameter (metric) of the bolt that attachs the tensioner holder to the
        aluminum profile (or whatever is attached to)
    bolttens_mtr : integer (could be float 2.5)
        diameter (metric) of the bolt for the tensioner
    hold_bas_h : float
        height of the base of the tensioner holder
        if 0, it will take wall_thick
    opt_tens_chmf : int
        1: there is a chamfer at every edge of tensioner, inside the holder
        0: there is a chamfer only at the edges along axis_w, not along axis_h
    hold_hole_2sides : int
        In the tensioner holder there is a hole to see inside, it can be at
        each side of the holder or just on one side
        0: only at one side
        1: at both sides
    min_width: make the rim the minimum: the diameter of the washer
        0: normal width: the width of the aluminum profile
        1: minimum width: diameter of the washer
    tol : float
        Tolerances to print
    axis_d : FreeCAD.Vector
        depth vector of coordinate system
    axis_w : FreeCAD.Vector
        width vector of coordinate system
        if V0: it will be calculated using the cross product: axis_l x axis_h
    axis_h : FreeCAD.Vector
        height vector of coordinate system
    pos_d : int
        location of pos along the axis_d (0,1,2,3,4)
        0: at the back of the holder
        1: at the place where the tensioner can reach all the way inside
        2: at the center of the base along axis_d, where the bolts to attach
           the holder base to the aluminum profile
        3: at the end of the base
        4: at the end of the holder
    pos_w : int
        location of pos along the axis_w (0,1,2)
        0: at the center of symmetry
        1: at the inner walls of the holder
        2: at the end of the holder (the top part, where the base starts)
        3: at the center of the bolt holes to attach the holder base to the
           aluminum profile
        4: at the end of the piece along axis_w
              axes have direction. So if pos_w == 3, the piece will be drawn
              along the positive side of axis_w
    pos_h : int
        location of pos along the axis_h (0,1,2,3,4)
        0: at the bottom of the holder
        1: at the top of the base of the holder (for the bolts)
        2: at the bottom of the hole where the idler tensioner goes
        3: at the middle point of the hole where the idler tensioner goes
        4: at the top of the holder
    pos : FreeCAD.Vector
        position of the piece

    Parameters for the set

    tens_in_ratio : float
        from 0 to 1, the ratio of the stroke that the tensioner is inside.
        if 1: it is all the way inside
        if 0: it is all the way outside (all the tens_stroke)





    Attributes:
    -----------
    All the parameters and attributes of father class SinglePart

    prnt_ax : FreeCAD.Vector
        Best axis to print (normal direction, pointing upwards)
    d0_cen : int
    w0_cen : int
    h0_cen : int
        indicates if pos_h = 0 (pos_d, pos_w) is at the center along
        axis_h, axis_d, axis_w, or if it is at the end.
        1 : at the center (symmetrical, or almost symmetrical)
        0 : at the end

    """
    def __init__(self,
                 aluprof_w,
                 belt_pos_h,
                 tens_h,
                 tens_w,
                 tens_d_inside,
                 wall_thick = 3.,
                 in_fillet = 1.,
                 boltaluprof_mtr = 3,
                 bolttens_mtr = 3,
                 hold_bas_h = 0,
                 opt_tens_chmf = 1,
                 hold_hole_2sides = 1,
                 min_width = 0,
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

        # pos_w = 0 is at the center, not pos_d, pos_h
        self.d0_cen = 0
        self.w0_cen = 1
        self.h0_cen = 0

        # --- bolt to attach to the aluminum profile
        # dictionary of the bolt
        d_boltaluprof = kcomp.D912[boltaluprof_mtr]
        self.d_boltaluprof = d_boltaluprof
        self.boltaluprof_head_r_tol = d_boltaluprof['head_r_tol']
        self.boltaluprof_r_tol = d_boltaluprof['shank_r_tol']
        self.boltaluprof_head_l = d_boltaluprof['head_l']
        # better to make a hole for the washer
        self.washer_aluprof_d = kcomp.D125[boltaluprof_mtr]['do']
        self.washer_aluprof_r_tol = self.washer_aluprof_d/2.+tol

        # calculation of the dimensions:
        self.hold_w = tens_w + 2*wall_thick

        self.hold_d = tens_d_inside + wall_thick
        # base of the tensioner holder
        if min_width == 0:
            self.rim_w = aluprof_w
        else:
            self.rim_w = self.washer_aluprof_d
        self.hold_bas_w = self.hold_w + 2*self.rim_w
        self.hold_bas_d = aluprof_w
        if hold_bas_h == 0:
            self.hold_bas_h = wall_thick
        else:
            self.hold_bas_h = hold_bas_h

        # --- bolt of the tensioner
        self.bolttens_dict = kcomp.D912[bolttens_mtr]
        # the shank radius including tolerance
        self.bolttens_r_tol = self.bolttens_dict['shank_r_tol']



        #  check that the position of the belt is higher than the minimum
        #                            axis_h
        #                           ___:___
        #                          /  ___  \
        #            ..............| |   | |......
        #            :             | |___| |.....:tens_h/2
        # belt_pos_h +             |_______|
        #            :      _______|       |_______.....
        #            :.....(_______|_______|_______)...+hold_bas_h
        #                                                : :          :
        #  
        if belt_pos_h < tens_h/2. + self.hold_bas_h:
            self.belt_pos_h = tens_h/2. + self.hold_bas_h
            msg = 'argument belt_pos_h is smaller than minimum, new value: '
            logger.warning(msg + str(self.belt_pos_h))
        self.hold_h = self.belt_pos_h + tens_h/2. + wall_thick


        # ------ vectors from the different position points
        # d_o[1] is the distance from o to 1
        self.d_o[0] = V0
        self.d_o[1] = self.vec_d(wall_thick)
        self.d_o[2] = self.vec_d(self.hold_bas_d/2.)
        self.d_o[3] = self.vec_d(self.hold_bas_d)
        self.d_o[4] = self.vec_d(self.hold_d)

        self.w_o[0] = V0
        self.w_o[1] = self.vec_w(-self.tens_w/2.)
        self.w_o[2] = self.vec_w(-self.hold_w/2.)
        self.w_o[3] = self.vec_w(-self.hold_w/2. - self.rim_w/2.)
        self.w_o[4] = self.vec_w(-self.hold_w/2. - self.rim_w)

        # h_o[1] is the distance from o to 1
        self.h_o[0] = V0
        self.h_o[1] = self.vec_h(self.hold_bas_h)
        self.h_o[2] = self.vec_h(self.belt_pos_h - tens_h/2.)
        self.h_o[3] = self.vec_h(self.belt_pos_h)
        self.h_o[4] = self.vec_h(self.hold_h)

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()


        # --------------- step 01 --------------------------- 
        #    the base, to attach it to the aluminum profiles
        #    
        #
        #                         axis_h                axis_h
        #                            :                  :
        #              .. ___________:___________       :________
        #  hold_bas_h.+..|___________:___________|      |________|...axis_d
        #
        #                 .... hold_bas_w ........
        #                :                        :
        #                :________________________:......axis_w
        #                |           :            |    :
        #                |           :            |    + hold_bas_d
        #                |___________:____________|....:
        #                            :            :
        #                          axis_d
        shp01 = fcfun.shp_box_dir(box_w = self.hold_bas_w,
                                  box_d = self.hold_bas_d,
                                  box_h = self.hold_bas_h,
                                  fc_axis_h = self.axis_h,
                                  fc_axis_d = self.axis_d,
                                  cw=1, cd=0, ch=0, pos=self.pos_o)
        #    --------------- step 02 --------------------------- 
        #    Fillet the base
        #    The piece will be printed on the h w plane, so this fillet will be 
        #    raising
        #  
        #                          axis_h
        #                             :
        #                f4___________:___________f2
        #                 (_______________________)... axis_w
        #                f3                        f1
        #
        bas_fil_r = self.in_fillet
        if self.hold_bas_h/2. <= self.in_fillet:
            msg1 = 'Radius of holder base fillet is larger than 2 x base height'
            msg2 = ' making fillet smaller: '
            bas_fil_r = self.hold_bas_h /2. - 0.1
            logger.warning(msg1 + msg2 + str(bas_fil_r))
        # fillet along axis_d :
        shp02 = fcfun.shp_filletchamfer_dir (shp=shp01, fc_axis=self.axis_d,
                                             fillet = 1, radius=bas_fil_r)

        #    --------------- step 03 --------------------------- 
        #    The main box
        #                          axis_h              axis_h
        #                             :    rim_w         :
        #                             :    ..+....       :
        #           .............. ___:___:       :      :____________
        #           :             |       |       :      |            |
        #           :             |       |       :      |            |
        #   hold_h +:             |       |       :      |            |
        #           :             |       |       :      |            |     
        #           :      _______|       |_______:      |________    |
        #           :.....(_______|_______|_______)      |________|___|...axis_d
        #                                                :            :
        #                  .... hold_bas_w ........      :.. hold_d...:
        #                 :                        :
        #                 :        .hold_w.        :
        #                 :       :       :        :
        #                 :_______:_______:________:.......axis_w
        #                 |       |       |        |    :
        #                 |       |       |        |    + hold_bas_d
        #                 |_______|       |________|....:
        #                         |       |
        #                         |_______|
        #                             :
        #                             :
        #                           axis_d 

        shp03 = fcfun.shp_box_dir(box_w = self.hold_w,
                                  box_d = self.hold_d,
                                  box_h = self.hold_h,
                                  fc_axis_h = self.axis_h,
                                  fc_axis_d = self.axis_d,
                                  cw=1, cd=0, ch=0, pos=self.pos_o)
        #    --------------- step 04 --------------------------- 
        #    Fillets on top
        #                          axis_h   rim_w
        #                             :    ..+....:
        #           .............  ___4___        : 
        #           :             /       \       :
        #           :             |       |       :
        #   hold_h +:             |       |       :
        #           :             |       |       :
        #           :      _______|       |_______:
        #           :.....(_______|_______|_______).... axis_w
    
        #                 :______-2___0___2________:.......axis_w
        #                 |       |       |        |    :
        #                 |       |       |        |    + hold_bas_d
        #                 |_______|       |________|....:
        #                         |       |
        #                         |_______|

        # fillet along axis_d and the vertex should contain points:
        # d=0, w=(-2,2) , h = 4
        pts_list = [self.get_pos_dwh(0,2,4), self.get_pos_dwh(0,-2,4)]
        shp04 = fcfun.shp_filletchamfer_dirpts (shp=shp03,
                                                fc_axis=self.axis_d,
                                                fc_pts=pts_list,
                                                fillet = 1,
                                                radius=self.in_fillet)



        #    --------------- step 05 --------------------------- 
        #    large chamfer at the bottom
        #                axis_h                 axis_h
        #                  :                      :
        #   Option A    ___:___                   :____________
        #              /       \                  |            |
        #              |       |                  |            |
        #              |_______|                  |            |
        #              |       |                  |           /       
        #       _______|_______|_______           |________ /  
        #      (___________C___________)..axis_w  |________|...C...axis_d

        #  
        #               axis_h                 axis_h
        #                  :                      :
        #   Option B    ___:___                   :____________
        #              /       \                  |            |
        #              |       |                  |            |
        #              |       |                  |            |
        #              |_______|                  |            |      
        #       _______|       |_______           |________   /  
        #      (_______|___4___|_______)..axis_w  |________|/..4...axis_d
        #                                         :            :
        #                                         :............:
        #                                               +  
        #                                             hold_d
        #
        # option B: using more material (probably sturdier)
        #chmf_rad = min(self.hold_d - self.hold_bas_d,
        #               self.hold_h - (self.tens_h + 2*wall_thick))
        # option A: using less material
        chmf_rad = min(self.hold_d-self.hold_bas_d + self.hold_bas_h,
                       self.hold_h - (self.tens_h + 2*wall_thick))
        
        print(chmf_rad)
        # Find a point along the vertex that is going to be chamfered.
        # See drawings: Point C:
        if chmf_rad > 0:
            pt_c = self.get_pos_d(4)
            shp05 = fcfun.shp_filletchamfer_dirpt (shp = shp04,
                                                   fc_axis = self.axis_w,
                                                   fc_pt = pt_c,
                                                   fillet = 0,
                                                   radius = chmf_rad)
        else:
            shp05 = shp04

        #    --------------- step 06 --------------------------- 
        #    Hole for the tensioner
        #                                             axis_h
        #                                                :
        #                                                : tens_d_inside
        #                        axis_h                  :  ....+.....
        #                       ___:___                  :_:__________:
        #                      /  ___  \                 |  ..........|
        #                      | | 3 | | pos_d=1,pos_h=3 | 1          |
        #            ..........| |___| |                 | :..........|
        # tens_pos_h +         |_______|                 |            |      
        #            :  _______|       |_______          |________   /  
        #            :.(_______|_______|_______).axis_w  |________|/....axis_d
        #                                                : :          :
        #                                                :+           :
        #                                                :wall_thick  :
        #                                                :            :
        #                                                :............:
        #                                                      +
        #                                                    hold_l
        #

        # position of point A is pos_tens0
        if self.opt_tens_chmf == 0: # no optional chamfer, only along axis_w
            edge_dir = self.axis_w
        else:
            edge_dir = V0

        pos_06 = self.get_pos_dwh(1,0,3)
   
        shp06 = fcfun.shp_boxdir_fillchmfplane(
                               box_w = self.tens_w,
                               box_d = self.hold_d,
                               box_h = self.tens_h,
                               axis_d = self.axis_d,
                               axis_h = self.axis_h,
                               cd=0, cw=1, ch=1,
                               xtr_nd = tol,  #tolerance inside
                               xtr_w  = tol/2.,  #tolerances on each side
                               xtr_nw = tol/2.,
                               xtr_h  = tol/2.,
                               xtr_nh = tol/2.,
                               fillet = 0, # chamfer
                               radius = 2*self.in_fillet-kcomp.TOL,
                               plane_fill = self.axis_d.negative(),
                               both_planes = 0,
                               edge_dir = edge_dir,
                               pos = pos_06)

        #    --------------- step 07 --------------------------- 
        #    A hole to be able to see inside, could be on one side or both
        #
        #    hold_hole_2sides = 1:
        #              axis_h                   axis_h
        #                :                        :
        #             ___:___                     :____________
        #            /  ___  \                    |  ._______ .|
        #            |:|   |:|                    | :|_______| |
        #            | |___| |                    |  ..........|
        #            |_______|                    |            |      
        #     _______|       |_______             |________   /  
        #    (_______|_______|_______)..>axis_w   |________|/......>axis_d
        #
        #    hold_hole_2sides = 0:
        #              axis_h                   axis_h
        #                :                        :
        #             ___:___                     :____________
        #            /  ___  \                    |  ._______ .|
        #            2:|   | |<-Not a hole here   3 *________| |
        #            | |___| |                    |  ..........|
        #            |_______|                    |            |      
        #     _______|       |_______             |________   /  
        #    (_______|_______|_______)..>axis_w   |________|/......>axis_d
        #           -2 pos_w                pos_d = 1

        if self.hold_hole_2sides == 1:
            hold_hole_w = self.hold_w
        else:
            hold_hole_w = self.wall_thick
        # position of point 7:
        # height of point 7, is the center of the tensioner:
        pos_07 = self.get_pos_dwh(1,-2,3)
        shp07 = fcfun.shp_box_dir_xtr (
                                       box_w = hold_hole_w,
                                       box_d =  self.hold_d
                                              - 2*wall_thick,
                                       box_h = tens_h/2.,
                                       fc_axis_h = self.axis_h,
                                       fc_axis_d = self.axis_d,
                                       fc_axis_w = self.axis_w,
                                       ch = 1, cd = 0, cw = 0,
                                       xtr_w = 1, xtr_nw = 1,
                                       pos=pos_07)
        # chamfer the edges
        shp07 = fcfun.shp_filletchamfer_dir (shp=shp07, fc_axis=self.axis_w,
                                             fillet = 0, radius=tens_h/6)
        # /* --------------- step 08 --------------------------- 
        #    A hole for the leadscrew
        #            axis_h             axis_h
        #              :                  :
        #           ___:___               :____________
        #          /  ___  \              |  ._______ .|
        #          |:| O |:|              |::|_______| |
        #          | |___| |              |  ..........|
        #          |_______|              |            |      
        #   _______|       |_______       |________   /  
        #  (_______|_______|_______)      |________|/......> axis_d
        #
        pos_08 = self.get_pos_h(3)
        shp08 = fcfun.shp_cylcenxtr (r = self.bolttens_r_tol,
                                     h = wall_thick,
                                     normal = self.axis_d,
                                     ch = 0, xtr_top=1, xtr_bot=1,
                                     pos = pos_08)

        #    --------------- step 09 --------------------------- 
        #    09a: Fuse all the elements to cut
        #    09b: Cut the box with the elements to cut
        #    09c: Fuse the base with the holder
        #    09d: chamfer the union
        #            axis_h           axis_h
        #              :               :
        #           ___:___            :____________
        #          /  ___  \           |  ._______ .|
        #          |:| O |:|           |::|_______| |...
        #         /| |___| |\          |  ..........|...belt_h/2 -tensnut_ap_tol
        #        / |_______| \         |            |  :+tens_pos_h
        #   ____/__A       B__\____    A________   /   :  ...
        #  (_______|_______|_______)   |________|/.....:.....hold_bas_h
        #
        shp09a = fcfun.fuseshplist([shp06, shp07, shp08])
        shp09b = shp05.cut(shp09a)
        shp09c = shp09b.fuse(shp02) # fuse with the base
        shp09c = shp09c.removeSplitter() # refine shape

        # chamfer the union, points A and B:
        # Radius of chamfer
        chmf_rad = min(self.rim_w/2, self.belt_pos_h - tens_h/2.)
        # add the points A,B to the list to have the edges chamfered
        pts = [self.get_pos_dwh(0,2,1), self.get_pos_dwh(0,-2,1)]
        shp09d = fcfun.shp_filletchamfer_dirpts (shp=shp09c,
                                                 fc_axis=self.axis_d,
                                                 fc_pts=pts,
                                                 fillet = 0,
                                                 radius=chmf_rad)
        shp09d = shp09d.removeSplitter() # refine shape


        #    --------------- step 10 --------------------------- 
        #    Bolt holes to attach the piece to the aluminum profile
        #                                
        #             axis_h            axis_h
        #            ___:___              :____________
        #           /  ___  \             |  ._______ .|
        #           |:| O |:|             |::|_______| |
        #          /| |___| |\            |  ..........|
        #         / |_______| \           |            |
        #    ____/__|       |__\____      |________   /
        #   (__::___|_______|___::__)     |___::___|/....axis_d
        #      -3   pos_w        3      pos_d 2

        #             hold_w   aluprof_w
        #            ...+... ...+...
        #    _______:_______:_______:.......axis_w
        #   |       |       |       |    :
        #   |   A   |       |   B   |    + hold_bas_d
        #   |_______|       |_______|....:
        #           |       |   :
        #           |_______|   :
        #               :       :
        #               :.......:
        #                   +
        #               (hold_w+aluprof_w)/2

        shp_bolt_list = []
        for w_i in [-3,3]:
            # points A and B
            pt_i = self.get_pos_dwh(2,w_i,0)
            shp_i = fcfun.shp_bolt_dir(
                       r_shank = self.boltaluprof_r_tol,
                       l_bolt = self.hold_bas_h +2*self.boltaluprof_head_r_tol,
                       r_head = self.washer_aluprof_r_tol,
                       # extra head, just in case
                       l_head = 2*self.boltaluprof_head_l,
                       xtr_head = 1, xtr_shank = 1,
                       support = 0,
                       fc_normal = self.axis_h.negative(),
                       pos_n = 2, #at the end of the shank
                       pos = pt_i)
            shp_bolt_list.append(shp_i)
        shp10_bolts = fcfun.fuseshplist(shp_bolt_list)
        shp10_final = shp09d.cut(shp10_bolts)
        shp10_final = shp10_final.removeSplitter()

        self.shp = shp10_final
 
        #Part.show(shp10_final)

#doc = FreeCAD.newDocument()
#shp_hold = ShpTensionerHolder(
#                              aluprof_w = 15,
#                              belt_pos_h = 22.,
#                              tens_h = 10.,
#                              tens_w = 10.,
#                              tens_d_inside = 25.,
#                              wall_thick = 3.,
#                              in_fillet = 2.,
#                              boltaluprof_mtr = 3,
#                              bolttens_mtr = 3,
#                              hold_bas_h = 0,
#                              opt_tens_chmf = 1,
#                              hold_hole_2sides = 1,
#                              tol = kcomp.TOL,
#                              axis_d = VX,
#                              axis_w = VY,
#                              axis_h = VZ,
#                              pos_d = 0,
#                              pos_w = 0,
#                              pos_h = 0,
#                              pos = V0)

class PartTensionerHolder (fc_clss.SinglePart, ShpTensionerHolder):
    """ Integration of a ShpTensionerHolder object into a PartTensionerHolder
    object, so it is a FreeCAD object that can be visualized in FreeCAD
    """
    def __init__(self,
                 aluprof_w,
                 belt_pos_h,
                 tens_h,
                 tens_w,
                 tens_d_inside,
                 wall_thick = 3.,
                 in_fillet = 1.,
                 boltaluprof_mtr = 3,
                 bolttens_mtr = 3,
                 hold_bas_h = 0,
                 opt_tens_chmf = 1,
                 hold_hole_2sides = 1,
                 min_width = 0,
                 tol = kcomp.TOL,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0,
                 model_type = 0, #exact
                 name = ''):

        default_name = 'tensioner_holder'
        self.set_name (name, default_name, change = 0)
        # First the shape is created
        ShpTensionerHolder.__init__(self,
                               aluprof_w = aluprof_w,
                               belt_pos_h = belt_pos_h,
                               tens_h = tens_h,
                               tens_w = tens_w,
                               tens_d_inside = tens_d_inside,
                               wall_thick = wall_thick,
                               in_fillet = in_fillet,
                               boltaluprof_mtr = boltaluprof_mtr,
                               bolttens_mtr = bolttens_mtr,
                               hold_bas_h = hold_bas_h,
                               opt_tens_chmf = opt_tens_chmf,
                               hold_hole_2sides = hold_hole_2sides,
                               min_width = min_width,
                               #tol = tol,
                               tol = 3.5*tol, #extra tol needed
                               axis_d = axis_d,
                               axis_w = axis_w,
                               axis_h = axis_h,
                               pos_d = pos_d,
                               pos_w = pos_w,
                               pos_h = pos_h,
                               pos = pos)
        fc_clss.SinglePart.__init__(self)


#doc = FreeCAD.newDocument()
#holder = PartTensionerHolder(
#                              aluprof_w = 15,
#                              belt_pos_h = 22.,
#                              tens_h = 10.,
#                              tens_w = 10.,
#                              tens_d_inside = 25.,
#                              wall_thick = 3.,
#                              in_fillet = 2.,
#                              boltaluprof_mtr = 3,
#                              bolttens_mtr = 3,
#                              hold_bas_h = 0,
#                              opt_tens_chmf = 1,
#                              hold_hole_2sides = 1,
#                              tol = kcomp.TOL,
#                              axis_d = VX,
#                              axis_w = VY,
#                              axis_h = VZ,
#                              pos_d = 0,
#                              pos_w = 0,
#                              pos_h = 0,
#                              pos = V0,
#                              name = 'tensioner_holder')


class TensionerSet (fc_clss.PartsSet):
    """ Set composed of the idler pulley and the tensioner

                              axis_h            axis_h 
                               :                  :
                            ___:___               :______________
                           |  ___  |              |  __________  |---
                           | |   | |              | |__________| | : |
    .---- belt_pos_h------/| |___| |\             |________      |---
    :                    / |_______| \            |        |    /      
    :             . ____/  |       |  \____       |________|  /
    :..hold_bas_h:.|_::____|_______|____::_|      |___::___|/......>axis_d
   
                                wall_thick
                                  +
                                 : :         
                    _____________:_:________.........>axis_w
                   |    |  | :   : |  |     |    :
                   |  O |  | :   : |  |  O  |    + aluprof_w
                   |____|__| :   : |__|_____|....:
                           | :   : |
                           |_:___:_|
                             |   |
                              \_/
                               :
                               :
                             axis_d

                             axis_h            axis_h 
                               :         pos_h    :
    ....................... ___:___         4     :______________
    :                      |  ___  |              |  __________  |---
    :                      | |   | |        3     | |__________| | : |
    :+hold_h              /| |___| |\       2     |________      |---
    :                    / |_______| \            |        |    /      
    :             . ____/  |       |  \____ 1     |________|  /
    :..hold_bas_h:.|_::____|___o___|____::_|0     o___::___|/......>axis_d
                                                  01   2   3     4 5 6: pos_d
 
                                      having the tensioner extended:    7  8
                                                    _____________       :  :
                                                                 |---------
                                                                 |      :  |
                                                                 |---------
   
   
                    .... hold_bas_w ........
                   :        .hold_w.        :
                   :       :    wall_thick  :
                   :       :      +         :
                   :       :     : :        :
          pos_w:   4__3____2_1_0_:_:________:........>axis_w
                   |    |  | :   : |  |     |    :
                   |  O |  | :   : |  |  O  |    + hold_bas_l
                   |____|__| :   : |__|_____|....:
                           | :   : |
                           |_:___:_|
                             |   |
                              \_/
                               :
                               :
                             axis_d

        pos_o (origin) is at pos_d=0, pos_w=0, pos_h=0, It marked with o

    Parameters
    ----------
    aluprof_w : float
        Width of the aluminum profile
    belt_pos_h : float
        The position along axis_h where the idler pulley that conveys the belt
        starts. THIS POSITION IS CENTERED at the ilder pulley
    tens_h : float
        height of the ilder tensioner
    tens_w : float
        width of the ilder tensioner
    tens_d_inside : float
        Max length (depth) of the ilder tensioner that is inside the holder
    wall_thick : float
        Thickness of the walls
    in_fillet: float
        radius of the inner fillets
    boltaluprof_mtr : float
        diameter (metric) of the bolt that attachs the tensioner holder to the
        aluminum profile (or whatever is attached to)
    bolttens_mtr : float
        diameter (metric) of the bolt for the tensioner
    hold_bas_h : float
        height of the base of the tensioner holder
        if 0, it will take wall_thick
    opt_tens_chmf : int
        1: there is a chamfer at every edge of tensioner, inside the holder
        0: there is a chamfer only at the edges along axis_w, not along axis_h
    hold_hole_2sides : int
        In the tensioner holder there is a hole to see inside, it can be at
        each side of the holder or just on one side
        0: only at one side
        1: at both sides
    min_width: make the rim the minimum: the diameter of the washer
        0: normal width: the width of the aluminum profile
        1: minimum width: diameter of the washer
    tol : float
        Tolerances to print
    axis_d : FreeCAD.Vector
        depth vector of coordinate system
    axis_w : FreeCAD.Vector
        width vector of coordinate system
        if V0: it will be calculated using the cross product: axis_l x axis_h
    axis_h : FreeCAD.Vector
        height vector of coordinate system
    pos_d : int
        location of pos along the axis_d
        0: at the back of the holder
        1: at the place where the tensioner can reach all the way inside
        2: at the center of the base along axis_d, where the bolts to attach
           the holder base to the aluminum profile
        3: at the end of the base
        4: at the end of the holder
        5: at the center of the pulley
        6: at the end of the idler tensioner
        7: at the center of the pulley, when idler is all the way out
        8: at the end of the idler tensioner, whenit is all the way out
    pos_w : int
        location of pos along the axis_w
        0: at the center of symmetry
        1: at the inner walls of the holder, which is the pulley radius
        2: at the end of the holder (the top part, where the base starts)
        3: at the center of the bolt holes to attach the holder base to the
           aluminum profile
        4: at the end of the piece along axis_w
              axes have direction. So if pos_w == 3, the piece will be drawn
              along the positive side of axis_w
    pos_h : int
        location of pos along the axis_h (0,1,2,3,4)
        0: at the bottom of the holder
        1: at the top of the base of the holder (for the bolts)
        2: at the bottom of the hole where the idler tensioner goes
        3: at the middle point of the hole where the idler tensioner goes
        4: at the top of the holder
    pos : FreeCAD.Vector
        position of the piece

    Paramenters for the set

    tens_in_ratio : float
        from 0 to 1, the ratio of the stroke that the tensioner is inside.
        if 1: it is all the way inside
        if 0: it is all the way outside (all the tens_stroke)





    Attributes:
    -----------
    All the parameters and attributes of father class SinglePart

    prnt_ax : FreeCAD.Vector
        Best axis to print (normal direction, pointing upwards)
    d0_cen : int
    w0_cen : int
    h0_cen : int
        indicates if pos_h = 0 (pos_d, pos_w) is at the center along
        axis_h, axis_d, axis_w, or if it is at the end.
        1 : at the center (symmetrical, or almost symmetrical)
        0 : at the end
    tot_d : float
        total depth, including the idler tensioner
    tot_d_extend : float
        total depth including the idler tensioner, having it extended


    Parameters:
    """

    def __init__(self,
                 aluprof_w = 20.,
                 belt_pos_h = 20., 
                 hold_bas_h = 0,
                 hold_hole_2sides = 0,
                 boltidler_mtr = 3,
                 bolttens_mtr = 3,
                 boltaluprof_mtr = 3,
                 tens_stroke = 20. ,
                 wall_thick = 3.,
                 in_fillet = 2.,
                 pulley_stroke_dist = 0,
                 nut_holder_thick = 4. ,
                 opt_tens_chmf = 1,
                 min_width = 0,
                 tol = kcomp.TOL,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0,
                 group = 0,
                 name = ''):

        default_name = 'tensioner_set'
        self.set_name (name, default_name, change = 0)

        fc_clss.PartsSet.__init__(self, axis_d = axis_d,
                                  axis_w = axis_w, axis_h = axis_h)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])

        # pos_w = 0 is at the center, not pos_d, pos_h
        self.d0_cen = 0
        self.w0_cen = 1
        self.h0_cen = 0

        # Creation of the idler pulley set, we cannot know the relative 
        # position from pos, so we put it at pos_d,w,h = 0

        idler_tensioner = IdlerTensionerSet(
                                 boltidler_mtr = boltidler_mtr,
                                 bolttens_mtr  = bolttens_mtr,
                                 tens_stroke = tens_stroke,
                                 wall_thick = wall_thick,
                                 in_fillet = in_fillet,
                                 pulley_stroke_dist = pulley_stroke_dist,
                                 nut_holder_thick = nut_holder_thick ,
                                 opt_tens_chmf = opt_tens_chmf,
                                 tol = tol,
                                 axis_d = self.axis_d,
                                 axis_w = self.axis_w,
                                 axis_h = self.axis_h,
                                 pos_d = 0,
                                 pos_w = 0,
                                 pos_h = 0,
                                 pos = pos)

        self.append_part(idler_tensioner)
        idler_tensioner.parent = self

        # creation of the holder
        tensioner_holder = PartTensionerHolder(
                               aluprof_w = aluprof_w,
                               belt_pos_h = belt_pos_h,
                               tens_h = idler_tensioner.tens_h,
                               tens_w = idler_tensioner.tens_w,
                               tens_d_inside = idler_tensioner.tens_d_inside,
                               wall_thick = wall_thick,
                               in_fillet = in_fillet,
                               boltaluprof_mtr = boltaluprof_mtr,
                               bolttens_mtr = bolttens_mtr,
                               hold_bas_h = hold_bas_h,
                               opt_tens_chmf = opt_tens_chmf,
                               hold_hole_2sides = hold_hole_2sides,
                               min_width = min_width,
                               tol = tol,
                               axis_d = self.axis_d,
                               axis_w = self.axis_w,
                               axis_h = self.axis_h,
                               pos_d = 0,
                               pos_w = 0,
                               pos_h = 0,
                               pos = pos,
                               model_type = 0) #exact

        self.append_part(tensioner_holder)
        idler_tensioner.parent = self

        self.d_o[0] = V0
        self.d_o[1] = tensioner_holder.d_o[1]
        self.d_o[2] = tensioner_holder.d_o[2]
        self.d_o[3] = tensioner_holder.d_o[3]
        self.d_o[4] = tensioner_holder.d_o[4]
        self.d_o[5] = self.d_o[1] + idler_tensioner.d_o[5]
        self.d_o[6] = self.d_o[1] + idler_tensioner.d_o[6]
        self.d_o[7] = self.d_o[5] + self.vec_d(tens_stroke)
        self.d_o[8] = self.d_o[6] + self.vec_d(tens_stroke)

        self.tot_d = self.d_o[6].Length
        self.tot_d_extend = self.d_o[8].Length

        # these are the same
        for i in tensioner_holder.w_o:
            self.w_o[i] = tensioner_holder.w_o[i]
        for i in tensioner_holder.h_o:
            self.h_o[i] = tensioner_holder.h_o[i]
                                   

        # Now we place the idler tensioner according to pos_d,w,h
        # argument 1 means that pos_o wasnt in place and has to be
        # adjusted
        self.set_pos_o(adjust = 1)

        # Now we have the position where the origin is, but:
        # - we havent located the idler_tensioner at pos_o
        # - we havent located the pulley at pos_o + dist to axis

        # we should have call PartIdlerTensioner (pos = self.pos_o)
        # instead, we have it at (pos = self.pos)
        # so we have to move PartIdlerTensioner self.pos_o - self.pos
        self.set_part_place(tensioner_holder)

        self.set_part_place(idler_tensioner,   self.get_o_to_d(1)
                                             + self.get_o_to_h(3))

        # bolt and washer for the leadscrew
        bolt_length_list = kcomp.D912_L[bolttens_mtr]

        max_tens_bolt_l =  (  idler_tensioner.tens_stroke
                            + idler_tensioner.nut_holder_tot
                            + tensioner_holder.wall_thick)
        print('max tens:' + str(max_tens_bolt_l))
        tens_bolt = partset.Din912BoltWashSet(
                                         metric  = bolttens_mtr,
                                         shank_l = max_tens_bolt_l,
                                         # smaller considering the washer
                                         shank_l_adjust = -2,
                                         axis_h  = self.axis_d,
                                         pos_h   = 3,
                                         pos_d   = 0,
                                         pos_w   = 0,
                                         pos     = self.get_pos_dwh(0,0,3))
        self.append_part(tens_bolt)
        tens_bolt.parent = self


        self.place_fcos()
        if group == 1:
            self.make_group()

    def get_tensioner_holder(self):
        """ gets the tensioner holder"""
        part_list = self.get_parts()
        for part_i in part_list:
            if isinstance(part_i, PartTensionerHolder):
                return part_i


    def get_idler_tensioner(self):
        """ gets the idler tensioner set"""
        part_list = self.get_parts()
        for part_i in part_list:
            if isinstance(part_i, IdlerTensionerSet):
                return part_i

    def set_pos_tensioner (self, new_tens_out_ratio = None):
        """ Sets the tensioner place, depending on the attributes tens_in_ratio
        and tens_stroke
        Parameters:
        -----------
        new_tens_out_ratio : float [0,1]
            ratio of the tensioner that is outside.
            It can be any value from 0 to 1
            0: all the way inside
            1: maximum value outside (tens_stroke)
        """
        if new_tens_out_ratio is not None:
            # set the new tens_in_ratio
            self.tens_out_ratio = new_tens_out_ratio
        self.tens_out = self.tens_out_ratio * self.tens_stroke
        idler_tensioner = self.get_idler_tensioner()
        idler_tensioner.extra_mov = idler_tensioner.vec_d(self.tens_out)
        self.place_fcos()


"""

doc = FreeCAD.newDocument()
t_set1 = TensionerSet(
                     aluprof_w = 20.,
                     #belt_pos_h = 32.5, #bottom of belt:30 + 2.5 to center
                     #belt_pos_h = 37.5, #bottom of belt:35 + 2.5 to center
                     #belt_pos_h = 47.5, #bottom of belt:45 + 2.5 to center
                     belt_pos_h = 20., # to center of belt
                     hold_bas_h = 0,
                     hold_hole_2sides = 1,
                     boltidler_mtr = 3,
                     bolttens_mtr = 3,
                     boltaluprof_mtr = 3,
                     tens_stroke = 12. ,
                     wall_thick = 3.,
                     in_fillet = 2.,
                     pulley_stroke_dist = 0,
                     nut_holder_thick = 3. ,
                     opt_tens_chmf = 0,
                     min_width = 0,
                     tol = kcomp.TOL,
                     axis_d = VX,
                     axis_w = VYN,
                     axis_h = VZ,
                     pos_d = 0,
                     pos_w = 0,
                     pos_h = 0,
                     #pos = FreeCAD.Vector(1,0,10),
                     pos = FreeCAD.Vector(0,0,0),
                     name = 'tensioner_set')

# get the set, and the the part
t_set1.get_idler_tensioner().get_idler_tensioner().set_color(fcfun.ORANGE)
t_set1.get_tensioner_holder().set_color(fcfun.LSKYBLUE)


t_set2 = TensionerSet(
                     aluprof_w = 20.,
                     #belt_pos_h = 32.5, #bottom of belt:30 + 2.5 to center
                     #belt_pos_h = 37.5, #bottom of belt:35 + 2.5 to center
                     #belt_pos_h = 47.5, #bottom of belt:45 + 2.5 to center
                     belt_pos_h = 20., # to center of belt
                     hold_bas_h = 0,
                     hold_hole_2sides = 1,
                     boltidler_mtr = 3,
                     bolttens_mtr = 3,
                     boltaluprof_mtr = 3,
                     tens_stroke = 12. ,
                     wall_thick = 3.,
                     in_fillet = 2.,
                     pulley_stroke_dist = 0,
                     nut_holder_thick = 3. ,
                     opt_tens_chmf = 0,
                     min_width = 0,
                     tol = kcomp.TOL,
                     axis_d = VX,
                     axis_w = VYN,
                     axis_h = VZ,
                     pos_d = 0,
                     pos_w = 0,
                     pos_h = 0,
                     pos = FreeCAD.Vector(
                           t_set1.get_tensioner_holder().hold_bas_w,0,0),
                     name = 'tensioner_set_extend')

# get the set, and the the part
t_set2.get_idler_tensioner().get_idler_tensioner().set_color(fcfun.ORANGE)
t_set2.get_tensioner_holder().set_color(fcfun.LSKYBLUE)
t_set2.set_pos_tensioner(1)


# --------- 


doc = FreeCAD.newDocument()
t_set1 = TensionerSet(
                     aluprof_w = 20.,
                     #belt_pos_h = 32.5, #bottom of belt:30 + 2.5 to center
                     #belt_pos_h = 37.5, #bottom of belt:35 + 2.5 to center
                     #belt_pos_h = 47.5, #bottom of belt:45 + 2.5 to center
                     belt_pos_h = 45., # to center of belt
                     hold_bas_h = 0,
                     hold_hole_2sides = 1,
                     boltidler_mtr = 3,
                     bolttens_mtr = 3,
                     boltaluprof_mtr = 3,
                     tens_stroke = 12. ,
                     wall_thick = 3.,
                     in_fillet = 2.,
                     pulley_stroke_dist = 0,
                     nut_holder_thick = 3. ,
                     opt_tens_chmf = 0,
                     min_width = 0,
                     tol = kcomp.TOL,
                     axis_d = VX,
                     axis_w = VYN,
                     axis_h = VZ,
                     pos_d = 0,
                     pos_w = 0,
                     pos_h = 0,
                     #pos = FreeCAD.Vector(1,0,10),
                     pos = FreeCAD.Vector(0,0,0),
                     name = 'tensioner_set')

# get the set, and the the part
t_set1.get_idler_tensioner().get_idler_tensioner().set_color(fcfun.ORANGE)
t_set1.get_tensioner_holder().set_color(fcfun.LSKYBLUE)


t_set2 = TensionerSet(
                     aluprof_w = 20.,
                     #belt_pos_h = 32.5, #bottom of belt:30 + 2.5 to center
                     #belt_pos_h = 37.5, #bottom of belt:35 + 2.5 to center
                     #belt_pos_h = 47.5, #bottom of belt:45 + 2.5 to center
                     belt_pos_h = 25., # to center of belt
                     hold_bas_h = 0,
                     hold_hole_2sides = 1,
                     boltidler_mtr = 3,
                     bolttens_mtr = 3,
                     boltaluprof_mtr = 3,
                     tens_stroke = 12. ,
                     wall_thick = 3.,
                     in_fillet = 2.,
                     pulley_stroke_dist = 0,
                     nut_holder_thick = 3. ,
                     opt_tens_chmf = 0,
                     min_width = 0,
                     tol = kcomp.TOL,
                     axis_d = VX,
                     axis_w = VYN,
                     axis_h = VZ,
                     pos_d = 0,
                     pos_w = 0,
                     pos_h = 0,
                     pos = FreeCAD.Vector(
                           55,0,0),
                     name = 'tensioner_set_extend')

# get the set, and the the part
t_set2.get_idler_tensioner().get_idler_tensioner().set_color(fcfun.ORANGE)
t_set2.get_tensioner_holder().set_color(fcfun.LSKYBLUE)
# all the way extended
#t_set2.set_pos_tensioner(1)



t_set3 = TensionerSet(
                     aluprof_w = 20.,
                     #belt_pos_h = 32.5, #bottom of belt:30 + 2.5 to center
                     #belt_pos_h = 37.5, #bottom of belt:35 + 2.5 to center
                     #belt_pos_h = 47.5, #bottom of belt:45 + 2.5 to center
                     belt_pos_h = 5., # to center of belt
                     hold_bas_h = 0,
                     hold_hole_2sides = 1,
                     boltidler_mtr = 3,
                     bolttens_mtr = 3,
                     boltaluprof_mtr = 3,
                     tens_stroke = 12. ,
                     wall_thick = 3.,
                     in_fillet = 2.,
                     pulley_stroke_dist = 0,
                     nut_holder_thick = 3. ,
                     opt_tens_chmf = 0,
                     min_width = 0,
                     tol = kcomp.TOL,
                     axis_d = VX,
                     axis_w = VYN,
                     axis_h = VZ,
                     pos_d = 0,
                     pos_w = 0,
                     pos_h = 0,
                     pos = FreeCAD.Vector(
                           100,0,0),
                     name = 'tensioner_set_extend')

# get the set, and the the part
t_set3.get_idler_tensioner().get_idler_tensioner().set_color(fcfun.ORANGE)
t_set3.get_tensioner_holder().set_color(fcfun.LSKYBLUE)
# all the way extended
#t_set3.set_pos_tensioner(1)

"""

#t_set30 = TensionerSet(
#                     aluprof_w = 30.,
#                     #belt_pos_h = 32.5, #bottom of belt:30 + 2.5 to center
#                     #belt_pos_h = 37.5, #bottom of belt:35 + 2.5 to center
#                     #belt_pos_h = 47.5, #bottom of belt:45 + 2.5 to center
#                     belt_pos_h = 33.5,
#                     hold_bas_h = 8,
#                     hold_hole_2sides = 1,
#                     boltidler_mtr = 4,
#                     bolttens_mtr = 4,
#                     boltaluprof_mtr = 4,
#                     tens_stroke = 20. ,
#                     wall_thick = 5.,
#                     in_fillet = 2.,
#                     pulley_stroke_dist = 0,
#                     nut_holder_thick = 4. ,
#                     opt_tens_chmf = 1,
#                     min_width = 0,
#                     tol = kcomp.TOL,
#                     axis_d = VX,
#                     axis_w = VYN,
#                     axis_h = VZ,
#                     pos_d = 0,
#                     pos_w = 0,
#                     pos_h = 0,
#                     #pos = FreeCAD.Vector(1,0,10),
#                     pos = FreeCAD.Vector(-80,0,0),
#                     name = 'tensioner_set')
#
## get the set, and the the part
#t_set30.get_idler_tensioner().get_idler_tensioner().set_color(fcfun.ORANGE)
#t_set30.get_tensioner_holder().set_color(fcfun.LSKYBLUE)



