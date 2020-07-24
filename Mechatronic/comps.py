# ----------------------------------------------------------------------------
# -- Components
# -- comps library
# -- Python classes that creates useful parts for FreeCAD
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- October-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------


import FreeCAD
import Part
import logging
import os
import inspect
import Draft
import DraftGeomUtils
import DraftVecUtils
import math
#import copy;
#import Mesh;

# ---------------------- can be taken away after debugging
# directory this file is
filepath = os.getcwd()
import sys
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath)
# ---------------------- can be taken away after debugging

import kcomp # before, it was called mat_cte
import fcfun
import shp_clss
import fc_clss

from fcfun import V0, VX, VY, VZ, V0ROT, addBox, addCyl, addCyl_pos, fillet_len
from fcfun import VXN, VYN, VZN
from fcfun import addBolt, addBoltNut_hole, NutHole


logging.basicConfig(level=logging.DEBUG,
                    format='%(%(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
#
#        _______       _______________________________  TotH = H
#       |  ___  |                     
#       | /   \ |      __________ HoleH = h
#       | \___/ |  __
#     __|       |__ /| __
#    |_____________|/  __ TotD = L ___________________
#
#     <- TotW  = W->
#
# hole_x: 1 the depth along X axis 
#           Hole facing X
#         0 the depth along Y axis 
#           Hole facing Y
# cx:     1 if you want the coordinates referenced to the x center of the piece
#         it can be done because it is a new shape formed from the union
# cy:     1 if you want the coordinates referenced to the y center of the piece
# upsdown:  NOT YET
#            0: Normal vertical position, referenced to 0
#            1:  z0 is the center of the hexagon (nut)
#              it can be done because it is a new shape formed from the union


class Sk (object):

    """
     SK dimensions:
     dictionary for the dimensions
     mbolt: is mounting bolt. it corresponds to its metric
     tbolt: is the tightening bolt.
    SK12 = { 'd':12.0, 'H':37.5, 'W':42.0, 'L':14.0, 'B':32.0, 'S':5.5,
             'h':23.0, 'A':21.0, 'b': 5.0, 'g':6.0,  'I':20.0,
              'mbolt': 5, 'tbolt': 4} 
    """

    # separation of the upper side (it is not defined). Change it
    # measured for sk12 is 1.2
    up_sep_dist = 1.2

    # tolerances for holes 
    holtol = 1.1

    def __init__(self, size, name, hole_x = 1, cx=0, cy=0):
        self.size = size
        self.name = name
        self.cx = cx
        self.cy = cy

        skdict = kcomp.SK.get(size)
        if skdict == None:
            logger.warning("Sk size %d not supported", size)
        else:
            doc = FreeCAD.ActiveDocument
            # Total height:
            sk_z = skdict['H'];
            self.TotH = sk_z
            # Total width (Y):
            sk_w = skdict['W'];
            self.TotW = sk_w
            # Total depth (x):
            sk_d = skdict['L'];
            self.TotD = sk_d
            # Base height
            sk_base_h = skdict['g'];
            # center width
            sk_center_w = skdict['I'];
            # Axis height:
            sk_axis_h = skdict['h'];
            self.HoleH = sk_axis_h;
    
            # tightening bolt with added tolerances:
            # Bolt's head radius
            tbolt_head_r = (self.holtol
                            * kcomp.D912_HEAD_D[skdict['tbolt']])/2.0
            # Bolt's head lenght
            tbolt_head_l = (self.holtol
                            * kcomp.D912_HEAD_L[skdict['tbolt']] )
            # Mounting bolt radius with added tolerance
            mbolt_r = self.holtol * skdict['mbolt']/2.
    
            # the total dimensions: LxWxH
            # we will cut it
            total_box = addBox(x = sk_d,
                               y = sk_w,
                               z = sk_z,
                               name = "total_box",
                               cx = False, cy=True)

            # what we have to cut from the sides
            side_box_y = (sk_w - skdict['I'])/2.
            side_box_z = sk_z - skdict['g']
    
            side_cut_box_r = addBox (sk_d, side_box_y, side_box_z,
                                     "side_box_r")
            side_cut_pos_r = FreeCAD.Vector(0,
                                            skdict['I']/2.,
                                            skdict['g'])
            side_cut_box_r.Placement.Base = side_cut_pos_r

            side_cut_box_l= addBox (sk_d, side_box_y, side_box_z,
                                     "side_box_l")
            side_cut_pos_l = FreeCAD.Vector(0,-sk_w/2.,skdict['g'])
            side_cut_box_l.Placement.Base = side_cut_pos_l

            # union 
            side_boxes = doc.addObject("Part::Fuse", "side_boxes")
            side_boxes.Base = side_cut_box_r
            side_boxes.Tool = side_cut_box_l

            # difference 
            sk_shape = doc.addObject("Part::Cut", "sk_shape")
            sk_shape.Base = total_box
            sk_shape.Tool = side_boxes

            # Shaft hole, its height has +2 to make it throughl L all de way
            shaft_hole = addCyl(skdict['d']/2.,
                                sk_d+2,
                                "shaft_hole")

            """
            First argument defines de position: -1, 0, h
            Second argument rotation: 90 degrees rotation in Y.
            Third argument the center of the rotation, in this case,
                  it is in the cylinder
            axis at the base of the cylinder 
            """
            shaft_hole.Placement = FreeCAD.Placement(
                                         FreeCAD.Vector(-1,0,skdict['h']),
                                         FreeCAD.Rotation(VY,90),
                                         V0)

            # the upper sepparation
            up_sep = addBox( sk_d +2,
                             self.up_sep_dist,
                             sk_z-skdict['h'] +1,
                             "up_sep")
            up_sep_pos = FreeCAD.Vector(-1,
                                        -self.up_sep_dist/2,
                                         skdict['h']+1)
            up_sep.Placement.Base = up_sep_pos

            #Tightening bolt shaft hole, its height has +2 to make it
            #throughl L all de way
            #skdict['tbolt'] is the diameter of the bolt: (M..) M4, ...
            #tbolt_head_r: is the radius of the tightening bolt's head
            #(including tolerance), which its bottom either
            #- is at the middle point between
            #  - A: the total height :sk_z
            #  - B: the top of the shaft hole: skdict['h']+skdict['d']/2
            #  - so the result will be (A + B)/2
            #or it is aligned with the top of the 12mm shaft, whose height is: 
            #    skdict['h']+skdict['d']/2
            tbolt_shaft = addCyl(skdict['tbolt']/2,skdict['I']+2,
                                      "tbolt_shaft")
            tbolt_shaft_pos = FreeCAD.Vector(sk_d/2.,
                            skdict['I']/2.+1,
                            skdict['h']+skdict['d']/2.+tbolt_head_r/self.holtol)
                            #(sk_z + skdict['h']+skdict['d']/2.)/2.)
            tbolt_shaft.Placement = FreeCAD.Placement(tbolt_shaft_pos,
                                                 FreeCAD.Rotation(VX,90),
                                                 V0)

            # Head of the thigthening bolt
            tbolt_head = addCyl(tbolt_head_r,tbolt_head_l+1, "tbolt_head")
            tbolt_head_pos = FreeCAD.Vector(sk_d/2.,
                           skdict['I']/2.+1,
                           skdict['h']+skdict['d']/2+tbolt_head_r/self.holtol)
                           #(sk_z + skdict['h']+skdict['d']/2.)/2.)
            tbolt_head.Placement = FreeCAD.Placement(tbolt_head_pos,
                                         FreeCAD.Rotation(VX,90),
                                         V0)


            #Make an union of all these parts

            fuse_shaft_holes = doc.addObject("Part::MultiFuse",
                                             "fuse_shaft_holes")
            fuse_shaft_holes.Shapes = [tbolt_head,
                                       tbolt_shaft,
                                       up_sep, shaft_hole]

            #Cut from the sk_shape

            sk_shape_w_holes = doc.addObject("Part::Cut", "sk_shape_w_holes")
            sk_shape_w_holes.Base = sk_shape
            sk_shape_w_holes.Tool = fuse_shaft_holes

            #Mounting bolts
            mbolt_sh_r = addCyl(mbolt_r,skdict['g']+2., "mbolt_sh_r")
            mbolt_sh_l = addCyl(mbolt_r,skdict['g']+2., "mbolt_sh_l")

            mbolt_sh_r_pos = FreeCAD.Vector(sk_d/2,
                                            skdict['B']/2.,
                                            -1)

            mbolt_sh_l_pos = FreeCAD.Vector(sk_d/2,
                                            -skdict['B']/2.,
                                            -1)

            mbolt_sh_r.Placement.Base = mbolt_sh_r_pos
            mbolt_sh_l.Placement.Base = mbolt_sh_l_pos

            # Equivalent expresions to the ones above
            #mbolt_sh_l.Placement = FreeCAD.Placement(mbolt_sh_l_pos, v0rot, v0)
            #mbolt_sh_r.Placement = FreeCAD.Placement(mbolt_sh_r_pos, v0rot, v0)

            mbolts_sh = doc.addObject("Part::Fuse", "mbolts_sh")
            mbolts_sh.Base = mbolt_sh_r
            mbolts_sh.Tool = mbolt_sh_l

            # Instead of moving all the objects from the begining. I do it here
            # so it is easier, and since a new object will be created, it is
            # referenced correctly
            # Now, it is centered on Y, having the width on X, hole facing X
            # on the positive side of X
            if hole_x == 1:
                # this is how it is, no rotation
                rot = FreeCAD.Rotation(VZ,0)
                if cx == 1: #we want centered on X,bring back the half of depth
                    xpos = -self.TotD/2.
                else:
                    xpos = 0 # how it is
                if cy == 1: # centered on Y, how it is
                    ypos = 0
                else:
                    ypos = self.TotW/2.0 # bring forward the width
            else: # hole facing Y
                rot = FreeCAD.Rotation (VZ,90)
                # After rotating, it is centered on X, 
                if cx == 1: # centered on X, how it is
                    xpos = 0
                else:
                    xpos = self.TotW /2.0
                if cy == 1: # we want centered on Y, bring back
                    ypos = - self.TotD/2.0
                else:
                    ypos = 0
             

            sk_shape_w_holes.Placement.Base = FreeCAD.Vector (xpos, ypos, 0)
            mbolts_sh.Placement.Base = FreeCAD.Vector (xpos, ypos, 0)
            sk_shape_w_holes.Placement.Rotation = rot
            mbolts_sh.Placement.Rotation = rot
 

            sk_final = doc.addObject("Part::Cut", name)
            sk_final.Base = sk_shape_w_holes
            sk_final.Tool = mbolts_sh

            self.fco = sk_final   # the FreeCad Object



class Sk_dir (object):
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
        include the tightening bolt, or if ref_wc != 1
    ref_hr : int
        * 1: reference at the Rod Height dimension (rod center):
          points 1, 2, 3
        * 0: reference at the base: points 4, 5
    ref_wc : int
        * 1: reference at the center on the width dimension (fc_axis_w)
          points: 2, 4,
        * 0: reference at one of the bolt holes, point 5
        * -1: reference at one end. point 8
    ref_dc : int
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
                 ref_hr = 1,
                 ref_wc = 1,
                 ref_dc = 1,
                 pillow = 0, #make it the same height of a pillow block
                 pos = V0,
                 wfco = 1,
                 tol = 0.3,
                 name= "shaft_holder"):
        self.size = size
        self.wfco = wfco
        self.name = name
        self.pos = pos
        self.tol = tol
        self.ref_hr = ref_hr
        self.ref_wc = ref_wc
        self.ref_dc = ref_dc

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
        # Total height:
        sk_h = skdict['H'];
        self.tot_h = sk_h
        # Total width (Y):
        sk_w = skdict['W'];
        self.tot_w = sk_w
        # Total depth (x):
        sk_d = skdict['L'];
        self.tot_d = sk_d
        # Base height
        sk_base_h = skdict['g'];
        # center width
        sk_center_w = skdict['I'];
        # Axis height:
        sk_axis_h = skdict['h'];
        self.axis_h = sk_axis_h;
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

        if ref_hr == 1:  # distance vectors on axis_h
            ref2rod_h = V0
            ref2base_h = DraftVecUtils.scale(axis_h, -sk_axis_h)
        else:
            ref2rod_h = DraftVecUtils.scale(axis_h, sk_axis_h)
            ref2base_h = V0
        if ref_wc == 1:  # distance vectors on axis_w
            ref2cen_w = V0
            ref2bolt_w = DraftVecUtils.scale(axis_w, -sk_mbolt_sep/2.)
            ref2end_w = DraftVecUtils.scale(axis_w, -sk_w/2.)
        elif ref_wc == 0:
            ref2cen_w =  DraftVecUtils.scale(axis_w, sk_mbolt_sep/2.)
            ref2bolt_w = V0
            ref2end_w = DraftVecUtils.scale(axis_w, -(sk_w-sk_mbolt_sep)/2.)
        else: # ref_wc == -1 at the end on the width dimension
            ref2cen_w =  DraftVecUtils.scale(axis_w, sk_w/2.)
            ref2bolt_w = DraftVecUtils.scale(axis_w, (sk_w-sk_mbolt_sep)/2.)
        if ref_dc == 1:  # distance vectors on axis_d
            ref2cen_d = V0
            ref2end_d = DraftVecUtils.scale(axis_d, -sk_d/2.)
        else:
            ref2cen_d = DraftVecUtils.scale(axis_d, sk_d/2.)
            ref2end_d = V0

        basecen_pos = pos + ref2base_h + ref2cen_w + ref2cen_d
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
        rodcen_pos = pos + ref2rod_h + ref2cen_w + ref2cen_d
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
            # a freeCAD object is created
            fco = doc.addObject("Part::Feature", name )
            fco.Shape = self.shp
            self.fco = fco

    def color (self, color = (1,1,1)):
        if self.wfco == 1:
            self.fco.ViewObject.ShapeColor = color
        else:
            logger.debug("Object with no fco")

#doc =FreeCAD.newDocument()
#h_sk = Sk_dir (size = 8,
#                 fc_axis_h = VX,
#                 fc_axis_d = VZ,
#                 fc_axis_w = V0,
#                 ref_hr = 0,
#                 ref_wc = 0,
#                 ref_dc = 0,
#                 pillow = 0,
#                 pos = V0,
#                 tol = 0.3,
#                 wfco = 1,
#                 name= "sk8_tol03")


# --------------------------------------------------------------------
# Creates a Misumi Aluminun Profile 30x30 Series 6 Width 8
# length:   the length of the profile
# axis      'x', 'y' or 'z'
#           'x' will along the x axis
#           'y' will along the y axis
#           'z' will be vertical
# cx:     1 if you want the coordinates referenced to the x center of the piece
#         it can be done because it is a new shape formed from the union
# cy:     1 if you want the coordinates referenced to the y center of the piece
# cz:     1 if you want the coordinates referenced to the z center of the piece
# ATTRIBUTES:
# fco: The freecad object
# Sk: The sketch of the aluminum profile

