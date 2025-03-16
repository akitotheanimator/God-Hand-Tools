bl_info = {
    "name": "Blen2Mot Import (hMot)",
    "blender": (3, 6, 0),
    "category": "File>Import",
    "author": "Akito",
    "version": (2, 0, 0),
    "description": "Export Animation directly to MOT",
    "tracker_url": "https://github.com/akitotheanimator/God-Hand-Tools/tree/main",
}






import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
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


class ImportMultipleFilesHMOT(bpy.types.Operator, ImportHelper):
    """Import God Hand Head Motion"""
    bl_idname = "import_scene.hmot"
    bl_label = "Import Animation"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".hmot"
    filter_glob: StringProperty(
        default="*.hmot",
        options={'HIDDEN'},
        maxlen=255,
    )
    files: CollectionProperty(
        type=bpy.types.PropertyGroup
    )
    

           
    def execute(self, context):
     layout = self.layout     
     

     directory = self.filepath
     directory = directory.replace(os.path.basename(directory),"")
     directory = directory[:-1]
     bpy.context.scene.tool_settings.use_keyframe_insert_auto = False 
     

     for file_elem in self.files:
        file_path = f"{directory}/{file_elem.name}"
        with open(file_path, "rb") as file:
            filemagic = struct.unpack("<I", file.read(4))[0]
            if filemagic != 862090349:
                self.report({'ERROR'}, "File " + file_path + " file wasn't a MOT file, skipping...")
                continue
            
            
            bpy.ops.object.empty_add(location=(0, 0, 0))
            object = bpy.context.object
            object.name = str(os.path.basename(file_path)) + "_Properties"
            bpy.ops.object.mode_set(mode='OBJECT')
            
            bpy.context.scene.render.fps = 30
            bpy.context.scene.frame_start = 0
            bpy.context.scene.frame_current = 0
            animation = bpy.data.actions.new(name=str(os.path.basename(file_path)))
            object.animation_data_create()
            object.animation_data.action = animation
            bpy.data.actions[animation.name].use_fake_user = True
     
            FE = struct.unpack("<H", file.read(2))[0] - 1
            bpy.context.scene.frame_end = FE
            propertyCount = struct.unpack("<B", file.read(1))[0]
            loops = bool(struct.unpack("<B", file.read(1))[0])
            if hasattr(bpy.context.scene, 'properties_MOT'):
               context.scene.properties_MOT.loop_MOT = loops
            
            
            for i in range(0, propertyCount - 1):
                
                bone = struct.unpack("<b", file.read(1))[0]
                
                property = struct.unpack("<B", file.read(1))[0]
                print(property)
                
                keyframec = struct.unpack("<H", file.read(2))[0]
                
                prop1 = struct.unpack("<B", file.read(1))[0]
                prop2 = struct.unpack("<B", file.read(1))[0]
                prop3 = struct.unpack("<B", file.read(1))[0]
                prop4 = struct.unpack("<B", file.read(1))[0]
                
                
                bname = str(prop1) + "_" + str(prop2) + "_" + str(prop3) + "_" + str(prop4)
                ipr = normalize_property(property)
                propTransform = get_property(property)
                    
                    
                group = None
                for existing_group in object.animation_data.action.groups:
                    if existing_group.name == bname:
                       group = existing_group
                       break
                if not group:
                       group = object.animation_data.action.groups.new(name=bname)
                       
                       
                if property != 64 and property != 67:
                  if property <= 15:
                    bpy.context.scene.frame_current = 0
                    value = struct.unpack("<f", file.read(4))[0]
                    if propTransform == "location":
                       object.location = Vector((value,value,value))
                       
                    if propTransform == "rotation_euler":
                       object.rotation_euler = Vector((value,value,value))
                       
                    object.keyframe_insert(data_path=propTransform, index=ipr, frame=0)  
                    fcurve = animation.fcurves.find(f'{propTransform}', index=ipr)
                    if fcurve.group != group:
                       fcurve.group = group
                
                  if property >= 16:
                    bpy.context.scene.frame_current = 0
                    
                    offset_data = struct.unpack("<I", file.read(4))[0]
                    lb = file.tell()
                    file.seek(offset_data)
                    keyframes = []
                    
                    P = 0
                    PD = 0
                    M0 = 0
                    DM0 = 0
                    M1 = 0
                    DM1 = 0
                    if property < 80:
                        if property < 50:
                           P = from_ushort(struct.unpack("<H", file.read(2))[0])
                           PD = from_ushort(struct.unpack("<H", file.read(2))[0])
                           M0 = from_ushort(struct.unpack("<H", file.read(2))[0])
                           DM0 = from_ushort(struct.unpack("<H", file.read(2))[0])
                           M1 = from_ushort(struct.unpack("<H", file.read(2))[0])
                           DM1 = from_ushort(struct.unpack("<H", file.read(2))[0])
                        else:
                           P = struct.unpack("<f", file.read(4))[0]
                           PD = struct.unpack("<f", file.read(4))[0]
                           M0 = struct.unpack("<f", file.read(4))[0]
                           DM0 = struct.unpack("<f", file.read(4))[0]
                           M1 = struct.unpack("<f", file.read(4))[0]
                           DM1 = struct.unpack("<f", file.read(4))[0]
                    
                    T = 0
                            
                    for cur in range(0, keyframec):
                        if property < 80:
                            if property < 50:
                              T += struct.unpack("<B", file.read(1))[0]
                              qv = struct.unpack("<B", file.read(1))[0]
                              qm0 = struct.unpack("<B", file.read(1))[0]
                              qm1 = struct.unpack("<B", file.read(1))[0] 
                            
                            
                            
                              PVAL = P + PD * qv
                              keyframes.append((T,PVAL,M0 + DM0 * qm0,M1 + DM1 * qm1))
                            else:
                              T = struct.unpack("<H", file.read(2))[0]
                              qv = struct.unpack("<H", file.read(2))[0]
                              qm0 = struct.unpack("<H", file.read(2))[0]
                              qm1 = struct.unpack("<H", file.read(2))[0] 
                            
                            
                            
                              PVAL = P + PD * qv
                              keyframes.append((T,PVAL, (M0 + DM0 * qm0) , (M1 + DM1 * qm1)))
                              
                              
                              
                        else:
                            T = struct.unpack("<H", file.read(2))[0]
                            struct.unpack("<H", file.read(2))[0]
                            
                            v = struct.unpack("<f", file.read(4))[0]
                            m0 = struct.unpack("<f", file.read(4))[0]
                            m1 = struct.unpack("<f", file.read(4))[0] 
                            keyframes.append(T,v,m0,m1)   
                            
                            
                            
                            
                            
                    for kf in range(0,len(keyframes)):
                        TIME = keyframes[kf][0]
                        p0 = keyframes[kf][1]
                        if propTransform == "location":
                           pose_bone.location = Vector((p0,p0,p0))
                       
                        if propTransform == "rotation_euler":
                           pose_bone.rotation_euler = Vector((p0,p0,p0))
                             
                             
                        pose_bone.keyframe_insert(data_path=propTransform, index=ipr, frame=TIME)  
                        
                    for kf in range(0,len(keyframes)-1):
                        p0 = keyframes[kf][1]
                        p1 = keyframes[kf + 1][1]
                        
                        m0 = keyframes[kf][3]
                        m1 = keyframes[kf+1][2]
                
                        fcurve = animation.fcurves.find(f'pose.bones["{bname}"].{propTransform}', index=ipr)
                        if fcurve.group != group:
                           fcurve.group = group
                           
                        fcurve.keyframe_points[kf].handle_right_type = 'FREE'
                        fcurve.keyframe_points[kf].handle_right.y = p0 + (m0 / 3.0)
                        
                        
                        fcurve.keyframe_points[kf+1].handle_left_type = 'FREE'
                        fcurve.keyframe_points[kf+1].handle_left.y = p1 - (m1 / 3.0)
                        

                    file.seek(lb)
                if property == 64:
                    print("ohwow")
                    
                    offset_data = struct.unpack("<I", file.read(4))[0]
                    lb = file.tell()
                    file.seek(offset_data)
                    
                    
                    P = struct.unpack("<f", file.read(4))[0]
                    PD = struct.unpack("<f", file.read(4))[0]
                    
                    propName = str(prop1) + "_" + str(prop2) + "_" + str(prop3) + "_"+str(prop4)
                    object[propName] = 0
                    
                    for cur in range(0, keyframec):
                        qv = struct.unpack("<H", file.read(2))[0]
                        PVAL = P + PD * qv
                        object[propName] = PVAL
                        object.keyframe_insert(data_path="[\""+propName+"\"]", frame=cur)  
                        
                    bpy.context.view_layer.objects.active = object
                    file.seek(lb)
                    
                if property == 67:    
                    offset_data = struct.unpack("<I", file.read(4))[0]
                    lb = file.tell()
                    file.seek(offset_data)
                    file.seek(lb)

                    
     bpy.context.scene.frame_current = 1
     
     bpy.ops.object.location_clear(clear_delta=False)
     bpy.ops.object.rotation_clear(clear_delta=False)
     bpy.ops.object.scale_clear(clear_delta=False)

     bpy.context.scene.frame_current = 0
     return {'FINISHED'}
 
 
