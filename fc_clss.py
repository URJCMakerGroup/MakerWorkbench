# ----------------------------------------------------------------------------
# -- Classes for FreeCAD pieces, parts, part sets
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- https://github.com/felipe-m/fcad-comps
# -- December-2017
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

import os
import sys
import inspect
import logging
import math
import FreeCAD
import FreeCADGui
import Part
import DraftVecUtils
import Mesh
import MeshPart

# to get the current directory. Freecad has to be executed from the same
# directory this file is
filepath = os.getcwd()
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath) 
#sys.path.append(filepath + '/' + 'comps')
sys.path.append(filepath + '/../../' + 'comps')


import kcomp   # import material constants and other constants
import fcfun   # import my functions for freecad. FreeCad Functions
import shp_clss
import kparts

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Possible names: Single Part, Element, Piece
# Either:
# - have an attribute to indicate what kind of part is it, or
# - have subclasses to indicate the kind of part that it is
#
# Kind of possible parts are:
# 0: Not to print: It is just an outline, a rough/vague 3D model,
#                  for example bolts or bearings
#                  Some times the models dont have details, for example,
#                  bearings are just cylinders with a inner hole. Or bolts
#                  that dont have threads
# 0?: Not to print: It can be an exact model, like a washer, but it is not to
#                  print, tolerances are not inluced
# 1: Dimensional model: it can be printed to assemble a model, but the part
#                       will not work as defined. For example, optical cubes
#                       that they just have the dimmensions, but they dont
#                       have the inner holes or the threads for the bolts
# 2: Printable model: it can be printed, but better to buy it,
#                     the printed part may work well.
#                     washer. You can print it, but better get it
# 3: To be printed: an object designed to be printed

# exact. Not to print because it has no tolerances
# with tolerances (to be printed)
# rough