class MisumiAlu30s6w8 (object):

    # filename of Aluminum profile sketch
    skfilename = "misumi_profile_hfs_serie6_w8_30x30.FCStd"
    ALU_W = 30.0
    ALU_Wh = ALU_W / 2.0  # half of it

    def __init__ (self, length, name, axis = 'x',
                  cx=False, cy=False, cz=False):
        doc = FreeCAD.ActiveDocument
        self.length = length
        self.name = name
        self.axis = axis
        self.cx = cx
        self.cy = cy
        self.cz = cz
        # filepath
        path = os.getcwd()
        #logging.debug(path)
        self.skpath = path + '/../../freecad/comps/'
        doc_sk = FreeCAD.openDocument(self.skpath + self.skfilename)

        list_obj_alumprofile = []
        for obj in doc_sk.Objects:
            
            #if (hasattr(obj,'ViewObject') and obj.ViewObject.isVisible()
            #    and hasattr(obj,'Shape') and len(obj.Shape.Faces) > 0 ):
            #   # len(obj.Shape.Faces) > 0 to avoid sketches
            #    list_obj_alumprofile.append(obj)
            if len(obj.Shape.Faces) == 0:
                orig_alumsk = obj

        FreeCAD.ActiveDocument = doc
        self.Sk = doc.addObject("Sketcher::SketchObject", 'sk_' + name)
        self.Sk.Geometry = orig_alumsk.Geometry
        print (orig_alumsk.Geometry)
        print (orig_alumsk.Constraints)
        self.Sk.Constraints = orig_alumsk.Constraints
        self.Sk.ViewObject.Visibility = False

        FreeCAD.closeDocument(doc_sk.Name)
        FreeCAD.ActiveDocument = doc #otherwise, clone will not work

        doc.recompute()

        # The sketch is on plane XY, facing Z
        if axis == 'x':
            self.Dir = (length,0,0)
            # rotation on Y
            rot = FreeCAD.Rotation(VY,90)
            if cx == True:
                xpos = - self.length / 2.0
            else:
                xpos = 0
            if cy == True:
                ypos = 0
            else:
                ypos = self.ALU_Wh  # half of the aluminum profile width
            if cz == True:
                zpos = 0
            else:
                zpos = self.ALU_Wh
        elif axis == 'y':
            self.Dir = (0,length,0)
            # rotation on X
            rot = FreeCAD.Rotation(VX,-90)
            if cx == True:
                xpos = 0
            else:
                xpos = self.ALU_Wh
            if cy == True:
                ypos = - self.length / 2.0
            else:
                ypos = 0
            if cz == True:
                zpos = 0
            else:
                zpos = self.ALU_Wh
        elif axis == 'z':
            self.Dir = (0,0,length)
            # no rotation
            rot = FreeCAD.Rotation(VZ,0)
            if cx == True:
                xpos = 0
            else:
                xpos = self.ALU_Wh
            if cy == True:
                ypos = 0
            else:
                ypos = self.ALU_Wh
            if cz == True:
                zpos = - self.length / 2.0
            else:
                zpos = 0
        else:
            logging.debug ("wrong argument")
              
        self.Sk.Placement.Rotation = rot
        self.Sk.Placement.Base = FreeCAD.Vector(xpos,ypos,zpos)

        alu_extr = doc.addObject("Part::Extrusion", name)
        alu_extr.Base = self.Sk
        alu_extr.Dir = self.Dir
        alu_extr.Solid = True

        self.fco = alu_extr   # the FreeCad Object


# ----------- class RectRndBar ---------------------------------------------
# Creates a rectangular bar with rounded edges, and with the posibility
# to be hollow
#
# Base:     the length of the base of the rectangle
# Height:   the length of the height of the rectangle
# Length:   the length of the bar, the extrusion 
# Radius:   the radius of the rounded edges (fillet)
# Thick:    the thikness of the bar (hollow bar)
#           If it is zero or larger than base or 
#               height, it will be full
# inrad_same : True: inradius = radius. When the radius is very small
#              False:  inradius = radius - thick 
# axis      'x', 'y' or 'z'
#           direction of the bar
#           'x' will along the x axis
#           'y' will along the y axis
#           'z' will be vertical
# baseaxis  'x', 'y' or 'z'
#           in which axis the base is on. Cannot be the same as axis
# cx:     1 if you want the coordinates referenced to the x center of the piece
#         it can be done because it is a new shape formed from the union
# cy:     1 if you want the coordinates referenced to the y center of the piece
# cz:     1 if you want the coordinates referenced to the z center of the piece
# attributes:
# inRad : radius of the inner radius
# inBase : lenght of the inner rectangle
# inHeight : height of the inner rectangle
# hollow   : True, if it is hollow, False if it is not
# face     : the face has been extruded
# fco      : FreeCad Object

class RectRndBar (object):

    def __init__ (self, Base, Height, Length, Radius, Thick = 0, 
                  inrad_same = False, axis = 'x',
                  baseaxis = 'y', name = "rectrndbar",
                  cx=False, cy=False, cz=False):
        doc = FreeCAD.ActiveDocument
        self.Base = Base
        self.Height = Height
        self.Length = Length
        self.Radius = Radius
        self.Thick = Thick
        self.inrad_same = inrad_same
        self.name = name
        self.axis = axis
        self.baseaxis = baseaxis
        self.cx = cx
        self.cy = cy
        self.cz = cz

        self.inBase = Base - 2 * Thick
        self.inHeight = Height - 2 * Thick

        if Thick == 0 or Thick >= Base or Thick >= Height:
            self.Thick = 0
            self.hollow = False
            self.inRad = 0  
            self.inrad_same = False  
            self.inBase = 0
            self.inHeight = 0
        else :
            self.hollow = True
            if inrad_same == True:
               self.inRad = Radius
            else:
               if Radius > Thick:
                   self.inRad = Radius - Thick
               else:
                   self.inRad = 0  # a rectangle, with no rounded edges (inside)

        wire_ext = fcfun.shpRndRectWire (x=Base, y=Height, r=Radius,
                                         zpos= Length/2.0)
        face_ext = Part.Face(wire_ext)
        if self.hollow == True:
            wire_int = fcfun.shpRndRectWire (x=self.inBase, 
                                             y=self.inHeight,
                                             r=self.inRad,
                                             zpos= Length/2.0)
            face_int = Part.Face(wire_int)
            face = face_ext.cut(face_int)
        else:
            face = face_ext  # is not hollow

        self.face = face

        # Rotate and extrude in the appropiate direction

        # now is facing Z, I use vec2
        if axis == 'x': # rotate to Z, the 1 or -1 makes the extrusion different
           vec2 = (1,0,0)
           dir_extr = FreeCAD.Vector(Length,0,0)
        elif axis == 'y':
           vec2 = (0,1,0)
           dir_extr = FreeCAD.Vector(0,Length,0)
        elif axis == 'z':
           vec2 = (0,0,1)
           dir_extr = FreeCAD.Vector(0,0,Length)

        if baseaxis == 'x':
           vec1 = (1,0,0)
        elif baseaxis == 'y':
           vec1 = (0,1,0)
        elif baseaxis == 'z':
           vec1 = (0,0,1)

        vrot = fcfun.calc_rot (vec1,vec2)
        vdesp = fcfun.calc_desp_ncen (
                                      Length = self.Base,
                                      Width = self.Height,
                                      Height = self.Length ,
                                      vec1 = vec1, vec2 = vec2,
                                      cx = cx, cy=cy, cz=cz)

        face.Placement.Base = vdesp
        face.Placement.Rotation = vrot

        shp_extr = face.extrude(dir_extr)
        rndbar = doc.addObject("Part::Feature", name)
        rndbar.Shape = shp_extr

        self.fco = rndbar
        
# ----------- end class RectRndBar ----------------------------------------


# ----------- class AluProf ---------------------------------------------
# Creates a generic aluminum profile 
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
# width:    the Width of the profile, it is squared
# length:   the length of the bar, the extrusion 
# thick: the thickness of the side
# slot: the width of the rail 
# insquare: the width of the inner square
# indiam: the diameter of the inner hole. If 0, there is no hole
# axis      'x', 'y' or 'z'
#           direction of the bar
#           'x' will be along the x axis
#           'y' will be along the y axis
#           'z' will be vertical
# cx:     1 if you want the coordinates referenced to the x center of the piece
#         it can be done because it is a new shape formed from the union
# cy:     1 if you want the coordinates referenced to the y center of the piece
# cz:     1 if you want the coordinates referenced to the z center of the piece
# attributes:
# the arguments and
# ax_center : 1 if the profile is centered along its axis. 0 if not
# face     : the face that has been extruded
# shp      : the shape
# fco      : the freecad object

# How rotation y movement works

#  Initial
#             Y
#             :
#             :
#          _  :  _
#         |_|_:_|_|
#   ........|.:.|........ X
#          _|_:_|_
#         |_| : |_|
#             :
#             :
#             :
#
#
#  Final                    axis = 'x'  -> Rotation -90 on axis Y: pitch -90
#             Z             cx = 0      
#             :             cy = 0      -> Translation Y: width/2
#             :             cz = 1      -> Translation Z: 0
#             :  
#             :_     _ 
#             |_|___|_|
#   ..........:.|...|........ Y
#             :_|___|_
#             |_|   |_|
#             :
#             :
#             :
#
#
#  Final                    axis = 'x'  -> Rotation -90 on axis Y: pitch -90
#             Z             cx = 0      
#             :             cy = 0      -> Translation Y: width/2
#             :             cz = 0      -> Translation Z: width/2
#             :  
#             :_     _ 
#             |_|___|_|
#             : |   |
#             :_|___|_
#   ..........|_|...|_|.......Y
#             :
#             :
#             :
#
#
#
#


class AluProf (object):

    def __init__ (self, width, length, thick, slot, insquare, 
                  indiam, axis = 'x',
                  name = "genaluprof",
                  cx=False, cy=False, cz=False):
        doc = FreeCAD.ActiveDocument
        self.width  = width
        self.length = length
        self.thick  = thick
        self.slot   = slot
        self.name   = name
        self.insquare = insquare
        self.indiam = indiam
        self.name   = name
        self.axis = axis
        self.fcvec_axis = fcfun.getfcvecofname(axis)
        self.cx = cx
        self.cy = cy
        self.cz = cz

        fcvec_axis = self.fcvec_axis
        
        # vectors of the points
        vecpoints = fcfun.aluprof_vec (width, thick, slot, insquare)
        doc.recompute()

        # wire Face
        wire_aluprof = fcfun.wire_sim_xy (vecpoints)


        # if it is not centered on X, and the axis doesn't go along X
        if cx == 0 and axis != 'x':
            posx = width/2.
        else:
            posx = 0

        if cy == 0 and axis != 'y':
            posy = width/2.
        else:
            posy = 0

        if cz == 0 and axis != 'z':
            posz = width/2.
        else:
            posz = 0

        if axis == 'x':
            ax_center = cx
        elif axis == 'y':
            ax_center = cy
        elif axis == 'z':
            ax_center = cz
        else:
            ax_center = 0
            logger.error("axis %s not defined. Supported: 'x', 'y', 'z', axis")

        self.ax_center = ax_center

        doc.recompute()
            
        pos = FreeCAD.Vector(posx,posy,posz)  # Position
        vec_axis =  fcfun.getfcvecofname(axis)
       
        face_ext = Part.Face(wire_aluprof)
        # since vec2 of calc_rot is referenced to VNZ, vec_facenomal is negated
        vec_naxis = DraftVecUtils.neg(vec_axis)
        vrot = fcfun.fc_calc_rot(V0, vec_naxis)
        face_ext.Placement.Rotation = vrot
        face_ext.Placement.Base = pos

        # inner hole
        if indiam > 0 :
            hole =  Part.makeCircle (indiam/2.,   # Radius
                                     pos,  # Position
                                     vec_axis)  # direction
            wire_hole = Part.Wire(hole)
            face_hole = Part.Face(wire_hole)

            face_profile = face_ext.cut(face_hole)
        else:
            face_profile = face_ext

        shp_profile = fcfun.shp_extrud_face (
                                 face = face_profile,
                                 length = length,
                                 vec_extr_axis = vec_axis,
                                 centered = ax_center)
        self.shp = shp_profile
        fco_profile = doc.addObject("Part::Feature", name)
        fco_profile.Shape = shp_profile
        
        self.fco = fco_profile

        self.defaluline()

    def color (self, color = (1,1,1)):
        self.fco.ViewObject.ShapeColor = color
        linecol = []
        for col_i in color:
            if col_i < 0.2:
                linecol.append(0.)
            else:
                linecol.append(col_i - 0.2)
        print (str(linecol))       
        self.fco.ViewObject.LineColor = tuple(linecol)
        print(str(color) + ' -  '  + str(self.fco.ViewObject.LineColor))


    def linecolor (self, color = (1,1,1)):
        self.fco.ViewObject.LineColor = color

    def linewidth (self, width = 1.):
        self.fco.ViewObject.LineWidth = width

    def defaluline (self):
        self.fco.ViewObject.LineColor = (0.5,0.5,0.5)
        self.fco.ViewObject.LineWidth = 1.



# ----------- class AluProf_dir ---------------------------------------------


class AluProf_dir (object):

    """
    Creates a generic aluminum profile in any direction
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
   
    Parameters
    ----------
    width : float
        The Width of the profile, it is squared
    length : float
        The length of the bar, the extrusion 
    thick : float
        The thickness of the side
    slot : float
        The width of the rail 
    insquare : float
        The width of the inner square
    indiam : float
        The diameter of the inner hole. If 0, there is no hole
    fc_axis_l : FreeCAD.Vector
         axis on the length direction
    fc_axis_w : FreeCAD.Vector
         axis on the width direction
    fc_axis_p : FreeCAD.Vector
         axis on the other width direction (perpendicular)
         can be V0 if ref_p = 1
    ref_l : int
        Reference (zero) on the fc_axis_l
        * 1: reference at the center
        * 2: reference at the end, the other end will be on the direction of
           fc_axis_l
    ref_w : int
        Reference (zero) on the fc_axis_w
        * 1: reference at the center
        * 2: reference at the side, the other end side will be on the
           direction of fc_axis_w
    ref_p : int
        Reference (zero) on the fc_axis_p
        * 1: reference at the center
        * 2: reference at the side, the other end side will be on the
           direction of fc_axis_p
    xtr_l : float
        if >0 it will be that extra length on the direction of fc_axis_l
        I dont think it is useful for a profile, but since it is easy to
        do, I just do it
    xtr_nl : float
        if >0 it will be that extra height on the opositve direction of
        fc_axis_l
    pos : FreeCAD.Vector
        FreeCAD vector of the position 
    wfco : int
        1 a freecad object will be created. 0: only a shape
    name : str
        Name of the freecad object
    
    Attributes
    ----------
    face : 
        The face that has been extruded
    shp : 
        The shape
    fco : 
        The freecad object
   
    ::

     ref_w = 1  ; ref_p = 1

                fc_axis_w
                :
                :
             _  :  _
            |_|_:_|_|
      ........|.:.|........ fc_axis_p
             _|_:_|_
            |_| : |_|
                :
                :
                :
   
   
     ref_w = 1 ; ref_p = 2              

                fc_axis_w
                :       
                :      
                :  
                :_     _ 
                |_|___|_|
      ..........:.|...|........ fc_axis_p
                :_|___|_
                |_|   |_|
                :
                :
                :
   
    """
