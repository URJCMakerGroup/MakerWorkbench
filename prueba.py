# scrip de prube para la generación de una placa con cuatro orificios para tornillos. Así mismo como la generación de los cuatro tornillos.
# En total tendremos cuatro objetos.
# El primer objeto será una placa con cuatro orificios. Los otros cuatro orificios serán tornillos.

import FreeCAD
import fcfun
from fcfun import VX, VY, VZ, V0
import parts 
import fc_clss
import shp_clss
import kcomp

def placa_con_tornillos_fun():
    # generamos una placa de dimensiones 100x100x10
    shp_placa = fcfun.shp_box_dir(box_w = 100.,
                                    box_d = 100.,
                                    box_h = 10.,
                                    fc_axis_w = VX,
                                    fc_axis_d = VY,
                                    fc_axis_h = VZ,
                                    cw = 0, cd = 0, ch = 0,
                                    pos = V0)
    
    # añadimos un tornillo en la posición 1x1x1
    shp_bolt1 = fcfun.shp_cyl(3., 10., normal = VZ, pos = FreeCAD.Vector(10,10,0))

    # sustraemos la forma del primer tornillo de la placa
    shp_placa_1hole = shp_placa.cut(shp_bolt1)

    # añadimos un tornillo en la posición 9x1x1
    shp_bolt2 = fcfun.shp_cyl(3., 10., normal = VZ, pos = FreeCAD.Vector(90,10,0))

    # sustraemos la forma del segundo tornillo de la placa
    shp_placa_2hole = shp_placa_1hole.cut(shp_bolt2)

    # añadimos un tornillo en la posición 9x9x1
    shp_bolt3 = fcfun.shp_cyl(3., 10., normal = VZ, pos = FreeCAD.Vector(90,90,0))

    # sustraemos la forma del tercero tornillo de la placa
    shp_placa_3hole = shp_placa_2hole.cut(shp_bolt3)

    # añadimos un tornillo en la posición 1x9x1
    shp_bolt4 = fcfun.shp_cyl(3., 10., normal = VZ, pos = FreeCAD.Vector(10,90,0))

    # sustraemos la forma del cuarto tornillo de la placa
    shp_placa_4hole = shp_placa_3hole.cut(shp_bolt4)
    
    # convertimos la placa con cuatro tornillos en objeto
    placa_4hole = FreeCAD.ActiveDocument.addObject("Part::Feature","Placa_perforada")
    placa_4hole.Shape = shp_placa_4hole
    
    # generamos cuatro tornillos individualmente y los convertimos a objetos individualmente
    tornillo_1 = fc_clss.Din912Bolt(metric = 3, shank_l = 10,
                                    shank_l_adjust = 0,
                                    shank_out = 0,
                                    head_out = 0,
                                    axis_h = -VZ, axis_d = None, axis_w = None,
                                    pos_h = 0, pos_d = 0, pos_w = 0,
                                    pos = V0+FreeCAD.Vector(10,10,10),
                                    model_type = 0,
                                    name = 'bolt1')
    tornillo_2 = fc_clss.Din912Bolt(metric = 3, shank_l = 10,
                                    shank_l_adjust = 0,
                                    shank_out = 0,
                                    head_out = 0,
                                    axis_h = -VZ, axis_d = None, axis_w = None,
                                    pos_h = 0, pos_d = 0, pos_w = 0,
                                    pos = V0+FreeCAD.Vector(90,10,10),
                                    model_type = 0,
                                    name = 'bolt2')
    tornillo_3 = fc_clss.Din912Bolt(metric = 3, shank_l = 10,
                                    shank_l_adjust = 0,
                                    shank_out = 0,
                                    head_out = 0,
                                    axis_h = -VZ, axis_d = None, axis_w = None,
                                    pos_h = 0, pos_d = 0, pos_w = 0,
                                    pos = V0+FreeCAD.Vector(90,90,10),
                                    model_type = 0,
                                    name = 'bolt3')
    tornillo_4 = fc_clss.Din912Bolt(metric = 3, shank_l = 10,
                                    shank_l_adjust = 0,
                                    shank_out = 0,
                                    head_out = 0,
                                    axis_h = -VZ, axis_d = None, axis_w = None,
                                    pos_h = 0, pos_d = 0, pos_w = 0,
                                    pos = V0+FreeCAD.Vector(10,90,10),
                                    model_type = 0,
                                    name = 'bolt4')
