# ----------------------------------------------------------------------------
# -- Components
# -- comps library
# -- Python classes that creates useful parts for FreeCAD
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- October-2016
# ----------------------------------------------------------------------------
# -- (c) David Muñoz
# -- Update
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- February-2021
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

import FreeCAD
import Part
import DraftVecUtils
import inspect
import logging
import os
import math

import fcfun
import kcomp
import NuevaClase
from NuevaClase import Obj3D

from fcfun import V0, VX, VY, VZ, addCyl_pos

logging.basicConfig(level=logging.DEBUG,
                    format='%(%(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


class SkDir (Obj3D):
    # Similar to Sk, but in any direction

    """
    SK dimensions:
    dictionary for the dimensions
    ::
    
        mbolt: is mounting bolt. it corresponds to its metric
        tbolt: is the tightening bolt.
        SK12 = { 'd':12.0, 'H':37.5, 'W':42.0, 'L':14.0, 'B':32.0, 'S':5.5,
                 'h':23.0, 'A':21.0, 'b': 5.0, 'g':6.0,  'I':20.0,
                 'mbolt': 5, 'tbolt': 4} 

    ::

             fc_axis_h
             :
          ___:___       _______________________________  tot_h 
         |  ___  |                     
         | /   \ |      __________ HoleH = h
         | \___/ |  __
       __|       |__ /| __
      |_____________|/  __ TotD = L ___________________
  
           ___:___                     ___
          |  ___  |                   |...|       
          | / 2 \ |                   3 1 |.....> fc_axis_d
          | \_*_/ |                   |...|
      ____|       |____               |___|
     8_:5_____4_____::_|..fc_axis_w   6_7_|....... fc_axis_d
     :                 :              :   :
     :... tot_w .......:              :...:
                                       tot_d
 
    Parameters
    ----------
    fc_axis_h : FreeCAD.Vector
        Axis on the height direction
    fc_axis_d : FreeCAD.Vector
        Axis on the depth (rod) direction
    fc_axis_w : FreeCAD.Vector
        Width (perpendicular) dimension, only useful if I finally
        include the tightening bolt, or if w_o != 1
    h_o : int
        * 1: reference at the Rod Height dimension (rod center):
          points 1, 2, 3
        * 0: reference at the base: points 4, 5
    w_o : int
        * 1: reference at the center on the width dimension (fc_axis_w)
          points: 2, 4,
        * 0: reference at one of the bolt holes, point 5
        * -1: reference at one end. point 8
    d_o : int
        * 1: reference at the center of the depth dimension
          (fc_axis_d) points: 1,7
        * 0: reference at one of the ends on the depth dimension
          points 3, 6
    pillow : int
        * 1 to make it the same height of a pillow block
    pos : FreeCAD.Vector
        Placement
    wfco : int
        * 1 to create a FreeCAD Object
    tol : float
        Tolerance of the axis
    name : str
        FreeCAD Object name
        
    Returns
    -------
    FreeCAD Object
        FreeCAD Object of a shaft holder

    """

    # separation of the upper side (it is not defined). Change it
    # measured for sk12 is 1.2
    up_sep_dist = 1.2

    # tolerances for holes 
    holtol = 1.1

    def __init__(self, size,
                 fc_axis_h=VZ,
                 fc_axis_d=VX,
                 fc_axis_w=V0,
                 pos_h=1,
                 pos_w=1,
                 pos_d=1,
                 pillow=0,  # make it the same height of a pillow block
                 pos=V0,
                 wfco=1,
                 tol=0.3,
                 name="shaft_holder"):
        self.size = size
        self.wfco = wfco
        self.name = name

        self.pos = FreeCAD.Vector(0, 0, 0)
        self.position = pos

        self.tol = tol
        self.pos_h = pos_h
        self.pos_w = pos_w
        self.pos_d = pos_d

        doc = FreeCAD.ActiveDocument
        if pillow == 0:
            skdict = kcomp.SK.get(size)
        else:
            skdict = kcomp.PILLOW_SK.get(size)
        if skdict is None:
            logger.error("Sk size %d not supported", size)

        # normalize de axis
        axis_h = DraftVecUtils.scaleTo(fc_axis_h, 1)
        axis_d = DraftVecUtils.scaleTo(fc_axis_d, 1)
        if fc_axis_w == V0:
            axis_w = axis_h.cross(axis_d)
        else:
            axis_w = DraftVecUtils.scaleTo(fc_axis_w, 1)

        axis_h_n = axis_h.negative()
        axis_d_n = axis_d.negative()
        axis_w_n = axis_w.negative()

        NuevaClase.Obj3D.__init__(self, axis_d, axis_w, axis_h, name=name)

        # Total height:
        sk_h = skdict['H']
        self.tot_h = sk_h
        # Total width (Y):
        sk_w = skdict['W']
        self.tot_w = sk_w
        # Total depth (x):
        sk_d = skdict['L']
        self.tot_d = sk_d
        # Base height
        sk_base_h = skdict['g']
        # center width
        sk_center_w = skdict['I']
        # Axis height:
        sk_axis_h = skdict['h']
        # self.axis_h = sk_axis_h
        # Mounting bolts separation
        sk_mbolt_sep = skdict['B']
    
        # tightening bolt with added tolerances:
        tbolt_d = skdict['tbolt']
        # Bolt's head radius
        tbolt_head_r = (self.holtol
                        * kcomp.D912_HEAD_D[skdict['tbolt']])/2.0
        # Bolt's head length
        tbolt_head_l = (self.holtol
                        * kcomp.D912_HEAD_L[skdict['tbolt']])
        # Mounting bolt radius with added tolerance
        mbolt_r = self.holtol * skdict['mbolt']/2.

        self.d0_cen = 0 
        self.w0_cen = 1  # symmetric
        self.h0_cen = 0
        # vectors from the origin to the points along axis_d:
        self.d_o[0] = V0  # origin
        self.d_o[1] = self.vec_d(sk_d/2.)
        self.d_o[2] = self.vec_d(sk_d)
        
        # vectors from the origin to the points along axis_w:
        self.w_o[0] = V0
        self.w_o[1] = self.vec_w(sk_mbolt_sep/2)
        self.w_o[2] = self.vec_w(sk_w/2)

        # vectors from the origin to the points along axis_h:
        self.h_o[0] = V0
        self.h_o[1] = self.vec_h(sk_axis_h)

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        # TODO: See how to change this reference points
        if pos_h == 1:  # distance vectors on axis_h
            ref2rod_h = V0  # h_o[0]
            ref2base_h = DraftVecUtils.scale(axis_h, -sk_axis_h)  # h_o[1]
        else:
            ref2rod_h = DraftVecUtils.scale(axis_h, sk_axis_h)  # h_o[1]
            ref2base_h = V0  # h_o[0]
        if pos_w == 0:  # distance vectors on axis_w
            ref2cen_w = V0  # w_o[0]
            ref2bolt_w = DraftVecUtils.scale(axis_w, -sk_mbolt_sep/2.)  # w_o[-1]
            ref2end_w = DraftVecUtils.scale(axis_w, -sk_w/2.)  # w_o[2]
        elif pos_w == 1:
            ref2cen_w = DraftVecUtils.scale(axis_w, sk_mbolt_sep/2.)  # w_o[1]
            ref2bolt_w = V0  # w_o[0]
            ref2end_w = DraftVecUtils.scale(axis_w, -(sk_w-sk_mbolt_sep)/2.)  # w_o[]
        else:  # w_o == -1 at the end on the width dimension
            ref2cen_w = DraftVecUtils.scale(axis_w, sk_w/2.)  # w_o[2]
            ref2bolt_w = DraftVecUtils.scale(axis_w, (sk_w-sk_mbolt_sep)/2.)  # w_o[]
        if pos_d == 1:  # distance vectors on axis_d
            ref2cen_d = V0  # d_o[0]
            ref2end_d = DraftVecUtils.scale(axis_d, -sk_d/2.)  # d_o[1]
        else:
            ref2cen_d = DraftVecUtils.scale(axis_d, sk_d/2.)  # d_o[1]
            ref2end_d = V0  # d_o[0]

        # TODO: Use the newe method:
        # super().get_pos_dwh(pos_d,pos_w,pos_h)
        basecen_pos = self.pos + ref2base_h + ref2cen_w + ref2cen_d
        # Making the tall box:
        shp_tall = fcfun.shp_box_dir(box_w=sk_center_w,
                                     box_d=sk_d,
                                     box_h=sk_h,
                                     fc_axis_w=axis_w,
                                     fc_axis_h=axis_h,
                                     fc_axis_d=axis_d,
                                     cw=1, cd=1, ch=0, pos=basecen_pos)
        # Making the wide box:
        shp_wide = fcfun.shp_box_dir(box_w=sk_w,
                                     box_d=sk_d,
                                     box_h=sk_base_h,
                                     fc_axis_w=axis_w,
                                     fc_axis_h=axis_h,
                                     fc_axis_d=axis_d,
                                     cw=1, cd=1, ch=0, pos=basecen_pos)
        shp_sk = shp_tall.fuse(shp_wide)
        doc.recompute()
        shp_sk = shp_sk.removeSplitter()
        
        holes = []

        # Shaft hole, 
        rodcen_pos = self.pos + ref2rod_h + ref2cen_w + ref2cen_d
        rod_hole = fcfun.shp_cylcenxtr(r=size/2. + self.tol,
                                       h=sk_d,
                                       normal=axis_d,
                                       ch=1,
                                       xtr_top=1,
                                       xtr_bot=1,
                                       pos=rodcen_pos)
        holes.append(rod_hole)

        # the upper sepparation
        shp_topopen = fcfun.shp_box_dir_xtr(box_w=self.up_sep_dist,
                                            box_d=sk_d,
                                            box_h=sk_h-sk_axis_h,
                                            fc_axis_w=axis_w,
                                            fc_axis_h=axis_h,
                                            fc_axis_d=axis_d,
                                            cw=1, cd=1, ch=0,
                                            xtr_h=1, xtr_d=1, xtr_nd=1,
                                            pos=rodcen_pos)
        holes.append(shp_topopen)

        # Tightening bolt hole
        # tbolt_d is the diameter of the bolt: (M..) M4, ...
        # tbolt_head_r: is the radius of the tightening bolt's head
        # (including tolerance), which its bottom either
        # - is at the middle point between
        #  - A: the total height :sk_h
        #  - B: the top of the shaft hole: axis_h + size/2.
        #  - so the result will be (A + B)/2
        # tot_h - (axis_h + size/2.)
        #       _______..A........................
        #      |  ___  |.B.......+ rodtop2top_dist = sk_h - (axis_h + size/2.) 
        #      | /   \ |.......+ size/2.
        #      | \___/ |       :
        #    __|       |__     + axis_h
        #   |_____________|....:

        rodtop2top_dist = sk_h - (sk_axis_h + size/2.)
        tbolt_pos = (rodcen_pos
                     + DraftVecUtils.scale(axis_w, sk_center_w/2.)
                     + DraftVecUtils.scale(axis_h, size/2.)
                     + DraftVecUtils.scale(axis_h, rodtop2top_dist/2.))
        shp_tbolt = fcfun.shp_bolt_dir(r_shank=tbolt_d/2.,
                                       l_bolt=sk_center_w,
                                       r_head=tbolt_head_r,
                                       l_head=tbolt_head_l,
                                       hex_head=0,
                                       xtr_head=1,
                                       xtr_shank=1,
                                       support=0,
                                       fc_normal=axis_w_n,
                                       fc_verx1=axis_h,
                                       pos=tbolt_pos)
        holes.append(shp_tbolt)
 
        # Mounting bolts
        cen2mbolt_w = DraftVecUtils.scale(axis_w, sk_mbolt_sep/2.)
        for w_pos in [cen2mbolt_w.negative(), cen2mbolt_w]:
            mbolt_pos = basecen_pos + w_pos
            mbolt_hole = fcfun.shp_cylcenxtr(r=mbolt_r,
                                             h=sk_d,
                                             normal=axis_h,
                                             ch=0,
                                             xtr_top=1,
                                             xtr_bot=1,
                                             pos=mbolt_pos)
            holes.append(mbolt_hole)

        shp_holes = fcfun.fuseshplist(holes)
        shp_sk = shp_sk.cut(shp_holes)
        self.shp = shp_sk

        if wfco == 1:
            super().create_fco()
            # Need to set first in (0,0,0) and after that set the real placement.
            # This enable to do rotations without any issue
            self.fco.Placement.Base = FreeCAD.Vector(0, 0, 0)
            self.fco.Placement.Base = self.position

    def color(self, color=(1, 1, 1)):
        if self.wfco == 1:
            self.fco.ViewObject.ShapeColor = color
        else:
            logger.debug("Object with no fco")


class AluProf (Obj3D):

    """
    Creates a shape of a generic aluminum profile in any direction
    ::

         :----- width ----:
         :       slot     :
         :      :--:      :
         :______:  :______:
         |    __|  |__    |
         | |\ \      / /| |
         |_| \ \____/ / |_| ...........
             |        | ......        insquare
             |  (  )  | ......indiam  :
          _  |  ____  | ..............:
         | | / /    \ \ | |
         | |/ /_    _\ \| | .... 
         |______|  |______| ....thick
   
    Parameters:
    -----------
    width: float
        Width of the profile, it is squared
    depth: float
        (depth) length of the bar, the extrusion 
    thick: float
        Thickness of the side
    slot: float
        Width of the rail slot
    insquare: float
        Width of the inner square
    indiam: float
        Diameter of the inner hole. If 0, there is no hole
    xtr_d: float
        If >0 it will be that extra depth (length) on the direction of axis_d
    xtr_nd: float
        If >0 it will be that extra depth (length) on the opositve direction of
        axis_d
        can be V0 if pos_h = 0
    axis_d : FreeCAD.Vector
        Axis along the length (depth) direction
    axis_w : FreeCAD.Vector
        Axis along the width direction
    axis_h = axis on the other width direction (perpendicular)
        Axis along the width direction
    pos_d: int
        Location of pos along axis_d (see drawing)

            * 0: start point, counting xtr_nd,
               if xtr_nd == 0 -> pos_d 0 and 1 will be the same
            * 1: start point, not counting xtr_nd
            * 2: middle point not conunting xtr_nd and xtr_d
            * 3: middle point conunting xtr_nd and xtr_d
            * 4: end point, not counting xtr_d
            * 5: end point considering xtr_d

    pos_w: int
        Location of pos along axis_w (see drawing). Symmetric, negative indexes
        means the other side

            * 0: at the center of symmetry
            * 1: at the inner square
            * 2: at the interior side of the outer part of the rail (thickness of the4           side
            * 3: at the end of the profile along axis_w

    pos_h: int
        Same as pos_w 
    pos : FreeCAD.Vector
        Position of point defined by pos_d, pos_w, pos_h
   
    Attributes:
    -----------
    pos_o: FreeCAD.Vector
        origin, at pos_d=pos_w=pos_h = 0
        Shown in the drawing with a o

    ::

            axis_h
            :               xtr_nd       depth       xtr_d
            :                   .+..........+.........+..
            :                   :  :                :   :
         _  :  _                :__:________________:___:
        |_|_:_|_|               |_______________________|
          | o.|........ axis_w  o                       |....... axis_d
         _|___|_                |_______________________| 
        |_|   |_|               |_______________________|
            0 123               0  1        23      4   5 
              |||               :  :        ::      :   end
              || end            :  :        ::     end not counting xtr_d
              ||                :  :        : 
              ||                :  :        : middle point considering total
              | thickness       :  :        :  length (xtr_nd + depth + xtr_d)
              |                 :  :        :
               inner square     :  :         middle point considering depth only
                                :  :
                                :   start point, not counting xtr_nd
                                :
                                 start point, counting xtr_nd


         :______:  :______:
         |    __|  |__    |
         | |\ \      / /| |
         |_| \ \____/ / |_| ...........
             |        | ......        insquare
             |  (  )  | ......indiam  :
          _  |  ____  | ..............:
         | | / /    \ \ | |
         | |/ /_    _\ \| | .... 
         |______|  |______| ....thick
                  0   1 2 3   pos_w = pos_h
   
   
    """

    def __init__(self, depth,
                 aluprof_dict,
                 xtr_d=0, xtr_nd=0,
                 axis_d=VX, axis_w=VY, axis_h=V0,
                 pos_d=0, pos_w=0, pos_h=0,
                 pos=V0,
                 model_type=1,  # dimensional model
                 name=None):
        
        width = aluprof_dict['w']
        depth = depth
        thick = aluprof_dict['t']
        slot = aluprof_dict['slot']
        insquare = aluprof_dict['insq']
        indiam = aluprof_dict['indiam']

        # either axis_w or axis_h can be V0, but not both
        if (axis_w is None) or (axis_w == V0):
            if (axis_h is None) or (axis_h == V0):
                logger.error('Either axis_w or axis_h must be defined')
                logger.warning('getting a random perpendicular verctor')
                axis_w = fcfun.get_fc_perpend1(axis_d)
            else:
                axis_w = axis_h.cross(axis_d)

        if (axis_h is None) or (axis_h == V0):
            axis_h = axis_d.cross(axis_w)

        if name is None:
            name = ('aluprof_w' + str(int(aluprof_dict['w']))
                    + 'l_' + str(int(xtr_nd + depth + xtr_d)))

        Obj3D.__init__(self, axis_d, axis_w, axis_h, name=name)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self, i):
                setattr(self, i, values[i])
        
        self.pos = FreeCAD.Vector(0, 0, 0)
        self.position = pos

        self.d0_cen = 0
        self.w0_cen = 1  # symmetric
        self.h0_cen = 1  # symmetric

        # total length (depth)
        self.tot_d = xtr_nd + depth + xtr_d

        # vectors from the origin to the points along axis_d:
        self.d_o[0] = V0  # origin
        self.d_o[1] = self.vec_d(xtr_nd)  # if xtr_nd= 0: same as d_o[0]
        # middle point, not considering xtr_nd and xtr_d
        self.d_o[2] = self.vec_d(xtr_nd + depth/2.)
        # middle point considering xtr_nd and xtr_d
        self.d_o[3] = self.vec_d(self.tot_d / 2.)
        self.d_o[4] = self.vec_d(xtr_nd + depth)
        self.d_o[5] = self.vec_d(self.tot_d)

        # vectors from the origin to the points along axis_w:
        # symmetric: negative
        self.w_o[0] = V0  # center: origin
        self.w_o[1] = self.vec_w(-insquare/2.)
        self.w_o[2] = self.vec_w(-(width/2. - thick))
        self.w_o[3] = self.vec_w(-width/2.)

        # vectors from the origin to the points along axis_h:
        # symmetric: negative
        self.h_o[0] = V0  # center: origin
        self.h_o[1] = self.vec_h(-insquare/2.)
        self.h_o[2] = self.vec_h(-(width/2. - thick))
        self.h_o[3] = self.vec_h(-width/2.)

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        shp_alu_wire = fcfun.shp_aluwire_dir(width, thick, slot, insquare,
                                             fc_axis_x=self.axis_w,
                                             fc_axis_y=self.axis_h,
                                             ref_x=1,  # pos_o is centered
                                             ref_y=1,  # pos_o is centered
                                             pos=self.pos_o)

        # make a face of the wire
        shp_alu_face = Part.Face(shp_alu_wire)
        # inner hole
        if indiam > 0:
            hole = Part.makeCircle(indiam/2.,   # Radius
                                   self.pos_o,  # Position
                                   self.axis_d)  # direction
            wire_hole = Part.Wire(hole)
            face_hole = Part.Face(wire_hole)
            shp_alu_face = shp_alu_face.cut(face_hole)

        # extrude it
        dir_extrud = DraftVecUtils.scaleTo(self.axis_d, self.tot_d)
        shp_aluprof = shp_alu_face.extrude(dir_extrud)

        self.shp = shp_aluprof

        super().create_fco()
        # Need to set first in (0,0,0) and after that set the real placement.
        # This enable to do rotations without any issue
        self.fco.Placement.Base = FreeCAD.Vector(0, 0, 0)
        self.fco.Placement.Base = self.position


