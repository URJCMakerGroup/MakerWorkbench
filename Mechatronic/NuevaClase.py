import FreeCAD
import Part
import DraftVecUtils

import os
import sys
import math
import inspect
import logging

import fcfun
import kcomp

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Obj3D (object):
    """ This is the the basic class, that provides reference axes and 
    methods to get positions

    It is the parent class of other classes, no instantiation of this class

    These objects have their own coordinate axes:
    axis_d: depth
    axis_w: width
    axis_h: height

    They have an origin point pos_o (created in a child class)
    and have different interesting points
    d_o
    w_o
    h_o

    and methods to get to them

    pos_o_adjustment : FreeCAD.Vector
        if not V0 indicates that shape has not been placed at pos_o, so the FreeCAD object
        will need to be placed at pos_o_adjust

    This object could be a FreeCAD Object or not
    fco: FreeCAD Object
        if fco = 1 create FreeCAD Object
        if fco = 0 not FreeCAD Object
            
    """
    def __init__(self, axis_d = None, axis_w = None, axis_h = None, name = None):
        # the TopoShape has an origin, and distance vectors from it to 
        # the different points along the coordinate system  
        self.d_o = {}  # along axis_d
        self.w_o = {}  # along axis_w
        self.h_o = {}  # along axis_h

        self.dict_child = {} # dict of child 
        self.dict_child_sum = {} # dict of child add
        self.dict_child_res = {} # dict of child remove

        self.parts_lst = [] # list of all the parts

        self.rel_place = V0
        self.extra_mov = V0

        self.name = name

        self.doc = FreeCAD.ActiveDocument

        if axis_h is not None:
            axis_h = DraftVecUtils.scaleTo(axis_h,1)
        else:
            self.h_o[0] = V0
            self.pos_h = 0
            axis_h = V0
        self.axis_h = axis_h

        if axis_d is not None:
            axis_d = DraftVecUtils.scaleTo(axis_d,1)
        else:
            self.d_o[0] = V0
            self.pos_d = 0
            axis_d = V0
        self.axis_d = axis_d

        if axis_w is not None:
            axis_w = DraftVecUtils.scaleTo(axis_w,1)
        else:
            self.w_o[0] = V0
            self.pos_w = 0
            axis_w = V0
        self.axis_w = axis_w

        self.pos_o_adjust = V0

    def vec_d(self, d):
        """ creates a vector along axis_d (depth) with the length of argument d

        Returns a FreeCAD.Vector

        Parameter:
        ----------
        d : float
            depth: lenght of the vector along axis_d
        """

        # self.axis_d is normalized, so no need to use DraftVecUtils.scaleTo
        vec_d = DraftVecUtils.scale(self.axis_d, d)
        return vec_d


    def vec_w(self, w):
        """ creates a vector along axis_w (width) with the length of argument w

        Returns a FreeCAD.Vector

        Parameter:
        ----------
        w : float
            width: lenght of the vector along axis_w
        """

        # self.axis_w is normalized, so no need to use DraftVecUtils.scaleTo
        vec_w = DraftVecUtils.scale(self.axis_w, w)
        return vec_w


    def vec_h(self, h):
        """ creates a vector along axis_h (height) with the length of argument h

        Returns a FreeCAD.Vector

        Parameter:
        ----------
        h : float
            height: lenght of the vector along axis_h
        """

        # self.axis_h is normalized, so no need to use DraftVecUtils.scaleTo
        vec_h = DraftVecUtils.scale(self.axis_h, h)
        return vec_h

    def vec_d_w_h(self, d, w, h):
        """ creates a vector with:
            depth  : along axis_d
            width  : along axis_w
            height : along axis_h

        Returns a FreeCAD.Vector

        Parameters:
        ----------
        d, w, h : float
            depth, widht and height
        """

        vec = self.vec_d(d) + self.vec_w(w) + self.vec_h(h)
        return vec

    def set_pos_o(self, adjust=0):
        """ calculates the position of the origin, and saves it in
        attribute pos_o
        Parameters:
        -----------
        adjust : int
             1: If, when created, wasnt possible to set the piece at pos_o,
                and it was placed at pos, then the position will be adjusted
        """

        vec_from_pos_o =  (  self.get_o_to_d(self.pos_d)
                           + self.get_o_to_w(self.pos_w)
                           + self.get_o_to_h(self.pos_h))
        vec_to_pos_o =  vec_from_pos_o.negative()
        self.pos_o = self.pos + vec_to_pos_o
        if adjust == 1:
            self.pos_o_adjust = vec_to_pos_o # self.pos_o - self.pos

    def get_o_to_d(self, pos_d):
        """ returns the vector from origin pos_o to pos_d
        If it is symmetrical along axis_d, pos_d == 0 will be at the middle
        Then, pos_d > 0 will be the points on the positive side of axis_d
        and   pos_d < 0 will be the points on the negative side of axis_d

          d0_cen = 1
                :
           _____:_____
          |     :     |   self.d_o[1] is the vector from orig to -1
          |     :     |   self.d_o[0] is the vector from orig to 0
          |_____:_____|......> axis_d
         -2 -1  0  1  2

         o---------> A:  o to  1  :
         o------>    B:  o to  0  : d_o[0]
         o--->       C:  o to -1  : d_o[1]
         o    -->    D: -1 to  0  : d_o[0] - d_o[1] : B - C
                     A = B + D
                     A = B + (B-C) = 2B - C

        d0_cen = 0
          :
          :___________
          |           |   self.d_o[1] is the vector from orig to 1
          |           |
          |___________|......> axis_d
          0  1  2  3  4

        """
        abs_pos_d = abs(pos_d)
        if self.d0_cen == 1:
            if pos_d <= 0: 
                try:
                    vec = self.d_o[abs_pos_d]
                except KeyError:
                    logger.error('pos_d key not defined ' + str(pos_d))
                else:
                    return vec
            else:
                try:
                    vec_0_to_d = (self.d_o[0]).sub(self.d_o[pos_d]) # D= B-C
                except KeyError:
                    logger.error('pos_d key not defined ' + str(pos_d))
                else:
                    vec_orig_to_d = self.d_o[0] + vec_0_to_d # A = B + D
                    return vec_orig_to_d
        else: #pos_d == 0 is at the end, distances are calculated directly
            try:
                vec = self.d_o[pos_d]
            except KeyError:
                logger.error('pos_d key not defined' + str(pos_d))
            else:
                return vec

    def get_o_to_w(self, pos_w):
        """ returns the vector from origin pos_o to pos_w
        If it is symmetrical along axis_w, pos_w == 0 will be at the middle
        Then, pos_w > 0 will be the points on the positive side of axis_w
        and   pos_w < 0 will be the points on the negative side of axis_w
        See get_o_to_d drawings
        """
        abs_pos_w = abs(pos_w)
        if self.w0_cen == 1:
            if pos_w <= 0:
                try:
                    vec = self.w_o[abs_pos_w]
                except KeyError:
                    logger.error('pos_w key not defined ' + str(pos_w))
                else:
                    return vec
            else:
                try:
                    vec_0_to_w = (self.w_o[0]).sub(self.w_o[pos_w]) # D= B-C
                except KeyError:
                    logger.error('pos_w key not defined ' + str(pos_w))
                else:
                    vec_orig_to_w = self.w_o[0] + vec_0_to_w # A = B + D
                    return vec_orig_to_w
        else: #pos_w == 0 is at the end, distances are calculated directly
            try:
                vec = self.w_o[pos_w]
            except KeyError:
                logger.error('pos_w key not defined' + str(pos_w))
            else:
                return vec

    def get_o_to_h(self, pos_h):
        """ returns the vector from origin pos_o to pos_h
        If it is symmetrical along axis_h, pos_h == 0 will be at the middle
        Then, pos_h > 0 will be the points on the positive side of axis_h
        and   pos_h < 0 will be the points on the negative side of axis_h
        See get_o_to_d drawings
        """
        abs_pos_h = abs(pos_h)
        if self.h0_cen == 1:
            if pos_h <= 0:
                try:
                    vec = self.h_o[abs_pos_h]
                except KeyError:
                    logger.error('pos_h key not defined ' + str(pos_h))
                else:
                    return vec
            else:
                try:
                    vec_0_to_h = (self.h_o[0]).sub(self.h_o[pos_h]) # D= B-C
                except KeyError:
                    logger.error('pos_h key not defined ' + str(pos_h))
                else:
                    vec_orig_to_h = self.h_o[0] + vec_0_to_h # A = B + D
                    return vec_orig_to_h
        else: #pos_h == 0 is at the end, distances are calculated directly
            try:
                vec = self.h_o[pos_h]
            except KeyError:
                logger.error('pos_h key not defined' + str(pos_h))
            else:
                return vec

    def get_d_ab(self, pta, ptb):
        """ returns the vector along axis_d from pos_d = pta to pos_d = ptb
        """
        vec = self.get_o_to_d(ptb).sub(self.get_o_to_d(pta))
        return vec

    def get_w_ab(self, pta, ptb):
        """ returns the vector along axis_h from pos_w = pta to pos_w = ptb
        """
        vec = self.get_o_to_w(ptb).sub(self.get_o_to_w(pta))
        return vec

    def get_h_ab(self, pta, ptb):
        """ returns the vector along axis_h from pos_h = pta to pos_h = ptb
        """
        vec = self.get_o_to_h(ptb).sub(self.get_o_to_h(pta))
        return vec


    def get_pos_d(self, pos_d):
        """ returns the absolute position of the pos_d point
        """
        return self.pos_o + self.get_o_to_d(pos_d)

    def get_pos_w(self, pos_w):
        """ returns the absolute position of the pos_w point
        """
        return self.pos_o + self.get_o_to_w(pos_w)

    def get_pos_h(self, pos_h):
        """ returns the absolute position of the pos_h point
        """
        return self.pos_o + self.get_o_to_h(pos_h)

    def get_pos_dwh(self, pos_d, pos_w, pos_h):
        """ returns the absolute position of the pos_d, pos_w, pos_h point
        """
        pos = (self.pos_o + self.get_o_to_d(pos_d)
                          + self.get_o_to_w(pos_w)
                          + self.get_o_to_h(pos_h))
        return pos

    def set_name (self, name = '', default_name = '', change = 0):
        """ Sets the name attribute to the value of parameter name
        if name is empty, it will take default_name.
        if change == 1, it will change the self.name attribute to name, 
            default_name
        if change == 0, if self.name is not empty, it will preserve it

        Parameters:
        -----------
        name : str
            This is the name, but it can be empty.
        default_name : str
            This is the default_name, if not name
        change : int
            1: change the value of self.name
            0: preserve the value of self.name if it exists

        """
        # attribute name has not been created
        if (not hasattr(self, 'name') or  # attribute name has not been created
            not self.name or              # attribute name is empty
            change == 1):                 # attribute has to be changed
            if name == None:
                self.name = default_name
            else:
                self.name = name
    
    def create_fco (self, name = None):
        """ creates a FreeCAD object of the TopoShape in self.shp

        Parameters:
        -----------
        name : str
            it is optional if there is a self.name

        """
        if not name:
            name = self.name
        
        fco = fcfun.add_fcobj(self.shp, name, self.doc)
        self.fco = fco
        # logger.info('Created the fco '+ name)

        try:
            self.fco.addProperty("Part::PropertyPartShape","Shape",name, "Shape of the object",1)
            self.fco.Shape = self.shp
        except:
            logger.warning('No se puede asignar la propiedad shape')

        try:
            self.fco.addProperty("App::PropertyVector","axis_d",name,"Internal axis d",4).axis_d = self.axis_d
        except:
            logger.warning('Error al asignar la propiedad axis d')

        try: 
            self.fco.addProperty("App::PropertyVector","axis_w",name,"Internal axis w",4).axis_w = self.axis_w
        except:
            logger.warning('Error al asignar la propiedad axis w')

        try:
            self.fco.addProperty("App::PropertyVector","axis_h",name,"Internal axis h",4).axis_h = self.axis_h
        except:
            logger.warning('Error al asignar la propiedad axis h')

        try:
            self.fco.addProperty("App::PropertyInteger","d0_cen",name,"Points d_o are symmetrics",4).d0_cen = self.d0_cen
        except:
            logger.warning('Error al asignar la propiedad d0_cen')

        try:
            self.fco.addProperty("App::PropertyInteger","w0_cen",name,"Points w_o are symmetrics",4).w0_cen = self.w0_cen
        except:
            logger.warning('Error al asignar la propiedad w0_cen')

        try:
            self.fco.addProperty("App::PropertyInteger","h0_cen",name,"Points h_o are symmetrics",4).h0_cen = self.h0_cen
        except:
            logger.warning('Error al asignar la propiedad h0_cen')

        try:
            self.fco.addProperty("App::PropertyVectorList","d_o",name,"Points o to d",4).d_o = self.d_o
        except:
            logger.warning('Error al asignar la propiedad d_o')

        try:
            self.fco.addProperty("App::PropertyVectorList","w_o",name,"Points o to w",4).w_o = self.w_o
        except:
            logger.warning('Error al asignar la propiedad w_o')

        try:
            self.fco.addProperty("App::PropertyVectorList","h_o",name,"Points o to h",4).h_o = self.h_o
        except:
            logger.warning('Error al asignar la propiedad h_o')

        # try: #TODO: Furute line of the proyect. Add childs propertys to the father. This doesn't make sense if the children don't have points to import
        #     self.fco.addProperty("App::PropertyStringList","childs",name,"List of childs",4).childs = self.dict_child.keys()
        #     try:
        #         for key in self.dict_child:
        #             self.fco.addProperty("App::PropertyFloatList",key + "_d_o",name,"Points o to d of " + key,4)# = self.dict_child[key]['child_d_o']
        #     except:
        #         logger.warning('Error al asignar la propiedad child_d_o')
        # except:
        #     logger.warning('Error al asignar la propiedad childs')
        # 
        # try:
        #     self.fco.addProperty("App::PropertyStringList","childs_sum",name,"List of childs add",4).childs_sum = self.dict_child_sum.keys()
        # except:
        #     logger.warning('Error al asignar la propiedad childs_sum')
        # 
        # try:
        #     self.fco.addProperty("App::PropertyStringList","childs_res",name,"List of childs res",4).childs_res = self.dict_child_res.keys()
        # except:
        #     logger.warning('Error al asignar la propiedad childs_res')

    def add_child(self, child, child_sum = 1, child_name = None):
        """ add child with their features
        child_sum:
            1: the child adds volume to the model
            0: the child removes volume from the model
        """
            
        # Create a dictionary for each child trhat is added with key data

        try: # TODO: Furute line of the proyect. Improve the child dictionary and usability 
            self.dict_child[child_name] = dict(child_d_o = child.d_o, child_w_o = child.w_o, child_h_o = child.h_o, child_shp = child.shp)
        except AttributeError:
            self.dict_child[child_name] = dict(child_d_o = None, child_w_o = None, child_h_o = None, child_shp = child)
            # logger.warning('Child has no points atributes')

        if child_sum == 1:
            self.dict_child_sum[child_name] = self.dict_child[child_name]
        else:
            self.dict_child_res[child_name] = self.dict_child[child_name]
                
    def get_child(self):
        """ returns a dict of childs, could be an empty dict.
        """
        return self.dict_child
        
    def make_parent(self, name):
        if len(self.dict_child) == 0:
            pass
        else:
            if len(self.dict_child_sum) == 0 and len(self.dict_child_res) == 0:
                pass
            else:
                shp_sum_list = []
                shp_res_list = []
                for key in self.dict_child_sum:
                    # listar todos los volumenes a sumar
                    shp_sum_list.append(self.dict_child[key]['child_shp'])

                for key in self.dict_child_res:

                    # listar todos los volumenes a restar
                    shp_res_list.append(self.dict_child[key]['child_shp'])

                shp_sum = fcfun.fuseshplist(shp_sum_list)
                shp_res = fcfun.fuseshplist(shp_res_list)
                # restar a los volumenes a sumar los volumenes a restar
                self.shp = shp_sum.cut(shp_res)
                return self

    def append_part (self, part):
        """ Appends a new part to the list of parts
        """
        self.parts_lst.append(part)

    def get_parts (self):
        """ get a list of the parts, 
        """
        return self.parts_lst
        
    def make_group (self):
        self.fco = self.doc.addObject("Part::Compound", self.name)
        list_fco = []
        parts = []
        part_list = self.get_parts()
        for part in part_list:
            parts.append
            try:
                fco_i = part.fco
            except AttributeError:
                logger.error('part is not a single part or compound')
            else:
                list_fco.append(fco_i)
                parts.append(fco_i.Name)
        self.fco.Links = list_fco
        self.doc.recompute()

    def set_part_place(self, child_part, vec_o_to_childpart = V0, add = 0):
        """ Modifies the attribute child_part.place, which defines the
        displacement of the child_part respect to self.pos_o
        Adds this displacement to the part's children
        """
        
        rel_place = self.pos_o_adjust + vec_o_to_childpart
        if add == 0:
            child_part.rel_place = rel_place
        else:
            child_part.rel_place = child_part.rel_place + rel_place
        child_part.fco.Placement.Base = child_part.rel_place
        
    def place_fcos (self, displacement = V0):
        """ Place the freecad objects
        
        """
        #if type(place) is tuple:
        #   place = FreeCAD.Vector(place) # change to FreeCAD.Vector
        
        tot_displ = (  self.pos_o_adjust + displacement
                     + self.rel_place + self.extra_mov)
        self.tot_displ = tot_displ
        for part in self.parts_lst:
            if hasattr(part, 'fco') == True:
                tot_displ = (  part.pos_o_adjust + displacement
                             + part.rel_place + part.extra_mov)
                part.tot_displ = tot_displ
                part.fco.Placement.Base = part.tot_displ
            elif hasattr(part, 'parts_lst') == True:
                for part_in_part in part.parts_lst:
                    tot_displ = (  part_in_part.pos_o_adjust + displacement
                                 + part_in_part.rel_place + part_in_part.extra_mov)
                    part_in_part.tot_displ = tot_displ
                    part_in_part.fco.Placement.Base = part_in_part.tot_displ
            else:
                logger.warning('No attribute fco')

                
        # self.fco.Placement.Base = tot_displ

