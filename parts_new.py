
import FreeCAD
import Part
import DraftVecUtils
import inspect
import logging

import fcfun
import kcomp
import NuevaClase
from NuevaClase import Obj3D

from fcfun import V0, VX, VY, VZ
from kcomp import TOL

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class NemaMotorHolder(Obj3D):
    """
    Creates a holder for a Nema motor. Similar to NemaMotorHolder but creating
    the classes defined for shapes and parts. See shp_clss and fc_clss
    ::

              axis_d
                 :
                 :
         ________:_________
        ||                ||
        || O     __     O ||
        ||    /      \    ||
        ||   |        |   ||
        ||    \      /    ||
        || O     __     O ||
        ||________________|| .....
        ||________________|| ..... wall_thick.....> axis_w

           motor_xtr_space           motor_xtr_space
          ::            ::             ::
         _::____________::_         ___::____________ ..............> axis_d
        |  ::  :    :  ::  |       |      :     :    |    + motorside_thick
        |__::__:____:__::__|       0.1....:..3..:....5....:
        ||                ||       | :              /
        || ||          || ||       | :           /
        || ||          || ||       | :        /
        || ||          || ||       | :      /
        || ||          || ||       | :   /
        ||________________||       |_: /
        ::       :                 :                 :
         + reinf_thick             :....tot_d........:
                 :                 :
                 v                 v
               axis_h            axis_h


              axis_d
                 :
         ________5_________
        ||                ||
        || O     4_     O ||
        ||    /      \    ||
        ||   |   3    |   ||
        ||    \      /    ||
        || O     2_     O ||
        ||_______1________|| .....
        ||_______o____::__|| ..... wall_thick.....> axis_w
                 0    1 2  3 (axis_w)

         ________o_________ ....................................> axis_w
        |  ::  :    :  ::  |                                  :
        |__::__:_1__:__::__|....................              :
        ||                ||....+ motor_min_h  :              :
        ||  ||   2    ||  ||                   :              +tot_h
        ||  ||        ||  ||                   + motor_max_h  :
        ||  ||        ||  ||                   :              :
        ||  ||   3    ||  ||...................:              :
        ||_______4________||..................................:
        :   :    :     :   :
        :   :    v     :   :
        :   :  axis_h  :   :
        :   :          :   :
        :   :..........:   :
        :   bolt_wall_sep  :
        :                  :
        :                  :
        :.....tot_w........:


    pos_o (origin) is at pos_d=0, pos_w=0, pos_h=0, it's marked with o
        
    Parameters:
    -----------
    nema_size : int
        Size of the motor (NEMA)
    wall_thick: float
        Thickness of the side where the holder will be screwed to
    motorside_thick: float
        Thickness of the top side where the motor will be screwed to
    reinf_thick: float
        Thickness of the reinforcement walls
    motor_min_h: float
        Distance of from the inner top side to the top hole of the bolts to 
        attach the holder (see drawing)
    motor_max_h: float
        Distance of from the inner top side to the bottom hole of the bolts to 
        attach the holder
    rail: int
        1: the holes for the bolts are not holes, there are 2 rails, from
           motor_min_h to motor_max_h
        0: just 2 pairs of holes. One pair at defined by motor_min_h and the
           other defined by motor_max_h
    motor_xtr_space: float
        Extra separation between the motor and the wall side
        and also between the motor and each of the sides
    bolt_wall_d: int/float
        Metric of the bolts to attach the holder
    bolt_wall_sep: float
        Separation between the 2 bolt holes (or rails). Optional.
    chmf_r: float
        Radius of the chamfer, whenever chamfer is done
    axis_h: FreeCAD Vector
        Axis along the axis of the motor
    axis_d: FreeCAD Vector
        Axis normal to surface where the holder will be attached to
    axis_w: FreeCAD Vector
        Axis perpendicular to axis_h and axis_d, symmetrical (not necessary)
    pos_d : int
        Location of pos along axis_d (0,1,2,3,4,5)
        0: at the beginning, touching the wall where it is attached
        1: at the inner side of the side where it will be screwed
        2: bolts holes closed to the wall to attach the motor
        3: at the motor axis
        4: bolts holes away from to the wall to attach the motor
        5: at the end of the piece
    pos_w : int
        Location of pos along axis_w (0,1,2,3). Symmetrical
        0: at the center of symmetry
        1: at the center of the rails (or holes) to attach the holder
        2: at the center of the holes to attach the motor
        3: at the end of the piece
    pos_h : int
        Location of pos along axis_h (0,1,2,3)
        0: at the top (on the side of the motor axis)
        1: inside the motor wall
        2: Top end of the rail
        3: Bottom end of the rail
        4: Bottom end of the piece
    pos : FreeCAD.Vector
        Position of the piece

    """

    def __init__ (self,
                  nema_size = 17,
                  wall_thick = 4.,
                  motorside_thick = 4.,
                  reinf_thick = 4.,
                  motor_min_h =10.,
                  motor_max_h =20.,
                  rail = 1, # if there is a rail or not at the profile side
                  motor_xtr_space = 2., # counting on one side
                  bolt_wall_d = 4., # Metric of the wall bolts
                  bolt_wall_sep = 0, # optional
                  chmf_r = 1.,
                  axis_h = VZ,
                  axis_d = VX,
                  axis_w = None,
                  pos_h = 1,  # 1: inner wall of the motor side
                  pos_d = 3,  # 3: motor axis
                  pos_w = 0,  # 0: center of symmetry
                  pos = V0,
                  model_type = 3, #to be printed
                  name = None):

        self.pos = FreeCAD.Vector(0,0,0)
        self.position = pos

        if name == None:
            name = 'nema' + str(nema_size) + '_motorholder'

        if axis_w is None or axis_w == V0:
            axis_w = axis_h.cross(axis_d)

        NuevaClase.Obj3D.__init__(self, axis_d, axis_w, axis_h, name)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

        # normal axes to print without support
        self.prnt_ax = self.axis_h

        self.motor_w = kcomp.NEMA_W[nema_size]
        self.motor_bolt_sep = kcomp.NEMA_BOLT_SEP[nema_size]
        self.motor_bolt_d = kcomp.NEMA_BOLT_D[nema_size]

        self.boltwallshank_r_tol = kcomp.D912[bolt_wall_d]['shank_r_tol']
        self.boltwallhead_l = kcomp.D912[bolt_wall_d]['head_l']
        self.boltwallhead_r = kcomp.D912[bolt_wall_d]['head_r']
        self.washer_thick = kcomp.WASH_D125_T[bolt_wall_d]

        # calculation of the bolt wall separation
        self.max_bolt_wall_sep = self.motor_w - 2 * self.boltwallhead_r
    
        if bolt_wall_sep == 0:
            self.bolt_wall_sep = self.max_bolt_wall_sep
        elif bolt_wall_sep > self.max_bolt_wall_sep:
            logger.debug('bolt wall separtion too large: ' + str(bolt_wall_sep))
            self.bolt_wall_sep = self.max_bolt_wall_sep
            logger.debug('taking larges value: ' + str(self.bolt_wall_sep))
        elif bolt_wall_sep <  4 * self.boltwallhead_r:
            logger.debug('bolt wall separtion too short: ' + str(bolt_wall_sep))
            self.bolt_wall_sep = self.max_bolt_wall_sep
            logger.debug('taking larges value: ' + str(self.bolt_wall_sep))
        # else: the given separation is good

        # distance from the motor to the inner wall (in axis_d)
        self.motor_inwall_space = (  motor_xtr_space
                                   + self.boltwallhead_l + self.washer_thick)
        # making the big box that will contain everything and will be cut
        self.tot_h = motorside_thick + motor_max_h + 2 * bolt_wall_d
        self.tot_w = 2* reinf_thick + self.motor_w + 2 * motor_xtr_space
        self.tot_d = (   wall_thick + self.motor_w + self.motor_inwall_space)
        # distance from the motor axis to the wall (in axis_d)
        self.motax2wall = wall_thick + self.motor_inwall_space + self.motor_w/2.

        # definition of which axis is symmetrical
        self.h0_cen = 0
        self.d0_cen = 0
        self.w0_cen = 1 # symmetrical

        # vectors from the origin to the points along axis_h:
        self.h_o[0] = V0
        self.h_o[1] = self.vec_h(motorside_thick)
        self.h_o[2] = self.vec_h(motorside_thick + motor_min_h)
        self.h_o[3] = self.vec_h(motorside_thick + motor_max_h)
        self.h_o[4] = self.vec_h(self.tot_h)

        # position along axis_d
        self.d_o[0] = V0
        self.d_o[1] = self.vec_d(wall_thick) # inner wall
        # distance to the inner bolts of the motor
        self.d_o[2] = self.vec_d(self.motax2wall - self.motor_bolt_sep/2.)
        self.d_o[3] = self.vec_d(self.motax2wall)  # motor axis
        self.d_o[4] = self.vec_d(self.motax2wall + self.motor_bolt_sep/2.)
        self.d_o[5] = self.vec_d(self.tot_d)

        # vectors from the origin to the points along axis_w:
        # these are negative because actually the pos_w indicates a negative
        # position along axis_w (this happens when it is symmetrical)
        self.w_o[0] = V0
        self.w_o[1] = self.vec_w(-self.bolt_wall_sep/2.)
        self.w_o[2] = self.vec_w(-self.motor_bolt_sep/2.)
        self.w_o[3] = self.vec_w(-self.tot_w/2.)

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        # make the whole box, extra height and depth to cut all the way
        # back and down:
        shp_box = fcfun.shp_box_dir (box_w = self.tot_w,
                                     box_d = self.tot_d,
                                     box_h = self.tot_h,
                                     fc_axis_h = self.axis_h,
                                     fc_axis_d = self.axis_d,
                                     cw=1, cd=0, ch=0, pos = self.pos_o)
        # little chamfer at the corners, if fillet there are some problems
        shp_box = fcfun.shp_filletchamfer_dir(shp_box, self.axis_h,
                                              fillet=0,
                                              radius = chmf_r)
        shp_box = shp_box.removeSplitter()

        # chamfer of the box to make a 'triangular' reinforcement
        chmf_reinf_r = min(self.tot_d- wall_thick, self.tot_h-motorside_thick)
        # chamfer at the lower point (h=4), and the other end of d (d=5)
        shp_box = fcfun.shp_filletchamfer_dirpt(shp_box, self.axis_w,
                                              fc_pt =self.get_pos_dwh(5,0,4),
                                              fillet=0,
                                              radius = chmf_reinf_r)
        shp_box = shp_box.removeSplitter()

        # holes:
        holes = []
        # the space for the motor
        shp_motor = fcfun.shp_box_dir (
                                    box_w = self.motor_w + 2 * motor_xtr_space,
                                    box_d = self.tot_d + chmf_r,
                                    box_h = self.tot_h,
                                    fc_axis_h = self.axis_h,
                                    fc_axis_d = self.axis_d,
                                    cw=1, cd=0, ch=0,
                                    # at the inner walls
                                    pos = self.get_pos_dwh(1,0,1))

        shp_motor = fcfun.shp_filletchamfer_dir(shp_motor, fc_axis=self.axis_h,
                                                fillet=0, radius=chmf_r)
        holes.append(shp_motor)

        # central circle of the motor
        shp_hole = fcfun.shp_cylcenxtr(
                                 r=(self.motor_bolt_sep - self.motor_bolt_d)/2.,
                                 h = motorside_thick,
                                 normal = self.axis_h,
                                 ch = 0,
                                 xtr_top = 1,
                                 xtr_bot = 1,
                                 # position of the motor axis, at the top
                                 pos = self.get_pos_d(3))
        holes.append(shp_hole)

        # motor bolt holes
        for pt_d in (2,4):  # points of the motor holes along axis d
            for pt_w in (-2,2): # points of the motor holes along axis_w
                shp_hole = fcfun.shp_cylcenxtr( r = self.motor_bolt_d/2.+TOL,
                                            h = motorside_thick,
                                            normal = self.axis_h,
                                            ch = 0,
                                            xtr_top = 1,
                                            xtr_bot = 1,
                                            pos = self.get_pos_dwh(pt_d,pt_w,0))
                holes.append(shp_hole)
    
        # rail holes. To mount the motor holder to a profile or whatever
        for pt_w in (-1,1): # points of the holes to attach the holder
            # hole for the rails
            if rail == 1:
                shp_hole = fcfun.shp_box_dir_xtr(
                                       box_w = self.boltwallshank_r_tol * 2.,
                                       box_d = wall_thick,
                                       box_h = motor_max_h - motor_min_h,
                                       fc_axis_h = self.axis_h,
                                       fc_axis_d = self.axis_d,
                                       cw=1, cd=0, ch=0,
                                       xtr_d =1, xtr_nd=1, #to cut
                                       # h:2 the position on top of the rail
                                       pos = self.get_pos_dwh(0,pt_w,2))
                holes.append(shp_hole)
            # hole for the ending of the rails (4 semicircles)
            for pt_h in (2,3) : # both ends of the rail (along axis_h)
                shp_hole = fcfun.shp_cylcenxtr(
                                            r = self.boltwallshank_r_tol,
                                            h = wall_thick,
                                            normal = self.axis_d,
                                            ch = 0,
                                            xtr_top = 1,
                                            xtr_bot = 1,
                                            pos = self.get_pos_dwh(0,pt_w,pt_h))
                holes.append(shp_hole)

        shp_holes = fcfun.fuseshplist(holes)
        shp_motorholder = shp_box.cut(shp_holes)
        shp_bracket =shp_motorholder.removeSplitter()
        self.shp = shp_bracket
        super().create_fco()
        # Need to set first in (0,0,0) and after that set the real placement.
        # This enable to do rotations without any issue
        self.fco.Placement.Base = FreeCAD.Vector(0,0,0) 
        self.fco.Placement.Base = self.position