class placa(shp_clss.Obj3D):
    """ 
       w_0       w_1        w_2
        .         .          .
        .         .          .
        _____________________  _ _ _ h_1
       /                    /| _ _ _ d_2 h_0
      /                    / /
     /                    / / _ _ _ d_1
    /____________________/ /
    |____________________|/ _ _ _ d_0
    """
    def __init__(self, w, d, h, pos):
        shp_clss.Obj3D.__init__(self,axis_d = VY, axis_w=V0, axis_h=VZ)
        self.shp_placa = fcfun.shp_box_dir_xtr(box_w=w, box_d=d, box_h=h, fc_axis_h=VZ, fc_axis_d=VY, fc_axis_w=V0, cw=0, cd=0, ch=0, pos=pos)

class placa_con_tornillos(fc_clss.Din912Bolt, placa):
    def __init__(self,d,w,h,pos):
        placa.__init__(self,w,d,h,pos)
        shp_placa = self.shp_placa

        metric = 3
        bolt_dict = kcomp.D912[metric]
        thread_l = 18
        shank_l = 30
        shp_clss.ShpBolt.__init__(self,shank_r = bolt_dict['d']/2.,
                                       shank_l = shank_l,
                                       head_r = bolt_dict['head_r'],
                                       head_l = bolt_dict['head_l'],
                                       thread_l = thread_l,
                                       head_type = 0, # cylindrical. 1: hexagonal
                                       socket_l = bolt_dict['head_l'],
                                       socket_2ap = bolt_dict['ap2'],
                                       shank_out = 0,
                                       head_out = 1,
                                       axis_h = -VZ, axis_d = None, axis_w = None,
                                       pos_h = 0, pos_d = 0, pos_w = 0,
                                       pos = pos + FreeCAD.Vector(w*0.1,d*0.1,h))
        shp_placa = shp_placa.cut(self.shp)

        shp_clss.ShpBolt.__init__(self,shank_r = bolt_dict['d']/2.,
                                       shank_l = shank_l,
                                       head_r = bolt_dict['head_r'],
                                       head_l = bolt_dict['head_l'],
                                       thread_l = thread_l,
                                       head_type = 0, # cylindrical. 1: hexagonal
                                       socket_l = bolt_dict['head_l'],
                                       socket_2ap = bolt_dict['ap2'],
                                       shank_out = 0,
                                       head_out = 1,
                                       axis_h = -VZ, axis_d = None, axis_w = None,
                                       pos_h = 0, pos_d = 0, pos_w = 0,
                                       pos = pos + FreeCAD.Vector(w*0.9,d*0.1,h))
        shp_placa = shp_placa.cut(self.shp)

        shp_clss.ShpBolt.__init__(self,shank_r = bolt_dict['d']/2.,
                                       shank_l = shank_l,
                                       head_r = bolt_dict['head_r'],
                                       head_l = bolt_dict['head_l'],
                                       thread_l = thread_l,
                                       head_type = 0, # cylindrical. 1: hexagonal
                                       socket_l = bolt_dict['head_l'],
                                       socket_2ap = bolt_dict['ap2'],
                                       shank_out = 0,
                                       head_out = 1,
                                       axis_h = -VZ, axis_d = None, axis_w = None,
                                       pos_h = 0, pos_d = 0, pos_w = 0,
                                       pos = pos + FreeCAD.Vector(w*0.9,d*0.9,h))
        shp_placa = shp_placa.cut(self.shp)

        shp_clss.ShpBolt.__init__(self,shank_r = bolt_dict['d']/2.,
                                       shank_l = shank_l,
                                       head_r = bolt_dict['head_r'],
                                       head_l = bolt_dict['head_l'],
                                       thread_l = thread_l,
                                       head_type = 0, # cylindrical. 1: hexagonal
                                       socket_l = bolt_dict['head_l'],
                                       socket_2ap = bolt_dict['ap2'],
                                       shank_out = 0,
                                       head_out = 1,
                                       axis_h = -VZ, axis_d = None, axis_w = None,
                                       pos_h = 0, pos_d = 0, pos_w = 0,
                                       pos = pos + FreeCAD.Vector(w*0.1,d*0.*9,h))
        self.shp_placa_con_tornillos = shp_placa.cut(self.shp)
        #placa con tornillos tertminada


