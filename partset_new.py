import FreeCAD
import Part
import DraftVecUtils
import inspect
import logging
import math

import fcfun
import kcomp
import NuevaClase
from NuevaClase import Obj3D

from fcfun import V0, VX, VY, VZ

logging.basicConfig(level=logging.DEBUG,
                    format='%(%(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


class PartNemaMotor (Obj3D):
    """ Creates a shape of a Nema Motor
    It can be a shape to cut the piece where it may be embedded
    ::

               axis_h
                  :
                  :
                  2 ............................
                 | |                           :
                 | |                           + shaft_l
              ___|1|___.............           :
        _____|____0____|_____......:..circle_h.:
       | ::       3       :: |     : .. h=3 bolt_depth
       |                     |     :
       |                     |     :
       |                     |     + base_l
       |                     |     :
       |                     |     :
       |                     |     :
       |__________4__________|.....:
                 : :               :
                 : :               :
                 : :               :+ rear_shaft_l (optional)
                 : :               :
                 :01...2..3..4.....:...........axis_d (same as axis_w)
           axis_h:5 


                axis_w
                  :
                  :
        __________:__________.....
       /                     \....: chmf_r
       |  O               O  |
       |          _          |
       |        .   .        |
       |      (  ( )  )      |........axis_d
       |        .   .        |
       |          -          |
       |  O               O  |
       \_____________________/
       :                     :
       :.....................:
                  +
               motor_w (same as d): Nema size in inches /10


     pos_o (origin) is at pos_h=0, pos_d=pos_w=0

    Parameters:
    -----------
    nema_size : int
        Nema size of the motor. Nema 17 means that the front is 1.7 inches
        each side (it is a square)
    base_l : float,
        Length (height) of the base
    shaft_l = float,
        Length (height) of the shaft, including the small cylinder (circle)
        at the base
    shaft_r = float,
        Radius of the shaft, if not defined, it will take the dimension defined
        in kcomp
    circle_r : float,
        Radius of the cylinder (circle) at the base of the shaft
        if 0 or circle_h = 0 -> no cylinder
    circle_h : float,
        Height of the cylinder at the base of the shaft
        if 0 or circle_r = 0 -> no cylinder
    chmf_r : float, 
        Chamfer radius of the chamfer along the base length (height)
    rear_shaft_l : float,
        Length of the rear shaft, 0 : no rear shaft
    bolt_depth : 3.,
        Depth of the bolt holes of the motor
    bolt_out : 0,
        Length of the bolts to be outside (to make holes), in case of a shape
        to cut
    cut_extra : 0,
        In case that the shape is to make a hole for the motor, it will have
        an extra size to make it fit. If 0, no extra size
    axis_d : FreeCAD.Vector
        Depth vector of coordinate system
    axis_w : FreeCAD.Vector
        Width vector of coordinate system
    axis_h : FreeCAD.Vector
        Height vector of coordinate system
    pos_d : int
        Location of pos along the axis_d (0,1,2,3,4), see drawing
            * 0: at the axis of the shaft
            * 1: at the radius of the shaft
            * 2: at the end of the circle(cylinder) at the base of the shaft
            * 3: at the bolts
            * 4: at the end of the piece

    pos_w : int
        Same as pos_d
    pos_h : int
        Location of pos along the axis_h (0,1,2,3,4,5), see drawing
            * 0: at the base of the shaft (not including the circle at the base
               of the shaft)
            * 1: at the end of the circle at the base of the shaft
            * 2: at the end of the shaft
            * 3: at the end of the bolt holes
            * 4: at the bottom base
            * 5: at the end of the rear shaft, if no rear shaft, it will be
               the same as pos_h = 4

    pos : FreeCAD.Vector
        Position of the motor, at the point defined by pos_d, pos_w, pos_h

    Attributes:
    ----------
    """

    def __init__( self,
                  nema_size = 17,
                  base_l = 32.,
                  shaft_l = 20.,
                  shaft_r = 0,
                  circle_r = 11.,
                  circle_h = 2.,
                  chmf_r = 1, 
                  rear_shaft_l=0,
                  bolt_depth = 3.,
                  bolt_out = 2.,
                  cut_extra = 0,
                  axis_d = VX,
                  axis_w = None,
                  axis_h = VZ,
                  pos_d = 0,
                  pos_w = 0,
                  pos_h = 0,
                  pos = V0,
                  name = None):

        if name == None:
            name = 'nema' + str(nema_size) + '_motor_l' + str(int(base_l))
        self.name = name

        if (axis_w is None) or (axis_w == V0):
            axis_w = axis_h.cross(axis_d)

        Obj3D.__init__(self, axis_d, axis_w, axis_h, name)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])


        self.motor_w = kcomp.NEMA_W[nema_size]
        if shaft_r == 0:
            self.shaft_d  = kcomp.NEMA_SHAFT_D[nema_size]
            self.shaft_r  = self.shaft_d /2.
            shaft_r  = self.shaft_r

        self.shaft_l = shaft_l
        self.base_l = base_l
        self.rear_shaft_l = rear_shaft_l

        self.nemabolt_sep = kcomp.NEMA_BOLT_SEP[nema_size]

        nemabolt_d = kcomp.NEMA_BOLT_D[nema_size]
        self.nemabolt_d = nemabolt_d
        self.nemabolt_r = nemabolt_d/2.
        mtol = kcomp.TOL - 0.1

        if circle_r == 0 or circle_h == 0:
            # No circle
            circle_r = 0
            circle_h = 0
            self.circle_r = 0
            self.circle_h = 0

        self.h0_cen = 0
        self.d0_cen = 1 # symmetrical
        self.w0_cen = 1 # symmetrical

        # vectors from the origin to the points along axis_h:
        self.h_o[0] = V0 # base of the shaft: origin
        self.h_o[1] = self.vec_h(self.circle_h)
        self.h_o[2] = self.vec_h(self.shaft_l) #includes circle_h
        self.h_o[3] = self.vec_h(-bolt_depth)
        self.h_o[4] = self.vec_h(-self.base_l)
        self.h_o[5] = self.vec_h(-self.base_l -self.rear_shaft_l)

        # vectors from the origin to the points along axis_d:
        # these are negative because actually the pos_d indicates a negative
        # position along axis_d (this happens when it is symmetrical)
        self.d_o[0] = V0
        self.d_o[1] = self.vec_d(-self.shaft_r)
        self.d_o[2] = self.vec_d(-self.circle_r)
        self.d_o[3] = self.vec_d(-self.nemabolt_sep/2.)
        self.d_o[4] = self.vec_d(-self.motor_w/2.)

        # position along axis_w (similar to axis_d)
        self.w_o[0] = V0
        self.w_o[1] = self.vec_w(-self.shaft_r)
        self.w_o[2] = self.vec_w(-self.circle_r)
        self.w_o[3] = self.vec_w(-self.nemabolt_sep/2.)
        self.w_o[4] = self.vec_w(-self.motor_w/2.)

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        # ---------- building of the piece ------------------

        # -------- base of the motor
        # if cut_extra, there will be extra at each side, since the piece
        # is built from the center of symmetry, it will be equally extended
        # on each side
        shp_base = fcfun.shp_box_dir(box_w = self.motor_w + 2*cut_extra,
                                     box_d = self.motor_w + 2*cut_extra,
                                     box_h = self.base_l,
                                     fc_axis_w = self.axis_w,
                                     fc_axis_d = self.axis_d,
                                     fc_axis_h = self.axis_h,
                                     cw = 1, cd = 1, ch = 0,
                                     pos = self.get_pos_h(4))

        shp_base = fcfun.shp_filletchamfer_dir (shp_base, self.axis_h,
                                                fillet = 0, radius = chmf_r)
        shp_base = shp_base.removeSplitter()

        fuse_list = []
        holes_list = []

        # --------- bolts (holes or extensions if cut_extra > 0)
        for pt_d in (-3,3):
            for pt_w in (-3,3):
                if cut_extra == 0: # there will be holes for the bolts
                    # pos_h=3 is at the end of the hole for the bolts
                    bolt_pos = self.get_pos_dwh(pt_d,pt_w,3)
                    shp_hole = fcfun.shp_cylcenxtr (r = self.nemabolt_r,
                                                    h = bolt_depth,
                                                    normal = self.axis_h,
                                                    ch = 0,
                                                    xtr_top = 1,
                                                    xtr_bot = 0,
                                                    pos = bolt_pos)
                    holes_list.append(shp_hole)
                else: # the bolts will protude to make holes in the shape to cut
                    # pos_h=0 is at the the base of the shaft
                    bolt_pos = self.get_pos_dwh(pt_d,pt_w,0)
                    shp_hole = fcfun.shp_cylcenxtr (r = self.nemabolt_r,
                                                    h = bolt_out,
                                                    normal = self.axis_h,
                                                    ch = 0,
                                                    xtr_top = 0,
                                                    xtr_bot = 1,
                                                    pos = bolt_pos)
                    fuse_list.append(shp_hole)

        if cut_extra == 0:
            shp_holes = fcfun.fuseshplist(holes_list)
            shp_base = shp_base.cut(shp_holes)
            shp_base = shp_base.removeSplitter()


        # -------- circle (flat cylinder) at the base of the shaft
        # could add cut_extra to circle_h or circle_r, but it can be 
        # set in the arguments
        if circle_r > 0 and circle_h > 0:
            shp_circle = fcfun.shp_cylcenxtr(r = circle_r,
                                             h = circle_h,
                                             normal = self.axis_h,
                                             ch = 0, # not centered
                                             xtr_top = 0, # no extra at top
                                             xtr_bot = 1, # extra to fuse
                                             pos = self.pos_o)
            fuse_list.append(shp_circle)

        # ------- Shaft
        shp_shaft = fcfun.shp_cylcenxtr(r = self.shaft_r,
                                        h = self.shaft_l,
                                        normal = self.axis_h,
                                        ch = 0, # not centered
                                        xtr_top = 0, # no extra at top
                                        xtr_bot = 1, # extra to fuse
                                        # shaft length stats from the base
                                        # not from the circle
                                        pos = self.pos_o)
        fuse_list.append(shp_shaft)

        if rear_shaft_l > 0:
            shp_rearshaft = fcfun.shp_cylcenxtr(r = self.shaft_r,
                                        h = self.rear_shaft_l,
                                        normal = self.axis_h,
                                        ch = 0, # not centered
                                        xtr_top = 1, # to fuse
                                        xtr_bot = 0, # no extra at bottom
                                        pos = self.get_pos_h(5))

            fuse_list.append(shp_rearshaft)
        
        shp_motor = shp_base.multiFuse(fuse_list)
        shp_motor = shp_motor.removeSplitter()
        self.shp = shp_motor

        super().create_fco(self.name)

        # Save the arguments that have not been created yet
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): 
                setattr(self, i, values[i])

        self.model_type = 1 # Dimensional model