class ShpCylHole (Obj3D):
    """
    Creates a shape of a hollow cylinder
    Similar to fcfun shp_cylhole_gen, but creates the object with the useful
    attributes and methods
    Makes a hollow cylinder in any position and direction, with optional extra
    heights, and inner and outer radius, and various locations in the cylinder

    Parameters:
    -----------
    r_out : float
        radius of the outside cylinder
    r_in : float
        radius of the inner hole of the cylinder
    h : float
        height of the cylinder
    axis_h : FreeCAD.Vector
        vector along the cylinder height
    axis_d : FreeCAD.Vector
        vector along the cylinder radius, a direction perpendicular to axis_h
        it is not necessary if pos_d == 0
        It can be None, but if None, axis_w has to be None
    axis_w : FreeCAD.Vector
        vector along the cylinder radius,
        a direction perpendicular to axis_h and axis_d
        it is not necessary if pos_w == 0
        It can be None
    pos_h : int
        location of pos along axis_h (0, 1)
        0: the cylinder pos is centered along its height, not considering
           xtr_top, xtr_bot
        1: the cylinder pos is at its base (not considering xtr_h)
    pos_d : int
        location of pos along axis_d (0, 1)
        0: pos is at the circunference center
        1: pos is at the inner circunsference, on axis_d, at r_in from the
           circle center (not at r_in + xtr_r_in)
        2: pos is at the outer circunsference, on axis_d, at r_out from the
           circle center (not at r_out + xtr_r_out)
    pos_w : int
        location of pos along axis_w (0, 1)
        0: pos is at the circunference center
        1: pos is at the inner circunsference, on axis_w, at r_in from the
           circle center (not at r_in + xtr_r_in)
        2: pos is at the outer circunsference, on axis_w, at r_out from the
           circle center (not at r_out + xtr_r_out)
    xtr_top : float
        Extra height on top, it is not taken under consideration when
        calculating the cylinder center along the height
    xtr_bot : float
        Extra height at the bottom, it is not taken under consideration when
        calculating the cylinder center along the height or the position of
        the base
    xtr_r_in : float
        Extra length of the inner radius (hollow cylinder),
        it is not taken under consideration when calculating pos_d or pos_w.
        It can be negative, so this inner radius would be smaller
    xtr_r_out : float
        Extra length of the outer radius
        it is not taken under consideration when calculating pos_d or pos_w.
        It can be negative, so this outer radius would be smaller
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes:
    -----------
    pos_o : FreeCAD.Vector
        Position of the origin of the shape
    h_o : dictionary of FreeCAD.Vector
        vectors from the origin to the different points along axis_h
    d_o : dictionary of FreeCAD.Vector
        vectors from the origin to the different points along axis_d
    w_o : dictionary of FreeCAD.Vector
        vectors from the origin to the different points along axis_w
    h0_cen : int
    d0_cen : int
    w0_cen : int
        indicates if pos_h = 0 (pos_d, pos_w) is at the center along
        axis_h, axis_d, axis_w, or if it is at the end.
        1 : at the center (symmetrical, or almost symmetrical)
        0 : at the end
    shp : OCC Topological Shape
        The shape of this part


    pos_h = 1, pos_d = 0, pos_w = 0
    pos at 1:
            axis_w
              :
              :
             . .    
           . . . .
         ( (  0  ) ) ---- axis_d
           . . . .
             . .    

           axis_h
              :
              :
          ...............
         :____:____:....: xtr_top
         | :     : |
         | :     : |
         | :     : |
         | :  0  : |     0: pos would be at 0, if pos_h == 0
         | :     : |
         | :     : |
         |_:__1__:_|....>axis_d
         :.:..o..:.:....: xtr_bot        This o will be pos_o (orig)
         : :  :
         : :..:
         :  + :
         :r_in:
         :    :
         :....:
           +
          r_out
         

    Values for pos_d  (similar to pos_w along it axis)


           axis_h
              :
              :
          ...............
         :____:____:....: xtr_top
         | :     : |
         | :     : |
         | :     : |
         2 1  0  : |....>axis_d    (if pos_h == 0)
         | :     : |
         | :     : |
         |_:_____:_|.....
         :.:..o..:.:....: xtr_bot        This o will be pos_o (orig)
         : :  :
         : :..:
         :  + :
         :r_in:
         :    :
         :....:
           +
          r_out

    """
    def __init__(self,
                 r_out, r_in, h,
                 axis_h = VZ, axis_d = None, axis_w = None,
                 pos_h = 0, pos_d = 0, pos_w = 0,
                 xtr_top=0, xtr_bot=0,
                 xtr_r_out=0, xtr_r_in=0,
                 pos = V0,
                 name = None):


        Obj3D.__init__(self, axis_d, axis_w, axis_h, name)
        
        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

        # THIS IS WORKING, but it seems that the signs are not right
        # vectors from o (orig) along axis_h, to the pos_h points
        # h_o is a dictionary created in Obj3D.__init__
        self.h_o[0] =  self.vec_h(h/2. + xtr_bot)
        self.h_o[1] =  self.vec_h(xtr_bot)
        # pos_h = 0 is at the center
        self.h0_cen = 1

        self.d_o[0] = V0
        if self.axis_d is not None:
            self.d_o[1] = self.vec_d(-r_in)
            self.d_o[2] = self.vec_d(-r_out)
        elif pos_d != 0:
            logger.error('axis_d not defined while pos_d != 0')
        # pos_d = 0 is at the center
        self.d0_cen = 1

        self.w_o[0] = V0
        if self.axis_w is not None:
            self.w_o[1] = self.vec_w(-r_in)
            self.w_o[2] = self.vec_w(-r_out)
        elif pos_w != 0:
            logger.error('axis_w not defined while pos_w != 0')
        # pos_w = 0 is at the center
        self.w0_cen = 1

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        shpcyl = fcfun.shp_cylholedir (r_out = r_out + xtr_r_out, #ext radius
                                       r_in  = r_in + xtr_r_in, #internal radius
                                       h     = h+xtr_bot+xtr_top, # height
                                       normal= self.axis_h,       # direction
                                       pos   = self.pos_o)        # Position

        self.shp = shpcyl
        self.prnt_ax = self.axis_h