#
#  Final                    axis = 'x'  -> Rotation -90 on axis Y: pitch -90
#             Z             cx = 0      
#             :             cy = 0      -> Translation Y: width/2
#             :             cz = 0      -> Translation Z: width/2
#             :  
#             :_     _ 
#             |_|___|_|
#             : |   |
#             :_|___|_
#   ..........|_|...|_|.......Y
#             :
#             :
#             :
#
#
#
#

    def __init__ (self, width, length, thick, slot, insquare, 
                  indiam, fc_axis_l = VX, fc_axis_w = VY, fc_axis_p = V0,
                  ref_l = 0, ref_w = 1, ref_p = 1,
                  xtr_l=0, xtr_nl=0,  pos = V0,
                  wfco = 1, name = "aluprof"):
        doc = FreeCAD.ActiveDocument
        self.width  = width
        self.length = length
        self.thick  = thick
        self.slot   = slot
        self.name   = name
        self.insquare = insquare
        self.indiam = indiam
        self.name   = name
        self.wfco = wfco
        self.pos = pos
        # normalize the axis
        axis_l = DraftVecUtils.scaleTo(fc_axis_l,1)
        axis_w = DraftVecUtils.scaleTo(fc_axis_w,1)
        if fc_axis_p == V0:
            axis_p = axis_l.cross(axis_w)
        else:
            axis_p = DraftVecUtils.scaleTo(fc_axis_p,1)
        axis_l_n = axis_l.negative()

        self.axis_l = axis_l
        self.axis_w = axis_w
        self.axis_p = axis_p

        # getting the base position

        if ref_l == 1: # move the postion half of the height down 
            base_pos = pos + DraftVecUtils.scale(axis_l_n, length/2. + xtr_nl)
        else:
            base_pos = pos + DraftVecUtils.scale(axis_l_n, xtr_nl)


        # Get the center position
        if ref_w == 2:
            ref2center_w = DraftVecUtils.scale(axis_w, width/2.)
        else:
            ref2center_w = V0
        if ref_p == 2:
            ref2center_p = DraftVecUtils.scale(axis_p, width/2.)
        else:
            ref2center_p = V0

        basecen_pos = base_pos + ref2center_w + ref2center_p


        shp_alu_wire = fcfun.shp_aluwire_dir (width, thick, slot, insquare,
                                              fc_axis_x = axis_w,
                                              fc_axis_y = axis_p,
                                              ref_x = 1, #already centered
                                              ref_y = 1, #already centered
                                              pos = basecen_pos)


        # make a face of the wire
        shp_alu_face = Part.Face (shp_alu_wire)
        # inner hole
        if indiam > 0 :
            hole =  Part.makeCircle (indiam/2.,   # Radius
                                     basecen_pos,  # Position
                                     axis_l)  # direction
            wire_hole = Part.Wire(hole)
            face_hole = Part.Face(wire_hole)
            shp_alu_face = shp_alu_face.cut(face_hole)

        # extrude it
        dir_extrud = DraftVecUtils.scaleTo(axis_l, length + xtr_nl + xtr_l)
        shp_aluprof = shp_alu_face.extrude(dir_extrud)

        self.shp = shp_aluprof
        if wfco == 1:
            fco_aluprof = doc.addObject("Part::Feature", name)
            fco_aluprof.Shape = shp_aluprof
            self.fco = fco_aluprof
            self.defaluline()

    def color (self, color = (1,1,1)):
        self.fco.ViewObject.ShapeColor = color
        linecol = []
        for col_i in color:
            #print (str(col_i))
            if col_i < 0.2:
                linecol.append(0.)
            else:
                linecol.append(col_i - 0.2)
        #print (str(linecol))       
        self.fco.ViewObject.LineColor = tuple(linecol)
        #print(str(color) + ' -  '  + str(self.fco.ViewObject.LineColor))
        #print(str(linecol))

    def linecolor (self, color = (1,1,1)):
        self.fco.ViewObject.LineColor = color

    def linewidth (self, width = 1.):
        self.fco.ViewObject.LineWidth = width

    def defaluline (self):
        self.fco.ViewObject.LineColor = (0.5,0.5,0.5)
        self.fco.ViewObject.LineWidth = 1.



# ----------- end class AluProf_dir ----------------------------------------

# Function that having a dictionary of the aluminum profile, just calls
# the class AluProf, 
def getaluprof ( aludict, length, 
                 axis = 'x',
                 name = "genaluprof",
                 cx=False, cy=False, cz=False):

    h_aluprof = AluProf ( width=aludict['w'],
                               length = length, 
                               thick = aludict['t'],
                               slot  = aludict['slot'],
                               insquare = aludict['insq'], 
                               indiam   = aludict['indiam'],
                               axis = axis,
                               name = name,
                               cx=cx, cy=cy, cz=cz)

    return (h_aluprof)


# Function that having a dictionary of the aluminum profile, just calls
# the class AluProf_dir, 
def getaluprof_dir ( aludict, length, 
                    fc_axis_l = VX, fc_axis_w = VY, fc_axis_p = V0,
                    ref_l = 0, ref_w = 1, ref_p = 1,
                    xtr_l=0, xtr_nl=0,  pos = V0,
                    wfco = 1, name = "aluprof"):

    h_aluprof = AluProf_dir ( width=aludict['w'],
                              length = length, 
                              thick = aludict['t'],
                              slot  = aludict['slot'],
                              insquare = aludict['insq'], 
                              indiam   = aludict['indiam'],
                              fc_axis_l = fc_axis_l,
                              fc_axis_w = fc_axis_w,
                              fc_axis_p = fc_axis_p,
                              ref_l = ref_l, ref_w = ref_w, ref_p = ref_p,
                              xtr_l = xtr_l, xtr_nl = xtr_nl,
                              pos = pos, wfco = wfco,
                              name = name)

    return (h_aluprof)


#doc =FreeCAD.newDocument()
#h_aluprof = getaluprof_dir(aludict= kcomp.ALU_MOTEDIS_20I5,
#                         length=50, 
#                    fc_axis_l = FreeCAD.Vector(1,1,0),
#                    fc_axis_w = FreeCAD.Vector(-1,1,0),
#                    fc_axis_p = V0,
#                    ref_l = 1, ref_w = 2, ref_p = 2,
#                    xtr_l=0, xtr_nl=0,  pos = FreeCAD.Vector(1,2,4),
#                    wfco = 1, name = "aluprof")



#cls_aluprof = getaluprof(aludict= kcomp.ALU_MOTEDIS_20I5,
#                         length=80) 
#
#cls_aluprof = getaluprof(aludict= kcomp.ALU_MOTEDIS_20I5,
#                         axis = 'z',
#                         length=100) 
#
#cls_aluprof = getaluprof(aludict= kcomp.ALU_MOTEDIS_20I5,
#                         length=40, 
#                         axis = 'y',
#                 cx=True, cy=False, cz=False)
##
#h_aluprof = getaluprof(aludict= kcomp.ALU_MAKERBEAM_10,
#                         length=60, 
#                         axis = 'y',
#                 cx=True, cy=False, cz=True)
#
#h_aluprof = getaluprof(aludict= kcomp.ALU_MAKERBEAM_15,
#                         length=50, 
#                         axis = 'x',
#                 cx=True, cy=True, cz=True)
#













# ----------- class ShpAluProf ---------------------------------------------


class ShpAluProf (shp_clss.Obj3D):

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

    def __init__ (self, width, depth, thick, slot,
                  insquare, indiam,
                  xtr_d=0, xtr_nd=0,
                  axis_d = VX, axis_w = VY, axis_h = V0,
                  pos_d = 0, pos_w = 0, pos_h = 0,
                  pos = V0):


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

        shp_clss.Obj3D.__init__(self, axis_d, axis_w, axis_h)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

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

class PartAluProf (fc_clss.SinglePart, ShpAluProf):
    """ 
    Integration of a ShpAluProf object into a PartAluProf
    object, so it is a FreeCAD object that can be visualized in FreeCAD
    Instead of using all the arguments of ShpAluProf, it will use
    a dictionary

    Parameters
    ----------
    depth : float
        (depth) length of the bar, the extrusion 
    aluprof_dict : dictionary
        Dictionary with all the information about the profile
        in kcomp.py there are some dictionaries that can be used, they are
        not exact -- same as ShpAluProf
    xtr_d : float
        If >0 it will be that extra depth (length) on the direction of axis_d
    xtr_nd : float
        If >0 it will be that extra depth (length) on the opositve direction of
        axis_d can be V0 if pos_h = 0
    axis_d : FreeCAD.Vector
        Axis along the length (depth) direction
    axis_w : FreeCAD.Vector
        Axis along the width direction
    axis_h : FreeCAD.Vector
        Axis along the width direction
    pos_d : int
        Location of pos along axis_d (see drawing)

            * 0: start point, counting xtr_nd,
              if xtr_nd == 0 -> pos_d 0 and 1 will be the same
            * 1: start point, not counting xtr_nd
            * 2: middle point not conunting xtr_nd and xtr_d
            * 3: middle point conunting xtr_nd and xtr_d
            * 4: end point, not counting xtr_d
            * 5: end point considering xtr_d

    pos_w : int
        Location of pos along axis_w (see drawing). Symmetric, negative indexes
        means the other side
        
            * 0: at the center of symmetry
            * 1: at the inner square
            * 2: at the interior side of the outer part of the rail (thickness of the4 side)
            * 3: at the end of the profile along axis_w 

    pos_h : int
        Same as pos_w 
    pos : FreeCAD.Vector
        Position of point defined by pos_d, pos_w, pos_h
    model_type : int
        Kind of model
        
            * 1: dimensional model: it can be printed to assemble a model,but the part
              will not work as defined. For example, if printed this aluminum
              profile will not work as defined, and also, it is not exact

    name : str
        Name of the object

    """


    def __init__( self, depth,
                  aluprof_dict,
                  xtr_d=0, xtr_nd=0,
                  axis_d = VX, axis_w = VY, axis_h = V0,
                  pos_d = 0, pos_w = 0, pos_h = 0,
                  pos = V0,
                  model_type = 1, # dimensional model
                  name = ''):

        default_name = ( 'aluprof_w' + str(int(aluprof_dict['w']))
                         + 'l_' + str(int(xtr_nd + depth + xtr_d)))
        self.set_name (name, default_name, change=0)

        ShpAluProf.__init__(self,
                            width  = aluprof_dict['w'],
                            depth  = depth,
                            thick  = aluprof_dict['t'],
                            slot   = aluprof_dict['slot'],
                            insquare = aluprof_dict['insq'],
                            indiam   = aluprof_dict['indiam'],
                            xtr_d    = xtr_d,
                            xtr_nd   = xtr_nd,
                            axis_d   = axis_d,
                            axis_w   = axis_w,
                            axis_h   = axis_h,
                            pos_d    = pos_d, pos_w = pos_w, pos_h = pos_h,
                            pos      = pos) 

        # creation of the part
        fc_clss.SinglePart.__init__(self)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): 
                setattr(self, i, values[i])


        self.set_line_width(1.)
        self.set_point_size(1.)
        self.set_line_color((.2, .2, .2))


#AluProf = PartAluProf(depth = 200,
#                      #aluprof_dict = kcomp.ALU_MOTEDIS_30B8,
#                      aluprof_dict = kcomp.ALU_MAKERBEAM_15,
#                      #xtr_d=10, xtr_nd=20,
#                      axis_d = VX, axis_w = VY, axis_h = V0,
#                      #pos_d = 3, pos_w = 1, pos_h = -2,
#                      pos = V0)


            
# ----------- NEMA MOTOR
# Creates NEMA motor including its hole to cut the piece where is going
# to be embebbed. 

# ARGUMENTS:
# size: size of the motor: 11, 14, 17, 23, 34 or 42
# length: length of the motor
# shaft_l: length of the motor shaft
# chmf: the chamfer of the corners, as it were a radius
#       0: no chamfer
# circle_r: the radius of the little circle on the base of the shaft.
#           if 0, not defined, I will take the half of the bolt separation 
# circle_h: the height of the circle. If cero, no circle
# rshaft_l: length of the motor the rear shaft. 0 if it doesn't have
# bolt_depth: depth of the bolts holes inside the motor. 
# bolt_out: length of the bolts holes outside the motor
# container: 1: if you want to have a container to make a hole to fit it in
#               a piece
# normal: direction of the shaft
# pos   : position of the base of the shaft. Not considering the circle that
#         usually is on the base of the shaft

# ATTRIBUTES: all the arguments, and:
# shaft_d: diameter of the motor shaft
# fco: the FreeCad Object of the motor
# shp_cont: the container of the motor. To cut other pieces. It is a shape
#           not a FreeCad Object (fco)
# fco_cont: Having problems with shapes and fco. So I will do it with fco 
#           instead of shapes  To cut other pieces.
#           Make decision about how to finally do it

# base_place: position of the 2 elements: All of them have the same base
#             position.
#             It is (0,0,0) when initialized, it has to be changed using the
#             function base_place

#  Bolts need to be debugged, for some cases they don't work properly
#                _____     ______
#               |_____|    ______+ extra: 1 mm
#               |     |         |
#               |_____|         + bolt_out
#                 | |           |
#               __|_|_____ _____j
#              |  : :           + bolt_depth 
#              |  :_:      _____|
#              |  
#

class NemaMotor (object):
    """ Not recommended for new designs, see ShpNemaMotor and PartNemaMotor
    """

    def __init__ (self, size, length, shaft_l, 
                  circle_r, circle_h, name = "nemamotor", chmf = 1, 
                  rshaft_l=0, bolt_depth = 3, bolt_out = 2, container=1,
                  normal = VZ, pos = V0):

        doc = FreeCAD.ActiveDocument
        self.base_place = (0,0,0)
        self.size     = size
        self.width    = kcomp.NEMA_W[size]
        self.length   = length
        self.shaft_l  = shaft_l
        self.shaft_d  = kcomp.NEMA_SHAFT_D[size]
        self.circle_r = circle_r
        self.circle_h = circle_h
        self.chmf     = chmf
        self.rshaft_l = rshaft_l
        self.bolt_depth = bolt_depth
        self.bolt_out = bolt_out
        self.container = container
        nnormal = DraftVecUtils.scaleTo(normal,1)
        self.normal = nnormal
        self.pos = pos
        nemabolt_d = kcomp.NEMA_BOLT_D[size]
        self.nemabolt_d = nemabolt_d
        mtol = kcomp.TOL - 0.1

        lnormal = DraftVecUtils.scaleTo(nnormal,length)
        neg_lnormal = DraftVecUtils.neg(lnormal)

        # motor shape
        v1 = FreeCAD.Vector(self.width/2.-chmf, self.width/2.,0)
        v2 = FreeCAD.Vector(self.width/2.,   self.width/2.-chmf,0)
        motorwire = fcfun.wire_sim_xy([v1,v2])
        # motor wire normal is VZ
        # DraftVecUtils doesnt work as well
        # rot = DraftVecUtils.getRotation(VZ, nnormal)
        # the order matter VZ, nnormal. It seems it doent matter VZ or VZN
        # this is valid:
        #rot = DraftGeomUtils.getRotation(VZ,nnormal)
        #print rot
        rot = FreeCAD.Rotation(VZ,nnormal)
        print(rot)
        motorwire.Placement.Rotation = rot
        motorwire.Placement.Base = pos
        motorface = Part.Face(motorwire)
        shp_motorbox = motorface.extrude(neg_lnormal)
        # shaft shape
        if rshaft_l == 0: # no rear shaft
            shp_shaft = fcfun.shp_cyl (
                               r=self.shaft_d/2.,
                               h= shaft_l,
                               normal = nnormal,
                               pos = pos)
        else:
            rshaft_posend = DraftVecUtils.scaleTo(neg_lnormal, rshaft_l+length)
            shp_shaft = fcfun.shp_cyl (
                               r = self.shaft_d/2.,
                               h = shaft_l + rshaft_l + length,
                               normal = nnormal,
                               pos = pos + rshaft_posend)
                               
        shp_motorshaft = shp_motorbox.fuse(shp_shaft)
        # Bolt holes
        # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        # There is something wrong with the position of these bolts
