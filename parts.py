# ----------------------------------------------------------------------------
# -- Parts to print
# -- comps library
# -- Python FreeCAD functions and classes that groups components
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronics. Rey Juan Carlos University (urjc.es)
# -- November-2016
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

import FreeCAD
import Part
import Draft
import Mesh
import MeshPart
import DraftVecUtils
import logging
import inspect

# ---------------------- can be taken away after debugging
import os
# directory this file is
filepath = os.getcwd()
import sys
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath)
# ---------------------- can be taken away after debugging

import kcomp 
import kcomp_optic
import fcfun
import comps
import kparts
import shp_clss
import fc_clss

from fcfun import V0, VX, VY, VZ, V0ROT, addBox, addCyl, addCyl_pos, fillet_len
from fcfun import VXN, VYN, VZN
from fcfun import addBolt, addBoltNut_hole, NutHole
from kcomp import TOL


stl_dir = "/stl/"

logging.basicConfig(level=logging.DEBUG,
                    format='%(%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ----------- class AluProfBracketPerp -----------------------------------

class AluProfBracketPerp (object):

    """ 
    Bracket to join 2 aluminum profiles that are perpendicular,
    that is, they are not on the same plane
    ::

        aluprof_perp (perpendicular to the bracket)   
          /  / /  bracket (not drawn)
         /  / /_____
        /  / /_____/|
       /__/ /______|/ aluprof_lin (it is in line with the bracket)
       |__|/

                     fc_perp_ax (is not the axis of the perpendicular
                       :         profile, but the axis of the bracket
       aluprof_perp    :         attached to the perpendicular profile
                    ___:_             
                   |   |  \ bracket  
                  _|___|____\___ .........> fc_line_ax
     alusize_lin +              aluprof_lin
                 :_______________

                         fc_perp_ax
                          :
                          :br_perp_thick
                          .+.
                      ....:__:
                      :   |  |\ 
        alusize_perp  +   |  |   \ 
                      :   |  |______\..
                      :...|_________|..: br_lin_thick .........> fc_lin_ax
                          :.........:
                             
           

    Parameters
    ----------
    alusize_lin : float
        Width of the aluminum profile on the line
    alusize_perp : float
        Width of the perpendicular aluminum profile
    br_lin_thick : float
        Thickness of the line bracket
    br_perp_thick : float
        Thickness of the perpendicular bracket
    bolt_lin_d : int
        Metric of the bolt 3, 4, ... (integer)
    bolt_perp_d : int
        Metric of the bolt 3, 4, ... (integer) on the profile line
        if 0, the same as bolt_lin_d
    nbolts_lin : int
        Number of bolts one bolt on the fc_lin_ax, 
        number of bolts: two bolts on the fc_lin_ax
    bolts_lin_dist : float
        If more than one bolt on fc_lin_ax, defines the 
        distance between them.
        if zero, takes min distance
    bolts_lin_rail : int
        Instead of bolt holes, it will be a rail
        it doesn't make sense to have number of bolts with this option
        it will work on 2 bolts or more. If nbolts_lin == 3, it 
        will make a rail between them. so it will be the same to have
        nbolts_lin = 2 and bolts_lin_dist = 20
        nbolts_lin = 3 and bolts_lin_dist = 10
        The rail will be 20, and it will look the same, it will be
        more clear to have the first option: 2 bolts
    xtr_bolt_head : float
        Extra space for the bolt head length,
        and making a space for it
    xtr_bolt_head_d : float
        Extra space for the bolt head diameter,
        and making a space for it. For the wall bolt
    reinforce : int
        1, if it is reinforced on the sides of lin profile
    fc_perp_ax : FreeCAD.Vector
        Axis of the bracket on the perpendicular prof, see picture
    fc_lin_ax : FreeCAD.Vector
        Axis of the bracket on the aligned profile, see picture
    pos : FreeCAD.Vector
        Position of the center of the bracket on the intersection
    wfco : int
        * if 1: With FreeCad Object: a freecad object is created
        * if 0: only the shape
    name : str
        Name of the freecad object, if created

    """

    def __init__(self, alusize_lin, alusize_perp,
                 br_perp_thick = 3.,
                 br_lin_thick = 3.,
                 bolt_lin_d = 3, #metric of the bolt 
                 bolt_perp_d = 0, #metric of the bolt
                 nbolts_lin = 1,
                 bolts_lin_dist = 0,
                 bolts_lin_rail = 0,
                 xtr_bolt_head = 3,
                 xtr_bolt_head_d = 0,
                 reinforce = 1,
                 fc_perp_ax = VZ,
                 fc_lin_ax = VX,
                 pos = V0,
                 wfco=1,
                 name = 'bracket'):

        doc = FreeCAD.ActiveDocument
        self.name = name
        # bolt lin dimensions
        boltli_dict = kcomp.D912[bolt_lin_d]
        boltlihead_r = boltli_dict['head_r']
        boltlihead_r_tol = boltli_dict['head_r_tol']
        boltlishank_r_tol = boltli_dict['shank_r_tol']
        boltlihead_l = boltli_dict['head_l']
        if bolt_perp_d == 0:
            bolt_perp_d = bolt_lin_d
        boltpe_dict = kcomp.D912[bolt_perp_d]
        boltpehead_r = boltpe_dict['head_r']
        boltpehead_r_tol = boltpe_dict['head_r_tol']
        boltpeshank_r_tol = boltpe_dict['shank_r_tol']
        boltpehead_l = boltpe_dict['head_l']

        boltmaxhead_r = max(boltlihead_r, boltpehead_r)
        boltmaxhead_r_tol = max(boltlihead_r_tol, boltpehead_r_tol)

        # normalize axis, just in case:
        axis_perp = DraftVecUtils.scaleTo(fc_perp_ax,1)
        axis_lin = DraftVecUtils.scaleTo(fc_lin_ax,1)
        axis_perp_neg = axis_perp.negative()
        axis_lin_neg = axis_lin.negative()
        axis_wid   = axis_perp.cross(axis_lin)

        #Calculate the length of the brlin_l
        #         br_perp_thick :boltpehead_l
        #                  :  : : boltlihead_r
        #              ....:__: :  :
        #              :   |  |_   :
        # alusize_perp +   |  |_| _:_
        #              :   |  |__|___|___ 
        #              :...|_____________|
        #                  :.......:
        #                 bolt1li_dist = br_perp_thick+boltpehead_l+boltlihead_r
        #                          :  :  :
        #                        2 x boltlihead_r
        #                  :.............:
        #                      + brlin_l

        bolt1li_dist = (  br_perp_thick + boltpehead_l + boltlihead_r_tol
                        + xtr_bolt_head )


        brlin_l = bolt1li_dist + 2 * boltlihead_r
        if nbolts_lin > 1:
            if bolts_lin_dist == 0:
                # for every new bolt, add 3 times the bolt head radius
                bolts_lin_dist = 3 *  boltlihead_r
            elif bolts_lin_dist <  (3 *  boltlihead_r) :
                logger.warning ('bolt_lin_dist too short')
                bolts_lin_dist = 3 *  boltlihead_r
            brlin_l = brlin_l + (nbolts_lin-1)* bolts_lin_dist

        #              ....:__: :  :           _________
        #              :   |  |_   :          ||       ||
        # alusize_perp +   |  |_| _:_         ||   O   ||
        #              :   |  |__|___|___     ||_______||
        #              :...|_____________|    |___:_:___|......axis_wid
        #                  :.............:    :.........:
        #                    + brlin_l             + alusize_lin

        shp_box = fcfun.shp_box_dir (box_w = alusize_lin,
                                     box_d = brlin_l,
                                     box_h = alusize_perp,
                                     fc_axis_h = axis_perp,
                                     fc_axis_d = axis_lin,
                                     cw = 1, cd = 0, ch = 0,
                                     pos = pos)

        chmf_out_r = min(brlin_l-br_perp_thick, alusize_perp-br_lin_thick)

        chmf_out_pos = (   pos + DraftVecUtils.scaleTo(axis_lin, brlin_l)
                         + DraftVecUtils.scaleTo(axis_perp, alusize_perp))

        shp_box = fcfun.shp_filletchamfer_dirpt(shp_box,
                                                   fc_axis = axis_wid,
                                                   fc_pt = chmf_out_pos,
                                                   fillet = 0,
                                                   radius = chmf_out_r)

        #                                       inside_w
        #                                       ...+...
        #              ....:__: :  :           :_______:
        #              :   |  |_   :          ||       ||
        # alusize_perp +   |  |_| _:_         ||   O   ||
        #              :   |  |__|___|___     ||_______||
        #              :...|_____________|    |___:_:___|
        #                  :.............:    :.........:
        #                    + brlin_l             + alusize_lin
        # cut the box inside
        # Inside width
        # add one, to have it a minimum of one mm
        if (reinforce == 1 and
           (alusize_lin > 2*(boltmaxhead_r + kcomp.TOL) + 1 )):
            inside_w =  2*(boltmaxhead_r + kcomp.TOL)
            #print ("inside width " + str(inside_w))
        else:
            #no space for reinforcement, or reinforcement 0
            inside_w = alusize_lin + 2 # +2 to make the cut

        # chamfer of the inside box
        chmf_in_r = alusize_perp/2. - br_lin_thick -boltpehead_r_tol
        logger.debug ("chamfer radius" + str(chmf_in_r))

        # inside box:
        insbox_pos = ( pos + DraftVecUtils.scale(axis_lin,br_perp_thick)
                           + DraftVecUtils.scale(axis_perp,br_lin_thick))
        shp_insbox = fcfun.shp_box_dir (box_w = inside_w,
                                     box_d = brlin_l,
                                     box_h = alusize_perp,
                                     fc_axis_h = axis_perp,
                                     fc_axis_d = axis_lin,
                                     cw = 1, cd = 0, ch = 0,
                                     pos = insbox_pos)
        if chmf_in_r > 0 :
            shp_insbox = fcfun.shp_filletchamfer_dirpt(shp_insbox,
                                                     fc_axis = axis_wid,
                                                     fc_pt = insbox_pos,
                                                     fillet = 0,
                                                     radius = chmf_in_r)
        #Part.show(shp_insbox)
        shp_box = shp_box.cut(shp_insbox)

        #pos_boltpe =  pos + DraftVecUtils.scale(axis_perp,alusize_perp/2.) 
        #shp_boltpe= fcfun.shp_cylcenxtr(r=boltshank_r_tol,
        #                    h=brack_thick,
        #                    normal = axis_lin,
        #                    ch = 0, xtr_top = 1, xtr_bot=1,
        #                    pos = pos_boltpe)

        boltholes = []
        pos_boltpe =  (pos + DraftVecUtils.scale(axis_perp,alusize_perp/2.)
                     + DraftVecUtils.scale(axis_lin,br_perp_thick+boltpehead_l))
        shp_boltpe = fcfun.shp_bolt_dir(r_shank = boltpeshank_r_tol,
                            l_bolt = br_perp_thick + boltpehead_l,
                            r_head = boltpehead_r_tol + xtr_bolt_head_d/2.,
                            l_head = boltpehead_l,
                            xtr_head = xtr_bolt_head,
                            xtr_shank = 1,
                            support = 0,
                            fc_normal = axis_lin_neg,
                            fc_verx1 = axis_perp, #it doesn't matter
                            pos = pos_boltpe)
        boltholes.append(shp_boltpe)

        # position of the first bolt
        pos_boltli =  pos + DraftVecUtils.scale(axis_lin,bolt1li_dist) 
        pos_boltli_top = (pos_boltli
                         + DraftVecUtils.scale(axis_perp, alusize_perp))
        if bolts_lin_rail == 1 and nbolts_lin > 1:
            # there is a rail
            rail_l = (nbolts_lin - 1) * bolts_lin_dist
            # 2 Stadium to cut the chamfer if it is too big
            shp_railli = fcfun.shp_2stadium_dir (length = rail_l,
                               r_s = boltlishank_r_tol,
                               r_l = boltlihead_r_tol + kcomp.TOL/2., #extra TOL
                               h_tot = alusize_perp,
                               h_rl = alusize_perp-br_lin_thick,
                               fc_axis_h = axis_perp_neg,
                               fc_axis_l = axis_lin,
                               ref_l = 2, #ref on the circle center
                               rl_h0 = 1, #bolt head is on pos
                               xtr_h = 1,
                               xtr_nh = 1,
                               pos = pos_boltli_top)
            boltholes.append(shp_railli)
        else: # holes for the bolts
            # first boltli hole , make a bolt, in case there is chamfer to cut
            shp_boltli = fcfun.shp_bolt_dir(r_shank = boltlishank_r_tol,
                            l_bolt = alusize_perp,
                            r_head = boltlihead_r_tol + kcomp.TOL/2., #extra TOL
                            l_head = alusize_perp-br_lin_thick,
                            xtr_head = 1,
                            xtr_shank = 1,
                            support = 0,
                            fc_normal = axis_perp_neg,
                            fc_verx1 = axis_lin, #it doesn't matter
                            pos = pos_boltli_top)
            boltholes.append(shp_boltli)
            # the rest of boltli holes
            for ibolt in range (1, nbolts_lin):
                pos_boltli = (  pos_boltli
                               + DraftVecUtils.scale(axis_lin,bolts_lin_dist)) 
                shp_boltli= fcfun.shp_cylcenxtr(r=boltlishank_r_tol,
                                h=br_lin_thick,
                                normal = axis_perp,
                                ch = 0, xtr_top = 1, xtr_bot=1,
                                pos = pos_boltli)
                boltholes.append(shp_boltli)

        shp_boltfuse = fcfun.fuseshplist(boltholes)

        shp_bracket = shp_box.cut(shp_boltfuse)
        doc.recompute()
        shp_bracket =shp_bracket.removeSplitter()
        doc.recompute()

        self.shp = shp_bracket
        self.wfco = wfco
        if wfco == 1:
            # a freeCAD object is created
            fco_bracket = doc.addObject("Part::Feature", name )
            fco_bracket.Shape = shp_bracket
            self.fco = fco_bracket

    def color (self, color = (1,1,1)):
        if self.wfco == 1:
            self.fco.ViewObject.ShapeColor = color
        else:
            logger.debug("Bracket object with no fco")
        
    # exports the shape into stl format
    # exportStl has problems in FreeCAD 0.17 when there are cylinders
    # or fillets
    def export_stl (self, name = ""):
        #filepath = os.getcwd()
        if not name:
            name = self.name
        stlPath = filepath + "/stl/"
        stlFileName = stlPath + name + "2.stl"
        # not working well with FreeCAD 0.17
        #self.shp.exportStl(stlFileName)
        mesh_shp = MeshPart.meshFromShape(self.shp,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp.write(stlFileName)
        del mesh_shp
       
#doc = FreeCAD.newDocument()

#al = AluProfBracketPerp ( alusize_lin = 10, alusize_perp = 10,
#                 br_perp_thick = 3.,
#                 br_lin_thick = 3.,
#                 bolt_lin_d = 3,
#                 bolt_perp_d = 3,
#                 nbolts_lin = 1,
#                 xtr_bolt_head = 4,
#                 xtr_bolt_head_d = 2*kcomp.TOL, # space for the nut
#                 reinforce = 0,
#                 fc_perp_ax = VZ,
#                 fc_lin_ax = VX,
#                 pos = V0,
#                 wfco=1,
#                 name = 'bracket_lin3_1bolt_noreinfore')
#al.export_stl()

#AluProfBracketPerp ( alusize_lin = 10, alusize_perp = 10,
#                 br_perp_thick = 3.,
#                 br_lin_thick = 3.,
#                 bolt_d = 3,
#                 nbolts_lin = 2,
#                 xtr_bolt_head = 3,
#                 xtr_bolt_head_d = 2*kcomp.TOL, # space for the nut
#                 reinforce = 0,
#                 fc_perp_ax = VZ,
#                 fc_lin_ax = VX,
#                 pos = V0,
#                 wfco=1,
#                 name = 'bracket_lin3_2bolts_noreinfore')

#doc = FreeCAD.newDocument()

#AluProfBracketPerp ( alusize_lin = 10, alusize_perp = 20,
#                 br_perp_thick = 3.,
#                 br_lin_thick = 3.,
#                 bolt_lin_d = 3,
#                 bolt_perp_d = 3,
#                 nbolts_lin = 2,
#                 bolts_lin_dist = 0,
#                 bolts_lin_rail = 0,
#                 xtr_bolt_head = 3,
#                 xtr_bolt_head_d = 2*kcomp.TOL, # space for the nut
#                 reinforce = 1,
#                 fc_perp_ax = VZ,
#                 fc_lin_ax = VX,
#                 pos = V0,
#                 wfco=1,
#                 name = 'bracket_lin3_1bolt_noreinfore')

#AluProfBracketPerp ( alusize_lin = 20, alusize_perp = 10,
#                 br_perp_thick = 3.,
#                 br_lin_thick = 3.,
#                 bolt_lin_d = 3,
#                 bolt_perp_d = 3,
#                 nbolts_lin = 2,
#                 bolts_lin_dist = 0,
#                 bolts_lin_rail = 0,
#                 xtr_bolt_head = 3,
#                 xtr_bolt_head_d = 2*kcomp.TOL, # space for the nut
#                 reinforce = 1,
#                 fc_perp_ax = VZ,
#                 fc_lin_ax = VX,
#                 pos = V0,
#                 wfco=1,
#                 name = 'bracket_lin3_1bolt_noreinfore')


#AluProfBracketPerp ( alusize_lin = 10, alusize_perp = 10,
#                 br_perp_thick = 3.,
#                 br_lin_thick = 3.,
#                 bolt_lin_d = 4,
#                 bolt_perp_d = 3,
#                 nbolts_lin = 2,
#                 bolts_lin_dist = 25,
#                 bolts_lin_rail = 1,
#                 xtr_bolt_head = 3,
#                 xtr_bolt_head_d = 2*kcomp.TOL, # space for the nut
#                 reinforce = 0,
#                 fc_perp_ax = VZ,
#                 fc_lin_ax = VX,
#                 pos = V0,
#                 wfco=1,
#                 name = 'bracket_lin3_1bolt_noreinfore')
#
#AluProfBracketPerp ( alusize_lin = 25, alusize_perp = 10,
#                 br_perp_thick = 3.,
#                 br_lin_thick = 3.,
#                 bolt_lin_d = 6,
#                 bolt_perp_d = 3,
#                 nbolts_lin = 2,
#                 bolts_lin_dist = 50,
#                 bolts_lin_rail = 1,
#                 xtr_bolt_head = 3,
#                 xtr_bolt_head_d = 2*kcomp.TOL, # space for the nut
#                 reinforce = 1,
#                 fc_perp_ax = VZ,
#                 fc_lin_ax = VX,
#                 pos = V0,
#                 wfco=1,
#                 name = 'bracket_lin3_1bolt_noreinfore')


# ----------- class AluProfBracketPerpWide -----------------------------------

class AluProfBracketPerpFlap (object):

    """ 
    Bracket to join 2 aluminum profiles that are perpendicular,
    that is, they are not on the same plane
    It is wide because it has 2 ears/flaps? on the sides, to attach
    to the perpendicular profile
    ::

        aluprof_perp (perpendicular to the bracket)   
          /  / /  bracket (not drawn)
         /  / /_____
        /  / /_____/|
       /__/ /______|/ aluprof_lin (it is in line with the bracket)
       |__|/


                     fc_perp_ax (is not the axis of the perpendicular
                       :         profile, but the axis of the bracket
       aluprof_perp    :         attached to the perpendicular profile
                    ___:_             
                   |   |  \ bracket  
                  _|___|____\___ .........> fc_line_ax
     alusize_lin +              aluprof_lin
                 :_______________


                         fc_perp_ax
                          :
                          :br_perp_thick
                          .+.
                      ....:__:
                      :   |  |\ 
        alusize_perp  +   |  |   \ 
                      :   |  |______\..
                      :...|__|______|..: br_lin_thick .........> fc_lin_ax
                          :.........:
                             
           

    Parameters
    ----------
    alusize_lin : float
        Width of the aluminum profile on the line
    alusize_perp : float
        Width of the perpendicular aluminum profile
    br_lin_thick : float
        Thickness of the line bracket
    br_perp_thick : float
        Thickness of the perpendicular bracket
    bolt_lin_d : int
        Metric of the bolt 3, 4, ... (integer)
    bolt_perp_d : int
        Metric of the bolt 3, 4, ... (integer) on the profile line
        if 0, the same as bolt_lin_d
    nbolts_lin : int
        * 1: just one bolt on the fc_lin_ax, or two bolts
        * 2: two bolts on the fc_lin_ax, or two bolts
    bolts_lin_dist : float
        If more than one bolt on fc_lin_ax, defines the 
        distance between them.
        if zero, takes min distance
    bolts_lin_rail : int
        Instead of bolt holes, it will be a rail
        it doesn't make sense to have number of bolts with this option
        it will work on 2 bolts or more. If nbolts_lin == 3, it 
        will make a rail between them. so it will be the same to have
        nbolts_lin = 2 and bolts_lin_dist = 20
        nbolts_lin = 3 and bolts_lin_dist = 10
        The rail will be 20, and it will look the same, it will be
        more clear to have the first option: 2 bolts
    xtr_bolt_head : float
        Extra space for the bolt head on the line to the wall
        (perpendicular)
    sunk : int
        * 0: just drilled
        * 1: if the top part is removed,
        * 2: No reinforcement at all
    flap : int
        If it has flaps or if it doesn't have flaps, it is kind of useless
        because it is just the middle part without bolts on the
        wall, but it can be used to make a union with other parts
    fc_perp_ax : FreeCAD.Vector
        Axis of the bracket on the perpendicular profile, see picture
    fc_lin_ax : FreeCAD.Vector
        Axis of the bracket on the aligned profile, see picture
    pos : FreeCAD.Vector
        Position of the center of the bracket on the intersection
    wfco :
        * 1: With FreeCad Object: a freecad object is created
        * 0: only the shape
    name : str
        Name of the freecad object, if created
    """

    def __init__(self, alusize_lin, alusize_perp,
                 br_perp_thick = 3.,
                 br_lin_thick = 3.,
                 bolt_lin_d = 3, #metric of the bolt
                 bolt_perp_d = 0, #metric of the bolt
                 nbolts_lin = 1,
                 bolts_lin_dist = 0,
                 bolts_lin_rail = 0,
                 xtr_bolt_head = 1,
                 sunk = 1,
                 flap = 1,
                 fc_perp_ax = VZ,
                 fc_lin_ax = VX,
                 pos = V0,
                 wfco=1,
                 name = 'bracket_flap'):

        doc = FreeCAD.ActiveDocument
        self.name = name
        boltli_dict = kcomp.D912[bolt_lin_d]
        boltlihead_r = boltli_dict['head_r']
        boltlihead_r_tol = boltli_dict['head_r_tol']
        boltlishank_r_tol = boltli_dict['shank_r_tol']
        boltlihead_l = boltli_dict['head_l']
        if bolt_perp_d == 0:
            bolt_perp_d = bolt_lin_d
        boltpe_dict = kcomp.D912[bolt_perp_d]
        boltpehead_r = boltpe_dict['head_r']
        boltpehead_r_tol = boltpe_dict['head_r_tol']
        boltpeshank_r_tol = boltpe_dict['shank_r_tol']
        boltpehead_l = boltpe_dict['head_l']

        # normalize axis, just in case:
        axis_perp = DraftVecUtils.scaleTo(fc_perp_ax,1)
        axis_lin = DraftVecUtils.scaleTo(fc_lin_ax,1)
        axis_perp_neg = axis_perp.negative()
        axis_lin_neg = axis_lin.negative()
        axis_wid   = axis_perp.cross(axis_lin)

        #Calculate the length of the brlin_l
        #                  :+  br_perp_thick :boltpehead_l
        #                  :  :+xtr_bolt_head
        #                  :  : : + boltlihead_r
        #              ....:__: :  :
        #              :   |  |    :
        # alusize_perp +   |  |   _:_
        #              :   |  |__|___|___ 
        #              :...|_____________|
        #                  :.......:
        #                 +bolt1li_dist=br_perp_thick+xtr_bolt_head+boltlihead_r
        #                          :  :  :
        #                        2 x boltlihead_r
        #                  :.............:
        #                      + brlin_l

        bolt1li_dist = br_perp_thick + xtr_bolt_head + boltlihead_r 

        brlin_l = bolt1li_dist + 2 * boltlihead_r
        if nbolts_lin > 1:
            if bolts_lin_dist == 0:
                # for every new bolt, add 3 times the bolt head radius
                bolts_lin_dist = 3 *  boltlihead_r
            elif bolts_lin_dist <  (3 *  boltlihead_r) :
                logger.warning ('bolt_lin_dist too short')
                bolts_lin_dist = 3 *  boltlihead_r
            brlin_l = brlin_l + (nbolts_lin-1)* bolts_lin_dist

        #                      1
        #              ....:__: : :        _____________________
        #              :   |  |   :       |     ||       ||     |
        # alusize_perp +   |  |  _:_      |  O  ||       ||  O  |
        #              :   |  |_|___|___  |     ||_______||     |
        #              :...|____________| |_____|___:_:___|_____|..axis_wid
        #                  :............: :     :.........:
        #                    + brlin_l    :     :alusize_lin
        #                                 :.....:
        #                                  oneflap_w:
        #                                  min(4xboltpehead_r, alusize_lin)
        #                                 :.....................:
        #                                   totalflap_w

        shp_boxbr = fcfun.shp_box_dir (box_w = alusize_lin,
                                     box_d = brlin_l,
                                     box_h = alusize_perp,
                                     fc_axis_h = axis_perp,
                                     fc_axis_d = axis_lin,
                                     cw = 1, cd = 0, ch = 0,
                                     pos = pos)


        oneflap_w = 0
        if flap == 1:
            oneflap_w = min(4*boltpehead_r, alusize_lin)
            totalflap_w = alusize_lin + 2 * oneflap_w
            shp_flap = fcfun.shp_box_dir (box_w = totalflap_w,
                                          box_d = br_perp_thick,
                                          box_h = alusize_perp,
                                          fc_axis_h = axis_perp,
                                          fc_axis_d = axis_lin,
                                          cw = 1, cd = 0, ch = 0,
                                          pos = pos)

            shp_boxbr = shp_boxbr.fuse(shp_flap)


            chmf_pts = []
            for isg in [-0.5,0.5]:
                chmf_pt_pos = (pos
                           + DraftVecUtils.scale(axis_lin, br_perp_thick)
                           + DraftVecUtils.scale(axis_wid, isg * alusize_lin))
                chmf_pts.append(chmf_pt_pos)

            # reinforcement of the flaps with the central space
            shp_boxbr = fcfun.shp_filletchamfer_dirpts(shp_boxbr,
                                                       fc_axis = axis_perp,
                                                       fc_pts = chmf_pts,
                                                       fillet = 0,
                                                       radius = boltpehead_r )

            doc.recompute()
            shp_boxbr =shp_boxbr.removeSplitter()



        chmf_out_r = min(brlin_l-br_perp_thick, alusize_perp-br_lin_thick)

        chmf_out_pos = (   pos + DraftVecUtils.scaleTo(axis_lin, brlin_l)
                         + DraftVecUtils.scaleTo(axis_perp, alusize_perp))

        shp_boxbr = fcfun.shp_filletchamfer_dirpt(shp_boxbr,
                                                   fc_axis = axis_wid,
                                                   fc_pt = chmf_out_pos,
                                                   fillet = 0,
                                                   radius = chmf_out_r)

        #              ....:__: : :        _____________________
        #              :   |  |   :       |     ||       ||     |
        # alusize_perp +   |  |  _:_      |  O  ||       ||  O  |
        #              :   |  |_|___|___  |     ||_______||     |
        #              :...|____________| |_____|___:_:___|_____|..axis_wid
        #                  :.............:       :.........:
        #                    + brlin_l             + alusize_lin

        boltholes = []
        # inside box: (sunk == 1)
        if sunk > 0:
            # cut the box inside
            # Inside width
            # add one, to have it a minimum of one mm
            if (sunk == 1) and (alusize_lin > 2*(boltlihead_r + kcomp.TOL) + 1):
                inside_w =  2*(boltlihead_r + kcomp.TOL)
                #print ("inside width " + str(inside_w))
            else:
                # no space for reinforcement, or no reinforcement (sunk == 2)
                inside_w = alusize_lin + oneflap_w + 2 # +2 to make the cut

            # chamfer of the inside box
            chmf_in_r = alusize_perp/2. - br_lin_thick -boltlihead_r_tol
            logger.debug ("chamfer radius" + str(chmf_in_r))

            insbox_pos = ( pos + DraftVecUtils.scale(axis_lin,br_perp_thick)
                           + DraftVecUtils.scale(axis_perp,br_lin_thick))
            shp_insbox = fcfun.shp_box_dir (box_w = inside_w,
                                     box_d = brlin_l,
                                     box_h = alusize_perp,
                                     fc_axis_h = axis_perp,
                                     fc_axis_d = axis_lin,
                                     cw = 1, cd = 0, ch = 0,
                                     pos = insbox_pos)
            if chmf_in_r > 0 :
                shp_insbox = fcfun.shp_filletchamfer_dirpt(shp_insbox,
                                                     fc_axis = axis_wid,
                                                     fc_pt = insbox_pos,
                                                     fillet = 0,
                                                     radius = chmf_in_r)
            shp_boxbr = shp_boxbr.cut(shp_insbox)

            #pos_boltpe = pos +DraftVecUtils.scale(axis_perp,alusize_perp/2.) 
            #shp_boltpe= fcfun.shp_cylcenxtr(r=boltshank_r_tol,
            #                    h=brack_thick,
            #                    normal = axis_lin,
            #                    ch = 0, xtr_top = 1, xtr_bot=1,
            #                    pos = pos_boltpe)

        if flap == 1:
            boltpe_dist_w = (alusize_lin+oneflap_w)/2
            for iboltpe in [-boltpe_dist_w,boltpe_dist_w]:
                pos_boltpe =  (pos
                      + DraftVecUtils.scale(axis_perp,alusize_perp/2.)
                      + DraftVecUtils.scale(axis_lin,br_perp_thick+boltpehead_l)
                      + DraftVecUtils.scale(axis_wid, iboltpe))
                shp_boltpe = fcfun.shp_bolt_dir(r_shank = boltpeshank_r_tol,
                              l_bolt = br_perp_thick + boltpehead_l,
                              r_head = boltpehead_r_tol + kcomp.TOL, #extra TOL
                              l_head = boltpehead_l,
                              xtr_head = 2,
                              xtr_shank = 1,
                              support = 0,
                              fc_normal = axis_lin_neg,
                              fc_verx1 = axis_perp, #it doesn't matter
                              pos = pos_boltpe)
                boltholes.append(shp_boltpe)


        # position of the first bolt, on top
        pos_boltli = ( pos + DraftVecUtils.scale(axis_lin,bolt1li_dist) +
                        DraftVecUtils.scale(axis_perp, alusize_perp))
        if bolts_lin_rail == 1 and nbolts_lin > 1:
            # there is rail
            rail_l = (nbolts_lin - 1) * bolts_lin_dist
            # make the hole also for the head of the bolts, even that maybe
            # it is not necessary because it is sunk
            shp_railli = fcfun.shp_2stadium_dir (length = rail_l,
                               r_s = boltlishank_r_tol,
                               r_l = boltlihead_r_tol + kcomp.TOL/2., #extra TOL
                               h_tot = alusize_perp,
                               h_rl = alusize_perp-br_lin_thick,
                               fc_axis_h = axis_perp_neg,
                               fc_axis_l = axis_lin,
                               ref_l = 2, #ref on the circle center
                               rl_h0 = 1, #bolt head is on pos
                               xtr_h = 1,
                               xtr_nh = 1,
                               pos = pos_boltli)
            boltholes.append(shp_railli)
        else :
            # first bolt hole:
            shp_boltli = fcfun.shp_bolt_dir(r_shank = boltlishank_r_tol,
                            l_bolt = alusize_perp,
                            r_head = boltlihead_r_tol + kcomp.TOL/2., #extra TOL
                            l_head = alusize_perp-br_lin_thick,
                            xtr_head = 1,
                            xtr_shank = 1,
                            support = 0,
                            fc_normal = axis_perp_neg,
                            fc_verx1 = axis_lin, #it doesn't matter
                            pos = pos_boltli)
            boltholes.append(shp_boltli)

            #if nbolts_lin > 1:
            for ibolt in range (1, nbolts_lin):
                pos_boltli = (  pos_boltli
                               + DraftVecUtils.scale(axis_lin,bolts_lin_dist)) 
                shp_boltli = fcfun.shp_bolt_dir(r_shank = boltlishank_r_tol,
                            l_bolt = alusize_perp,
                            r_head = boltlihead_r_tol + kcomp.TOL/2., #extra TOL
                            l_head = alusize_perp-br_lin_thick,
                            xtr_head = 1,
                            xtr_shank = 1,
                            support = 0,
                            fc_normal = axis_perp_neg,
                            fc_verx1 = axis_lin, #it doesn't matter
                            pos = pos_boltli)
                boltholes.append(shp_boltli)

        shp_boltfuse = fcfun.fuseshplist(boltholes)

        shp_bracket = shp_boxbr.cut(shp_boltfuse)
        doc.recompute()
        shp_bracket =shp_bracket.removeSplitter()
        doc.recompute()

        self.shp = shp_bracket
        self.wfco = wfco
        if wfco == 1:
            # a freeCAD object is created
            fco_bracket = doc.addObject("Part::Feature", name )
            fco_bracket.Shape = shp_bracket
            self.fco = fco_bracket

    def color (self, color = (1,1,1)):
        if self.wfco == 1:
            self.fco.ViewObject.ShapeColor = color
        else:
            logger.debug("Bracket object with no fco")
        
    # exports the shape into stl format
    def export_stl (self, name = ""):
        #filepath = os.getcwd()
        if not name:
            name = self.name
        stlPath = filepath + "/stl/"
        stlFileName = stlPath + name + ".stl"
        # exportStl is not working well with FreeCAD 0.17
        #self.shp.exportStl(stlFileName)
        mesh_shp = MeshPart.meshFromShape(self.shp,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp.write(stlFileName)
        del mesh_shp

#doc = FreeCAD.newDocument()

#AluProfBracketPerpFlap ( alusize_lin = 10, alusize_perp = 15,
#                         br_perp_thick = 4.,
#                         br_lin_thick = 3.,
#                         bolt_lin_d = 3,
#                         bolt_perp_d = 3,
#                         nbolts_lin = 2,
#                         bolts_lin_dist = 0,
#                         bolts_lin_rail = 0,
#                         xtr_bolt_head = 1,
#                         sunk = 0,
#                         flap = 1, 
#                         fc_perp_ax = VZ,
#                         fc_lin_ax = VX,
#                         pos = V0,
#                         wfco=1,
#                         name = 'bracket3_flap')

#AluProfBracketPerpFlap ( alusize_lin = 15, alusize_perp = 10,
#                         br_perp_thick = 4.,
#                         br_lin_thick = 3.,
#                         bolt_lin_d = 3,
#                         bolt_perp_d = 3,
#                         nbolts_lin = 2,
#                         bolts_lin_dist = 0,
#                         bolts_lin_rail = 0,
#                         xtr_bolt_head = 1,
#                         sunk = 0,
#                         flap = 1, 
#                         fc_perp_ax = VZ,
#                         fc_lin_ax = VX,
#                         pos = V0,
#                         wfco=1,
#                         name = 'bracket3_flap')

#AluProfBracketPerpFlap ( alusize_lin = 25, alusize_perp = 20,
#                         br_perp_thick = 4.,
#                         br_lin_thick = 4.,
#                         bolt_lin_d = 6,
#                         bolt_perp_d = 4.,
#                         nbolts_lin = 2,
#                         bolts_lin_dist = 50,
#                         bolts_lin_rail = 1,
#                         xtr_bolt_head = 1,
#                         sunk = 0,
#                         flap = 1, 
#                         fc_perp_ax = VZ,
#                         fc_lin_ax = VX,
#                         pos = V0,
#                         wfco=1,
#                         name = 'bracket3_flap')


#AluProfBracketPerpFlap ( alusize_lin = 10, alusize_perp = 10,
#                         br_perp_thick = 3.,
#                         br_lin_thick = 3.,
#                         nbolts_lin = 2,
#                         xtr_bolt_head = 1,
#                         sunk = 2,
#                         flap = 1, 
#                         fc_perp_ax = VZ,
#                         fc_lin_ax = VX,
#                         pos = V0,
#                         wfco=1,
#                         name = 'bracket3_flap_sunk')



# ----------- class AluProfBracketPerpTwin -----------------------------------

class AluProfBracketPerpTwin (object):

    """ 
    Bracket to join 3 aluminum profiles that are perpendicular,
    that is, they are not on the same plane
    to the perpendicular profile
    ::

        aluprof_perp (perpendicular to the bracket)   
                    . fc_wide_ax
              ___  .
             /  /|.
            /  / /______
           /  / /______/| aluprof_lin (it is in line with the bracket)
          /  / /_______|/-----------
         /  / /_____              . alu_sep
        /  / *_____/|           .
       /__/ /______|/-----------
       |__|/           aluprof_lin (it is in line with the bracket)
             * shows the reference for the position (argument pos)
               the direction of fc_wide_ax indicates where the other
               line of the bracket will be

                     fc_perp_ax (is not the axis of the perpendicular
                       :         profile, but the axis of the bracket
       aluprof_perp    :         attached to the perpendicular profile
                    ___:_             
                   |   |  \ bracket  
                  _|___|____\___ .........> fc_line_ax
     alusize_lin +              aluprof_lin
                 :_______________


                         fc_perp_ax
                          :
                          :br_perp_thick
                          .+.
                      ....:__:
                      :   |  |\ 
        alusize_perp  +   |  |   \ 
                      :   |  |______\..
                      :...|_________|..: br_lin_thick .........> fc_lin_ax
                          :.........:

                                             * bolt_perp_line
                                            1: * there is a bolt hole
                                            0: * no bolt hole there
                     ....:__: : :         __________________________
                     :   |  |   :         ||       ||     ||       ||
        alusize_perp +   |  |  _:_        ||   *   ||  O  ||   *   ||
                     :   |  |_|___|___    ||_______||     ||_______||
                     :...|____________|   |___:_:___|_____|___:_:__||..axis_wid
                         :.............:  :.........:..+..:
                           + brlin_l           +     union_w          
                                           alusize_lin         :   
                                               :..alu_sep......:
                             
    Parameters
    ----------
    alusize_lin : float
        Width of the aluminum profile on the line
    alusize_perp : float
        Width of the perpendicular aluminum profile
    alu_sep : float
        Separation of the 2 parallel profiles, from their centers
    br_lin_thick : float
        Thickness of the line bracket
    br_perp_thick : float
        Thickness of the perpendicular bracket
    bolt_lin_d : int
        Metric of the bolt 3, 4, ... (integer)
    bolt_perp_d : int
        Metric of the bolt 3, 4, ... (integer) on the profile line
        if 0, the same as bolt_lin_d
    nbolts_lin : int
        * 1: just one bolt on the fc_lin_ax, or two bolts
        * 2: two bolts on the fc_lin_ax, or two bolts
    bolts_lin_dist : float
        If more than one bolt on fc_lin_ax, defines the 
        distance between them.
        if zero, takes min distance
    bolts_lin_rail : int
        Instead of bolt holes, it will be a rail
        it doesn't make sense to have number of bolts with this option
        it will work on 2 bolts or more. If nbolts_lin == 3, it 
        will make a rail between them. so it will be the same to have
        nbolts_lin = 2 and bolts_lin_dist = 20
        nbolts_lin = 3 and bolts_lin_dist = 10
        The rail will be 20, and it will look the same, it will be
        more clear to have the first option: 2 bolts
    bolt_perp_line : int
        * 1: if it has a bolt on the wall (perp) but in line
          with the line aluminum profiles
        * 0: no bolt 
    xtr_bolt_head : float
        Extra space for the bolt head, and making a space for it
        only makes sense if bolt_perp_line == 1
    sunk : int
        * 0: No sunk, just drill holes: bolt_perp_line should be 0
        * 1: sunk, but with reinforcement if possible
        * 2: no reinforcement
    fc_perp_ax : FreeCAD.Vector
        Axis of the bracket on the perpendicular prof, see picture
    fc_lin_ax : FreeCAD.Vector
        Axis of the bracket on the aligned profile, see picture
    fc_wide_ax : FreeCAD.Vector
        Axis of the bracket on wide direction, see picture
        its direction shows where the other aligned profile is
    pos : FreeCAD.Vector
        Position of the center of the bracket on the intersection
    wfco : int 
        * 1: With FreeCad Object: a freecad object is created
        * 0: only the shape
    name : str
        Name of the freecad object, if created
    """

    def __init__(self, alusize_lin, alusize_perp,
                 alu_sep,
                 br_perp_thick = 3.,
                 br_lin_thick = 3.,
                 bolt_lin_d = 3, #metric of the bolt
                 bolt_perp_d = 0, #metric of the bolt
                 nbolts_lin = 1,
                 bolts_lin_dist = 1,
                 bolts_lin_rail = 0,
                 bolt_perp_line = 0,
                 xtr_bolt_head = 3,
                 sunk = 0,
                 fc_perp_ax = VZ,
                 fc_lin_ax = VX,
                 fc_wide_ax = VY,
                 pos = V0,
                 wfco=1,
                 name = 'bracket_twin'):

        doc = FreeCAD.ActiveDocument
        self.name = name

        boltli_dict = kcomp.D912[bolt_lin_d]
        boltlihead_r = boltli_dict['head_r']
        boltlihead_r_tol = boltli_dict['head_r_tol']
        boltlishank_r_tol = boltli_dict['shank_r_tol']
        boltlihead_l = boltli_dict['head_l']
        if bolt_perp_d == 0:
            bolt_perp_d = bolt_lin_d
        boltpe_dict = kcomp.D912[bolt_perp_d]
        boltpehead_r = boltpe_dict['head_r']
        boltpehead_r_tol = boltpe_dict['head_r_tol']
        boltpeshank_r_tol = boltpe_dict['shank_r_tol']
        boltpehead_l = boltpe_dict['head_l']

        # normalize axis, just in case:
        axis_perp = DraftVecUtils.scaleTo(fc_perp_ax,1)
        axis_lin = DraftVecUtils.scaleTo(fc_lin_ax,1)
        axis_perp_neg = axis_perp.negative()
        axis_lin_neg = axis_lin.negative()
        axis_wid  = DraftVecUtils.scaleTo(fc_wide_ax,1) 

        # position of the other profile
        brlin2_pos = pos + DraftVecUtils.scale(axis_wid, alu_sep)
        if bolt_perp_line == 1: # there is bolt
            if sunk == 2:
                reinforce = 0
            else:
                reinforce = 1
            h_brlin1 = AluProfBracketPerp(alusize_lin = alusize_lin,
                                        alusize_perp = alusize_perp,
                                        br_perp_thick = br_perp_thick,
                                        br_lin_thick = br_lin_thick,
                                        bolt_lin_d = bolt_lin_d,
                                        bolt_perp_d = bolt_perp_d,
                                        nbolts_lin = nbolts_lin,
                                        bolts_lin_dist = bolts_lin_dist,
                                        bolts_lin_rail = bolts_lin_rail,
                                        xtr_bolt_head = xtr_bolt_head,
                                        reinforce = reinforce,
                                        fc_perp_ax = axis_perp,
                                        fc_lin_ax = axis_lin,
                                        pos = pos,
                                        wfco = 0)
            h_brlin2 = AluProfBracketPerp(alusize_lin = alusize_lin,
                                        alusize_perp = alusize_perp,
                                        br_perp_thick = br_perp_thick,
                                        br_lin_thick = br_lin_thick,
                                        bolt_lin_d = bolt_lin_d,
                                        bolt_perp_d = bolt_perp_d,
                                        nbolts_lin = nbolts_lin,
                                        bolts_lin_dist = bolts_lin_dist,
                                        bolts_lin_rail = bolts_lin_rail,
                                        xtr_bolt_head = xtr_bolt_head,
                                        reinforce = reinforce,
                                        fc_perp_ax = axis_perp,
                                        fc_lin_ax = axis_lin,
                                        pos = brlin2_pos,
                                        wfco = 0)
        else: # no hole:
            h_brlin1 = AluProfBracketPerpFlap (
                                        alusize_lin = alusize_lin,
                                        alusize_perp = alusize_perp,
                                        br_perp_thick = br_perp_thick,
                                        br_lin_thick = br_lin_thick,
                                        bolt_lin_d = bolt_lin_d,
                                        bolt_perp_d = bolt_perp_d,
                                        nbolts_lin = nbolts_lin,
                                        bolts_lin_dist = bolts_lin_dist,
                                        bolts_lin_rail = bolts_lin_rail,
                                        xtr_bolt_head = xtr_bolt_head,
                                        sunk = sunk,
                                        flap = 0, #no flap
                                        fc_perp_ax = axis_perp,
                                        fc_lin_ax = axis_lin,
                                        pos = pos,
                                        wfco = 0)
            h_brlin2 = AluProfBracketPerpFlap (
                                        alusize_lin = alusize_lin,
                                        alusize_perp = alusize_perp,
                                        br_perp_thick = br_perp_thick,
                                        br_lin_thick = br_lin_thick,
                                        bolt_lin_d = bolt_lin_d,
                                        bolt_perp_d = bolt_perp_d,
                                        nbolts_lin = nbolts_lin,
                                        bolts_lin_dist = bolts_lin_dist,
                                        bolts_lin_rail = bolts_lin_rail,
                                        xtr_bolt_head = xtr_bolt_head,
                                        sunk = sunk,
                                        flap = 0, #no flap
                                        fc_perp_ax = axis_perp,
                                        fc_lin_ax = axis_lin,
                                        pos = brlin2_pos,
                                        wfco = 0)

        shp_brlin1 = h_brlin1.shp
        shp_brlin2 = h_brlin2.shp

        # center of the 2, to make the union between both
        pos_mid = pos + DraftVecUtils.scale(axis_wid, alu_sep/2.)

        # box_w has +2 to make the union
        union_w = alu_sep-alusize_lin
        shp_union = fcfun.shp_box_dir (box_w = union_w + 2,
                                       box_d = br_perp_thick,
                                       box_h = alusize_perp,
                                       fc_axis_h = axis_perp,
                                       fc_axis_d = axis_lin,
                                       cw = 1, cd = 0, ch = 0,
                                       pos = pos_mid)

        shp_twinbr = fcfun.fuseshplist([shp_brlin1, shp_union, shp_brlin2])
        
        doc.recompute()
        shp_twinbr = shp_twinbr.removeSplitter()

        # chamfer the union 
        chmf_pts = []
        chmf_pt_pos = (pos + DraftVecUtils.scaleTo(axis_lin, br_perp_thick)
                    + DraftVecUtils.scaleTo(axis_wid, alu_sep- alusize_lin/2.))
        chmf_pts.append(chmf_pt_pos)
        chmf_pt_pos = (pos + DraftVecUtils.scaleTo(axis_lin, br_perp_thick)
                         + DraftVecUtils.scaleTo(axis_wid, alusize_lin/2.))
        chmf_pts.append(chmf_pt_pos)


        shp_twinbr = fcfun.shp_filletchamfer_dirpts(shp_twinbr,
                                                    fc_axis = axis_perp,
                                                    fc_pts = chmf_pts,
                                                    fillet = 0,
                                                    radius = boltpehead_r )

        doc.recompute()
        shp_twinbr = shp_twinbr.removeSplitter()

        bolthole_list = []
        if bolt_perp_line == 1 or union_w < 8 * boltpehead_r:
            # one bolt in the middle
            pos_boltpe =  (pos
                    + DraftVecUtils.scale(axis_perp,alusize_perp/2.)
                    + DraftVecUtils.scale(axis_lin,br_perp_thick+boltpehead_l)
                    + DraftVecUtils.scale(axis_wid, alu_sep/2.))
            shp_boltpe = fcfun.shp_bolt_dir(r_shank = boltpeshank_r_tol,
                            l_bolt = br_perp_thick + boltpehead_l,
                            r_head = boltpehead_r_tol + kcomp.TOL, #extra TOL
                            l_head = boltpehead_l,
                            xtr_head = 2,
                            xtr_shank = 1,
                            support = 0,
                            fc_normal = axis_lin_neg,
                            fc_verx1 = axis_perp, #it doesn't matter
                            pos = pos_boltpe)
            bolthole_list.append(shp_boltpe)
        else:
            # 2 holes:
            boltpe_w_pos1 = alusize_lin/2. + 2* boltpehead_r
            boltpe_w_pos2 = alu_sep - alusize_lin/2. - 2* boltpehead_r
            for w_pos in [boltpe_w_pos1, boltpe_w_pos2]:
                pos_boltpe =  (pos
                    + DraftVecUtils.scale(axis_perp,alusize_perp/2.)
                    + DraftVecUtils.scale(axis_lin,br_perp_thick+boltpehead_l)
                    + DraftVecUtils.scale(axis_wid, w_pos))
                shp_boltpe = fcfun.shp_bolt_dir(r_shank = boltpeshank_r_tol,
                            l_bolt = br_perp_thick + boltpehead_l,
                            r_head = boltpehead_r_tol + kcomp.TOL, #extra TOL
                            l_head = boltpehead_l,
                            xtr_head = 2,
                            xtr_shank = 1,
                            support = 0,
                            fc_normal = axis_lin_neg,
                            fc_verx1 = axis_perp, #it doesn't matter
                            pos = pos_boltpe)
                bolthole_list.append(shp_boltpe)

        shp_boltpe = fcfun.fuseshplist(bolthole_list)

        shp_twinbr = shp_twinbr.cut(shp_boltpe)
        doc.recompute()
        shp_bracket =shp_twinbr.removeSplitter()
        doc.recompute()

        self.shp = shp_bracket
        self.wfco = wfco
        if wfco == 1:
            # a freeCAD object is created
            fco_bracket = doc.addObject("Part::Feature", name )
            fco_bracket.Shape = shp_bracket
            self.fco = fco_bracket

    def color (self, color = (1,1,1)):
        if self.wfco == 1:
            self.fco.ViewObject.ShapeColor = color
        else:
            logger.debug("Bracket object with no fco")

    # exports the shape into stl format
    def export_stl (self, name = ""):
        #filepath = os.getcwd()
        if not name:
            name = self.name
        stlPath = filepath + "/stl/"
        stlFileName = stlPath + name + ".stl"
        # exportStl not working well with FreeCAD 0.17
        #self.shp.exportStl(stlFileName)
        mesh_shp = MeshPart.meshFromShape(self.shp,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp.write(stlFileName)
        del mesh_shp


    
#doc = FreeCAD.newDocument()

#AluProfBracketPerpTwin ( alusize_lin = 10, alusize_perp = 10,
#                 alu_sep = 40.,
#                 br_perp_thick = 3.,
#                 br_lin_thick = 3.,
#                 bolt_d = 3,
#                 nbolts_lin = 2,
#                 bolt_perp_line = 0,
#                 xtr_bolt_head = 2, 
#                 sunk = 2,
#                 fc_perp_ax = VZ,
#                 fc_lin_ax = VX,
#                 fc_wide_ax = VY,
#                 pos = V0,
#                 wfco=1,
#                 name = 'bracket_twin3')

#AluProfBracketPerpTwin ( alusize_lin = 16, alusize_perp = 30,
#                 alu_sep = 25.,
#                 br_perp_thick = 4.,
#                 br_lin_thick = 4.,
#                 bolt_lin_d = 6,
#                 bolt_perp_d = 4,
#                 nbolts_lin = 2,
#                 bolts_lin_dist = 15,
#                 bolts_lin_rail = 1,
#                 bolt_perp_line = 0,
#                 xtr_bolt_head = 4, # more extra because of the perp bolt
#                 sunk = 0,
#                 fc_perp_ax = VZ,
#                 fc_lin_ax = VX,
#                 fc_wide_ax = VY,
#                 pos = V0,
#                 wfco=1,
#                 name = 'bracket_twin3_perp')

#AluProfBracketPerpTwin ( alusize_lin = 16, alusize_perp = 15,
#                 alu_sep = 25.,
#                 br_perp_thick = 4.,
#                 br_lin_thick = 4.,
#                 bolt_lin_d = 6,
#                 bolt_perp_d = 3,
#                 nbolts_lin = 2,
#                 bolts_lin_dist = 15,
#                 bolts_lin_rail = 1,
#                 bolt_perp_line = 0,
#                 xtr_bolt_head = 4, # more extra because of the perp bolt
#                 sunk = 0,
#                 fc_perp_ax = VZ,
#                 fc_lin_ax = VX,
#                 fc_wide_ax = VY,
#                 pos = V0,
#                 wfco=1,
#                 name = 'bracket_twin3_perp')

#AluProfBracketPerpTwin ( alusize_lin = 16, alusize_perp = 10,
#                 alu_sep = 25.,
#                 br_perp_thick = 3.,
#                 br_lin_thick = 3.,
#                 bolt_lin_d = 6,
#                 bolt_perp_d = 3.,
#                 nbolts_lin = 2,
#                 bolts_lin_dist = 15,
#                 bolts_lin_rail = 1,
#                 bolt_perp_line = 0,
#                 xtr_bolt_head = 4, # more extra because of the perp bolt
#                 sunk = 0,
#                 fc_perp_ax = VZ,
#                 fc_lin_ax = VX,
#                 fc_wide_ax = VY,
#                 pos = V0,
#                 wfco=1,
#                 name = 'bracket_twin3_perp')



# ----------- class IdlePulleyHolder ---------------------------
# Creates a holder for a IdlePulley. Usually made of bolts, washers and bearings
# It may include a space for a endstop
# It is centered at the idle pulley, but at the back, and at the profile height
#
#          hole for endstop
#         /   []: hole for the nut
#       ________  ___ 
#      ||__|    |    + above_h
#   ___|     [] |____:__________  Z=0
#      |        |      :         aluminum profile
#      | O    O |      :
#      |________|      + profile_size
#   __________________:________
#
#        O: holes for bolts to attach to the profile
#                 
#               Z 
#               :
#        _______:__ ...
#       /         /|   :
#      /________ / |   :
#      ||__|    |  |   + height
#      |     [] |  |   :
#      |        |  | ..:
#      | O    O | /    
#      |________|/.. + depth 
#      :        :
#      :........:
#          + width
#
#   attach_dir = '-y'  enstop_side= 1     TOP VIEW
#
#
#                Y
#                :                
#                :
#              __:_________
#             |  :   |__| |
#             | (:)       |
#          ...|__:________|..... X
#
# ----- Arguments:
# profile_size: size of the aluminum profile. 20mm, 30mm
# pulleybolt_d: diameter of the bolt used to hold the pulley
# holdbolt_d: diameter of the bolts used to attach this part to the aluminum
#   profile
# above_h: height of this piece above the aluminum profile
# rail: possibility of having a rail instead of holes for mounting the 
#       holder. It has been made fast, so there may be bugs
# mindepth: If there is a minimum depth. Sometimes needed for the endstop
#            to reach its target
# attach_dir: Normal vector to where the holder is attached:'x','-x','y','-y'
#             NOW ONLY -y IS SUPPORTED. YOU CAN ROTATE IT
# endstop_side: -1, 0, 1. Side where the enstop will be
#                if attach_dir= 'x', this will be referred to the y axis 
#                if 0, there will be no endstop
# endstop_h: height of the endstop. If 0 it will be just on top of the profile
# ----- Attributes:
# depth    : depth of the holder
# width    : depth of the holder
# height    : depth of the holder
# fco      : cad object of the compound

class IdlePulleyHolder (object):
    """
    Creates a holder for a IdlePulley. Usually made of bolts, washers and bearings
    It may include a space for a endstop
    It is centered at the idle pulley, but at the back, and at the profile height
    ::

              hole for endstop
             /   []: hole for the nut
           ________  ___ 
          ||__|    |    + above_h
       ___|     [] |____:__________  Z=0
          |        |      :         aluminum profile
          | O    O |      :
          |________|      + profile_size
       __________________:________
     
            O: holes for bolts to attach to the profile
                     
                   Z 
                   :
            _______:__ ...
           /         /|   :
          /________ / |   :
          ||__|    |  |   + height
          |     [] |  |   :
          |        |  | ..:
          | O    O | /    
          |________|/.. + depth 
          :        :
          :........:
              + width
     
       attach_dir = '-y'  enstop_side= 1     TOP VIEW
     
     
                    Y
                    :                
                    :
                  __:_________
                 |  :   |__| |
                 | (:)       |
              ...|__:________|..... X

    Parameters
    ----------
    profile_size : float
        Size of the aluminum profile. 20mm, 30mm
    pulleybolt_d : float
        Diameter of the bolt used to hold the pulley
    holdbolt_d : float
        Diameter of the bolts used to attach this part to the aluminum
        profile
    above_h : float
        Height of this piece above the aluminum profile
    rail : float
        Possibility of having a rail instead of holes for mounting the 
        holder. It has been made fast, so there may be bugs
    mindepth : float
        If there is a minimum depth. Sometimes needed for the endstop
        to reach its target
    attach_dir : str
        Normal vector to where the holder is attached:'x','-x','y','-y'
        NOW ONLY -y IS SUPPORTED. YOU CAN ROTATE IT
    endstop_side : int
        -1, 0, 1. Side where the enstop will be
        if attach_dir= 'x', this will be referred to the y axis 
        if 0, there will be no endstop
    endstop_h : float
        Height of the endstop. If 0 it will be just on top of the profile
    pos : FreeCAD.Vector
        Object Placement 

    Attributes
    ----------
    depth : float
        Depth of the holder
    width : float
        Width of the holder
    height : float
        Height of the holder
    fcoFat : 
        Cad object of the compound

    """
    def __init__ (self, profile_size, pulleybolt_d, holdbolt_d, above_h,
                  rail = 0,
                  mindepth = 0,
                  attach_dir = '-y', endstop_side = 0,
                  endstop_posh = 0,
                  pos = V0,
                  name = "idlepulleyhold"):

        doc = FreeCAD.ActiveDocument

        self.profile_size = profile_size
        self.pulleybolt_d = pulleybolt_d
        self.holdbolt_d   = holdbolt_d
        self.above_h      = above_h

        
        # extra width on each side of the nut
        extra_w = 4.
        # ----------------- Depth calculation
        pulleynut_d = kcomp.NUT_D934_D[int(pulleybolt_d)]
        pulleynut_d_tol = pulleynut_d + 3*TOL
        pulleydepth = pulleynut_d + 2 * extra_w
        depth = max(pulleydepth, mindepth)
        if endstop_side != 0:
            extra_endstop = 3.
            endstop_l =  kcomp.ENDSTOP_B['L']
            endstop_ht =  kcomp.ENDSTOP_B['HT']
            endstop_h =  kcomp.ENDSTOP_B['H']
            endstopdepth = endstop_ht + extra_endstop + extra_w
            depth = max (endstopdepth, depth)
            endstop_boltsep = kcomp.ENDSTOP_B['BOLT_SEP']
            endstop_bolt_h = kcomp.ENDSTOP_B['BOLT_H']
            endstop_bolt_d = kcomp.ENDSTOP_B['BOLT_D']
            # distance of the bolt to the end
            endstop_bolt2lend = (endstop_l - endstop_boltsep)/2.
            # distance of the bolt to the topend
            endstop_bolt2hend = endstop_h - endstop_bolt_h
        self.depth = depth

        # ----------------- Width calculation
        holdbolthead_d = kcomp.D912_HEAD_D[int(holdbolt_d)]
        # the minimum width due to the holding bolts
        minwidth_holdbolt = 2 * holdbolthead_d + 4*extra_w
        # the minimum width due to the endstop
        if endstop_side == 0:
            endstop_l = 0
            endstop_ht = 0
            minwidth_endstop = 0
        else:
            minwidth_endstop = (  endstop_l
                                + 2*TOL
                                + pulleynut_d_tol
                                + 3*extra_w )
        width = max(minwidth_holdbolt, minwidth_endstop)
        self.width = width

        # ----------------- Height calculation
        base_h = .9 * profile_size # no need to go all the way down
        height = base_h + above_h
        self.height = height

#   attach_dir = '-y'  enstop_side= 1
#
#
#                Y
#                :                
#                :
#       p10    __:_________ p11
#             |  :   |__| |
#             | (:)       |        depth
#          ...|__:________|..... X
#           p00          p01 
#                 width
#                :
#      
#                      Y
#                      :
#       p11    ________:__ p01
#             | |__|   :  |
#             |       (:) |        depth
#          ...|________:__|..... X
#           p10          p00 
#                 width


        # Constants to dimensions
        # holding bolts that will be shank in the piece, the rest will be
        # for the head
        bolt_shank = 5.
        
        # holes for the holding bolts
        # separation from the center of the hole to the end
        hbolt_endsep =  extra_w + holdbolthead_d/2.
        # separation between the holding bolts
        hbolt_sep = width - 2 * ( extra_w + holdbolthead_d/2.)
        
        # Nut for the pulley bolt
        pulleynut_h = kcomp.NUT_D934_L[int(pulleybolt_d)]
        pulleynut_hole_h = kcomp.NUT_HOLE_MULT_H * pulleynut_h
        # height inside the piece of the pulley bolt
        # adding 1 to give enough space to the 25mm bolt, it was to tight
        pulleybolt_h = 2 * extra_w + pulleynut_hole_h +1

        if attach_dir == '-y':
            if endstop_side == 0:
                p0x = - width/2.
                p1x = + width/2.
                sg = 1 #sign
            else:
                sg = endstop_side # sign
                p0x = sg * (- pulleynut_d_tol/2. - extra_w)
                p1x =  p0x + sg * width
            p00 = FreeCAD.Vector ( p0x, 0, - base_h)
            p01 = FreeCAD.Vector ( p1x, 0, - base_h)
            p11 = FreeCAD.Vector ( p1x, depth, - base_h)
            p10 = FreeCAD.Vector ( p0x, depth, - base_h)


            shp_wire_base = Part.makePolygon([p00,p01, p11, p10, p00])
            shp_face_base = Part.Face(shp_wire_base)
            shp_box = shp_face_base.extrude(FreeCAD.Vector(0,0,height))

            hbolt_p0x = p0x + sg * hbolt_endsep
            #shank of holding bolt
            pos_shank_hbolt0 = FreeCAD.Vector(hbolt_p0x,
                                              -1,
                                             -profile_size/2.)
            if rail == 0:
                shp_shank_hbolt0 = fcfun.shp_cyl ( r = holdbolt_d/2. + TOL,
                                               h= bolt_shank + 2, normal = VY,
                                               pos = pos_shank_hbolt0)
                if depth > bolt_shank :
                    pos_head_hbolt0 = FreeCAD.Vector(hbolt_p0x,
                                                 bolt_shank,
                                                 -profile_size/2.)
                    shp_head_hbolt0 = fcfun.shp_cyl (
                                           r = holdbolthead_d/2. + TOL,
                                           h = depth - bolt_shank + 1,
                                           normal = VY,
                                           pos = pos_head_hbolt0)
                    shp_hbolt0 = shp_shank_hbolt0.fuse(shp_head_hbolt0)
                else: # no head
                    shp_hbolt0 = shp_shank_hbolt0 
                shp_hbolt1 = shp_hbolt0.copy()
                # It is in zero
                shp_hbolt1.Placement.Base.x = sg * hbolt_sep
            else:
                rail = min(rail, above_h-profile_size/2.)
                shp_shank_hbolt0 = fcfun.shp_stadium_dir (
                                            length = rail,
                                            radius = holdbolt_d/2. + TOL,
                                            height= bolt_shank + 2,
                                            fc_axis_l = VZ,
                                            fc_axis_h = VY,
                                            ref_l = 2, ref_h = 2,
                                            pos = pos_shank_hbolt0)
                if depth > bolt_shank :
                    pos_head_hbolt0 = FreeCAD.Vector(hbolt_p0x,
                                                 bolt_shank,
                                                 -profile_size/2.)
                    shp_head_hbolt0 = fcfun.shp_stadium_dir (
                                           length = rail,
                                           radius = holdbolthead_d/2. + TOL,
                                           height = depth - bolt_shank + 1,
                                           fc_axis_l = VZ,
                                           fc_axis_h = VY,
                                            ref_l = 2, ref_h = 2,
                                           pos = pos_head_hbolt0)
                    shp_hbolt0 = shp_shank_hbolt0.fuse(shp_head_hbolt0)
                else: # no head
                    shp_hbolt0 = shp_shank_hbolt0 
                shp_hbolt1 = shp_hbolt0.copy()
                # It is in zero
                shp_hbolt1.Placement.Base.x = sg * hbolt_sep

            # hole for the pulley bolt
            pulleybolt_pos = FreeCAD.Vector (0, depth - pulleydepth/2.,
                                             above_h - pulleybolt_h)
            shp_pulleybolt = fcfun.shp_cyl (r = pulleybolt_d/2. + 0.9*TOL/2,
                                            h = pulleybolt_h + 1,
                                            normal = VZ,
                                            pos = pulleybolt_pos)
                                   
                                            
            holes_list = [shp_hbolt0, shp_hbolt1]
            # hole for the nut:

            # hole for the endstop
            if endstop_side != 0:
                #endstopbox_l = endstop_l + 2*TOL
                #endstopbox_w = endstop_ht + extra_endstop + TOL
                endstopbox_l = endstop_l + 2*TOL + extra_w + 1
                endstopbox_w = depth + 2
                #endstop_posx = p1x + sg*(extra_w + endstopbox_l/2.)
                endstop_posx = p1x - sg*(endstopbox_l/2. -1)
                endstop_posy = (depth - endstopbox_w )
                #endstop_posy = (depth - endstopbox_w )
                endstop_posy = -1

                endstop_pos = FreeCAD.Vector(endstop_posx, endstop_posy,
                                             endstop_posh)
                shp_endstop = fcfun.shp_boxcen(x=endstopbox_l,
                                               y=endstopbox_w,
                                               z=above_h-endstop_posh +1,
                                               cx=1,
                                               pos=endstop_pos)
                holes_list.append(shp_endstop)

                # hole for the bolts of the endstop
                endstopbolt0_pos = FreeCAD.Vector(
                                  endstop_posx - endstop_boltsep/2.,
                                  depth - endstop_bolt2hend,
                                  endstop_posh + 1)
                shp_endstopbolt0 = fcfun.shp_cyl (
                                        r= endstop_bolt_d/2. + TOL/2.,
                                        h = extra_w + 1,
                                        normal = fcfun.VZN,
                                        pos=endstopbolt0_pos)
                holes_list.append(shp_endstopbolt0)
                shp_endstopbolt1 = shp_endstopbolt0.copy()
                shp_endstopbolt1.Placement.Base.x = endstop_boltsep
                holes_list.append(shp_endstopbolt1)

            shp_holes = shp_pulleybolt.multiFuse(holes_list)
            shp_pulleyhold = shp_box.cut(shp_holes)

            pulleyhold_aux = doc.addObject("Part::Feature", name + '_aux')
            pulleyhold_aux.Shape = shp_pulleyhold

            # fillet the top part if it has no endstop. So the belt doesn't
            # hit the corner
            if endstop_side == 0:
                fillet_r = (width - pulleynut_d_tol - 2 * extra_w) / 2.
                pulleyhold_aux = fcfun.filletchamfer(
                                       fco = pulleyhold_aux,
                                       e_len = depth,
                                       name = name + '_chmf',
                                       fillet = 1,
                                       radius = fillet_r,
                                       axis = 'y',
                                       zpos_chk = 1,
                                       zpos = above_h)
                                          


            h_nuthole = fcfun.NutHole (nut_r = pulleynut_d_tol/2.,
                                       nut_h = pulleynut_hole_h,
                                       hole_h = pulleydepth/2. + TOL,
                                       name = name + '_nuthole',
                                       extra = 1,
                                       nuthole_x = 0,
                                       cx = 1, cy = 0, holedown = 0)
            nuthole = h_nuthole.fco
            nuthole.Placement.Rotation = FreeCAD.Rotation(VX,-90)
            nuthole.Placement.Base.y = depth - pulleydepth/2. - TOL
            nuthole.Placement.Base.z = above_h - extra_w
            
            pulley_holder = doc.addObject("Part::Cut", name)
            pulley_holder.Base = pulleyhold_aux    
            pulley_holder.Tool = nuthole    
            pulley_holder.Placement.Base = pos

            self.fco = pulley_holder

        doc.recompute()

    def color (self, color = (1,1,1)):
        self.fco.ViewObject.ShapeColor = color

            
            
        

#doc = FreeCAD.newDocument()

#idp = IdlePulleyHolder( profile_size=20.,
#                        pulleybolt_d=3.,
#                        holdbolt_d = 5,
#                        #above_h = 47-15-9.5,
#                        above_h = 35. - 1.,
#                        mindepth = 0,
#                        attach_dir = '-y',
#                        endstop_side = 0,
#                        endstop_posh = 0,
#                        name = "idlepulleyhold")


#idp = IdlePulleyHolder( profile_size=30.,
#                        pulleybolt_d=3.,
#                        holdbolt_d = 4,
#                        above_h = 40,
#                        rail = 30,
#                        mindepth = 0,
#                        attach_dir = '-y',
#                        endstop_side = 0,
#                        endstop_posh = 0,
#                        name = "idlepulleyhold")




# Holder for the endstop to be attached to the rail of SEB15A_R
# Made fast and with hardcoded constants, no parametric


def endstopholder_rail ():

    in_w = kcomp.SEB15A_R['rw']
    add_w = 4.
    #out_w = in_w + 2 * add_w
    out_w = 36.

    ends_d = 6.  #endstop depth
    supp_d = 12.5 # support depth

    total_d = supp_d - ends_d + add_w

    bolt_h = 18.
    extra_h = 5.

    total_h = bolt_h + extra_h + add_w
    obox = fcfun.shp_boxcenfill(out_w, total_d, total_h, 1,
                                cx=1, cy=0, cz=0)


    ibox = fcfun.shp_boxcen(in_w + 1.5 * TOL, add_w + 1, total_h + 2,
                            cx=1, cy=0, cz=0, pos = FreeCAD.Vector(0, -1,-1))


    endsbolt2top = 7. # distance of the endstop bolt to the top
    endsboltsep = 9.6 # distance between endstop bolts
    endsbolt_depth = 5.5 # depth of the holes
    endsbolt_diam = 2.5 # diameter

    ends_bolt_pos0 = FreeCAD.Vector ( endsboltsep/2., total_d +1,
                                      total_h - endsbolt2top)
    ends_bolt0 = fcfun.shp_cyl (r=endsbolt_diam/2.+TOL/2.,
                                h = endsbolt_depth +1,
                                normal = VYN,
                                pos = ends_bolt_pos0) 
    ends_bolt_pos1 = FreeCAD.Vector ( -endsboltsep/2.,
                                       total_d +1,
                                       total_h - endsbolt2top)
    ends_bolt1 = fcfun.shp_cyl (r=endsbolt_diam/2.+TOL/2.,
                                h = endsbolt_depth +1,
                                normal = VYN,
                                pos = ends_bolt_pos1) 

    ends_bolt_pos00 = FreeCAD.Vector ( endsboltsep*1.5,
                                       total_d +1,
                                       total_h - endsbolt2top)
    ends_bolt00 = fcfun.shp_cyl (r=endsbolt_diam/2.+TOL/2.,
                                 h = endsbolt_depth +1,
                                 normal = VYN,
                                 pos = ends_bolt_pos00) 
    ends_bolt_pos11 = FreeCAD.Vector ( -endsboltsep*1.5,
                                        total_d +1,
                                        total_h - endsbolt2top)

    ends_bolt11 = fcfun.shp_cyl (r=endsbolt_diam/2.+TOL/2.,
                                 h = endsbolt_depth +1,
                                 normal = VYN,
                                 pos = ends_bolt_pos11) 



    railbolt_d = 3.

    railbolt = fcfun.shp_boxcenfill ( x=railbolt_d + 0.8*TOL,
                                      y= total_d + 2,
                                      z = railbolt_d + extra_h,
                                      fillrad = railbolt_d/2.,
                                      fx = 0, fy=1, fz=0,
                                      cx=1, cy=0, cz=0,
                                      pos = FreeCAD.Vector(0, -1, add_w))


    railbolthead_d = kcomp.D912_HEAD_D[int(railbolt_d)]

    railbolt_head_pos =  FreeCAD.Vector(
                                     0,
                                     add_w+3,
                                     add_w-railbolthead_d/2. + railbolt_d/2. )

    railbolt_head = fcfun.shp_boxcenfill (x=railbolthead_d + TOL,
                                          y= total_d + 2,
                                          z = railbolthead_d + extra_h,
                                          fillrad = railbolthead_d/2.,
                                          fx = 0, fy=1, fz=0,
                                          cx=1, cy=0, cz=0,
                                          pos = railbolt_head_pos)

    shp_fusecut = ibox.multiFuse([ends_bolt0, ends_bolt1,
                                  ends_bolt00, ends_bolt11,
                                  railbolt, railbolt_head])

    box = obox.cut(shp_fusecut)
    #Part.show (box)
    return (box)

class SimpleEndstopHolder (object):

    """
    Very simple endstop holder to be attached to a alu profile and
    that can be adjusted
    ::
    
              rail_l         fc_axis_w
           ...+....           :
          :        :          :
        ______________________:
       |   ________           |
       |  (________)      O   |
       |   ________           |-----> fc_axis_d
       |  (________)      O   |
       |______________________|
                    :          :
                    estp_tot_h

       ref_d points:          fc_axis_h
                              :
       1___2______3_______4___5.............     ref_h = 2
       | :..........:    : : |:.....       + h
       |__:________:_____:_:_|:.....base_h.:     ref_h = 1


       ref_w points
                             fc_axis_w
        _____________________ :
       |   ________     |    |:
       |  (________) ---| 0  |:
       1   ________  ---|    |:-----> fc_axis_d.
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
    fc_axis_d : FreeCAD Vector
        Axis along the depth
    fc_axis_w : FreeCAD Vector
        Axis along the width
    fc_axis_h : FreeCAD Vector
        Axis along the height
    ref_d : int
        Reference (zero) of fc_axis_d

            * 1 = at the end on the side of the rails
            * 2 = at the circle center of one rail (closer to 1)
            * 3 = at the circle center of the other rail, closer to endstop
            * 4 = at the bolt of the endstop
            * 5 = at the end of the endstop (the holder ends before that)

    ref_w : int
        Reference on fc_axis_w. it is symmetrical, only the negative side

            * 1 = centered
            * 2 = at one endstop bolt
              the other endstop bolt will be on the direction of fc_axis_w
            * 3 = at one rail center
              the rail center will be on the direction of fc_axis_w
            * 4 = at the end
              the end will be on the direction of fc_axis_w

    ref_h : int
        Reference (zero) of fc_axis_h

            * 1: at the bottom
            * 2: on top

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
                 fc_axis_d = VX,
                 fc_axis_w = V0,
                 fc_axis_h = VZ,
                 ref_d = 1,
                 ref_w = 1,
                 ref_h = 1,
                 pos = V0,
                 wfco = 1,
                 name = 'simple_enstop_holder'):

        self.wfco = wfco
        self.name = name
        self.base_h = base_h,
        doc = FreeCAD.ActiveDocument
        # normalize the axis
        axis_h = DraftVecUtils.scaleTo(fc_axis_h,1)
        axis_d = DraftVecUtils.scaleTo(fc_axis_d,1)
        if fc_axis_w == V0:
            axis_w = axis_h.cross(axis_d)
        else:
            axis_w = DraftVecUtils.scaleTo(fc_axis_w,1)
        axis_h_n = axis_h.negative()
        axis_d_n = axis_d.negative()
        axis_w_n = axis_w.negative()    

        self.axis_h = axis_h
        self.axis_d = axis_d
        self.axis_w = axis_w
        # best axis to print, to be pointing up:
        self.axis_print = axis_h

        self.d_endstop = d_endstop

        #                              :holder_out
        #      __:________:____________: :..................
        #     |   _________      |     |                   :
        #     |  (_________) ----| 0   |                   + tot_w
        #     |   _________  ----|     |-----> fc_axis_d   :
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
        #     |   _________  ----|       |-----> fc_axis_d   :
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
            # Taking the minimum length, very tight
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
        dis_1_2_d = 2* mbolt_head_r
        dis_1_3_d = dis_1_2_d + rail_l
        #dis_2_3_d = rail_l
        dis_1_5_d = tot_d + holder_out
        dis_1_4_d = dis_1_5_d - (estp_d - estp_bolt_dist)
        # distances to the new point, that is the second bolt hole, if exists
        if estop_2ndbolt_topdist > 0 :
            dis_1_6_d = dis_1_5_d - estop_2ndbolt_topdist
        else:
            # same as 4: (to avoid errors) it will be the same hole
            dis_1_6_d = dis_1_4_d

        fc_1_2_d = DraftVecUtils.scale(axis_d, dis_1_2_d)
        fc_1_3_d = DraftVecUtils.scale(axis_d, dis_1_3_d)
        fc_1_4_d = DraftVecUtils.scale(axis_d, dis_1_4_d)
        fc_1_5_d = DraftVecUtils.scale(axis_d, dis_1_5_d)
        fc_1_6_d = DraftVecUtils.scale(axis_d, dis_1_6_d)
        # vector from the reference point to point 1 on axis_d
        if ref_d == 1: 
            refto_1_d = V0
        elif ref_d == 2:
            refto_1_d = fc_1_2_d.negative()
        elif ref_d == 3:
            refto_1_d = fc_1_3_d.negative()
        elif ref_d == 4:
            refto_1_d = fc_1_4_d.negative()
        elif ref_d == 5:
            refto_1_d = fc_1_5_d.negative()
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

        fc_1_2_w = DraftVecUtils.scale(axis_w_n, dis_1_2_w)
        fc_1_3_w = DraftVecUtils.scale(axis_w_n, dis_1_3_w)
        fc_1_4_w = DraftVecUtils.scale(axis_w_n, dis_1_4_w)
        # vector from the reference point to point 1 on axis_w
        if ref_w == 1: 
            refto_1_w = V0
        elif ref_w == 2:
            refto_1_w = fc_1_2_w.negative()
        elif ref_w == 3:
            refto_1_w = fc_1_3_w.negative()
        elif ref_w == 4:
            refto_1_w = fc_1_4_w.negative()
        else:
            logger.error('wrong reference point')

        # ------------ DISTANCES ON AXIS_H
        fc_1_2_h = DraftVecUtils.scale(axis_h, tot_h)
        fc_2_1_h = fc_1_2_h.negative()
        if ref_h == 1: 
            refto_2_h = fc_1_2_h
        elif ref_h == 2:
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
        d1_w1_h2_pos = pos + refto_1_d + refto_1_w + refto_2_h
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
                           # 1 TOL didn't fit
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
                           # 1 TOL didn't fit
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
            # a freeCAD object is created
            fco = doc.addObject("Part::Feature", name )
            fco.Shape = self.shp
            self.fco = fco

    def color (self, color = (1,1,1)):
        if self.wfco == 1:
            self.fco.ViewObject.ShapeColor = color
        else:
            logger.debug("Object with no fco")

    # exports the shape to STL format
    def export_stl (self, name = ""):
        if not name:
            name = self.name
        stlPath = filepath + stl_dir
        stlFileName = stlPath + name + ".stl"
        # exportStl not working well with FreeCAD 0.17
        #self.fco.Shape.exportStl(stlFileName)
        mesh_shp = MeshPart.meshFromShape(self.fco.Shape,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp.write(stlFileName)
        del mesh_shp


#doc = FreeCAD.newDocument()
#h_estp = SimpleEndstopHolder(
#                 d_endstop = kcomp.ENDSTOP_D3V,
#                 rail_l = 25,
#                 base_h = 3.,
#                 h = 0,
#                 holder_out = 0, 
#                 #csunk = 1,
#                 mbolt_d = 4.,
#                 endstop_nut_dist = 2.,
#                 min_d = 1,
#                 fc_axis_d = VX,
#                 fc_axis_w = V0,
#                 fc_axis_h = VZ,
#                 ref_d = 2,
#                 ref_w = 1,
#                 ref_h = 1,
#                 pos = V0,
#                 wfco = 1,
#                 name = 'simple_endstop_holder')


# ----------- thin linear bearing housing with one rail to be attached

class ThinLinBearHouse1rail (object):

    """
    Makes a housing for a linear bearing, but it is very thin
    and intended to be attached to one rail, instead of 2
    it has to parts, the lower and the upper part
    ::

         ________                           ______________
        | ::...::|                         | ::........:: |
        | ::   ::|    Upper part           |.::        ::.|
        |-::( )::|------                   |.::        ::.|  --> fc_slide_axis
        | ::...::|    Lower part           | ::........:: | 
        |_::___::|                   ______| ::        :: |______
        |_::|_|::|                  |__:_:___::________::__:_:__|
                                                   :
         _________                                 :
        |____O____|                                v
        |  0: :0  |                            fc_bot_axis
        | :     : |
        | :     : |
        | :     : |
        | :.....: |
        |__0:_:0__|
        |____O____|
        
         ________                           ______________
        | ::...::|                         | ::........:: |
        | ::   ::|    Upper part           |.::        ::.|
        |-::( )::|------                   |.::   *axis_center = 1
        | ::...::|    Lower part           | ::........:: | 
        |_::___::|                   ______| ::        :: |______
        |_::|_|::|                  |__:_:___::___*____::__:_:__|
             |                                   axis_center = 0
             |
             V
           always centered in this axis

                                            ______________
        1: axis_center=1                   | ::........:: |
           mid_center =1                   |.::        ::.|
        2: axis_center=0                4  |.::   1 --> fc_slide_axis
           mid_center =1                   | ::........:: | 
        3: axis_center=0             ______| ::        :: |______
           mid_center =0             |_:3:___::___2____::__:_:__|
        4: axis_center=1
           mid_center =0


    Parameters
    ----------
    d_lbear : dictionary
        Dictionary with the dimensions of the linear bearing
    fc_slide_axis : FreeCAD.Vector
        Direction of the slide
    fc_bot_axis : FreeCAD.Vector
        Direction of the bottom
    axis_center : int
        See picture, indicates the reference point
    mid_center : int
        See picture, indicates the reference point
    pos : FreeCAD.Vector
        Position of the reference point,

    Attributes
    ----------
    n1_slide_axis : FreeCAD.Vector
    n1_bot_axis : FreeCAD.Vector
    n1_perp : FreeCAD.Vector
    axis_h : float
    boltcen_axis_dist : float
    boltcen_perp_dist : float


    Dimensions:
        * tot_h, tot_w, tot_l
        * housing_l, base_h

    FreeCAD objects:
        * fco_top : Top part of the linear bearing housing
        * fco_bot : Bottom part of the linear bearing housing

    ::

           ________                           ______________
          | ::...::|                         | ::........:: |
          | ::   ::|                         |.::        ::.|
          |-::( )::|---:                     |.::        ::.|  --> n1_slide_axis
          | ::...::|   +axis_h               | ::........:: | 
          |_::___::|   :               ______| ::        :: |______
          |_::|_|::|...:              |__:_:___::________::__:_:__|
                                                     :
           _________                                 v
          |____O____|                              n1_bot_axis
          |  0: :0  |
          | :     : |
          | :     : |---+ boltcen_axis_dist ..            --> n1_perp
          | :     : |   :                    :
          | :.....: |   :                    + boltrailcen_dist
          |__0:_:0__|----                    :
          |____O____|------------------------:
             :   :
             :   :
             :...:
               +boltcen_perp_dist
         
                                             ....housing_l..
                                             :              :
           ________....                      :______________:
          | ::...::|   :                     | ::........:: |
          | ::   ::|   :                     |.::        ::.|
          |-::( )::|   :                     |.::        ::.|  --> n1_slide_axis
          | ::...::|   +tot_h                | ::........:: | 
          |_::___::|   :           ... ______| ::        :: |______
          |_::|_|::|...:    base_h ...|__:_:___::________::__:_:__|
          :        :                  :                           :
          :........:                  :...........................:
              +                                      +
             tot_w                                 tot_l       

    """

    MIN_SEP_WALL = 3. # min separation of a wall
    MIN2_SEP_WALL = 2. # min separation of a wall
    OUT_SEP_H = kparts.OUT_SEP_H
    MTOL = kparts.MTOL
    MLTOL = kparts.MLTOL 
    TOL_BEARING_L = kparts.TOL_BEARING_L
    # Radius to fillet the sides
    FILLT_R = kparts.FILLT_R

    def __init__(self, d_lbear,
                 fc_slide_axis = VX,
                 fc_bot_axis =VZN,
                 axis_center = 1,
                 mid_center  = 1,
                 pos = V0,
                 name = 'thinlinbearhouse1rail'
                ):

        # normalize, just in case
        n1_slide_axis = DraftVecUtils.scaleTo(fc_slide_axis,1)
        n1_bot_axis = DraftVecUtils.scaleTo(fc_bot_axis,1)
        n1_bot_axis_neg = DraftVecUtils.neg(n1_bot_axis)
        # vector perpendicular to the others
        n1_perp = n1_slide_axis.cross(n1_bot_axis)

        rod_d =  d_lbear['Di']
        self.rod_r = d_lbear['Di']/2.
        rod_r = self.rod_r
        self.bear_r = d_lbear['Di']
        if rod_d >= 12:
            BOLT_D = 4
        else:
            BOLT_D = 3  # M3 bolts

        doc = FreeCAD.ActiveDocument

        MIN_SEP_WALL = self.MIN_SEP_WALL
        MIN2_SEP_WALL = self.MIN2_SEP_WALL
        OUT_SEP_H = self.OUT_SEP_H
        # bolt dimensions:
        MTOL = self.MTOL
        MLTOL = self.MLTOL
        BOLT_HEAD_R = kcomp.D912_HEAD_D[BOLT_D] / 2.0
        BOLT_HEAD_L = kcomp.D912_HEAD_L[BOLT_D] + MTOL
        BOLT_HEAD_R_TOL = BOLT_HEAD_R + MTOL # More toler/2.0 
        BOLT_SHANK_R_TOL = BOLT_D / 2.0 + MTOL # more tolerance: MTOL/2.
        BOLT_NUT_R = kcomp.NUT_D934_D[BOLT_D] / 2.0
        BOLT_NUT_L = kcomp.NUT_D934_L[BOLT_D] + MTOL
        #  1.5 TOL because diameter values are minimum, so they may be larger
        BOLT_NUT_R_TOL = BOLT_NUT_R + 1.5*MTOL

        # bearing dimensions:
        bearing_l     = d_lbear['L'] 
        bearing_l_tol = bearing_l + self.TOL_BEARING_L
        bearing_d     = d_lbear['De']
        bearing_d_tol = bearing_d + 2.0 * self.MLTOL
        bearing_r     = bearing_d / 2.0
        bearing_r_tol = bearing_r + self.MLTOL

        #There are two basic pieces: the base and the housing for the linear
        # bearing
        # dimensions of the housing:
        # length on the direction of the sliding rod
        bolt2wall = fcfun.get_bolt_end_sep(BOLT_D, hasnut=1) 
        #housing_l = bearing_l_tol + 2 * (2*BOLT_HEAD_R_TOL + 2* MIN_SEP_WALL)
        housing_l = bearing_l_tol + 2 * (2* bolt2wall)
        print ("housing_l: %", housing_l)
        # width of the housing (very tight)
        if rod_d > 8 :
          housing_w = max ((bearing_d_tol + 2* MIN_SEP_WALL), 
                           (d_lbear['Di'] + 4* MIN2_SEP_WALL + 2*BOLT_D))
        else: # 8 is very tight
          housing_w = max ((bearing_d_tol + 2* MIN_SEP_WALL), 
                           (d_lbear['Di'] + 4* MIN_SEP_WALL + 2*BOLT_D))
        print ("housing_w: %", housing_w)

        # dimensions of the base:
        # length on the direction of the sliding rod
        base_l = housing_l +  4* MIN_SEP_WALL + 4 * BOLT_HEAD_R_TOL
        print ("base_l: %", base_l)
        # width of the base (very tight), the same as the housing
        base_w = housing_w
        print ("base_w: %", base_w)
        # height of the base (not tight). twice the minimum height
        base_h = 2 * OUT_SEP_H 
        print ("base_h: %", base_h)

        # height of the housing (not tight, can be large)
        housing_h = base_h +  2* BOLT_HEAD_L + bearing_d_tol
        print ("housing_h: %", housing_h)


        # distance on the slide_axis from midcenter=0 to midcenter 1.
        # the bolt to join the housing to the rail
        boltrailcen_dist = housing_l/2. + BOLT_HEAD_R_TOL + MIN_SEP_WALL
        # distance on the bot_axis from the rod to the bottom
        # the base and the housing are overlapped.
        # Not taking the tolerance
        #axis_h = bearing_d/2. + 2 * OUT_SEP_H + BOLT_HEAD_L
        axis_h = ( rod_r + kparts.ROD_SPACE_MIN + base_h
                             + 2 * BOLT_HEAD_L)

        #To make the boxes, we take the reference on midcenter=1 and 
        # axis_center = 0. Point 2 on the drawing

        if mid_center == 0:
            # get the vector to the center:
            fc_tomidcenter = DraftVecUtils.scale(n1_slide_axis,boltrailcen_dist)
        else:
            fc_tomidcenter = V0
        if axis_center == 1:
            fc_tobottom = DraftVecUtils.scale(n1_bot_axis,axis_h)
            fc_toaxis = V0
        else:
            fc_tobottom = V0
            fc_toaxis = DraftVecUtils.scale(n1_bot_axis,-axis_h)

        botcenter_pos = pos + fc_tomidcenter + fc_tobottom

        # point 1 on the drawing
        axiscenter_pos = pos + fc_tomidcenter + fc_toaxis

        shp_base = fcfun.shp_box_dir(box_w = base_w,
                                     box_d = base_l, #dir of n1_slide_axis
                                     box_h = base_h,
                                     fc_axis_h = n1_bot_axis_neg,
                                     fc_axis_d = n1_slide_axis,
                                     cw= 1, cd=1, ch=0,
                                     pos = botcenter_pos)

        # fillet the base:
        shp_base_fllt = fcfun.shp_filletchamfer_dir(shp_base,
                                                    fc_axis=fc_bot_axis,
                                                    radius=kparts.FILLT_R)


        shp_housing = fcfun.shp_box_dir(box_w = housing_w,
                                     box_d = housing_l, #dir of n1_slide_axis
                                     box_h = housing_h,
                                     fc_axis_h = n1_bot_axis_neg,
                                     fc_axis_d = n1_slide_axis,
                                     cw= 1, cd=1, ch=0,
                                     pos = botcenter_pos)
        #Part.show(shp_housing)

        shp_block = shp_base_fllt.fuse(shp_housing)

        # the rod hole
        shp_rod = fcfun.shp_cylcenxtr(r = rod_r + kparts.ROD_SPACE_MIN,
                                      h = base_l,
                                      normal = n1_slide_axis,
                                      ch = 1, xtr_top = 1, xtr_bot=1,
                                      pos = axiscenter_pos)
        # the linear bearing hole
        shp_lbear = fcfun.shp_cylcenxtr(r = bearing_r_tol,
                                        h = bearing_l_tol,
                                        normal = n1_slide_axis,
                                        ch = 1, xtr_top = 1, xtr_bot=1,
                                        pos = axiscenter_pos)
        shp_rodlbear = shp_rod.fuse(shp_lbear)
        shp_block_hole = shp_block.cut(shp_rodlbear)

        # bolts to attach to the support
        
        bolt1_atch_pos = (  botcenter_pos
                          + DraftVecUtils.scale(n1_slide_axis,boltrailcen_dist))
        bolt2_atch_pos = (  botcenter_pos
                         + DraftVecUtils.scale(n1_slide_axis,-boltrailcen_dist))

        print('shank tol' + str(BOLT_SHANK_R_TOL))
        shp_bolt1_atch = fcfun.shp_cylcenxtr(r=BOLT_SHANK_R_TOL,
                                             h = base_h,
                                             normal = n1_bot_axis_neg,
                                             ch = 0, xtr_top = 1, xtr_bot = 1,
                                             pos = bolt1_atch_pos)
        shp_bolt2_atch = fcfun.shp_cylcenxtr(r=BOLT_SHANK_R_TOL,
                                             h = base_h,
                                             normal = n1_bot_axis_neg,
                                             ch = 0, xtr_top = 1, xtr_bot = 1,
                                             pos = bolt2_atch_pos)
        bolt_holes = [shp_bolt2_atch]

        # 4 bolts to join the upper and lower parts
        # distance of the bolts to the center, on n1_slide_axis dir
        boltcen_axis_dist = housing_l/2. - bolt2wall
        # distance of the bolts to the center, on n1_perp dir
        boltcen_perp_dist = housing_w/2. - bolt2wall



        for vec_axis in [DraftVecUtils.scale(n1_slide_axis,boltcen_axis_dist),
                         DraftVecUtils.scale(n1_slide_axis,-boltcen_axis_dist)]:
            for vec_perp in [DraftVecUtils.scale(n1_perp,
                                                 boltcen_perp_dist),
                             DraftVecUtils.scale(n1_perp,
                                                 -boltcen_perp_dist)]:
                pos_i = botcenter_pos + vec_axis + vec_perp
                # the nut hole will be on the bottom side,
                
                shp_bolt = fcfun.shp_boltnut_dir_hole (
                                  r_shank = BOLT_SHANK_R_TOL,
                                  l_bolt  = housing_h,
                                  r_head  = BOLT_HEAD_R_TOL,
                                  l_head  = BOLT_HEAD_L,
                                  r_nut  = BOLT_NUT_R_TOL,
                                  # more space, because we want it well inside
                                  l_nut  = 1.5*BOLT_NUT_L,
                                  hex_head = 0,
                                  xtr_head=1,     xtr_nut=1,
                                  supp_head=1,    supp_nut=1,
                                  headstart=0,
                                  fc_normal = n1_bot_axis_neg,
                                  fc_verx1=V0,
                                  pos = pos_i)
                bolt_holes.append(shp_bolt)

        # ----------------- Attributes
        self.n1_slide_axis = n1_slide_axis
        self.n1_bot_axis = n1_bot_axis
        self.n1_perp = n1_perp
        self.axis_h = axis_h
        self.boltcen_axis_dist = boltcen_axis_dist
        self.boltcen_perp_dist = boltcen_perp_dist
        self.tot_h = housing_h
        self.tot_w = housing_w # == base_w
        self.tot_l = base_l
        self.housing_l  = housing_l
        self.base_h = base_h
        
        shp_bolt_holes = shp_bolt1_atch.multiFuse(bolt_holes)       
        shp_lbear_housing = shp_block_hole.cut(shp_bolt_holes)
        doc.recompute()
        # making 2 parts, intersection with 2 boxes:
        shp_box_top = fcfun.shp_box_dir(
                                     box_w = housing_w + 2,
                                     box_d = housing_l + 2, 
                                     box_h = housing_h /2. + 2,
                                     fc_axis_h = n1_bot_axis_neg,
                                     fc_axis_d = n1_slide_axis,
                                     cw= 1, cd=1, ch=0,
                                     pos = axiscenter_pos)
        shp_lbear_housing_top = shp_lbear_housing.common(shp_box_top)
        shp_lbear_housing_top = shp_lbear_housing_top.removeSplitter() 
        fco_lbear_top = doc.addObject("Part::Feature", name + '_'
                                      + str(rod_d) + '_top') 
        fco_lbear_top.Shape = shp_lbear_housing_top


        shp_box_bot = fcfun.shp_box_dir(
                                     box_w = base_w + 2,
                                     box_d = base_l + 2,
                                     # larger, just in case
                                     box_h = housing_h/2. + base_h + 2,
                                     fc_axis_h = n1_bot_axis,
                                     fc_axis_d = n1_slide_axis,
                                     cw= 1, cd=1, ch=0,
                                     pos = axiscenter_pos)
        shp_lbear_housing_bot = shp_lbear_housing.common(shp_box_bot)
        shp_lbear_housing_bot = shp_lbear_housing_bot.removeSplitter()
        fco_lbear_bot = doc.addObject("Part::Feature", name + '_'
                                      + str(rod_d) + '_bot') 
        fco_lbear_bot.Shape = shp_lbear_housing_bot

        self.fco_top = fco_lbear_top
        self.fco_bot = fco_lbear_bot

    def color (self, color = (1,1,1)):
        self.fco_top.ViewObject.ShapeColor = color
        self.fco_bot.ViewObject.ShapeColor = color



#doc = FreeCAD.newDocument()
#ThinLinBearHouse1rail (kcomp.LMUU[8])
#ThinLinBearHouse (kcomp.LMEUU[10], mid_center=0)

# ----------- thin linear bearing housing with one rail to be attached

class ThinLinBearHouse (object):

    """
    Makes a housing for a linear bearing, but it is very thin
    and intended to be attached to 2 rail
    it has to parts, the lower and the upper part
    ::

         ________                           ______________
        | ::...::|                         | ::........:: |
        | ::   ::|    Upper part           |.::        ::.|
        |-::( )::|------                   |.::        ::.|  --> fc_slide_axis
        | ::...::|    Lower part           | ::........:: | 
        |_::___::|                         |_::________::_|
                                                   :
                                                   :
         _________                                 v
        |  0: :0  |                            fc_bot_axis
        | :     : |
        | :     : |
        | :     : |--------> fc_perp_axis
        | :     : |
        | :.....: |
        |__0:_:0__|
 
        
         ________                           ______________
        | ::...::|                         | ::........:: |
        | ::   ::|    Upper part           |.::        ::.|
        |-::( )::|------> fc_perp_axis     |.::   *axis_center = 1
        | ::...::|    Lower part           | ::........:: | 
        |_::___::|                         |_::___*____::_|
          |  |                                   axis_center = 0
          |  |
          V  V
          centered in any of these axes

                                            ______________
        1: axis_center=1                   | ::........:: |
           mid_center =1                   |.::        ::.|
        2: axis_center=0                   |.:4   1 --> fc_slide_axis
           mid_center =1                   | ::........:: | 
        3: axis_center=0                   | ::        :: |
           mid_center =0                   |_:3___2____::_|
        4: axis_center=1

        And 8 more possibilities:
        5: bolt_center = 1
        6: bolt_center = 0

         _________              
        |  5:6:   |             
        | :     : |
        | :     : |
        | :     : |--------> fc_perp_axis
        | :     : |
        | :.....: |
        |__0:_:0__|
          mid_center =0


    Parameters
    ----------
    d_lbear : dictionary
        Dictionary with the dimensions of the linear bearing
    fc_slide_axis : FreeCAD.Vector
        Direction of the slide
    fc_bot_axis : FreeCAD.Vector
        Direction of the bottom
    fc_perp_axis : FreeCAD.Vector
        Direction of the other
        perpendicular direction. Not useful unless bolt_center == 1
        if = V0 it doesn't matter
    axis_h : int
        Distance from the bottom to the rod axis  

            * 0: take the minimum distance
            * X: (any value) take that value, if it is smaller than the 
              minimum it will raise an error and would not take that 
              value

    bolts_side : int
        See picture, indicates the side where is bolt
    axis_center : int
        See picture, indicates the reference point
    mid_center : int
        See picture, indicates the reference point
    bolt_center : int
        See picture, indicates the reference point, if it is
        on the bolt or on the axis
    pos : FreeCAD.Vector
        Position of the reference point,

    Attributes
    ----------    
    n1_slide_axis : FreeCAD.Vector
    n1_bot_axis : FreeCAD.Vector
    n1_perp : FreeCAD.Vector
    axis_h : float
    boltcen_axis_dist : float
    boltcen_perp_dist : float


    Dimensions:    
        * H, W, L

    FreeCAD objects:
        * fco_top : Top part of the linear bearing housing
        * fco_bot : Bottom part of the linear bearing housing


    ::

           ________                           ______________
          | ::...::|                         | ::........:: |
          | ::   ::|                         |.::        ::.|
          |-::( )::|---:                     |.::        ::.|  --> n1_slide_axis
          | ::...::|   +axis_h               | ::........:: | 
          |_::___::|   :                     | ::        :: |
          |_::___::|...:                     |_::________::_|
                                                     :
                                                     v
           _________                               n1_bot_axis
          |  0: :0  |                  
          | :     : |
          | :     : |........ --> n1_perp
          | :     : |   :
          | :.....: |   + boltcen_axis_dist
          |__0:_:0__|---:
             :   :
             :   :
             :...:
               +boltcen_perp_dist
         
                                             ...... L .......
                                             :              :
           ________....                      :______________:
          | ::...::|   :                     | ::........:: |
          | ::   ::|   :                     |.::        ::.|
          |-::( )::|   :                     |.::        ::.|  --> n1_slide_axis
          | ::...::|   + H                   | ::........:: | 
          |_::___::|...:                     |_::________::_|
          :        :
          :........:
              + 
              W

         bolts_side = 0            bolts_side = 1
          _________                
         |  0: :0  |                ___________ 
         | :     : |               | 0:     :0 |
         | :     : |               |  :     :  |
         | :     : |               |  :     :  |
         | :.....: |               |_0:_____:0_|
         |__0:_:0__|
 

    """

    MIN_SEP_WALL = 3. # min separation of a wall
    MIN2_SEP_WALL = 2. # min separation of a wall
    OUT_SEP_H = kparts.OUT_SEP_H # minimum separation of the linear bearing
    MTOL = kparts.MTOL
    MLTOL = kparts.MLTOL
    TOL_BEARING_L = kparts.TOL_BEARING_L
    # Radius to fillet the sides
    FILLT_R = kparts.FILLT_R

    def __init__(self, d_lbear,
                 fc_slide_axis = VX,
                 fc_bot_axis =VZN,
                 fc_perp_axis = V0,
                 axis_h = 0,
                 bolts_side = 1,
                 axis_center = 1,
                 mid_center  = 1,
                 bolt_center  = 0,
                 pos = V0,
                 name = 'thinlinbearhouse'
                ):

        self.name = name
        self.base_place = (0,0,0)
        # normalize, just in case
        n1_slide_axis = DraftVecUtils.scaleTo(fc_slide_axis,1)
        n1_bot_axis = DraftVecUtils.scaleTo(fc_bot_axis,1)
        n1_bot_axis_neg = DraftVecUtils.neg(n1_bot_axis)
        # vector perpendicular to the others
        v_cross = n1_slide_axis.cross(n1_bot_axis)
        if fc_perp_axis == V0:
            n1_perp = v_cross
        else:
            n1_perp =  DraftVecUtils.scaleTo(fc_perp_axis,1)
            if not fcfun.fc_isparal (v_cross,n1_perp):
                logger.debug("fc_perp_axis not perpendicular")
                n1_perp = v_cross

        self.rod_r = d_lbear['Di']/2.
        rod_r = self.rod_r
        self.bear_r = d_lbear['Di']
        if rod_r >= 6:
            BOLT_D = 4
        else:
            BOLT_D = 3  # M3 bolts

        doc = FreeCAD.ActiveDocument

        MIN_SEP_WALL = self.MIN_SEP_WALL
        MIN2_SEP_WALL = self.MIN2_SEP_WALL
        OUT_SEP_H = self.OUT_SEP_H
        # bolt dimensions:
        MTOL = self.MTOL
        MLTOL = self.MLTOL
        BOLT_HEAD_R = kcomp.D912_HEAD_D[BOLT_D] / 2.0
        BOLT_HEAD_L = kcomp.D912_HEAD_L[BOLT_D] + MTOL
        BOLT_HEAD_R_TOL = BOLT_HEAD_R + MTOL/2.0 
        BOLT_SHANK_R_TOL = BOLT_D / 2.0 + MTOL/2.0

        # bearing dimensions:
        bearing_l     = d_lbear['L'] 
        bearing_l_tol = bearing_l + self.TOL_BEARING_L
        bearing_d     = d_lbear['De']
        bearing_d_tol = bearing_d + 2.0 * self.MLTOL
        bearing_r     = bearing_d / 2.0
        bearing_r_tol = bearing_r + self.MLTOL

        # dimensions of the housing:
        # length on the direction of the sliding rod
        bolt2wall = fcfun.get_bolt_end_sep(BOLT_D, hasnut=0) 
        #housing_l = bearing_l_tol + 2 * (2*BOLT_HEAD_R_TOL + 2* MIN_SEP_WALL)
        if bolts_side == 1:
            # bolts on the side of the linear bearing
            # bolt2axis: distance from the center (axis) to the bolt center
            bolt2axis = fcfun.get_bolt_bearing_sep (BOLT_D, hasnut=0,
                                                    lbearing_r = bearing_r) 
            # it will be shorter (on L), and wider (on W)
            housing_l = bearing_l + 2 * MIN_SEP_WALL
            housing_w = 2 * (bolt2wall + bolt2axis)
        else:
            # bolts after the linear bearing
            # it will be longer (on L), and shorter (on W)
            bolt2axis = fcfun.get_bolt_bearing_sep (BOLT_D, hasnut=0,
                                     lbearing_r = rod_r ) 
                                    #lbearing_r = rod_r + kparts.ROD_SPACE_MIN) 
            housing_l = bearing_l + 4*bolt2wall #bolt_r is included in bolt2wall
            housing_w = max ((bearing_d + 2* MIN_SEP_WALL), 
                              2 * (bolt2wall + bolt2axis))

        print("housing_l: %", housing_l)
        print("housing_w: %", housing_w)

        # bolt distance
        # distance of the bolts to the center, on n1_slide_axis dir
        boltcen_axis_dist = housing_l/2. - bolt2wall
        # distance of the bolts to the center, on n1_perp dir
        boltcen_perp_dist = bolt2axis

        # minimum height of the housing 
        housing_min_h = bearing_d + 2 * OUT_SEP_H
        axis_min_h = housing_min_h / 2.
        print("min housing_h: %", housing_min_h)
        if axis_h == 0:
            # minimum values
            housing_h = housing_min_h
            axis_h = axis_min_h
        elif axis_h >= axis_min_h:
            # the lower part will have longer height: axis_h
            # the upper part will be the minimum: axis_min_h
            housing_h = axis_h + axis_min_h
            axis_h = axis_h
        else: # the argument has an axis_h lower than the minimum possible
            logger.debug("axis_h %s cannot be smaller than %s",
                         str(axis_h), str(axis_min_h))
            housing_h = housing_min_h
            axis_h = axis_min_h

        # Attributes
        self.L = housing_l
        self.W = housing_w
        self.H = housing_h
        self.axis_h = axis_h
        self.boltcen_axis_dist = boltcen_axis_dist
        self.boltcen_perp_dist = boltcen_perp_dist
        self.n1_slide_axis = n1_slide_axis
        self.n1_bot_axis = n1_bot_axis
        self.n1_perp = n1_perp

        #To make the boxes, we take the reference on midcenter=1 and 
        # axis_center = 0. Point 2 on the drawing

        if mid_center == 0:
            # get the vector to the center:
            fc_tomidcenter = DraftVecUtils.scale(n1_slide_axis,
                                                 boltcen_axis_dist)
        else:
            fc_tomidcenter = V0

        if axis_center == 1:
            fc_tobottom = DraftVecUtils.scale(n1_bot_axis,axis_h)
            fc_toaxis = V0
        else:
            fc_tobottom = V0
            fc_toaxis = DraftVecUtils.scale(n1_bot_axis,-axis_h)

        if bolt_center == 1:
            fc_toaxis_perp = DraftVecUtils.scale(n1_perp, boltcen_perp_dist)
        else:
            fc_toaxis_perp = V0

        botcenter_pos = pos + fc_tomidcenter + fc_tobottom + fc_toaxis_perp

        # point 1 on the drawing
        axiscenter_pos = pos + fc_tomidcenter + fc_toaxis + fc_toaxis_perp
        # center on the top
        topcenter_pos = botcenter_pos + DraftVecUtils.scale(n1_bot_axis_neg,
                                                            housing_h)

        shp_housing = fcfun.shp_box_dir(box_w = housing_w,
                                     box_d = housing_l, #dir of n1_slide_axis
                                     box_h = housing_h,
                                     fc_axis_h = n1_bot_axis_neg,
                                     fc_axis_d = n1_slide_axis,
                                     cw= 1, cd=1, ch=0,
                                     pos = botcenter_pos)
        # fillet, small
        shp_block = fcfun.shp_filletchamfer_dir(shp_housing,
                                                fc_axis=fc_bot_axis,
                                                radius=2)

        # the rod hole
        shp_rod = fcfun.shp_cylcenxtr(r = rod_r + kparts.ROD_SPACE_MIN,
                                      h = housing_l,
                                      normal = n1_slide_axis,
                                      ch = 1, xtr_top = 1, xtr_bot=1,
                                      pos = axiscenter_pos)
        # the linear bearing hole
        shp_lbear = fcfun.shp_cylcenxtr(r = bearing_r_tol,
                                        h = bearing_l_tol,
                                        normal = n1_slide_axis,
                                        ch = 1, xtr_top = 1, xtr_bot=1,
                                        pos = axiscenter_pos)
        shp_rodlbear = shp_rod.fuse(shp_lbear)

        # 4 bolts 
        
        bolt_holes = []

        for vec_axis in [DraftVecUtils.scale(n1_slide_axis,boltcen_axis_dist),
                         DraftVecUtils.scale(n1_slide_axis,-boltcen_axis_dist)]:
            for vec_perp in [DraftVecUtils.scale(n1_perp,
                                                 boltcen_perp_dist),
                             DraftVecUtils.scale(n1_perp,
                                                 -boltcen_perp_dist)]:
                pos_i = topcenter_pos + vec_axis + vec_perp
                # the nut hole will be on the bottom side,
                
                shp_bolt = fcfun.shp_bolt_dir (
                                  r_shank = BOLT_SHANK_R_TOL,
                                  l_bolt  = housing_h,
                                  r_head  = BOLT_HEAD_R_TOL,
                                  l_head  = BOLT_HEAD_L,
                                  hex_head = 0,
                                  xtr_head=1,     xtr_shank=1,
                                  support=1,
                                  fc_normal = n1_bot_axis,
                                  fc_verx1=V0,
                                  pos = pos_i)
                bolt_holes.append(shp_bolt)

        shp_holes = shp_rodlbear.multiFuse(bolt_holes)       
        shp_lbear_housing = shp_block.cut(shp_holes)
        doc.recompute()
        # making 2 parts, intersection with 2 boxes:
        shp_box_top = fcfun.shp_box_dir(
                                     box_w = housing_w + 2,
                                     box_d = housing_l + 2, 
                                     box_h = housing_h - axis_h + 1,
                                     fc_axis_h = n1_bot_axis_neg,
                                     fc_axis_d = n1_slide_axis,
                                     cw= 1, cd=1, ch=0,
                                     pos = axiscenter_pos)
        shp_lbear_housing_top = shp_lbear_housing.common(shp_box_top)
        shp_lbear_housing_top = shp_lbear_housing_top.removeSplitter() 
        fco_lbear_top = doc.addObject("Part::Feature", name + '_top') 
        fco_lbear_top.Shape = shp_lbear_housing_top


        shp_box_bot = fcfun.shp_box_dir(
                                     box_w = housing_w + 2,
                                     box_d = housing_l + 2,
                                     # larger, just in case
                                     box_h = axis_h + 1,
                                     fc_axis_h = n1_bot_axis,
                                     fc_axis_d = n1_slide_axis,
                                     cw= 1, cd=1, ch=0,
                                     pos = axiscenter_pos)
        shp_lbear_housing_bot = shp_lbear_housing.common(shp_box_bot)
        shp_lbear_housing_bot = shp_lbear_housing_bot.removeSplitter()
        fco_lbear_bot = doc.addObject("Part::Feature", name + '_bot') 
        fco_lbear_bot.Shape = shp_lbear_housing_bot

        self.fco_top = fco_lbear_top
        self.fco_bot = fco_lbear_bot

    def BasePlace (self, position = (0,0,0)):
        self.base_place = position
        vpos = FreeCAD.Vector(position)
        self.fco_top.Placement.Base = vpos
        self.fco_bot.Placement.Base = vpos

    def color (self, color = (1,1,1)):
        self.fco_top.ViewObject.ShapeColor = color
        self.fco_bot.ViewObject.ShapeColor = color

    def export_stl (self, name = ""):
        #filepath = os.getcwd()
        if not name:
            name = self.name
        stlPath = filepath + stl_dir
        stlFileName_top = stlPath + name + "_top" + ".stl"
        stlFileName_bot = stlPath + name + "_bot" + ".stl"

        # exportStl not working well with FreeCAD 0.17
        #self.fco_top.Shape.exportStl(stlFileName_top)
        #self.fco_bot.Shape.exportStl(stlFileName_bot)
        # this would work:
        #Mesh.export([self.fco_top], stlFileName_top)
        #Mesh.export([self.fco_bot], stlFileName_bot)
        mesh_shp_top = MeshPart.meshFromShape(self.fco_top.Shape,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp_top.write(stlFileName_top)
        del mesh_shp_top

        mesh_shp_bot = MeshPart.meshFromShape(self.fco_bot.Shape,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp_bot.write(stlFileName_bot)
        del mesh_shp_bot





#AAAAAAA
#doc = FreeCAD.newDocument()
#ThinLinBearHouse (kcomp.LMEUU[10])
#ThinLinBearHouse (kcomp.LMEUU[10], mid_center=1)
#ThinLinBearHouse (kcomp.LMEUU[10], bolts_side=0, mid_center=1)
#ThinLinBearHouse (kcomp.LMEUU[10], axis_h = 10, bolts_side=0, mid_center=1)
#ThinLinBearHouse (kcomp.LMEUU[10], axis_h = 15, bolts_side=0, mid_center=1)

#ThinLinBearHouse (kcomp.LMEUU[12], axis_h = 0, bolts_side=0, mid_center=1)
#ThinLinBearHouse (kcomp.LMELUU[12], axis_h = 0, bolts_side=0, mid_center=1)
#ThinLinBearHouse (kcomp.LMELUU[12], axis_h = 0, bolts_side=1, mid_center=1)
 
#ThinLinBearHouse (kcomp.LMEUU[12],
#                  fc_slide_axis = VY,
#                  fc_bot_axis = VZN,
#                  fc_perp_axis = VX,
#                  axis_h = 0, bolts_side=0, mid_center=1, bolt_center = 1)
#ThinLinBearHouse (kcomp.LMELUU[12],
#                  fc_slide_axis = VY,
#                  fc_bot_axis = VZN,
#                  fc_perp_axis = VXN,
#                  axis_h = 0, bolts_side=0, mid_center=1, bolt_center = 1)
#ThinLinBearHouse (kcomp.LMELUU[12],
#                  fc_slide_axis = VX,
#                  fc_bot_axis = VZN,
#                  fc_perp_axis = VYN,
#                  axis_h = 0, bolts_side=1,
#                  axis_center=0, mid_center=0, bolt_center = 1)

 

# ----------- Linear bearing housing 

class LinBearHouse (object):

    """
    Makes a housing for a linear bearing takes the dimensions
    from a dictionary, like the one defined in kcomp.py
    it has to parts, the lower and the upper part
    ::

          _____________                           ______________
         |::   ___   ::|                         |.::........::.|
         |:: /     \ ::|    Upper part           | ::        :: |
         |---|-----|---|------                   | ::        :: |
         |::  \___/  ::|    Lower part           |.::........::.| 
         |::_________::|                         |_::________::_|      
 
          _____________ 
         | 0 :     : 0 |
         |   :     :   |
         |   :     :   |
         |   :     :   |
         |   :     :   |
         |_0_:_____:_0_|
         



                                            ________________
        1: axis_center=1                   | : :........: : |
           mid_center =1                   |.: :        : :.|
        2: axis_center=0                   |.:4:   1 --------->: fc_slide_axis
           mid_center =1                   | : :........:.: | 
        3: axis_center=0                   | : :        : : |
           mid_center =0                   |_:3:___2____:_:_|
        4: axis_center=1
           mid_center =0

    """


    MTOL = kparts.MTOL
    MLTOL = kparts.MLTOL
    TOL_BEARING_L = kparts.TOL_BEARING_L
    # Radius to fillet the sides
    FILLT_R = kparts.FILLT_R


    def __init__(self, d_lbearhousing,
                 fc_slide_axis = VX,
                 fc_bot_axis =VZN,
                 axis_center = 1,
                 mid_center  = 1,
                 pos = V0,
                 name = 'linbearhouse'
                ):

        housing_l = d_lbearhousing['L']
        housing_w = d_lbearhousing['W']
        housing_h = d_lbearhousing['H']
        self.L = housing_l
        self.W = housing_w
        self.H = housing_h
        self.axis_h =  d_lbearhousing['axis_h']
        self.bolt_sep_l =  d_lbearhousing['bolt_sep_l']
        self.bolt_sep_w =  d_lbearhousing['bolt_sep_w']
        self.bolt_d =  d_lbearhousing['bolt_d']
        axis_h = self.axis_h
        self.name = name


        # normalize, just in case they are not
        n1_slide_axis = DraftVecUtils.scaleTo(fc_slide_axis,1)
        n1_bot_axis = DraftVecUtils.scaleTo(fc_bot_axis,1)
        n1_bot_axis_neg = DraftVecUtils.neg(n1_bot_axis)
        # vector perpendicular to the others
        n1_perp = n1_slide_axis.cross(n1_bot_axis)

        # get the linear bearing dictionary
        d_lbear = d_lbearhousing['lbear']
        self.rod_r = d_lbear['Di']/2.
        rod_r = self.rod_r
        self.bear_r = d_lbear['Di']
        bolt_d = d_lbearhousing['bolt_d']

        doc = FreeCAD.ActiveDocument
        # bolt dimensions:
        MTOL = self.MTOL
        MLTOL = self.MLTOL
        BOLT_HEAD_R = kcomp.D912_HEAD_D[bolt_d] / 2.0
        BOLT_HEAD_L = kcomp.D912_HEAD_L[bolt_d] + MTOL
        BOLT_HEAD_R_TOL = BOLT_HEAD_R + MTOL/2.0 
        BOLT_SHANK_R_TOL = bolt_d / 2.0 + MTOL/2.0

        # bearing dimensions:
        bearing_l     = d_lbear['L']
        bearing_l_tol = bearing_l + self.TOL_BEARING_L
        bearing_d     = d_lbear['De']
        bearing_d_tol = bearing_d + 2.0 * self.MLTOL
        bearing_r     = bearing_d / 2.0
        bearing_r_tol = bearing_r + self.MLTOL

        cenbolt_dist_l = d_lbearhousing['bolt_sep_l']/2.
        cenbolt_dist_w = d_lbearhousing['bolt_sep_w']/2.

        #To make the boxes, we take the reference on midcenter=1 and 
        # axis_center = 0. Point 2 on the drawing

        if mid_center == 0:
            # get the vector to the center:
            fc_tomidcenter = DraftVecUtils.scale(n1_slide_axis,cenbolt_dist_l)
        else:
            fc_tomidcenter = V0
        if axis_center == 1:
            fc_tobottom = DraftVecUtils.scale(n1_bot_axis,axis_h)
            fc_toaxis = V0
        else:
            fc_tobottom = V0
            fc_toaxis = DraftVecUtils.scale(n1_bot_axis,-axis_h)

        # point 2 on the drawing
        botcenter_pos = pos + fc_tomidcenter + fc_tobottom

        # point 1 on the drawing
        axiscenter_pos = pos + fc_tomidcenter + fc_toaxis

        # center on top
        topcenter_pos = botcenter_pos + DraftVecUtils.scale(n1_bot_axis_neg,
                                                            housing_h)

        shp_housing = fcfun.shp_box_dir(box_w = housing_w,
                                     box_d = housing_l, #dir of n1_slide_axis
                                     box_h = housing_h,
                                     fc_axis_h = n1_bot_axis_neg,
                                     fc_axis_d = n1_slide_axis,
                                     cw= 1, cd=1, ch=0,
                                     pos = botcenter_pos)

        # fillet the base:
        shp_housing_fllt = fcfun.shp_filletchamfer_dir(shp_housing,
                                                    fc_axis=fc_bot_axis,
                                                    radius=2)

        # the rod hole
        shp_rod = fcfun.shp_cylcenxtr(r = rod_r + kparts.ROD_SPACE_MIN,
                                      h = housing_l,
                                      normal = n1_slide_axis,
                                      ch = 1, xtr_top = 1, xtr_bot=1,
                                      pos = axiscenter_pos)
        # the linear bearing hole
        shp_lbear = fcfun.shp_cylcenxtr(r = bearing_r_tol,
                                        h = bearing_l_tol,
                                        normal = n1_slide_axis,
                                        ch = 1, xtr_top = 1, xtr_bot=1,
                                        pos = axiscenter_pos)
        shp_rodlbear = shp_rod.fuse(shp_lbear)

        # 4 bolts to join the upper and lower parts
        # distance of the bolts to the center, on n1_slide_axis dir

        bolt_holes = []

        for vec_axis in [DraftVecUtils.scale(n1_slide_axis,cenbolt_dist_l),
                         DraftVecUtils.scale(n1_slide_axis,-cenbolt_dist_l)]:
            for vec_perp in [DraftVecUtils.scale(n1_perp,
                                                 cenbolt_dist_w),
                             DraftVecUtils.scale(n1_perp,
                                                 -cenbolt_dist_w)]:
                pos_i = topcenter_pos + vec_axis + vec_perp
                # the nut hole will be on the bottom side,
                
                shp_bolt = fcfun.shp_bolt_dir (
                                  r_shank = BOLT_SHANK_R_TOL,
                                  l_bolt  = housing_h,
                                  r_head  = BOLT_HEAD_R_TOL,
                                  l_head  = BOLT_HEAD_L,
                                  hex_head = 0,
                                  xtr_head=1,     xtr_shank=1,
                                  support=1,
                                  fc_normal = n1_bot_axis,
                                  fc_verx1=V0,
                                  pos = pos_i)
                bolt_holes.append(shp_bolt)

        shp_holes = shp_rodlbear.multiFuse(bolt_holes)       
        shp_lbear_housing = shp_housing_fllt.cut(shp_holes)
        #Part.show(shp_lbear_housing)
        doc.recompute()
        # making 2 parts, intersection with 2 boxes:
        shp_box_top = fcfun.shp_box_dir(
                                     box_w = housing_w + 2,
                                     box_d = housing_l + 2, 
                                     box_h = housing_h - axis_h + 2,
                                     fc_axis_h = n1_bot_axis_neg,
                                     fc_axis_d = n1_slide_axis,
                                     cw= 1, cd=1, ch=0,
                                     pos = axiscenter_pos)
        shp_lbear_housing_top = shp_lbear_housing.common(shp_box_top)
        shp_lbear_housing_top = shp_lbear_housing_top.removeSplitter() 
        fco_lbear_top = doc.addObject("Part::Feature", name + '_top') 
        fco_lbear_top.Shape = shp_lbear_housing_top

        shp_box_bot = fcfun.shp_box_dir(
                                     box_w = housing_w + 2,
                                     box_d = housing_l + 2,
                                     # larger, just in case
                                     box_h = axis_h + 2,
                                     fc_axis_h = n1_bot_axis,
                                     fc_axis_d = n1_slide_axis,
                                     cw= 1, cd=1, ch=0,
                                     pos = axiscenter_pos)
        shp_lbear_housing_bot = shp_lbear_housing.common(shp_box_bot)
        shp_lbear_housing_bot = shp_lbear_housing_bot.removeSplitter()
        fco_lbear_bot = doc.addObject("Part::Feature", name + '_bot') 
        fco_lbear_bot.Shape = shp_lbear_housing_bot

        self.fco_top = fco_lbear_top
        self.fco_bot = fco_lbear_bot
        doc.recompute()

    def color (self, color = (1,1,1)):
        self.fco_top.ViewObject.ShapeColor = color
        self.fco_bot.ViewObject.ShapeColor = color

    def export_stl (self, name = ""):
        #filepath = os.getcwd()
        if not name:
            name = self.name
        #stlPath = filepath + "/freecad/stl/"
        stlPath = filepath + stl_dir
        stlFileName_top = stlPath + name + "_top" + ".stl"
        stlFileName_bot = stlPath + name + "_bot" + ".stl"

        # exportStl not working well with FreeCAD 0.17
        #self.fco_top.Shape.exportStl(stlFileName_top)
        # this would be valid
        #Mesh.export([self.fco_top], stlFileName_top)
        mesh_shp_top = MeshPart.meshFromShape(self.fco_top.Shape,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp_top.write(stlFileName_top)
        del mesh_shp_top

        mesh_shp_bot = MeshPart.meshFromShape(self.fco_bot.Shape,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp_bot.write(stlFileName_bot)
        del mesh_shp_bot


#doc = FreeCAD.newDocument()
#lin12 = LinBearHouse (kcomp.SCUU[12])
#LinBearHouse (kcomp.SCUU_Pr[10])


# ----------- thin linear bearing housing with asymmetrical distance
# between the bolts

class ThinLinBearHouseAsim (object):

    """
    There are
    
        +-------------+---------------------------+-----------------------+
        |3 axis:      | 3 planes (normal to axis) |  3 distances to plane |
        +=============+===========================+=======================+
        | fc_fro_ax   |   fro: front              |   D: dep: depth       |
        +-------------+---------------------------+-----------------------+
        | fc_bot_ax   |   hor: horizontal)        |   H: hei: height      |
        +-------------+---------------------------+-----------------------+
        | fc_sid_ax   |   lat: lateral (medial)   |   W: wid: width       |
        +-------------+---------------------------+-----------------------+

    The planes are on the center of the slidding rod (height and width),
    and on the middle of the piece (width)

    The 3 axis are perpendicular, but the cross product of 2 vectors may
    result on the other vector or its negative.

    fc_fro_ax points to the front of the figure, but it is symmetrical
    so it can point to the back
    fc_bot_ax points to the bottom of the figure (not symmetrical)
    fc_sid_ax points to the side of the figure. Not symmetrical if
    bolt2cen_wid_n or bolt2cen_wid_p are not zero

    Makes a housing for a linear bearing, but it is very thin
    and intended to be attached to 2 rail
    it has to parts, the lower and the upper part
    ::

         ________                           ______________
        | ::...::|                         | ::........:: |
        | ::   ::|    Upper part           |.::        ::.|
        |-::( )::|------ Horizontal plane  |.::        ::.|  --> fc_fro_ax
        | ::...::|    Lower part           | ::........:: | 
        |_::___::|                         |_::________::_|
                                                   :
                                                   :
         _________                                 v
        |  0: :0  |                            fc_bot_axis
        | :     : |
        | :     : |
        | :     : |--------> fc_sid_ax
        | :     : |
        | :.....: |
        |__0:_:0__|
         ________                           ______________
        | ::...::|                         | ::........:: |
        | ::   ::|    Upper part           |.::        ::.|
        |-::( )::|------> fc_sid_ax        |.::   *refcen_hei = 1
        | ::...::|    Lower part           | ::........:: | 
        |_::___::|                         |_::___*____::_|
          |  |                                   refcen_hei = 0
          |  |
          V  V
          centered in any of these axes
        refcen_hei: reference centered on the height
                  =1: the horizontal plane (height) is on the axis of the rod
                  =0: the horizontal plane is at the bottom 
        refcen_dep: reference centered on the depth
                  =1: the frontal plane (depth) is on the middle of the piece
                  =0: the frontal plane is at the bolts
        refcen_wid=1: reference centered on the width
                      the lateral plane (width) is on the medial axis, dividing
                      the piece on the right and left
                  =0: the lateral plane is at the bolts

                                            ______________
        1: refcen_hei=1                    | ::........:: |
           fro_center =1                   |.::        ::.|
        2: refcen_hei=0                    |.:4   1 --> fc_fro_ax
           fro_center =1                   | ::........:: | 
        3: refcen_hei=0                    | ::        :: |
           fro_center =0                   |_:3___2____::_|
        4: refcen_hei=1

        And 8 more possibilities:
        5: refcen_wid = 0
        6: refcen_wid = 1

         _________              
        |  5:6:   |             
        | :     : |
        | :     : |
        | :     : |--------> fc_sid_ax
        | :     : |
        | :.....: |
        |__0:_:0__|


    Parameters
    ----------
    d_lbear : dictionary
        Dictionary with the dimensions of the linear bearing
    fc_fro_ax : FreeCAD.Vector
        Direction of the slide
    fc_bot_ax : FreeCAD.Vector
        Direction of the bottom
    fc_sid_ax : FreeCAD.Vector
        Direction of the other
        perpendicular direction. Not useful unless refcen_wid == 0
        if = V0 it doesn't matter
    axis_h : float
        Distance from the bottom to the rod axis

            * 0: take the minimum distance
            * X: (any value) take that value, if it is smaller than the 
              minimum it will raise an error and would not take that 
              value

    refcen_hei : int
        See picture, indicates the reference point
    refcen_dep : int
        See picture, indicates the reference point
    refcen_wid : int
        See picture, indicates the reference point, if it is
        on the bolt or on the axis
    pos : FreeCAD.Vector
        Position of the reference point,

    Attributes
    ----------
    nfro_ax : FreeCAD.Vector normalized fc_fro_ax
    nbot_ax : FreeCAD.Vector normalized fc_bot_ax
    nsid_ax : FreeCAD.Vector
    axis_h : float
    bolt2cen_dep : float
    bolt2cen_wid_n : float
    bolt2cen_wid_p : float
    bolt2bolt_wid : bolt2cen_wid_n + bolt2cen_wid_p


    Dimensions:
        * D : float

            housing_d

        * W : float
            
            housing_w

        * H : float
            
            housing_h

    FreeCAD objects:
        * fco_top : Top part of the linear bearing housing
        * fco_bot : Bottom part of the linear bearing housing
            
    ::

           ________                           ______________
          | ::...::|                         | ::........:: |
          | ::   ::|                         |.::        ::.|
          |-::( )::|---:                     |.::        ::.|  --> nfro_ax
          | ::...::|   +axis_h               | ::........:: | 
          |_::___::|   :                     | ::        :: |
          |_::___::|...:                     |_::________::_|
                                                     :
                                                     v
           _________                               nbot_ax
          |  0: :0  |                  
          | :     : |
          | :     : |........ --> nsid_ax
          | :     : |   :
          | :.....: |   + boltcen_dep
          |__0:_:0__|---:
             : : :
             : : :
             :.:.:
              : + bolt2cen_wid_p: distance form the bolt to the center
              :     on the width dimension. The bolt on the positive side
              + bolt2cen_wid_n: distance form the bolt to the center
             :      on the width dimension. The bolt on the negative side
             :
             + if refcen_wid=0 the reference will be on the bolt2cen_wid_n
         
                                             ...... D .......
                                             :              :
           ________....                      :______________:
          | ::...::|   :                     | ::........:: |
          | ::   ::|   :                     |.::        ::.|
          |-::( )::|   :                     |.::        ::.|  --> nfro_ax
          | ::...::|   + H                   | ::........:: | 
          |_::___::|...:                     |_::________::_|
          :        :
          :........:
              + 
              W


          bolts_side = 0            bolts_side = 1
           _________                
          |  0: :0  |                ___________ 
          | :     : |               | 0:     :0 |
          | :     : |               |  :     :  |
          | :     : |               |  :     :  |
          | :.....: |               |_0:_____:0_|
          |__0:_:0__|

    """

    MIN_SEP_WALL = 3. # min separation of a wall
    MIN2_SEP_WALL = 2. # min separation of a wall
    OUT_SEP_H = kparts.OUT_SEP_H # minimum separation of the linear bearing
    MTOL = kparts.MTOL
    MLTOL = kparts.MLTOL
    TOL_BEARING_L = kparts.TOL_BEARING_L
    # Radius to fillet the sides
    FILLT_R = kparts.FILLT_R

    def __init__(self, d_lbear,
                 fc_fro_ax = VX,
                 fc_bot_ax =VZN,
                 fc_sid_ax = V0,
                 axis_h = 0,
                 bolts_side = 1,
                 refcen_hei = 1,
                 refcen_dep  = 1,
                 refcen_wid  = 1,
                 bolt2cen_wid_n = 0,
                 bolt2cen_wid_p = 0,
                 pos = V0,
                 name = 'thinlinbearhouse_asim'
                ):

        self.name = name
        self.base_place = (0,0,0)
        # normalize, just in case
        nfro_ax = DraftVecUtils.scaleTo(fc_fro_ax,1)
        nbot_ax = DraftVecUtils.scaleTo(fc_bot_ax,1)
        nbot_ax_n = DraftVecUtils.neg(nbot_ax)
        # vector perpendicular to the others
        v_cross = nfro_ax.cross(nbot_ax)
        if fc_sid_ax == V0:
            nsid_ax = v_cross
        else:
            nsid_ax =  DraftVecUtils.scaleTo(fc_sid_ax,1)
            if not fcfun.fc_isparal (v_cross,nsid_ax):
                logger.debug("fc_sid_ax not perpendicular")
                nsid_ax = v_cross

        self.rod_r = d_lbear['Di']/2.
        rod_r = self.rod_r
        self.bear_r = d_lbear['Di']
        if rod_r >= 6:
            BOLT_D = 4
        else:
            BOLT_D = 3  # M3 bolts

        doc = FreeCAD.ActiveDocument

        MIN_SEP_WALL = self.MIN_SEP_WALL
        MIN2_SEP_WALL = self.MIN2_SEP_WALL
        OUT_SEP_H = self.OUT_SEP_H
        # bolt dimensions:
        MTOL = self.MTOL
        MLTOL = self.MLTOL
        BOLT_HEAD_R = kcomp.D912_HEAD_D[BOLT_D] / 2.0
        BOLT_HEAD_L = kcomp.D912_HEAD_L[BOLT_D] + MTOL
        BOLT_HEAD_R_TOL = BOLT_HEAD_R + MTOL/2.0 
        BOLT_SHANK_R_TOL = BOLT_D / 2.0 + MTOL/2.0

        # bearing dimensions:
        bearing_l     = d_lbear['L'] 
        bearing_l_tol = bearing_l + self.TOL_BEARING_L
        bearing_d     = d_lbear['De']
        bearing_d_tol = bearing_d + 2.0 * self.MLTOL
        bearing_r     = bearing_d / 2.0
        bearing_r_tol = bearing_r + self.MLTOL

        # dimensions of the housing:
        # length on the direction of the sliding rod
        bolt2wall = fcfun.get_bolt_end_sep(BOLT_D, hasnut=0) 
        #housing_d = bearing_l_tol + 2 * (2*BOLT_HEAD_R_TOL + 2* MIN_SEP_WALL)
        if bolts_side == 1:
            # bolts on the side of the linear bearing
            # bolt2cen_wid: distance from the center (axis) to the bolt center
            bolt2cen_wid = fcfun.get_bolt_bearing_sep (BOLT_D, hasnut=0,
                                                    lbearing_r = bearing_r) 

        else:
            # bolts after the linear bearing (front axis)
            # it will be longer (on D), and shorter (on W)
            bolt2cen_wid = fcfun.get_bolt_bearing_sep (BOLT_D, hasnut=0,
                                     lbearing_r = rod_r ) 
                                    #lbearing_r = rod_r + kparts.ROD_SPACE_MIN) 

        # check if it is going to be wider
        if bolt2cen_wid_n > 0:
            if bolt2cen_wid_n < bolt2cen_wid:
                logger.debug("bolt2cen_wid_n smaller than minimum")
                bolt2cen_wid_n = bolt2cen_wid
            else:
                bolt2cen_wid_n = bolt2cen_wid_n
        else:
            bolt2cen_wid_n = bolt2cen_wid
        if bolt2cen_wid_p > 0:
            if bolt2cen_wid_p < bolt2cen_wid:
                logger.debug("bolt2cen_wid_p smaller than minimum")
                bolt2cen_wid_p = bolt2cen_wid
            else:
                bolt2cen_wid_p = bolt2cen_wid_p
        else:
            bolt2cen_wid_p = bolt2cen_wid

        if bolts_side == 1:
            # it will be shorter (on D), and wider (on W)
            housing_d = bearing_l + 2 * MIN_SEP_WALL
            housing_w = 2 * bolt2wall + bolt2cen_wid_n + bolt2cen_wid_p
        else: 
            housing_d = bearing_l + 4*bolt2wall #bolt_r is included in bolt2wall
            housing_w = max ((bearing_d + 2* MIN_SEP_WALL), 
                              2 * bolt2wall + bolt2cen_wid_n + bolt2cen_wid_p)


        print("housing_d: %", housing_d)
        print("housing_w: %", housing_w)

        # bolt distance
        # distance of the bolts to the center, on nfro_ax dir
        bolt2cen_dep = housing_d/2. - bolt2wall

        # minimum height of the housing 
        housing_min_h = bearing_d + 2 * OUT_SEP_H
        axis_min_h = housing_min_h / 2.
        print("min housing_h: %", housing_min_h)
        if axis_h == 0:
            # minimum values
            housing_h = housing_min_h
            axis_h = axis_min_h
        elif axis_h >= axis_min_h:
            # the lower part will have longer height: axis_h
            # the upper part will be the minimum: axis_min_h
            housing_h = axis_h + axis_min_h
            axis_h = axis_h
        else: # the argument has an axis_h lower than the minimum possible
            logger.debug("axis_h %s cannot be smaller than %s",
                         str(axis_h), str(axis_min_h))
            housing_h = housing_min_h
            axis_h = axis_min_h

        # Attributes
        self.D = housing_d
        self.W = housing_w
        self.H = housing_h
        self.axis_h = axis_h
        self.bolt2cen_dep = bolt2cen_dep
        self.bolt2cen_wid_n = bolt2cen_wid_n
        self.bolt2cen_wid_p = bolt2cen_wid_p
        self.bolt2bolt_wid = bolt2cen_wid_p + bolt2cen_wid_n
        self.nfro_ax = nfro_ax
        self.nbot_ax = nbot_ax
        self.nsid_ax = nsid_ax

        #To make the boxes, we take the reference on midcenter=1 and 
        # refcen_hei = 0. Point 2 on the drawing

        if refcen_dep == 0: #the center is not on frontal plane
            # get the vector from the reference center to the center:
            fc_ref2cen_dep = DraftVecUtils.scale(nfro_ax,
                                                 bolt2cen_dep)
        else:
            fc_ref2cen_dep = V0

        if refcen_hei == 1:
            fc_ref2bot_hei = DraftVecUtils.scale(nbot_ax,axis_h)
            fc_ref2cen_hei = V0
        else:
            fc_ref2bot_hei = V0
            fc_ref2cen_hei = DraftVecUtils.scale(nbot_ax,-axis_h)

        if refcen_wid == 0:
            fc_ref2cen_wid = DraftVecUtils.scale(nsid_ax, bolt2cen_wid_n)
            # since it is not symmetrical the side n and the side p, we
            # another center for the housing, not for the rod
            fc_ref2houscen_wid = DraftVecUtils.scale(nsid_ax,
                                        (bolt2cen_wid_n + bolt2cen_wid_p)/2.)
        else:
            fc_ref2cen_wid = V0
            # since it is not symmetrical the side n and the side p, we
            # another center for the housing, not for the rod
            fc_ref2houscen_wid = DraftVecUtils.scale(nsid_ax,
                                        (bolt2cen_wid_p - bolt2cen_wid_n)/2.)


        botcenter_pos = pos + fc_ref2cen_dep + fc_ref2bot_hei + fc_ref2cen_wid
        bothouscenter_pos =  (  pos + fc_ref2cen_dep + fc_ref2bot_hei
                              + fc_ref2houscen_wid)

        # point 1 on the drawing
        axiscenter_pos = pos + fc_ref2cen_dep + fc_ref2cen_hei + fc_ref2cen_wid
        axishouscenter_pos = (  pos + fc_ref2cen_dep + fc_ref2cen_hei
                              + fc_ref2houscen_wid )
        # center on the top
        topcenter_pos = botcenter_pos + DraftVecUtils.scale(nbot_ax_n,
                                                            housing_h)

        shp_housing = fcfun.shp_box_dir(box_w = housing_w,
                                        box_d = housing_d, #dir of nfro_ax
                                        box_h = housing_h,
                                        fc_axis_h = nbot_ax_n,
                                        fc_axis_d = nfro_ax,
                                        cw= 1, cd=1, ch=0,
                                        pos = bothouscenter_pos)
        # fillet, small
        shp_block = fcfun.shp_filletchamfer_dir(shp_housing,
                                                fc_axis=fc_bot_ax,
                                                radius=2)

        # the rod hole
        shp_rod = fcfun.shp_cylcenxtr(r = rod_r + kparts.ROD_SPACE_MIN,
                                      h = housing_d,
                                      normal = nfro_ax,
                                      ch = 1, xtr_top = 1, xtr_bot=1,
                                      pos = axiscenter_pos)
        # the linear bearing hole
        shp_lbear = fcfun.shp_cylcenxtr(r = bearing_r_tol,
                                        h = bearing_l_tol,
                                        normal = nfro_ax,
                                        ch = 1, xtr_top = 1, xtr_bot=1,
                                        pos = axiscenter_pos)
        shp_rodlbear = shp_rod.fuse(shp_lbear)

        # 4 bolts 
        
        bolt_holes = []

        for vec_axis in [DraftVecUtils.scale(nfro_ax,bolt2cen_dep),
                         DraftVecUtils.scale(nfro_ax,-bolt2cen_dep)]:
            for vec_perp in [DraftVecUtils.scale(nsid_ax,
                                                 bolt2cen_wid_p),
                             DraftVecUtils.scale(nsid_ax,
                                                 -bolt2cen_wid_n)]:
                pos_i = topcenter_pos + vec_axis + vec_perp
                # the nut hole will be on the bottom side,
                
                shp_bolt = fcfun.shp_bolt_dir (
                                  r_shank = BOLT_SHANK_R_TOL,
                                  l_bolt  = housing_h,
                                  r_head  = BOLT_HEAD_R_TOL,
                                  l_head  = BOLT_HEAD_L,
                                  hex_head = 0,
                                  xtr_head=1,     xtr_shank=1,
                                  support=1,
                                  fc_normal = nbot_ax,
                                  fc_verx1=V0,
                                  pos = pos_i)
                bolt_holes.append(shp_bolt)

        shp_holes = shp_rodlbear.multiFuse(bolt_holes)       
        shp_lbear_housing = shp_block.cut(shp_holes)
        doc.recompute()
        # making 2 parts, intersection with 2 boxes:
        shp_box_top = fcfun.shp_box_dir(
                                     box_w = housing_w + 2,
                                     box_d = housing_d + 2, 
                                     box_h = housing_h - axis_h + 1,
                                     fc_axis_h = nbot_ax_n,
                                     fc_axis_d = nfro_ax,
                                     cw= 1, cd=1, ch=0,
                                     pos = axishouscenter_pos)
        shp_lbear_housing_top = shp_lbear_housing.common(shp_box_top)
        shp_lbear_housing_top = shp_lbear_housing_top.removeSplitter() 
        fco_lbear_top = doc.addObject("Part::Feature", name + '_top') 
        fco_lbear_top.Shape = shp_lbear_housing_top


        shp_box_bot = fcfun.shp_box_dir(
                                     box_w = housing_w + 2,
                                     box_d = housing_d + 2,
                                     # larger, just in case
                                     box_h = axis_h + 1,
                                     fc_axis_h = nbot_ax,
                                     fc_axis_d = nfro_ax,
                                     cw= 1, cd=1, ch=0,
                                     pos = axishouscenter_pos)
        shp_lbear_housing_bot = shp_lbear_housing.common(shp_box_bot)
        shp_lbear_housing_bot = shp_lbear_housing_bot.removeSplitter()
        fco_lbear_bot = doc.addObject("Part::Feature", name + '_bot') 
        fco_lbear_bot.Shape = shp_lbear_housing_bot

        self.fco_top = fco_lbear_top
        self.fco_bot = fco_lbear_bot

    def BasePlace (self, position = (0,0,0)):
        self.base_place = position
        vpos = FreeCAD.Vector(position)
        self.fco_top.Placement.Base = vpos
        self.fco_bot.Placement.Base = vpos

    def color (self, color = (1,1,1)):
        self.fco_top.ViewObject.ShapeColor = color
        self.fco_bot.ViewObject.ShapeColor = color

    def export_stl (self, name = ""):
        #filepath = os.getcwd()
        if not name:
            name = self.name
        stlPath = filepath + stl_dir
        stlFileName_top = stlPath + name + "_top" + ".stl"
        stlFileName_bot = stlPath + name + "_bot" + ".stl"
        # exportStl not working well with FreeCAD 0.17
        #self.fco_top.Shape.exportStl(stlFileName_top)
        #self.fco_bot.Shape.exportStl(stlFileName_bot)

        mesh_shp_top = MeshPart.meshFromShape(self.fco_top.Shape,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp_top.write(stlFileName_top)
        del mesh_shp_top
        mesh_shp_bot = MeshPart.meshFromShape(self.fco_bot.Shape,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp_bot.write(stlFileName_bot)
        del mesh_shp_bot




#doc = FreeCAD.newDocument()
#ThinLinBearHouseAsim (kcomp.LMELUU[12],
#                  fc_fro_ax = VX,
#                  fc_bot_ax = VZN,
#                  fc_sid_ax = VYN,
#                  axis_h = 0, bolts_side=0,
#                  refcen_hei=1, refcen_dep=1, refcen_wid = 1,
#                  bolt2cen_wid_n = 0,
#                  bolt2cen_wid_p = 25)



# ----------- NemaMotorHolder
class NemaMotorHolder (object):

    """
    Creates a holder for a Nema motor
    ::

         __________________
        ||                ||
        || O     __     O ||
        ||    /      \    ||
        ||   |   1    |   ||
        ||    \      /    ||
        || O     __     O ||
        ||________________|| .....
        ||_______2________|| ..... wall_thick

                                      motor_xtr_space_d
                                     :  :
         ________3_________        3_:__:____________ ....
        |  ::  :    :  ::  |       |      :     :    |    + motor_thick
        |__::__:_1__:__::__|       2......:..1..:....|....:..........> fc_axis_n
        ||                ||       | :              /
        || ||          || ||       | :           /
        || ||          || ||       | :        /
        || ||          || ||       | :      /
        || ||          || ||       | :   /
        ||________________||       |_: /
        ::                         :                 :
         + reinf_thick             :....tot_d........:

                fc_axis_h
                 :
         ________:_________ ..................................
        |  ::  :    :  ::  |                                  :
        |__::__:_1__:__::__|....................              :
        ||                ||....+ motor_min_h  :              :
        || ||          || ||                   :              +tot_h
        || ||          || ||                   + motor_max_h  :
        || ||          || ||                   :              :
        || ||          || ||...................:              :
        ||________________||..................................:
        :  :            :  :
        :  :            :  :
        :  :............:  :
        :   bolt_wall_sep  :
        :                  :
        :                  :
        :.....tot_w........:
                         ::
                          motor_xtr_space
        
       1: ref_axis = 1 & ref_bolt = 0 
       2: ref_axis = 0 & ref_bolt = 0 
       --3: ref_axis = 0 & ref_bolt = 0 

    Parameters
    ----------
    nema_size : int
        Size of the motor (NEMA)
    wall_thick : float
        Thickness of the side where the holder will be screwed to
    motor_thick : float
        Thickness of the top side where the motor will be screwed to
    reinf_thick : float
        Thickness of the reinforcement walls
    motor_min_h : float
        Distance of from the inner top side to the top hole of the bolts to 
        attach the holder (see drawing)
    motor_max_h : float
        Distance of from the inner top side to the bottom hole of the bolts to 
        attach the holder
    rail : int
        * 2: the rail goes all the way to the end, not closed
        * 1: the holes for the bolts are not holes, there are 2 rails, from
          motor_min_h to motor_max_h
        * 0: just 2 pairs of holes. One pair at defined by motor_min_h and the
          other defined by motor_max_h

    motor_xtr_space : float
        Extra separation between the motor and the sides
    motor_xtr_space_d : float
        Extra separation between the motor and the wall side (where the bolts)
        it didn't exist before, so for compatibility
        
            * -1: same has motor_xtr_space (compatibility), considering bolt head
              length
            * 0: no separation
            * >0: exact separation

    bolt_wall_d : int/float
        Metric of the bolts to attach the holder
    bolt_wall_sep : float
        Separation between the 2 bolt holes (or rails). Optional.
    chmf_r : float
        Radius of the chamfer, whenever chamfer is done
    fc_axis_h : FreeCAD Vector
        Axis along the axis of the motor
    fc_axis_n : FreeCAD Vector
        Axis normal to surface where the holder will be attached to
    ref_axis : int
        * 1: the zero of the vertical axis (axis_h) is on the motor axis
        * 0: the zero of the vertical axis (axis_h) is at the wall

    pos : FreeCAD.Vector
        Position of the holder (considering ref_axis)
    wfco : int
        * 1: creates a FreeCAD object
        * 0: only creates a shape

    name : string
        Name of the FreeCAD object

    """

    def __init__ (self,
                  nema_size = 17,
                  wall_thick = 4.,
                  motor_thick = 4.,
                  reinf_thick = 4.,
                  motor_min_h =10.,
                  motor_max_h =20.,
                  rail = 1, # if there is a rail or not at the profile side
                  motor_xtr_space = 2., # counting on one side
                  motor_xtr_space_d = -1, # same as motor_xtr_space
                  bolt_wall_d = 4., # Metric of the wall bolts
                  bolt_wall_sep = 30., # optional
                  chmf_r = 1.,
                  fc_axis_h = VZ,
                  fc_axis_n = VX,
                  #fc_axis_p = VY,
                  ref_axis = 1, 
                  #ref_bolt = 0,
                  pos = V0,
                  wfco = 1,
                  name = 'nema_holder'):

        doc = FreeCAD.ActiveDocument

        # normalize de axis
        axis_h = DraftVecUtils.scaleTo(fc_axis_h,1)
        axis_n = DraftVecUtils.scaleTo(fc_axis_n,1)
        axis_p = axis_h.cross(axis_n) #perpendicular
        axis_n_n = axis_n.negative()
        axis_h_n = axis_h.negative()

        self.axis_h = axis_h
        self.axis_n = axis_n
        self.axis_p = axis_p
        # best axis to print:
        self.axis_print = axis_h_n

        self.pos = pos
        self.name = name

        motor_w = kcomp.NEMA_W[nema_size]
        motor_bolt_sep = kcomp.NEMA_BOLT_SEP[nema_size]
        motor_bolt_d = kcomp.NEMA_BOLT_D[nema_size]

        boltwallshank_r_tol = kcomp.D912[bolt_wall_d]['shank_r_tol']
        boltwallhead_l = kcomp.D912[bolt_wall_d]['head_l']
        boltwallhead_r = kcomp.D912[bolt_wall_d]['head_r']
        washer_thick = kcomp.WASH_D125_T[bolt_wall_d]

        # calculation of the bolt wall separation
        # if larger is not needed
        max_bolt_wall_sep = motor_w - 2 * boltwallhead_r
      
        motor_box_w = motor_w
        if bolt_wall_sep == 0:
            bolt_wall_sep = max_bolt_wall_sep
        elif bolt_wall_sep > max_bolt_wall_sep:
            logger.debug('bolt wall separtion larger: ' + str(bolt_wall_sep))
            logger.debug('making the box width larger')
            motor_box_w = bolt_wall_sep + 2 * boltwallhead_r
            logger.debug('taking large value: ' + str(bolt_wall_sep))
        elif bolt_wall_sep <  4 * boltwallhead_r:
            logger.debug('bolt wall separtion too short: ' + str(bolt_wall_sep))
            bolt_wall_sep = max_bolt_wall_sep
            logger.debug('taking large value: ' + str(bolt_wall_sep))
        # else: the given separation is good

        # making the big box that will contain everything and will be cut
        if rail == 2:
            tot_h = motor_thick + motor_max_h
        else:
            tot_h = motor_thick + motor_max_h + 2 * bolt_wall_d
        tot_w = 2* reinf_thick + motor_box_w + 2 * motor_xtr_space

        if motor_xtr_space_d == -1: # same as motor_xtr_space
            motor_xtr_space_d = motor_xtr_space + boltwallhead_l + washer_thick
        tot_d = wall_thick + motor_w + motor_xtr_space_d


        # getting the offset of the reference
        # distance of the motor axis to de wall
        motax2wall_dist = wall_thick + motor_w/2. + motor_xtr_space_d
        self.motax2wall_dist = motax2wall_dist
        if ref_axis == 1:
            ref2motax = V0  #point 1
            ref2motaxwall = DraftVecUtils.scale(axis_n_n, motax2wall_dist) 
        else:
            ref2motax = DraftVecUtils.scale(axis_n, motax2wall_dist)
            ref2motaxwall = V0 # point 2

        motax_pos = pos + ref2motax
        motaxwall_pos = pos + ref2motaxwall

        # point centered on the symmetrical plane, on top of axis_h and
        # on the wall (point 3)
        ref2topwallcent = (  ref2motaxwall
                             + DraftVecUtils.scale(axis_h, motor_thick))
        topwallcent_pos = pos + ref2topwallcent

        # attributes with dimensions, distances and positions
        self.tot_h = tot_h
        self.tot_w = tot_w
        self.tot_d = tot_d
        self.ref2motax = ref2motax
        self.ref2motaxwall = ref2motaxwall
        self.ref2topwallcent = ref2topwallcent
        self.motax_pos = motax_pos
        self.motaxwall_pos = motaxwall_pos
        self.topwallcent_pos = topwallcent_pos

        # make the whole box, extra height and depth to cut all the way
        # back and down:
        shp_box = fcfun.shp_box_dir (box_w = tot_w,
                                     box_d = tot_d,
                                     box_h = tot_h,
                                     fc_axis_h = axis_h_n,
                                     fc_axis_d = axis_n,
                                     cw=1, cd=0, ch=0, pos = topwallcent_pos)
        # little chamfer at the corners, if fillet there are some problems
        shp_box = fcfun.shp_filletchamfer_dir(shp_box, axis_h,
                                              fillet=0,
                                              radius = chmf_r)
        doc.recompute()
        shp_box = shp_box.removeSplitter()

        # chamfer of the box to make a 'triangular' reinforcement
        chmf_reinf_r = min(tot_d- wall_thick, tot_h-motor_thick)
        # look for the point:
        chmf_pos = (  topwallcent_pos
                          + DraftVecUtils.scale(axis_h_n, tot_h)
                          + DraftVecUtils.scale(axis_n, tot_d))
        shp_box = fcfun.shp_filletchamfer_dirpt(shp_box, axis_p,
                                              fc_pt =chmf_pos,
                                              fillet=0,
                                              radius = chmf_reinf_r)
        doc.recompute()

        # holes:
        holes = []
        motaxinwall_pos = (motaxwall_pos
                           + DraftVecUtils.scale(axis_n, wall_thick))
        # the space for the motor
        shp_motor = fcfun.shp_box_dir (
                                   box_w = motor_box_w +  2 * motor_xtr_space,
                                   box_d = tot_d + chmf_r,
                                   box_h = tot_h,
                                   fc_axis_h = axis_h_n,
                                   fc_axis_d = axis_n,
                                   cw=1, cd=0, ch=0,
                                   pos = motaxinwall_pos)

        shp_motor = fcfun.shp_filletchamfer_dir(shp_motor, fc_axis=axis_h,
                                                fillet=0, radius=chmf_r)
        doc.recompute()
        holes.append(shp_motor)

        # central circle of the motor
        shp_hole = fcfun.shp_cylcenxtr(r=(motor_bolt_sep - motor_bolt_d)/2.,
                                       h = motor_thick,
                                       normal = axis_h,
                                       ch = 0,
                                       xtr_top = 1,
                                       xtr_bot = 1,
                                       pos = motax_pos)
        holes.append(shp_hole)

        # motor bolt holes
        for add_n in (DraftVecUtils.scale(axis_n, motor_bolt_sep/2.),
                      DraftVecUtils.scale(axis_n,-motor_bolt_sep/2.)):
            for add_p in (DraftVecUtils.scale(axis_p, motor_bolt_sep/2.),
                      DraftVecUtils.scale(axis_p,-motor_bolt_sep/2.)):
                hole_pos = motax_pos + add_n + add_p
                shp_hole = fcfun.shp_cylcenxtr( r = motor_bolt_d/2.+TOL,
                                                h = motor_thick,
                                                normal = axis_h,
                                                ch = 0,
                                                xtr_top = 1,
                                                xtr_bot = 1,
                                                pos = hole_pos)
                holes.append(shp_hole)

        # rail holes. To mount the motor holder to a profile or whatever
        for add_p in (DraftVecUtils.scale(axis_p, bolt_wall_sep/2.),
                      DraftVecUtils.scale(axis_p,-bolt_wall_sep/2.)):
            # hole for the rails
            hole_pos = (motaxwall_pos + add_p
                        + DraftVecUtils.scale(axis_h_n, motor_min_h))
            if rail > 0:
                shp_hole = fcfun.shp_box_dir_xtr(
                                       box_w = boltwallshank_r_tol * 2.,
                                       box_d = wall_thick,
                                       box_h = motor_max_h - motor_min_h,
                                       fc_axis_h = axis_h_n,
                                       fc_axis_d = axis_n,
                                       cw=1, cd=0, ch=0,
                                       xtr_d =1, xtr_nd=1, #to cut
                                       pos = hole_pos)
                holes.append(shp_hole)
            # hole for the ending of the rails (semicircles)
            for add_h in (DraftVecUtils.scale(axis_h_n, motor_min_h),
                          DraftVecUtils.scale(axis_h_n, motor_max_h)):
                hole_pos = motaxwall_pos + add_h + add_p
                shp_hole = fcfun.shp_cylcenxtr( r = boltwallshank_r_tol,
                                                h = wall_thick,
                                                normal = axis_n,
                                                ch = 0,
                                                xtr_top = 1,
                                                xtr_bot = 1,
                                                pos = hole_pos)
                holes.append(shp_hole)

        
                

        shp_holes = fcfun.fuseshplist(holes)

        shp_motorholder = shp_box.cut(shp_holes)
        
        self.shp = shp_motorholder
        if wfco == 1:
            # a freeCAD object is created
            fco_motorholder = doc.addObject("Part::Feature", name )
            fco_motorholder.Shape = shp_motorholder
            self.fco = fco_motorholder



    def color (self, color = (1,1,1)):
        if self.wfco == 1:
            self.fco.ViewObject.ShapeColor = color
        else:
            logger.debug("Object with no fco")

    # exports the shape to STL format
    def export_stl (self, name = ""):
        # ------------------------------------------
        # check how to do this
        axis_up = self.axis_print
        rotation = DraftVecUtils.getRotation(axis_up, VZ)
        if (DraftVecUtils.equals(axis_up, VZN)):
            #we have to flip it, but rotation doesn't get it done:
            rotation = FreeCAD.Rotation(VX,180)
            
        shp = self.shp
        #shp.Placement.Rotation = rotation
        #Part.show(shp)
        shp.Placement.Base = self.topwallcent_pos.negative()
        #Part.show(shp)
        shp.Placement.Rotation = rotation
        #Part.show(shp)
        
        if not name:
            name = self.name
        stlPath = filepath + "/stl/"
        stlFileName = stlPath + name + ".stl"
        #print (" %s", stlFileName)

        # exportStl is not working well with FreeCAD 0.17
        #self.shp.exportStl(stlFileName)
        mesh_shp = MeshPart.meshFromShape(self.shp,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp.write(stlFileName)
        del mesh_shp






#doc = FreeCAD.newDocument()
#h_nema = NemaMotorHolder ( 
#                  nema_size = 17,
#                  wall_thick = 4.,
#                  motor_thick = 4.,
#                  reinf_thick = 3.,
#                  motor_min_h =8., 
#                  motor_max_h = 35.,
#                  motor_xtr_space = 2., # counting on one side
#                  motor_xtr_space_d = -1, 
#                  bolt_wall_d = 4.,
#                  chmf_r = 0.2,
#                  #bolt_wall_sep = 40., # optional
#                  rail = 1,
#                  fc_axis_h = VZN,#FreeCAD.Vector(1,1,0),
#                  fc_axis_n = VX, #FreeCAD.Vector(1,-1,0),
#                  #fc_axis_p = VY,
#                  ref_axis = 1, 
#                  #ref_bolt = 0,
#                  pos = V0, # FreeCAD.Vector(3,2,5),
#                  wfco = 1,
#                  name = 'nema17_holder_rail35_8')

#doc = FreeCAD.newDocument()
#h_nema = NemaMotorHolder ( 
#                  nema_size = 17,
#                  wall_thick = 5.,
#                  motor_thick = 4.,
#                  reinf_thick = 4.,
#                  motor_min_h =8.,
#                  motor_max_h = 33.,
#                  rail = 0,
#                  motor_xtr_space = 2., # counting on one side
#                  bolt_wall_d = 3.,
#                  chmf_r = 1.,
#                  fc_axis_h = VZN,#FreeCAD.Vector(1,1,0),
#                  fc_axis_n = VX, #FreeCAD.Vector(1,-1,0),
#                  #fc_axis_p = VY,
#                  ref_axis = 1, 
#                  #ref_bolt = 0,
#                  pos = V0, # FreeCAD.Vector(3,2,5),
#                  wfco = 1,
#                  name = 'nema_holder')


# a porras:
#doc = FreeCAD.newDocument()
#h_nema = NemaMotorHolder ( 
#                  nema_size = 17,
#                  wall_thick = 5.,
#                  motor_thick = 3.,
#                  reinf_thick = 4.,
#                  motor_min_h =8.,
#                  motor_max_h = 43.,
#                  rail = 1,
#                  motor_xtr_space = 2., # counting on one side
#                  bolt_wall_d = 3.,
#                  chmf_r = 1.,
#                  fc_axis_h = VZN,#FreeCAD.Vector(1,1,0),
#                  fc_axis_n = VX, #FreeCAD.Vector(1,-1,0),
#                  #fc_axis_p = VY,
#                  ref_axis = 1, 
#                  #ref_bolt = 0,
#                  pos = V0, # FreeCAD.Vector(3,2,5),
#                  wfco = 1,
#                  name = 'nema_holder_52h')








# ----------- ShpNemaMotorHolder
class ShpNemaMotorHolder (shp_clss.Obj3D):
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
                  pos = V0):

        if axis_w is None or axis_w == V0:
            axis_w = axis_h.cross(axis_d)

        shp_clss.Obj3D.__init__(self, axis_d, axis_w, axis_h)

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
            self.bolt_wall_sep = self.self.max_bolt_wall_sep
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
        self.shp = shp_motorholder


#doc = FreeCAD.newDocument()
#shpob_nema = ShpNemaMotorHolder ( 
#                  nema_size = 17,
#                  wall_thick = 6.,
#                  motorside_thick = 6.,
#                  reinf_thick = 1.,
#                  motor_min_h =10.,
#                  motor_max_h =50.,
#                  rail = 1, # if there is a rail or not at the profile side
#                  motor_xtr_space = 3., # counting on one side
#                  bolt_wall_d = 4., # Metric of the wall bolts
#                  #bolt_wall_sep = 30., # optional
#                  chmf_r = 1.,
#                  axis_h = VZ,
#                  axis_d = VX,
#                  axis_w = None,
#                  pos_h = 1,  # 1: inner wall of the motor side
#                  pos_d = 3,  # 3: motor axis
#                  pos_w = 0,  # 0: center of symmetry
#                  pos = V0)

#Part.show(shpob_nema.shp)

class PartNemaMotorHolder(fc_clss.SinglePart, ShpNemaMotorHolder):
    """ Integration of a ShpNemaMotorHolder object into PartNemaMotorHolder
    object, so it is a FreeCAD object that can be visualized in FreeCAD
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
                  name = ''):

        default_name = 'nema' + str(nema_size) + '_motorholder'
        self.set_name (name, default_name, change = 0)
        # First the shape is created
        ShpNemaMotorHolder.__init__(self,
                  nema_size = nema_size,
                  wall_thick = wall_thick,
                  motorside_thick = motorside_thick,
                  reinf_thick = reinf_thick,
                  motor_min_h = motor_min_h,
                  motor_max_h = motor_max_h,
                  rail = rail, 
                  motor_xtr_space = motor_xtr_space,
                  bolt_wall_d = bolt_wall_d,
                  bolt_wall_sep = bolt_wall_sep,
                  chmf_r = chmf_r,
                  axis_h = axis_h,
                  axis_d = axis_d,
                  axis_w = axis_w,
                  pos_h = pos_h,
                  pos_d = pos_d,
                  pos_w = pos_w,
                  pos = pos)

        #then the part:
        fc_clss.SinglePart.__init__(self)

        # save the arguments that haven't been assigned as attributes
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): 
                setattr(self, i, values[i])

#doc = FreeCAD.newDocument()
#part_nemahold = PartNemaMotorHolder ( 
#                  nema_size = 23,
#                  wall_thick = 4.,
#                  motorside_thick = 4.,
#                  reinf_thick = 4.,
#                  motor_min_h =10.,
#                  motor_max_h =20.,
#                  rail = 1, # if there is a rail or not at the profile side
#                  motor_xtr_space = 2., # counting on one side
#                  bolt_wall_d = 4., # Metric of the wall bolts
#                  #bolt_wall_sep = 30., # optional
#                  chmf_r = 1.,
#                  axis_h = VZ,
#                  axis_d = VX,
#                  axis_w = None,
#                  pos_h = 1,  # 1: inner wall of the motor side
#                  pos_d = 3,  # 3: motor axis
#                  pos_w = 0,  # 0: center of symmetry
#                  pos = V0)
















# ----------- ShpNemaMotorHolderVer
# TODO
#class ShpNemaMotorHolderVer (shp_clss.Obj3D):
    """
    Creates a VERTICAL holder for a Nema motor.
    ::

              axis_h
                 :
                 :                     0 1
         ________:_________             _........> axis_d
        |                  |           | |
        |  O     __     O  |           | |
        |     /      \     |
        |    |        |    |
        |     \      /     |
        |  O     __     O  |
        |                  | .....
        |  ||    ||    ||  |
        |  ||    ||    ||  |
        |  ||    ||    ||  |
        |  ||    ||    ||  |
        |  ||    ||    ||  |
        |  ||    ||    ||  |
        | ________________ | ..... > axis_w

        0: just 2 pairs of holes. One pair at defined by motor_min_h and the
           other defined by motor_max_h

    Parameters
    ----------
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


    def __init__ (self,
                  nema_size = 17,
                  wall_thick = 4.,
                  motor_min_h =10.,
                  motor_max_h =20.,
                  rail = 1, # if there is a rail or not at the profile side
                  axis_h = VZ,
                  axis_d = VX,
                  axis_w = None,
                  pos_h = 0,  # 1: inner wall of the motor side
                  pos_d = 0,  # 3: motor axis
                  pos_w = 0,  # 0: center of symmetry
                  pos = V0):

    """

class Plate3CageCubes (object):

    """
    Creates a plate to join 3 Cage Cubes

                          fc_top_ax   fc_fro_ax
                               :      /
        _______________________:_____/__________..............
       | O            O        :  O /         O |--top_h/2   + top_h
       |..........  ____  .....:..... ..........|..:.........:
       |o  ___  o: |SQR | :o  _:_ /o: :o  ___  o|
       |  /   \  : |____| :  / :.\..:.:. /...\..|..... fc_sid_ax
       |  \___/  :        :  \___/  : :  \___/  |
       |o_______o:________:o_______o:_:o_______o|
          :   :    :....:
          :. .:      + sqr_w
            + hole_d
                             fc_fro_ax
                               :
       ___________        _____:_____ __________ 
       |o  ___  o|        |o  _:_ /o| |o  ___  o|  --> cage cubes
       |  /   \  |        |  / : \  | |  /   \  |
       |  \___/  |        |  \_:_/  | |  \___/  |
       |o_______o|________|____:___ |_|o_______o|........... fc_sid_ax
       |  :   :              :   :       :   :  |  + thick
       |__:___:______________:___:_______:___:__|..:
            :                  :           :
            :.... cube_dist_n..:...........:
                                     + cube_dist_p



    Thruholes of the bolts are not drawn

    The position of the plate: pos, is referenced to the center of the
    hole of the middle plate.

    There are 3 axes:
        - fc_fro_ax: FreeCAD.Vector pointing to the direction of the cage
          cubes, and it is on the surface touching the cubes
        - fc_top_ax: FreeCAD.Vector pointing to the top, where there is an
          extra length (top_h) to hold an aluminum profile
        - fc_sid_ax: FreeCAD.Vector pointing to the side p (positive)

        ________________________________________
       | O            O           O           O |
       |..........        ........... ..........|
       |o  ___  o:        :o  ___  o: :o  ___  o|
       |  /   \  :        :  /   \  : :  /   \  |
       |  \___/  :        :  \___/  : :  \___/  |
       |o_______o:________:_________:_:o_______o|
            :                  :           :
            :.... cube_dist_n..:           :

    Arguments:
        d_cagecube: dictionary with the dimensions of the cage cube
        thick: thickness of the plate, in mm
        cube_dist_n: distance from center to center of the middle cage cube
               to the cube in opposite direction (negative) of fc_sid_ax
        cube_dist_p: distance from center to center of the middle cage cube
               to the cube in the same direction (positive) of fc_sid_ax
        top_h: length of the extra part on top of the plate to hold a
               aluminum profile or whatever
        cube_face: indicates which face of the cube is facing the plate.
               There are 3 possible faces (defined in kparts.py):
               THRUHOLE (1) : the big hole is a thruhole without threads
               THRURODS (2) : the face has 4 thruholes for the rods
               RODSCREWS(3): the face has 4 tapped holes for screwing the
                            end of the rods
        hole_d: diameter of the central thruhole facing the plate.
               0: take the value of the cagecube hole
               X: take this value, since there may be something attached,
                  such as a tubelens, which may have a ring that makes
                  necessary to have larger diameter hole
               -1: no hole
        boltatt_n: number of bolt holes on the extra top side
        boltatt_d: diameter of the bolt holes on the top side
        sqr_h: height of the square hole done if there is space between cubes
               if 0: no rectangle.
               The rectangle only will be on the larger space between cubes
        sqr_w: width of the square(rectangle) hole done if there is space
               between cubes. It is made in line with the top of the cubes
               centered on the width space
               if 0: takes all the space of the space
        fc_fro_ax: FreeCAD.Vector pointing to the direction of the cage
               cubes, and it is on the surface touching the cubes
        fc_top_ax: FreeCAD.Vector pointing to the top, where there is an
               extra length (top_h) to hold an aluminum profile
        fc_sid_ax: FreeCAD.Vector pointing to the side p (positive)
        fillet_r: radius of the fillet of the corners, if 0, no fillet
        holes_tol : Add tolerance for the holes, it seems that even when milled
                it is needed
        moreboltholes : if more bolt holes are made to attach things
        pos: FreeCAD.Vector with the position of the reference. 
               Center of the hole of the middle plate, on the face touching
               the cagecube
        name: str with the name of the FreeCAD.Object

    """

    ROD_SCREWS = kcomp_optic.ROD_SCREWS
    THRU_RODS = kcomp_optic.THRU_RODS
    THRU_HOLE = kcomp_optic.THRU_HOLE

    def __init__(self,
                 d_cagecube,
                 thick,
                 cube_dist_n,
                 cube_dist_p,
                 top_h = 10,
                 #which side of the cube faces the plate
                 cube_face = kcomp_optic.ROD_SCREWS,
                 hole_d = 0, 
                 boltatt_n = 6, 
                 boltatt_d = 3, 
                 sqr_h = 0,
                 sqr_w = 0,
                 fc_fro_ax = VX,
                 fc_top_ax = VZ,
                 fc_sid_ax = VY,
                 fillet_r = 1.,
                 holes_tol = 0,
                 moreboltholes = 0,
                 pos = V0,
                 name = 'Plate3CageCubes'
                ):

        self.d_cagecube = d_cagecube
        self.name = name
        cage_w = d_cagecube['L']

        #get normalized vectors
        nfro_ax = DraftVecUtils.scaleTo(fc_fro_ax,1)
        nfro_ax_n = nfro_ax.negative()
        ntop_ax = DraftVecUtils.scaleTo(fc_top_ax,1)
        nsid_ax = DraftVecUtils.scaleTo(fc_sid_ax,1)

        # calculate the plate dimensions
        # and its center
        #  ________________________________________.............
        # | O            O           O           O |  + top_h  :
        # |..........        ........... ..........|..:        :
        # |o  ___  o:        :o  _ _  o: :o  ___  o|  :        + plate_h
        # |  /   \  :        :  / : \  : :  /   \  |  + cage_w :
        # |  \___/  :        :  \___/  : :  \___/  |  :        :
        # |o_______o:________:o_______o:_:o_______o|..:........:
        # :    :                  :           :    :
        # :    :.... cube_dist_n..:...........:    :
        # :                          +cube_dist_p  :
        # :......plate_w...........................: 


        plate_w = cube_dist_n + cube_dist_p + cage_w
        plate_h = cage_w + top_h



        # the center of the plate on the fc_top_ax and tc_sid_ax vectors
        platecen_pos = ( pos
                  + DraftVecUtils.scale(ntop_ax,top_h/2.)
                  + DraftVecUtils.scale(nsid_ax,(cube_dist_p-cube_dist_n)/2.))

        shp_box = fcfun.shp_box_dir (box_w = plate_w,
                                     box_d = plate_h,
                                     box_h = thick,
                                     fc_axis_h = nfro_ax_n,
                                     fc_axis_d = ntop_ax,
                                     cw=1, cd=1, ch=0,
                                     pos = platecen_pos)

        if fillet_r > 0:
            # fillet the four corners
            shp_box = fcfun.shp_filletchamfer_dir(shp_box, fc_axis = fc_fro_ax,
                                              fillet = 1, radius = fillet_r)

        # diameter of the holes of the cubes:
        if cube_face == self.ROD_SCREWS:
            cube_hole_d = d_cagecube['thru_thread_d'] + holes_tol
            bolt_d = d_cagecube['rod_thread_d'] + holes_tol
        elif cube_face == self.THRU_RODS:
            cube_hole_d = d_cagecube['thru_thread_d'] + holes_tol
            bolt_d = d_cagecube['thru_rod_d'] + holes_tol
        elif cube_face == self.THRU_HOLE:
            cube_hole_d = d_cagecube['thru_hole_d'] + holes_tol
            bolt_d = d_cagecube['rod_thread_d'] + holes_tol
        else:
            logger.debug("cube_face not supported %s", cube_face)
            cube_hole_d = d_cagecube['thru_thread_d'] + holes_tol
            bolt_d = d_cagecube['rod_thread_d'] + holes_tol

        bolt_r = bolt_d/2.

        # position of the cage on the positive and negative sides:
        pos_cage_p = pos + DraftVecUtils.scale(nsid_ax,cube_dist_p)
        pos_cage_n = pos + DraftVecUtils.scale(nsid_ax,-cube_dist_n)
        holes_list = []
        if hole_d >= 0: #if <0: no hole
            if hole_d == 0:
                hole_d = cube_hole_d
            # check if the diameter is larger than the cage diameter
            elif hole_d < cube_hole_d:
                logger.debug("hole_d smaller than cube hole"); 
                logger.debug("taking the minimum %s", cube_hole_d)
                hole_d = cube_hole_d
            else:
                hole_d = hole_d

            hole_r = hole_d/2.
            # central big hole (it is on pos)
            shp_bighole_cen = fcfun.shp_cylcenxtr (r= hole_r, h = thick,
                                                   normal = nfro_ax_n,
                                                   ch=0, xtr_top=1, xtr_bot=1,
                                                   pos = pos)

            shp_bighole_p = fcfun.shp_cylcenxtr (r= hole_r, h = thick,
                                                 normal = nfro_ax_n,
                                                 ch=0, xtr_top=1, xtr_bot=1,
                                                 pos = pos_cage_p)

            shp_bighole_n = fcfun.shp_cylcenxtr (r= hole_r, h = thick,
                                                 normal = nfro_ax_n,
                                                 ch=0, xtr_top=1, xtr_bot=1,
                                                 pos = pos_cage_n)
            # add the large holes to the list
            holes_list.extend([shp_bighole_cen, shp_bighole_p,
                               shp_bighole_n])

        ################

        cagebolt_sep = d_cagecube['thru_rod_sep']
        cagebolt2cen = cagebolt_sep /2.
        bolt_pos_top_p = DraftVecUtils.scale(ntop_ax, cagebolt2cen)
        bolt_pos_top_n = DraftVecUtils.scale(ntop_ax, -cagebolt2cen)
        bolt_pos_sid_p = DraftVecUtils.scale(nsid_ax, cagebolt2cen)
        bolt_pos_sid_n = DraftVecUtils.scale(nsid_ax, -cagebolt2cen)

        for pos_i in [pos, pos_cage_p, pos_cage_n]:
            for top_add in [bolt_pos_top_p, bolt_pos_top_n]:
                for sid_add in [bolt_pos_sid_p, bolt_pos_sid_n]:
                    pos_boltcage = pos_i + top_add + sid_add
                    shp_boltcage = fcfun.shp_cylcenxtr (r= bolt_r, h = thick,
                                             normal = nfro_ax_n,
                                             ch=0, xtr_top=1, xtr_bot=1,
                                             pos = pos_boltcage)
                    holes_list.append(shp_boltcage)

        # bolts to attach the aluminum profile:
        if boltatt_n < 2:
            boltatt_n = 2
        # the first and the last bolt will be at the same fc_sid_ax as the
        # cage bols.
        # the distance between the first and the last is:
        boltatt_dist =  cube_dist_n + cube_dist_p + cagebolt_sep
        boltatt_sep = boltatt_dist / (boltatt_n - 1)
        vec_boltatt_add = DraftVecUtils.scale(nsid_ax, boltatt_sep)
        #The first bolt will be:
        boltatt_pos = (   pos_cage_n
                        + DraftVecUtils.scale(nsid_ax, -cagebolt2cen)
                        + DraftVecUtils.scale(ntop_ax, cage_w/2. + top_h/2.))
        boltatt_r = boltatt_d/2.
        for it_boltatt in range(boltatt_n):
            shp_boltatt = fcfun.shp_cylcenxtr (r= boltatt_r, h = thick,
                                             normal = nfro_ax_n,
                                             ch=0, xtr_top=1, xtr_bot=1,
                                             pos = boltatt_pos)
            boltatt_pos = boltatt_pos + vec_boltatt_add
            holes_list.append(shp_boltatt)

        if cube_dist_n > cube_dist_p :
            # large space central vector
            larg_sp_c_vec = DraftVecUtils.scale(nsid_ax,-cube_dist_n/2.)
            shor_sp_c_vec = DraftVecUtils.scale(nsid_ax,cube_dist_p/2.)
            # width of the large space
            larg_sp_w = cube_dist_n - cage_w
            shor_sp_w = cube_dist_p - cage_w
        else:
            larg_sp_c_vec = DraftVecUtils.scale(nsid_ax,cube_dist_p/2.)
            shor_sp_c_vec = DraftVecUtils.scale(nsid_ax,-cube_dist_n/2.)
            # width of the large space
            larg_sp_w = cube_dist_p - cage_w
            shor_sp_w = cube_dist_n - cage_w

        # square (rectangle holes):
        #  a rectangle on the larger distance between the cubes
        if sqr_h > 0: 
            #  ________________________________________
            # | O            O           O           O |
            # |.......... _____                ........|
            # |o  ___  o: |_:_| larg_sp_c_pos    ___  o|
            # |  /   \  :   :<--------: \  : :  /   \  |
            # |  \___/  :        :  \___/  : :  \___/  |
            # |o_______o:________:o_______o:_:o_______o|
            # vector of the distance from the center to the square

            pos_sqr = (pos + larg_sp_c_vec +
                             DraftVecUtils.scale(ntop_ax,cage_w/2. - sqr_h/2.))
            if sqr_w == 0: # square width will be the total distance
                sqr_w = larg_sp_w

            # since I don't have shp_box_dir_extr, I put extra depth
            # double thick because we need extra and I haven't brought it back
            # then a little more to cut the other
            # 1 mm tolerance. 0.5 on each side
            shp_sqr = fcfun.shp_box_dir (box_w = sqr_w + 1., # 1mm tolerance
                                         box_d = 2.1 * thick,
                                         box_h = sqr_h + 1.,
                                         fc_axis_h = ntop_ax,
                                         fc_axis_d = nfro_ax_n,
                                         cw=1, cd=1, ch=1, pos= pos_sqr)
            holes_list.append(shp_sqr)
            

        # more bolt holes ( holes):
        if moreboltholes == 1: 
            #  ________________________________________
            # | O            O           O           O |
            # |........................................|
            # |o  ___  o:                  : :o  ___  o|
            # |  /   \  :   :<--------: \  : :  /   \  |
            # |  \___/  : O    O :  \___/  : :  \___/  |
            # |o_______o:________:o_______o:_:o_______o|

            # holes on the shorter side
            pos_bolt = pos + bolt_pos_top_n + shor_sp_c_vec
            shp_bolt = fcfun.shp_cylcenxtr (r= bolt_r, h = thick,
                                                normal = nfro_ax_n,
                                                ch=0, xtr_top=1, xtr_bot=1,
                                                pos = pos_bolt)
            holes_list.append(shp_bolt)
            pos_bolt = ( pos + bolt_pos_top_n + shor_sp_c_vec +
                             DraftVecUtils.scale(ntop_ax,20))
            shp_bolt = fcfun.shp_cylcenxtr (r= bolt_r, h = thick,
                                                normal = nfro_ax_n,
                                                ch=0, xtr_top=1, xtr_bot=1,
                                                pos = pos_bolt)
            holes_list.append(shp_bolt)

            # holes on the larger side
 
            pos_bolt = pos + bolt_pos_top_n + larg_sp_c_vec
            shp_bolt = fcfun.shp_cylcenxtr (r= bolt_r, h = thick,
                                                normal = nfro_ax_n,
                                                ch=0, xtr_top=1, xtr_bot=1,
                                                pos = pos_bolt)
            holes_list.append(shp_bolt)
            pos_bolt = ( pos + bolt_pos_top_n + larg_sp_c_vec +
                             DraftVecUtils.scale(ntop_ax,20))
            shp_bolt = fcfun.shp_cylcenxtr (r= bolt_r, h = thick,
                                                normal = nfro_ax_n,
                                                ch=0, xtr_top=1, xtr_bot=1,
                                                pos = pos_bolt)
            holes_list.append(shp_bolt)
            # holes on the larger side
                                                
            pos_bolt = (pos + bolt_pos_top_n + larg_sp_c_vec +
                             DraftVecUtils.scale(nsid_ax,20))
            shp_bolt = fcfun.shp_cylcenxtr (r= bolt_r, h = thick,
                                                normal = nfro_ax_n,
                                                ch=0, xtr_top=1, xtr_bot=1,
                                                pos = pos_bolt)
            holes_list.append(shp_bolt)
            pos_bolt = ( pos + bolt_pos_top_n + larg_sp_c_vec +
                             DraftVecUtils.scale(nsid_ax,20) +
                             DraftVecUtils.scale(ntop_ax,20))
            shp_bolt = fcfun.shp_cylcenxtr (r= bolt_r, h = thick,
                                                normal = nfro_ax_n,
                                                ch=0, xtr_top=1, xtr_bot=1,
                                                pos = pos_bolt)
            holes_list.append(shp_bolt)


            # holes on the larger side
                                                
            pos_bolt = (pos + bolt_pos_top_n + larg_sp_c_vec +
                             DraftVecUtils.scale(nsid_ax,-15))
            shp_bolt = fcfun.shp_cylcenxtr (r= bolt_r, h = thick,
                                                normal = nfro_ax_n,
                                                ch=0, xtr_top=1, xtr_bot=1,
                                                pos = pos_bolt)
            holes_list.append(shp_bolt)
            pos_bolt = ( pos + bolt_pos_top_n + larg_sp_c_vec +
                             DraftVecUtils.scale(nsid_ax,-15) +
                             DraftVecUtils.scale(ntop_ax,20))
            shp_bolt = fcfun.shp_cylcenxtr (r= bolt_r, h = thick,
                                                normal = nfro_ax_n,
                                                ch=0, xtr_top=1, xtr_bot=1,
                                                pos = pos_bolt)
            holes_list.append(shp_bolt)


            

        
            

        shp_holes = fcfun.fuseshplist(holes_list)
        shp_plate = shp_box.cut(shp_holes)


        doc = FreeCAD.ActiveDocument
        fco_plate =  doc.addObject("Part::Feature", name) 
        fco_plate.Shape = shp_plate
        self.fco = fco_plate

    def color (self, color = (1,1,1)):
        self.fco.ViewObject.ShapeColor = color

    # exports the shape to STL format
    def export_stl (self, name = ""):
        if not name:
            name = self.name
        #stlPath = filepath + "/freecad/stl/"
        stlPath = filepath + stl_dir
        stlFileName = stlPath + name + ".stl"
        #print (stlFileName)
        # exportStl is not working well with FreeCAD 0.17
        #self.fco.Shape.exportStl(stlFileName)
        mesh_shp = MeshPart.meshFromShape(self.fco.Shape,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp.write(stlFileName)
        del mesh_shp


                           

#doc = FreeCAD.newDocument()
#Plate3CageCubes(d_cagecube = kcomp_optic.CAGE_CUBE_60,
#                thick = 5,
#                cube_dist_n = 120,
#                cube_dist_p = 80,
#                top_h = 10,
#                cube_face = 'rodscrews',#which side of the cube faces the plate
#                hole_d = 0, 
#                boltatt_n = 6,
#                boltatt_d = 3+TOL,
#                fc_fro_ax = VX,
#                fc_top_ax = VZ,
#                fc_sid_ax = VY,
#                pos = V0,
#                name = 'Plate3CageCubes')

class hallestop_holder (object):


    def __init__(self,
                 stp_w = 21.,
                 stp_h = 31.,
                 base_thick = 4.,
                 sup_thick = 4.,
                 bolt_base_d = 3, #metric of the bolt 
                 bolt_sup_d = 3, #metric of the bolt
                 bolt_sup_sep = 17.,
                 alu_rail_l = 5,
                 stp_rail_l = 5,
                 xtr_bolt_head = 3,
                 xtr_bolt_head_d = 0,
                 reinforce = 1,
                 base_min_dist = 1,
                 fc_perp_ax = VZ,
                 fc_lin_ax = VX,
                 pos = V0,
                 wfco=1,
                 name = 'holder'):

        doc = FreeCAD.ActiveDocument
        self.name = name
        # bolt lin dimensions
        boltli_dict = kcomp.D912[bolt_base_d]
        boltlihead_r = boltli_dict['head_r']
        boltlihead_r_tol = boltli_dict['head_r_tol']
        boltlishank_r_tol = boltli_dict['shank_r_tol']
        boltlihead_l = boltli_dict['head_l']
        if bolt_sup_d == 0:
            bolt_sup_d = bolt_lin_d
        boltpe_dict = kcomp.D912[bolt_sup_d]
        boltpehead_r = boltpe_dict['head_r']
        boltpehead_r_tol = boltpe_dict['head_r_tol']
        boltpeshank_r_tol = boltpe_dict['shank_r_tol']
        boltpehead_l = boltpe_dict['head_l']

        boltmaxhead_r = max(boltlihead_r, boltpehead_r)
        boltmaxhead_r_tol = max(boltlihead_r_tol, boltpehead_r_tol)

        # normalize axis, just in case:
        axis_perp = DraftVecUtils.scaleTo(fc_perp_ax,1)
        axis_lin = DraftVecUtils.scaleTo(fc_lin_ax,1)
        axis_perp_neg = axis_perp.negative()
        axis_lin_neg = axis_lin.negative()
        axis_wid   = axis_perp.cross(axis_lin)

        #Calculate the length of the sup_l
        #         sup_thick :boltpehead_l
        #                  :  : : boltlihead_r
        #              ....:__: :  :
        #              :   |  |_   :
        # sup_h        +   |  |_| _:_
        #              :   |  |__|___|___ 
        #              :...|_____________|
        #                  :.......:
        #                 bolt1li_dist = sup_thick+boltpehead_l+boltlihead_r
        #                          :  :  :
        #                        2 x boltlihead_r
        #                  :.............:
        #                      + sup_l

        if base_min_dist == 0:
            bolt1li_dist = (  sup_thick + boltpehead_l + boltlihead_r_tol
                        + xtr_bolt_head )
            sup_l = bolt1li_dist + 2 * boltlihead_r + alu_rail_l
        else: 
            bolt1li_dist = ( sup_thick + boltlihead_r_tol
                        + xtr_bolt_head +kcomp.TOL)
            sup_l = bolt1li_dist + 0.8*boltlihead_r + alu_rail_l

        tot_w = max(stp_w + 2 * boltpehead_r, 8 * boltlihead_r) + 2 * reinforce


        #              ....:__: :  :           _________
        #              :   |  |_   :          ||       ||
        #   su_h       +   |  |_| _:_         ||   O   ||
        #              :   |  |__|___|___     ||_______||
        #              :...|_____________|    |___:_:___|......axis_wid
        #                  :.............:    :.........:
        #                    + sup_l             + tot_w

        sup_h = 2*boltpehead_r + base_thick + stp_rail_l

        shp_box = fcfun.shp_box_dir (box_w = tot_w,
                                     box_d = sup_l,
                                     box_h = sup_h,
                                     fc_axis_h = axis_perp,
                                     fc_axis_d = axis_lin,
                                     cw = 1, cd = 0, ch = 0,
                                     pos = pos)

        chmf_out_r = min(sup_l-sup_thick, sup_h-base_thick)

        chmf_out_pos = (   pos + DraftVecUtils.scaleTo(axis_lin, sup_l)
                         + DraftVecUtils.scaleTo(axis_perp, sup_h))

        shp_box = fcfun.shp_filletchamfer_dirpt(shp_box,
                                                   fc_axis = axis_wid,
                                                   fc_pt = chmf_out_pos,
                                                   fillet = 0,
                                                   radius = chmf_out_r)

        #                                       inside_w
        #                                       ...+...
        #              ....:__: :  :           :_______:
        #              :   |  |_   :          ||       ||
        #        sup_h +   |  |_| _:_         ||   O   ||
        #              :   |  |__|___|___     ||_______||
        #              :...|_____________|    |___:_:___|
        #                  :.............:    :.........:
        #                    + sup_l             + tot_w
        # cut the box inside
        # Inside width
        # add one, to have it a minimum of one mm
        if (reinforce > 0 and
           (tot_w > 2*(boltmaxhead_r + kcomp.TOL) + 1 )):
            inside_w =  tot_w - 2 * reinforce
            #print ("inside width " + str(inside_w))
        else:
            #no space for reinforcement, or reinforcement 0
            inside_w = tot_w + 2 # +2 to make the cut

        # chamfer of the inside box
        chmf_in_r = boltpehead_r
        logger.debug ("chamfer radius" + str(chmf_in_r))

        # inside box:
        insbox_pos = ( pos + DraftVecUtils.scale(axis_lin,sup_thick)
                           + DraftVecUtils.scale(axis_perp,base_thick))
        shp_insbox = fcfun.shp_box_dir (box_w = inside_w,
                                     box_d = sup_l,
                                     box_h = sup_h,
                                     fc_axis_h = axis_perp,
                                     fc_axis_d = axis_lin,
                                     cw = 1, cd = 0, ch = 0,
                                     pos = insbox_pos)
        if chmf_in_r > 0 :
            shp_insbox = fcfun.shp_filletchamfer_dirpt(shp_insbox,
                                                     fc_axis = axis_wid,
                                                     fc_pt = insbox_pos,
                                                     fillet = 0,
                                                     radius = chmf_in_r)
        #Part.show(shp_insbox)
        shp_box = shp_box.cut(shp_insbox)

        #pos_boltpe =  pos + DraftVecUtils.scale(axis_perp,sup_h/2.) 
        #shp_boltpe= fcfun.shp_cylcenxtr(r=boltshank_r_tol,
        #                    h=brack_thick,
        #                    normal = axis_lin,
        #                    ch = 0, xtr_top = 1, xtr_bot=1,
        #                    pos = pos_boltpe)

        boltholes = []
        for pos_wi in [ DraftVecUtils.scale(axis_wid,-bolt_sup_sep/2.),
                        DraftVecUtils.scale(axis_wid,bolt_sup_sep/2.)]:
            pos_boltpe =  (pos
                     + DraftVecUtils.scale(axis_perp,
                                           base_thick +(sup_h-base_thick)/2.)
                     + DraftVecUtils.scale(axis_lin,sup_thick+boltpehead_l)
                     + pos_wi)
            shp_boltpe = fcfun.shp_2stadium_dir(
                               length = stp_rail_l,
                               r_s = boltpeshank_r_tol,
                               #r_l =  boltpehead_r_tol + xtr_bolt_head_d/2.,
                               r_l =  boltpehead_r + xtr_bolt_head_d/2.,
                               h_tot = sup_thick + boltpehead_l,
                               h_rl = boltpehead_l,
                               fc_axis_h = axis_lin_neg,
                               fc_axis_l = axis_perp,
                               ref_l = 1, #ref on the circle center
                               rl_h0 = 1, #bolt head is on pos
                               xtr_h = 1,
                               xtr_nh = 1,
                               pos = pos_boltpe)
            boltholes.append(shp_boltpe)

        pos_boltli =  pos + DraftVecUtils.scale(axis_lin,bolt1li_dist) 
        #pos_wi_sca = tot_w/2. -2*boltlihead_r - reinforce
        pos_wi_sca = bolt_sup_sep/2.
        for pos_wi in  [ DraftVecUtils.scale(axis_wid,-pos_wi_sca),
                        DraftVecUtils.scale(axis_wid,pos_wi_sca)]:
            # 2 Stadium to cut the chamfer if it is too big
            pos_boltli_top = (pos_boltli
                         + DraftVecUtils.scale(axis_perp, sup_h) 
                         + pos_wi)
            shp_railli = fcfun.shp_2stadium_dir (length = alu_rail_l,
                               r_s = boltlishank_r_tol,
                               r_l = boltlihead_r_tol + kcomp.TOL/2., #extra TOL
                               h_tot = sup_h,
                               h_rl = sup_h-base_thick,
                               fc_axis_h = axis_perp_neg,
                               fc_axis_l = axis_lin,
                               ref_l = 2, #ref on the circle center
                               rl_h0 = 1, #bolt head is on pos
                               xtr_h = 1,
                               xtr_nh = 1,
                               pos = pos_boltli_top)
            boltholes.append(shp_railli)

        shp_boltfuse = fcfun.fuseshplist(boltholes)

        shp_bracket = shp_box.cut(shp_boltfuse)
        doc.recompute()
        shp_bracket =shp_bracket.removeSplitter()
        doc.recompute()

        self.shp = shp_bracket
        self.wfco = wfco
        if wfco == 1:
            # a freeCAD object is created
            fco_bracket = doc.addObject("Part::Feature", name )
            fco_bracket.Shape = shp_bracket
            self.fco = fco_bracket

    def color (self, color = (1,1,1)):
        if self.wfco == 1:
            self.fco.ViewObject.ShapeColor = color
        else:
            logger.debug("Bracket object with no fco")
        
    # exports the shape into stl format
    def export_stl (self, name = ""):
        #filepath = os.getcwd()
        if not name:
            name = self.name
        stlPath = filepath + "/stl/"
        stlFileName = stlPath + name + ".stl"

        # exportStl is not working well with FreeCAD 0.17
        #self.shp.exportStl(stlFileName)
        mesh_shp = MeshPart.meshFromShape(self.shp,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp.write(stlFileName)
        del mesh_shp

       
#doc = FreeCAD.newDocument()

#hs = hallestop_holder ( 
#                 stp_w = 21.,
#                 stp_h = 31.,
#                 base_thick = 4.,
#                 sup_thick = 5.,
#                 bolt_base_d = 3, #metric of the bolt 
#                 bolt_sup_d = 3, #metric of the bolt
#                 bolt_sup_sep = 17.,
#                 alu_rail_l = 10,
#                 stp_rail_l = 20,
#                 xtr_bolt_head = 0,
#                 xtr_bolt_head_d = 0,
#                 base_min_dist = 1,
#                 reinforce = 4,
#                 fc_perp_ax = VZ,
#                 fc_lin_ax = VX,
#                 pos = V0,
#                 wfco=1,
#                 name = 'holder')


#hs = hallestop_holder ( 
#                 stp_w = 21.,
#                 stp_h = 31.,
#                 base_thick = 3.,
#                 sup_thick = 3.,
#                 bolt_base_d = 3, #metric of the bolt 
#                 bolt_sup_d = 3, #metric of the bolt
#                 bolt_sup_sep = 17.,
#                 alu_rail_l = 7,
#                 stp_rail_l = 5,
#                 xtr_bolt_head = 0,
#                 xtr_bolt_head_d = 0,
#                 base_min_dist = 1,
#                 reinforce = 2,
#                 fc_perp_ax = VZ,
#                 fc_lin_ax = VX,
#                 pos = V0,
#                 wfco=1,
#                 name = 'holder')


#hs = hallestop_holder ( 
#                 stp_w = 21.,
#                 stp_h = 31.,
#                 base_thick = 3.,
#                 sup_thick = 3.,
#                 bolt_base_d = 3, #metric of the bolt 
#                 bolt_sup_d = 3, #metric of the bolt
#                 bolt_sup_sep = 17.,
#                 alu_rail_l = 10,
#                 stp_rail_l = 10,
#                 xtr_bolt_head = 0,
#                 xtr_bolt_head_d = 0,
#                 base_min_dist = 1,
#                 reinforce = 4,
#                 fc_perp_ax = VZ,
#                 fc_lin_ax = VX,
#                 pos = V0,
#                 wfco=1,
#                 name = 'holder')


# for the optical sensor CNY70 and TR
class sensor_holder (object):


    def __init__(self,
                 sensor_support_length = 10.,
                 sensor_pin_sep = 2.54,
                 sensor_pin_pos_h = 3,
                 sensor_pin_pos_w = 2,
                 sensor_pin_r_tol = 1.05,
                 sensor_pin_rows = 6,
                 sensor_pin_cols = 6,
                 #sensor_clip_pos_h = 2.45, #position from center
                 #sensor_clip_h_tol = 1.28,
                 #sensor_clip_w_tol = 1.,
                 base_height = 37., # height of the cd case
                 base_width = 20., # width of the cd case
                 flap_depth = 8.,
                 flap_thick = 2.,
                 base_thick = 2., #la altura
                 basesensor_thick = 9., #la altura de la parte de los sensores
                 pos = V0,
                 axis_h = VZ,
                 axis_d = VX,
                 axis_w = VY,
                 wfco=1,
                 name = 'holder'):

        axis_h = DraftVecUtils.scaleTo(axis_h,1)
        axis_d = DraftVecUtils.scaleTo(axis_d,1)
        axis_w = DraftVecUtils.scaleTo(axis_w,1)

        axis_h_n = DraftVecUtils.scaleTo(axis_h,-1)
        axis_d_n = DraftVecUtils.scaleTo(axis_d,-1)
        axis_w_n = DraftVecUtils.scaleTo(axis_w,-1)

        TOL = 0.4
        base_h = base_height + TOL;
        shp_list = []
        shp_base = fcfun.shp_box_dir_xtr(box_w=base_width,
                                     box_d=base_thick,
                                     box_h=base_h,
                                     fc_axis_h=axis_h,
                                     fc_axis_d=axis_d,
                                     fc_axis_w=axis_w_n,
                                     cw=0,cd=0,ch=0,
                                     xtr_h=1, xtr_nh=1,pos=V0)
        shp_list.append(shp_base)

        sup_sensor_w = (sensor_pin_cols ) * sensor_pin_sep + sensor_pin_pos_w
        sup_sensor_h = (sensor_pin_rows ) * sensor_pin_sep + sensor_pin_pos_h
        pos_sup_sensor = ( V0 + DraftVecUtils.scale(axis_d_n,
                              basesensor_thick-base_thick))
        shp_sup_sensor = fcfun.shp_box_dir_xtr(
                                     box_w=sup_sensor_w,
                                     box_d=basesensor_thick,
                                     box_h=sup_sensor_h,
                                     fc_axis_h=axis_h,
                                     fc_axis_d=axis_d,
                                     fc_axis_w=axis_w,
                                     cw=0,cd=0,ch=0,
                                     xtr_h=0, xtr_nw=1,pos=pos_sup_sensor)
        shp_list.append(shp_sup_sensor)

        shp_top_flap = fcfun.shp_box_dir_xtr(
                                     box_w=base_width,
                                     box_d=flap_depth,
                                     box_h=flap_thick,
                                     fc_axis_h=axis_h,
                                     fc_axis_d=axis_d_n,
                                     fc_axis_w=axis_w_n,
                                     cw=0,cd=0,ch=0,
                                     xtr_h=0, xtr_nd=base_thick,
                                     pos=FreeCAD.Vector(0,0,base_h))
        shp_list.append(shp_top_flap)

        shp_bot_flap = fcfun.shp_box_dir_xtr(
                                     box_w=base_width,
                                     box_d=flap_depth,
                                     box_h=flap_thick,
                                     fc_axis_h=axis_h_n,
                                     fc_axis_d=axis_d_n,
                                     fc_axis_w=axis_w_n,
                                     cw=0,cd=0,ch=0,
                                     xtr_h=0, xtr_nd=base_thick,
                                     pos=V0)
        shp_list.append(shp_bot_flap)

        pos_hole_w = sensor_pin_pos_w 
        holes_list =[]
        for w_i in range (sensor_pin_cols):
            pos_hole_h = sensor_pin_pos_h 
            for h_i in range (sensor_pin_rows):
                pos_pin = (pos_sup_sensor 
                              + DraftVecUtils.scale(axis_w, pos_hole_w)
                              + DraftVecUtils.scale(axis_h, pos_hole_h))
                shp_pin_hole = fcfun.shp_cylcenxtr(r=sensor_pin_r_tol,
                                     h = basesensor_thick,
                                     normal = axis_d,
                                     ch=0, xtr_top = 1,xtr_bot=1,
                                     pos = pos_pin)
                pos_hole_h = pos_hole_h + sensor_pin_sep
                holes_list.append(shp_pin_hole)
            pos_hole_w = pos_hole_w + sensor_pin_sep

        shp_holes = fcfun.fuseshplist(holes_list)
        shp_solid = fcfun.fuseshplist(shp_list)
        shp_final = shp_solid.cut(shp_holes)
        shp_final = shp_final.removeSplitter()
        
        fco_sensor_holder = FreeCAD.ActiveDocument.addObject("Part::Feature", name )
        fco_sensor_holder.Shape = shp_final
        
 
#sensor_holder()
