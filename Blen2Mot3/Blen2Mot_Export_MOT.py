bl_info = {
    "name": "Blen2Mot Export",
    "blender": (3, 6, 0),
    "category": "File>Export",
    "author": "Akito",
    "version": (2, 0, 0),
    "description": "Export Animation directly to MOT",
    "warning": "Use only EULER Rotations. QUATERNION rotations will be IGNORED",
    "tracker_url": "https://github.com/akitotheanimator/God-Hand-Tools/tree/main",
}






import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty,BoolVectorProperty, FloatProperty
import os
import struct

import mathutils
from mathutils import Matrix
import math
from mathutils import Vector
import bmesh
import numpy as np


def from_ushort(half_precision: int) -> float:
    half_precision = int(half_precision)
    exponent = (half_precision >> 9) & ((1 << 6) - 1)
    significand = half_precision & ((1 << 9) - 1)
    sign = (half_precision >> 15) & 1
    biased_exponent = exponent - 47
    value = (sign * -2 + 1) * (2 ** biased_exponent) * (1 + significand / (2 ** 9))
    return value


def map_value(value, from_min, from_max, to_min, to_max):
    normalized_value = (value - from_min) / (from_max - from_min)
    mapped_value = to_min + (normalized_value * (to_max - to_min))
    return mapped_value


def to_ushort(value: float) -> int:
    binary32 = struct.pack('f', value)
    int32 = struct.unpack('I', binary32)[0]

    sign = (int32 >> 31) & 0x1
    exponent = (int32 >> 23) & 0xFF
    mantissa = int32 & 0x7FFFFF

    exponent_value = exponent - 127 + 47
    if exponent_value < 0:
        exponent_value = 0
    elif exponent_value > 63:
        exponent_value = 63
    

    significand = mantissa >> 14
    if significand > 0x1FF:
        significand = 0x1FF
    
    binary16 = (sign << 15) | (exponent_value << 9) | significand
    return binary16
    