class PartGtPulley (Obj3D):
    """ Creates a GT pulley, no exact dimensions, just for the model
    ::
 
             flange_d
          ......+......
         :             :
         :_____________:....................
         |_____:_:_____|...: top_flange_h   :
            |  : :  |      :                :
            |  : :  |      :+ toothed_h     :
          __|__:_:__|__....:                :
         | ____:_:_____|....+ bot_flange_h  :
          |    : :    |                      + tot_h
          |    : :    |                     :
          |    : :    |                     :
          |____:_:____|_....................:
          :    : :     :
          :    :.:     :
          :     +      :
          :   shaft_d  :
          :            :
          :............:
                +
              base_d


    Parameters:
    -----------
    pitch: float/int
        Distance between teeth: Typically 2mm, or 3mm
    n_teeth: int
        Number of teeth of the pulley
    toothed_h: float
        Height of the toothed part of the pulley
    top_flange_h: float
        Height (thickness) of the top flange, if 0, no top flange
    bot_flange_h: float
        Height (thickness) of the bot flange, if 0, no bottom flange
    tot_h: float
        Total height of the pulley
    flange_d: float
        Flange diameter, if 0, it will be the same as the base_d
    base_d: float
        Base diameter
    shaft_d: float
        Shaft diameter
    tol: float
        Tolerance for radius (it will substracted to the radius)
        twice for the diameter. Or added if a shape to substract
    axis_h: FreeCAD.Vector
        Height vector of coordinate system (this is required)
    axis_d: FreeCAD.Vector
        Depth vector of coordinate system (perpendicular to the height)
        can be NULL
    axis_w: FreeCAD.Vector
        Width vector of coordinate system
        if V0: it will be calculated using the cross product: axis_h x axis_d
    pos_h: int
        Location of pos along the axis_h (0,1,2,3,4,5)

            * 0: at the base
            * 1: at the base of the bottom flange
            * 2: at the base of the toothed part
            * 3: at the center of the toothed part
            * 4: at the end (top) of the toothed part
            * 5: at the end (top) of the pulley

    pos_d: int
        Location of pos along the axis_d (0,1,2,3,4,5,6)

            * 0: at the center of symmetry
            * 1: at the shaft radius
            * 2: at the inner radius
            * 3: at the external radius
            * 4: at the pitch radius (outside the toothed part)
            * 5: at the end of the base (not the toothed part)
            * 6: at the end of the flange (V0 is no flange)
        
    pos_w: int
        Location of pos along the axis_w (0,1,2,3,4,5,6)
        same as pos_d
    pos: FreeCAD.Vector
        Position of the piece


    The toothed part of the pulley has 2 diameters, besides there also is
    the pitch diameter that is external to the outer diameter (related to
    the belt pitch)
    ::

                 tooth_outd : external diameter of the toothed part
               .....+.....    of the pulley
              :           :
              :           :
            | | |  : :  | | |
            | | |  : :  | | |
            | | |  : :  | | |
            | | |  : :  | | |
            | | |  : :  | | |
            :   :       :   :
            :   :.......:   :
            :       +       :
            :   tooth_ind   :  internal diameter of the toothed part
            :               :  of the pulley
            :...............:
                    +
                 pitch_d = (n_teeth x pitch) / pi  (diameter)
                                    |
                                    v
                                perimeter (n_teeth x pitch)


 
       _   _   _   _ ...............................
     _/ \_/ \_/ \_/ \_....:+ tooth_height: 0.75    + belt_height: 1.38        
                      ....:+ PLD: 0.254            :            
     _________________.............................:
       :   :
       :...:
         + tooth separation 2mm (pitch)
 
 
     PLD: Pitch Line Distance (I think), where the tensile cord is
          when the belt is on a pulley, that would be the distance added
          to the outside diameter of the belt. What is called the pitch
          diameter: for a GT2 is 


              axis_h
                :
                :
         _______:_______ .....5
        |______:_:______|.....4
            |  : :  |
            |  : :  |........3
            |  : :  |
         ___|__:_:__|___ .....2
        |______:_:______|.....1
         |     : :     | 
         |     : :     | 
         |     : :     | 
         |_____:o:_____|......0   
         :      :   :
         :      :   :
                01..23456.......axis_d, axis_w

         pos_o (origin) is at pos_h=0, pos_d=0, pos_w=0 (marked with o)

    """

    def __init__(self,
                 pitch = 2.,
                 n_teeth = 20,
                 toothed_h = 7.5,
                 top_flange_h = 1.,
                 bot_flange_h = 0,
                 tot_h = 16.,
                 flange_d = 15.,
                 base_d = 15.,
                 shaft_d = 5.,
                 tol = 0,
                 axis_d = VX,
                 axis_w = VY,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0,
                 model_type = 1, # dimensional model
                 name = None):

        if name == None:
            name = 'gt' + str(int(pitch)) + '_pulley_' + str(n_teeth)
        self.name = name

        if (((axis_d is None) or (axis_d == V0)) and
            ((axis_w is None) or (axis_w == V0))):
            # both are null, we create a random perpendicular vectors
            axis_d = fcfun.get_fc_perpend1(axis_h)
            axis_w = axis_h.cross(axis_d)
        else:
            if ((axis_d is None) or (axis_d == V0)):
                axis_d = axis_w.cross(axis_h)
            elif ((axis_w is None) or (axis_w == V0)):
                axis_w = axis_h.cross(axis_d)
            # all axis are defined

        Obj3D.__init__(self, axis_d, axis_w, axis_h, name)

        if (top_flange_h > 0 or bot_flange_h > 0) and flange_d == 0:
            logger.debug("Flange height is not null, but diameter is null")
            logger.debug("Flange diameter will be the same as the base")
            flange_d = base_d
            self.flange_d = flange_flange_d
            

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

        # belt dictionary:
        self.belt_dict = kcomp.GT[pitch]
        # diameters of the pulley:
        # pitch diameter, it is not on the pulley, but outside, on the belt
        self.pitch_d = n_teeth * pitch / math.pi
        self.pitch_r = self.pitch_d /2.
        # out radius and diameter, diameter at the outer part of the teeth
        self.tooth_out_r = self.pitch_r - self.belt_dict['PLD']
        self.tooth_out_d = 2 * self.tooth_out_r
        # inner radius and diameter, diameter at the inner part of the teeth
        self.tooth_in_r = self.tooth_out_r - self.belt_dict['TOOTH_H']
        self.tooth_in_d = 2 * self.tooth_in_r

        self.base_r = base_d / 2.
        self.shaft_r = shaft_d / 2.
        self.flange_r = flange_d / 2.

        self.base_d = base_d
        # height of the base, without the toothed part and the flange
        self.base_h = tot_h - toothed_h - top_flange_h - bot_flange_h
        self.tot_h = tot_h
        self.toothed_h = toothed_h
        self.top_flange_h = top_flange_h
        self.bot_flange_h = bot_flange_h

        self.h0_cen = 0
        self.d0_cen = 1 # symmetrical
        self.w0_cen = 1 # symmetrical

        # vectors from the origin to the points along axis_h:
        self.h_o[0] = V0
        self.h_o[1] = self.vec_h(self.base_h)
        self.h_o[2] = self.vec_h(self.base_h + self.bot_flange_h)
        self.h_o[3] = self.vec_h(self.base_h + self.bot_flange_h + toothed_h/2.)
        self.h_o[4] = self.vec_h(self.tot_h - top_flange_h)
        self.h_o[5] = self.vec_h(self.tot_h)

        # vectors from the origin to the points along axis_d:
        # these are negative because actually the pos_d indicates a negative
        # position along axis_d (this happens when it is symmetrical)
        self.d_o[0] = V0
        self.d_o[1] = self.vec_d(-self.shaft_r)
        self.d_o[2] = self.vec_d(-self.tooth_in_r)
        self.d_o[3] = self.vec_d(-self.tooth_out_r)
        self.d_o[4] = self.vec_d(-self.pitch_r)
        self.d_o[5] = self.vec_d(-self.base_r)
        self.d_o[6] = self.vec_d(-self.flange_r)

        # position along axis_w
        self.w_o[0] = V0
        self.w_o[1] = self.vec_w(-self.shaft_r)
        self.w_o[2] = self.vec_w(-self.tooth_in_r)
        self.w_o[3] = self.vec_w(-self.tooth_out_r)
        self.w_o[4] = self.vec_w(-self.pitch_r)
        self.w_o[5] = self.vec_w(-self.base_r)
        self.w_o[6] = self.vec_w(-self.flange_r)

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        shp_fuse_list = []
        # Cilynder with a hole, with an extra for the fusion
        # calculation of the extra at the bottom to make the fusion
        if self.bot_flange_h > 0:
            xtr_bot = self.bot_flange_h/2.
        elif self.base_d > self.tooth_out_d:
            xtr_bot = self.base_h/2.
        else:
            xtr_bot = 0
        # external diameter (maybe later teeth will be made
        shp_tooth_cyl = fcfun.shp_cylhole_gen(r_out = self.tooth_out_r,
                                            r_in  = self.shaft_r + tol,
                                            h = self.toothed_h,
                                            axis_h = self.axis_h,
                                            pos_h = 1, #position at the bottom
                                            xtr_top = top_flange_h/2.,
                                            xtr_bot = xtr_bot,
                                            pos = self.get_pos_h(2))
        shp_fuse_list.append(shp_tooth_cyl)
        if self.bot_flange_h > 0:
            # same width
            if self.flange_d == self.base_d:
                shp_base_flg_cyl = fcfun.shp_cylholedir(
                                    r_out = self.base_r,
                                    r_in  = self.shaft_r + tol,
                                    h = self.base_h + self.bot_flange_h,
                                    normal = self.axis_h,
                                    pos = self.pos_o)
                shp_fuse_list.append(shp_base_flg_cyl)
            else:
                shp_base_cyl = fcfun.shp_cylholedir(
                                    r_out = self.base_r,
                                    r_in  = self.shaft_r + tol,
                                    h = self.base_h,
                                    normal = self.axis_h,
                                    pos = self.pos_o)
                shp_bot_flange_cyl = fcfun.shp_cylholedir(
                                    r_out = self.flange_r,
                                    r_in  = self.shaft_r + tol,
                                    h = self.bot_flange_h,
                                    normal = self.axis_h,
                                    pos = self.get_pos_h(1))
                shp_fuse_list.append(shp_base_cyl)
                shp_fuse_list.append(shp_bot_flange_cyl)
        else: #no bottom flange
            shp_base_cyl = fcfun.shp_cylholedir(
                                    r_out = self.base_r,
                                    r_in  = self.shaft_r + tol,
                                    h = self.base_h,
                                    normal = self.axis_h,
                                    pos = self.pos_o)
            shp_fuse_list.append(shp_base_cyl)
        if self.top_flange_h > 0:
            shp_top_flange_cyl = fcfun.shp_cylholedir(
                                    r_out = self.flange_r,
                                    r_in  = self.shaft_r + tol,
                                    h = self.top_flange_h,
                                    normal = self.axis_h,
                                    pos = self.get_pos_h(4))
            shp_fuse_list.append(shp_top_flange_cyl)

        shp_pulley = fcfun.fuseshplist(shp_fuse_list)

        shp_pulley = shp_pulley.removeSplitter()

        self.shp = shp_pulley

        # normal axes to print without support
        self.prnt_ax = self.axis_h

        super().create_fco()

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): 
                setattr(self, i, values[i])

