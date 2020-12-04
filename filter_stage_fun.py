# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# -- Function Filter stage
# ----------------------------------------------------------------------------
# -- (c) David Muñoz Bernal
# ----------------------------------------------------------------------------
#
# This function includes:
#   - Filter holder
#   - Idler pulley and belt tensioner
#   - Stepper motor holder
#
#  -------------------- Filter holder:
#
#                     axis_h
#                        :
#                        :
#         ___    ___     :     ___    ___       ____
#        |   |  |   |    :    |   |  |   |     | || |
#        |...|__|___|____:____|___|__|...|     |_||_|
#        |         _           _         |     |  ..|
#        |        |o|         |o|        |     |::  |
#        |        |o|         |o|        |     |::  |
#        |                               |     |  ..|
#        |                               |     |  ..|
#        |      (O)             (O)      |     |::  |
#        |                               |     |  ..|
#        |                               |     |  ..|
#        |  (O)   (o)   (O)   (o)   (O)  |     |::  |
#        |_______________________________|     |  ..|
#        |_______________________________|     |     \_________________
#        |  :.........................:  |     |       :............:  |
#        |   :                       :   |     |        :          :   |
#        |___:___________x___________:___|     x________:__________:___|.>axis_d
#
#
#         _______________x_______________ ......> axis_w
#        |____|                     |____|
#        |____   <  )          (  >  ____|
#        |____|_____________________|____|
#        |_______________________________|
#        |  ___________________________  |
#        | | ......................... | |
#        | | :                       : | |
#        | | :                       : | |
#        | | :                       : | |
#        | | :.......................: | |
#        | |___________________________| |
#         \_____________________________/
#                        :
#                        :
#                        :
#                      axis_d
#
#
#  - Idler pulley and belt tensioner
#
#                           axis_h            axis_h 
#                            :                  :
# ....................... ___:___               :______________
# :                      |  ___  |     pos_h:   |  __________  |---
# :                      | |   | |        3     | |__________| | : |
# :+hold_h              /| |___| |\       1,2   |________      |---
# :                    / |_______| \            |        |    /      
# :             . ____/  |       |  \____       |________|  /
# :..hold_bas_h:.|_::____|_______|____::_|0     |___::___|/......axis_d
#                                               0    1           2: pos_d
#
#
#
#                 .... hold_bas_w ........
#                :        .hold_w.        :
#              aluprof_w :    wall_thick  :
#                :..+....:      +         :
#                :       :     : :        :
#       pos_w:   2__1____:___0_:_:________:........axis_w
#                |    |  | :   : |  |     |    :
#                |  O |  | :   : |  |  O  |    + hold_bas_d
#                |____|__| :   : |__|_____|....:
#                        | :   : |
#                        |_:___:_|
#                          |   |
#                           \_/
#                            :
#                            :
#                           axis_d

import os
import sys
import inspect
import logging
import math
import FreeCAD
import FreeCADGui
import Part
import DraftVecUtils

# to get the current directory. Freecad has to be executed from the same
# directory this file is
filepath = os.getcwd()
# to get the components
# In FreeCAD can be added: Preferences->General->Macro->Macro path
sys.path.append(filepath) 
sys.path.append(filepath + '/' + 'comps')
#sys.path.append(filepath + '/../../' + 'comps')

# path to save the FreeCAD files
fcad_path = filepath + '/../freecad/'

# path to save the STL files
stl_path = filepath + '/../stl/'

import kcomp
import fcfun
import shp_clss
import fc_clss
import tensioner_clss
import filter_holder_clss
import comps
import partgroup
import parts
import partset
import beltcl
import kcomp

from fcfun import V0, VX, VY, VZ, V0ROT
from fcfun import VXN, VYN, VZN

doc = FreeCAD.ActiveDocument

axis_mov   = VY
axis_front = VX
axis_up    = VZ

