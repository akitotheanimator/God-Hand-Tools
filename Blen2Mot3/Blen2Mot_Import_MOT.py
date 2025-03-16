bl_info = {
    "name": "Blen2Mot Import (Mot)",
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


class ImportMultipleFilesMOT(bpy.types.Operator, ImportHelper):
    """Import God Hand Motion"""
    bl_idname = "import_scene.mot"
    bl_label = "Import Animation"
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
    
    meth: EnumProperty(
        name="Spacing Switch Solver",
        description="Sets the UP Axis of the model.",
        items=(
            ('TYPE1', "Full Precision", "Set ups a rigging for the space change properties, it's the most precise space switch solver because it emulates how the space switch is calculated on the game runtime (fastest to load)"),
            ('TYPE2', "Full Precision Keyframes", "Converts the bones space switch movements to keyframes, avoiding the creation of constraints. However, exporting back to MOT can generate some weird movements on the bones that uses space switching (slowest to load)"),

        ),
        default='TYPE1',
    )
    fix_rotation_space: BoolProperty(
        name="Fix bone space",
        description="Sometimes some bones can use other transform space. Enable this if you want to fix it. However, the exported the animation will look messed up",
        default=True,
    )
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object   
        return active_object is not None
        
        
    def draw(self, context):
        layout = self.layout   
        layout.prop(self, "fix_rotation_space")
        
        
        if self.fix_rotation_space:
            layout.prop(self, "meth")
           
           
    def execute(self, context):
     bpy.ops.object.mode_set(mode='POSE') 
     layout = self.layout     
     armature = bpy.context.object
     armature.location = Vector((0.0,0.0,0.0))
     #armature.rotation_euler = Vector((0.0,0.0,0.0))
     armature.scale = Vector((1.0,1.0,1.0))    
        
        
     directory = self.filepath
     directory = directory.replace(os.path.basename(directory),"")
     directory = directory[:-1]
     bpy.context.scene.tool_settings.use_keyframe_insert_auto = False 
                
                
     for i in range(0,32):
         armature.data.layers[i] = True

     bpy.ops.object.mode_set(mode='POSE')  
     bpy.ops.pose.select_all(action='SELECT') 
     bpy.ops.pose.rotation_mode_set(type='XYZ')
     bpy.context.view_layer.update()
     if armature.animation_data != None:
        armature.animation_data.action = None
     
     bpy.ops.pose.loc_clear()
     bpy.ops.pose.rot_clear()
     bpy.ops.pose.scale_clear()
     bpy.context.view_layer.update()
     
     
     bpy.ops.object.mode_set(mode='POSE') 
     
      
     for i in range(0,32):
         armature.data.layers[i] = False
     bpy.context.object.data.layers[0] = True
     bpy.ops.pose.select_all(action='DESELECT')




     listBones = []
     
     

     for file_elem in self.files:
        file_path = f"{directory}/{file_elem.name}"
        with open(file_path, "rb") as file:
            filemagic = struct.unpack("<I", file.read(4))[0]
            if filemagic != 862090349:
                self.report({'ERROR'}, "File " + file_path + " file wasn't a MOT file, skipping...")
                continue
            bpy.context.scene.render.fps = 30
            bpy.context.scene.frame_start = 0
            bpy.context.scene.frame_current = 0
            animation = bpy.data.actions.new(name=str(os.path.basename(file_path)))
            armature.animation_data_create()
            armature.animation_data.action = animation
            bpy.data.actions[animation.name].use_fake_user = True
     
     
     
            
            

                
            FE = struct.unpack("<H", file.read(2))[0] - 1
            bpy.context.scene.frame_end = FE
            propertyCount = struct.unpack("<B", file.read(1))[0]
            loops = bool(struct.unpack("<B", file.read(1))[0])
            if hasattr(bpy.context.scene, 'properties_MOT'):
               context.scene.properties_MOT.loop_MOT = loops
            
            
            for i in range(0, propertyCount - 1):
                
                #print(file.tell())
                bone = struct.unpack("<b", file.read(1))[0]
                property = struct.unpack("<B", file.read(1))[0]
                print(str(bone) + "  prop " + str(property))
                bname = str(bone + 1)
                if bone + 1 == 0:
                    bname = "root"
                if property != 64:
                  pose_bone = armature.pose.bones[bname]
                
                keyframec = struct.unpack("<H", file.read(2))[0]
                
                prop1 = struct.unpack("<B", file.read(1))[0]
                prop2 = struct.unpack("<B", file.read(1))[0]
                prop3 = struct.unpack("<B", file.read(1))[0]
                prop4 = struct.unpack("<B", file.read(1))[0]
                ipr = normalize_property(property)
                propTransform = get_property(property)
                    
                    
                group = None
                for existing_group in armature.animation_data.action.groups:
                    if existing_group.name == bname:
                       group = existing_group
                       break
                if not group:
                       group = armature.animation_data.action.groups.new(name=bname)
                       
                       
                
                if property <= 15:
                    bpy.context.scene.frame_current = 0
                    value = struct.unpack("<f", file.read(4))[0]

                    if propTransform == "location":
                       pose_bone.location = get_global_position_from_origin(pose_bone,armature) + Vector((value,value,value))
                       
                    if propTransform == "rotation_euler":
                       pose_bone.rotation_euler = Vector((value,value,value))
                       
                       
                    pose_bone.keyframe_insert(data_path=propTransform, index=ipr, frame=0)  
                    fcurve = animation.fcurves.find(f'pose.bones["{bname}"].{propTransform}', index=ipr)
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
                        if property < 48:
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
                          
                          
                    if prop1 == 1 or prop2 == 1 or prop3 == 1 or prop4 == 1:
                       if self.meth == "TYPE1":
                          if hasattr(bpy.context.scene, 'ik_feet_bones_mot'):
                            if context.scene.ik_feet_bones != "":
                              
                              bones = []
                              
                              sp = context.scene.ik_feet_bones.split(',')
                              for bni in sp:
                                  let = bni.replace(" ","")
                                  bones.append(let)
                              containsBone = 0
                              for bni in bones:
                                  if str(bone + 3) in bni:
                                      containsBone += 1
                              if containsBone == 0:
                                  bones.append(str(bone + 3))
                                  
                                  
                              retString = ""   
                              for bni in bones:
                                  if len(bni) > 0:
                                     retString += bni + ","
                              retString = retString[:-1]
                              context.scene.ik_feet_bones = retString
                            else:
                              context.scene.ik_feet_bones = str(bone + 3)
                              
                            spt = context.scene.ik_feet_bones.split(',')
                            bone_setup(context,self)
                          else:
                             bone_setup_nopanel(context,self,bone+3,armature)
                       else:
                           listBones.append(bone+1) 
                           
                           
                            
                    for cur in range(0, keyframec):
                        if property < 80:
                            if property < 48:
                              T += struct.unpack("<B", file.read(1))[0]
                              qv = struct.unpack("<B", file.read(1))[0]
                              qm0 = struct.unpack("<B", file.read(1))[0]
                              qm1 = struct.unpack("<B", file.read(1))[0] 
                            
                            
                            
                              PVAL = P + PD * qv
                              if propTransform == "location":
                                 PVAL = get_global_position_from_origin(pose_bone,armature)[ipr] + PVAL
                              keyframes.append((T,PVAL,M0 + DM0 * qm0,M1 + DM1 * qm1))
                            else:
                              T = struct.unpack("<H", file.read(2))[0]
                              qv = struct.unpack("<H", file.read(2))[0]
                              qm0 = struct.unpack("<H", file.read(2))[0]
                              qm1 = struct.unpack("<H", file.read(2))[0] 
                            
                            
                            
                              PVAL = P + PD * qv
                              if propTransform == "location":
                                 PVAL = get_global_position_from_origin(pose_bone,armature)[ipr] + PVAL
                              keyframes.append((T,PVAL, (M0 + DM0 * qm0) , (M1 + DM1 * qm1)))
                              
                              
                              
                        else:
                            T = struct.unpack("<H", file.read(2))[0]
                            struct.unpack("<H", file.read(2))[0]
                            
                            v = struct.unpack("<f", file.read(4))[0]
                            m0 = struct.unpack("<f", file.read(4))[0]
                            m1 = struct.unpack("<f", file.read(4))[0] 
                            keyframes.append((T,v,m0,m1))   
                            
                            
                            
                            
                            
                    for kf in range(0,len(keyframes)):
                        TIME = keyframes[kf][0]
                        p0 = keyframes[kf][1]
                        if propTransform == "location":
                           pose_bone.location = Vector((p0,p0,p0))
                       
                        if propTransform == "rotation_euler":
                           pose_bone.rotation_euler = Vector((p0,p0,p0))
                             
                        print(propTransform)
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
                    
     bpy.context.scene.frame_current = 1
     
     

     for i in range(0,32):
         bpy.context.object.data.layers[i] = True
         
     bpy.ops.object.mode_set(mode='POSE')  
     bpy.ops.pose.select_all(action='SELECT') 
     bpy.ops.pose.rotation_mode_set(type='XYZ')
     
     bpy.ops.pose.loc_clear()
     bpy.ops.pose.rot_clear()
     bpy.ops.pose.scale_clear()
     bpy.context.scene.frame_current = 0
     
     
     if self.meth == "TYPE2":
               listBones = list(set(listBones))
               bone_bake(context,self,listBones,armature,FE,animation)
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
    if vt == 0 or vt == 16 or vt == 48 or vt == 80:
       return "location"
    if vt == 1 or vt == 17 or vt == 49 or vt == 81:
       return "location"
    if vt == 2 or vt == 18 or vt == 50 or vt == 82:
       return "location"



    if vt == 3 or vt == 19 or vt == 51 or vt == 83:
       return "rotation_euler"
    if vt == 4 or vt == 20 or vt == 52 or vt == 84:
       return "rotation_euler"
    if vt == 5 or vt == 21 or vt == 53 or vt == 85:
       return "rotation_euler"
   
   
   
    if vt == 6 or vt == 22 or vt == 54 or vt == 86:
       return "scale"
    if vt == 7 or vt == 23 or vt == 55 or vt == 87:
       return "scale"
    if vt == 8 or vt == 24 or vt == 56 or vt == 88:
       return "scale"
    return "location"
    
def normalize_property(value):
    vt = value
    #this normalizes the properties, so i can just insert the keyframe easily
    if vt == 0 or vt == 16 or vt == 48 or vt == 80:
       return 0
    if vt == 1 or vt == 17 or vt == 49 or vt == 81:
       return 1
    if vt == 2 or vt == 18 or vt == 50 or vt == 82:
       return 2



    if vt == 3 or vt == 19 or vt == 51 or vt == 83:
       return 0
    if vt == 4 or vt == 20 or vt == 52 or vt == 84:
       return 1
    if vt == 5 or vt == 21 or vt == 53 or vt == 85:
       return 2
   
   
   
    if vt == 6 or vt == 22 or vt == 54 or vt == 86:
       return 0
    if vt == 7 or vt == 23 or vt == 55 or vt == 87:
       return 1
    if vt == 8 or vt == 24 or vt == 56 or vt == 88:
       return 2
   
   

def menu_func_import_mot(self, context):
    self.layout.operator(
        ImportMultipleFilesMOT.bl_idname,
        text="Import God Hand Mot (.mot)",
        icon='ACTION'
    )

def register():
    bpy.utils.register_class(ImportMultipleFilesMOT)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_mot)

def unregister():
    bpy.utils.unregister_class(ImportMultipleFilesMOT)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_mot)

if __name__ == "__main__":
    register()
