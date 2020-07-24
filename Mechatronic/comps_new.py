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

logging.basicConfig(level=logging.DEBUG,
                    format='%(%(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

class Sk_dir (Obj3D):
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
                 fc_axis_h = VZ,
                 fc_axis_d = VX,
                 fc_axis_w = V0,
                 pos_h = 1,
                 pos_w = 1,
                 pos_d = 1,
                 pillow = 0, #make it the same height of a pillow block
                 pos = V0,
                 wfco = 1,
                 tol = 0.3,
                 name= "shaft_holder"):
        self.size = size
        self.wfco = wfco
        self.name = name

        self.pos = FreeCAD.Vector(0,0,0)
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
        if skdict == None:
            logger.error("Sk size %d not supported", size)

        # normalize de axis
        axis_h = DraftVecUtils.scaleTo(fc_axis_h,1)
        axis_d = DraftVecUtils.scaleTo(fc_axis_d,1)
        if fc_axis_w == V0:
            axis_w = axis_h.cross(axis_d)
        else:
            axis_w = DraftVecUtils.scaleTo(fc_axis_w,1)

        axis_h_n = axis_h.negative()
        axis_d_n = axis_d.negative()
        axis_w_n = axis_w.negative()

        NuevaClase.Obj3D.__init__(self, axis_d, axis_w, axis_h, name = name)

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
        # Bolt's head lenght
        tbolt_head_l = (self.holtol
                        * kcomp.D912_HEAD_L[skdict['tbolt']] )
        # Mounting bolt radius with added tolerance
        mbolt_r = self.holtol * skdict['mbolt']/2.


        self.d0_cen = 0 
        self.w0_cen = 1 # symmetric
        self.h0_cen = 0
        # vectors from the origin to the points along axis_d:
        self.d_o[0] = V0 # origin
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
            ref2rod_h = V0 # h_o[0]
            ref2base_h = DraftVecUtils.scale(axis_h, -sk_axis_h) # h_o[1]
        else:
            ref2rod_h = DraftVecUtils.scale(axis_h, sk_axis_h) # h_o[1]
            ref2base_h = V0 # h_o[0]
        if pos_w == 0:  # distance vectors on axis_w
            ref2cen_w = V0 # w_o[0]
            ref2bolt_w = DraftVecUtils.scale(axis_w, -sk_mbolt_sep/2.) # w_o[-1]
            ref2end_w = DraftVecUtils.scale(axis_w, -sk_w/2.) # w_o[2]
        elif pos_w == 1:
            ref2cen_w =  DraftVecUtils.scale(axis_w, sk_mbolt_sep/2.) # w_o[1]
            ref2bolt_w = V0 # w_o[0]
            ref2end_w = DraftVecUtils.scale(axis_w, -(sk_w-sk_mbolt_sep)/2.) # w_o[]
        else: # w_o == -1 at the end on the width dimension
            ref2cen_w =  DraftVecUtils.scale(axis_w, sk_w/2.) # w_o[2]
            ref2bolt_w = DraftVecUtils.scale(axis_w, (sk_w-sk_mbolt_sep)/2.) # w_o[]
        if pos_d == 1:  # distance vectors on axis_d
            ref2cen_d = V0 # d_o[0]
            ref2end_d = DraftVecUtils.scale(axis_d, -sk_d/2.) # d_o[1]
        else:
            ref2cen_d = DraftVecUtils.scale(axis_d, sk_d/2.) # d_o[1]
            ref2end_d = V0 # d_o[0]

        # TODO: Use the newe method:
        # super().get_pos_dwh(pos_d,pos_w,pos_h)
        basecen_pos = self.pos + ref2base_h + ref2cen_w + ref2cen_d
        # Making the tall box:
        shp_tall = fcfun.shp_box_dir (box_w = sk_center_w, 
                                  box_d = sk_d,
                                  box_h = sk_h,
                                  fc_axis_w = axis_w,
                                  fc_axis_h = axis_h,
                                  fc_axis_d = axis_d,
                                  cw = 1, cd= 1, ch=0, pos = basecen_pos)
        # Making the wide box:
        shp_wide = fcfun.shp_box_dir (box_w = sk_w, 
                                  box_d = sk_d,
                                  box_h = sk_base_h,
                                  fc_axis_w = axis_w,
                                  fc_axis_h = axis_h,
                                  fc_axis_d = axis_d,
                                  cw = 1, cd= 1, ch=0, pos = basecen_pos)
        shp_sk = shp_tall.fuse(shp_wide)
        doc.recompute()
        shp_sk = shp_sk.removeSplitter()

        
        holes = []

        # Shaft hole, 
        rodcen_pos = self.pos + ref2rod_h + ref2cen_w + ref2cen_d
        rod_hole = fcfun.shp_cylcenxtr(r= size/2. +self.tol,
                                         h = sk_d,
                                         normal = axis_d,
                                         ch = 1,
                                         xtr_top = 1,
                                         xtr_bot = 1,
                                         pos = rodcen_pos)
        holes.append(rod_hole)

        # the upper sepparation
        shp_topopen = fcfun.shp_box_dir_xtr (
                                  box_w = self.up_sep_dist, 
                                  box_d = sk_d,
                                  box_h = sk_h-sk_axis_h,
                                  fc_axis_w = axis_w,
                                  fc_axis_h = axis_h,
                                  fc_axis_d = axis_d,
                                  cw = 1, cd= 1, ch=0,
                                  xtr_h = 1, xtr_d = 1, xtr_nd = 1,
                                  pos = rodcen_pos)
        holes.append(shp_topopen)

        # Tightening bolt hole
        # tbolt_d is the diameter of the bolt: (M..) M4, ...
        # tbolt_head_r: is the radius of the tightening bolt's head
        # (including tolerance), which its bottom either
        #- is at the middle point between
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
        tbolt_pos = (   rodcen_pos
                      + DraftVecUtils.scale(axis_w, sk_center_w/2.)
                      + DraftVecUtils.scale(axis_h, size/2.)
                      + DraftVecUtils.scale(axis_h, rodtop2top_dist/2.))
        shp_tbolt = fcfun.shp_bolt_dir(r_shank= tbolt_d/2.,
                                        l_bolt = sk_center_w,
                                        r_head = tbolt_head_r,
                                        l_head = tbolt_head_l,
                                        hex_head = 0,
                                        xtr_head = 1,
                                        xtr_shank = 1,
                                        support = 0,
                                        fc_normal = axis_w_n,
                                        fc_verx1 = axis_h,
                                        pos = tbolt_pos)
        holes.append(shp_tbolt)
 
        #Mounting bolts
        cen2mbolt_w = DraftVecUtils.scale(axis_w, sk_mbolt_sep/2.)
        for w_pos in [cen2mbolt_w.negative(), cen2mbolt_w]:
            mbolt_pos = basecen_pos + w_pos
            mbolt_hole = fcfun.shp_cylcenxtr(r= mbolt_r,
                                           h = sk_d,
                                           normal = axis_h,
                                           ch = 0,
                                           xtr_top = 1,
                                           xtr_bot = 1,
                                           pos = mbolt_pos)
            holes.append(mbolt_hole)
 

        shp_holes = fcfun.fuseshplist(holes)
        shp_sk = shp_sk.cut(shp_holes)
        self.shp = shp_sk

        if wfco == 1:
            super().create_fco()
            # Need to set first in (0,0,0) and after that set the real placement.
            # This enable to do rotations without any issue
            self.fco.Placement.Base = FreeCAD.Vector(0,0,0) 
            self.fco.Placement.Base = self.position
            
            

    def color (self, color = (1,1,1)):
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
        0: start point, counting xtr_nd,
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
               inner square     :  :         middle poit considering depth only
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

    def __init__ (self, depth,
                  aluprof_dict,
                  xtr_d=0, xtr_nd=0,
                  axis_d = VX, axis_w = VY, axis_h = V0,
                  pos_d = 0, pos_w = 0, pos_h = 0,
                  pos = V0,
                  model_type = 1, # dimensional model
                  name = None):
        
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

        if name == None:
            name = ( 'aluprof_w' + str(int(aluprof_dict['w']))
                        + 'l_' + str(int(xtr_nd + depth + xtr_d)))

        Obj3D.__init__(self, axis_d, axis_w, axis_h, name = name)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])
        
        self.pos = FreeCAD.Vector(0,0,0)
        self.position = pos

        self.d0_cen = 0
        self.w0_cen = 1 # symmetric
        self.h0_cen = 1 # symmetric

        # total length (depth)
        self.tot_d = xtr_nd + depth + xtr_d

        # vectors from the origin to the points along axis_d:
        self.d_o[0] = V0 # origin
        self.d_o[1] = self.vec_d(xtr_nd) #if xtr_nd= 0: same as d_o[0]
        # middle point, not considering xtr_nd and xtr_d
        self.d_o[2] = self.vec_d(xtr_nd + depth/2.)
        # middle point considering xtr_nd and xtr_d
        self.d_o[3] = self.vec_d(self.tot_d /2.)
        self.d_o[4] = self.vec_d(xtr_nd + depth)
        self.d_o[5] = self.vec_d(self.tot_d)

        # vectors from the origin to the points along axis_w:
        # symmetric: negative
        self.w_o[0] = V0 # center: origin
        self.w_o[1] = self.vec_w(-insquare/2.)
        self.w_o[2] = self.vec_w(-(width/2. - thick))
        self.w_o[3] = self.vec_w(-width/2.)

        # vectors from the origin to the points along axis_h:
        # symmetric: negative
        self.h_o[0] = V0 # center: origin
        self.h_o[1] = self.vec_h(-insquare/2.)
        self.h_o[2] = self.vec_h(-(width/2. - thick))
        self.h_o[3] = self.vec_h(-width/2.)

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        shp_alu_wire = fcfun.shp_aluwire_dir (width, thick, slot, insquare,
                                              fc_axis_x = self.axis_w,
                                              fc_axis_y = self.axis_h,
                                              ref_x = 1, # pos_o is centered
                                              ref_y = 1, # pos_o is centered
                                              pos = self.pos_o)


        # make a face of the wire
        shp_alu_face = Part.Face (shp_alu_wire)
        # inner hole
        if indiam > 0 :
            hole =  Part.makeCircle (indiam/2.,   # Radius
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
        self.fco.Placement.Base = FreeCAD.Vector(0,0,0) 
        self.fco.Placement.Base = self.position

class PartLinGuideBlock (Obj3D):
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
        The axis along the depth (lenght) of the block (and rail) 
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
    def __init__ (self, block_dict, rail_dict,
                  axis_d = VX, axis_w = V0, axis_h = VZ,
                  pos_d = 0, pos_w = 0, pos_h = 0,
                  pos = V0,
                  model_type = 1, # dimensional model
                  name = None):

        self.pos = FreeCAD.Vector(0,0,0)
        self.position = pos

        if name == None:
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

        self.block_d  = block_dict['bl']
        self.block_ds = block_dict['bls']
        self.block_w  = block_dict['bw']
        self.block_ws = block_dict['bws']
        self.block_h  = block_dict['bh']

        self.linguide_h = block_dict['lh']

        self.bolt_dsep = block_dict['boltlsep']
        self.bolt_wsep = block_dict['boltwsep']
        self.bolt_d    = block_dict['boltd']
        self.bolt_l    = block_dict['boltl']

        linguide_h = block_dict['lh']

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

        self.d0_cen = 1 # symmetric
        self.w0_cen = 1 # symmetric
        self.h0_cen = 0

        if self.bolt_l == 0: # thruhole
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
        self.d_o[0] = V0 # Origin (center symmetric)
        self.d_o[1] = self.vec_d(-self.bolt_dsep/2.)
        self.d_o[2] = self.vec_d(-self.block_ds/2.)
        self.d_o[3] = self.vec_d(-self.block_d/2.)
 
        # vectors from the origin to the points along axis_w:
        self.w_o[0] = V0 # Origin (center symmetric)
        self.w_o[1] = self.vec_w(-self.rail_w/2.)
        self.w_o[2] = self.vec_w(-self.bolt_wsep/2.)
        self.w_o[3] = self.vec_w(-self.block_ws/2.)
        self.w_o[4] = self.vec_w(-self.block_w/2.)
 
        # vectors from the origin to the points along axis_h:
        # could make more sense to have the origin at the top
        self.h_o[0] = V0 # Origin at the bottom
        self.h_o[1] = self.vec_h(self.rail_ins_h)
        self.h_o[2] = self.vec_h(self.block_h - self.bolt_l)
        self.h_o[3] = self.vec_h(self.block_h)
        self.h_o[4] = self.vec_h(-self.rail_bot_h)
 
        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        # the main block
        shp_mblock = fcfun.shp_box_dir (box_w = self.block_w,
                                        box_d = self.block_ds,
                                        box_h = self.block_h,
                                        fc_axis_w = self.axis_w,
                                        fc_axis_d = self.axis_d,
                                        fc_axis_h = self.axis_h,
                                        cw = 1, cd = 1, ch = 0,
                                        pos = self.pos_o)

        # the extra block
        shp_exblock = fcfun.shp_box_dir (box_w = self.block_ws,
                                        box_d = self.block_d,
                                        box_h = self.block_h,
                                        fc_axis_w = self.axis_w,
                                        fc_axis_d = self.axis_d,
                                        fc_axis_h = self.axis_h,
                                        cw = 1, cd = 1, ch = 0,
                                        pos = self.pos_o)

        # fusion of these blocks
        shp_block = shp_mblock.fuse(shp_exblock)

        holes_list = []

        # rail hole:
        if self.rail_h > 0 and self.rail_w > 0:
            wire_rail = fcfun.wire_lgrail( rail_w = self.rail_w,
                                           rail_h = self.rail_h,
                                           axis_w = self.axis_w,
                                           axis_h = self.axis_h,
                                           pos_w = 0, pos_h = 0,
                                           pos = self.get_pos_h(4))

            face_rail = Part.Face(wire_rail)
            shp_rail = fcfun.shp_extrud_face (face = face_rail,
                                              length = self.block_d + 2,
                                              vec_extr_axis = self.axis_d,
                                              centered = 1)

            #Part.show(shp_rail)
            holes_list.append(shp_rail)

        # bolt holes:
        for d_i in (-1, 1): # positions of the holes along axis_d
            for w_i in (-2, 2): # positions of the holes along axis_w
                shp_bolt = fcfun.shp_cylcenxtr (
                                        r = self.bolt_d/2.,
                                        h = self.bolt_l,
                                        normal = axis_h,
                                        ch = 0,
                                        xtr_top = 1,
                                        xtr_bot = self.thruhole,
                                        pos = self.get_pos_dwh(d_i, w_i, 2))
                holes_list.append(shp_bolt)

        shp_holes = fcfun.fuseshplist(holes_list)
        shp_block = shp_block.cut(shp_holes)
        shp_block = shp_block.removeSplitter()

        self.shp = shp_block
        super().create_fco(self.name)
        # Need to set first in (0,0,0) and after that set the real placement.
        # This enable to do rotations without any issue
        self.fco.Placement.Base = FreeCAD.Vector(0,0,0) 
        self.fco.Placement.Base = self.position