class LinGuideBlock (Obj3D):
    """ 
    Integration of a ShpLinGuideBlock object into a PartLinGuideBlock
    object, so it is a FreeCAD object that can be visualized in FreeCAD
    Instead of using all the arguments of ShpLinGuideBlock, it will use
    a dictionary

   ::

                       axis_h
                          :
                          :
              ____________3_____________.........................         
             |::|         2          |::|...bolt_l   :          :
             |  |     ____1____      |  |            :          :+linguide_h
             |  |    |    :    |     |  |            :+ block_h :
             |  |     \   :   /      |  |            :          :
             |__|_____/   o   \______|__|............:..........:..> axis_w
               :     :         :      :                         :
               :     :         :      :                         :
               :     :....4....:      :.........................:
               :          +           :
               :       rail_w         :
               :                      :
               :......................:
                          +
                      bolt_wsep
             
                        
                        axis_d (direction of the rail)
                          :
                          :
                 _________3_________ ....................
              __|____:____2____:____|__  ...            :
             |       :         :       |    :           :
             | 0     :    1    :     0 |    :           :
             | :     :         :       |    :           :
             | :     :         :       |    :           :
             | :     :    o    1    32 4.......................> axis_w
             | + bolt_dsep     :       |    :           :
             | :     :         :       |    + block_ds  :
             | 0     :         :     0 |    :           :+ block_d
             |_______:_________:_______|....:           :
             :  |____:_________:____|   ................:
             :  :                  :  :
             :  :.... block_ws ....:  :
             :                        :
             :....... block_w ........:


    Parameters
    ----------
    block_dict: dictionary
        Dictionary with the information about the block
    rail_dict: dictionary
        Dictionary with the information about the rail,
        it is not necessary, but if not provided, the block will not have
        the rail hole
    axis_d: FreeCAD.Vector
        The axis along the depth (length) of the block (and rail) 
    axis_w: FreeCAD.Vector
        The axis along the width of the block
    axis_h: FreeCAD.Vector
        The axis along the height of the block, pointing up
    pos_d: int
        Location of pos along axis_d (see drawing). Symmetric, negative indexes
        means the other side

            * 0: at the center (symmetric)
            * 1: at the bolt hole
            * 2: at the end of the smaller part of the block
            * 3: at the end of the end of the block

    pos_w: int
        Location of pos along axis_w (see drawing). Symmetric, negative indexes
        means the other side
        
            * 0: at the center of symmetry
            * 1: at the inner hole of the rail
            * 2: at the bolt holes (it can be after the smaller part of the block)
            * 3: at the end of the smaller part of the block
            * 4: at the end of the end of the block

    pos_h: int
        Location of pos along axis_h (see drawing)
        
            * 0: at the bottom (could make more sense to have 0 at the top instead
            * 1: at the top of the rail hole
            * 2: at the bottom of the bolt holes, if thruholes, same as 0
            * 3: at the top end
            * 4: at the bottom of the rail (not the block), if the rail has been
              defined

    pos: FreeCAD.Vector
        Position at the point defined by pos_d, pos_w, pos_h

    """
    def __init__(self, block_dict, rail_dict,
                 axis_d=VX, axis_w=V0, axis_h=VZ,
                 pos_d=0, pos_w=0, pos_h=0,
                 pos=V0,
                 model_type=1,  # dimensional model
                 name=None):

        self.pos = FreeCAD.Vector(0, 0, 0)
        self.position = pos

        if name is None:
            self.name = block_dict['name'] + '_block'

        if rail_dict is None:
            self.rail_h = 0
            self.rail_w = 0
        else:
            self.rail_h = rail_dict['rh']
            self.rail_w = rail_dict['rw']

        if (axis_w is None) or (axis_w == V0):
            axis_w = axis_h.cross(axis_d)

        Obj3D.__init__(self, axis_d, axis_w, axis_h, self.name)

        self.block_d = block_dict['bl']
        self.block_ds = block_dict['bls']
        self.block_w = block_dict['bw']
        self.block_ws = block_dict['bws']
        self.block_h = block_dict['bh']

        self.linguide_h = block_dict['lh']

        self.bolt_dsep = block_dict['boltlsep']
        self.bolt_wsep = block_dict['boltwsep']
        self.bolt_d = block_dict['boltd']
        self.bolt_l = block_dict['boltl']

        linguide_h = block_dict['lh']

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self, i):
                setattr(self, i, values[i])

        self.d0_cen = 1  # symmetric
        self.w0_cen = 1  # symmetric
        self.h0_cen = 0

        if self.bolt_l == 0:  # thruhole
            self.bolt_l = self.block_h
            self.thruhole = 1
        else:
            self.thruhole = 0

        if self.rail_h == 0 or linguide_h == 0:
            self.rail_h = 0
            self.linguide_h = 0
            self.rail_ins_h = 0
            self.rail_bot_h = 0
        else:
            self.rail_ins_h = self.block_h - (self.linguide_h - self.rail_h)
            self.rail_bot_h = self.rail_h - self.rail_ins_h

        # vectors from the origin to the points along axis_d:
        self.d_o[0] = V0  # Origin (center symmetric)
        self.d_o[1] = self.vec_d(-self.bolt_dsep/2.)
        self.d_o[2] = self.vec_d(-self.block_ds/2.)
        self.d_o[3] = self.vec_d(-self.block_d/2.)
 
        # vectors from the origin to the points along axis_w:
        self.w_o[0] = V0  # Origin (center symmetric)
        self.w_o[1] = self.vec_w(-self.rail_w/2.)
        self.w_o[2] = self.vec_w(-self.bolt_wsep/2.)
        self.w_o[3] = self.vec_w(-self.block_ws/2.)
        self.w_o[4] = self.vec_w(-self.block_w/2.)
 
        # vectors from the origin to the points along axis_h:
        # could make more sense to have the origin at the top
        self.h_o[0] = V0  # Origin at the bottom
        self.h_o[1] = self.vec_h(self.rail_ins_h)
        self.h_o[2] = self.vec_h(self.block_h - self.bolt_l)
        self.h_o[3] = self.vec_h(self.block_h)
        self.h_o[4] = self.vec_h(-self.rail_bot_h)
 
        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        # the main block
        shp_mblock = fcfun.shp_box_dir(box_w=self.block_w,
                                       box_d=self.block_ds,
                                       box_h=self.block_h,
                                       fc_axis_w=self.axis_w,
                                       fc_axis_d=self.axis_d,
                                       fc_axis_h=self.axis_h,
                                       cw=1, cd=1, ch=0,
                                       pos=self.pos_o)

        # the extra block
        shp_exblock = fcfun.shp_box_dir(box_w=self.block_ws,
                                        box_d=self.block_d,
                                        box_h=self.block_h,
                                        fc_axis_w=self.axis_w,
                                        fc_axis_d=self.axis_d,
                                        fc_axis_h=self.axis_h,
                                        cw=1, cd=1, ch=0,
                                        pos=self.pos_o)

        # fusion of these blocks
        shp_block = shp_mblock.fuse(shp_exblock)

        holes_list = []

        # rail hole:
        if self.rail_h > 0 and self.rail_w > 0:
            wire_rail = fcfun.wire_lgrail(rail_w=self.rail_w,
                                          rail_h=self.rail_h,
                                          axis_w=self.axis_w,
                                          axis_h=self.axis_h,
                                          pos_w=0, pos_h=0,
                                          pos=self.get_pos_h(4))

            face_rail = Part.Face(wire_rail)
            shp_rail = fcfun.shp_extrud_face(face=face_rail,
                                             length=self.block_d + 2,
                                             vec_extr_axis=self.axis_d,
                                             centered=1)

            # Part.show(shp_rail)
            holes_list.append(shp_rail)

        # bolt holes:
        for d_i in (-1, 1):  # positions of the holes along axis_d
            for w_i in (-2, 2):  # positions of the holes along axis_w
                shp_bolt = fcfun.shp_cylcenxtr(r=self.bolt_d/2.,
                                               h=self.bolt_l,
                                               normal=axis_h,
                                               ch=0,
                                               xtr_top=1,
                                               xtr_bot=self.thruhole,
                                               pos=self.get_pos_dwh(d_i, w_i, 2))
                holes_list.append(shp_bolt)

        shp_holes = fcfun.fuseshplist(holes_list)
        shp_block = shp_block.cut(shp_holes)
        shp_block = shp_block.removeSplitter()

        self.shp = shp_block
        super().create_fco(self.name)
        # Need to set first in (0,0,0) and after that set the real placement.
        # This enable to do rotations without any issue
        self.fco.Placement.Base = FreeCAD.Vector(0, 0, 0)
        self.fco.Placement.Base = self.position