class fco_placa_con_tornillos(placa_con_tornillos):
    def __init__(self,w,d,h,pos):
        fco = FreeCAD.ActiveDocument.addObject("Part::Feature","Placa con tornillos")
        placa_con_tornillos.__init__(self,w,d,h,pos) # return self.shp
        metric = 3
        bolt_dict = kcomp.D912[metric]
        thread_l = 18
        shank_l = 30
        shp_clss.ShpBolt.__init__(self,shank_r = bolt_dict['d']/2.,
                                       shank_l = shank_l,
                                       head_r = bolt_dict['head_r'],
                                       head_l = bolt_dict['head_l'],
                                       thread_l = thread_l,
                                       head_type = 0, # cylindrical. 1: hexagonal
                                       socket_l = bolt_dict['head_l'],
                                       socket_2ap = bolt_dict['ap2'],
                                       shank_out = 0,
                                       head_out = 1,
                                       axis_h = -VZ, axis_d = None, axis_w = None,
                                       pos_h = 0, pos_d = 0, pos_w = 0,
                                       pos = pos + FreeCAD.Vector(w*0.1,d*0.1,h))

        self.shp_placa_con_tornillos = self.shp_placa_con_tornillos.fuse(self.shp)

        shp_clss.ShpBolt.__init__(self,shank_r = bolt_dict['d']/2.,
                                       shank_l = shank_l,
                                       head_r = bolt_dict['head_r'],
                                       head_l = bolt_dict['head_l'],
                                       thread_l = thread_l,
                                       head_type = 0, # cylindrical. 1: hexagonal
                                       socket_l = bolt_dict['head_l'],
                                       socket_2ap = bolt_dict['ap2'],
                                       shank_out = 0,
                                       head_out = 1,
                                       axis_h = -VZ, axis_d = None, axis_w = None,
                                       pos_h = 0, pos_d = 0, pos_w = 0,
                                       pos = pos + FreeCAD.Vector(w*0.1,d*0.9,h))

        self.shp_placa_con_tornillos = self.shp_placa_con_tornillos.fuse(self.shp)
        
        shp_clss.ShpBolt.__init__(self,shank_r = bolt_dict['d']/2.,
                                       shank_l = shank_l,
                                       head_r = bolt_dict['head_r'],
                                       head_l = bolt_dict['head_l'],
                                       thread_l = thread_l,
                                       head_type = 0, # cylindrical. 1: hexagonal
                                       socket_l = bolt_dict['head_l'],
                                       socket_2ap = bolt_dict['ap2'],
                                       shank_out = 0,
                                       head_out = 1,
                                       axis_h = -VZ, axis_d = None, axis_w = None,
                                       pos_h = 0, pos_d = 0, pos_w = 0,
                                       pos = pos + FreeCAD.Vector(w*0.9,d*0.9,h))

        self.shp_placa_con_tornillos = self.shp_placa_con_tornillos.fuse(self.shp)
        
        shp_clss.ShpBolt.__init__(self,shank_r = bolt_dict['d']/2.,
                                       shank_l = shank_l,
                                       head_r = bolt_dict['head_r'],
                                       head_l = bolt_dict['head_l'],
                                       thread_l = thread_l,
                                       head_type = 0, # cylindrical. 1: hexagonal
                                       socket_l = bolt_dict['head_l'],
                                       socket_2ap = bolt_dict['ap2'],
                                       shank_out = 0,
                                       head_out = 1,
                                       axis_h = -VZ, axis_d = None, axis_w = None,
                                       pos_h = 0, pos_d = 0, pos_w = 0,
                                       pos = pos + FreeCAD.Vector(w*0.9,d*0.1,h))

        self.shp_placa_con_tornillos = self.shp_placa_con_tornillos.fuse(self.shp)
        
        fco.Shape = self.shp_placa_con_tornillos

