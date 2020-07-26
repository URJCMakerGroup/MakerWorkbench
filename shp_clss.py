# ----------------------------------------------------------------------------
# -- Obj3D class and children
# ----------------------------------------------------------------------------
# -- (c) Felipe Machado
# -- Area of Electronic Technology. Rey Juan Carlos University (urjc.es)
# -- January-2018
# ----------------------------------------------------------------------------
# --- LGPL Licence
# ----------------------------------------------------------------------------

import FreeCAD
import Part
import DraftVecUtils

import os
import sys
import math
import inspect
import logging

# directory this file is
filepath = os.getcwd()
import sys
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath)

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
            
    """
    def __init__(self, axis_d = None, axis_w = None, axis_h = None):
        # the TopoShape has an origin, and distance vectors from it to 
        # the different points along the coordinate system  
        self.d_o = {}  # along axis_d
        self.w_o = {}  # along axis_w
        self.h_o = {}  # along axis_h
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



class ShpCyl (Obj3D):
    """
    Creates a shape of a cylinder
    Makes a cylinder in any position and direction, with optional extra
    heights and radius, and various locations in the cylinder

    Parameters:
    -----------
    r : float
        radius of the cylinder
    h : float
        height of the cylinder
    axis_h : FreeCAD.Vector
        vector along the cylinder height
    axis_d : FreeCAD.Vector
        vector along the cylinder radius, a direction perpendicular to axis_h
        It is not necessary if pos_d == 0
        It can be None, but if None, axis_w has to be None
    axis_w : FreeCAD.Vector
        vector along the cylinder radius
        a direction perpendicular to axis_h and axis_d
        It is not necessary if pos_w == 0
        It can be None
    pos_h : int
        location of pos along axis_h (0, 1)
        0: the cylinder pos is centered along its height
        1: the cylinder pos is at its base (not considering xtr_h)
    pos_d : int
        location of pos along axis_d (0, 1)
        0: pos is at the circunference center
        1: pos is at the circunsference, on axis_d, at r from the circle center
           (not at r + xtr_r)
    pos_w : int
        location of pos along axis_w (0, 1)
        0: pos is at the circunference center
        1: pos is at the circunsference, on axis_w, at r from the circle center
           (not at r + xtr_r)
    xtr_top : float
        Extra height on top, it is not taken under consideration when
        calculating the cylinder center along the height
    xtr_bot : float
        Extra height at the bottom, it is not taken under consideration when
        calculating the cylinder center along the height or the position of
        the base
    xtr_r : float
        Extra length of the radius, it is not taken under consideration when
        calculating pos_d or pos_w
    pos : FreeCAD.Vector
        Position of the cylinder, taking into account where the center is
    print_ax: FreeCAD.Vector
        The best direction to print, pointing upwards
        it can be V0 if there is no best direction

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
           .     .
         (    o    ) ---- axis_d       This o will be pos_o (origin)
           .     .
             . .    

           axis_h
              :
              :
          ...............
         :____:____:....: xtr_top
         |         |
         |         |
         |         |
         |         |
         |         |
         |         |
         |____1____|...............> axis_d
         :....o....:....: xtr_bot             This o will be pos_o


    pos_h = 0, pos_d = 1, pos_w = 0
    pos at x:

       axis_w
         :
         :
         :   . .    
         : .     .
         x         ) ----> axis_d
           .     .
             . .    

           axis_h
              :
              :
          ...............
         :____:____:....: xtr_top
         |         |
         |         |
         |         |
         x         |....>axis_d    h = 0
         |         |
         |         |
         |_________|.....
         :....o....:....: xtr_bot        This o will be pos_o


    pos_h = 0, pos_d = 1, pos_w = 1
    pos at x:

       axis_w
         :
         :
         :   . .    
         : .     .
         (         )
           .     .
         x   . .     ....> axis_d

        axis_h
         :
         :
          ...............
         :____:____:....: xtr_top
        ||         |
        ||         |
        ||         |
        |x         |....>axis_d
        ||         |
        ||         |
        ||_________|.....
        ::....o....:....: xtr_bot
        :;
        xtr_r

    """
    def __init__(self, 
                 r, h, axis_h = VZ, 
                 axis_d = None, axis_w = None,
                 pos_h = 0, pos_d = 0, pos_w = 0,
                 xtr_top=0, xtr_bot=0, xtr_r=0, pos = V0):

        Obj3D.__init__(self, axis_d, axis_w, axis_h)

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i): # so we keep the attributes already set
                setattr(self, i, values[i])

        # vectors from o (orig) along axis_h, to the pos_h points
        # h_o is a dictionary created in Obj3D.__init__
        self.h_o[0] =  self.vec_h(h/2. + xtr_bot)
        self.h_o[1] =  self.vec_h(xtr_bot)
        # pos_h = 0 is at the center
        self.h0_cen = 1

        self.d_o[0] = V0
        if self.axis_d is not None:
            self.d_o[1] = self.vec_d(-r)
        elif pos_d == 1:
            logger.error('axis_d not defined while pos_d ==1')
        # pos_d = 0 is at the center
        self.d0_cen = 1

        self.w_o[0] = V0
        if self.axis_w is not None:
            self.w_o[1] = self.vec_w(-r)
        elif pos_w == 1:
            logger.error('axis_w not defined while pos_w ==1')
        # pos_w = 0 is at the center
        self.w0_cen = 1

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        shpcyl = fcfun.shp_cyl (r      = r + xtr_r,         # radius
                                h      = h+xtr_bot+xtr_top, # height
                                normal = self.axis_h,       # direction
                                pos    = self.pos_o)        # Position

        self.shp = shpcyl

#cyl = ShpCyl (r=2, h=2, axis_h = VZ, 
#              axis_d = VX, axis_w = VY,
#              pos_h = 1, pos_d = 1, pos_w = 0,
#              xtr_top=0, xtr_bot=1, xtr_r=2,
#              pos = V0)
#              #pos = FreeCAD.Vector(1,2,0))
#Part.show(cyl.shp)



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
                 pos = V0):


        Obj3D.__init__(self, axis_d, axis_w, axis_h)

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


#cyl = ShpCylHole (r_in=2, r_out=6, h=4,
#                       #axis_h = FreeCAD.Vector(1,1,0), 
#                       axis_h = VZ,
#                       #axis_d = VX, axis_w = VYN,
#                       axis_d = VX,
#                       pos_h = 1,  pos_d = 1, pos_w = 0,
#                       xtr_top=1, xtr_bot=1,
#                       xtr_r_in=0, xtr_r_out=0,
#                       pos = V0)
#                       #pos = FreeCAD.Vector(1,2,3))
#Part.show(cyl.shp)




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
                 pos = V0):


        Obj3D.__init__(self, axis_d, axis_w, axis_h)

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


#prism = ShpPrismHole (n_sides = 4,
#                      r_out   = 20,
#                      h       = 4,
#                      r_in   = 1,
#                      h_offset = 1,
#                      xtr_r_in = 2,
#                      xtr_r_out = 4,
#                      axis_d_apo = 0,
#                      axis_h = VZ, axis_d = VX, axis_w = VY,
#                      pos_h = -2, pos_d = 0, pos_w = 0,
#                      pos = V0)

#Part.show(prism.shp)







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
                 pos = V0):


        Obj3D.__init__(self, axis_d, axis_w, axis_h)

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
                                  

#metric = 3
#bolt_dict = kcomp.D912[metric]
#thread_l = 18
#shank_l = 30
#shp_bolt = ShpBolt (
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








# ------------------- def wire_beltclamp
# Not sure if a wire should be an Obj3D class

class WireBeltClamped (Obj3D):

    """
    Creates a wire following 2 pulleys and ending in a belt clamp
    But it is a wire in FreeCAD, has no volumen

      axis_w
        :
        :
     pulley1                   pulley2
          
        -----------------------------------
      (   )                             (   )--------> axis_d
        ---------===  ( )  ( )  ===--------
               clamp1          clamp2

      1 0        2 3   45  67   8 9      10 11   pos_d
        :          :            :         :
        :          :            :         :
        :          :............:         :
        :                +                :
        :             clamp_sep           :
        :                                 :
        :.................................:
                       +
                     pull_sep_d

      pos_w points:

      axis_w
        :                                    pull2
        :      clamp1                 clamp2
       2_                                     3-
                                             ( 1 )   - - pull_sep_w (positive)
     (  0  )   - - - - - - - - - - - - - - -  5-     - -
              6 ___ ...................___.............:+ clamp_pull1_w (neg)
       4-     7       < )        ( >                   :+ clamp_w
              8 ___ ...................___.............:



      axis_w
        :                                      pull2
        :      clamp1                 clamp2
        _                                         -
                                                (   )   - - pull_sep_w(positive)
     (     )   - - - - - - - - - - - - - - - - -  -     - -
                ___ ...................___.............:+ clamp_pull1_w (neg)
        -             < )        ( >                   :+ clamp_w
                ___ ...................___.............:
        :      :   :   ::         :   :   :       :
        :      :   :   :cyl_r     :   :   :       :
        :      :   :...:          :...:   :.......:
        :      :   :  +            +  :   :   +
        :      :   :  clamp_cyl_sep   :   :   +
        :      :   :                  :   :  clamp_pull2_d
        :      :   :                  :...:
        :      :   :                  :  +
        :      :   :..................: clamp_d
        :      :   :        +
        :      :   :       clamp_sep
        :      :...:   
        :      : +
        :      : clamp_d
        :      :
        :......:
           +
         clamp_pull1_d
         

    Parameters:
    -----------
    pull1_dm: float
        diameter of pulley 1
    pull2_dm: float
        diameter of pulley 2
    pull_sep_d : float
        separation between the 2 pulleys centers along axis_d
    pull_sep_w : float
        separation between the 2 pulleys centers along axis_w
        if positive, pulley 2 is further away in the direction of axis_w
        if negative, pulley 2 is further away opposite to the direction of
           axis_w
    clamp_pull1_d : float
        separation between the clamp (side closer to the center) and the center
        of the pulley1 along axis d
    clamp_pull1_w : float
        separation between the center of the clamp and the center of the
        pulley1 along axis w
    clamp_pull2_d : float
        separation between the clamp (side closer to the center) and the center
        of the pulley1 along axis d
        clamp_pull2_w can be calculated because the clamps are aligned along
        axis_d, so it will be clamp_pull1_d + pull_sep_w
    clamp_d : float
        length of the clamp (same for each clamp)
    clamp_w : float
        width of inner space (same for each clamp)
    clamp_cyl_sep : float
        separation between clamp and the center of the cylinder (or the center)
        of the larger cylinder (when is a belt shape)
    cyl_r : float
        Radius of the cylinder for the belt, if it is not a cylinder but a
        shape of 2 cylinders: < ) , then the raidius of the larger one

    axis_d :  FreeCAD.Vector
        Coordinate System Vector along the depth
    axis_w :  FreeCAD.Vector
        Coordinate System Vector along the width
    pos_d : int
        location of pos along the axis_d, see drawing
        0: center of the pulley 1
        1: end of pulley 1
        2: end of clamp 1, closest end to pulley 1
        3: other end of clamp 1, closest to cylinder
        4: center of cylinder (or shape < ) 1
        5: external radius of cylinder 1
        6: external radius of cylinder 2
        7: center of cylinder (or shape ( > 2
        8: end of clamp 2, closest to cylinder
        9: other end of clamp 2, closest end to pulley 2
        10: center of pulley 2
        11: end of pulley 2
    pos_w : int
        location of pos along the axis_w, see drawing
        0: center of pulley 1
        1: center of pulley 2
        2: end (radius) of pulley 1 along axis_w
        3: end (radius) of pulley 2 along axis_w
        4: other end (radius) of pulley 1 opposite to axis_w
        5: other end (radius) of pulley 2 opposite to axis_w
        6: clamp space, closest to the pulley
        7: center of clamp space
        8: clamp space, far away from the pulley
    pos: FreeCAD vector of the position of the reference

    Attributes:
    -----------
    clamp_sep : float
        separation between clamps, the closest ends


    """

    def __init__(self,
                 pull1_dm,
                 pull2_dm,
                 pull_sep_d,
                 pull_sep_w,
                 clamp_pull1_d,
                 clamp_pull1_w,
                 clamp_pull2_d,
                 clamp_d,
                 clamp_w,
                 clamp_cyl_sep,
                 cyl_r,
                 axis_d = VY,
                 axis_w = VX,
                 pos_d = 0,
                 pos_w = 0,
                 pos=V0):

        axis_h = axis_d.cross(axis_w)
        Obj3D.__init__(self, axis_d = axis_d, axis_w = axis_w, axis_h = None)

        self.axis_wn = self.axis_w.negative()

        # save the arguments as attributes:
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        for i in args:
            if not hasattr(self,i):
                setattr(self, i, values[i])

        self.pull1_r = pull1_dm/2.
        self.pull2_r = pull2_dm/2.

        self.clamp_sep = (pull_sep_d - ( clamp_pull1_d + 2*clamp_d +
                                        clamp_pull2_d))

        self.d0_cen = 0 # non symmetrical
        self.w0_cen = 0
        self.h0_cen = 0


        # vectors from the origin to the points along axis_d:
        self.d_o[0] = V0
        self.d_o[1] = self.vec_d(-self.pull1_r)
        self.d_o[2] = self.vec_d(clamp_pull1_d)
        self.d_o[3] = self.vec_d(clamp_pull1_d + clamp_d)
        self.d_o[4] = self.vec_d(clamp_pull1_d + clamp_d + clamp_cyl_sep)
                    # get_o_to_d (could be used)
        self.d_o[5] = self.d_o[4] + self.vec_d(cyl_r)

        self.d_o[8] = self.d_o[3] + self.vec_d(self.clamp_sep)
        self.d_o[7] = self.d_o[8] + self.vec_d(-clamp_cyl_sep)
        self.d_o[6] = self.d_o[7] + self.vec_d(-cyl_r)

        self.d_o[9]  = self.d_o[8]  + self.vec_d(clamp_d)
        self.d_o[10] = self.d_o[9]  + self.vec_d(clamp_pull2_d)
        self.d_o[11] = self.d_o[10] + self.vec_d(self.pull2_r)

        # vectors from the origin to the points along axis_w:
        self.w_o[0] = V0
        self.w_o[1] = self.vec_w(pull_sep_w)
        self.w_o[2] = self.vec_w(self.pull1_r)
        self.w_o[3] = self.vec_w(pull_sep_w + self.pull2_r)
        self.w_o[4] = self.vec_w(-self.pull1_r)
        self.w_o[5] = self.vec_w(pull_sep_w - self.pull2_r)
        self.w_o[6] = self.vec_w(-clamp_pull1_w)
        self.w_o[7] = self.vec_w(-(clamp_pull1_w + clamp_w/2.))
        self.w_o[8] = self.vec_w(-(clamp_pull1_w + clamp_w))

        # there is no axis_h, there for, always 0
        self.h_o[0] = V0

        # calculates the position of the origin, and keeps it in attribute pos_o
        self.set_pos_o()

        #axis_w
        #  :                                    pull2
        #  :
        #  2_                                   I3-
        #   H                                   ( 1 )   
        #(  0  )                                 5J 
        # G      6 ___     C        N     ___
        #  4-    7 A B   < )        ( >   P Q
        #        8 F_E     D        M     L_K
        #          ---                    --- 
        #        clamp1                  clamp2

        # at clamp 1, touching the clamp (w=6)
        A_pt = self.get_pos_dwh(2,6,0)
        B_pt = self.get_pos_dwh(3,6,0)
        E_pt = self.get_pos_dwh(3,8,0)
        F_pt = self.get_pos_dwh(2,8,0)

        Q_pt = self.get_pos_dwh(9,6,0)
        P_pt = self.get_pos_dwh(8,6,0)
        L_pt = self.get_pos_dwh(8,8,0)
        K_pt = self.get_pos_dwh(9,8,0)

        line_AB = Part.LineSegment(A_pt, B_pt).toShape()
        line_EF = Part.LineSegment(E_pt, F_pt).toShape()
        # from B tangent point to the cylinder
        cyl1_center_pt = self.get_pos_dwh(4,7,0)
        C_pt = fcfun.get_tangent_circle_pt(ext_pt=B_pt,
                                       center_pt= cyl1_center_pt,
                                       rad = cyl_r,
                                       axis_n = axis_h,
                                       axis_side = self.axis_w)
        line_BC = Part.LineSegment(B_pt, C_pt).toShape()

        D_pt = fcfun.get_tangent_circle_pt(ext_pt=E_pt,
                                       center_pt= cyl1_center_pt,
                                       rad = cyl_r,
                                       axis_n = axis_h,
                                       axis_side = self.axis_wn)
        line_DE = Part.LineSegment(D_pt, E_pt).toShape()

        arc_CD = Part.Arc(C_pt, self.get_pos_dwh(5,7,0),D_pt).toShape()

        pull1_center_pt = self.get_pos_dwh(0,0,0)
        G_pt = fcfun.get_tangent_circle_pt(ext_pt=F_pt,
                                       center_pt= pull1_center_pt,
                                       rad = self.pull1_r,
                                       axis_n = axis_h,
                                       axis_side = self.axis_wn)

        line_FG = Part.LineSegment(F_pt, G_pt).toShape()

        pull2_center_pt = self.get_pos_dwh(10,1,0)
        HI_list = fcfun.get_tangent_2circles(
                                       center1_pt = pull1_center_pt,
                                       center2_pt = pull2_center_pt,
                                       rad1 = self.pull1_r,
                                       rad2 = self.pull2_r,
                                       axis_n = axis_h,
                                       axis_side = self.axis_w)

        H_pt = HI_list[0][0]
        I_pt = HI_list[0][1]

        arc_GH = Part.Arc(G_pt, self.get_pos_dwh(1,0,0),H_pt).toShape()
        line_HI = Part.LineSegment(H_pt, I_pt).toShape()


        J_pt = fcfun.get_tangent_circle_pt(ext_pt=K_pt,
                                       center_pt= pull2_center_pt,
                                       rad = self.pull2_r,
                                       axis_n = axis_h,
                                       axis_side = self.axis_wn)
        arc_IJ = Part.Arc(I_pt, self.get_pos_dwh(11,1,0),J_pt).toShape()

        line_JK = Part.LineSegment(J_pt, K_pt).toShape()
        line_KL = Part.LineSegment(K_pt, L_pt).toShape()


        cyl2_center_pt = self.get_pos_dwh(7,7,0)
        M_pt = fcfun.get_tangent_circle_pt(ext_pt=L_pt,
                                       center_pt= cyl2_center_pt,
                                       rad = cyl_r,
                                       axis_n = axis_h,
                                       axis_side = self.axis_wn)
        line_LM = Part.LineSegment(L_pt, M_pt).toShape()

        N_pt = fcfun.get_tangent_circle_pt(ext_pt=P_pt,
                                       center_pt= cyl2_center_pt,
                                       rad = cyl_r,
                                       axis_n = axis_h,
                                       axis_side = self.axis_w)

        arc_MN = Part.Arc(M_pt, self.get_pos_dwh(6,7,0),N_pt).toShape()

        line_NP = Part.LineSegment(N_pt, P_pt).toShape()
        line_PQ = Part.LineSegment(P_pt, Q_pt).toShape()
        

        
        belt_wire = Part.Wire([line_AB, line_BC, arc_CD,
                          line_DE, line_EF, line_FG, arc_GH, line_HI,
                          arc_IJ, line_JK, line_KL, line_LM, arc_MN,
                          line_NP, line_PQ])



        #Part.show(belt_wire)
        self.belt_wire = belt_wire


#belt_wire = WireBeltClamped (
#                 pull1_dm = 5,
#                 pull2_dm = 6,
#                 pull_sep_d = 80,
#                 pull_sep_w = 0,
#                 clamp_pull1_d = 15,
#                 clamp_pull1_w = 5,
#                 clamp_pull2_d = 15,
#                 clamp_d = 5,
#                 clamp_w = 4,
#                 clamp_cyl_sep = 8,
#                 cyl_r = 3,
#                 axis_d = VY,
#                 axis_w = VX,
#                 pos_d = 0,
#                 pos_w = 0,
#                 pos=V0)