class LinGuideRail (Obj3D):
    """ Creates a shape of a linear guide rail
    The linear guide rail has a dent, but it is just to show the shape, 
    the dimensions are not exact
    ::

                      axis_h
                        :
                        :
                        :
                        :bolth_d
                    ....:.+...
                   :    :    :
                ___:____3____:___...................
               |   :         :   |    :bolth_h     :
               |   :....2....:   |....:            :
                \     :   :     /   A little dent to see that it is a rail
                /     : 1 :     \ .....            :
               |      :   :      |     :           :+ rail_h
               |      :   :      |     + rail_h/2. :
               |      :   :      |     :           :
               |______:_o_:______|.....:...........:...... axis_w
               :      : 0 : 1    2
               :      :   :      :
               :      :...:      :
               :      bolt_d     :
               :                 :
               :.................:
                        +
                     rail_w


                     bolt_wsep: if 0, only one hole (common)
                     ...+...
                    :       :
               _________o_________.....................
               |:               :|    :                :
               |:               :|    :+ boltend_sep   :
               |:  ( )  1  ( )  :|----                 :
               |:               :|    :                :
               |:               :|    :+ bolt_lsep     :
               |:               :|    :                :
               |:               :|    :                :+ rail_d
               |:      ( )      :|----                 :
               |:       2       :|     only one bolt (either case, not like this
               |:               :|                     :
               |:               :|                     :
               |:               :|                     :
               |:      (3)      :|                     :
               |:               :|                     :
               |:               :|                     :
               |:_______4_______:|.....................:...axis_w
                        :
                        :
                        :
                        :
                        v
                      axis_d


    Parameters:
    -----------
    rail_d : float
        Length (depth) of the rail
    rail_w : float
        Width of the rail
    rail_h : float
        Height of the rail
    bolt_lsep : float
        Separation between bolts on the depth (length) dimension
    bolt_wsep : float
        Separation between bolts on the width dimension,

            * 0: there is only one bolt

    bolt_d : float
        Diameter of the hole for the bolt
    bolth_d : float
        Diameter of the hole for the head of the bolt
    bolth_h : float
        Height of the hole for the head of the bolt
    boltend_sep : float
        Separation on one end, from the bolt to the end

            * 0: evenly distributed

    axis_d : FreeCAD.Vector
        The axis along the depth (length) of the rail 
    axis_w : FreeCAD.Vector
        The axis along the width of the rail
    axis_h : FreeCAD.Vector
        The axis along the height of the rail, pointing up
    pos_d : int
        Location of pos along axis_d (see drawing)

            * 0: at the beginning of the rail
            * 1: at the first bolt hole
            * 2: at the middle of the rail (not necessary at a bolt hole)
            * 3: at the last bolt hole
            * 4: at the end of the rail

    pos_w : int
        Location of pos along axis_w (see drawing). Symmetric, negative indexes
        means the other side

        * 0: at the center of symmetry
        * 1: at the bolt holes (only make sense if there are 2 bolt holes)
             otherwise it will be like pos_w = 0
        * 2: at the end of the rail along axis_w

    pos_h : int
        Location of pos along axis_h (see drawing)

        *   0: at the bottom
        *   1: at the middle (it is not a specific place)
        *   1: at the bolt head
        *   3: at the top end

    pos : FreeCAD.Vector
        Position at the point defined by pos_d, pos_w, pos_h

    """

    def __init__(self, rail_d,
                 rail_dict,
                 boltend_sep=0,
                 axis_d=VX, axis_w=V0, axis_h=VZ,
                 pos_d=0, pos_w=0, pos_h=0,
                 pos=V0,
                 model_type=1,  # dimensional model,
                 name=None):

        if name is None:
            self.name = rail_dict['name']
        else:
            self.name = name
        
        if boltend_sep == 0:
            boltends = 0
        elif boltend_sep < 0:
            boltends = rail_dict['boltend_sep']
        else:
            boltends = boltend_sep
        
        rail_w = rail_dict['rw'],
        rail_h = rail_dict['rh'],
        bolt_lsep = rail_dict['boltlsep'],
        bolt_wsep = rail_dict['boltwsep'],
        bolt_d = rail_dict['boltd'],
        bolth_d = rail_dict['bolthd'],
        bolth_h = rail_dict['bolthh'],

        if (axis_w is None) or (axis_w == V0):
            axis_w = axis_h.cross(axis_d)

        Obj3D.__init__(self, axis_d, axis_w, axis_h, self.name)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self, i):
                setattr(self, i, values[i])

        self.d0_cen = 0
        self.w0_cen = 1  # symmetric
        self.h0_cen = 0

        # calculation of the number of bolt holes along axis_d
        if boltend_sep != 0:
            nbolt_l = (rail_d - boltend_sep) // bolt_lsep  # integer division
            rail_rem = rail_d - boltend_sep - nbolt_l * bolt_lsep 
            if rail_rem > bolth_d:
                # one bolt more
                nbolt_l = nbolt_l + 1
            self.boltend_sep = boltend_sep
        else:  # leave even distance
            # number of bolt lines, on the depth (length) axis
            nbolt_l = rail_d // bolt_lsep  # integer division
            # don't use % in case is not int
            rail_rem = rail_d - nbolt_l * bolt_lsep 
            if rail_rem > 2 * bolth_d:
                # one bolt more
                nbolt_l = nbolt_l + 1
                # separation between the bolt and the end
                self.boltend_sep = rail_rem / 2.
            else:
                self.boltend_sep = (bolt_lsep + rail_rem) / 2.
        self.nbolt_l = int(nbolt_l)

        # vectors from the origin to the points along axis_d:
        self.d_o[0] = V0  # origin
        self.d_o[1] = self.vec_d(self.boltend_sep)
        self.d_o[2] = self.vec_d(rail_d/2.)
        self.d_o[3] = self.vec_d((self.nbolt_l-1)*bolt_lsep + self.boltend_sep)
        self.d_o[4] = self.vec_d(rail_d)

        # vectors from the origin to the points along axis_w:
        # symmetric: negative
        self.w_o[0] = V0  # base: origin
        self.w_o[1] = self.vec_w(-bolt_wsep/2.)  # if 0: same as w_o[0]
        self.w_o[2] = self.vec_w(-rail_w/2.)

        # vectors from the origin to the points along axis_h:
        self.h_o[0] = V0  # base: origin
        self.h_o[1] = self.vec_h(rail_h/2.)
        self.h_o[2] = self.vec_h(rail_h - bolth_h)
        self.h_o[3] = self.vec_h(rail_h)

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        wire_rail = fcfun.wire_lgrail(rail_w=rail_w,
                                      rail_h=rail_h,
                                      axis_w=self.axis_w,
                                      axis_h=self.axis_h,
                                      pos_w=0, pos_h=0,
                                      pos=self.pos_o)

        # make a face of the wire 
        shp_face_rail = Part.Face(wire_rail)
        shp_plainrail = shp_face_rail.extrude(self.vec_d(rail_d))

        holes_list = []
        # bolt holes
        bolthole_pos = self.get_pos_dwh(1, 0, 3)
        for i in range(0, self.nbolt_l):
            if bolt_wsep == 0:  # just one bolt
                shp_bolt = fcfun.shp_bolt_dir(r_shank=bolt_d/2.,
                                              l_bolt=rail_h,
                                              r_head=bolth_d/2.,
                                              l_head=bolth_h,
                                              xtr_head=1, xtr_shank=1,
                                              support=0,
                                              fc_normal=self.axis_h.negative(),
                                              pos_n=0, pos=bolthole_pos)
                holes_list.append(shp_bolt)
            else:
                for i in (-1, 1):
                    bolthole_pos_i = bolthole_pos + self.get_pos_w(i)
                    shp_bolt = fcfun.shp_bolt_dir(r_shank=bolt_d/2.,
                                                  l_bolt=rail_h,
                                                  r_head=bolth_d/2.,
                                                  l_head=bolth_h,
                                                  xtr_head=1, xtr_shank=1,
                                                  support=0,
                                                  fc_normal=self.axis_h.negative(),
                                                  pos_n=0, pos=bolthole_pos_i)
                    holes_list.append(shp_bolt)
            bolthole_pos = bolthole_pos + self.vec_d(bolt_lsep)

        shp_holes = fcfun.fuseshplist(holes_list)
        shp_rail = shp_plainrail.cut(shp_holes)
        shp_rail = shp_rail.removeSplitter()

        self.shp = shp_rail
        super().create_fco(self.name)
        # Need to set first in (0,0,0) and after that set the real placement.
        # This enable to do rotations without any issue
        self.fco.Placement.Base = FreeCAD.Vector(0, 0, 0)
        self.fco.Placement.Base = self.position