class SimpleEndstopHolder (Obj3D):

    """
    Very simple endstop holder to be attached to a alu profile and
    that can be adjusted
    ::
    
              rail_l         axis_w
           ...+....           :
          :        :          :
        ______________________:
       |   ________           |
       |  (________)      O   |
       |   ________           |-----> axis_d
       |  (________)      O   |
       |______________________|
                    :          :
                    estp_tot_h

       pos_d points:          axis_h
                              :
       1___2______3_______4___5.............     ref_h = 2
       | :..........:    : : |:.....       + h
       |__:________:_____:_:_|:.....base_h.:     ref_h = 1


       pos_w points
                             axis_w
        _____________________ :
       |   ________     |    |:
       |  (________) ---| 0  |:
       1   ________  ---|    |:-----> axis_d.
       3  (________) ---| 2  |:
       4________________|____|:

                               
        _____________________ .......
       | :          :    : : |:.....: endstop_nut_dist 
       | :..........:   :   :|:     
       |__:________:____:___:|:.....
 
                  if endstop_nut_dist == 0
                    just take the length+TOL of the nut
        _____________________ 
       | :          :    : : |:
       | :..........:    : : |:.....
       |__:________:____:___:|:.....kcomp.NUT_D934_L[estp_bolt_d]+TOL

    Parameters
    ----------
    d_endstop : 
        Dictionary of the endstop
    rail_l : float
        Length of the rail, but only the internal length, not counting
        the arches to make the semicircles for the bolts
        just from semicircle center to the other semicircle center
    h : float
        Total height, if 0 it will be the minimum height
    base_h : float
        Height for the base (for the mounting bolts)
    holder_out : float
        The endstop holder can end a little bit before to avoid
        it to be the endstop
    mbolt_d : float
        Diameter (metric) of the mounting bolts (for the holder
        not for the endstop
    endstop_nut_dist : 
        Distance from the top to the endstop nut.
        if zero
    min_d : int
        1: make the endstop axis_d dimension the minimum
    axis_d : FreeCAD Vector
        Axis along the depth
    axis_w : FreeCAD Vector
        Axis along the width
    axis_h : FreeCAD Vector
        Axis along the height
    pos_d : int
        Reference (zero) of axis_d

            * 0 = at the end on the side of the rails
            * 1 = at the circle center of one rail (closer to 1)
            * 2 = at the circle center of the other rail, closer to endstop
            * 3 = at the bolt of the endstop
            * 4 = at the end of the endstop (the holder ends before that)

    pos_w : int
        Reference on axis_w. it is symmetrical, only the negative side

            * 0 = centered
            * 1 = at one endstop bolt
              the other endstop bolt will be on the direction of fc_axis_w
            * 2 = at one rail center
              the rail center will be on the direction of fc_axis_w
            * 3 = at the end
              the end will be on the direction of fc_axis_w

    pos_h : int
        Reference (zero) of axis_h

            * 0: at the bottom
            * 1: on top

    pos : FreeCAD.Vector
        Object placement
    wfco : int
        1 a freecad object will be created
    name : str
        Name of the freecad object, if created

    the rails can be countersunk to make space for the bolts

    """

    def __init__(self,
                 d_endstop,
                 rail_l = 15,
                 base_h = 5.,
                 h = 0,
                 holder_out = 2.,
                 #csunk = 1,
                 mbolt_d = 3.,
                 endstop_nut_dist = 0,
                 min_d = 0,
                 axis_d = VX,
                 axis_w = V0,
                 axis_h = VZ,
                 pos_d = 1,
                 pos_w = 1,
                 pos_h = 1,
                 pos = V0,
                 wfco = 1,
                 name = 'simple_enstop_holder'):

        self.pos = FreeCAD.Vector(0,0,0)
        self.position = pos

        self.wfco = wfco
        self.name = name
        self.base_h = base_h,

        # normalize the axis
        axis_h = DraftVecUtils.scaleTo(axis_h,1)
        axis_d = DraftVecUtils.scaleTo(axis_d,1)
        if axis_w == V0:
            axis_w = axis_h.cross(axis_d)
        else:
            axis_w = DraftVecUtils.scaleTo(axis_w,1)
        axis_h_n = axis_h.negative()
        axis_d_n = axis_d.negative()
        axis_w_n = axis_w.negative()    

        self.axis_h = axis_h
        self.axis_d = axis_d
        self.axis_w = axis_w

        self.d0_cen = 0
        self.w0_cen = 1 # centered
        self.h0_cen = 0

        self.pos_d = pos_d
        self.pos_w = pos_w
        self.pos_h = pos_h

        self.pos = pos

        Obj3D.__init__(self, axis_d, axis_w, axis_h, name)

        # best axis to print, to be pointing up:
        self.axis_print = axis_h

        self.d_endstop = d_endstop

        #                              :holder_out
        #      __:________:____________: :..................
        #     |   _________      |     |                   :
        #     |  (_________) ----| 0   |                   + tot_w
        #     |   _________  ----|     |-----> axis_d      :
        #     |  (_________) ----| 0   |                   :
        #     |__________________|_____|...................:
        #     :  :         : :   : :     :
        #     :  :..rail_l.: :   : :     :
        #     :  :         : :   :.:     :
        #     :bolthead_d  : :   : +estp_bolt_dist
        #                  : :   :       :
        #          bolthead_r:   :.......:
        #                    :      +estp_d
        #                    :           :
        #                    :.estp_tot_d:
        #     :...................._..:  :
        #         tot_d

        #      The width depend which side is larger
        #
        #                     ...... ______________________ ....
        #        mbolt_head_r ......|   ________     |     |    :
        #        mbolt_head_d ......|  (________) ---| 0   |    :
        #mbolt_head_d or more ......|   ________  ---|     |    + estp_w or more
        #        mbolt_head_d ......|  (________) ---| 0   |    :
        #        mbolt_head_r ......|________________|_____|....:


        #   it can have a second hole:
        #                             :  :estop_topbolt_dist
        #                                : holder_out
        #      __:________:______________: :..................
        #     |   _________      |       |                   :
        #     |  (_________) ----| 0  0  |                   + tot_w
        #     |   _________  ----|       |-----> axis_d      :
        #     |  (_________) ----| 0  0  |                   :
        #     |__________________|_______|...................:
        #     :  :     

        # mounting bolt data
        d_mbolt = kcomp.D912[int(mbolt_d)]  #dictionary of the mounting bolt
        #print(str(d_mbolt))
        mbolt_r_tol = d_mbolt['shank_r_tol']
        mbolt_head_r = d_mbolt['head_r']
        mbolt_head_r_tol = d_mbolt['head_r_tol']
        mbolt_head_l = d_mbolt['head_l']
        print (str(mbolt_head_l))
        # endstop data. change h->d, d->h, l->w
        estp_tot_d = d_endstop['HT']
        estp_d = d_endstop['H']
        estp_bolt_dist = d_endstop['BOLT_H']
        estp_bolt_sep = d_endstop['BOLT_SEP']
        estp_bolt_d = d_endstop['BOLT_D']  #diameter, not depth
        estp_w = d_endstop['L']

        # if there is a second bolt 
        if 'BOLT_TOP_H' in d_endstop:
           estop_2ndbolt_topdist = d_endstop['BOLT_TOP_H']
        else:
           estop_2ndbolt_topdist = 0

        # length of the pins:
        estp_pin_d  = estp_tot_d - estp_d
        if min_d == 0:
            tot_d = 3*mbolt_head_r + rail_l + estp_tot_d - holder_out
            # nut axis: (nut axis of the hexagon vertex
            hex_verx = axis_d
        else:
            # Taking the minimum lenght, very tight
            tot_d = (3*mbolt_head_r + rail_l + estp_d - holder_out
                     + estp_pin_d/2.)
            hex_verx = axis_w # less space

        # Total width is the largest value from:
        # - the width(length) of the endstop
        # - the rail width: 2 bolt head diameters, and 2 more: 1 diameter 
        #   between, and a radius to the end
        tot_w = max(estp_w, 8 * mbolt_head_r)
 
        if h== 0:
            tot_h = base_h + mbolt_head_l
        else:
            tot_h = base_h + mbolt_head_l
            if tot_h > h:
                logger.debug('h is smaller that it should, taking: ')
                logger.debug(str(tot_h))
            else:
                tot_h = h

        self.tot_h = tot_h
        self.tot_w = tot_w
        self.tot_d = tot_d

        if endstop_nut_dist == 0:
            endstop_nut_l =  kcomp.NUT_D934_L[estp_bolt_d]+TOL
        else:
            if endstop_nut_dist > tot_h -  kcomp.NUT_D934_L[estp_bolt_d]+TOL:
                logger.debug('endstop_nut_dist: ' + str(endstop_nut_dist)
                             + ' larger than total height - (nut length+tol): '
                             + str(tot_h) + ' - '
                             + str( kcomp.NUT_D934_L[estp_bolt_d] + TOL))
                endstop_nut_l =  kcomp.NUT_D934_L[estp_bolt_d]+TOL
            else:
                endstop_nut_l = tot_h - endstop_nut_dist
            
        # ------------ DISTANCES ON AXIS_D
        # ref_d points:          fc_axis_h
                               
        #  1___2______3_______4__.5.............     ref_h = 2
        #  | :..........:    : : |:.....       + h
        #  |__:________:_____:_:_|:.....base_h.:     ref_h = 1

        # the end it is not on the holder because of -holder_out
        # distance from 1 to 2 in axis_d
        
        # vectors from the origin to the points along axis_d:
        self.d_o[0] = V0
        self.d_o[1] = self.vec_d(2* mbolt_head_r)
        self.d_o[2] = self.vec_d(2* mbolt_head_r + rail_l)
        self.d_o[3] = self.vec_d((tot_d + holder_out) - (estp_d - estp_bolt_dist))
        self.d_o[4] = self.vec_d(tot_d + holder_out)
        if estop_2ndbolt_topdist > 0 :
            self.d_o[5] = self.vec_d(tot_d + holder_out - estop_2ndbolt_topdist)
        else:
            self.d_o[5] = self.d_o[3]

        # vectors from the origin to the points along axis_w:
        self.w_o[0] = V0
        self.w_o[1] = self.vec_w(estp_bolt_sep/2.)
        self.w_o[2] = self.vec_w(tot_w/2. - 2* mbolt_head_r)
        self.w_o[3] = self.vec_w(tot_w/2.)

        # vectors from the origin to the points along axis_h:
        self.h_o[0] = V0
        self.h_o[1] = self.vec_h(tot_h)

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        # TODO: clear this parts when points d_o, w_o, h_o
        dis_1_2_d = 2* mbolt_head_r # d_o[1]
        dis_1_3_d = dis_1_2_d + rail_l # d_o[2]
        #dis_2_3_d = rail_l
        dis_1_5_d = tot_d + holder_out # d_o[4]
        dis_1_4_d = dis_1_5_d - (estp_d - estp_bolt_dist) # d_o[3]
        # distances to the new point, that is the second bolt hole, if exists
        if estop_2ndbolt_topdist > 0 :
            dis_1_6_d = dis_1_5_d - estop_2ndbolt_topdist
        else:
            # same as 4: (to avoid errors) it will be the same hole
            dis_1_6_d = dis_1_4_d

        fc_1_2_d = self.d_o[1]
        fc_1_3_d = self.d_o[2]
        fc_1_4_d = self.d_o[3]
        fc_1_5_d = self.d_o[4]
        fc_1_6_d = self.d_o[5]
        # vector from the reference point to point 1 on axis_d
        if pos_d == 0: 
            refto_1_d = V0
        elif pos_d == 1:
            refto_1_d = fc_1_2_d.negative()
        elif pos_d == 2:
            refto_1_d = fc_1_3_d.negative()
        elif pos_d == 3:
            refto_1_d = fc_1_4_d.negative()
        elif pos_d == 4:
            refto_1_d = fc_1_5_d.negative()
        elif pos_d == 5:
            refto_1_d = fc_1_6_d.negative()
        else:
            logger.error('wrong reference point')

        # ------------ DISTANCES ON AXIS_W
        # ref_w points
        #                      fc_axis_w
        #  _____________________ :
        # |   ________     |    |:
        # |  (________) ---| 0  |:
        # 1   ________  ---|    |:-----> fc_axis_d.
        # 3  (________) ---| 2  |:
        # 4________________|____|:

        # distance from 1 to 2 on axis_w
        dis_1_2_w = estp_bolt_sep/2.
        dis_1_4_w = tot_w/2.
        dis_1_3_w = dis_1_4_w - 2* mbolt_head_r

        fc_1_2_w = self.w_o[1]
        fc_1_3_w = self.w_o[2]
        fc_1_4_w = self.w_o[3]
        # vector from the reference point to point 1 on axis_w
        if pos_w == 0: 
            refto_1_w = V0
        elif pos_w == 1:
            refto_1_w = fc_1_2_w.negative()
        elif pos_w == 2:
            refto_1_w = fc_1_3_w.negative()
        elif pos_w == 3:
            refto_1_w = fc_1_4_w.negative()
        else:
            logger.error('wrong reference point')

        # ------------ DISTANCES ON AXIS_H
        fc_1_2_h = DraftVecUtils.scale(axis_h, tot_h)
        fc_2_1_h = fc_1_2_h.negative()
        if pos_h == 0: 
            refto_2_h = self.h_o[1]
        elif pos_h == 1:
            refto_2_h = V0
        else:
            logger.error('wrong reference point')


        # Situation of the point on d=1, s=1, h=2
        #       ____________
        #      /
        #     * d1_w1_h2
        #    /____________
        #    |
        #
        # this is an absolute position
        # super().get_pos_dwh(pos_d,pos_w,pos_h)
        d1_w1_h2_pos = self.pos + refto_1_d + refto_1_w + refto_2_h
        d1_w1_h1_pos = d1_w1_h2_pos + fc_2_1_h


        # draw the box from this point d1 s1 h2
        shp_box = fcfun.shp_box_dir(box_w = tot_w,
                                    box_d = tot_d,
                                    box_h = tot_h,
                                    fc_axis_h = axis_h_n,
                                    fc_axis_d = axis_d,
                                    cw = 1, cd = 0, ch = 0,
                                    pos = d1_w1_h2_pos)

        shp_box = fcfun.shp_filletchamfer_dir(shp_box, fc_axis = axis_h,
                                              fillet=1,
                                              radius = 2)

        holes = []
        # holes for the endstop bolts, point: d4 w2 h1
        for fc_1_2_wi in [fc_1_2_w, fc_1_2_w.negative()]:
            pos_estpbolt = d1_w1_h1_pos + fc_1_4_d + fc_1_2_wi
            # hole with the nut hole
            shp_estpbolt = fcfun.shp_bolt_dir (
                             r_shank= (estp_bolt_d+TOL)/2.,
                             l_bolt = tot_h,
                           # 1 TOL didnt fit
                           r_head = (kcomp.NUT_D934_D[estp_bolt_d]+2*TOL)/2.,
                             l_head = endstop_nut_l,
                             hex_head = 1,
                             xtr_head = 1, xtr_shank = 1,
                             fc_normal = axis_h,
                             fc_verx1 = hex_verx,
                             pos = pos_estpbolt)
            holes.append(shp_estpbolt)
            # it can have a second hole
            if estop_2ndbolt_topdist >0:
                pos_estp_top_bolt =  d1_w1_h1_pos + fc_1_6_d + fc_1_2_wi
                # hole with the nut hole
                shp_estpbolt = fcfun.shp_bolt_dir (
                             r_shank= (estp_bolt_d+TOL)/2.,
                             l_bolt = tot_h,
                           # 1 TOL didnt fit
                           r_head = (kcomp.NUT_D934_D[estp_bolt_d]+2*TOL)/2.,
                             l_head = endstop_nut_l,
                             hex_head = 1,
                             xtr_head = 1, xtr_shank = 1,
                             fc_normal = axis_h,
                             fc_verx1 = hex_verx,
                             pos = pos_estp_top_bolt)
                holes.append(shp_estpbolt)



        # holes for the rails, point d2 w3 h2
        for fc_1_3_wi in [fc_1_3_w, fc_1_3_w.negative()]:
            #hole for the rails, use the function stadium
            rail_pos = d1_w1_h2_pos + fc_1_2_d + fc_1_3_wi
            shp_rail_sunk = fcfun.shp_stadium_dir (
                                  length = rail_l,
                                  radius = mbolt_head_r_tol,
                                  height = mbolt_head_l,
                                  fc_axis_l = axis_d,
                                  fc_axis_h = axis_h_n,
                                  ref_l = 2, #at the center of semicircle
                                  ref_s = 1, # symmetrical on the short side
                                  ref_h = 2,
                                  xtr_h = 0,
                                  xtr_nh = 1,
                                  pos = rail_pos)
            shp_rail = fcfun.shp_stadium_dir (
                                  length = rail_l,
                                  radius = mbolt_r_tol,
                                  height = tot_h,
                                  fc_axis_l = axis_d,
                                  fc_axis_h = axis_h_n,
                                  ref_l = 2,
                                  ref_s = 1,
                                  ref_h = 2,
                                  xtr_h = 1,
                                  xtr_nh = 0,
                                  pos = rail_pos)

                                  
                                  
            holes.append(shp_rail)
            holes.append(shp_rail_sunk)

        shp_holes = fcfun.fuseshplist(holes)
        shp_holder = shp_box.cut(shp_holes)
           
        self.shp = shp_holder

        if wfco == 1:
            super().create_fco()
            # Need to set first in (0,0,0) and after that set the real placement.
            # This enable to do rotations without any issue
            self.fco.Placement.Base = FreeCAD.Vector(0,0,0) 
            self.fco.Placement.Base = self.position