def Prisma_hueco():
    # generamos una caja de 100x100x100 como base de este ejemplo
    shp_caja = fcfun.shp_box_dir_xtr(100,100,100,fc_axis_h=VZ,fc_axis_d=VY,fc_axis_w=V0,cw=0,cd=0,ch=0,pos=V0)
    # generamos una segunda forma que será una segunda caja de 100x80x80
    shp_caja_2 = fcfun.shp_box_dir_xtr(100,80,80,fc_axis_h=VZ,fc_axis_d=VY,fc_axis_w=V0,cw=0,cd=0,ch=0,pos=V0+FreeCAD.Vector(0,10,10))
    # restamos a shp_caja shp_caja_2 para realizar un prisma hueco por una cara
    shp_caja = shp_caja.cut(shp_caja_2)
    # PRUEBA DE LA GENERACIÓN DEL SHAPE POR FASES
        #form1 = FreeCAD.ActiveDocument.addObject("Part::Feature","Prisma hueco 1")
        #form1.Shape = shp_caja
    # generamos una tercera forma que será una tercera caja de 80x100x80
    shp_caja_3 = fcfun.shp_box_dir_xtr(80,100,80,fc_axis_h=VZ,fc_axis_d=VY,fc_axis_w=V0,cw=0,cd=0,ch=0,pos=V0+FreeCAD.Vector(10,0,10))
    # restamos a shp_form shp_caja_3 para realizar un prisma hueco por dos caras
    shp_caja = shp_caja.cut(shp_caja_3)
    # PRUEBA DE LA GENERACIÓN DEL SHAPE POR FASES
        #form2 = FreeCAD.ActiveDocument.addObject("Part::Feature","Prisma hueco 2")
        #form2.Shape = shp_caja
    # generamos una cuarta forma que será una cuarta caja de 80x80x100
    shp_caja_4 = fcfun.shp_box_dir_xtr(80,80,100,fc_axis_h=VZ,fc_axis_d=VY,fc_axis_w=V0,cw=0,cd=0,ch=0,pos=V0+FreeCAD.Vector(10,10,0))
    # restamos a shp_form shp_caja_4 para realizar un prisma hueco por dos caras
    shp_caja = shp_caja.cut(shp_caja_4)
    form = FreeCAD.ActiveDocument.addObject("Part::Feature","Prisma hueco")
    form.Shape = shp_caja.removeSplitter()

def silla_fun():
    # vamos a generar una silla sencilla con primas

    # Primero hacemos el asiento
    shp_silla = fcfun.shp_box_dir_xtr(box_w=450,box_d=450,box_h=25,fc_axis_h=VZ,fc_axis_d=VY,fc_axis_w=V0,cw=0,cd=0,ch=0,pos=V0)
    # hacemos el respaldo
    shp_respaldo = fcfun.shp_box_dir_xtr(box_w=450,box_d=25,box_h=600,fc_axis_h=VZ,fc_axis_d=VY,fc_axis_w=V0,cw=0,cd=0,ch=0,pos=V0+FreeCAD.Vector(0,425,0))
    shp_silla = shp_silla.fuse(shp_respaldo)
    
    shp_pata_1 = fcfun.shp_box_dir_xtr(box_w=25,box_d=25,box_h=400,fc_axis_h=VZ,fc_axis_d=VY,fc_axis_w=V0,cw=0,cd=0,ch=0,pos=V0+FreeCAD.Vector(0,425,-400))
    shp_silla = shp_silla.fuse(shp_pata_1)
    shp_pata_2 = fcfun.shp_box_dir_xtr(box_w=25,box_d=25,box_h=400,fc_axis_h=VZ,fc_axis_d=VY,fc_axis_w=V0,cw=0,cd=0,ch=0,pos=V0+FreeCAD.Vector(425,425,-400))
    shp_silla = shp_silla.fuse(shp_pata_2)
    shp_pata_3 = fcfun.shp_box_dir_xtr(box_w=25,box_d=25,box_h=400,fc_axis_h=VZ,fc_axis_d=VY,fc_axis_w=V0,cw=0,cd=0,ch=0,pos=V0+FreeCAD.Vector(425,0,-400))
    shp_silla = shp_silla.fuse(shp_pata_3)
    shp_pata_4 = fcfun.shp_box_dir_xtr(box_w=25,box_d=25,box_h=400,fc_axis_h=VZ,fc_axis_d=VY,fc_axis_w=V0,cw=0,cd=0,ch=0,pos=V0+FreeCAD.Vector(0,0,-400))
    shp_silla = shp_silla.fuse(shp_pata_4)

    silla = FreeCAD.ActiveDocument.addObject("Part::Feature","Silla")
    silla.Shape = shp_silla.removeSplitter()