# ---------- class LinBearing ----------------------------------------
# Creates a cylinder with a thru-hole object
# it also creates a copy of the cylinder without the hole, but a little
# bit larger, to be used to cut other shapes where this cylinder will be
# This will be useful for linear bearing/bushings container
#     r_ext: external radius,
#     r_int: internal radius,
#     h: height
#     name
#     axis: 'x', 'y' or 'z'
#           'x' will along the x axis
#           'y' will along the y axis
#           'z' will be vertical
#     h_disp: displacement on the height.
#             if 0, the base of the cylinder will be on the plane
#             if -h/2: the plane will be cutting h/2
#     r_tol : What to add to r_ext for the container cylinder
#     h_tol : What to add to h for the container cylinder, half on each side

# ARGUMENTS:
# bearing: the fco (FreeCAD object) of the bearing
# bearing_cont: the fco (FreeCAD object) of the container bearing.
#               to cut it

# base_place: position of the 3 elements: All of them have the same base
#             position.
#             It is (0,0,0) when initialized, it has to be changed using the
#             function base_place

class LinBearing (Obj3D):

    def __init__(self,
                 r_ext,
                 r_int,
                 h,
                 name,
                 axis='z',
                 h_disp=0,
                 r_tol=0,
                 h_tol=0):

        self.base_place = (0, 0, 0)
        self.r_ext = r_ext
        self.r_int = r_int
        self.h = h
        self.name = name
        self.axis = axis
        self.h_disp = h_disp
        self.r_tol = r_tol
        self.h_tol = h_tol
        Obj3D.__init__(self, axis_d=axis, axis_w=None, axis_h=None, name=name)
        bearing = fcfun.addCylHole(r_ext=r_ext,
                                   r_int=r_int,
                                   h=h,
                                   name=name,
                                   axis=axis,
                                   h_disp=h_disp)
        self.bearing = bearing

        bearing_cont = fcfun.addCyl_pos(r=r_ext + r_tol,
                                        h=h + h_tol,
                                        name=name + "_cont",
                                        axis=axis,
                                        h_disp = h_disp - h_tol/2.0)
        # Hide the container
        self.bearing_cont = bearing_cont
        if bearing_cont.ViewObject is None:
            bearing_cont.ViewObject.Visibility = False

    # Move the bearing and its container
    def BasePlace(self, position=(0, 0, 0)):
        self.base_place = position
        self.bearing.Placement.Base = FreeCAD.Vector(position)
        self.bearing_cont.Placement.Base = FreeCAD.Vector(position)