class ShpBolt (Obj3D):
    """
    Creates a shape of a Bolt
    Similar to fcfun.shp_bolt_dir, but creates the object with the useful
    attributes and methods
    Makes a bolt with various locations and head types
    It is an approximate model. The thread is not made, it is just a little
    smaller just to see where it is

    Parameters:
    -----------
    shank_r : float
        radius of the shank
    shank_l : float
        length of the bolt, not including the head (different from shp_bolt_dir)
    head_r : float
        radius of the head, it it hexagonal, radius of the cirumradius
    head_l : float
        length of the head
    thread_l : float
        length of the shank that is threaded
        if 0: all the shank is threaded
    head_type : int
        0: round (cylinder). Default
        1: hexagonal
    socket_l : float
        depth of the hex socket, if 0, no hex socket
    socket_2ap : float
        socket: 2 x apotheme (usually S in the dimensinal drawings)
        Iit is the wrench size, the diameter would be 2*apotheme / cos30
        It is not the circumdiameter
        if 0: no hex socket
    shank_out : float
        0: default
        distance to the end of the shank, just for positioning, it doesnt
        change shank_l
        I dont think it is necessary, but just in case
    head_out : float
        0: default
        distance to the end of the head, just for positioning, it doesnt
        change head_l
        I dont think it is necessary, but just in case
    axis_h : FreeCAD.Vector
        vector along the axis of the bolt, pointing from the head to the shank
    axis_d : FreeCAD.Vector
        vector along the radius, a direction perpendicular to axis_h
        If the head is hexagonal, the direction of one vertex
    axis_w : FreeCAD.Vector
        vector along the cylinder radius,
        a direction perpendicular to axis_h and axis_d
        it is not necessary if pos_w == 0
        It can be None
    pos_h : int
        location of pos along axis_h
        0: top of the head, considering head_out,
        1: position of the head not considering head_out
           if head_out = 0, it will be the same as pos_h = 0
        2: end of the socket, if no socket, will be the same as pos_h = 0
        3: union of the head and the shank
        4: where the screw starts, if all the shank is screwed, it will be
           the same as pos_h = 2
        5: end of the shank, not considering shank_out
        6: end of the shank, if shank_out = 0, will be the same as pos_h = 5
        6: top of the head, considering xtr_head_l, if xtr_head_l = 0
           will be the same as pos_h = 0
    pos_d : int
        location of pos along axis_d (symmetric)
        0: pos is at the central axis
        1: radius of the shank
        2: radius of the head
    pos_w : int
        location of pos along axis_d (symmetric)
        0: pos is at the central axis
        1: radius of the shank
        2: radius of the head
    pos : FreeCAD.Vector
        Position of the bolt, taking into account where the pos_h, pos_d, pos_w
        are

    Attributes:
    -----------
    pos_o : FreeCAD.Vector
        Position of the origin of the shape

    self.tot_l : float
        Total length of the bolt: head_l + shank_l
    shp : OCC Topological Shape
        The shape of this part



                                   axis_h
                                     :
                                     : shank_r
                                     :+
                                     : :
                                     : :
                     ....6......... _:_:...................
           shank_out+....5.........| : |    :             :
                                   | : |    + thread_l    :
                                   | : |    :             :
                                   | : |    :             :
                                   | : |    :             + shank_l
                         4         |.:.|....:             :
                                   | : |                  :
                         3       __| : |__................:
                                |    :    |               :
                         2      |  ..:..  |...            + head_l
                      ...1......|  : : :  |  :+socket_l   :
             head_out+...0......|__:_:_:__|..:......:.....:.... axis_d
                                     0 1  2 
                                     :    :
                                     :....:
                                        + head_r


    """
    def __init__(self,
                 shank_r,
                 shank_l,
                 head_r,
                 head_l,
                 thread_l = 0,
                 head_type = 0, # cylindrical. 1: hexagonal
                 socket_l = 0,
                 socket_2ap = 0,
                 shank_out = 0,
                 head_out = 0,
                 axis_h = VZ, axis_d = None, axis_w = None,
                 pos_h = 0, pos_d = 0, pos_w = 0,
                 pos = V0,
                 name = None):


        Obj3D.__init__(self, axis_d, axis_w, axis_h, name)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

        self.h0_cen = 0
        self.d0_cen = 1 # symmetrical
        self.w0_cen = 1 # symmetrical

        self.tot_l = head_l + shank_l

        # vectors from o (orig) along axis_h, to the pos_h points
        # h_o is a dictionary created in Obj3D.__init__
        self.h_o[0] =  V0 #origin
        self.h_o[1] =  self.vec_h(head_out)
        self.h_o[2] =  self.vec_h(socket_l)
        self.h_o[3] =  self.vec_h(head_l)
        self.h_o[4] =  self.vec_h(self.tot_l - thread_l)
        self.h_o[5] =  self.vec_h(self.tot_l - shank_out)
        self.h_o[6] =  self.vec_h(self.tot_l)

        self.d_o[0] = V0
        if not (self.axis_d is None or self.axis_d == V0):
            # negative because is symmetric
            self.d_o[1] = self.vec_d(-shank_r)
            self.d_o[2] = self.vec_d(-head_r)
        elif pos_d != 0:
            logger.error('axis_d not defined while pos_d != 0')
        # pos_d = 0 is at the center

        self.w_o[0] = V0
        if not (self.axis_w is None or self.axis_w == V0):
            # negative because is symmetric
            self.w_o[1] = self.vec_w(-shank_r)
            self.w_o[2] = self.vec_w(-head_r)
        elif pos_w != 0:
            logger.error('axis_w not defined while pos_w != 0')
        # pos_w = 0 is at the center

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        if head_type == 0: # cylindrical
            shp_head = fcfun.shp_cylcenxtr (r = head_r, h = head_l,
                                  normal = self.axis_h,
                                  ch=0, # not centered
                                  # no extra on top, the shank will be there
                                  xtr_top = 0,
                                  xtr_bot = 0,
                                  pos = self.pos_o)

        else: # hexagonal
            if (self.axis_d is None) or (self.axis_d == V0):
                logger.error('axis_d need to be defined')
            else:
                shp_head = fcfun.shp_regprism_dirxtr (
                                  n_sides = 6, radius = head_r,
                                  length = head_l,
                                  fc_normal = self.axis_h,
                                  fc_verx1 = self.axis_d,
                                  centered=0,
                                  # no extra on top, the shank will be there
                                  xtr_top = 0, xtr_bot = 0,
                                  pos = self.pos_o)

        if socket_l > 0 and socket_2ap > 0 : # there is socket
            # diameter of the socket (circumdiameter)
            self.cos30 = 0.86603
            self.socket_dm = socket_2ap / self.cos30
            self.socket_r = self.socket_dm / 2.
            if (self.axis_d is None) or (self.axis_d == V0):
                # just make an axis_d
                self.axis_d = fcfun.get_fc_perpend1(self.axis_h)

            shp_socket = fcfun.shp_regprism_dirxtr (
                                  n_sides = 6, radius = self.socket_r,
                                  length = socket_l,
                                  fc_normal = self.axis_h,
                                  fc_verx1 = self.axis_d,
                                  centered=0,
                                  xtr_top = 0, xtr_bot = 1, #to cut
                                  pos = self.pos_o)
            shp_head = shp_head.cut(shp_socket)
            

        if thread_l == 0 or thread_l >= shank_l: #all the shank is threaded
            shp_shank = fcfun.shp_cylcenxtr (r = shank_r, h = shank_l,
                                             normal = self.axis_h,
                                             ch=0, # not centered
                                             xtr_top = 0,
                                             xtr_bot = head_l/2., #to make union
                                             pos = self.get_pos_h(3))
        else : # not threaded shank plus threaded, but just a little smaller
            # to see the line
            shp_shank = fcfun.shp_cylcenxtr (r = shank_r, h = shank_l-thread_l,
                                             normal = self.axis_h,
                                             ch=0, # not centered
                                             xtr_top = 0,
                                             xtr_bot = head_l/2., #to make union
                                             pos = self.get_pos_h(3))
            shp_thread = fcfun.shp_cylcenxtr (r = shank_r-0.1,
                                              h = thread_l,
                                              normal = self.axis_h,
                                              ch=0, # not centered
                                              xtr_top = 0,
                                              xtr_bot = 1, #to make union
                                              pos = self.get_pos_h(4))

            shp_shank = shp_shank.fuse(shp_thread)





        shp_bolt = shp_head.fuse(shp_shank)

        self.shp = shp_bolt
        # no axis would be good to print, and it is not a piece to print
        # however, this would be the best
        self.prnt_ax = self.axis_h 