class pata(shp_clss.Obj3D):
    """ pata de la silla
   w_0  w_1
    .    .
    .____.  _ _ _ h_2
    /___/|
    |   ||
    |   ||
    |   ||
    |   || _ _ _ h_1
    |   ||
    |   ||
    |   ||
    |___|/ _ _ _ h_0
    
    prisma rectangular
    """
    def __init__(self, w, d, h, pos):
        shp_clss.Obj3D.__init__(self,axis_d = VY, axis_w=V0, axis_h=VZ)
        self.shp_pata = fcfun.shp_box_dir_xtr(box_w=w, box_d=d, box_h=h, fc_axis_h=VZ, fc_axis_d=VY, fc_axis_w=V0, cw=0, cd=0, ch=0, pos=pos)
        self.shp_pata.h_0 = pos
        self.shp_pata.h_1 = pos + h/2
        self.shp_pata.h_2 = pos + h
        self.shp_pata.w_0 = pos 
        self.shp_pata.w_1 = pos + w/2
        self.shp_pata.w_2 = pos + w
        self.shp_pata.d_0 = pos
        self.shp_pata.d_1 = pos + d/2
        self.shp_pata.d_2 = pos + d

"""def shp_pata_fun(w, d, h, pos):
    shp_pata = fcfun.shp_box_dir_xtr(box_w=w, box_d=d, box_h=h, fc_axis_h=VZ, fc_axis_d=VY, fc_axis_w=V0, cw=0, cd=0, ch=0, pos=pos)
    return (shp_pata)"""

class respaldo(shp_clss.Obj3D):
    """ respaldo de la silla
   w_0          w_1             w_2
    .            .               .
    .            .               .
     ____________________________  _ _ _ h_2
    /___________________________/|
    |                           ||
    |                           ||
    |                           ||
    |                           ||
    |                           || _ _ _ h_1
    |                           ||
    |                           ||
    |                           ||
    |                           ||
    |                           ||
    |                           || _ _ _ h_0
    |___________________________|/
    
    """
    def __init__(self, w, d, h, pos):
        shp_clss.Obj3D.__init__(self,axis_d = VY, axis_w=V0, axis_h=VZ)
        self.shp_respaldo = fcfun.shp_box_dir_xtr(box_w=w, box_d=d, box_h=h, fc_axis_h=VZ, fc_axis_d=VY, fc_axis_w=V0, cw=0, cd=0, ch=0, pos=pos)
        self.shp_respaldo.h_0 = pos
        self.shp_respaldo.h_1 = pos + h/2
        self.shp_respaldo.h_2 = pos + h
        self.shp_respaldo.w_0 = pos 
        self.shp_respaldo.w_1 = pos + w/2
        self.shp_respaldo.w_2 = pos + w
        self.shp_respaldo.d_0 = pos
        self.shp_respaldo.d_1 = pos + d/2
        self.shp_respaldo.d_2 = pos + d        

"""def shp_respando_fun(w, d, h, pos):
    shp_respaldo = fcfun.shp_box_dir_xtr(box_w=w, box_d=d, box_h=h, fc_axis_h=VZ, fc_axis_d=VY, fc_axis_w=V0, cw=0, cd=0, ch=0, pos=pos)
    return (shp_respaldo)"""

class asiento(shp_clss.Obj3D):
    """ asiento de la silla
       w_0       w_1        w_2
        .         .          .
        .         .          .
        _____________________  _ _ _ h_1
       /                    /| _ _ _ d_2 h_0
      /                    / /
     /                    / / _ _ _ d_1
    /____________________/ /
    |____________________|/ _ _ _ d_0
    """
    def __init__(self, w, d, h, pos):
        shp_clss.Obj3D.__init__(self,axis_d = VY, axis_w=V0, axis_h=VZ)
        self.shp_asiento = fcfun.shp_box_dir_xtr(box_w=w, box_d=d, box_h=h, fc_axis_h=VZ, fc_axis_d=VY, fc_axis_w=V0, cw=0, cd=0, ch=0, pos=pos)
        self.shp_asiento.h_0 = pos
        self.shp_asiento.h_1 = pos + h/2
        self.shp_asiento.h_2 = pos + h
        self.shp_asiento.w_0 = pos 
        self.shp_asiento.w_1 = pos + w/2
        self.shp_asiento.w_2 = pos + w
        self.shp_asiento.d_0 = pos
        self.shp_asiento.d_1 = pos + d/2
        self.shp_asiento.d_2 = pos + d