#        bhole00_pos = FreeCAD.Vector(-kcomp.NEMA_BOLT_SEP[size]/2,
#                                     -kcomp.NEMA_BOLT_SEP[size]/2,
#                                     -bolt_depth) + pos
#        bhole01_pos = FreeCAD.Vector(-kcomp.NEMA_BOLT_SEP[size]/2,
#                                      kcomp.NEMA_BOLT_SEP[size]/2,
#                                     -bolt_depth) + pos
#        bhole10_pos = FreeCAD.Vector( kcomp.NEMA_BOLT_SEP[size]/2,
#                                     -kcomp.NEMA_BOLT_SEP[size]/2,
#                                     -bolt_depth) + pos
#        bhole11_pos = FreeCAD.Vector( kcomp.NEMA_BOLT_SEP[size]/2,
#                                      kcomp.NEMA_BOLT_SEP[size]/2,
#                                     -bolt_depth) + pos
#        bhole00_posrot = DraftVecUtils.rotate(bhole00_pos, rot.Angle, rot.Axis)
#        bhole01_posrot = DraftVecUtils.rotate(bhole01_pos, rot.Angle, rot.Axis)
#        bhole10_posrot = DraftVecUtils.rotate(bhole10_pos, rot.Angle, rot.Axis)
#        bhole11_posrot = DraftVecUtils.rotate(bhole11_pos, rot.Angle, rot.Axis)
#        shp_bolt00 = fcfun.shp_cyl (
#                                   r=kcomp.NEMA_BOLT_D[size]/2.+kcomp.TOL/2.,
#                                   h=bolt_depth + shaft_l,
#                                   normal = nnormal,
#                                   pos= bhole00_posrot)
#        shp_bolt01 = fcfun.shp_cyl ( 
#                                   r=kcomp.NEMA_BOLT_D[size]/2.+kcomp.TOL/2.,
#                                   h=bolt_depth + shaft_l,
#                                   normal = nnormal,
#                                   pos= bhole01_posrot)
#        shp_bolt10 = fcfun.shp_cyl (
#                                   r=kcomp.NEMA_BOLT_D[size]/2.+kcomp.TOL/2.,
#                                   h=bolt_depth + shaft_l,
#                                   normal = nnormal,
#                                   pos= bhole10_posrot)
#        shp_bolt11 = fcfun.shp_cyl (
#                                   r=kcomp.NEMA_BOLT_D[size]/2.+kcomp.TOL/2.,
#                                   h=bolt_depth + shaft_l,
#                                   normal = nnormal,
#                                   pos= bhole11_posrot)
#        shp_bolts = shp_bolt00.multiFuse([shp_bolt01, shp_bolt10, shp_bolt11])


        # list of shapes to make a fusion of the container
        shp_contfuselist = []
#        shp_contfuselist.append(shp_bolts)

        b2hole00_pos = FreeCAD.Vector(-kcomp.NEMA_BOLT_SEP[size]/2,
                                      -kcomp.NEMA_BOLT_SEP[size]/2,
                                      -bolt_depth)
        b2hole01_pos = FreeCAD.Vector(-kcomp.NEMA_BOLT_SEP[size]/2,
                                       kcomp.NEMA_BOLT_SEP[size]/2,
                                      -bolt_depth)
        b2hole10_pos = FreeCAD.Vector( kcomp.NEMA_BOLT_SEP[size]/2,
                                      -kcomp.NEMA_BOLT_SEP[size]/2,
                                      -bolt_depth)
        b2hole11_pos = FreeCAD.Vector( kcomp.NEMA_BOLT_SEP[size]/2,
                                       kcomp.NEMA_BOLT_SEP[size]/2,
                                      -bolt_depth)

        b2hole00 = addBolt (
            r_shank = nemabolt_d/2. + mtol/2.,
            l_bolt = bolt_out + bolt_depth,
            r_head = kcomp.D912_HEAD_D[nemabolt_d]/2. + mtol/2.,
            l_head = kcomp.D912_HEAD_L[nemabolt_d] + mtol,
            hex_head = 0, extra =1, support=1, headdown = 0, name ="b2hole00")

        b2hole01 = Draft.clone(b2hole00)
        b2hole01.Label = "b2hole01"
        b2hole10 = Draft.clone(b2hole00)
        b2hole10.Label = "b2hole10"
        b2hole11 = Draft.clone(b2hole00)
        b2hole11.Label = "b2hole11"

        b2hole00.ViewObject.Visibility=False
        b2hole01.ViewObject.Visibility=False
        b2hole10.ViewObject.Visibility=False
        b2hole11.ViewObject.Visibility=False

        b2hole00.Placement.Base = b2hole00_pos
        b2hole01.Placement.Base = b2hole01_pos
        b2hole10.Placement.Base = b2hole10_pos
        b2hole11.Placement.Base = b2hole11_pos

        # it doesnt work if dont recompute here! probably the clones
        doc.recompute()

        b2holes_list = [b2hole00, b2hole01, b2hole10, b2hole11]
        # not an efficient way, either use shapes or fco, but not both
        shp_b2holes = b2hole00.Shape.multiFuse([b2hole01.Shape,
                                                b2hole10.Shape,
                                                b2hole11.Shape])
        #Part.show(shp_b2holes)

        b2holes = doc.addObject("Part::MultiFuse", "b2holes")
        b2holes.Shapes = b2holes_list
        b2holes.ViewObject.Visibility=False

        shp_b2holes.Placement.Base = pos
        shp_b2holes.Placement.Rotation = rot
        shp_contfuselist.append(shp_b2holes)


        # Circle on the base of the shaft
        if circle_r == 0:
            calcircle_r = kcomp.NEMA_BOLT_SEP[size]/2.
        else:
            calcircle_r = circle_r
        if circle_h != 0:
            shp_circle = fcfun.shp_cyl (
                               r=calcircle_r,
                               h= circle_h + 1, #supperposition for union
                               normal = nnormal,
                               #supperposition for union
                               pos = pos - nnormal)
            # fmotor: fused motor
            shp_fmotor = shp_motorshaft.fuse(shp_circle)
        else:
            shp_fmotor = shp_motorshaft

        #fmotor = doc.addObject("Part::Feature", "fmotor")
        #fmotor.Shape = shp_fmotor

        #shp_motor = shp_fmotor.cut(shp_bolts)
        shp_motor = shp_fmotor.cut(shp_b2holes)
        #Part.show(shp_bolts)
        
        # container
        if container == 1:
            # 2*TOL to make sure it fits
            v1 = FreeCAD.Vector(self.width/2.-chmf/2. + 2*kcomp.TOL,
                                self.width/2. + 2*kcomp.TOL, 0)
            v2 = FreeCAD.Vector(self.width/2.+ 2*kcomp.TOL,
                                self.width/2.-chmf/2. + 2*kcomp.TOL,0)
            cont_motorwire = fcfun.wire_sim_xy([v1,v2])
            cont_motorwire.Placement.Rotation = rot
            cont_motorwire.Placement.Base = pos
            cont_motorface = Part.Face(cont_motorwire)
            shp_contmotor_box = cont_motorface.extrude(neg_lnormal)

            # the container is much wider than the shaft

            if rshaft_l == 0: # no rear shaft
                shp_contshaft = fcfun.shp_cyl (
                                   r=calcircle_r + kcomp.TOL,
                                   h= shaft_l + 1,
                                   normal = nnormal,
                                   pos = pos - nnormal )
            else:
                shp_contshaft = fcfun.shp_cyl (
                                   r=calcircle_r + kcomp.TOL,
                                   h= shaft_l + rshaft_l + length,
                                   normal = nnormal,
                                   pos = pos + rshaft_posend)
            shp_contfuselist.append(shp_contshaft)
            shp_contmotor = shp_contmotor_box.multiFuse(shp_contfuselist)
        else:
            shp_contmotor = shp_motor # we put the same shape
        

        doc.recompute()

        #fco_motor = doc.addObject("Part::Cut", name)
        #fco_motor.Base = fmotor
        #fco_motor.Tool = b2holes
        fco_motor = doc.addObject("Part::Feature", name)
        fco_motor.Shape = shp_motor

        self.fco = fco_motor
        self.shp_cont = shp_contmotor
        #Part.show(shp_contmotor)


        doc.recompute()


   # Move the motor and its container
    def BasePlace (self, position = (0,0,0)):
        self.base_place = position
        self.fco.Placement.Base = FreeCAD.Vector(position)
        #self.shp_cont.Placement.Base = FreeCAD.Vector(position)
        self.fco_cont.Placement.Base = FreeCAD.Vector(position)

#doc =FreeCAD.newDocument()

# Revisar este caso AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
# con los bolts
#nm = NemaMotor(size=17, length=40, shaft_l=24, circle_r = 0,
#               circle_h=2, name='nema17', chmf=2.,
#               rshaft_l = 10, bolt_depth = 3, bolt_out=5,
#               #normal= FreeCAD.Vector(1,-0.75,1), pos = FreeCAD.Vector(0,5,2))
#               normal= FreeCAD.Vector(0,0,-1), pos = FreeCAD.Vector(-2,5,2))


# ----------- NEMA MOTOR

class ShpNemaMotor (shp_clss.Obj3D):
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

    def __init__ (self,
                  nema_size = 17,
                  base_l = 32.,
                  shaft_l = 24.,
                  shaft_r = 0,
                  circle_r = 11.,
                  circle_h = 2.,
                  chmf_r = 1, 
                  rear_shaft_l=0,
                  bolt_depth = 3.,
                  bolt_out = 2,
                  cut_extra = 0,
                  axis_d = VX,
                  axis_w = None,
                  axis_h = VZ,
                  pos_d = 0,
                  pos_w = 0,
                  pos_h = 1,
                  pos = V0):

        if (axis_w is None) or (axis_w == V0):
            axis_w = axis_h.cross(axis_d)

        shp_clss.Obj3D.__init__(self, axis_d, axis_w, axis_h)

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

#doc =FreeCAD.newDocument()
#snm = ShpNemaMotor(
#                  cut_extra = 1,
#                  pos_d = 2,
#                  pos_w = 1,
#                  pos_h = 1,
#)
#Part.show(snm.shp)