class ShpPrismHole (Obj3D):
    """
    Creates a shape of a hollow prism
    Similar to fcfun shp_regprism_dirxtr, but creates the object with the useful
    attributes and methods
    Makes a hollow prism in any position and direction, with different positions
    heights, and inner and outer radius, and various locations in the cylinder

    Parameters:
    -----------
    n_sides : int
        number of sides of the polygon
    r_out : float
        circumradius of the polygon
    h : float
        total height of the cylinder
    r_in : float
        radius of the inner hole
        if 0, no inner hole
    h_offset : float
        0: default
        Distance from the top, just to place the prism, see pos_h
        if negative, from the bottom
    xtr_r_in : float
        Extra length of the inner radius (hollow cylinder),
        it is not taken under consideration when calculating pos_d or pos_w.
        It can be negative, so this inner radius would be smaller
    xtr_r_out : float
        Extra length of the circumradius
        it is not taken under consideration when calculating pos_d or pos_w.
        It can be negative, so this outer radius would be smaller
    axis_d_apo : int
        0: default: axis_d points to the vertex
        1: axis_d points to the center of a side
    axis_h : FreeCAD.Vector
        vector along the cylinder height
    axis_d : FreeCAD.Vector
        vector along the first vertex, a direction perpendicular to axis_h
        it is not necessary if pos_d == 0
        It can be None, but if None, axis_w has to be None
    axis_w : FreeCAD.Vector
        vector along the cylinder radius,
        a direction perpendicular to axis_h and axis_d
        it is not necessary if pos_w == 0
        It can be None
    pos_h : int
        location of pos along axis_h
         0: at the center
        -1: at the base
         1: at the top
        -2: at the base + h_offset
         2: at the top + h_offset
    pos_d : int
        location of pos along axis_d (-2, -1, 0, 1, 2)
        0: pos is at the circunference center (axis)
        1: pos is at the inner circunsference, on axis_d, at r_in from the
           circle center (not at r_in + xtr_r_in)
        2: pos is at the apothem, on axis_d
        3: pos is at the outer circunsference, on axis_d, at r_out from the
           circle center (not at r_out + xtr_r_out)
    pos_w : int
        location of pos along axis_w (-2, -1, 0, 1, 2)
        0: pos is at the circunference center
        1: pos is at the inner circunsference, on axis_w, at r_in from the
           circle center (not at r_in + xtr_r_in)
        2: pos is at the apothem, on axis_w
        3: pos is at the outer circunsference, on axis_w, at r_out from the
           circle center (not at r_out + xtr_r_out)
    pos : FreeCAD.Vector
        Position of the prism, taking into account where the center is

    Attributes:
    -----------
    pos_o : FreeCAD.Vector
        Position of the origin of the shape
    h_o : dictionary of FreeCAD.Vector
        vectors from the origin to the different points along axis_h
    d_o : dictionary of FreeCAD.Vector
        vectors from the origin to the different points along axis_d
    w_o : dictionary of FreeCAD.Vector
        vectors from the origin to the different points along axis_w
    h0_cen : int
    d0_cen : int
    w0_cen : int
        indicates if pos_h = 0 (pos_d, pos_w) is at the center along
        axis_h, axis_d, axis_w, or if it is at the end.
        1 : at the center (symmetrical, or almost symmetrical)
        0 : at the end
    shp : OCC Topological Shape
        The shape of this part


            __:__ 
           /     \ 
          /  / \  \........axis_d     
          \  \ /  / 
           \____ / 

              01 23  pos_d

           axis_h
              :
              :
          ____:____ ....            1
         : :     : :    : h_offset
         : :     : :....:           2
         | :     : |
         | :     : |
         | :  o  : |                0 This o will be pos_o (orig)
         | :     : |
         | :     : |.....          -2
         | :     : |    : off_set
         :_:_____:_:....: bot_out  -1  .....> axis_d
         : :  :    
         : :..:
         :  + :
         :r_in:
         :    :
         :....:
           +
          r_out
         


    """
    def __init__(self, n_sides,
                 r_out, h, r_in,
                 h_offset = 0,
                 xtr_r_in = 0,
                 xtr_r_out = 0,
                 axis_d_apo = 0,
                 axis_h = VZ, axis_d = None, axis_w = None,
                 pos_h = 0, pos_d = 0, pos_w = 0,
                 pos = V0,
                 name = None):


        Obj3D.__init__(self, axis_d, axis_w, axis_h, name)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

        self.h0_cen = 1 # symmetric
        # vectors from o (orig) along axis_h, to the pos_h points
        # h_o is a dictionary created in Obj3D.__init__
        self.h_o[0] =  V0
        self.h_o[1] =  self.vec_h(-h/2.)
        self.h_o[2] =  self.vec_h(-h/2. + h_offset)

        # apotheme
        self.apo = r_out * math.cos(math.pi/n_sides)
        self.d_o[0] = V0
        if self.axis_d != V0:
            # not considering the extra radius (usually tolerances)
            self.d_o[1] = self.vec_d(-r_in)
            self.d_o[2] = self.vec_d(-self.apo)
            self.d_o[3] = self.vec_d(-r_out)
        else:
            if pos_d != 0:
                logger.error('axis_d not defined while pos_d != 0')
            self.axis_d = fcfun.get_fc_perpend1(self.axis_h)
        # pos_d = 0 is at the center
        self.d0_cen = 1

        self.w_o[0] = V0
        if self.axis_w != V0:
            self.w_o[1] = self.vec_w(-r_in)
            self.w_o[2] = self.vec_w(-self.apo)
            self.w_o[3] = self.vec_w(-r_out)
        elif pos_w != 0:
            logger.error('axis_w not defined while pos_w != 0')
        # pos_w = 0 is at the center
        self.w0_cen = 1

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        if axis_d_apo == 0:
            self.axis_apo = self.axis_d
        else: # rotate 360/(2*nsides)
            self.axis_apo = DraftVecUtils.rotate(self.axis_d, math.pi/n_sides,
                                                 self.axis_h)

        shp_prism = fcfun.shp_regprism_dirxtr(n_sides = n_sides,
                                              radius = r_out + xtr_r_out,
                                              length = h,
                                              fc_normal = self.axis_h,
                                              fc_verx1 = self.axis_apo,
                                              centered = 0,
                                              pos=self.get_pos_h(-1))
        if r_in > 0:
            shp_cyl = fcfun.shp_cylcenxtr (r       = r_in + xtr_r_in,
                                           h       = h,
                                           normal  = self.axis_h,
                                           ch      = 0,
                                           xtr_top = 1, # to cut
                                           xtr_bot = 1, # to cut
                                           pos     = self.get_pos_h(-1))
            self.shp = shp_prism.cut(shp_cyl)
        else :
            self.shp = shp_prism
        self.prnt_ax = self.axis_h