class SinglePart (object):
    """
    This is a 3D model that only has one part.
    It can be either a part that forms a whole object with other parts, 
    or just a piece that can be used standalone 
    This is a Parent Class of all kind of objects
    
    All the pieces have 3 axis that define their 3 main perpendicular directions
    Depth, Width, Height

    Attributes
    ------------
    fco: FreeCAD Object
        The freecad object of this part

    place : FreeCAD Object
        When this part is an object of another one (set). This is the vector to
        place this part into the the set

    place : FreeCAD.Vector
        Position of the object
        There is the parameter pos, where the piece is built and can be at
        any position.
        Once the piece is built, its placement (Placement.Base) is at V0:
        FreeCAD.Vector(0,0,0), however it can be located at any place, since
        pos could have been set anywhere.
        The attribute place will move again the whole piece, including its parts

    color : Tuple of 3 floats, each of them from 0. to 1.
        They define the RGB colors.
        0.: no color on that channel
        1.: full intesity on that channel

    """
    def __init__(self):
        # bring the active document
        self.doc = FreeCAD.ActiveDocument

        # placement of the piece at V0, altough pos can set it anywhere
        self.place = V0   #check this and rel_place
        #self.displacement = V0
        self.rel_place = V0
        self.extra_mov = V0

        self.create_fco(self.name)
        #self.tol = tol
        #self.model_type = model_type

    def get_parts(self):
        """ returns an empty list, because it is a SinglePart.
        Therefore has no parts
        """
        return []

    def set_color (self, color = (1.,1.,1.)):
        """ Sets a new color for the piece

        Parameters
        -----------
        color : tuple of 3 floats from 0. to 1.
            RGB colors

        """
        # just in case the value is 0 or 1, and it is an int
        self.color = (float(color[0]),float(color[1]), float(color[2]))
        self.fco.ViewObject.ShapeColor = self.color

    def set_line_color (self, color = (1.,1.,1.)):
        """ Sets a new color for the vertex lines of the piece

        Parameters
        -----------
        color : tuple of 3 floats from 0. to 1.
            RGB colors

        """
        # just in case the value is 0 or 1, and it is an int
        self.line_color = (float(color[0]),float(color[1]), float(color[2]))
        self.fco.ViewObject.LineColor = self.line_color


    def set_line_width (self, width = 1.):
        """ Sets the line width of the vertexes

        Parameters
        -----------
        width : float from 0. to 1.

        """
        # just in case the value is 0 or 1, and it is an int
        self.line_width = float(width)
        self.fco.ViewObject.LineWidth = self.line_width


    def set_point_size (self, size = 1.):
        """ Sets the point size

        Parameters
        -----------
        size : float
            it seems it goes from 1. up to 64

        """
        self.point_size = size
        self.fco.ViewObject.PointSize = self.point_size


    def set_name (self, name = '', default_name = '', change = 0):
        """ Sets the name attribute to the value of parameter name
        if name is empty, it will take default_name.
        if change == 1, it will change the self.name attribute to name, 
            default_name
        if change == 0, if self.name is not empty, it will preserve it

        Parameters
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
            change == 1):                 # attribute has te be changed
            if not name:
                self.name = default_name
            else:
                self.name = name

    def create_fco (self, name = ''):
        """ creates a FreeCAD object of the TopoShape in self.shp

        Parameters
        -----------
        name : str
            it is optional if there is a self.name

        """
        if not name:
            name = self.name
        fco = fcfun.add_fcobj(self.shp, name, self.doc)
        self.fco = fco


    # ----- 
    def place_fcos (self, displacement = V0):
        """ Place the freecad objects
        
        """
        #if type(place) is tuple:
        #   place = FreeCAD.Vector(place) # change to FreeCAD.Vector
        
        tot_displ = (  self.pos_o_adjust + displacement
                     + self.rel_place + self.extra_mov)
        self.tot_displ = tot_displ
        self.fco.Placement.Base = tot_displ
    
    def set_place (self, place = V0):
        """ Sets a new placement for the piece

        Parameters
        -----------
        place : FreeCAD.Vector
            new position of the pieces
        """
        if type(place) is tuple:
            place = FreeCAD.Vector(place) # change to FreeCAD.Vector
        if type(place) is FreeCAD.Vector:
            self.fco.Placement.Base = place
            self.place = place

    # ----- Export to STL method
    def export_stl(self, prefix = "", name = "", stl_path = ""):
        """ exports to stl the piece to print 

        Parameters
        -----------
        prefix : str
            Prefix to the piece, may be useful if name is not given
            and want to add a prefix to the self.name
            an underscore will be added between prefix and name
        name : str
            Name of the piece, if not given, it will take self.name
        stl_path : the path to save the stl files
        """
        if not name:
            filename = self.name
        if prefix:
            filename = prefix + '_' + filename

        if not stl_path:
            stl_filename = filename + '.stl'
        else:
            stl_filename = stl_path + filename + '.stl'
        
        # I think this is a bug, before it may be called pos0, but
        # now should be pos_o
        pos_o = self.pos_o
        rotation = FreeCAD.Rotation(self.prnt_ax, VZ)
        shp = self.shp
        # ----------- moving the shape doesnt work:
        # I think that is because it is bound to a FreeCAD object
        #shp.Placement.Base = self.pos.negative() + self.place.negative()
        #shp.translate (self.pos.negative() + self.place.negative())
        #shp.rotate (V0, rotation.Axis, math.degrees(rotation.Angle))
        #shp.Placement.Base = self.place
        #shp.Placement.Rotation = fcfun.V0ROT
        # ----------- option 1. making a copy of the shape
        # and then deleting it (nullify)
        #shp_cpy = shp.copy()
        #shp_cpy.translate (pos_o.negative() + self.place.negative())
        #shp_cpy.rotate (V0, rotation.Axis, math.degrees(rotation.Angle))
        #shp_cpy.exportStl(stl_path + filename + 'stl')
        #shp_cpy.nullify()
        # ----------- option 2. moving the freecad object
        
        # place is no longer used, it should be rel_place or abs_place
        self.fco.Placement.Base = pos_o.negative() + self.place.negative()
        self.fco.Placement.Rotation = rotation
        self.doc.recompute()

        # exportStl is not working well with FreeCAD 0.17
        #self.fco.Shape.exportStl(self.stl_path + filename + '.stl')
        mesh_shp = MeshPart.meshFromShape(self.fco.Shape,
                                          LinearDeflection=kparts.LIN_DEFL, 
                                          AngularDeflection=kparts.ANG_DEFL)
        mesh_shp.write(stl_filename)
        del mesh_shp

        self.fco.Placement.Base = self.place
        self.fco.Placement.Rotation = V0ROT
        self.doc.recompute()

    def save_fcad(self, prefix = "", name = ""):
        """ Save the FreeCAD document, actually, it may not be a class method
        only for the name

        prefix : str
            Prefix to the piece, may be useful if name is not given
            and want to add a prefix to the self.name
            an underscore will be added between prefix and name
        name : str
            Name of the piece, if not given, it will take self.name
        """
        if not name:
            filename = self.name
        if prefix:
            filename = prefix + '_' + filename

        fcad_filename = self.fcad_path + name + '.FCStd'
        print(fcad_filename)
        self.doc.saveAs (fcad_filename)


# Possible names: Parts     , Pieces,         Elements,
#                      Group        Ensemble,         Set, 
class PartsSet (shp_clss.Obj3D):
    """
    This is a 3D model that has a set of parts (SinglePart or others)
    
    All the pieces have 3 axis that define their 3 main perpendicular directions
    Depth, Width, Height

    place : FreeCAD.Vector
        Position of the tensioner set.
        There is the parameter pos, where the piece is built and can be at
        any position.
        Once the piece is built, its placement (Placement.Base) is at V0:
        FreeCAD.Vector(0,0,0), however it can be located at any place, since
        pos could have been set anywhere.
        The attribute place will move again the whole piece, including its parts

    color : Tuple of 3 elements, each of them from 0 to 1
        They define the RGB colors.
        0: no color on that channel
        1: full intesity on that channel

    """

    def __init__(self, axis_d, axis_w, axis_h):
        
        # bring the active document
        self.doc = FreeCAD.ActiveDocument

        shp_clss.Obj3D.__init__(self, axis_d, axis_w, axis_h)

        self.parts_lst = [] # list of all the parts (SinglePart, ...)

        self.place = V0  # check these places, unify them
        self.abs_place = V0
        self.rel_place = V0
        self.extra_mov = V0
        self.displacement = V0

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
        part_list = self.get_parts()
        for part in part_list:
            try:
                fco_i = part.fco
            except AttributeError:
                logger.error('part is not a single part or compound')
            else:
                list_fco.append(fco_i)
        self.fco.Links = list_fco
        self.doc.recompute()
        
    def get_abs_place (self):
        """ gets the placement of the object, with any adjustment
        So the shape has been created at pos, and this is any movement done
        after this movement of the freecadobject
        """
        
        return self.abs_place

    def get_rel_place (self):
        """ gets the placement of the object, with any adjustment
        So the shape has been created at pos, and this is any movement done
        after this movement of the freecadobject
        """
        
        return self.rel_place

        
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
        #child_part.abs_place = self.get_abs_place() + child_part.rel_place
        #try:
        #    child_part.fco.Placement.Base = child_part.abs_place
        #except AttributeError: # only SimpleParts objects have fco,not PartsSet
        #    pass
        # add this displacement to all the children
        #part_list = child_part.get_parts()
        #for grandchild_i in part_list:
            #child_part.set_part_place(grandchild_i, add = 1)
        
        
    def mov_place(self, child_part, vec_o_to_childpart = V0):
        """ Modifies the attribute child_part.place, which defines the
        displacement of the child_part respect to self.pos_o
        Adds this displacement to the part's children
        """
        
        displacement = (self.pos_o - self.pos) + vec_o_to_childpart + self.place
        child_part.place = child_part.place + displacement
        try:
            child_part.fco.Placement.Base = child_part.place
        except AttributeError: # only SimpleParts objects have fco, not PartsSet
            pass
        # add this displacement to all the children
        part_list = child_part.get_parts()
        for grandchild_i in part_list:
            child_part.add_part_place(grandchild_i)
        
    def set_color (self, color = (1.,1.,1.), part_i = 0):
        """ Sets a new color for the whole set of parts or for the selected
        parts

        Parameters
        -----------
        color : tuple of 3 floats from 0. to 1.
            RGB colors
        part_i : int
            index of the part to change the color
            0: all the parts
            1... the index of the part

        """
        # just in case the value is 0 or 1, and it is an int
        color = (float(color[0]),float(color[1]), float(color[2]))
        if part_i == 0:
            self.color = color #only if all the parts have the same color
            for part in self.parts_lst:  # list of SinglePart objects
                part.set_color(color)
        else:
            self.parts_lst[part_i-1].set_color(color)

    # ----- 
    def place_fcos (self, displacement = V0):
        """ Place the freecad objects
        """
        #if type(place) is tuple:
        #   place = FreeCAD.Vector(place) # change to FreeCAD.Vector
        
        # having pos_o_adjust and rel_place made the sum twice
        #tot_displ = (  self.pos_o_adjust + displacement 
        tot_displ = (  displacement 
                     + self.rel_place + self.extra_mov)
        self.tot_displ = tot_displ
        #if this set has been grouped, we dont have to go to its children
        try:
            self.fco.Placement.Base = tot_displ
        except AttributeError:
            # Not grouped: set the new position for every freecad object
            for part in self.parts_lst:
                part.place_fcos(tot_displ)


    # ----- Export to STL method
    def export_stl(self, part_i = 0, prefix = ""):
        """ exports to stl the part or the parts to print
        Save them in a STL file

        Parameters
        -----------
        part_i : int
            index of the part to print
            0: all the printable parts
            1... index of the part

        prefix : str
            Prefix to all the parts
        """
        
        if part_i == 0: # export all the parts
            for part in self.parts_lst:
                part.export_stl(prefix = prefix)
        else:
            self.parts_lst[part_i-1].export_stl(prefix = prefix)


    def save_fcad(self, prefix = "", name = ""):
        """ Save the FreeCAD document, actually, it may not be a class method
        only for the name

        prefix : str
            Prefix to the name, may be useful if name is not given
            and want to add a prefix to the self.name
            an underscore will be added between prefix and name
        name : str
            Name of the part, if not given, it will take self.name
        """
        if not name:
            filename = self.name
        if prefix:
            filename = prefix + '_' + filename

        fcad_filename = self.fcad_path + name + '.FCStd'
        print(fcad_filename)
        self.doc.saveAs (fcad_filename)

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
            change == 1):                 # attribute has te be changed
            if not name:
                self.name = default_name
            else:
                self.name = name


class Washer (SinglePart, shp_clss.ShpCylHole):
    """ Washer, that is, a cylinder with a inner hole

    Parameters
    -----------
    r_out : float
        external (outside) radius
    r_in : float
        internal radius
    h : float
        height
    axis_h : FreeCAD.Vector
        vector along the cylinder height
    pos_h : int
        location of pos along axis_h (0,1)
        0: the cylinder pos is centered along its height
        1: the cylinder pos is at its base
    tol : float
        Tolerance for the inner and outer radius.
        Being an outline, probably it is not to print, so by default: tol = 0
        It is the tolerance for the diameter, so the radius will be added/subs
        have of this tolerance
        tol will be added to the inner radius (so it will be larger)
        tol will be substracted to the outer radius (so it will be smaller)
        
    model_type : int
        type of model:
        exact, outline
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes
    -----------
    All the parameters and attributes of parent classes SinglePart ShpCylHole

    metric : int or float (in case of M2.5) or even str for inches ?
        Metric of the washer

    """
    def __init__(self, r_out, r_in, h, axis_h, pos_h, tol = 0, pos = V0,
                 model_type = 0, # exact
                 name = ''):

        # sets the object name if not already set by a child class
        if not hasattr(self, 'metric'):
            self.metric = int(2 * r_in)
        default_name = 'washer' + str(self.metric)
        self.set_name (name, default_name, change = 0)

        tol_r = tol / 2.

        # First the shape is created
        shp_clss.ShpCylHole.__init__(self, r_out = r_out, r_in = r_in,
                                     h = h, axis_h = axis_h,
                                     pos_h = pos_h,
                                     # inside tolerance is more
                                     xtr_r_in = tol_r,
                                     # outside tolerance is less
                                     xtr_r_out = - tol_r,
                                     pos = pos)

        # Then the Part
        SinglePart.__init__(self)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])



class Din125Washer (Washer):
    """ Din 125 Washer, this is the regular washer

    Parameters
    -----------
    metric : int (maybe float: 2.5)
 
    axis_h : FreeCAD.Vector
        Vector along the cylinder height
    pos_h : int
        Location of pos along axis_h (0,1)
        
            * 0: the cylinder pos is at its base
            * 1: the cylinder pos is centered along its height

    tol : float
        Tolerance for the inner and outer radius.
        It is the tolerance for the diameter, so the radius will be added/subs
        have of this tolerance.

            * tol will be added to the inner radius (so it will be larger).
            * tol will be substracted to the outer radius (so it will be smaller).

    model_type : int
        Type of model:
        
            * 0: exact
            * 1: outline

    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Note
    ----
    All the parameters and attributes of father class CylHole

    Attributes
    -----------
    metric : int or float (in case of M2.5) or even str for inches ?
        Metric of the washer

    model_type : int
    """
    def __init__(self, metric, axis_h, pos_h, tol = 0, pos = V0,
                 model_type = 0, # exact
                 name = ''):

        # sets the object name if not already set by a child class
        self.metric = metric
        default_name = 'din125_washer_m' + str(self.metric)
        self.set_name (name, default_name, change = 0)

        washer_dict = kcomp.D125[metric]
        Washer.__init__(self,
                        r_out = washer_dict['do']/2.,
                        r_in = washer_dict['di']/2.,
                        h = washer_dict['t'],
                        axis_h = axis_h,
                        pos_h = pos_h,
                        tol = tol, pos = pos,
                        model_type = model_type)


class Din9021Washer (Washer):
    """ Din 9021 Washer, this is the larger washer

    Parameters
    -----------
    metric : int (maybe float: 2.5)
 
    axis_h : FreeCAD.Vector
        Vector along the cylinder height
    pos_h : int
        Location of pos along axis_h (0,1)
        
            * 0: the cylinder pos is at its base
            * 1: the cylinder pos is centered along its height

    tol : float
        Tolerance for the inner and outer radius.
        It is the tolerance for the diameter, so the radius will be added/subs
        have of this tolerance
            
            * tol will be added to the inner radius (so it will be larger)
            * tol will be substracted to the outer radius (so it will be smaller)

    model_type : int
        Type of model:
            
            * 0: exact
            * 1: outline

    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Note
    ----
    All the parameters and attributes of father class CylHole

    Attributes
    -----------
    metric : int or float (in case of M2.5) or even str for inches ?
        Metric of the washer

    model_type : int
    """
    def __init__(self, metric, axis_h, pos_h, tol = 0, pos = V0,
                 model_type = 0, # exact
                 name = ''):

        # sets the object name if not already set by a child class
        self.metric = metric
        default_name = 'din9021_washer_m' + str(self.metric)
        self.set_name (name, default_name, change = 0)

        washer_dict = kcomp.D9021[metric]
        Washer.__init__(self,
                        r_out = washer_dict['do']/2.,
                        r_in = washer_dict['di']/2.,
                        h = washer_dict['t'],
                        axis_h = axis_h,
                        pos_h = pos_h,
                        tol = tol, pos = pos,
                        model_type = model_type)




#doc = FreeCAD.newDocument()
#washer = Din125Washer( metric = 5,
#                    axis_h = VZ, pos_h = 1, tol = 0, pos = V0,
#                    model_type = 0, # exact
#                    name = '')
#wash = Din9021Washer( metric = 5,
#                    axis_h = VZ, pos_h = 1, tol = 0,
#                    pos = washer.pos + DraftVecUtils.scale(VZ,washer.h),
#                    model_type = 0, # exact
#                    name = '')


class BearingOutl (SinglePart, shp_clss.ShpCylHole):
    """ Bearing outline , that is, a cylinder with a inner hole.
    It does not include the balls and parts

    Parameters
    -----------
    bearing_nb : int
        Bearing number code
    axis_h : FreeCAD.Vector
        vector along the cylinder height
    pos_h : int
        location of pos along axis_h (0,1)
        0: the cylinder pos is centered along its height
        1: the cylinder pos is at its base
    axis_d : FreeCAD.Vector
        vector along the cylinder radius, a direction perpendicular to axis_h
        it is not necessary if pos_d == 0
        It can be None, but if None, axis_w has to be None
    axis_w : FreeCAD.Vector
        vector along one radius (perpendicular to axis_h and axis_d)
        it can be None
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
    tol : float
        Tolerance for the inner and outer radius.
        It is the tolerance for the diameter, so the radius will be added/subs
        have of this tolerance
        tol will be added to the inner radius (so it will be larger)
        tol will be substracted to the outer radius (so it will be smaller)
        
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is

    Attributes
    -----------
    All the parameters and attributes of parent classes SinglePart ShpCylHole

    metric : int or float (in case of M2.5) or even str for inches ?
        Metric of the washer

    model_type : int
        type of model:
        1: outline (is not an exact model)

    bearing_nb : int
        number of the bearing, such as 624, 608, ... see kcomp.BEARING
    bear_d : dictionary
        dictionary with the dimensions of the bearing

    """
    def __init__(self, bearing_nb, axis_h, pos_h,
                 axis_d = None, axis_w = None,
                 pos_d = 0, pos_w = 0, tol = 0, pos = V0,
                 name = ''):

        self.model_type = 1 # outline
        # sets the object name if not already set by a child class
        default_name = 'bearing_' + str(bearing_nb) 
        self.set_name (name, default_name, change = 0)
        self.bearing_nb = bearing_nb

        print(bearing_nb)
        print(default_name)

        try:
            bear_d = kcomp.BEARING[bearing_nb]
            self.bear_d = bear_d
        except KeyError:
            logger.error('Bearing key not found: ' + str(bearing_nb))
        else: # no exception:
            if tol == 0:
                tol_r = 0
            else:
                tol_r = tol / 2. #just in case there is tolerance
            # First the shape is created
            shp_clss.ShpCylHole.__init__(self,
                                         r_out = bear_d['do']/2.,
                                         r_in = bear_d['di']/2.,
                                         h = bear_d['t'],
                                         axis_h = axis_h,
                                         axis_d = axis_d,
                                         axis_w = axis_w,
                                         pos_d = pos_d,
                                         pos_w = pos_w,
                                         pos_h = pos_h,
                                         # inside tolerance is more
                                         xtr_r_in = tol_r,
                                         # outside tolerance is less
                                         xtr_r_out = - tol_r,
                                         pos = pos)

            # Then the Part
            SinglePart.__init__(self)


#bear = BearingOutl( bearing_nb = 608,
#                    axis_h = VZN, pos_h = 1, tol = 0,
#                    pos = washer.pos + DraftVecUtils.scale(VZN,washer.h),
#                    name = '')

class Nut (SinglePart, shp_clss.ShpPrismHole):
    """
    Creates a Nut, using shp_clss.ShpPrismHole
    See comments of ShpPrismHole

    Parameters
    -----------
    r_out : float
        circumradius of the hexagon (side)
    h : float
        height of the cylinder
    r_in : float
        radius of the inner hole
    axis_d_apo : int
        0: default: axis_d points to the vertex
        1: axis_d points to the center of a side
    h_offset : float
        0: default
        Distance from the top, just to place the nut, see pos_h
        if negative, from the bottom
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
           circle center
        2: pos is at the apothem, on axis_d
        3: pos is at the outer circunsference, on axis_d, at r_out from the
           circle center
    pos_w : int
        location of pos along axis_w (-2, -1, 0, 1, 2)
        0: pos is at the circunference center
        1: pos is at the inner circunsference, on axis_w, at r_in from the
           circle center
        2: pos is at the apothem, on axis_w
        3: pos is at the outer circunsference, on axis_w, at r_out from the
           center
    pos : FreeCAD.Vector
        Position of the prism, taking into account where the center is


    """

    def __init__(self, r_out, h, r_in, 
                axis_d_apo = 0, h_offset = 0,
                axis_h = VZ, axis_d = None, axis_w = None,
                pos_h = 0, pos_d = 0, pos_w = 0, pos = V0,
                model_type = 0, name = ''):

        # sets the object name if not already set by a child class
        if not hasattr(self, 'metric'):
            self.metric = int(2 * r_in)
        default_name = 'nut_m' + str(self.metric)
        self.set_name (name, default_name, change = 0)

        # First the shape is created
        shp_clss.ShpPrismHole.__init__(self, n_sides = 6,
                                       r_out = r_out, h = h,
                                       r_in = r_in,
                                       axis_d_apo = axis_d_apo,
                                       h_offset = h_offset,
                                       axis_h = axis_h,
                                       axis_d = axis_d,
                                       axis_w = axis_w,
                                       pos_h = pos_h,
                                       pos_d = pos_d,
                                       pos_w = pos_w,
                                       pos   = pos)


        # Then the Part
        SinglePart.__init__(self)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])


#doc = FreeCAD.newDocument()
#nut = Nut ( r_out   = 10,
#            h       = 4,
#            r_in   = 5,
#            h_offset = 1,
#            axis_d_apo = 0,
#            axis_h = VZ, axis_d = VX, axis_w = VY,
#            pos_h = 2, pos_d = 0, pos_w = 0,
#            pos = V0)



class Din934Nut (Nut):
    """ Din 934 Nut

    Parameters
    -----------
    metric : int (maybe float: 2.5)

    axis_h : 
    axis_d_apo : int
        * 0: default: axis_d points to the vertex
        * 1: axis_d points to the center of a side
    h_offset : float
        Distance from the top, just to place the Nut, see pos_h
        if negative, from the bottom
    
            * 0: default
    
    axis_h : FreeCAD.Vector
        Vector along the axis, height
    axis_d : FreeCAD.Vector
        Vector along the first vertex, a direction perpendicular to axis_h.
        It is not necessary if pos_d == 0. 
        It can be None, but if None, axis_w has to be None
    axis_w : FreeCAD.Vector
        Vector along the cylinder radius,
        a direction perpendicular to axis_h and axis_d.
        It is not necessary if pos_w == 0. 
        It can be None
    pos_h : int
        Location of pos along axis_h

            *  0: at the center
            * -1: at the base
            *  1: at the top
            * -2: at the base + h_offset
            *  2: at the top + h_offset

    pos_d : int
        Location of pos along axis_d (-2, -1, 0, 1, 2)
        
            * 0: pos is at the circunference center (axis)
            * 1: pos is at the inner circunsference, on axis_d, at r_in from the
              circle center
            * 2: pos is at the apothem, on axis_d
            * 3: pos is at the outer circunsference, on axis_d, at r_out from the
              circle center

    pos_w : int
        Location of pos along axis_w (-2, -1, 0, 1, 2)
        
            * 0: pos is at the circunference center
            * 1: pos is at the inner circunsference, on axis_w, at r_in from the
              circle center
            * 2: pos is at the apothem, on axis_w
            * 3: pos is at the outer circunsference, on axis_w, at r_out from the
              center

    pos : FreeCAD.Vector
        Position of the prism, taking into account where the center is
    model_type : 0 
        Not to print, just an outline
    name : str
        Name of the bolt

    """

    def __init__(self, metric,
                axis_d_apo = 0, h_offset = 0,
                axis_h = VZ, axis_d = None, axis_w = None,
                pos_h = 0, pos_d = 0, pos_w = 0, pos = V0,
                model_type = 0, name = ''):

        if metric >= 3:
            str_metric = str(int(metric))
        else:
            str_metric = str(metric)
        default_name = 'd934nut_m' + str_metric
        self.set_name (name, default_name, change = 0)

        try:
            nut_dict = kcomp.D934[metric]
            self.nut_dict = nut_dict
        except KeyError:
            logger.error('nut key not found: ' + str(metric))
        else: #no exception
            Nut.__init__(self, 
                         r_out   = nut_dict['circ_r'],
                         h       = nut_dict['l'],
                         r_in    = metric/2.,
                         h_offset = h_offset,
                         axis_d_apo = axis_d_apo,
                         axis_h = axis_h, axis_d = axis_d, axis_w = axis_w,
                         pos_h = pos_h, pos_d = pos_d, pos_w = pos_w,
                         pos = pos,
                         model_type = model_type,
                         name = name)

#doc = FreeCAD.newDocument()
#nut = Din934Nut ( metric   = 3,
#                  h_offset = 0,
#                  axis_d_apo = 0,
#                  axis_h = VZ, axis_d = VX, axis_w = VY,
#                  pos_h = 2, pos_d = 0, pos_w = 0,
#                  pos = V0)





class Bolt (SinglePart, shp_clss.ShpBolt):
    """ Creates a FreeCAD object of a bolt, from ShpBolt.
        different from fcfun.shp_bolt_dir (which is a function)

    Makes a bolt with various locations and head types
    It is an approximate model. The thread is not made, it is just a little
    smaller just to see where it is

    Parameters
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
    model_type : 0 
        not to print, just an outline
    name : str
        name of the bolt

    Attributes
    -----------
    pos_o : FreeCAD.Vector
        Position of the origin of the shape

    self.tot_l : float
        Total length of the bolt: head_l + shank_l
    shp : OCC Topological Shape
        The shape of this part


    ::

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
                 model_type = 0,
                 name = ''):
    
        if not hasattr(self, 'metric'):
            metric = 2 * shank_r
            if metric >= 3:
                self.metric = int(metric)
            else:
                self.metric = metric
        default_name = 'bolt_m' + str(self.metric) + 'l' + str(int(shank_l))
        self.set_name (name, default_name, change = 0)

        # First the shape is created
        shp_clss.ShpBolt.__init__(self,
                                  shank_r = shank_r,
                                  shank_l = shank_l,
                                  head_r  = head_r,
                                  head_l  = head_l,
                                  thread_l = thread_l,
                                  head_type = head_type,
                                  socket_l = socket_l,
                                  socket_2ap = socket_2ap,
                                  shank_out = shank_out,
                                  head_out = head_out,
                                  axis_h = axis_h,
                                  axis_d = axis_d,
                                  axis_w = axis_w,
                                  pos_h = pos_h, pos_d = pos_d, pos_w = pos_w,
                                  pos = pos)

        # Then the Part
        SinglePart.__init__(self)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])
                                  