def bone_bake(context,self,name,obj,fend,animation):
    
    
        bpy.ops.object.mode_set(mode='EDIT')
        for i in name:
            Bone = obj.data.edit_bones[str(i + 2)]
            Bone.parent = obj.data.edit_bones[0]
               
               
               
        bpy.ops.object.mode_set(mode='POSE') 
        bpy.ops.pose.select_all(action='DESELECT') 
        for i in name:
            bone = obj.pose.bones[str(i + 1)] 
            bone2 = obj.pose.bones[str(i + 2)] 
            
            
            bpy.ops.pose.select_all(action='DESELECT')             
            constraint = bone.constraints.new('TRACK_TO')
            constraint.name = "lol"
            constraint.track_axis = 'TRACK_NEGATIVE_Y'
            constraint.up_axis = 'UP_Z'
            constraint.use_target_z = True
            constraint.target = obj
            constraint.subtarget = bone2.name
            bone.bone.select = True
            bpy.ops.nla.bake(frame_start=0, frame_end=fend, only_selected=True, visual_keying=True, clear_constraints=True, use_current_action=True, bake_types={'POSE'})
            bpy.ops.pose.select_all(action='DESELECT')

               
               
               
            bpy.ops.object.mode_set(mode='OBJECT') 
            
            bpy.ops.object.empty_add(location=(0, 0, 0))
            ikloc = bpy.context.object
            ikloc.name = "loc" + bone2.name
            
            
            
            constraint = ikloc.constraints.new('COPY_TRANSFORMS')
            constraint.name = "lol"
            constraint.target = obj
            constraint.subtarget = bone2.name
            bpy.ops.nla.bake(frame_start=0, frame_end=fend, only_selected=True, visual_keying=True, clear_constraints=True, use_current_action=True, bake_types={'OBJECT'})
            
            
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = obj
            
            
            bpy.ops.object.mode_set(mode='EDIT')
            obj.data.edit_bones.get(str(i + 2)).parent = obj.data.edit_bones.get(str(i + 1))
            bpy.ops.object.mode_set(mode='POSE') 
            bone2 = obj.pose.bones[str(i + 2)] 
            bone = obj.pose.bones[str(i + 1)] 
            bpy.ops.pose.loc_clear()
            bpy.ops.pose.rot_clear()
            bpy.ops.pose.scale_clear()
            
            
            constraint = bone2.constraints.new('COPY_TRANSFORMS')
            constraint.name = "lol"
            constraint.target = ikloc
            bpy.ops.pose.select_all(action='DESELECT')
            bone2.bone.select = True
            bpy.ops.nla.bake(frame_start=0, frame_end=fend, only_selected=True, visual_keying=True, clear_constraints=True, use_current_action=True, bake_types={'POSE'})
            
            
            bpy.ops.object.mode_set(mode='OBJECT') 
            ikloc.select_set(True)
            bpy.ops.object.delete()
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='POSE')
                    
                    
def bone_setup_nopanel(context,self,name,obj  ):
    
        bpy.ops.object.mode_set(mode='EDIT')

        Bone = obj.data.edit_bones[str(name)]
        if(Bone.parent != obj.data.edit_bones['root']):
               Bone.parent = obj.data.edit_bones['root']
               

      
        bpy.ops.object.mode_set(mode='POSE') 
        bone = obj.pose.bones[str(name - 1)] 
        for constraint in bone.constraints:
                  if constraint.name == "BLEN2MOT_LEG_SETUP":
                    bone.constraints.remove(constraint)
                    
                    
        constraint = bone.constraints.new('TRACK_TO')
        constraint.name = "BLEN2MOT_LEG_SETUP"
        constraint.track_axis = 'TRACK_NEGATIVE_Y'
        constraint.up_axis = 'UP_Z'
        constraint.use_target_z = True
        constraint.target = obj
        constraint.subtarget = str(name)
               