class NemaMotor (Obj3D):
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

    def __init__(self,
                 nema_size=17,
                 base_l=32.,
                 shaft_l=24.,
                 shaft_r=0,
                 circle_r=11.,
                 circle_h=2.,
                 chmf_r=1,
                 rear_shaft_l=0,
                 bolt_depth=3.,
                 bolt_out=2,
                 cut_extra=0,
                 axis_d=VX,
                 axis_w=None,
                 axis_h=VZ,
                 pos_d=0,
                 pos_w=0,
                 pos_h=1,
                 pos=V0,
                 name=None):

        if name is None:
            name = 'nema' + str(nema_size) + '_motor_l' + str(int(base_l))
        
        self.name = name

        if (axis_w is None) or (axis_w == V0):
            axis_w = axis_h.cross(axis_d)

        Obj3D.__init__(self, axis_d, axis_w, axis_h, self.name)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self, i):
                setattr(self, i, values[i])

        self.motor_w = kcomp.NEMA_W[nema_size]
        if shaft_r == 0:
            self.shaft_d = kcomp.NEMA_SHAFT_D[nema_size]
            self.shaft_r = self.shaft_d / 2.
            shaft_r = self.shaft_r

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
        self.d0_cen = 1  # symmetrical
        self.w0_cen = 1  # symmetrical

        # vectors from the origin to the points along axis_h:
        self.h_o[0] = V0  # base of the shaft: origin
        self.h_o[1] = self.vec_h(self.circle_h)
        self.h_o[2] = self.vec_h(self.shaft_l)  # includes circle_h
        self.h_o[3] = self.vec_h(-bolt_depth)
        self.h_o[4] = self.vec_h(-self.base_l)
        self.h_o[5] = self.vec_h(-self.base_l - self.rear_shaft_l)

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
        shp_base = fcfun.shp_box_dir(box_w=self.motor_w + 2*cut_extra,
                                     box_d=self.motor_w + 2*cut_extra,
                                     box_h=self.base_l,
                                     fc_axis_w=self.axis_w,
                                     fc_axis_d=self.axis_d,
                                     fc_axis_h=self.axis_h,
                                     cw=1, cd=1, ch=0,
                                     pos=self.get_pos_h(4))

        shp_base = fcfun.shp_filletchamfer_dir(shp_base, self.axis_h,
                                               fillet=0, radius=chmf_r)
        shp_base = shp_base.removeSplitter()

        fuse_list = []
        holes_list = []

        # --------- bolts (holes or extensions if cut_extra > 0)
        for pt_d in (-3, 3):
            for pt_w in (-3, 3):
                if cut_extra == 0:  # there will be holes for the bolts
                    # pos_h=3 is at the end of the hole for the bolts
                    bolt_pos = self.get_pos_dwh(pt_d, pt_w, 3)
                    shp_hole = fcfun.shp_cylcenxtr(r=self.nemabolt_r,
                                                   h=bolt_depth,
                                                   normal=self.axis_h,
                                                   ch=0,
                                                   xtr_top=1,
                                                   xtr_bot=0,
                                                   pos=bolt_pos)
                    holes_list.append(shp_hole)
                else:  # the bolts will protude to make holes in the shape to cut
                    # pos_h=0 is at the the base of the shaft
                    bolt_pos = self.get_pos_dwh(pt_d, pt_w, 0)
                    shp_hole = fcfun.shp_cylcenxtr(r=self.nemabolt_r,
                                                   h=bolt_out,
                                                   normal=self.axis_h,
                                                   ch=0,
                                                   xtr_top=0,
                                                   xtr_bot=1,
                                                   pos=bolt_pos)
                    fuse_list.append(shp_hole)

        if cut_extra == 0:
            shp_holes = fcfun.fuseshplist(holes_list)
            shp_base = shp_base.cut(shp_holes)
            shp_base = shp_base.removeSplitter()

        # -------- circle (flat cylinder) at the base of the shaft
        # could add cut_extra to circle_h or circle_r, but it can be 
        # set in the arguments
        if circle_r > 0 and circle_h > 0:
            shp_circle = fcfun.shp_cylcenxtr(r=circle_r,
                                             h=circle_h,
                                             normal=self.axis_h,
                                             ch=0,  # not centered
                                             xtr_top=0,  # no extra at top
                                             xtr_bot=1,  # extra to fuse
                                             pos=self.pos_o)
            fuse_list.append(shp_circle)

        # ------- Shaft
        shp_shaft = fcfun.shp_cylcenxtr(r=self.shaft_r,
                                        h=self.shaft_l,
                                        normal=self.axis_h,
                                        ch=0,  # not centered
                                        xtr_top=0,  # no extra at top
                                        xtr_bot=1,  # extra to fuse
                                        # shaft length stats from the base
                                        # not from the circle
                                        pos=self.pos_o)
        fuse_list.append(shp_shaft)

        if rear_shaft_l > 0:
            shp_rearshaft = fcfun.shp_cylcenxtr(r=self.shaft_r,
                                                h=self.rear_shaft_l,
                                                normal=self.axis_h,
                                                ch=0,  # not centered
                                                xtr_top=1,  # to fuse
                                                xtr_bot=0,  # no extra at bottom
                                                pos=self.get_pos_h(5))

            fuse_list.append(shp_rearshaft)
        
        shp_motor = shp_base.multiFuse(fuse_list)
        shp_motor = shp_motor.removeSplitter()
        self.shp = shp_motor
        
        super().create_fco(self.name)
        # Need to set first in (0,0,0) and after that set the real placement.
        # This enable to do rotations without any issue
        self.fco.Placement.Base = FreeCAD.Vector(0, 0, 0)
        self.fco.Placement.Base = self.position