####################################################################################
# Ejemplo de funcionamiento

class placa(Obj3D):

    def __init__(self, L_d = 10, L_w = 10, L_h = 2, axis_d = VX, axis_w = VY, axis_h = VZ, name = 'placa base'):
        """
            d_o[0] d_o[1]  d_o[2]
            :      :       :
            :____________:... h_o[2]
            |            |... h_o[1]
            |____________|... h_o[0]
           o
             ____________ ... w_o[2]
            |            |
            |            |... w_o[1]
            |            |
            |____________|... w_o[0]
           o
        """
        self.shp = fcfun.shp_boxcen(L_d, L_w, L_h, cx= False, cy=False, cz=False, pos=V0)
        self.name = name
        self.axis_d = axis_d
        self.axis_h = axis_h
        self.axis_w = axis_w

        Obj3D.__init__(self, self.axis_d , self.axis_w , self.axis_h, self.name)

        self.d_o[0] = 0
        self.d_o[1] = L_d/2
        self.d_o[2] = L_d
        
        self.w_o[0] = 0
        self.w_o[1] = L_w/2
        self.w_o[2] = L_w
        
        self.h_o[0] = 0
        self.h_o[1] = L_h/2
        self.h_o[2] = L_h

        #Obj3D.create_fco(self, name)