"""def shp_asiento_fun(w, d, h, pos):
    shp_asiento = fcfun.shp_box_dir_xtr(box_w=w, box_d=d, box_h=h, fc_axis_h=VZ, fc_axis_d=VY, fc_axis_w=V0, cw=0, cd=0, ch=0, pos=pos)
    return (shp_asiento)"""

"""class silla(shp_clss.Obj3D): #Funciona
    def __init__(self,w,d,h,h_resp,pos):
        shp_clss.Obj3D.__init__(self,axis_d = VY, axis_w=V0, axis_h=VZ)
        shp_asiento = shp_asiento_fun(w,d,25,pos+FreeCAD.Vector(0,0,h-h_resp))
        shp_silla = shp_asiento.removeSplitter()
        # Tenemos asiento
        shp_respaldo = shp_respando_fun(w,25,h_resp,pos+FreeCAD.Vector(0,w-25,h-h_resp))
        shp_silla = shp_silla.fuse(shp_respaldo) 
        # Asiento con resplado
        shp_silla = shp_silla.fuse(shp_pata_fun(25,25,h-h_resp,pos+FreeCAD.Vector(0,0,0)))
        shp_silla = shp_silla.fuse(shp_pata_fun(25,25,h-h_resp,pos+FreeCAD.Vector(w-25,0,0)))
        shp_silla = shp_silla.fuse(shp_pata_fun(25,25,h-h_resp,pos+FreeCAD.Vector(w-25,d-25,0)))
        shp_silla = shp_silla.fuse(shp_pata_fun(25,25,h-h_resp,pos+FreeCAD.Vector(0,d-25,0)))
        # Asiento con respaldo y patas
        self.shp = shp_silla.removeSplitter()"""

class silla(asiento, respaldo, pata):
    def __init__(self,w,d,h,h_resp,pos):
        asiento.__init__(self,w,d,25,pos+FreeCAD.Vector(0,0,h-h_resp)) # return self.shp_asiento
        shp_silla = self.shp_asiento
        # Tenemos asiento
        respaldo.__init__(self,w,25,h_resp,pos+FreeCAD.Vector(0,w-25,h-h_resp)) # return self.shp_respaldo
        shp_silla = shp_silla.fuse(self.shp_respaldo) 
        # Tenemos asiento con respaldo
        """ Como hacemos para tener distintos shape con el mismo nombre?
        self.shp_silla.d_0 es distinto para cada pata pero no podremos distinguierlo como está ahora mismo"""
        pata.__init__(self,25,25,h-h_resp,pos+FreeCAD.Vector(0,0,0))# return self.shp_pata
        shp_silla = shp_silla.fuse(self.shp_pata)
        # Tenemos una pata
        pata.__init__(self,25,25,h-h_resp,pos+FreeCAD.Vector(w-25,0,0))# return self.shp_pata
        shp_silla = shp_silla.fuse(self.shp_pata)
        # Tenemos dos patas
        pata.__init__(self,25,25,h-h_resp,pos+FreeCAD.Vector(w-25,d-25,0))# return self.shp_pata
        shp_silla = shp_silla.fuse(self.shp_pata)
        # Tenemos tres patas
        pata.__init__(self,25,25,h-h_resp,pos+FreeCAD.Vector(0,d-25,0))# return self.shp_pata
        shp_silla = shp_silla.fuse(self.shp_pata)
        # Tenemos la silla entera
        self.shp = shp_silla.removeSplitter()

class fco_silla(silla):
    def __init__(self,w,d,h,h_resp,pos):
        fco = FreeCAD.ActiveDocument.addObject("Part::Feature","Silla")
        silla.__init__(self,w,d,h,h_resp,pos) # return self.shp
        fco.Shape = self.shp