class GtPulley (Obj3D):
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
                 pitch=2.,
                 n_teeth=20,
                 toothed_h=7.5,
                 top_flange_h=1.,
                 bot_flange_h=0,
                 tot_h=16.,
                 flange_d=15.,
                 base_d=15.,
                 shaft_d=5.,
                 tol=0,
                 axis_d=None,
                 axis_w=None,
                 axis_h=VZ,
                 pos_d=0,
                 pos_w=0,
                 pos_h=0,
                 pos=V0,
                 model_type=1,  # dimensional model
                 name=None):

        if name is None:
            name = 'gt' + str(int(pitch)) + '_pulley_' + str(n_teeth)
        self.name = name
        
        # First the shape is created

        if (((axis_d is None) or (axis_d == V0)) and
           ((axis_w is None) or (axis_w == V0))):
            # both are null, we create a random perpendicular vectors
            axis_d = fcfun.get_fc_perpend1(axis_h)
            axis_w = axis_h.cross(axis_d)
        else:
            if(axis_d is None) or (axis_d == V0):
                axis_d = axis_w.cross(axis_h)
            elif(axis_w is None) or (axis_w == V0):
                axis_w = axis_h.cross(axis_d)
            # all axis are defined
      
        Obj3D.__init__(self, axis_d, axis_w, axis_h, self.name)

        if (top_flange_h > 0 or bot_flange_h > 0) and flange_d == 0:
            logger.debug("Flange height is not null, but diameter is null")
            logger.debug("Flange diameter will be the same as the base")
            flange_d = base_d
            self.flange_d = flange_d

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self, i):
                setattr(self, i, values[i])

        # belt dictionary:
        self.belt_dict = kcomp.GT[pitch]
        # diameters of the pulley:
        # pitch diameter, it is not on the pulley, but outside, on the belt
        self.pitch_d = n_teeth * pitch / math.pi
        self.pitch_r = self.pitch_d / 2.
        # out radius and diameter, diameter at the outer part of the teeth
        self.tooth_out_r = self.pitch_r - self.belt_dict['PLD']
        self.tooth_out_d = 2 * self.tooth_out_r
        # inner radius and diameter, diameter at the inner part of the teeth
        self.tooth_in_r = self.tooth_out_r - self.belt_dict['TOOTH_H']
        self.tooth_in_d = 2 * self.tooth_in_r

        self.base_r = base_d / 2.
        self.shaft_r = shaft_d / 2.
        self.flange_r = flange_d / 2.

        # height of the base, without the toothed part and the flange
        self.base_h = tot_h - toothed_h - top_flange_h - bot_flange_h

        self.h0_cen = 0
        self.d0_cen = 1  # symmetrical
        self.w0_cen = 1  # symmetrical

        # vectors from the origin to the points along axis_h:
        self.h_o[0] = V0
        self.h_o[1] = self.vec_h(self.base_h)
        self.h_o[2] = self.vec_h(self.base_h + bot_flange_h)
        self.h_o[3] = self.vec_h(self.base_h + bot_flange_h + toothed_h/2.)
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
        shp_tooth_cyl = fcfun.shp_cylhole_gen(r_out=self.tooth_out_r,
                                              r_in=self.shaft_r + tol,
                                              h=self.toothed_h,
                                              axis_h=self.axis_h,
                                              pos_h=1,  # position at the bottom
                                              xtr_top=top_flange_h/2.,
                                              xtr_bot=xtr_bot,
                                              pos=self.get_pos_h(2))
        shp_fuse_list.append(shp_tooth_cyl)
        if self.bot_flange_h > 0:
            # same width
            if self.flange_d == self.base_d:
                shp_base_flg_cyl = fcfun.shp_cylholedir(r_out=self.base_r,
                                                        r_in=self.shaft_r + tol,
                                                        h=self.base_h + self.bot_flange_h,
                                                        normal=self.axis_h,
                                                        pos=self.pos_o)
                shp_fuse_list.append(shp_base_flg_cyl)
            else:
                shp_base_cyl = fcfun.shp_cylholedir(r_out=self.base_r,
                                                    r_in=self.shaft_r + tol,
                                                    h=self.base_h,
                                                    normal=self.axis_h,
                                                    pos=self.pos_o)
                shp_bot_flange_cyl = fcfun.shp_cylholedir(r_out=self.flange_r,
                                                          r_in=self.shaft_r + tol,
                                                          h=self.bot_flange_h,
                                                          normal=self.axis_h,
                                                          pos=self.get_pos_h(1))
                shp_fuse_list.append(shp_base_cyl)
                shp_fuse_list.append(shp_bot_flange_cyl)
        else:  # no bottom flange
            shp_base_cyl = fcfun.shp_cylholedir(r_out=self.base_r,
                                                r_in=self.shaft_r + tol,
                                                h=self.base_h,
                                                normal=self.axis_h,
                                                pos=self.pos_o)
            shp_fuse_list.append(shp_base_cyl)
        if self.top_flange_h > 0:
            shp_top_flange_cyl = fcfun.shp_cylholedir(r_out=self.flange_r,
                                                      r_in=self.shaft_r + tol,
                                                      h=self.top_flange_h,
                                                      normal=self.axis_h,
                                                      pos=self.get_pos_h(4))
            shp_fuse_list.append(shp_top_flange_cyl)

        shp_pulley = fcfun.fuseshplist(shp_fuse_list)

        shp_pulley = shp_pulley.removeSplitter()

        self.shp = shp_pulley

        super().create_fco(self.name)
        # Need to set first in (0,0,0) and after that set the real placement.
        # This enable to do rotations without any issue
        self.fco.Placement.Base = FreeCAD.Vector(0, 0, 0)
        self.fco.Placement.Base = self.position

        # normal axes to print without support
        self.prnt_ax = self.axis_h


class MisumiAlu30s6w8 (Obj3D):  # TODO
    """
    Creates a Misumi Aluminun Profile 30x30 Series 6 Width 8

    Parameters:
    -----------
    length: float
        the length of the profile
    name: str
        name of the FreeCAD object
    axis: FreeCAD.Vector

        * 'x' will along the x axis
        * 'y' will along the y axis
        * 'z' will be vertical

    cx: int

        * 0: if you want the coordinates to be referenced to the starting point of the x-axis
        * 1: if you want the coordinates referenced to the x center of the piece

    cy: int

        * 0: if you want the coordinates to be referenced to the starting point of the y-axis
        * 1 if you want the coordinates referenced to the y center of the piece

    cz: int

        * 0: if you want the coordinates to be referenced to the starting point of the z-axis
        * 1 if you want the coordinates referenced to the z center of the piece

    fco: int

        * 0: Create the shape
        * 1: Create freecad object

    """
    # filename of Aluminum profile sketch
    skfilename = "misumi_profile_hfs_serie6_w8_30x30.FCStd"
    ALU_W = 30.0
    ALU_Wh = ALU_W / 2.0  # half of it

    def __init__(self, length, name, axis=VX,
                 cx=False, cy=False, cz=False, fco=1):
        doc = FreeCAD.ActiveDocument
        self.length = length
        self.name = name
        self.axis = axis
        self.cx = cx
        self.cy = cy
        self.cz = cz
        # filepath
        path = os.getcwd()
        # logging.debug(path)
        self.skpath = path + '/../../freecad/comps/'
        doc_sk = FreeCAD.openDocument(self.skpath + self.skfilename)

        list_obj_alumprofile = []
        for obj in doc_sk.Objects:
            
            # if (hasattr(obj,'ViewObject') and obj.ViewObject.isVisible()
            #    and hasattr(obj,'Shape') and len(obj.Shape.Faces) > 0 ):
            #   # len(obj.Shape.Faces) > 0 to avoid sketches
            #    list_obj_alumprofile.append(obj)
            if len(obj.Shape.Faces) == 0:
                orig_alumsk = obj

        FreeCAD.ActiveDocument = doc
        self.Sk = doc.addObject("Sketcher::SketchObject", 'sk_' + name)
        self.Sk.Geometry = orig_alumsk.Geometry
        print(orig_alumsk.Geometry)
        print(orig_alumsk.Constraints)
        self.Sk.Constraints = orig_alumsk.Constraints
        self.Sk.ViewObject.Visibility = False

        FreeCAD.closeDocument(doc_sk.Name)
        FreeCAD.ActiveDocument = doc  # otherwise, clone will not work

        doc.recompute()

        # The sketch is on plane XY, facing Z
        if axis == VX:
            self.Dir = (length, 0, 0)
            # rotation on Y
            rot = FreeCAD.Rotation(VY, 90)
            if cx:
                xpos = - self.length / 2.0
            else:
                xpos = 0
            if cy:
                ypos = 0
            else:
                ypos = self.ALU_Wh  # half of the aluminum profile width
            if cz:
                zpos = 0
            else:
                zpos = self.ALU_Wh
        elif axis == VY:
            self.Dir = (0, length, 0)
            # rotation on X
            rot = FreeCAD.Rotation(VX, -90)
            if cx:
                xpos = 0
            else:
                xpos = self.ALU_Wh
            if cy:
                ypos = - self.length / 2.0
            else:
                ypos = 0
            if cz:
                zpos = 0
            else:
                zpos = self.ALU_Wh
        elif axis == VZ:
            self.Dir = (0, 0, length)
            # no rotation
            rot = FreeCAD.Rotation(VZ, 0)
            if cx:
                xpos = 0
            else:
                xpos = self.ALU_Wh
            if cy:
                ypos = 0
            else:
                ypos = self.ALU_Wh
            if cz:
                zpos = - self.length / 2.0
            else:
                zpos = 0
        else:
            logging.debug("wrong argument")
              
        self.Sk.Placement.Rotation = rot
        self.Sk.Placement.Base = FreeCAD.Vector(xpos, ypos, zpos)

        alu_extr = doc.addObject("Part::Extrusion", name)
        alu_extr.Base = self.Sk
        alu_extr.Dir = self.Dir
        alu_extr.Solid = True

        # if fco == 1:
        self.fco = alu_extr   # the FreeCad Object
        # super().create_fco(name)