class ExportMOT(bpy.types.Operator, ExportHelper):
    """Export God Hand Motion"""
    bl_idname = "export_scene.mot"
    bl_label = "Export Animation"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".mot"
    filter_glob: StringProperty(
        default="*.mot",
        options={'HIDDEN'},
        maxlen=255,
    )
    files: CollectionProperty(
        type=bpy.types.PropertyGroup
    )
    
    determine_dynamicaly: BoolProperty(
        name="Set property types dynaically",
        description="This allows blen2mot to decide automatically the property type of each fcurve. You can constraint the allowed output types",
        default=True,
    )
    sp: BoolProperty(
        name = "Single Pose",
        description = "(when available, export curves that doesnt move as a single pose)",
        default = True,
    )
    qp: BoolProperty(
        name = "Quantized keyframes",
        description = "(when available, export curves that doesnt move too much as quantized curves)",
        default = True,
    )
    qpp: BoolProperty(
        name = "Quantized Precision keyframes",
        description = "(when available, export curves that moves too much as precision quantize curves)",
        default = True,
    )
    
    loops: BoolProperty(
        name = "Animation loops",
        description = "this will only show up if you dont have blen2mot installed. Bascially this sets if the animation is going to be looped or not",
        default = True,
    )
    
    
    
    threshold: FloatProperty(
        name = "Movement Threshold",
        description = "if the absolute value of the difference between the values of the first keyframe and last keyframe is lower than threshold, the curve will be determinated as a pose, not a curve.\n\nSet the threshold value to 0 if you want all of the animation curves to be processed as curves",
        default = 0.02,
    )
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object  
        selected_pose_bones = [pose_bone for pose_bone in active_object.pose.bones if pose_bone.bone.select]  
        return active_object is not None
        
    def draw(self, context):
        layout = self.layout   
        if not hasattr(bpy.context.scene.properties_MOT, 'loop_MOT'):
           layout.label(text="Blen2Mot couldn't be found.",icon="INFO")
           layout.label(text="you will not be able to tweak")
           layout.label(text="some configurations such as:")
           layout.label(text="* Precision bones")
           layout.label(text="* Curve Flags")
           layout.separator()
            
        layout.label(text="Allowed curve properties:")
        lt1 = layout.box()
        layout.separator()
        lt1.prop(self,"sp")
        lt1.prop(self,"qp")
        lt1.prop(self,"qpp")
        lt1.prop(self,"threshold")
        
        print(bpy.context.scene.properties_MOT.loop_MOT)
        if not hasattr(bpy.context.scene.properties_MOT, 'loop_MOT'):
            layout.prop(self,"loops")
           
    def execute(self, context):
     bpy.context.scene.tool_settings.use_keyframe_insert_auto = False 
     loopvalue = self.loops
     if hasattr(bpy.context.scene.properties_MOT, 'loop_MOT'):
         loopvalue = bpy.context.scene.properties_MOT.loop_MOT
        
     layout = self.layout      
     armature = bpy.context.object
     
     directory = self.filepath
     directory = directory.replace(os.path.basename(directory),"")
     directory = directory[:-1]
     bpy.context.scene.tool_settings.use_keyframe_insert_auto = False 
     bpy.context.scene.frame_current = 0
     bpy.context.view_layer.update()

     
     
     
     action = armature.animation_data.action if armature and armature.animation_data else None
     if action is None:
            self.report({'WARNING'}, "No action (animation) found.")
            return {'CANCELLED'}
        
        
        
     for file_elem in self.files:
        file_path = f"{directory}/{file_elem.name}"
        with open(file_path, "wb") as file:
            
            file.write(struct.pack('I', 862090349))
            
            tmp1 = file.tell()
            file.write((0).to_bytes(2,"little"))
            
            if len(action.fcurves) > 255:
                self.report({'WARNING'}, "There's more than 255 curves registered on the animation, delete some channels.")
                return {'CANCELLED'}
            FCO = 0
            lcountf = file.tell()
            file.write(struct.pack('B', (len(action.fcurves))))
            file.write(struct.pack('B', (1 if loopvalue else 0)))
            
            
            
            list_animation = []
            totalLength = 0
            for fcurve in action.fcurves:
                    spli = fcurve.data_path.split('"')
                    #print(fcurve.data_path)
                    if len(spli) < 2:
                       self.report({'WARNING'}, "The Armature Object was animated. delete the armature keyframes and try again.")
                       return {'CANCELLED'}
                    proP = spli[2].split(".")[1]
                    
                    lv0 = fcurve.keyframe_points[0].co.y
                    lv1 = fcurve.keyframe_points[len(fcurve.keyframe_points)-1].co.y
                    fv = abs(lv0 - lv1)
                    file.write((0).to_bytes(12,"little"))
                
                
                
            file.write((4294967167).to_bytes(12,"little"))
            fEnd = file.tell()
            file.seek(8)
            
            
            
            
            
            
            bone_names = [(int(bone.name.replace("root","0")) -1) for bone in armature.pose.bones]
            bone_names.sort()
            for bones in bone_names:
                for fcurve in action.fcurves:
                    spli = fcurve.data_path.split('"')
                    bName = int(spli[1].replace("root","0")) -1
                    bOGn = spli[1]
                    
                    curveI = fcurve.array_index
                    proP = spli[2].split(".")[1]
                    
                    lv0 = fcurve.keyframe_points[0].co.y
                    lv1 = fcurve.keyframe_points[len(fcurve.keyframe_points)-1].co.y
                    fv = abs(lv0 - lv1)
                    
                    
                    vO = 0.0
                    lv0 = 0.0
                    for fcurves in range(1, len(fcurve.keyframe_points)):
                        vt1t = fcurve.keyframe_points[fcurves].co.y
                        if proP == "rotation_euler":
                           vt1t *= (180 / math.pi)
                           
                        lv1 = vt1t
                        vO += abs(lv1 - lv0)
                        lv0 = vt1t       
                    if bName == bones:
                       FCO += 1
                       if fcurve.keyframe_points[len(fcurve.keyframe_points)-1].co.x > totalLength:
                          totalLength = int(fcurve.keyframe_points[len(fcurve.keyframe_points)-1].co.x)
                       
                       
                       file.write(struct.pack('b', bName))
                       propcO = file.tell()
                       file.write((0).to_bytes(1,"little"))
                       file.write(struct.pack('H', len(fcurve.keyframe_points)))
                       bn = armature.pose.bones[bOGn]
                       
                       fo = 0
                       has_prec = False
                       prop_names = list(bn.keys())
                       for prop_name in prop_names:
                           if returnPropertyCurve(prop_name,curveI) == (proP + str(curveI)) or "Every Property" in prop_name and "MOT" in prop_name:
                             if "MOTSF" in prop_name:
                               va = bn[prop_name]
                               fo += 1
                               file.write((va[0]).to_bytes(1,"little"))
                               file.write((va[1]).to_bytes(1,"little"))
                               file.write((va[2]).to_bytes(1,"little"))
                               file.write((va[3]).to_bytes(1,"little"))
                             if "MOTFP" in prop_name:
                                 has_prec = True
                       if fo == 0:
                           file.write((0).to_bytes(4,"little"))
                           
                           
                       curveOffset = file.tell()
                       file.write(struct.pack('I', 0)) 
                        
                        
                        
                       if abs(vO) < self.threshold:    
                           lFS = file.tell()
                           file.seek(curveOffset)
                           file.write(struct.pack('f',fcurve.keyframe_points[0].co.y))
                           file.seek(lFS) 
                           
                           tfl = file.tell()
                           file.seek(propcO)
                           file.write(struct.pack('B', (CURVEI(curveI,proP,0))))
                           file.seek(tfl)
                           
                           
                       else:
                           if has_prec == False:
                              qtz = True
                              for fcurves in range(0, len(fcurve.keyframe_points)):
                                  v1 = from_ushort(to_ushort(fcurve.keyframe_points[fcurves].co.y))
                                  v2 = fcurve.keyframe_points[fcurves].co.y
                                  otp = abs(v2 - v1)
                                  if otp > 0.3:
                                      qtz = False
                                      #if the precision had been more innacurate than 0.3, it will be a semi precision
                                      break
                                  
                                  
                              minV = 9999999999999.0
                              MaV = -9999999999999.0
                                  
                              minM0 = 9999999999999.0
                              MaM0 = -9999999999999.0
                                  
                              minM1 = 9999999999999.0
                              MaM1 = -9999999999999.0
                              for fcurves in range(0, len(fcurve.keyframe_points)):
                                      clTif = 0
                                      btV = fcurve.keyframe_points[fcurves].co.y
                                      if "location" in proP:
                                          clTif = get_global_position_from_origin(bn,armature)[curveI] * -1
                                          
                                          
                                      HL = fcurve.keyframe_points[fcurves].handle_left.y + clTif
                                      HR = fcurve.keyframe_points[fcurves].handle_right.y + clTif
                                      P0 = fcurve.keyframe_points[fcurves].co.y + clTif
                                      
                                      m0 = 3 * (P0 - HL)
                                      m1 = 3 * (HR - P0)
                                      
                                      
                                      
                                      if MaV < P0:
                                          MaV = P0
                                      if minV > P0:
                                          minV = P0
                                          
                                      if MaM0 < m0:
                                          MaM0 = m0   
                                      if minM0 > m0:
                                          minM0 = m0  
                                      if MaM1 < m1:
                                          MaM1 = m1
                                      if minM1 > m1:
                                          minM1 = m1
                                          
                              lFS = file.tell()
                              file.seek(fEnd)
                              startCurveO = file.tell()
                              
                              if qtz == True:
                                  miP = minV;
                                  maP = (MaV - miP) / 255;
                                  mi0 = minM0;
                                  ma0 = (MaM0 - mi0) / 255;
                                  mi1 = minM1;
                                  ma1 = (MaM1 - mi1) / 255;
                              
                                  file.write((to_ushort(miP)).to_bytes(2,"little"))
                                  file.write((to_ushort(maP)).to_bytes(2,"little"))
                                  file.write((to_ushort(mi0)).to_bytes(2,"little"))
                                  file.write((to_ushort(ma0)).to_bytes(2,"little"))
                                  file.write((to_ushort(mi1)).to_bytes(2,"little"))
                                  file.write((to_ushort(ma1)).to_bytes(2,"little"))
                                  
                                  laKF = int(fcurve.keyframe_points[0].co.x)
                                  for fcurves in range(0, len(fcurve.keyframe_points)):
                                      clTif = 0
                                      btV = fcurve.keyframe_points[fcurves].co.y
                                      if "location" in proP:
                                          clTif = get_global_position_from_origin(bn,armature)[curveI] * -1
                                          
                                          
                                      HL = fcurve.keyframe_points[fcurves].handle_left.y + clTif
                                      HR = fcurve.keyframe_points[fcurves].handle_right.y + clTif
                                      P0 = fcurve.keyframe_points[fcurves].co.y + clTif
                                      
                                      m0 = 3 * (P0 - HL)
                                      m1 = 3 * (HR - P0)
                                      
                                      fcurve.keyframe_points[fcurves].handle_right_type = 'FREE'
                                      fcurve.keyframe_points[fcurves].handle_left_type = 'FREE'
                                      TIME = fcurve.keyframe_points[fcurves].co.x
                                      neKF = int(TIME)
                                      
                                      file.write(struct.pack('B',(neKF - laKF)))
                                      file.write(struct.pack('B',int(map_value(P0,minV,MaV,0,255))))
                                      
                                      file.write(struct.pack('B',int(map_value(m0,minM0,MaM0,0,255))))
                                      file.write(struct.pack('B',int(map_value(m1,minM1,MaM1,0,255))))
                                      laKF = int(fcurve.keyframe_points[fcurves].co.x)
                                      
                                  tfl = file.tell()
                                  file.seek(propcO)
                                  file.write(struct.pack('B', (CURVEI(curveI,proP,16))))
                                  file.seek(tfl)
                                  
                                  
                              
                              
                              else:
                                  miP = minV;
                                  maP = (MaV - miP) / 65535;
                                  mi0 = minM0;
                                  ma0 = (MaM0 - mi0) / 65535;
                                  mi1 = minM1;
                                  ma1 = (MaM1 - mi1) / 65535;
                                  file.write(struct.pack('f',miP))
                                  file.write(struct.pack('f',maP))
                                  file.write(struct.pack('f',mi0))
                                  file.write(struct.pack('f',ma0))
                                  file.write(struct.pack('f',mi1))
                                  file.write(struct.pack('f',ma1))
                                  
                                  for fcurves in range(0, len(fcurve.keyframe_points)):
                                      clTif = 0
                                      btV = fcurve.keyframe_points[fcurves].co.y
                                      if "location" in proP:
                                          clTif = get_global_position_from_origin(bn,armature)[curveI] * -1
                                      HL = fcurve.keyframe_points[fcurves].handle_left.y + clTif
                                      HR = fcurve.keyframe_points[fcurves].handle_right.y + clTif
                                      P0 = fcurve.keyframe_points[fcurves].co.y + clTif
                                      
                                      m0 = 3 * (P0 - HL)
                                      m1 = 3 * (HR - P0)
                                      
                                      
                                      
                                      fcurve.keyframe_points[fcurves].handle_right_type = 'FREE'
                                      fcurve.keyframe_points[fcurves].handle_left_type = 'FREE'
                                      TIME = fcurve.keyframe_points[fcurves].co.x
                                      
                                      
                                      

                                      
                                      file.write(struct.pack('H',int(TIME)))
                                      file.write(struct.pack('H',int(map_value(P0,minV,MaV,0,65535))))
                                      
                                      
                                      file.write(struct.pack('H',int(map_value(m0,minM0,MaM0,0,65535))))
                                      file.write(struct.pack('H',int(map_value(m1,minM1,MaM1,0,65535))))
                                      
                                      
                                  tfl = file.tell()
                                  file.seek(propcO)
                                  file.write(struct.pack('B', CURVEI(curveI,proP,48)))
                                  file.seek(tfl)
                                  
                                  
                                  
                                      
                                      
                              fEnd = file.tell()    
                              file.seek(curveOffset)
                              file.write(struct.pack('I',startCurveO))
                              file.seek(lFS)
                                  
                           else:
                               
                               #print("ohwelllllllll")
                               lFS = file.tell()
                               file.seek(fEnd)
                               startCurveO = file.tell()
                               for fcurves in range(0, len(fcurve.keyframe_points)):
                                   
                                   fcurve.keyframe_points[fcurves].handle_right_type = 'FREE'
                                   fcurve.keyframe_points[fcurves].handle_left_type = 'FREE'
                                   
                                   HL = fcurve.keyframe_points[fcurves].handle_left.y
                                   HR = fcurve.keyframe_points[fcurves].handle_right.y
                                   P0 = fcurve.keyframe_points[fcurves].co.y
                                      
                                   
                                   
                                   TIME = fcurve.keyframe_points[fcurves].co.x
                                   
                                   
                                   

                                   m0 = 3 * (P0 - HL)
                                   m1 = 3 * (HR - P0)
                                   
                                   file.write(struct.pack('H',int(TIME)))
                                   file.write(struct.pack('H',65535))
                                   file.write(struct.pack('f',P0))
                                   file.write(struct.pack('f',m0))
                                   file.write(struct.pack('f',m1))
                                   
                                   
                                   
                                   
                               tfl = file.tell()
                               file.seek(propcO)
                               file.write(struct.pack('B', CURVEI(curveI,proP,80)))
                               file.seek(tfl)
                                  
                                  
                               fEnd = file.tell()
                               file.seek(curveOffset)
                               file.write(struct.pack('I',startCurveO))
                               file.seek(lFS)
            
            tmp2 = file.tell()
            file.seek(tmp1)
            file.write((totalLength).to_bytes(2,"little"))
            file.seek(tmp2)
            
            
            
            file.seek(lcountf)
            file.write((FCO+1).to_bytes(1,"little"))
            
     bpy.ops.object.mode_set(mode='POSE') 
     bpy.ops.pose.select_all(action='SELECT')
     bpy.ops.pose.loc_clear()
     bpy.ops.pose.rot_clear()
     bpy.ops.pose.scale_clear()
     bpy.ops.pose.select_all(action='DESELECT')
     
     
     bpy.context.scene.frame_current = 0
     bpy.context.view_layer.update()
  
     return {'FINISHED'}
