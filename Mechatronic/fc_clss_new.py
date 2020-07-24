import os
import sys
import inspect
import logging
import math
import FreeCAD
import FreeCADGui

import fcfun

from NuevaClase import Obj3D, ShpBolt, ShpPrismHole, ShpCylHole
from fcfun import V0, VX, VY, VZ, V0ROT

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import kcomp
import shp_clss

class Washer (ShpCylHole):
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
                 name = None):

        # sets the object name if not already set by a child class
        if not hasattr(self, 'metric'):
            self.metric = int(2 * r_in)
        if name == None:
            name = 'washer' + str(self.metric)
        self.name = name

        self.pos = FreeCAD.Vector(0,0,0)
        self.position = pos

        tol_r = tol / 2.

        # First the shape is created
        ShpCylHole.__init__(self, r_out = r_out, r_in = r_in,
                            h = h, axis_h = axis_h,
                            pos_h = pos_h,
                            # inside tolerance is more
                            xtr_r_in = tol_r,
                            # outside tolerance is less
                            xtr_r_out = - tol_r,
                            pos = self.pos,
                            name = self.name)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])

        super().create_fco()
        # Need to set first in (0,0,0) and after that set the real placement.
        # This enable to do rotations without any issue
        self.fco.Placement.Base = FreeCAD.Vector(0,0,0) 
        self.fco.Placement.Base = self.position

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
                 name = None):

        # sets the object name if not already set by a child class
        self.metric = metric
        if name == None:
            name = 'din125_washer_m' + str(self.metric)
        self.name = name

        washer_dict = kcomp.D125[metric]
        Washer.__init__(self,
                        r_out = washer_dict['do']/2.,
                        r_in = washer_dict['di']/2.,
                        h = washer_dict['t'],
                        axis_h = axis_h,
                        pos_h = pos_h,
                        tol = tol, pos = pos,
                        model_type = model_type,
                        name = self.name)

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
                 name = None):

        # sets the object name if not already set by a child class
        self.metric = metric
        if name == None:
            name = 'din9021_washer_m' + str(self.metric)
        self.name = name

        washer_dict = kcomp.D9021[metric]
        Washer.__init__(self,
                        r_out = washer_dict['do']/2.,
                        r_in = washer_dict['di']/2.,
                        h = washer_dict['t'],
                        axis_h = axis_h,
                        pos_h = pos_h,
                        tol = tol, pos = pos,
                        model_type = model_type,
                        name = self.name)

class BearingOutl (ShpCylHole):
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
                 name = None):

        self.pos = FreeCAD.Vector(0,0,0)
        self.position = pos

        self.model_type = 1 # outline
        # sets the object name if not already set by a child class
        if name == None:
            name = 'bearing_' + str(bearing_nb) 
        self.name = name
        self.bearing_nb = bearing_nb

        # print(bearing_nb)
        # print(default_name)

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
            ShpCylHole.__init__(self,
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
                                pos = self.pos,
                                name = self.name)

            super().create_fco()
            # Need to set first in (0,0,0) and after that set the real placement.
            # This enable to do rotations without any issue
            self.fco.Placement.Base = FreeCAD.Vector(0,0,0) 
            self.fco.Placement.Base = self.position

class Nut (ShpPrismHole):
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
                model_type = 0, name = None):

        # sets the object name if not already set by a child class
        if not hasattr(self, 'metric'):
            self.metric = int(2 * r_in)
        if name == None:
            name = 'nut_m' + str(self.metric)
        self.name = name

        self.pos = FreeCAD.Vector(0,0,0)
        self.position = pos

        # First the shape is created
        ShpPrismHole.__init__(self, n_sides = 6,
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
                            pos   = self.pos,
                            name = self.name)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])
        super().create_fco()
        # Need to set first in (0,0,0) and after that set the real placement.
        # This enable to do rotations without any issue
        self.fco.Placement.Base = FreeCAD.Vector(0,0,0) 
        self.fco.Placement.Base = self.position

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
                model_type = 0, name = None):

        if metric >= 3:
            str_metric = str(int(metric))
        else:
            str_metric = str(metric)
        if name == None:
            name = 'd934nut_m' + str_metric
        self.name = name

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
                         name = self.name)

class Bolt (ShpBolt):
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
                 name = None):
    
        if not hasattr(self, 'metric'):
            metric = 2 * shank_r
            if metric >= 3:
                self.metric = int(metric)
            else:
                self.metric = metric
        if name == None:
            name = 'bolt_m' + str(self.metric) + 'l' + str(int(shank_l))
        self.name = name

        self.pos = FreeCAD.Vector(0,0,0)
        self.position = pos

        # First the shape is created
        ShpBolt.__init__(self,
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
                        pos = self.pos,
                        name = self.name)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes by CylHole
                setattr(self, i, values[i])
        super().create_fco()
        # Need to set first in (0,0,0) and after that set the real placement.
        # This enable to do rotations without any issue
        self.fco.Placement.Base = FreeCAD.Vector(0,0,0) 
        self.fco.Placement.Base = self.position

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
                 name = None):

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

            if name == None:
                name = (  'd912bolt_m' + str_metric + '_l'
                            + str(int(self.shank_l)))
            self.name = name


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