def bone_setup(context,self):
        if(context.scene.ik_feet_bones == ""):
                self.report({'ERROR'}, "No feet bone was written in the \"Foot rig\" field!")
                return {'CANCELLED'}
        obj = context.object
        if obj and obj.type != 'ARMATURE':
                self.report({'ERROR'}, "No feet bone was written in the \"Foot rig\" field!")
                return {'CANCELLED'}
        
        
        
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        
        
        allB = context.scene.ik_feet_bones.split(',')
        for b in allB:
            name = int(b)
            nameParent = int(b)-1
            
            
            c = 0
            for at in obj.data.edit_bones:
                if at.name == str(name):
                    c+=1
            if c == 0:
                bpy.ops.object.mode_set(mode='POSE')
                self.report({'ERROR'}, "The bone \"" + str(name) +  "\" doesn't exist!")
                return {'CANCELLED'}
            
            
            
            c = 0
            for at in obj.data.edit_bones:
                if at.name == "root":
                    c+=1
            if c == 0:
                bpy.ops.object.mode_set(mode='POSE')
                self.report({'ERROR'}, "There's no bone named \"root\" on the skeleton!")
                return {'CANCELLED'}
            
            
            if nameParent < 1:
                nameParent = "root"
            
            
            
            if c > 1:
                bpy.ops.object.mode_set(mode='POSE')
                self.report({'ERROR'}, "There's more than 1 bone named \"root\" on the skeleton!")
                return {'CANCELLED'}
            
            Bone = obj.data.edit_bones[str(name)]
            if(Bone.parent != obj.data.edit_bones['root']):
               Bone.parent = obj.data.edit_bones['root']
    
    
            
        bpy.ops.object.mode_set(mode='POSE')
        for bone in obj.pose.bones:
            for constraint in bone.constraints:
                  if constraint.name == "BLEN2MOT_LEG_SETUP":
                    bone.constraints.remove(constraint)
                    
                    
        for b in allB:
           name1 = int(b)-1
           name2 = int(b)
           if name1 < 1:
               name1 = "root"
           bone = obj.pose.bones[str(name1)]
           constraint_exists = any(constraint.name == "BLEN2MOT_LEG_SETUP" for constraint in bone.constraints)
           if not constraint_exists:
                  
                  
                  
                     constraint = bone.constraints.new('TRACK_TO')
                     constraint.name = "BLEN2MOT_LEG_SETUP"
                     constraint.track_axis = 'TRACK_NEGATIVE_Y'
                     constraint.up_axis = 'UP_Z'
                     constraint.use_target_z = True
                     constraint.target = obj
                     constraint.subtarget = str(name2)
        bpy.ops.pose.select_all(action='DESELECT')





        bone_group_name = "ANIMATION_READY"
        if bone_group_name in obj.pose.bone_groups:
           obj.pose.bone_groups.remove(obj.pose.bone_groups[bone_group_name])
        new_bone_group = obj.pose.bone_groups.new(name=bone_group_name)
           
        bone_group_name = "ANIMATION_READY_PART01"
        if bone_group_name in obj.pose.bone_groups:
           obj.pose.bone_groups.remove(obj.pose.bone_groups[bone_group_name])
        new_bone_group = obj.pose.bone_groups.new(name=bone_group_name)
           
        bone_group_name = "ANIMATION_READY_PART02"
        if bone_group_name in obj.pose.bone_groups:
           obj.pose.bone_groups.remove(obj.pose.bone_groups[bone_group_name])
        new_bone_group = obj.pose.bone_groups.new(name=bone_group_name)
        
        bone_group_name = "ANIMATION_READY"
        bone_group = None
        for group in obj.pose.bone_groups:
                if group.name == bone_group_name:
                    bone_group = group
                    group.color_set = 'THEME04' #for animation
                    bpy.ops.pose.select_all(action='SELECT')
                    bpy.ops.pose.group_assign(type=1)
                    bpy.ops.pose.select_all(action='DESELECT')
                    break
            
        bone_group_name = "ANIMATION_READY_PART01"
        for group in obj.pose.bone_groups:
                if group.name == bone_group_name:
                    bone_group = group
                    group.color_set = 'THEME08'
                    for b in allB:
                          name2 = int(b)
                          bone = obj.pose.bones[str(name2)]
                          bone.bone_group = group
                       
                          break
        bone_group_name = "DEFAULT"
        for group in obj.pose.bone_groups:
                if group.name == bone_group_name:
                    bone_group = group
                    group.color_set = 'THEME07'
                    for b in allB:
                          name2 = int(b)-1
                          bone = obj.pose.bones[str(name2)]
                          bone.bone_group = group
        return {'FINISHED'}
    