#metric = 3
#bolt_dict = kcomp.D912[metric]
#thread_l = 18
#shank_l = 30
#bolt = Bolt (
#                 shank_r = bolt_dict['d']/2.,
#                 shank_l = shank_l,
#                 head_r  = bolt_dict['head_r'],
#                 head_l  = bolt_dict['head_l'],
#                 #thread_l = 0,
#                 thread_l = thread_l,
#                 head_type = 1, # cylindrical. 1: hexagonal
#                 #socket_l = bolt_dict['head_l']/2., # not sure
#                 socket_l = 0,
#                 socket_2ap = bolt_dict['ap2'],
#                 shank_out = 0,
#                 head_out = 1,
#                 axis_h = VX, axis_d = VY, axis_w = VZ,
#                 pos_h = 2, pos_d = 2, pos_w = 0,
#                 pos = FreeCAD.Vector(0,0,0))


class Din912Bolt (Bolt):
    """ Din 912 bolt. hex socket bolt

    Parameters
    -----------
    metric : int (may be float: 2.5

    shank_l : float
        length of the bolt, not including the head
    shank_l_adjust : int

        * 0: shank length will be the size of the parameter shank_l
        * -1: shank length will be the size of the closest shorter or equal
          to shank_l available lengths for this type of bolts
        * 1: shank length will be the size of the closest larger or equal
          to shank_l available lengths for this type of bolts

    shank_out : float
        Distance to the end of the shank, just for positioning, it doesnt
        change shank_l
        
            * 0: default
        
        Note
        ---
        I dont think it is necessary, but just in case

    head_out : float
        Distance to the end of the head, just for positioning, it doesnt
        change head_l
        
            * 0: default
        
        Note
        ----
        I dont think it is necessary, but just in case

    axis_h : FreeCAD.Vector
        Vector along the axis of the bolt, pointing from the head to the shank
    axis_d : FreeCAD.Vector
        Vector along the radius, a direction perpendicular to axis_h
        If the head is hexagonal, the direction of one vertex
    axis_w : FreeCAD.Vector
        Vector along the cylinder radius,
        a direction perpendicular to axis_h and axis_d.
        It is not necessary if pos_w == 0.
        It can be None
    pos_h : int
        Location of pos along axis_h
        
            * 0: top of the head, considering head_out,
            * 1: position of the head not considering head_out
              if head_out = 0, it will be the same as pos_h = 0
            * 2: end of the socket, if no socket, will be the same as pos_h = 0
            * 3: union of the head and the shank
            * 4: where the screw starts, if all the shank is screwed, it will be
              the same as pos_h = 2
            * 5: end of the shank, not considering shank_out
            * 6: end of the shank, if shank_out = 0, will be the same as pos_h = 5
            * 7: top of the head, considering xtr_head_l, if xtr_head_l = 0
              will be the same as pos_h = 0

    pos_d : int
        Location of pos along axis_d (symmetric)
        
            * 0: pos is at the central axis
            * 1: radius of the shank
            * 2: radius of the head

    pos_w : int
        Location of pos along axis_d (symmetric)
            
            * 0: pos is at the central axis
            * 1: radius of the shank
            * 2: radius of the head

    pos : FreeCAD.Vector
        Position of the bolt, taking into account where the pos_h, pos_d, pos_w
        are
    model_type : 0 
        Not to print, just an outline
    name : str
        Name of the bolt
    """

    def __init__(self, metric, shank_l,
                 shank_l_adjust = 0,
                 shank_out = 0,
                 head_out = 0,
                 axis_h = VZ, axis_d = None, axis_w = None,
                 pos_h = 0, pos_d = 0, pos_w = 0,
                 pos = V0,
                 model_type = 0,
                 name = ''):

        if metric >= 3:
            str_metric = str(int(metric))
        else:
            str_metric = str(metric)


        try:
            bolt_dict = kcomp.D912[metric]
            self.bolt_dict = bolt_dict
        except KeyError:
            logger.error('bolt key not found: ' + str(metric))
        else: # no exception

            if shank_l_adjust == 0:
                self.shank_l = shank_l
            else:
                sh_l_list = self.bolt_dict['shank_l_list']
                if shank_l_adjust == -1: # smaller closest to shank_l
                    self.shank_l = [sh_l for sh_l in sh_l_list
                                    if sh_l<=shank_l][-1]
                elif shank_l_adjust == 1: # larger closest to shank_l
                    self.shank_l = [sh_l for sh_l in sh_l_list
                                    if sh_l>=shank_l][0]
                else:
                    logger.error('wrong value for parameter shank_l_adjust')
                    self.shank_l = shank_l

            default_name = (  'd912bolt_m' + str_metric + '_l'
                            + str(int(self.shank_l)))
            self.set_name (name, default_name, change = 0)


            if bolt_dict['thread'] > self.shank_l:
                thread_l = 0 # all threaded
            else:
                thread_l = bolt_dict['thread']

            Bolt.__init__(self,
                     shank_r = bolt_dict['d']/2.,
                     shank_l = self.shank_l,
                     head_r  = bolt_dict['head_r'],
                     head_l  = bolt_dict['head_l'],
                     thread_l = thread_l,
                     head_type = 0, # cylindrical
                     socket_l = bolt_dict['head_l']/2., # not sure
                     socket_2ap = bolt_dict['ap2'],
                     shank_out = shank_out,
                     head_out = head_out,
                     axis_h = axis_h, axis_d = axis_d, axis_w = axis_w,
                     pos_h = pos_h, pos_d = pos_d, pos_w = pos_w,
                     pos = pos,
                     model_type = model_type)


#doc = FreeCAD.newDocument()
#bolt = Din912Bolt ( metric = 3, shank_l = 24,
#                    shank_out = 0, head_out = 0,
#                    axis_h = VY,
#                    axis_d = VX,
#                    axis_w = None,
#                    pos_h = 5,
#                    pos_d = 0,
#                    pos_w = 0,
#                    pos = V0)