def filter_stage_fun( move_l, Filter_Length, Filter_Width, nut_hole, tens_stroke_Var, base_w, wall_thick_Var, size_motor, h_motor, thik_motor, pos):
                    #move_l => mov_distance
                    #nut_hole => bolttens_mtr
                    #tens_stroke_Var => tens_stroke
                    #base_w => aluprof_w
                    #wall_thick_Var => wall_thick

    # distance in mm that the filter is going to move
    mov_distance = move_l #60.

    # width of the timing belt
    belt_w = 6.

    # position of the filter
    # position of the filter in the middle
    filter_pos_0 = pos
    # position of the filter relative to it 0 position
    filter_mov = DraftVecUtils.scale(axis_mov,0)
    filter_pos = filter_pos_0 + filter_mov
    # the point of this position is the filter center of symmetry and its base
    filter_pos_d = 9
    filter_pos_w = 0
    filter_pos_h = 1

    # width of the belt
    belt_w =  6.
    # height of the belt clamp
    beltclamp_h = belt_w + 2
    # length of the motor shaft
    motorshaft_l = 24.

    # width of the aluminum profile
    aluprof_w = base_w     #Base del tension holder  #20.
    # dictionary with the dimensions of the aluminum profile
    aluprof_dict = kcomp.ALU_PROF[aluprof_w]

    belt_dict = kcomp.GT[2]

    # ------ linear guide for the filter holder
    linguide_dict = kcomp.SEB15A
    linguide_blk_dict = linguide_dict['block']
    linguide_rail_dict = linguide_dict['rail']
    bolt_linguide_mtr = linguide_blk_dict['boltd']

    filter_holder = filter_holder_clss.PartFilterHolder(
                    filter_l = Filter_Length,
                    filter_w = Filter_Width,
                    filter_t = 2.5,
                    base_h = 6.,
                    hold_d = 10., #12
                    filt_supp_in = 2.,
                    filt_rim = 3.,
                    filt_cen_d = 30,
                    fillet_r = 1.,
                    boltcol1_dist = 20/2.,
                    boltcol2_dist = 12.5,
                    boltcol3_dist = 25,
                    boltrow1_h = 0,
                    boltrow1_2_dist = 12.5,
                    boltrow1_3_dist = 20.,
                    boltrow1_4_dist = 25.,
                    bolt_cen_mtr = 4, 
                    bolt_linguide_mtr = bolt_linguide_mtr,
                    beltclamp_t = 3.,
                    beltclamp_l = 12.,
                    beltclamp_h = beltclamp_h,
                    clamp_post_dist = 4.,
                    sm_beltpost_r = 1.,
                    tol = kcomp.TOL,
                    axis_d = axis_front,
                    axis_w = axis_mov,
                    axis_h = axis_up,
                    pos_d = filter_pos_d,
                    pos_w = filter_pos_w,
                    pos_h = filter_pos_h,
                    pos = filter_pos,
                    name = 'filter_holder')

    filter_holder.set_color(fcfun.YELLOW_05)

    


    # ------ linear guide for the filter holder
    # block:
    partLinGuideBlock = comps.PartLinGuideBlock (
                                        block_dict = linguide_blk_dict,
                                        rail_dict  = linguide_rail_dict,
                                        axis_d = axis_mov,
                                        axis_w = axis_up,
                                        axis_h = axis_front,
                                        pos_d = 0, pos_w = -2, pos_h = 3,
                                        pos = filter_holder.get_pos_dwh(0,0,3) )


    # 4 bolts to attach the filter holder to the linear guide
    # the bolt head has to be touching the hole for the bolt: pos_d = 5
    bolt_head_pos = filter_holder.get_o_to_d(5)
    for w_i in [-2, 2]:
        for d_i in [-1, 1]:
            # positions of the bolts at the linear guide
            filter_bolt_pos_i = (  partLinGuideBlock.get_pos_dwh(d_i, w_i, 3)
                                + bolt_head_pos)
            fc_clss.Din912Bolt(metric = bolt_linguide_mtr,
                            shank_l = (  bolt_head_pos.Length
                                        + partLinGuideBlock.bolt_l),
                            shank_l_adjust = -1, # shorter to shank_l
                            axis_h = axis_front.negative(),
                            pos_h = 3,
                            pos = filter_bolt_pos_i,
                            name = 'filter_bolt_w' + str(w_i) + '_d' + str(d_i)
                            )

            
    

    # rail
    # the rail will be in the direcion of:
    #   axis_up: defined by partLinGuideBlock
    #   axis_front: defined by partLinGuideBlock
    #   axis_mov: NOT defined by partLinGuideBlock, because it moves along
    #             this axis
    #             Defined by filter_pos_0

    pos_fromblock = partLinGuideBlock.get_pos_dwh(0,0,4)
    #dif_pos = pos_fromblock - filter_mov
    #min_axis_mov = DraftVecUtils.project(dif_pos, axis_mov)

    rail_xtr_d = 10.

    pos_rail = (  pos_fromblock - filter_mov
                + DraftVecUtils.scale(axis_mov, rail_xtr_d/2.))

    partLinGuideRail = comps.PartLinGuideRail (
                            rail_d = (   filter_holder.tot_w + mov_distance
                                        + rail_xtr_d),
                            rail_dict = linguide_rail_dict,
                            boltend_sep = 0,
                            axis_d = axis_mov,
                            axis_w = axis_up,
                            axis_h = axis_front,
                            # center along axis_d and axis_d, base along axis_h
                            pos_d = 2, pos_w = 0, pos_h = 0,
                            pos = pos_rail)

                        





    # get the position of the belt of the filter, at center of symmetry
    belt_pos_mov = filter_holder.get_pos_dwh(2,0,7)
    # get the position of the belt of the filter if not moved
    belt_pos = filter_holder.get_pos_dwh(2,0,7) - filter_mov

    tensioner_pos = (  belt_pos
                    + DraftVecUtils.scale(axis_mov,
                        mov_distance/2. + filter_holder.tot_w/2. + tens_stroke_Var)
                    + DraftVecUtils.scale(axis_up, belt_w/2.))


    # position of the set: motor pulley holder
    nemaholder_w_motor_pos = (
                    belt_pos
                    + DraftVecUtils.scale(axis_mov,
                                        - mov_distance/2.
                                        - filter_holder.tot_w/2.
                                        - aluprof_w)
                    + DraftVecUtils.scale(axis_up, belt_w/2.))

    print (str(belt_pos))
    print (str(tensioner_pos))

    # at the end of the idler tensioner, when it is all the way in
    tensioner_pos_d = 6
    #tensioner_pos_d = 2
    tensioner_pos_w = -1 # at the pulley radius
    tensioner_pos_h = 3 # middle point of the pulley

    # calculating the distance from the base of the tensioner to the middle of the
    # pulley, distance along axis_up (two planes)
    # these to sentences are equivalent
    # no need to be this complicated if using axis_z

    #tensioner_belt_h = ((DraftVecUtils.project(
    #                         tensioner_pos-pos_rail, axis_up)).Length
    #                       - aluprof_w / 2.)

    tensioner_belt_h = (pos_rail.distanceToPlane(tensioner_pos,axis_up.negative())
                        - aluprof_w/2.)

    # metric of the bolt to attach the tensioner
    boltaluprof_mtr = 4

    tensioner = tensioner_clss.TensionerSet(
                        aluprof_w = base_w,#20.,
                        belt_pos_h = tensioner_belt_h, 
                        hold_bas_h = 0,
                        hold_hole_2sides = 1,
                        boltidler_mtr = 3,
                        bolttens_mtr = nut_hole,   #métrica del tensor
                        boltaluprof_mtr = boltaluprof_mtr,
                        tens_stroke = tens_stroke_Var ,
                        wall_thick = wall_thick_Var,
                        in_fillet = 2.,
                        pulley_stroke_dist = 0,
                        nut_holder_thick = nut_hole ,   
                        opt_tens_chmf = 0,
                        min_width = 0,
                        tol = kcomp.TOL,
                        axis_d = axis_mov.negative(),
                        axis_w = axis_front.negative(),
                        axis_h = axis_up,
                        pos_d = tensioner_pos_d,
                        pos_w = tensioner_pos_w,
                        pos_h = tensioner_pos_h,
                        pos = tensioner_pos,
                        name = 'tensioner_set')

    # get_idler_tensioner gets the set, including the pulley. Either of these 2
    # would be correct
    #tensioner.get_idler_tensioner().get_idler_tensioner().set_color(fcfun.ORANGE)
    tensioner.get_idler_tensioner().set_color(fcfun.ORANGE,2)   #2: the tensioner
    tensioner.set_color(fcfun.LSKYBLUE,2) #2: the holder

    # position of the aluminum profile that supports the tensioner
    # point at the base, at the end along axis w, centered along axis_d (bolts)
    aluprof_tens_pos = tensioner.get_pos_dwh (2,-4,0)

    #distance from this end of the aluprofile to the linear guide rail

    aluprof_tens_l = (  aluprof_tens_pos.distanceToPlane(pos_rail, axis_front)
                    + aluprof_w)

    print('aluprof: ' + str(aluprof_tens_l))

    # length of the aluminum profile that supports the tensioner
    #aluprof_tens_l = tensioner.get_tensioner_holder().hold_bas_w

    aluprof_tens = comps.PartAluProf(depth = aluprof_tens_l,
                                    aluprof_dict = aluprof_dict,
                                    xtr_d = 0,
                                    #xtr_nd = aluprof_tens_l/2., # extra length
                                    xtr_nd = 0,
                                    axis_d = axis_front.negative(),
                                    axis_w = axis_mov,
                                    axis_h = axis_up,
                                    pos_d = 1, #end not counting xtr_nd
                                    pos_w = 0, # centered
                                    pos_h = 3,
                                    pos = aluprof_tens_pos)
                                    

    # Bolts for the belt tensioner
    max_tens_bolt_l = (aluprof_tens.get_h_ab(3,1).Length # space for bolt in profile
                    + tensioner.get_tensioner_holder().hold_bas_h) # base thickness
    print('shank_l ' + str(max_tens_bolt_l))
    for w_i in [-3, 3]: # position of bolts
        tens_bolt_i_pos = tensioner.get_pos_dwh(2,w_i,1)
        tens_bolt_i = partset.Din912BoltWashSet(
                                            metric  = boltaluprof_mtr,
                                            shank_l = max_tens_bolt_l,
                                            # smaller considering the washer
                                            shank_l_adjust = -2,
                                            axis_h  = axis_up.negative(),
                                            pos_h   = 3,
                                            pos_d   = 0,
                                            pos_w   = 0,
                                            pos     = tens_bolt_i_pos)


    # set with:
    # + motor holder
    # + motor
    # + pulley

    motor_holder_pos = (  belt_pos
                    + DraftVecUtils.scale(axis_mov, - mov_distance)
                    + DraftVecUtils.scale(axis_up, -(motorshaft_l - beltclamp_h)))


    #nema_size = 11
    nema_size = size_motor

    nemaholder_w_motor = partset.NemaMotorPulleyHolderSet(
                            nema_size = nema_size, 
                            motor_base_l = 32.,
                            motor_shaft_l = motorshaft_l,
                            motor_circle_r = 11.,
                            motor_circle_h = 2.,
                            motor_chmf_r = 1.,

                            pulley_pitch = 2.,
                            pulley_n_teeth = 20,
                            pulley_toothed_h = 7.5,
                            pulley_top_flange_h = 1.,
                            pulley_bot_flange_h = 0,
                            pulley_tot_h = 16.,
                            pulley_flange_d = 15.,
                            pulley_base_d = 15.,
                            #pulley_tol = 0,
                            pulley_pos_h = 5.,                        
                            hold_wall_thick = thik_motor,#4.,
                            hold_motorside_thick = 3.,
                            hold_reinf_thick = 3.,
                            hold_rail_min_h = 3.,
                            hold_rail_max_h = h_motor,#20.,
                            hold_motor_xtr_space = 2.,
                            hold_bolt_wall_d = 4.,
                            # hold_chmf_r = 1.,
                            axis_h = axis_up,
                            axis_d = axis_mov.negative(),
                            axis_w = axis_front,
                            pos_h = 11, # middle point of the pulley toothed part
                            pos_d = 0, #0: at the wall where this holder is attached
                            pos_w = 5, #5: inner radius of the pulley (to the back
                            pos = nemaholder_w_motor_pos)

    nemaholder_w_motor.set_color(fcfun.GREEN_05,2)   #2: the holder

    # aluminum profile for the motor holder

    aluprof_distance = (  aluprof_tens_pos.distanceToPlane(nemaholder_w_motor_pos,
                                                        axis_mov))

    aluprof_motor_pos = (  aluprof_tens_pos
                        - DraftVecUtils.scale(axis_mov, aluprof_distance))

    aluprof_motor = comps.PartAluProf(depth = aluprof_tens_l,
                                    aluprof_dict = aluprof_dict,
                                    xtr_d = 0,
                                    #xtr_nd = aluprof_tens_l/2., # extra length
                                    xtr_nd = 0,
                                    axis_d = axis_front.negative(),
                                    axis_w = axis_mov,
                                    axis_h = axis_up,
                                    pos_d = 1, #end not counting xtr_nd
                                    pos_w = -3, #not centered, touching the holder
                                    pos_h = 3,
                                    pos = aluprof_motor_pos)

    # get the top-right-corner:
    aluprof_linguide_pos = aluprof_motor.get_pos_dwh(5,3,3)

    aluprof_linguide = comps.PartAluProf(
                                    depth = aluprof_distance- 3*aluprof_w/2.,
                                    aluprof_dict = aluprof_dict,
                                    xtr_d = 0,
                                    xtr_nd = 0,
                                    axis_d = axis_mov,
                                    axis_w = axis_front,
                                    axis_h = axis_up,
                                    pos_d = 0, #end not counting xtr_nd
                                    pos_w = -3,
                                    pos_h = 3,
                                    pos = aluprof_linguide_pos)

    nema_motor_pull = nemaholder_w_motor.get_nema_motor_pulley()
    motor_pull = nema_motor_pull.get_gt_pulley()
    # external diameter of the motor pulley
    motor_pull_dm = 2 * (motor_pull.tooth_in_r + belt_dict['BELT_H'])

    tens_idler_set = tensioner.get_idler_tensioner()
    tens_pull = tens_idler_set.get_bear_wash_set()

    tens_pull_dm = 2 * (tens_pull.bear_r_out + belt_dict['BELT_H'])


    # d=5: center of pulley, inside
    # h=3: center of pulley on the height
    tens_pull_pos = tensioner.get_pos_dwh (5,0,3)
    # d=3: center of pulley
    # h=11: center of pulley on the height
    motor_pull_pos = nemaholder_w_motor.get_pos_dwh (3,0,11)

    pull_sep = tens_pull_pos - motor_pull_pos
    pull_sep_mov = pull_sep.dot(axis_mov)
    pull_sep_front = pull_sep.dot(axis_front.negative())

    # position of the internal side of the clamp block, closer to the motor
    # and closer to the linear guide
    filthold_clamp_pos_n = filter_holder.get_pos_dwh(1,-7,8)
    filthold_clamp_pos = filter_holder.get_pos_dwh(1,7,8)

    # distances to the belt
    motorpull_clamp_sep = filthold_clamp_pos_n - motor_pull_pos
    motorpull_clamp_sep_mov = motorpull_clamp_sep.dot(axis_mov)
    motorpull_clamp_sep_front = motorpull_clamp_sep.dot(axis_front)
    idlpull_clamp_sep_mov = (  pull_sep_mov
                            - motorpull_clamp_sep_mov
                            - filter_holder.tot_w)

    belt = beltcl.PartBeltClamped (
                        pull1_dm   = motor_pull_dm,
                        pull2_dm   = tens_pull_dm,
                        pull_sep_d = pull_sep_mov,
                        pull_sep_w = pull_sep_front,
                        clamp_pull1_d = motorpull_clamp_sep_mov,
                        clamp_pull1_w = motorpull_clamp_sep_front,
                        clamp_pull2_d = idlpull_clamp_sep_mov,
                        clamp_d = filter_holder.beltclamp_l,
                        clamp_w = filter_holder.beltclamp_t,
                        clamp_cyl_sep = filter_holder.clamp_lrbeltpostcen_dist,
                        cyl_r = filter_holder.lr_beltpost_r + belt_dict['BELT_H'],
                        belt_width = belt_w,
                        belt_thick = belt_dict['BELT_H'],
                        axis_d = axis_mov,
                        axis_w = axis_front.negative(),
                        axis_h = axis_up,
                        pos_d = 0,
                        pos_w = 0,
                        pos_h = 0,
                        pos=motor_pull_pos)

    belt.set_color(fcfun.GRAY_08)