class RectRndBar (Obj3D):  # TODO
    """
    Creates a rectangular bar with rounded edges, and with the possibility to be hollow

    Parameters:
    -----------
    Base: float
        the length of the base of the rectangle
    Height: float
        the length of the height of the rectangle
    Length: float
        the length of the bar, the extrusion 
    Radius: float
        the radius of the rounded edges (fillet)
    Thick: float
        the thickness of the bar (hollow bar)
        
        * If it is zero or larger than base or height, it will be full

    inrad_same: boolean

        * True: inradius = radius. When the radius is very small
        * False:  inradius = radius - thick 

    axis: str
        'x', 'y' or 'z' direction of the bar
        
        * 'x' will along the x axis
        * 'y' will along the y axis
        * 'z' will be vertical

    baseaxis: str
        'x', 'y' or 'z' in which axis the base is on. Cannot be the same as axis
    cx: int

        * 0: if you want the coordinates to be referenced to the starting point of the x-axis
        * 1 if you want the coordinates referenced to the x center of the piece

    cy: int

        * 0: if you want the coordinates to be referenced to the starting point of the y-axis
        * 1 if you want the coordinates referenced to the y center of the piece

    cz: int

        * 0: if you want the coordinates to be referenced to the starting point of the z-axis
        * 1 if you want the coordinates referenced to the z center of the piece

    """

    def __init__(self, base, height, length, radius, thick=0,
                 inrad_same=False, axis=VX,
                 baseaxis=VY, name="rectrndbar",
                 cx=False, cy=False, cz=False):
        doc = FreeCAD.ActiveDocument
        self.Base = base
        self.Height = height
        self.Length = length
        self.Radius = radius
        self.Thick = thick
        self.inrad_same = inrad_same
        self.name = name
        self.axis = axis
        self.baseaxis = baseaxis
        self.cx = cx
        self.cy = cy
        self.cz = cz

        self.inBase = base - 2 * thick
        self.inHeight = height - 2 * thick

        Obj3D.__init__(self,
                       axis_d=VX,
                       axis_w=None,
                       axis_h=None,
                       name=name)

        if thick == 0 or thick >= base or thick >= height:
            self.Thick = 0
            self.hollow = False
            self.inRad = 0  
            self.inrad_same = False  
            self.inBase = 0
            self.inHeight = 0
        else:
            self.hollow = True
            if inrad_same:
                self.inRad = radius
            else:
                if radius > thick:
                    self.inRad = radius - thick
                else:
                    self.inRad = 0  # a rectangle, with no rounded edges (inside)

        wire_ext = fcfun.shpRndRectWire(x=base, y=height, r=radius,
                                        zpos=length/2.0)
        face_ext = Part.Face(wire_ext)
        if self.hollow:
            wire_int = fcfun.shpRndRectWire(x=self.inBase,
                                            y=self.inHeight,
                                            r=self.inRad,
                                            zpos=length/2.0)
            face_int = Part.Face(wire_int)
            face = face_ext.cut(face_int)
        else:
            face = face_ext  # is not hollow

        self.face = face

        dir_extr = axis * length

        vrot = fcfun.calc_rot(baseaxis, axis)
        vdesp = fcfun.calc_desp_ncen(Length=self.Base,
                                     Width=self.Height,
                                     Height=self.Length,
                                     vec1=baseaxis, vec2=axis,
                                     cx=cx, cy=cy, cz=cz)

        face.Placement.Base = vdesp
        face.Placement.Rotation = vrot

        shp_extr = face.extrude(dir_extr)
        self.shp = shp_extr
        super().create_fco(name)


# ---------- class T8Nut ----------------------
# T8 Nut of a leadscrew
# nutaxis: where the nut is going to be facing
#          'x', '-x', 'y', '-y', 'z', '-z'
#
#           __
#          |__|
#          |__|
#    ______|  |_
#   |___________|
#   |___________|   ------- nutaxis = 'x'
#   |_______   _|
#          |__|
#          |__|
#          |__|
#
#             |
#              ------ this is the zero. Plane YZ=0

class T8Nut(Obj3D):  # TODO: fix
    NutL = kcomp.T8N_L
    FlangeL = kcomp.T8N_FLAN_L
    ShaftOut = kcomp.T8N_SHAFT_OUT
    LeadScrewD = kcomp.T8N_D_T8
    LeadScrewR = LeadScrewD / 2.0

    # Hole for the nut and the lead screw
    ShaftD = kcomp.T8N_D_SHAFT_EXT
    ShaftR = ShaftD / 2.0
    FlangeD = kcomp.T8N_D_FLAN
    FlangeR = FlangeD / 2.0
    # hole for the M3 bolts to attach the nut to the housing
    FlangeBoltHoleD = kcomp.T8N_BOLT_D
    FlangeBoltDmetric = int(kcomp.T8N_BOLT_D)
    # Diameter where the Flange Screws are located
    FlangeBoltPosD = kcomp.T8N_D_BOLT_POS

    def __init__(self, name, nutaxis='x'):
        doc = FreeCAD.ActiveDocument
        self.name = name
        self.nutaxis = nutaxis

        Obj3D.__init__(self,
                       axis_d=self.nutaxis,
                       axis_w=None,
                       axis_h=None,
                       name=self.name)

        flange_cyl = addCyl_pos(r=self.FlangeR,
                                h=self.FlangeL,
                                name="flange_cyl",
                                axis='z',
                                h_disp=- self.FlangeL)

        shaft_cyl = addCyl_pos(r=self.ShaftR,
                               h=self.NutL,
                               name="shaft_cyl",
                               axis='z',
                               h_disp=- self.NutL + self.ShaftOut)
        super().add_child(flange_cyl, 1, "flange_cyl")
        super().add_child(shaft_cyl, 1, "shaft_cyl")
        holes_list = []

        leadscrew_hole = addCyl_pos(r=self.LeadScrewR,
                                    h=self.NutL + 2,
                                    name="leadscrew_hole",
                                    axis='z',
                                    h_disp=- self.NutL + self.ShaftOut - 1)
        holes_list.append(leadscrew_hole)
        super().add_child(leadscrew_hole, 0, "leadscrew_hole")

        flangebolt_hole1 = addCyl_pos(r=self.FlangeBoltHoleD / 2.0,
                                      h=self.FlangeL + 2,
                                      name="flangebolt_hole1",
                                      axis='z',
                                      h_disp=- self.FlangeL - 1)
        flangebolt_hole1.Placement.Base.x = self.FlangeBoltPosD / 2.0
        super().add_child(flangebolt_hole1, 0, "flangebolt_hole1")
        holes_list.append(flangebolt_hole1)

        flangebolt_hole2 = addCyl_pos(r=self.FlangeBoltHoleD / 2.0,
                                      h=self.FlangeL + 2,
                                      name="flangebolt_hole2",
                                      axis='z',
                                      h_disp=- self.FlangeL - 1)
        flangebolt_hole2.Placement.Base.x = - self.FlangeBoltPosD / 2.0
        super().add_child(flangebolt_hole2, 0, "flangebolt_hole2")
        holes_list.append(flangebolt_hole2)

        flangebolt_hole3 = addCyl_pos(r=self.FlangeBoltHoleD / 2.0,
                                      h=self.FlangeL + 2,
                                      name="flangebolt_hole3",
                                      axis='z',
                                      h_disp=- self.FlangeL - 1)
        flangebolt_hole3.Placement.Base.y = self.FlangeBoltPosD / 2.0
        super().add_child(flangebolt_hole3, 0, "flangebolt_hole3")
        holes_list.append(flangebolt_hole3)

        flangebolt_hole4 = addCyl_pos(r=self.FlangeBoltHoleD / 2.0,
                                      h=self.FlangeL + 2,
                                      name="flangebolt_hole4",
                                      axis='z',
                                      h_disp=- self.FlangeL - 1)
        flangebolt_hole4.Placement.Base.y = - self.FlangeBoltPosD / 2.0
        super().add_child(flangebolt_hole4, 0, "flangebolt_hole4")
        holes_list.append(flangebolt_hole4)

        nut_holes = doc.addObject("Part::MultiFuse", "nut_holes")
        nut_holes.Shapes = holes_list

        nut_cyls = doc.addObject("Part::Fuse", "nut_cyls")
        nut_cyls.Base = flange_cyl
        nut_cyls.Tool = shaft_cyl

        if nutaxis == 'x':
            vrot = FreeCAD.Rotation(VY, 90)
        elif nutaxis == '-x':
            vrot = FreeCAD.Rotation(VY, -90)
        elif nutaxis == 'y':
            vrot = FreeCAD.Rotation(VX, -90)
        elif nutaxis == '-y':
            vrot = FreeCAD.Rotation(VX, 90)
        elif nutaxis == '-z':
            vrot = FreeCAD.Rotation(VX, 180)
        else:  # nutaxis =='z' no rotation
            vrot = FreeCAD.Rotation(VZ, 0)

        nut_cyls.Placement.Rotation = vrot
        nut_holes.Placement.Rotation = vrot

        t8nut = doc.addObject("Part::Cut", "t8nut")
        t8nut.Base = nut_cyls
        t8nut.Tool = nut_holes
        # recompute before color
        doc.recompute()
        t8nut.ViewObject.ShapeColor = fcfun.YELLOW

        self.fco = t8nut  # the FreeCad Object