class PartNemaMotor (fc_clss.SinglePart, ShpNemaMotor):
    """ Integration of a ShpNemaMotor objecto into a PartNemaMotor object
    so it will create a FreeCAD object that can be shown in FreeCAD GUI
    See ShpNemaMotor to get info about the parameters
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
                  name = ''):

        default_name = 'nema' + str(nema_size) + '_motor_l' + str(int(base_l))
        self.set_name (name, default_name, change = 0)
        # First the shape is created
        ShpNemaMotor.__init__(self,
                    nema_size = nema_size,
                    base_l = base_l,
                    shaft_l = shaft_l,
                    shaft_r = shaft_r,
                    circle_r = circle_r,
                    circle_h = circle_h,
                    chmf_r = chmf_r, 
                    rear_shaft_l = rear_shaft_l,
                    bolt_depth = bolt_depth,
                    bolt_out = bolt_out,
                    cut_extra = cut_extra,
                    axis_d = axis_d,
                    axis_w = axis_w,
                    axis_h = axis_h,
                    pos_d = pos_d,
                    pos_w = pos_w,
                    pos_h = pos_h,
                    pos = pos)

        # Second, the part is created
        fc_clss.SinglePart.__init__(self)

        # Save the arguments that have not been created yet
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): 
                setattr(self, i, values[i])

        self.model_type = 1 # Dimensional model


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

class LinBearing (object):

    def __init__ (self, r_ext, r_int, h, name, axis = 'z', h_disp = 0,
                  r_tol = 0, h_tol = 0):

        self.base_place = (0,0,0)
        self.r_ext  = r_ext
        self.r_int  = r_int
        self.h      = h
        self.name   = name
        self.axis   = axis
        self.h_disp = h_disp
        self.r_tol  = r_tol
        self.h_tol  = h_tol

        bearing = fcfun.addCylHole (r_ext = r_ext,
                              r_int = r_int,
                              h= h,
                              name = name,
                              axis = axis,
                              h_disp = h_disp)
        self.bearing = bearing

        bearing_cont = fcfun.addCyl_pos (r = r_ext + r_tol,
                                         h= h + h_tol,
                                         name = name + "_cont",
                                         axis = axis,
                                         h_disp = h_disp - h_tol/2.0)
        # Hide the container
        self.bearing_cont = bearing_cont
        if bearing_cont.ViewObject != None:
            bearing_cont.ViewObject.Visibility=False


    # Move the bearing and its container
    def BasePlace (self, position = (0,0,0)):
        self.base_place = position
        self.bearing.Placement.Base = FreeCAD.Vector(position)
        self.bearing_cont.Placement.Base = FreeCAD.Vector(position)


# ---------- class LinBearingClone ----------------------------------------
# Creates an object that is like LinBearing, but it has clones of it
# instead of original Cylinders
# h_bearing: is a LinBearing object. It has the h to indicate that it is
#            a handler, not a FreeCAD object. To get to the FreeCad object
#            take the attributes: bearing and bearing_cont (container)
# name     : name of the objects, depending on namadd, it will add it
#            to the original or not
# namadd   : 1: add to the original name
#            0: creates a new name

class LinBearingClone (LinBearing):

    def __init__ (self, h_bearing, name, namadd = 1):
        self.base_place = h_bearing.base_place
        self.r_ext      = h_bearing.r_ext
        self.r_int      = h_bearing.r_int
        self.h          = h_bearing.h
        if namadd == 1:
            self.name       = h_bearing.name + "_" + name
        else:
            self.name       = name
        self.axis       = h_bearing.axis
        self.h_disp     = h_bearing.h_disp
        self.r_tol      = h_bearing.r_tol
        self.h_tol      = h_bearing.h_tol

        bearing_clone = Draft.clone(h_bearing.bearing)
        bearing_clone.Label = self.name
        self.bearing = bearing_clone

        bearing_cont_clone = Draft.clone(h_bearing.bearing_cont)
        bearing_cont_clone.Label = self.name + "_cont"
        self.bearing_cont = bearing_cont_clone
        if bearing_cont_clone.ViewObject != None:
            bearing_cont_clone.ViewObject.Visibility=False


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

class T8Nut (object):

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

    def __init__ (self, name, nutaxis = 'x'):
        doc = FreeCAD.ActiveDocument
        self.name = name
        self.nutaxis = nutaxis

        flange_cyl = addCyl_pos (r = self.FlangeR,
                                 h = self.FlangeL,
                                 name = "flange_cyl",
                                 axis = 'z',
                                 h_disp = - self.FlangeL)
                      
        shaft_cyl = addCyl_pos ( r = self.ShaftR,
                                 h = self.NutL,
                                 name = "shaft_cyl",
                                 axis = 'z',
                                 h_disp = - self.NutL + self.ShaftOut)

        holes_list = []
                      
        leadscrew_hole = addCyl_pos ( r = self.LeadScrewR,
                                      h = self.NutL + 2,
                                      name = "leadscrew_hole",
                                      axis = 'z',
                                      h_disp = - self.NutL + self.ShaftOut -1)
        holes_list.append (leadscrew_hole)

        flangebolt_hole1 = addCyl_pos ( r = self.FlangeBoltHoleD/2.0,
                                         h = self.FlangeL + 2,
                                         name = "flangebolt_hole1",
                                         axis = 'z',
                                         h_disp = - self.FlangeL -1)
        flangebolt_hole1.Placement.Base.x = self.FlangeBoltPosD /2.0
        holes_list.append (flangebolt_hole1)
       
        flangebolt_hole2 = addCyl_pos ( r = self.FlangeBoltHoleD/2.0,
                                         h = self.FlangeL + 2,
                                         name = "flangebolt_hole2",
                                         axis = 'z',
                                         h_disp = - self.FlangeL -1)
        flangebolt_hole2.Placement.Base.x = - self.FlangeBoltPosD /2.0
        holes_list.append (flangebolt_hole2)
       
        flangebolt_hole3 = addCyl_pos ( r = self.FlangeBoltHoleD/2.0,
                                         h = self.FlangeL + 2,
                                         name = "flangebolt_hole3",
                                         axis = 'z',
                                         h_disp = - self.FlangeL -1)
        flangebolt_hole3.Placement.Base.y = self.FlangeBoltPosD /2.0
        holes_list.append (flangebolt_hole3)
       
        flangebolt_hole4 = addCyl_pos ( r = self.FlangeBoltHoleD/2.0,
                                         h = self.FlangeL + 2,
                                         name = "flangebolt_hole4",
                                         axis = 'z',
                                         h_disp = - self.FlangeL -1)
        flangebolt_hole4.Placement.Base.y = - self.FlangeBoltPosD /2.0
        holes_list.append (flangebolt_hole4)

        nut_holes = doc.addObject("Part::MultiFuse", "nut_holes")
        nut_holes.Shapes = holes_list

        nut_cyls = doc.addObject("Part::Fuse", "nut_cyls")
        nut_cyls.Base = flange_cyl
        nut_cyls.Tool = shaft_cyl

        if nutaxis == 'x':
            vrot = FreeCAD.Rotation (VY,90)
        elif nutaxis == '-x':
            vrot= FreeCAD.Rotation (VY,-90)
        elif nutaxis == 'y':
            vrot= FreeCAD.Rotation (VX,-90)
        elif nutaxis == '-y':
            vrot = FreeCAD.Rotation (VX,90)
        elif nutaxis == '-z':
            vrot = FreeCAD.Rotation (VX,180)
        else: # nutaxis =='z' no rotation
            vrot = FreeCAD.Rotation (VZ,0)

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

class T8NutHousing (object):

    Length = kcomp.T8NH_L
    Width  = kcomp.T8NH_W
    Height = kcomp.T8NH_H

    # separation between the bolts that attach to the moving part
    BoltLenSep  = kcomp.T8NH_BoltLSep
    BoltWidSep  = kcomp.T8NH_BoltWSep

    # separation between the bolts to the end
    BoltLen2end = (Length - BoltLenSep)/2
    BoltWid2end = (Width  - BoltWidSep)/2

    # Bolt dimensions, that attach to the moving part: M4 x 7
    BoltD = kcomp.T8NH_BoltD
    BoltR = BoltD / 2.0
    BoltL = kcomp.T8NH_BoltL + kcomp.TOL

    # Hole for the nut and the leadscrew
    ShaftD = kcomp.T8N_D_SHAFT_EXT + kcomp.TOL # I don't know the tolerances
    ShaftR = ShaftD / 2.0
    FlangeD = kcomp.T8N_D_FLAN + kcomp.TOL # I don't know the tolerances
    FlangeR = FlangeD / 2.0
    FlangeL = kcomp.T8N_FLAN_L + kcomp.TOL
    FlangeBoltD = kcomp.T8NH_FlanBoltD
    FlangeBoltR = FlangeBoltD / 2.0
    FlangeBoltL = kcomp.T8NH_FlanBoltL + kcomp.TOL
    # Diameter where the Flange Bolts are located
    FlangeBoltPosD = kcomp.T8N_D_BOLT_POS
  
    def __init__ (self, name, nutaxis = 'x', screwface_axis = 'z',
                  cx = 1, cy= 1, cz = 0):
        self.name = name
        self.nutaxis = nutaxis
        self.screwface_axis = screwface_axis
        self.cx = cx
        self.cy = cy
        self.cz = cz

        doc = FreeCAD.ActiveDocument
        # centered so it can be rotated without displacement, and everything
        # will be in place
        housing_box = fcfun.addBox_cen (self.Length, self.Width, self.Height,
                                  name= name + "_box", 
                                  cx=True, cy=True, cz=True)

        hole_list = []

        leadscr_hole = addCyl_pos (r=self.ShaftR, h= self.Length + 1,
                                   name = "leadscr_hole",
                                   axis = 'x', h_disp = -self.Length/2.0-1)
        hole_list.append(leadscr_hole)
        nutflange_hole = addCyl_pos (r=self.FlangeR, h= self.FlangeL + 1,
                                   name = "nutflange_hole",
                                   axis = 'x',
                                   h_disp = self.Length/2.0 - self.FlangeL)
        hole_list.append(nutflange_hole)
        # bolts to attach the nut flange to the housing
        # M3 x 10
        boltflange_l = addCyl_pos (r = self.FlangeBoltR,
                                    h = self.FlangeBoltL + 1,
                                    name = "boltflange_l",
                                    axis = 'x',
                                    h_disp =   self.Length/2.0
                                             - self.FlangeL
                                             - self.FlangeBoltL)
        boltflange_l.Placement.Base = FreeCAD.Vector(0,
                                    - self.FlangeBoltPosD / 2.0,
                                   )
        hole_list.append(boltflange_l)
        boltflange_r = addCyl_pos (r = self.FlangeBoltR,
                                    h = self.FlangeBoltL + 1,
                                    name = "boltflange_r",
                                    axis = 'x',
                                    h_disp =   self.Length/2.0
                                             - self.FlangeL
                                             - self.FlangeBoltL)
        boltflange_r.Placement.Base = FreeCAD.Vector (0,
                                   self.FlangeBoltPosD / 2.0,
                                   0)
        hole_list.append(boltflange_r)


        # bolts to attach the housing to the moving part
        # M4x7
        boltface_1 = fcfun.addCyl_pos (r = self.BoltR, h = self.BoltL + 1,
                                        name="boltface_1",
                                        axis = 'z',
                                        h_disp = -self.Height/2 -1)
        boltface_1.Placement.Base = FreeCAD.Vector (
                                    - self.Length/2.0 + self.BoltLen2end,
                                    - self.Width/2.0 + self.BoltWid2end,
                                      0)
        hole_list.append (boltface_1)
        boltface_2 = fcfun.addCyl_pos (r = self.BoltR, h = self.BoltL + 1,
                                        name="boltface_2",
                                        axis = 'z',
                                        h_disp = -self.Height/2 -1)
        boltface_2.Placement.Base = FreeCAD.Vector(
                                      self.BoltLenSep /2.0,
                                    - self.Width/2.0 + self.BoltWid2end,
                                      0)
        hole_list.append (boltface_2)
        boltface_3 = fcfun.addCyl_pos (r = self.BoltR, h = self.BoltL + 1,
                                        name="boltface_3",
                                        axis = 'z',
                                        h_disp = -self.Height/2 -1)
        boltface_3.Placement.Base = FreeCAD.Vector (
                                    - self.Length/2.0 + self.BoltLen2end,
                                      self.BoltWidSep /2.0,
                                      0)
        hole_list.append (boltface_3)
        boltface_4 = fcfun.addCyl_pos (r = self.BoltR, h = self.BoltL + 1,
                                        name="boltface_4",
                                        axis = 'z',
                                        h_disp = -self.Height/2 -1)
        boltface_4.Placement.Base = FreeCAD.Vector(
                                      self.BoltLenSep /2.0,
                                      self.BoltWidSep /2.0,
                                      0)
        hole_list.append (boltface_4)
        nuthouseholes = doc.addObject ("Part::MultiFuse", "nuthouse_holes")
        nuthouseholes.Shapes = hole_list
       
        # rotation vector calculation
        if nutaxis == 'x':
            vec1 = (1,0,0)
        elif nutaxis == '-x':
            vec1 = (-1,0,0)
        elif nutaxis == 'y':
            vec1 = (0,1,0)
        elif nutaxis == '-y':
            vec1 = (0,-1,0)
        elif nutaxis == 'z':
            vec1 = (0,0,1)
        elif nutaxis == '-z':
            vec1 = (0,0,-1)

        if screwface_axis == 'x':
            vec2 = (1,0,0)
        elif screwface_axis == '-x':
            vec2 = (-1,0,0)
        elif screwface_axis == 'y':
            vec2 = (0,1,0)
        elif screwface_axis == '-y':
            vec2 = (0,-1,0)
        elif screwface_axis == 'z':
            vec2 = (0,0,1)
        elif screwface_axis == '-z':
            vec2 = (0,0,-1)

        vrot = fcfun.calc_rot (vec1,vec2)
        vdesp = fcfun.calc_desp_ncen (
                                      Length = self.Length,
                                      Width = self.Width,
                                      Height = self.Height,
                                      vec1 = vec1, vec2 = vec2,
                                      cx = cx, cy=cy, cz=cz)

        housing_box.Placement.Rotation = vrot
        nuthouseholes.Placement.Rotation = vrot
        housing_box.Placement.Base = vdesp
        nuthouseholes.Placement.Base = vdesp

        t8nuthouse = doc.addObject ("Part::Cut", "t8nuthouse")
        t8nuthouse.Base = housing_box
        t8nuthouse.Tool = nuthouseholes

        self.fco = t8nuthouse  # the FreeCad Object



# ---------- class MisumiMinLeadscrewNut ----------------------
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
#
#             Z
#             :
#             :                           this is rounded
#           __:                        : _______ :
#          |..|   Y                    :/       \:
#          |..|  /                     | O     O |
#    ______|  | /                      |   ___   | This is flat
#   |      |  |/                       |  /   \  |
#  -|------|--|----- nutaxis (X)       | |  x--|-|------ Y
#   |______|  |                        |  \_:_/  |  cutaxis (z)
#          |..|                        |    :    |
#          |..|                        | O  :  O |
#          |__|                         \ __:__ /
#             :                             :
#             :                             :
#             + Zero. Plane YZ=0            -Z roundflan_axis (-Z) (also (Z)
#             :
#             -Z (roundflan_axis
#
# Parameters
# - thread_d: thread diameter
# - sh_ext_d: exterior diameter of the nut shaft
# - flan_d :  diameter of flange
# - H :       height (or length) of the nut
# - flan_cut: Cut of the flange (compact nut)
# - bolt_pos_d: Diameter of the position of the bolt holes
# - bolt_d: Diameter of the position of the bolt holes
# - bolt_ang: Angle of the position of the bolts, referred to the vertical
#             in degrees
# - nutaxis: 'x', '-x', 'y', '-y', 'z', '-z': axis of the leadscrew.
#             Positive or negative will change the orientation:
#                                   ___
#               nutaxis = 'z'      |   |
#                     :          __|   |__
#                 ____:____ . . |_________| . . .  z = 0
#                |__     __|         :
#                   |   |            :
#                   |___|          nutaxis = '-z'
#
#
# - cutaxis: 'x', 'y', 'z' : axis parallel the cut of the flange.
#            it doesn't matter positive or negative, because it is symmetrical
#            But it would not be an error
#
#             Z
#             :
#             :
#           / : \
#          |  :  |   cutaxis = 'z'
#          |  :  |
#          |  :..|...... Y
#          |     |
#          |     |
#          |     |
#           \ _ /
#            
#            
# - axis_pos: position of the nut along its axis. The position is independent
#             on the sign of nutaxis. So the sign it is not referenced to
#             the sign of nutaxis



class MisMinLScrNut (object):

    def __init__ (self, thread_d, sh_ext_d,
                  flan_d, H, flan_h, flan_cut, 
                  bolt_pos_d, bolt_d, bolt_ang = 30,
                  nutaxis='x',
                  cutaxis = '-z',
                  name='lscrew_nut',
                  axis_pos = 0):

        self.thread_d = thread_d
        self.sh_ext_d = sh_ext_d
        self.flan_d = flan_d
        self.H = H
        self.flan_h = flan_h
        self.flan_cut = flan_cut
        self.bolt_pos_d = bolt_pos_d 
        self.bolt_d = bolt_d
        self.bolt_ang = bolt_ang
        self.bolt_ang_rad = math.radians(bolt_ang)
        self.nutaxis = nutaxis
        self.cutaxis = cutaxis

        # to make it independent on the orientation of the nut
        if nutaxis == '-x' or nutaxis == '-y' or nutaxis == '-z':
            ax_pos_sign = - axis_pos
        else:
            ax_pos_sign = axis_pos

        self.ax_pos_sign = ax_pos_sign

        doc = FreeCAD.ActiveDocument
        basepos = FreeCAD.Vector(ax_pos_sign, 0,0)

        # Flange Cylinder
        flange_cyl = fcfun.shp_cyl (r= flan_d/2.,
                                    h= flan_h,
                                    normal = VXN, 
                                    pos = basepos)
        #Part.show(flange_cyl)
        # Box that will make the intersection with the flange to make the cut
        # Since the nut axis is on X, that will be the flan_h
        # the Cut is on Y
        flange_box = fcfun.shp_boxcen (
                               x = flan_h,
                               y = flan_cut,
                               z = flan_d,
                               cx=0, cy=1, cz=1,
                               pos = FreeCAD.Vector(-flan_h+ax_pos_sign,0,0))
        #Part.show(flange_box)
        flange_cut = flange_cyl.common(flange_box)
        #Part.show(flange_cut)
        # Nut Cylinder
        nut_cyl = fcfun.shp_cyl (r = sh_ext_d/2,
                                 h = H,
                                 normal = VXN, 
                                 pos = basepos)
        nut_shape = nut_cyl.fuse(flange_cut)
        # ----------------- Hole for the thread
        thread_hole = fcfun.shp_cylcenxtr (
                                 r = thread_d/2,
                                 h = H ,
                                 normal = VXN, 
                                 ch = 0,
                                 xtr_top = 1,
                                 xtr_bot = 1,
                                 pos = basepos)

        #  -------- Holes in the flange for the bolts
        # Position on Axis Z, It will be rotated 30 degrees
        bolthole_pos_z = FreeCAD.Vector(0,0,bolt_pos_d/2.)
        # the 4 angles that rotate bolthole_pos_z :
        angle = self.bolt_ang_rad
        rot_angles = [angle, -angle, angle + math.pi, -angle + math.pi]
        bolthole_list = []
        for angle_i in rot_angles:
            bolthole_pos_i = DraftVecUtils.rotate(bolthole_pos_z,
                                                    angle_i,
                                                    VX)
            bolthole_i = fcfun.shp_cylcenxtr (r=bolt_d/2.,
                                              h=flan_h,
                                              normal= VXN,
                                              ch=0,
                                              xtr_top=1,
                                              xtr_bot=1,
                                              pos = bolthole_pos_i + basepos)
            #Part.show(bolthole_i)
            bolthole_list.append(bolthole_i) 

        # fusion of holes
        nutholes = thread_hole.multiFuse(bolthole_list)

        # rotation of the nut and the holes before the cut
        vrot = fcfun.calc_rot(fcfun.getvecofname(nutaxis),
                              fcfun.getvecofname(cutaxis))
        nutholes.Placement.Rotation = vrot
        nut_shape.Placement.Rotation = vrot
        shp_lscrewnut = nut_shape.cut(nutholes)
        shp_lscrewnut = shp_lscrewnut.removeSplitter()
        #Part.show(shp_lscrewnut)

        # Creation of the FreeCAD Object

        fco_lscrewnut = doc.addObject("Part::Feature", name)
        fco_lscrewnut.Shape = shp_lscrewnut
        self.fco = fco_lscrewnut
        self.shp = shp_lscrewnut
        

        

# creates a misumi miniature leadscrew nut using a dictionary from kcomp


def get_mis_min_lscrnut (nutdict,
                         nutaxis='x',
                         cutaxis='-z',
                         name='lscrew_nut',
                         axis_pos = 0):

    h_lscrew = MisMinLScrNut (
                              thread_d = nutdict['T'],
                              sh_ext_d = nutdict['sh_ext_d'],
                              flan_d   = nutdict['flan_d'],
                              H        = nutdict['H'],
                              flan_h   = nutdict['flan_h'],
                              flan_cut = nutdict['flan_cut'], 
                              bolt_pos_d = nutdict['bolt_pos_d'],
                              bolt_d     = nutdict['bolt_d'],
                              bolt_ang   = nutdict['bolt_ang'],
                              nutaxis    = nutaxis,
                              cutaxis    = cutaxis,
                              name       = name,
                              axis_pos   = axis_pos)

    return h_lscrew


#get_mis_min_lscrnut (kcomp.MIS_LSCRNUT_C_L1_T4, 
#                     nutaxis = 'y',
#                     cutaxis = 'x',
#                     name = 'lscrew_nut',
#                     axis_pos = 10) 


#  -------------------- FlexCoupling
# Creates a flexible Shaft Coupling
# ARGUMENTS:
# ds: diameter of the smaller shaft
# dl: diameter of the larger shaft
# ctype: rb, xb
# axis: 'x', 'y' or 'z'
#           'x' will along the x axis
#           'y' will along the y axis
#           'z' will be vertical
# center: 1, 0: centered or not on the axis
# larg_neg: 1, 0: if the large diameter is on the negative side or not
# ATTRIBUTES
# The arguments and:
# length: Length of the coupler
# diam: External diameter of the coupler
# fco: The freecad object

class FlexCoupling (object):

    def __init__ (self, ds, dl, ctype='rb', name='flexcoupling',
                  axis='z', center = 1, larg_neg = 1):

        doc = FreeCAD.ActiveDocument
        self.ds = ds 
        self.dl = ds 
        self.ctype = ctype 
        self.axis = axis 
        self.center = center 
        self.larg_neg = larg_neg 
        self.name = name 

        if ctype == 'rb':
            self.length = kcomp.FLEXSC_RB_L[(ds,dl)]
            self.diam = kcomp.FLEXSC_RB_D[(ds,dl)]
        else:
            logger.error('Type not yet defined')

        # Shape of the larger diameter
        if larg_neg == 1:
            hpos_larg = -self.length/2
            hpos_smal = 0
        else:
            hpos_larg = -1  # superposition
            hpos_smal = -self.length/2
        shp_dl = fcfun.shp_cylhole (self.diam/2., dl/2., self.length/2.+1,
                                    axis=axis, h_disp = hpos_larg)
        shp_ds = fcfun.shp_cylhole (self.diam/2., ds/2., self.length/2.,
                                    axis=axis, h_disp = hpos_smal)

        shp_FlexCoupling = shp_dl.fuse(shp_ds)

        doc.recompute()
        fco_FlexCoupling = doc.addObject ("Part::Feature", name)
        fco_FlexCoupling.Shape = shp_FlexCoupling

        self.fco = fco_FlexCoupling
     

# ---------------------- LinGuide -----------------------------------

# ---------------------- LinGuideRail -------------------------------
# Makes the Rail of a linear guide
# Arguments:
# rail_l : length of the rail
# rail_w : width of the rail
# rail_h : height of the rail
# bolt_lsep : separation between bolts on the length dimension
# bolt_wsep : separation between bolts on the width dimension, it it is 0
#             there is only one bolt
# bolt_d : diameter of the hole for the bolt
# bolth_d : diameter of the hole for the head of the bolt
# bolth_h : heigth of the hole for the head of the bolt
# boltend_sep : separation on one end, from the bolt to the end
# axis_l : the axis where the lenght of the rail is: 'x', 'y', 'z'
# axis_b : the axis where the base of the rail is pointing:
#                                 'x',   'y',  'z', '-x', '-y', '-z',
# It will be centered on the width axis, and zero on the length and height
# Optional holes for the bolts, that go beyon the rail to cut 3D printed pieces.
# to be designed. Zero if you dont want to have them
# bolthole_d: diameter of the hole
# bolthole_l: length of the hole
# NOT IMPLEMENTED YET, NOW ONLY ON THE DIRECTION OF AXIS_B (SAME):
# bolthole_dir: direction of the hole, it would be:
#               'same'  same direction of axis_b
#               'opp'   oposite direction of axis_b
#               'both'  both directions
# bolthole_nutd: diameter of the nut 
# bolthole_nuth: length of the nut (including the head)

# name   : name of the freecad object
# Attributes:
# The Arguments and:
# ###shp_face_rail : the shape of the face of the section of the rail
# shp_plainrail : the shape of the plain rail
# nbolt_l : number of bolts lines (can be pairs, counted as one) on the l
#           direction
# fco : the freecad object of the rail

class LinGuideRail (object):

    def __init__ (self, rail_l, rail_w, rail_h,
                  bolt_lsep, bolt_wsep, bolt_d,
                  bolth_d, bolth_h, boltend_sep = 0,
                  axis_l = 'x', axis_b = '-z', name='linguiderail',
                  bolthole_d = 0, bolthole_l = 0, bolthole_dir = 0,
                  bolthole_nutd = 0, bolthole_nuth = 0):

        self.base_place = (0,0,0)
        self.rail_l = rail_l
        self.rail_w = rail_w
        self.rail_h = rail_h
        self.bolt_lsep = bolt_lsep
        self.bolt_wsep = bolt_wsep
        self.bolt_d = bolt_d
        self.bolth_d = bolth_d
        self.bolth_h = bolth_h
        self.axis_l = axis_l
        self.axis_b = axis_b

        doc = FreeCAD.ActiveDocument
        shp_face_rail = fcfun.shp_face_lgrail(rail_w, rail_h, axis_l, axis_b)
        #self.shp_face_rail = shp_face_rail
        # vector on the direction of the rail length. Extrusion
        vdir_l = fcfun.getfcvecofname(axis_l)
        vdir_extr = DraftVecUtils.scaleTo(vdir_l, rail_l)
        shp_plainrail = shp_face_rail.extrude(vdir_extr)
        self.shp_plainrail = shp_plainrail

        if boltend_sep != 0:
            nbolt_l = (rail_l - boltend_sep) // bolt_lsep #integer division
            self.boltend_sep = boltend_sep
        else: # leave even distance
            # number of bolt lines, on the length axis
            nbolt_l = rail_l // bolt_lsep # integer division
            #dont use % in case is not int
            rail_rem = rail_l - nbolt_l * bolt_lsep 
            # separation between the bolt and the end
            self.boltend_sep = rail_rem / 2.
        # there will be one bolt more than nbolt_l
        self.nbolt_l = nbolt_l + 1
        # bolt holes
        bolth_posz = rail_h - bolth_h
        doc.recompute()
        if bolt_wsep == 0: # just one bolt hole per line
            shp_boltshank = fcfun.shp_cyl(r=bolt_d/2., h=rail_h-bolth_h+2,
                              normal=VZ, pos=FreeCAD.Vector(0,0,-1))
            shp_bolthead = fcfun.shp_cyl(r=bolth_d/2., h=bolth_h+1,
                              normal=VZ, pos=FreeCAD.Vector(0,0,bolth_posz))
            shp_bolt = shp_boltshank.fuse(shp_bolthead)
            if bolthole_d != 0:
                fco_bolthole = addBolt(bolthole_d/2., bolthole_l,
                                       bolthole_nutd/2., bolthole_nuth,
                                       hex_head = 1, extra=1, support=1,
                                       headdown = 1, name= name +"_bolthole")
        else:
            shp_boltshank1 = fcfun.shp_cyl(r=bolt_d/2., h=rail_h-bolth_h+2,
                             normal=VZ, pos= FreeCAD.Vector(0,bolt_wsep/2.,-1))
            shp_bolthead1 = fcfun.shp_cyl(r=bolth_d/2., h=bolth_h+1,
                             normal=VZ, 
                             pos=FreeCAD.Vector(0,bolt_wsep/2.,bolth_posz))
            shp_bolt1 = shp_boltshank1.fuse(shp_bolthead1)
            shp_boltshank2 = fcfun.shp_cyl(r=bolt_d/2., h=rail_h-bolth_h+2,
                             normal=VZ,  pos=FreeCAD.Vector(0,-bolt_wsep/2.,-1))
            shp_bolthead2 = fcfun.shp_cyl(r=bolth_d/2., h=bolth_h+1,
                             normal=VZ,
                             pos=FreeCAD.Vector(0,-bolt_wsep/2.,bolth_posz))
            shp_bolt2 = shp_boltshank2.fuse(shp_bolthead2)
            shp_bolt = shp_bolt2.fuse(shp_bolt1)
            if bolthole_d != 0:
                fco_bolthole1 = addBolt(bolthole_d/2., bolthole_l,
                                       bolthole_nutd/2., bolthole_nuth,
                                       hex_head = 1, extra=1, support=1,
                                       headdown = 1, name =name+"_bolthole_1")
                fco_bolthole1.Placement.Base = FreeCAD.Vector(0,bolt_wsep/2.,0)
                fco_bolthole2 = addBolt(bolthole_d/2., bolthole_l,
                                       bolthole_nutd/2., bolthole_nuth,
                                       hex_head = 1, extra=1, support=1,
                                       headdown = 1, name =name +"_bolthole_2")
                fco_bolthole2.Placement.Base =FreeCAD.Vector(0,-bolt_wsep/2.,0)
                fco_bolthole = doc.addObject("Part::Fuse",name+"_bolthole")
                fco_bolthole.Base = fco_bolthole1
                fco_bolthole.Tool = fco_bolthole2

        # Rotation of the bolt holes
        vrot = fcfun.calc_rot(fcfun.getvecofname(axis_l),
                              fcfun.getvecofname(axis_b))
        shp_bolt.Placement.Rotation = vrot

        doc.recompute()
        # replicate the bolt holes:
        
        boltpos = DraftVecUtils.scaleTo(vdir_l, self.boltend_sep)
        addpos = DraftVecUtils.scaleTo(vdir_l, bolt_lsep)
        shp_bolt.Placement.Base = boltpos
        if bolthole_d != 0:
            vdir_b = fcfun.getfcvecofname(axis_b)
            bolthole_posz = DraftVecUtils.scaleTo(vdir_b, rail_h)
            fco_bolthole.Placement.Base = boltpos + bolthole_posz
            fco_bolthole.Placement.Rotation = vrot
            bolthole_list = [ fco_bolthole ]
        shp_bolt_list = []
        # starts on 0, because it is one more bolt than nbolt
        for ibolt in range(0, int(nbolt_l)):
            boltpos += addpos
            shp_bolt_i = shp_bolt.copy()
            shp_bolt_i.Placement.Base = boltpos
            shp_bolt_list.append(shp_bolt_i)
            if bolthole_d != 0:
                fco_bolthole_clone = Draft.clone(fco_bolthole)
                fco_bolthole_clone.Label = fco_bolthole.Label + str(ibolt)
                fco_bolthole_clone.Placement.Base = boltpos + bolthole_posz
                bolthole_list.append(fco_bolthole_clone)
            
        shp_bolts = shp_bolt.multiFuse(shp_bolt_list)

        shp_rail = shp_plainrail.cut(shp_bolts)

        if bolthole_d != 0:
            fco_bolthole = doc.addObject("Part::MultiFuse", name + "_bolt_hole")
            fco_bolthole.Shapes = bolthole_list
            fco_bolthole.ViewObject.Visibility = False
            self.fco_bolthole = fco_bolthole

        doc.recompute()
        fco_rail = doc.addObject("Part::Feature", name)
        fco_rail.Shape = shp_rail
        self.fco = fco_rail

    def BasePlace (self, position = (0,0,0)):
        self.base_place = position
        self.fco.Placement.Base = FreeCAD.Vector(position)


        
# a dictionary is used with the constants. Defined in kcomp.py
# hl = f_linguiderail(200, kcomp.SEBWM16_R, 'y', '-z')
def f_linguiderail (rail_l, d_rail, axis_l, axis_b, boltend_sep = 0,
                    name ='linguiderail'):

    if boltend_sep == 0:
        boltends =  d_rail['boltend_sep']
    else:
        boltends =  boltend_sep

    h_lgrail = LinGuideRail(rail_l    = rail_l,
                            rail_w    = d_rail['rw'],
                            rail_h    = d_rail['rh'],
                            bolt_lsep = d_rail['boltlsep'],
                            bolt_wsep = d_rail['boltwsep'],
                            bolt_d    = d_rail['boltd'],
                            bolth_d   = d_rail['bolthd'],
                            bolth_h   = d_rail['bolthh'],
                            boltend_sep = boltends,
                            axis_l    = axis_l,
                            axis_b    = axis_b,
                            name      = name)

    return h_lgrail

 
# a dictionary is used with the constants. Defined in kcomp.py
# Includes the bolt holes (BH) to pass through another 3D piece
def f_linguiderail_bh (rail_l, d_rail, axis_l, axis_b, boltend_sep = 0,
                  bolthole_d = 0, bolthole_l = 0, bolthole_dir = 0,
                  bolthole_nutd = 0, bolthole_nuth = 0,
                  name ='linguiderail'):

    if boltend_sep == 0:
        boltends =  d_rail['boltend_sep']
    else:
        boltends =  boltend_sep

    h_lgrail = LinGuideRail(rail_l    = rail_l,
                            rail_w    = d_rail['rw'],
                            rail_h    = d_rail['rh'],
                            bolt_lsep = d_rail['boltlsep'],
                            bolt_wsep = d_rail['boltwsep'],
                            bolt_d    = d_rail['boltd'],
                            bolth_d   = d_rail['bolthd'],
                            bolth_h   = d_rail['bolthh'],
                            boltend_sep = boltends,
                            axis_l    = axis_l,
                            axis_b    = axis_b,
                            bolthole_d = bolthole_d,
                            bolthole_l = bolthole_l,
                            bolthole_dir = bolthole_dir,
                            bolthole_nutd = bolthole_nutd,
                            bolthole_nuth = bolthole_nuth,
                            name      = name)

    return h_lgrail

#hl = f_linguiderail_bh(200, kcomp.SEBWM16_R, 'y', '-z',
#                         bolthole_d = 2 * kcomp.M3_SHANK_R_TOL,
#                         bolthole_l = 10.,
#                         bolthole_dir = 'same',
#                         bolthole_nutd = 2 * kcomp.M3_NUT_R_TOL, 
#                         bolthole_nuth = 2 * kcomp.M3_NUT_L,
#                         name = 'linguiderail' )










# ---------------------- ShpLinGuideRail -------------------------------

class ShpLinGuideRail (shp_clss.Obj3D):
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
        0: there is only one bolt
    bolt_d : float
        Diameter of the hole for the bolt
    bolth_d : float
        Diameter of the hole for the head of the bolt
    bolth_h : float
        Heigth of the hole for the head of the bolt
    boltend_sep : float
        Separation on one end, from the bolt to the end
        0: evenly distributed
    axis_d : FreeCAD.Vector
        The axis along the depth (lenght) of the rail 
    axis_w : FreeCAD.Vector
        The axis along the width of the rail
    axis_h : FreeCAD.Vector
        The axis along the height of the rail, pointing up
    pos_d : int
        Location of pos along axis_d (see drawing)
        0: at the beginning of the rail
        1: at the first bolt hole
        2: at the middle of the rail (not necessary at a bolt hole)
        3: at the last bolt hole
        4: at the end of the rail

    pos_w : int
        Location of pos along axis_w (see drawing). Symmetric, negative indexes
        means the other side
        0: at the center of symmetry
        1: at the bolt holes (only make sense if there are 2 bolt holes)
           otherwise it will be like pos_w = 0
        2: at the end of the rail along axis_w

    pos_h : int
        Location of pos along axis_h (see drawing)
        0: at the bottom
        1: at the middle (it is not a specific place)
        1: at the bolt head
        3: at the top end

    pos : FreeCAD.Vector
        Position at the point defined by pos_d, pos_w, pos_h

    """

    def __init__ (self, rail_d, rail_w, rail_h,
                  bolt_lsep, bolt_wsep, bolt_d,
                  bolth_d, bolth_h, boltend_sep = 0,
                  axis_d = VX, axis_w = V0, axis_h = VZ,
                  pos_d = 0, pos_w = 0, pos_h = 0,
                  pos = V0):


        if (axis_w is None) or (axis_w == V0):
            axis_w = axis_h.cross(axis_d)

        shp_clss.Obj3D.__init__(self, axis_d, axis_w, axis_h)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

        self.d0_cen = 0
        self.w0_cen = 1 # symmetric
        self.h0_cen = 0

        # calculation of the number of bolt holes along axis_d
        if boltend_sep != 0:
            nbolt_l = (rail_d - boltend_sep) // bolt_lsep #integer division
            rail_rem = rail_d - boltend_sep - nbolt_l * bolt_lsep 
            if rail_rem > bolth_d:
                # one bolt more
                nbolt_l = nbolt_l + 1
            self.boltend_sep = boltend_sep
        else: # leave even distance
            # number of bolt lines, on the depth (length) axis
            nbolt_l = rail_d // bolt_lsep # integer division
            #dont use % in case is not int
            rail_rem = rail_d - nbolt_l * bolt_lsep 
            if rail_rem > 2* bolth_d :
                # one bolt more
                nbolt_l = nbolt_l + 1
                # separation between the bolt and the end
                self.boltend_sep = rail_rem / 2.
            else:
                self.boltend_sep = (bolt_lsep + rail_rem) / 2.
        self.nbolt_l = int(nbolt_l)

        # vectors from the origin to the points along axis_d:
        self.d_o[0] = V0 # origin
        self.d_o[1] = self.vec_d(self.boltend_sep)
        self.d_o[2] = self.vec_d(rail_d/2.)
        self.d_o[3] = self.vec_d((self.nbolt_l-1)*bolt_lsep + self.boltend_sep)
        self.d_o[4] = self.vec_d(rail_d)

        # vectors from the origin to the points along axis_w:
        # symmetric: negative
        self.w_o[0] = V0 # base: origin
        self.w_o[1] = self.vec_w(-bolt_wsep/2.) #if 0: same as w_o[0]
        self.w_o[2] = self.vec_w(-rail_w/2.)

        # vectors from the origin to the points along axis_h:
        self.h_o[0] = V0 # base: origin
        self.h_o[1] = self.vec_h(rail_h/2.)
        self.h_o[2] = self.vec_h(rail_h - bolth_h)
        self.h_o[3] = self.vec_h(rail_h)


        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        wire_rail = fcfun.wire_lgrail( rail_w = rail_w,
                                       rail_h = rail_h,
                                       axis_w = self.axis_w,
                                       axis_h = self.axis_h,
                                       pos_w = 0, pos_h = 0,
                                       pos = self.pos_o)

        # make a face of the wire 
        shp_face_rail = Part.Face(wire_rail)
        shp_plainrail = shp_face_rail.extrude(self.vec_d(rail_d))

        holes_list = []
        # bolt holes
        bolthole_pos = self.get_pos_dwh(1,0,3)
        for i in range (0,self.nbolt_l):
            if bolt_wsep == 0: # just one bolt
                shp_bolt = fcfun.shp_bolt_dir (r_shank = bolt_d/2.,
                                           l_bolt = rail_h,
                                           r_head = bolth_d/2.,
                                           l_head = bolth_h,
                                           xtr_head = 1, xtr_shank = 1,
                                           support = 0,
                                           fc_normal = self.axis_h.negative(),
                                           pos_n = 0, pos = bolthole_pos)
                holes_list.append(shp_bolt)
            else:
                for i in (-1,1):
                    bolthole_pos_i = bolthole_pos + self.get_pos_w(i)
                    shp_bolt = fcfun.shp_bolt_dir (r_shank = bolt_d/2.,
                                           l_bolt = rail_h,
                                           r_head = bolth_d/2.,
                                           l_head = bolth_h,
                                           xtr_head = 1, xtr_shank = 1,
                                           support = 0,
                                           fc_normal = self.axis_h.negative(),
                                           pos_n = 0, pos = bolthole_pos_i)
                    holes_list.append(shp_bolt)
            bolthole_pos = bolthole_pos + self.vec_d(bolt_lsep)

        shp_holes = fcfun.fuseshplist(holes_list)
        shp_rail = shp_plainrail.cut(shp_holes)
        shp_rail = shp_rail.removeSplitter()

        self.shp = shp_rail
        #Part.show(shp_rail)
        