class hole(Obj3D):
    def __init__(self, r = None, h = None, axis_d = VX, axis_w = VY, axis_h = VZ, pos = V0, name = None):
        self.shp = fcfun.shp_cyl(r, h, axis_h, pos)
        self.name = name
        self.axis_d = axis_d
        self.axis_h = axis_h
        self.axis_w = axis_w

        Obj3D.__init__(self, self.axis_d , self.axis_w , self.axis_h, self.name)

        self.d_o[0] = 0
        self.d_o[1] = r/2
        self.d_o[2] = r
        
        self.w_o[0] = 0
        self.w_o[1] = r/2
        self.w_o[2] = r
        
        self.h_o[0] = 0
        self.h_o[1] = h/2
        self.h_o[2] = h

class placa_perforada(Obj3D):
    """
        d_o[0] d_o[1]  d_o[2]
        :      :       :
        :____________:... h_o[2]
        |     : :    |... h_o[1]
        |_____:_:____|... h_o[0]
        o
         ____________ ... w_o[2]
        |            |
        |      O     |... w_o[1]
        |            |
        |____________|... w_o[0]
        o
    """
    def __init__(self, d, w, h, r, name = 'placa perforada'):
        
        self.axis_d = VX
        self.axis_w = VY
        self.axis_h = VZ
        self.name = name
        
        Obj3D.__init__(self, self.axis_d , self.axis_w , self.axis_h , self.name)
        
        self.d_o[0] = 0
        self.d_o[1] = d/2
        self.d_o[2] = d
        
        self.w_o[0] = 0
        self.w_o[1] = w/2
        self.w_o[2] = w
        
        self.h_o[0] = 0
        self.h_o[1] = h/2
        self.h_o[2] = h
        
        # añadimos el hijo 1, añadiendo volumen
        placa_ = placa(d,w,h)
        Obj3D.add_child(self, placa_, 1, 'placa') 
        
        # añadimos el hijo 2, quitando volumen
        hole_ = hole(r, h+0.1, axis_d = VX, axis_w = VY, axis_h = VZ, pos = FreeCAD.Vector(self.d_o[1],self.w_o[1],self.h_o[0]))
        Obj3D.add_child(self, hole_, 0, 'hole')
        # creamos al padre
        Obj3D.make_parent(self, name)
        # creamos el fco
        Obj3D.create_fco(self, name)