# ---------- class T8NutHousing ----------------------
# Housing for a T8 Nut of a leadscrew
# nutaxis: where the nut is going to be facing
#          'x', '-x', 'y', '-y', 'z', '-z'
# boltface_axis: where the bolts are going to be facing
#          it cannot be the same axis as the nut
#          'x', '-x', 'y', '-y', 'z', '-z'
# cx, cy, cz, if it is centered on any of the axis

class T8NutHousing(Obj3D):
    Length = kcomp.T8NH_L
    Width = kcomp.T8NH_W
    Height = kcomp.T8NH_H

    # separation between the bolts that attach to the moving part
    BoltLenSep = kcomp.T8NH_BoltLSep
    BoltWidSep = kcomp.T8NH_BoltWSep

    # separation between the bolts to the end
    BoltLen2end = (Length - BoltLenSep) / 2
    BoltWid2end = (Width - BoltWidSep) / 2

    # Bolt dimensions, that attach to the moving part: M4 x 7
    BoltD = kcomp.T8NH_BoltD
    BoltR = BoltD / 2.0
    BoltL = kcomp.T8NH_BoltL + kcomp.TOL

    # Hole for the nut and the leadscrew
    ShaftD = kcomp.T8N_D_SHAFT_EXT + kcomp.TOL  # I don't know the tolerances
    ShaftR = ShaftD / 2.0
    FlangeD = kcomp.T8N_D_FLAN + kcomp.TOL  # I don't know the tolerances
    FlangeR = FlangeD / 2.0
    FlangeL = kcomp.T8N_FLAN_L + kcomp.TOL
    FlangeBoltD = kcomp.T8NH_FlanBoltD
    FlangeBoltR = FlangeBoltD / 2.0
    FlangeBoltL = kcomp.T8NH_FlanBoltL + kcomp.TOL
    # Diameter where the Flange Bolts are located
    FlangeBoltPosD = kcomp.T8N_D_BOLT_POS

    def __init__(self, name, nutaxis='x', screwface_axis='z',
                 cx=1, cy=1, cz=0):
        self.name = name
        self.nutaxis = nutaxis
        self.screwface_axis = screwface_axis
        self.cx = cx
        self.cy = cy
        self.cz = cz

        Obj3D.__init__(self, axis_d=self.nutaxis, axis_w=None, axis_h=None, name=self.name)

        doc = FreeCAD.ActiveDocument
        # centered so it can be rotated without displacement, and everything
        # will be in place
        housing_box = fcfun.addBox_cen(self.Length, self.Width, self.Height,
                                       name=name + "_box",
                                       cx=True, cy=True, cz=True)
        super().add_child(housing_box, child_sum=1, child_name=self.name + "_box")
        hole_list = []

        leadscr_hole = addCyl_pos(r=self.ShaftR, h=self.Length + 1,
                                  name="leadscr_hole",
                                  axis='x', h_disp=-self.Length / 2.0 - 1)
        super().add_child(leadscr_hole, child_sum=1, child_name="leadscr_hole")
        hole_list.append(leadscr_hole)
        nutflange_hole = addCyl_pos(r=self.FlangeR, h=self.FlangeL + 1,
                                    name="nutflange_hole",
                                    axis='x',
                                    h_disp=self.Length / 2.0 - self.FlangeL)
        super().add_child(nutflange_hole, child_sum=1, child_name="nutflange_hole")
        hole_list.append(nutflange_hole)
        # bolts to attach the nut flange to the housing
        # M3 x 10
        boltflange_l = addCyl_pos(r=self.FlangeBoltR,
                                  h=self.FlangeBoltL + 1,
                                  name="boltflange_l",
                                  axis='x',
                                  h_disp=self.Length / 2.0 - self.FlangeL - self.FlangeBoltL)
        boltflange_l.Placement.Base = FreeCAD.Vector(0,
                                                     - self.FlangeBoltPosD / 2.0,
                                                     )
        hole_list.append(boltflange_l)
        boltflange_r = addCyl_pos(r=self.FlangeBoltR,
                                  h=self.FlangeBoltL + 1,
                                  name="boltflange_r",
                                  axis='x',
                                  h_disp=self.Length / 2.0 - self.FlangeL - self.FlangeBoltL)
        boltflange_r.Placement.Base = FreeCAD.Vector(0,
                                                     self.FlangeBoltPosD / 2.0,
                                                     0)
        hole_list.append(boltflange_r)

        # bolts to attach the housing to the moving part
        # M4x7
        boltface_1 = fcfun.addCyl_pos(r=self.BoltR,
                                      h=self.BoltL + 1,
                                      name="boltface_1",
                                      axis='z',
                                      h_disp=-self.Height / 2 - 1)
        boltface_1.Placement.Base = FreeCAD.Vector(
            - self.Length / 2.0 + self.BoltLen2end,
            - self.Width / 2.0 + self.BoltWid2end,
            0)
        hole_list.append(boltface_1)
        boltface_2 = fcfun.addCyl_pos(r=self.BoltR,
                                      h=self.BoltL + 1,
                                      name="boltface_2",
                                      axis='z',
                                      h_disp=-self.Height / 2 - 1)
        boltface_2.Placement.Base = FreeCAD.Vector(
            self.BoltLenSep / 2.0,
            - self.Width / 2.0 + self.BoltWid2end,
            0)
        hole_list.append(boltface_2)
        boltface_3 = fcfun.addCyl_pos(r=self.BoltR,
                                      h=self.BoltL + 1,
                                      name="boltface_3",
                                      axis='z',
                                      h_disp=-self.Height / 2 - 1)
        boltface_3.Placement.Base = FreeCAD.Vector(
            - self.Length / 2.0 + self.BoltLen2end,
            self.BoltWidSep / 2.0,
            0)
        hole_list.append(boltface_3)
        boltface_4 = fcfun.addCyl_pos(r=self.BoltR,
                                      h=self.BoltL + 1,
                                      name="boltface_4",
                                      axis='z',
                                      h_disp=-self.Height / 2 - 1)
        boltface_4.Placement.Base = FreeCAD.Vector(
            self.BoltLenSep / 2.0,
            self.BoltWidSep / 2.0,
            0)
        hole_list.append(boltface_4)
        nuthouseholes = doc.addObject("Part::MultiFuse", "nuthouse_holes")
        nuthouseholes.Shapes = hole_list

        # rotation vector calculation
        if nutaxis == 'x':
            vec1 = (1, 0, 0)
        elif nutaxis == '-x':
            vec1 = (-1, 0, 0)
        elif nutaxis == 'y':
            vec1 = (0, 1, 0)
        elif nutaxis == '-y':
            vec1 = (0, -1, 0)
        elif nutaxis == 'z':
            vec1 = (0, 0, 1)
        elif nutaxis == '-z':
            vec1 = (0, 0, -1)

        if screwface_axis == 'x':
            vec2 = (1, 0, 0)
        elif screwface_axis == '-x':
            vec2 = (-1, 0, 0)
        elif screwface_axis == 'y':
            vec2 = (0, 1, 0)
        elif screwface_axis == '-y':
            vec2 = (0, -1, 0)
        elif screwface_axis == 'z':
            vec2 = (0, 0, 1)
        elif screwface_axis == '-z':
            vec2 = (0, 0, -1)

        vrot = fcfun.calc_rot(vec1, vec2)
        vdesp = fcfun.calc_desp_ncen(
            Length=self.Length,
            Width=self.Width,
            Height=self.Height,
            vec1=vec1, vec2=vec2,
            cx=cx, cy=cy, cz=cz)

        housing_box.Placement.Rotation = vrot
        nuthouseholes.Placement.Rotation = vrot
        housing_box.Placement.Base = vdesp
        nuthouseholes.Placement.Base = vdesp

        t8nuthouse = doc.addObject("Part::Cut", "t8nuthouse")
        t8nuthouse.Base = housing_box
        t8nuthouse.Tool = nuthouseholes

        self.fco = t8nuthouse  # the FreeCad Object