#shp_lgrail = ShpLinGuideRail( rail_d = 79., rail_w=40., rail_h=20.,
#                  bolt_lsep=20., bolt_wsep=15, bolt_d=3.,
#                  bolth_d=5., bolth_h=2., boltend_sep = 10,
#                  axis_d = VX, axis_w = V0, axis_h = VZ,
#                  pos_d = 0, pos_w = 0, pos_h = 0,
#                  pos = V0)


class PartLinGuideRail (fc_clss.SinglePart, ShpLinGuideRail):
    """ Integration of a ShpLinGuideRail object into a PartLinGuideRail
     object, so it is a FreeCAD object that can be visualized in FreeCAD
    Instead of using all the arguments of ShpLinGuideRail, it will use
    a dictionary

    Parameters:
    -----------
    rail_d : float
        Length (depth) of the rail
    rail_dict : dictionary
        Dictionary with all the information about the rail
        in kcomp.py there are some dictionaries of linear guide rails that
        can be used
    boltend_sep : float
        Separation on one end, from the bolt to the end
        it can be given by the dictionary as a default value
        >0: the value that will be take
        0: evenly distributed
        <0: value from the dictionary

    axis_d : FreeCAD.Vector
        The axis along the depth (lenght) of the rail 
    axis_w : FreeCAD.Vector
        The axis along the width of the rail
    axis_h : FreeCAD.Vector
        The axis along the height of the rail, pointing up
    pos_d : int
        Location of pos along axis_d (see drawing of ShpLinGuideRail)
        0: at the beginning of the rail
        1: at the first bolt hole
        2: at the middle of the rail (not necessary at a bolt hole)
        3: at the last bolt hole
        4: at the end of the rail

    pos_w : int
        Location of pos along axis_w (see drawing). Symmetric, negative indexes
        means the other side
        0: at the center of symmetry
        1: at the bolt holes (only make sense if there are 2 bolt holes)
           otherwise it will be like pos_w = 0
        2: at the end of the rail along axis_w

    pos_h : int
        Location of pos along axis_h (see drawing of ShpLinGuideRail)
        0: at the bottom
        1: at the middle (it is not a specific place)
        1: at the bolt head
        3: at the top end

    pos : FreeCAD.Vector
        Position at the point defined by pos_d, pos_w, pos_h
    """

    def __init__ (self, rail_d,
                  rail_dict,
                  boltend_sep = 0,
                  axis_d = VX, axis_w = V0, axis_h = VZ,
                  pos_d = 0, pos_w = 0, pos_h = 0,
                  pos = V0,
                  model_type = 1, # dimensional model,
                  name = ''):

        default_name = rail_dict['name']
        self.set_name (name, default_name, change=0)

        if boltend_sep == 0:
            boltends = 0
        elif boltend_sep < 0:
            boltends = rail_dict['boltend_sep']
        else:
            boltends = boltend_sep

        # creation of the shape
        ShpLinGuideRail.__init__(self,
                                 rail_d     = rail_d,
                                 rail_w     = rail_dict['rw'],
                                 rail_h     = rail_dict['rh'],
                                 bolt_lsep  = rail_dict['boltlsep'],
                                 bolt_wsep  = rail_dict['boltwsep'],
                                 bolt_d     = rail_dict['boltd'],
                                 bolth_d    = rail_dict['bolthd'],
                                 bolth_h    = rail_dict['bolthh'],
                                 boltend_sep = boltends,
                                 axis_d     = axis_d,
                                 axis_w     = axis_w,
                                 axis_h     = axis_h,
                                 pos_d      = pos_d,
                                 pos_w      = pos_w,
                                 pos_h      = pos_h,
                                 pos        = pos)

        # creation of the part
        fc_clss.SinglePart.__init__(self)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): 
                setattr(self, i, values[i])