class placa_tornillos(Obj3D):
    """
        d_o[0] d_o[2]  d_o[4]
        :  d_o[1]  d_o[3]
        :__:___:___:_:... h_o[2]
        | ::      :: |... h_o[1]
        |_::______::_|... h_o[0]
        o
         ____________ ... w_o[4]
        | o        o |... w_o[3]
        |            |... w_o[2]
        |            |... w_o[1]
        |_o________o_|... w_o[0]
        o
    """
    def __init__(self, d, w, h, r, name = 'placa tornillos'):
        axis_d = VX
        axis_w = VY
        axis_h = VZ

        Obj3D.__init__(self, axis_d , axis_w , axis_h , name)
        
        self.d_o[0] = 0
        self.d_o[1] = 2*r
        self.d_o[2] = d/2
        self.d_o[3] = d - 2*r
        self.d_o[4] = d
        
        self.w_o[0] = 0
        self.w_o[1] = 2*r
        self.w_o[2] = w/2
        self.w_o[3] = w - 2*r
        self.w_o[4] = w
        
        self.h_o[0] = 0
        self.h_o[1] = h/2
        self.h_o[2] = h
        
        # añadimos el hijo 1, añadiendo volumen
        Obj3D.add_child(self, placa(d,w,h),1, 'placa') 
        # añadimos el hijo 2, quitando volumen
        Obj3D.add_child(self, hole(r, h+0.1, axis_d = VX, axis_w = VY, axis_h = VZ, pos = FreeCAD.Vector(self.d_o[1],self.w_o[1],self.h_o[0])), 0, 'tornillo1')
        # añadimos el hijo 3, quitando volumen
        Obj3D.add_child(self, hole(r, h+0.1, axis_d = VX, axis_w = VY, axis_h = VZ, pos = FreeCAD.Vector(self.d_o[1],self.w_o[3],self.h_o[0])), 0, 'tornillo2')
        # añadimos el hijo 4, quitando volumen
        Obj3D.add_child(self, hole(r, h+0.1, axis_d = VX, axis_w = VY, axis_h = VZ, pos = FreeCAD.Vector(self.d_o[3],self.w_o[3],self.h_o[0])), 0, 'tornillo3')
        # añadimos el hijo 5, quitando volumen
        Obj3D.add_child(self, hole(r, h+0.1, axis_d = VX, axis_w = VY, axis_h = VZ, pos = FreeCAD.Vector(self.d_o[3],self.w_o[1],self.h_o[0])), 0, 'tornillo4')
        # creamos al padre
        Obj3D.make_parent(self, name)
        # creamos el fco
        Obj3D.create_fco(self, name)