def get_global_position_from_origin(bone,armature):
    bone.matrix = Matrix.Translation((0.0, 0.0, 0.0))
    return bone.location

def CURVEI(curveI,proP,a):
    print(curveI + a)
    if proP == "location":
        return curveI + a
    if proP == "rotation_euler":
        return (curveI+3) + a
    if proP == "scale":
        return (curveI+6) + a
    return 0
def map_value(value, from_min, from_max, to_min, to_max):
    lt1 = (to_max - to_min)
    lt2 = (from_max - from_min)
    if lt2 == 0:
        lt2 = 1
    scale = lt1 / lt2
    return to_min + (value - from_min) * scale
                           
                           
def returnProperty(input):
    print(input)
    if input == "All Positions":
       return "location"
    if input == "All Rotations":
       return "rotation_euler"
    return ""

def returnPropertyCurve(input, LT):

    signal = "X"
    if LT == 1:
        signal = "Y"
    if LT == 2:
        signal = "Z"
        
        
        
        
    if "MOTSF" in input and "Position" in input:
       return "location" + str(LT)
    if "MOTSF" in input and "Rotation" in input:
       return "rotation_euler" + str(LT)
    if "MOTSF" in input and "Scale" in input:
       return "scale" + str(LT)
   
    if "MOTFP" in input and "Position" in input:
       return "location" + str(LT)
    if "MOTFP" in input and "Rotation" in input:
       return "rotation_euler" + str(LT)
    if "MOTFP" in input and "Scale" in input:
       return "scale" + str(LT)
    return ""


def menu_func_export_mot(self, context):
    self.layout.operator(
        ExportMOT.bl_idname,
        text="Export God Hand Mot (.mot)",
        icon='ACTION'
    )

def register():
    bpy.utils.register_class(ExportMOT)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_mot)


def unregister():
    bpy.utils.unregister_class(ExportMOT)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_mot)

if __name__ == "__main__":
    register()