#doc = FreeCAD.newDocument()
#partLinGuideRail = PartLinGuideRail (
#                                     rail_d = 100.,
#                                     rail_dict = kcomp.SEBWM16_R,
#                                     boltend_sep = 0,
#                                     axis_d = VX, axis_w = V0, axis_h = VZ,
#                                     pos_d = 0, pos_w = 0, pos_h = 0,
#                                     pos = V0)



# ---------------------- LinGuideBlock -------------------------------
# Creates the block of the linear guide
# Arguments:
# block_l: Total length of the block
# block_ls: Small length of the block. Usually there is a plastic end, for 
#           lubricant or whatever
# block_w: Total Width of the block
# block_ws: Small width of the block (the plastic end)
# linguide_h: Height of the linear guide. Total, Rail + Block
# bolt_lsep: separation of the bolts, on the length direction
# bolt_wsep: separation of the bolts, on the width direction
# bolt_d: diameter of the hole of the bolt
# bolt_l: length of the hole. if 0, it is a thru-hole
# h_lgrail: handler of the linear guide rail
# block_pos_l: position of the block relative to the rail. From 0 to 1

# Attributes:
# axis_l: direction of the rail: 'x', 'y', 'z'
# axis_b: direction of the bottom of the rail: 'x', '-x', 'y', '-y', 'z', '-z'

#
#                 __________________     _____________
#              __|__________________|__  ___           |
#             |                        |    |          |
#             | 0 --- bolt_wsep ---  0 |    |          |
#             | :                      |    |          |
#             | :                      |    + block_ls + block_l
#             | + bolt_lsep            |    |          |
#             | :                      |    |          |
#             | 0                    0 |    |          |
#             |________________________| ___|          |
#                |__________________|    ______________|
#
#             |  |                  |  |
#             |  |____ block_ws ____|  |
#             |_______ block_w ________|
#

class LinGuideBlock (object):

    def __init__ (self, block_l, block_ls, block_w,  
                        block_ws, block_h, 
                        linguide_h,
                        bolt_lsep, bolt_wsep,
                        bolt_d, bolt_l,
                        h_lgrail,
                        block_pos_l,
                        name):

        doc = FreeCAD.ActiveDocument

        self.base_place = (0,0,0)
        self.block_l  = block_l
        self.block_ls = block_ls
        self.block_w  = block_w
        self.block_ws = block_ws
        self.block_h  = block_h 
        self.linguide_h = linguide_h 
        self.bolt_lsep = bolt_lsep 
        self.bolt_wsep = bolt_wsep 
        self.bolt_d  = bolt_d 
        if bolt_l == 0:
            self.bolt_l  = block_h 
        else:
            self.bolt_l  = bolt_l 
        self.h_lgrail  = h_lgrail 
        self.block_pos_l  = block_pos_l 

        shp_plainrail = h_lgrail.shp_plainrail

        self.axis_l = h_lgrail.axis_l
        self.axis_b = h_lgrail.axis_b

        blockend_l = (block_l - block_ls)/2.

        b_pos=FreeCAD.Vector(block_pos_l,0,linguide_h-block_h)
        # central block
        shp_cen_bl_box = fcfun.shp_boxcen(x=block_ls,
                                      y=block_w,
                                      z=block_h, 
                                      cx= 0, cy=1, cz=0,
                                      pos=b_pos)
        # bolt holes
        boltpos_z = linguide_h+1
        if bolt_l == 0:
            bolt_h = self.bolt_l + 2
        else:
            bolt_h = self.bolt_l + 1

        #if bolt_l == 0:
            #boltpos_z = linguide_h-block_h-1
        #else:
        #    boltpos_z = linguide_h-block_h

        boltpos00 = FreeCAD.Vector(block_pos_l + block_ls/2- bolt_lsep/2,
                                -bolt_wsep/2.,boltpos_z)
        shp_bolt00=fcfun.shp_cyl (r=bolt_d/2., h=bolt_h, normal=VZN,
                                 pos = boltpos00)
        boltpos01 = FreeCAD.Vector(block_pos_l + block_ls/2+ bolt_lsep/2,
                                -bolt_wsep/2.,boltpos_z)
        shp_bolt01=fcfun.shp_cyl (r=bolt_d/2., h=bolt_h, normal=VZN,
                                 pos = boltpos01)
        boltpos10 = FreeCAD.Vector(block_pos_l + block_ls/2- bolt_lsep/2,
                                 bolt_wsep/2.,boltpos_z)
        shp_bolt10=fcfun.shp_cyl (r=bolt_d/2., h=bolt_h, normal=VZN,
                                 pos = boltpos10)
        boltpos11 = FreeCAD.Vector(block_pos_l + block_ls/2+ bolt_lsep/2,
                                 bolt_wsep/2.,boltpos_z)
        shp_bolt11=fcfun.shp_cyl (r=bolt_d/2., h=bolt_h, normal=VZN,
                                 pos = boltpos11)
        shp_bolts = shp_bolt00.multiFuse([shp_bolt01,shp_bolt10, shp_bolt11])


        shp_cen_blhole = shp_cen_bl_box.cut(shp_bolts)


     

        # end blocks
        bbot_pos=FreeCAD.Vector(block_pos_l-blockend_l,0,linguide_h-block_h)
        shp_botend_bl_box = fcfun.shp_boxcen(x=blockend_l,
                                      y=block_ws,
                                      z=block_h, 
                                      cx= 0, cy=1, cz=0,
                                      pos=bbot_pos)

        btop_pos=FreeCAD.Vector(block_pos_l+block_ls,0,linguide_h-block_h)
        shp_topend_bl_box = fcfun.shp_boxcen(x=blockend_l,
                                      y=block_ws,
                                      z=block_h, 
                                      cx= 0, cy=1, cz=0,
                                      pos=btop_pos)
        shp_bl_box = shp_cen_blhole.multiFuse([shp_botend_bl_box,
                                               shp_topend_bl_box])




        vrot = fcfun.calc_rot(fcfun.getvecofname(self.axis_l),
                              fcfun.getvecofname(self.axis_b))
        shp_bl_box.Placement.Rotation = vrot

        shp_bl = shp_bl_box.cut(shp_plainrail)

        doc.recompute()
        fco_bl = doc.addObject("Part::Feature", name + '_block')
        fco_bl.Shape = shp_bl
        self.fco = fco_bl


    def BasePlace (self, position = (0,0,0)):
        self.base_place = position
        self.fco.Placement.Base = FreeCAD.Vector(position)

    

# ---------------------- f_linguide -------------------------------
        