def get_global_position_from_origin(bone,armature):
    bone.matrix = Matrix.Translation((0.0, 0.0, 0.0))
    return bone.location
    
    
def get_bone_position(bone,armature):
     return armature.data.bones[bone].head
     
def get_property(vt):
    if vt <= 15:
        if vt >= 3:
            return "rotation_euler"
        else:
            return "location"
        
    if vt >= 16 and vt < 50:
        if vt >= 19:
            return "rotation_euler"
        else:
            return "location"
        
    if vt >= 50 and vt < 80:
        if vt >= 53:
            return "rotation_euler"
        else:
            return "location"
        
        
    if vt >= 80 and vt < 86:
        if vt >= 83:
            return "rotation_euler"
        else:
            return "location"
    return vt
    
def normalize_property(value):
    vt = value
    #this normalizes the properties, so i can just insert the keyframe easily
    if vt <= 15:
        if vt >= 3:
            vt -= 3
            
            
    if vt >= 16 and vt < 50:
        if vt >= 19:
            vt -= 19
        else:
            vt -= 16
            
            
    if vt >= 50 and vt < 80:
        if vt >= 53:
            vt -= 53
        else:
            vt -= 50
            
            
            
    if vt >= 80 and vt < 86:
        if vt >= 83:
            vt -= 83
        else:
            vt -= 80
    return vt





def menu_func_import_hmot(self, context):
    self.layout.operator(
        ImportMultipleFilesHMOT.bl_idname,
        text="Import God Hand Head Mot (.hmot)",
        icon='ACTION'
    )

def register():
    bpy.utils.register_class(ImportMultipleFilesHMOT)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_hmot)

def unregister():
    bpy.utils.unregister_class(ImportMultipleFilesHMOT)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_hmot)

if __name__ == "__main__":
    register()