class NemaMotorPulleySet (Obj3D):
    """ 
    Set composed of a Nema Motor and a pulley

    Number positions of the pulley will be after the positions of the motor
    ::

            axis_h
                :
                :
         _______:_______ .....11 <-> 5
        |______:_:______|.....10 <-> 4
            |  : :  |
            |  : :  |........9 <-> 3
            |  : :  |
         ___|__:_:__|___ .....8 <-> 2
        |______:_:______|.....7 <-> 1
         |     : :     | 
         |     : :     | 
         |     : :     | 
         |_____:o:_____|......6 <-> 0 (for the pulley)
         :      :   :
         :      :   :
                0...56789.......axis_d, axis_w
                    |
                01  23456 (for the pulley)

              axis_h
                  :
                  :
                  2 ............................
                 | |                           :
                 | |                           + shaft_l
              ___|1|___.............           :
        _____|____0____|_____......:..circle_h.:
       | ::       3       :: |     :  
       |                     |     :
       |                     |     :
       |                     |     + base_l
       |                     |     :
       |                     |     :
       |                     |     :
       |__________4__________|.....:
                 : :               :
                 : :               :
                 : :               :+ rear_shaft_l (optional)
                 :5:               :
                  01...2..3..4.....:...........axis_d (same as axis_w)
                   |   |  |  |
                   |   |  |  v
                   |   |  | end of the motor
                   |   |  v
                   |   | bolt holes
                   |   V
                   |  radius of the circle (cylinder)
                   v
                   radius of the shaft



                axis_w
                  :
                  :
        __________:__________.....
       /                     \....: chmf_r
       |  O               O  |
       |          _          |
       |        .   .        |
       |      (  ( )  )      |........axis_d
       |        .   .        |
       |          -          |
       |  O               O  |
       \_____________________/
       :                     :
       :.....................:
                  +
               motor_w (same as d): Nema size in inches /10

     pos_o (origin) is at pos_d=0, pos_w=0, pos_h=1

    Parameters
    ----------
    nema_size: dict
        List of sizes defines in kcomps NEMA motor dimensions.
    base_l: float,
        Length (height) of the base
    shaft_l: float,
        Length (height) of the shaft, including the small cylinder (circle)
        at the base
    shaft_r: float,
        Radius of the shaft, if not defined, it will take the dimension defined
        in kcomp
    circle_r: float,
        Radius of the cylinder (circle) at the base of the shaft
        if 0 or circle_h = 0 -> no cylinder
    circle_h: float,
        Height of the cylinder at the base of the shaft
        if 0 or circle_r = 0 -> no cylinder
    chmf_r: float, 
        Chamfer radius of the chamfer along the base length (height)
    rear_shaft_l: float
        Length of the rear shaft, 0 : no rear shaft
    bolt_depth: float
        Depth of the bolt holes of the motor
    pulley_pitch: float/int
        Distance between teeth: Typically 2mm, or 3mm
    pulley_n_teeth: int
        Number of teeth of the pulley
    pulley_toothed_h: float
        Height of the toothed part of the pulley
    pulley_top_flange_h: float
        Height (thickness) of the top flange, if 0, no top flange
    pulley_bot_flange_h: float
        Height (thickness) of the bot flange, if 0, no bottom flange
    pulley_tot_h: float
        Total height of the pulley
    pulley_flange_d: float
        Flange diameter, if 0, it will be the same as the base_d
    pulley_base_d: float
        Base diameter
    pulley_tol: float
        Tolerance for radius (it will substracted to the radius)
        twice for the diameter. Or added if a shape to substract
    pulley_pos_h : float
        position in mm of the pulley along the shaft

            * 0:  it is at the base of the shaft
            * -1: the top of the pulley will be aligned with the end of the shaft

    axis_d: FreeCAD.Vector
        Depth vector of coordinate system (perpendicular to the height)
    axis_w: FreeCAD.Vector
        Width vector of coordinate system
        if V0: it will be calculated using the cross product: axis_h x axis_d
    axis_h: FreeCAD.Vector
        Height vector of coordinate system

    pos_d: int
        location of pos along the axis_d  see drawing

            * Locations coinciding with the motor
            
                * 0: at the axis of the shaft
                * 1: at the radius of the shaft
                * 2: at the end of the circle(cylinder) at the base of the shaft
                * 3: at the bolts
                * 4: at the end of the piece
            
            * Locations of the pulley
            
                * 5: at the inner radius
                * 7: at the external radius
                * 7: at the pitch radius (outside the toothed part)
                * 8: at the end of the base (not the toothed part)
                * 9: at the end of the flange (V0 is no flange)

    pos_w: int
        location of pos along the axis_w see drawing

            * Same locations of pos_d
    
    pos_h: int
        location of pos along the axis_h, see drawing
            
            * 0: at the base of the shaft (not including the circle at the base
              of the shaft)
            * 1: at the end of the circle at the base of the shaft
            * 2: at the end of the shaft
            * 3: at the end of the bolt holes
            * 4: at the bottom base
            * 5: at the end of the rear shaft, if no rear shaft, it will be
              the same as pos_h = 4
            * 6: at the base of the pulley
            * 7: at the base of the bottom flange of the pulley
            * 8: at the base of the toothed part of the pulley
            * 9: at the center of the toothed part of the pulley
            * 10: at the end (top) of the toothed part of the pulley
            * 11: at the end (top) of the pulley of the pulley

    pos : FreeCAD.Vector
        Position of the model
    name: str
        Object name
    """

    def __init__ (self,
                  # motor parameters
                  nema_size = 17,
                  base_l = 32.,
                  shaft_l = 24.,
                  shaft_r = 0,
                  circle_r = 11.,
                  circle_h = 2.,
                  chmf_r = 1, 
                  rear_shaft_l=0,
                  bolt_depth = 3.,
                  # pulley parameters
                  pulley_pitch = 2.,
                  pulley_n_teeth = 20,
                  pulley_toothed_h = 7.5,
                  pulley_top_flange_h = 1.,
                  pulley_bot_flange_h = 0,
                  pulley_tot_h = 16.,
                  pulley_flange_d = 15.,
                  pulley_base_d = 15.,
                  pulley_tol = 0,
                  pulley_pos_h = -1,
                  # general parameters
                  axis_d = VX,
                  axis_w = None,
                  axis_h = VZ,
                  pos_d = 0,
                  pos_w = 0,
                  pos_h = 1,
                  pos = V0,
                  group = 1,
                  name = ''):

        if name == None:
            name = 'nema' + str(nema_size) + '_pulley_set'
        self.name = name

        if (axis_w is None) or (axis_w == V0):
            axis_w = axis_h.cross(axis_d)

        Obj3D.__init__(self, axis_d, axis_w, axis_h, name)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

        # pos_w = 0 and pos_d are at the center, pos_h
        self.d0_cen = 1 #symmetric
        self.w0_cen = 1 #symmetric
        self.h0_cen = 0

        # creation of the motor, we don't know all the relative positions
        # so we create it at pos_d=pos_w = 0, pos_h = 1

        nema_motor = PartNemaMotor (nema_size = nema_size,
                                    base_l = base_l,
                                    shaft_l = shaft_l,
                                    shaft_r = shaft_r,
                                    circle_r = circle_r,
                                    circle_h = circle_h,
                                    chmf_r = chmf_r, 
                                    rear_shaft_l= rear_shaft_l,
                                    bolt_depth = bolt_depth,
                                    bolt_out  = 0,
                                    cut_extra = 0,
                                    axis_d = self.axis_d,
                                    axis_w = self.axis_w,
                                    axis_h = self.axis_h,
                                    pos_d = 0,
                                    pos_w = 0,
                                    pos_h = 0,
                                    pos = pos)

        super().append_part(nema_motor)
        nema_motor.parent = self

        self.shaft_r = nema_motor.shaft_r
        self.circle_r = nema_motor.circle_r
        self.circle_h = nema_motor.circle_h

        # creation of the pulley. Locate it at pos_d,w,h = 0
        gt_pulley = PartGtPulley (pitch = pulley_pitch,
                                n_teeth = pulley_n_teeth,
                                toothed_h = pulley_toothed_h,
                                top_flange_h = pulley_top_flange_h,
                                bot_flange_h = pulley_bot_flange_h,
                                tot_h = pulley_tot_h,
                                flange_d = pulley_flange_d,
                                base_d = pulley_base_d,
                                shaft_d = 2 * self.shaft_r,
                                tol = 0,
                                axis_d = self.axis_d,
                                axis_w = self.axis_w,
                                axis_h = self.axis_h,
                                pos_d = 0,
                                pos_w = 0,
                                pos_h = 0,
                                pos = pos,
                                model_type = 1) # dimensional model

        if pulley_pos_h < 0: #top of the pulley aligned with top of the shaft
            # shaft_l includes the length of the circle
            pulley_pos_h = shaft_l - gt_pulley.tot_h
            if pulley_pos_h < 0:
                pulley_pos_h = 0
            self.pulley_pos_h = pulley_pos_h
        elif pulley_pos_h + gt_pulley.base_h > shaft_l:
            logger.warning("pulley seems to be out of the shaft")

        super().append_part(gt_pulley)
        gt_pulley.parent = self

        # conversions of the relative points from the parts to the total set
        self.d_o[0] = nema_motor.d_o[0] # V0
        self.d_o[1] = nema_motor.d_o[1]
        self.d_o[2] = nema_motor.d_o[2]
        self.d_o[3] = nema_motor.d_o[3]
        self.d_o[4] = nema_motor.d_o[4]
        self.d_o[5] = gt_pulley.d_o[2]
        self.d_o[6] = gt_pulley.d_o[3]
        self.d_o[7] = gt_pulley.d_o[4]
        self.d_o[8] = gt_pulley.d_o[5]
        self.d_o[9] = gt_pulley.d_o[6]

        self.w_o[0] = nema_motor.w_o[0] # V0
        self.w_o[1] = nema_motor.w_o[1]
        self.w_o[2] = nema_motor.w_o[2]
        self.w_o[3] = nema_motor.w_o[3]
        self.w_o[4] = nema_motor.w_o[4]
        self.w_o[5] = gt_pulley.w_o[2]
        self.w_o[6] = gt_pulley.w_o[3]
        self.w_o[7] = gt_pulley.w_o[4]
        self.w_o[8] = gt_pulley.w_o[5]
        self.w_o[9] = gt_pulley.w_o[6]

        self.h_o[0] = nema_motor.h_o[0] # V0 (origin) base of the shaft
        self.h_o[1] = nema_motor.h_o[1] # end of the circle
        self.h_o[2] = nema_motor.h_o[2] # end of the shaft
        self.h_o[3] = nema_motor.h_o[3] # bottom end of the bolt holes
        self.h_o[4] = nema_motor.h_o[4] # bottom of the base 
        self.h_o[5] = nema_motor.h_o[5] # rear shaft
        # position of the base of the shaft (including the circle)
        # + nema_motor.h_o[0] = V0 (not needed)
        # relative position of the base of the pulley: V0 (not needed)
        # + gt_pulley.h_o[0] = V0 -> base of the pulley
        # distance from the base of the shaft (circle included) to the base
        # of the pulley:
        # + self.vec_h(self.pulley_pos_h):
        #self.h_o[6]  = (   nema_motor.h_o[0] + gt_pulley.h_o[0]
        #                 + self.vec_h(self.pulley_pos_h))
        self.h_o[6]  = self.vec_h(self.pulley_pos_h)
        self.h_o[7]  = self.h_o[6] + gt_pulley.h_o[1]
        self.h_o[8]  = self.h_o[6] + gt_pulley.h_o[2]
        self.h_o[9]  = self.h_o[6] + gt_pulley.h_o[3]
        self.h_o[10] = self.h_o[6] + gt_pulley.h_o[4]
        self.h_o[11] = self.h_o[6] + gt_pulley.h_o[5]

        # check if the pulley is on top of the shaft or not:
        if self.h_o[11].Length > self.h_o[5].Length:
            self.tot_h = self.h_o[11].Length + self.h_o[0].Length
        else:
            self.tot_h = self.h_o[5].Length + self.h_o[0].Length

        super().set_pos_o(adjust = 1)
        super().set_part_place(nema_motor)
        super().set_part_place(gt_pulley, self.get_o_to_h(6))

        super().place_fcos()
        if group == 1:
            super().make_group()

    def get_nema_motor(self):
        """ gets the nema motor"""
        part_list = self.get_parts()
        for part_i in part_list:
            if isinstance(part_i, PartNemaMotor):
                return part_i

    def get_gt_pulley(self):
        """ gets the gt2 pulley"""
        part_list = self.get_parts()
        for part_i in part_list:
            if isinstance(part_i, PartGtPulley):
                return part_i