# Arguments:
# rail_l: length of the linear guide
# dlg: a dictionary is used for the constants. Defined in kcomp.py
# axis_l : the axis where the lenght of the rail is: 'x', 'y', 'z'
# axis_b : the axis where the base of the rail is pointing:
# boltend_sep : separation on one end, from the bolt to the end
# bl_pos : Position of the block, relative to the length: 0. to 1.
# hl = f_linguiderail(200, kcomp.SEBWM16_R, 'y', '-z')
def f_linguide (rail_l, dlg, axis_l, axis_b, boltend_sep = 0,
                bl_pos = 0.,
                name ='linguide'):

    print(axis_l)

    d_rail = dlg['rail']
    if boltend_sep == 0:
        boltends =  d_rail['boltend_sep']
    else:
        boltends =  boltend_sep

    h_lgrail = LinGuideRail(rail_l    = rail_l,
                            rail_w    = d_rail['rw'],
                            rail_h    = d_rail['rh'],
                            bolt_lsep = d_rail['boltlsep'],
                            bolt_wsep = d_rail['boltwsep'],
                            bolt_d    = d_rail['boltd'],
                            bolth_d   = d_rail['bolthd'],
                            bolth_h   = d_rail['bolthh'],
                            boltend_sep = boltends,
                            axis_l    = axis_l,
                            axis_b    = axis_b,
                            name      = name)

    d_block = dlg['block']

    # position of the block refered to the rail
    # rail_l - d_block['b'] : the length of the rail - length of the block
    block_pos_l = bl_pos * (rail_l - d_block['bl'])

    h_brail = LinGuideBlock (
                             block_l  = d_block['bl'],
                             block_ls = d_block['bls'],
                             block_w  = d_block['bw'],
                             block_ws = d_block['bws'],
                             block_h  = d_block['bh'],
                             linguide_h = d_block['lh'],
                             bolt_lsep = d_block['boltlsep'],
                             bolt_wsep = d_block['boltwsep'],
                             bolt_d   = d_block['boltd'],
                             bolt_l   = d_block['boltl'],
                             h_lgrail = h_lgrail,
                             block_pos_l = block_pos_l,
                             name     = name)

    return h_lgrail


# ---------------------- class LinGuide -------------------------------
        
# Arguments:
# rail_l: length of the linear guide
# dlg: a dictionary is used for the constants. Defined in kcomp.py
# axis_l : the axis where the lenght of the rail is: 'x', 'y', 'z'
# axis_b : the axis where the base of the rail is pointing:
# boltend_sep : separation on one end, from the bolt to the end
# bl_pos : Position of the block, relative to the length: 0. to 1.
# hl = f_linguiderail(200, kcomp.SEBWM16_R, 'y', '-z')

class LinGuide(object):

    def __init__ (self, rail_l, dlg,
                   axis_l,
                  axis_b, boltend_sep = 0,
                  bl_pos = 0.,
                  name ='linguide'):

        self.base_place = (0,0,0)
        self.rail_l = rail_l
        self.dlg = dlg
        self.axis_l = axis_l
        self.axis_b = axis_b
        self.bl_pos = bl_pos

        d_rail = dlg['rail']
        self.d_rail = d_rail
        d_block = dlg['block']
        self.d_block = dlg['block']

        if boltend_sep == 0:
            boltend_sep =  d_rail['boltend_sep']
        else:
            boltend_sep =  boltend_sep
        self.boltend_sep =  boltend_sep

        h_lgrail = LinGuideRail(rail_l    = rail_l,
                            rail_w    = d_rail['rw'],
                            rail_h    = d_rail['rh'],
                            bolt_lsep = d_rail['boltlsep'],
                            bolt_wsep = d_rail['boltwsep'],
                            bolt_d    = d_rail['boltd'],
                            bolth_d   = d_rail['bolthd'],
                            bolth_h   = d_rail['bolthh'],
                            boltend_sep = boltend_sep,
                            axis_l    = axis_l,
                            axis_b    = axis_b,
                            name      = name)

        self.h_lgrail = h_lgrail


        # position of the block refered to the rail
        # rail_l - d_block['b'] : the length of the rail - length of the block
        block_pos_l = bl_pos * (rail_l - d_block['bl'])
        self.block_pos_l = block_pos_l

        h_brail = LinGuideBlock (
                                 block_l  = d_block['bl'],
                                 block_ls = d_block['bls'],
                                 block_w  = d_block['bw'],
                                 block_ws = d_block['bws'],
                                 block_h  = d_block['bh'],
                                 linguide_h = d_block['lh'],
                                 bolt_lsep = d_block['boltlsep'],
                                 bolt_wsep = d_block['boltwsep'],
                                 bolt_d   = d_block['boltd'],
                                 bolt_l   = d_block['boltl'],
                                 h_lgrail = h_lgrail,
                                 block_pos_l = block_pos_l,
                                 name     = name)

        self.h_brail = h_brail

    def BasePlace (self,position = (0,0,0)):
        self.base_place = position
        self.h_brail.BasePlace(position)
        self.h_lgrail.BasePlace(position)




#hl = f_linguide(200, kcomp.SEB15A, 'y', '-z',
#hl = f_linguide(200, kcomp.SEBWM16, 'y', '-z',
#                         boltend_sep = 0,
#                         bl_pos = 0.5,
#                         #bolthole_d = 2 * kcomp.M3_SHANK_R_TOL,
#                         #bolthole_l = 10.,
#                         #bolthole_dir = 'same',
#                         #bolthole_nutd = 2 * kcomp.M3_NUT_R_TOL, 
#                         #bolthole_nuth = 2 * kcomp.M3_NUT_L,
#                         name = 'linguiderail' )


#lg_nx = LinGuide (rail_l= 136.,
#                    dlg= kcomp.SEBWM16,
#                    axis_l = 'z', 
#                    axis_b='x',
#                    boltend_sep = 8., bl_pos=0.5, name='lg_nx')


class ShpLinGuideBlock (shp_clss.Obj3D):
    """ Creates a shape of a linear guide rail
    Creates a hole for the rail, no exact shape
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


     Origin at pos_o: pos_d = pos_w = pos_h = 0

    Parameters:
    -----------
    block_d: float
        Total length (depth) of the block
    block_ds: float
        Small length (depth) of the block. Usually there is a plastic end,
        for lubricant or whatever
    block_w: float
        Total Width of the block
    block_ws: float
        Small width of the block (the plastic end)
    block_h: float
        Height of the block
    bolt_dsep: float
        Separation of the bolts, on the depth (length) direction
    bolt_wsep: float
        Separation of the bolts, on the width direction
    bolt_d: float
        Diameter of the hole of the bolt
    bolt_l: float
        Length of the hole. if 0, it is a thru-hole
    linguide_h: float
        Height of the linear guide. Total, Rail + Block
        if 0: there will be internal hole for the rail
    rail_h: float
        Height of the rail
        if 0: there will be internal hole for the rail
    rail_w: float
        Width of the rail
        if 0: there will be internal hole for the rail
    axis_d : FreeCAD.Vector
        The axis along the depth (lenght) of the block (and rail) 
    axis_w : FreeCAD.Vector
        The axis along the width of the block
    axis_h : FreeCAD.Vector
        The axis along the height of the block, pointing up
    pos_d : int
        Location of pos along axis_d (see drawing). Symmetric, negative indexes
        means the other side
        0: at the center (symmetric)
        1: at the bolt hole
        2: at the end of the smaller part of the block
        3: at the end of the end of the block

    pos_w : int
        Location of pos along axis_w (see drawing). Symmetric, negative indexes
        means the other side
        0: at the center of symmetry
        1: at the inner hole of the rail
        2: at the bolt holes (it can be after the smaller part of the block)
        3: at the end of the smaller part of the block
        4: at the end of the end of the block

    pos_h : int
        Location of pos along axis_h (see drawing)
        0: at the bottom (could make more sense to have 0 at the top instead
        1: at the top of the rail hole
        2: at the bottom of the bolt holes, if thruholes, same as 0
        3: at the top end
        4: at the bottom of the rail (not the block), if the rail has been
           defined

    pos : FreeCAD.Vector
        Position at the point defined by pos_d, pos_w, pos_h

    ::

                      axis_h
                          :
                          :
              ____________3_____________.........................         
             |::|         2          |::|                       :
             |  |     ____1____      |  |................       :+linguide_h
             |  |    |    :    |     |  |  :            :       :
             |  |     \   :   /      |  |  :rail_ins_h  :       :
             |__|_____/   o   \______|__|..:            :       :
               :     :         :      :                 :rail_h :
               :     :         :      :                 :       :
               :     :....4....:      :.................:.......:
               :          +           :
               :       rail_w         :

            rail_ins_h = block_h - (linguide_h - rail_h)
    """

    def __init__( self,
                  block_d,
                  block_ds,
                  block_w,
                  block_ws,
                  block_h,

                  bolt_dsep,
                  bolt_wsep,
                  bolt_d,
                  bolt_l,

                  linguide_h=0,
                  rail_h=0,
                  rail_w=0,

                  axis_d = VX,
                  axis_w = VY,
                  axis_h = VZ,
                  pos_d = 0,
                  pos_w = 0,
                  pos_h = 0,
                  pos = V0):

        if (axis_w is None) or (axis_w == V0):
            axis_w = axis_h.cross(axis_d)

        shp_clss.Obj3D.__init__(self, axis_d, axis_w, axis_h)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

        self.d0_cen = 1 # symmetric
        self.w0_cen = 1 # symmetric
        self.h0_cen = 0

        if bolt_l == 0: # thruhole
            self.bolt_l = block_h
            self.thruhole = 1
        else:
            self.thruhole = 0

        if rail_h == 0 or linguide_h == 0:
            self.rail_h = 0
            self.linguide_h = 0
            self.rail_ins_h = 0
            self.rail_bot_h = 0
        else:
            self.rail_ins_h = block_h - (linguide_h - rail_h)
            self.rail_bot_h = rail_h - self.rail_ins_h


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
        if self.rail_h > 0 and rail_w > 0:
            wire_rail = fcfun.wire_lgrail( rail_w = rail_w,
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
                                        r = bolt_d/2.,
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
        #Part.show(shp_block)


#shp_linguide_block = ShpLinGuideBlock (
#                  block_d = kcomp.SEB10_B['bl'],
#                  block_ds = kcomp.SEB10_B['bls'],
#                  block_w = kcomp.SEB10_B['bw'],
#                  block_ws = kcomp.SEB10_B['bws'],
#                  block_h = kcomp.SEB10_B['bh'],
#
#                  #linguide_h = kcomp.SEB10_B['lh'],
#                  #rail_h = kcomp.SEB10_R['rh'],
#                  #rail_w = kcomp.SEB10_R['rw'],
#
#                  bolt_dsep = kcomp.SEB10_B['boltlsep'],
#                  bolt_wsep = kcomp.SEB10_B['boltwsep'],
#                  bolt_d = kcomp.SEB10_B['boltd'],
#                  bolt_l = kcomp.SEB10_B['boltl'],
#
#                  axis_d = VX,
#                  axis_w = VY,
#                  axis_h = VZ,
#                  pos_d = 0,
#                  pos_w = 0,
#                  pos_h = 0,
#                  pos = V0)


class PartLinGuideBlock (fc_clss.SinglePart, ShpLinGuideBlock):
    """ 
    Integration of a ShpLinGuideBlock object into a PartLinGuideBlock
    object, so it is a FreeCAD object that can be visualized in FreeCAD
    Instead of using all the arguments of ShpLinGuideBlock, it will use
    a dictionary

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
                  name = ''):


        default_name = block_dict['name'] + '_block'
        self.set_name (name, default_name, change=0)

        if rail_dict is None:
            self.rail_h = 0
            self.rail_w = 0
        else:
            self.rail_h = rail_dict['rh']
            self.rail_w = rail_dict['rw']


        # creation of the shape
        ShpLinGuideBlock.__init__( self,
                  block_d  = block_dict['bl'],
                  block_ds = block_dict['bls'],
                  block_w  = block_dict['bw'],
                  block_ws = block_dict['bws'],
                  block_h  = block_dict['bh'],

                  linguide_h = block_dict['lh'],
                  rail_h = self.rail_h,
                  rail_w = self.rail_w,

                  bolt_dsep = block_dict['boltlsep'],
                  bolt_wsep = block_dict['boltwsep'],
                  bolt_d    = block_dict['boltd'],
                  bolt_l    = block_dict['boltl'],

                  axis_d = axis_d,
                  axis_w = axis_w,
                  axis_h = axis_h,
                  pos_d = pos_d,
                  pos_w = pos_w,
                  pos_h = pos_h,
                  pos = pos)


        # creation of the part
        fc_clss.SinglePart.__init__(self)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): 
                setattr(self, i, values[i])


#doc = FreeCAD.newDocument()
#partLinGuideBlock = PartLinGuideBlock (
#                                     block_dict = kcomp.SEBWM16_B,
#                                     rail_dict  = kcomp.SEBWM16_R,
#                                     axis_d = VX, axis_w = VY, axis_h = VZ,
#                                     pos_d = 0, pos_w = -2, pos_h = 0,
#                                     pos = V0)









class ShpGtPulley (shp_clss.Obj3D):
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
                 axis_d = None,
                 axis_w = None,
                 axis_h = VZ,
                 pos_d = 0,
                 pos_w = 0,
                 pos_h = 0,
                 pos = V0):


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
      
        shp_clss.Obj3D.__init__(self, axis_d, axis_w, axis_h)

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

        # height of the base, without the toothed part and the flange
        self.base_h = tot_h - toothed_h - top_flange_h - bot_flange_h

        self.h0_cen = 0
        self.d0_cen = 1 # symmetrical
        self.w0_cen = 1 # symmetrical

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


#shpObjPulley = ShpGtPulley()


#doc = FreeCAD.newDocument()
#shpObjPulley = ShpGtPulley(
#                 pitch = 2.,
#                 n_teeth = 20,
#                 toothed_h = 7.5,
#                 top_flange_h = 1.,
#                 bot_flange_h = 2,
#                 tot_h = 16.,
#                 flange_d = 18.,
#                 base_d = 15.,
#                 shaft_d = 5.,
#                 tol = 0,
#                 axis_d = VX,
#                 axis_w = VY,
#                 axis_h = VZ,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos_h = 0,
#                 pos = FreeCAD.Vector(3,2,10))
#
#Part.show(shpObjPulley.shp)

class PartGtPulley (fc_clss.SinglePart, ShpGtPulley):
    """ Integration of a ShpGtPulley object into a PartGtPulley
    object, so it is a FreeCAD object that can be visualized in FreeCAD
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
                 name = ''):

        default_name = 'gt' + str(int(pitch)) + '_pulley_' + str(n_teeth)
        self.set_name (name, default_name, change = 0)
        # First the shape is created
        ShpGtPulley.__init__(self,
                 pitch = pitch,
                 n_teeth = n_teeth,
                 toothed_h = toothed_h,
                 top_flange_h = top_flange_h,
                 bot_flange_h = bot_flange_h,
                 tot_h = tot_h,
                 flange_d = flange_d,
                 base_d = base_d,
                 shaft_d = shaft_d,
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
            if not hasattr(self,i): 
                setattr(self, i, values[i])


#doc = FreeCAD.newDocument()
#partPulley = PartGtPulley(
#                 pitch = 2.,
#                 n_teeth = 20,
#                 toothed_h = 7.5,
#                 top_flange_h = 1.,
#                 bot_flange_h = 2,
#                 tot_h = 16.,
#                 flange_d = 18.,
#                 base_d = 8.,
#                 shaft_d = 5.,
#                 tol = 0,
#                 axis_d = VX,
#                 axis_w = VY,
#                 axis_h = VZ,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos_h = 0,
#                 pos = FreeCAD.Vector(3,2,10))

