bl_info = {
    "name": "Blen2MOT",
    "blender": (3, 2, 0),
    "category": "3D View",
    "author": "Akito",
    "version": (1, 0, 0),
    "description": "Export Animation directly to MOT",
    "warning": "Use only EULER Rotations. QUATERNION rotations will be IGNORED",
    "tracker_url": "https://github.com/akitotheanimator/God-Hand-Tools/tree/main",
}

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty,CollectionProperty
from bpy.types import Panel, Operator,OperatorFileListElement
from bpy_extras.io_utils import ImportHelper
import os
import re


class OBJECT_OT_Import(Operator, ImportHelper):
    bl_idname = "object.import_action"
    bl_label = "Import MOT Animation"
    bl_description = "Import MOT animation"



    files: CollectionProperty(
        name="File Path",
        type=OperatorFileListElement,
        )
    directory: StringProperty(
        subtype='DIR_PATH',
        )
            
    filter_glob: StringProperty(
        default="*.mot",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    def execute(self, context):
      obj = context.object
      if obj and obj.type != 'ARMATURE':
            self.report({'WARNING'}, "Select a armature!")
            return {'CANCELLED'}
      bpy.ops.object.mode_set(mode='POSE')
      bpy.ops.pose.select_all(action='SELECT')
      bpy.ops.pose.rotation_mode_set(type='XYZ')
      bpy.ops.pose.rot_clear()
      bpy.ops.pose.loc_clear()
      bpy.ops.pose.scale_clear()
      bpy.ops.pose.select_all(action='DESELECT')      
      directory = self.directory
      for file in self.files:
        filepath = os.path.join(directory, file.name)  
        #os.system('start cmd /k ' + context.scene.exe_path + ' ' + filepath + ' True ' + context.scene.bone_path)
        
        os.system('start /wait \"\"  \"' + context.scene.exe_path + '\" \"' + filepath + '\" \"True\" \"' + context.scene.bone_path + "\"")
        
        if obj is None:
            print("No active object found.")
    
    
        if obj.animation_data is None:
           obj.animation_data_create()

    
        action = bpy.data.actions.new(name=os.path.basename(filepath))
        obj.animation_data.action = action  # This makes it the active action
        #print(filepath.replace(".mot","_FTEMP.MFIL"));

        fileName = filepath.replace(".mot","_FTEMP.MFIL").replace(".MOT","_FTEMP.MFIL")
        print("FILE NAME: " + fileName);
        with open(fileName) as file: #istg why is python built like that?
           file_content = file.read()
           pSplit = file_content.split("\n")
           for line in pSplit:
               
               
               if line.split("|")[0] != "" :
                 boneInt = int(line.split("|")[0]) + 1
                 boneGet = str(boneInt);
                 if boneInt == 0: 
                   boneGet = "root"
                   
                   
                 bone = obj.pose.bones.get(str(boneGet))
                 boneName = str(boneGet)
                 group = None
                 for existing_group in bpy.context.object.animation_data.action.groups:
                     if existing_group.name == boneName:
                        group = existing_group
                        break
                 if not group:
                        group = bpy.context.object.animation_data.action.groups.new(name=boneName)
               
                 transform = line.split("|")[1]
                 splitTransform = line.split("$")
                 valueArray = []
                 for transformGet in splitTransform[1:]:
                   transformData = transformGet.split(",")
                   print("DATA:" + transformData[0] + "|" + transformData[1] + "|" + transformData[2] + "|" + transformData[3]+".");
                   
                   time = int(transformData[0]);
                   p0 = float(transformData[1]);
                   m0 = float(transformData[2]);
                   m1 = float(transformData[3]);
                   valueArray.append([time, p0, m0, m1])  # Add p0, m0, m1 to the list
                   
                 transformN = transform.replace(".x","").replace(".y","").replace(".z","")
                 iType = 0;

                       

                 for i in range(0, len(valueArray), 1):
                     p0 = valueArray[i][1]
                     if "location" in transform:
                          bone.location.x = p0
                     else:
                          bone.rotation_euler.x = p0
                     if "y" in transform: 
                         if "location" in transform:
                             bone.location.y = p0
                         else:
                             bone.rotation_euler.y = p0
                         iType = 1
                     if "z" in transform:
                         if "location" in transform:
                             bone.location.z = p0
                         else:
                             bone.rotation_euler.z = p0
                         iType = 2
                     bone.keyframe_insert(data_path=transformN, index=iType, frame=valueArray[i][0])

                 
                 
                 
                 
                 
                 
                 fcurve = action.fcurves.find(f'pose.bones["{boneName}"].{transformN}', index=iType)
                 fcurve.group = group
                 for i in range(0, len(fcurve.keyframe_points)-1, 1):
                     p0 = valueArray[i][1]
                     p1 = valueArray[i+1][1]
                     m0 = valueArray[i][2]
                     m1 = valueArray[i][3]
                     fcurve.keyframe_points[i].handle_right_type = 'FREE'
                     fcurve.keyframe_points[i].handle_left_type = 'FREE'
                     fcurve.keyframe_points[i].handle_right.y = p0 + m1/3
                     fcurve.keyframe_points[i].handle_left.y = p0 - m0/3
                     
                 p0 = valueArray[len(fcurve.keyframe_points)-1][1]
                 m1 = valueArray[len(fcurve.keyframe_points)-1][3]
                 fcurve.keyframe_points[len(fcurve.keyframe_points)-1].handle_right.y = p0 + m1/3
                     
                     
                 bpy.context.scene.frame_end = valueArray[len(valueArray)-1][0]
        os.remove(fileName) 
                 
                 

                           
      bpy.ops.object.mode_set(mode='POSE')
      bpy.ops.pose.select_all(action='SELECT')
      bpy.ops.pose.rotation_mode_set(type='XYZ')
      bpy.ops.pose.rot_clear()
      bpy.ops.pose.loc_clear()
      bpy.ops.pose.scale_clear()
      self.report({'INFO'}, f"Selected file: {filepath}")
      return {'FINISHED'}
    
    
class OBJECT_OT_Export(Operator):
    bl_idname = "object.export_action"
    bl_label = "Export"
    bl_description = "Export MOT animation"

    def execute(self, context):
                    
                    
                    
        folder_path = context.scene.folder_path
        if not folder_path:
            self.report({'WARNING'}, "No folder selected.")
            return {'CANCELLED'}
        obj = context.object
        
        if obj and obj.type == 'ARMATURE':
           for bone in obj.pose.bones:
            for constraint in bone.constraints:
               if "BLEN2MOT" in constraint.name:
                 toggle(context);
                 break
        
        
        
        action = obj.animation_data.action if obj and obj.animation_data else None
        if action is None:
            self.report({'WARNING'}, "No action (animation) found.")
            return {'CANCELLED'}
        actionRet = ''
        for fcurve in action.fcurves:
            bone_name = fcurve.data_path.split('"')[1]
            if "location" in fcurve.data_path:
               axis = fcurve.array_index
               fcurve_type = f"Location ({'XYZ'[axis]})"
            elif "rotation_quaternion" in fcurve.data_path:
                axis = fcurve.array_index
                fcurve_type = f"Rotation (Quaternion, {'WXYZ'[axis]})"
            elif "rotation_euler" in fcurve.data_path:
                axis = fcurve.array_index
                fcurve_type = f"Rotation (Euler, {'XYZ'[axis]})"
            elif "scale" in fcurve.data_path:
                axis = fcurve.array_index
                fcurve_type = f"Scale ({'XYZ'[axis]})"
            else:
                fcurve_type = "Unknown Type"
            actionRet += 'BONE=' + bone_name+'|\n'+fcurve_type+'\n'
            
            self.report({'INFO'}, f"Processing F-Curve for bone: {bone_name}, Type: {fcurve_type}")
            for keyframe in fcurve.keyframe_points:
                time = keyframe.co.x
                value = keyframe.co.y
                left_handle = keyframe.handle_left
                right_handle = keyframe.handle_right
                m0 = (value - left_handle.y) / (time - left_handle.x) if time != left_handle.x else 0
                m1 = (right_handle.y - value) / (right_handle.x - time) if right_handle.x != time else 0
                actionRet += str(time) + "^" +str(value) + "^"+ str(m0) + "^"+str(m1)+"^\n";
        actionRet+="finish"
        file_path = folder_path + "MOTTEMP" + action.name + ".txt"
        with open(file_path, 'w') as file:
           file.write(actionRet)
           
        file_path_args = folder_path + "MOTARGS" + action.name + ".txt"
        with open(file_path_args, 'w') as file:
           file.write(file_path + '\n' + action.name + '\n' + str(context.scene.loop) + '\n' + str(context.scene.bones_that_uses_ik) + '\n' + str(context.scene.bone_path) + '\n' + str(context.scene.output) + '\n' + str(context.scene.cutscene))
        
        
        self.report({'WARNING'}, 'start /wait \"\"  \"' + context.scene.exe_path + '\" \"' + file_path_args + '\"')
        
        os.system('start /wait \"\"  \"' + context.scene.exe_path + '\" \"' + file_path_args + '\" \"False\"')
        #os.system('start cmd /k ' + context.scene.exe_path + ' ' + file_path_args)
        
        self.report({'INFO'}, "Export complete.")
        return {'FINISHED'}
    

class DAOperator(bpy.types.Operator):
    bl_idname = "pose.delete_all_location"
    bl_label = "XYZ"

    def execute(self, context):
        bpy.ops.ed.undo_push()
        action = bpy.context.object.animation_data.action
        if not action:
            self.report({'ERROR'}, "No active action found.")
            return {'CANCELLED'}

        selected_bones = bpy.context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected.")
            return {'CANCELLED'}

        for fcurve in action.fcurves:
            if fcurve.data_path.endswith('location'):
                bone_name = fcurve.data_path.split('"')[1]
                if bone_name in [bone.name for bone in selected_bones]:
                    action.fcurves.remove(fcurve)
        return {'FINISHED'} 
class DXOperator(bpy.types.Operator):
    bl_idname = "pose.delete_x_location"
    bl_label = "X"

    def execute(self, context):
        bpy.ops.ed.undo_push()
        action = bpy.context.object.animation_data.action
        if not action:
            self.report({'ERROR'}, "No active action found.")
            return {'CANCELLED'}

        selected_bones = bpy.context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected.")
            return {'CANCELLED'}

        for fcurve in action.fcurves:
            if fcurve.data_path.endswith('location') and '0' in str(fcurve.array_index):
                bone_name = fcurve.data_path.split('"')[1]
                if bone_name in [bone.name for bone in selected_bones]:
                    action.fcurves.remove(fcurve)
        return {'FINISHED'}  
                
class DYOperator(bpy.types.Operator):
    bl_idname = "pose.delete_y_location"
    bl_label = "Y"

    def execute(self, context):
        bpy.ops.ed.undo_push()
        action = bpy.context.object.animation_data.action
        if not action:
            self.report({'ERROR'}, "No active action found.")
            return {'CANCELLED'}

        selected_bones = bpy.context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected.")
            return {'CANCELLED'}

        for fcurve in action.fcurves:
            if fcurve.data_path.endswith('location') and '1' in str(fcurve.array_index):
                bone_name = fcurve.data_path.split('"')[1]
                if bone_name in [bone.name for bone in selected_bones]:
                    action.fcurves.remove(fcurve)
        return {'FINISHED'}  
    
class DZOperator(bpy.types.Operator):
    bl_idname = "pose.delete_z_location"
    bl_label = "Z"

    def execute(self, context):
        bpy.ops.ed.undo_push()
        action = bpy.context.object.animation_data.action
        if not action:
            self.report({'ERROR'}, "No active action found.")
            return {'CANCELLED'}

        selected_bones = bpy.context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected.")
            return {'CANCELLED'}

        for fcurve in action.fcurves:
            if fcurve.data_path.endswith('location') and '2' in str(fcurve.array_index):
                bone_name = fcurve.data_path.split('"')[1]
                if bone_name in [bone.name for bone in selected_bones]:
                    action.fcurves.remove(fcurve)
        return {'FINISHED'}  
    
class DRAOperator(bpy.types.Operator):
    bl_idname = "pose.delete_all_rotation"
    bl_label = "XYZ"

    def execute(self, context):
        bpy.ops.ed.undo_push()
        action = bpy.context.object.animation_data.action
        if not action:
            self.report({'ERROR'}, "No active action found.")
            return {'CANCELLED'}

        selected_bones = bpy.context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected.")
            return {'CANCELLED'}

        for fcurve in action.fcurves:
            if fcurve.data_path.endswith('rotation_euler'):
                bone_name = fcurve.data_path.split('"')[1]
                if bone_name in [bone.name for bone in selected_bones]:
                    action.fcurves.remove(fcurve)
        return {'FINISHED'}  
class DRXOperator(bpy.types.Operator):
    bl_idname = "pose.delete_x_rotation"
    bl_label = "X"

    def execute(self, context):
        bpy.ops.ed.undo_push()
        action = bpy.context.object.animation_data.action
        if not action:
            self.report({'ERROR'}, "No active action found.")
            return {'CANCELLED'}

        selected_bones = bpy.context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected.")
            return {'CANCELLED'}

        for fcurve in action.fcurves:
            if fcurve.data_path.endswith('rotation_euler') and '0' in str(fcurve.array_index):
                bone_name = fcurve.data_path.split('"')[1]
                if bone_name in [bone.name for bone in selected_bones]:
                    action.fcurves.remove(fcurve)
        return {'FINISHED'}  
                
class DRYOperator(bpy.types.Operator):
    bl_idname = "pose.delete_y_rotation"
    bl_label = "Y"

    def execute(self, context):
        bpy.ops.ed.undo_push()
        action = bpy.context.object.animation_data.action
        if not action:
            self.report({'ERROR'}, "No active action found.")
            return {'CANCELLED'}

        selected_bones = bpy.context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected.")
            return {'CANCELLED'}

        for fcurve in action.fcurves:
            if fcurve.data_path.endswith('rotation_euler') and '1' in str(fcurve.array_index):
                bone_name = fcurve.data_path.split('"')[1]
                if bone_name in [bone.name for bone in selected_bones]:
                    action.fcurves.remove(fcurve)
        return {'FINISHED'}  
    
class DRZOperator(bpy.types.Operator):
    bl_idname = "pose.delete_z_rotation"
    bl_label = "Z"

    def execute(self, context):
        bpy.ops.ed.undo_push()
        action = bpy.context.object.animation_data.action
        if not action:
            self.report({'ERROR'}, "No active action found.")
            return {'CANCELLED'}

        selected_bones = bpy.context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected.")
            return {'CANCELLED'}

        for fcurve in action.fcurves:
            if fcurve.data_path.endswith('rotation_euler') and '2' in str(fcurve.array_index):
                bone_name = fcurve.data_path.split('"')[1]
                if bone_name in [bone.name for bone in selected_bones]:
                    action.fcurves.remove(fcurve)
        return {'FINISHED'}   
class DSAOperator(bpy.types.Operator):
    bl_idname = "pose.delete_all_scale"
    bl_label = "XYZ"

    def execute(self, context):
        bpy.ops.ed.undo_push()
        action = bpy.context.object.animation_data.action
        if not action:
            self.report({'ERROR'}, "No active action found.")
            return {'CANCELLED'}

        selected_bones = bpy.context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected.")
            return {'CANCELLED'}

        for fcurve in action.fcurves:
            if fcurve.data_path.endswith('scale'):
                bone_name = fcurve.data_path.split('"')[1]
                if bone_name in [bone.name for bone in selected_bones]:
                    action.fcurves.remove(fcurve)
        return {'FINISHED'}  

class DSXOperator(bpy.types.Operator):
    bl_idname = "pose.delete_x_scale"
    bl_label = "X"

    def execute(self, context):
        bpy.ops.ed.undo_push()
        action = bpy.context.object.animation_data.action
        if not action:
            self.report({'ERROR'}, "No active action found.")
            return {'CANCELLED'}

        selected_bones = bpy.context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected.")
            return {'CANCELLED'}

        for fcurve in action.fcurves:
            if fcurve.data_path.endswith('scale') and '0' in str(fcurve.array_index):
                bone_name = fcurve.data_path.split('"')[1]
                if bone_name in [bone.name for bone in selected_bones]:
                    action.fcurves.remove(fcurve)
        return {'FINISHED'}  
class DSYOperator(bpy.types.Operator):
    bl_idname = "pose.delete_y_scale"
    bl_label = "Y"

    def execute(self, context):
        bpy.ops.ed.undo_push()
        action = bpy.context.object.animation_data.action
        if not action:
            self.report({'ERROR'}, "No active action found.")
            return {'CANCELLED'}

        selected_bones = bpy.context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected.")
            return {'CANCELLED'}

        for fcurve in action.fcurves:
            if fcurve.data_path.endswith('scale') and '1' in str(fcurve.array_index):
                bone_name = fcurve.data_path.split('"')[1]
                if bone_name in [bone.name for bone in selected_bones]:
                    action.fcurves.remove(fcurve)
        return {'FINISHED'}  
    
class DSZOperator(bpy.types.Operator):
    bl_idname = "pose.delete_z_scale"
    bl_label = "Z"

    def execute(self, context):
        bpy.ops.ed.undo_push()
        action = bpy.context.object.animation_data.action
        if not action:
            self.report({'ERROR'}, "No active action found.")
            return {'CANCELLED'}

        selected_bones = bpy.context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected.")
            return {'CANCELLED'}

        for fcurve in action.fcurves:
            if fcurve.data_path.endswith('scale') and '2' in str(fcurve.array_index):
                bone_name = fcurve.data_path.split('"')[1]
                if bone_name in [bone.name for bone in selected_bones]:
                    action.fcurves.remove(fcurve)
        return {'FINISHED'}  
    
    
    
class CleanupOperator(bpy.types.Operator):
    bl_idname = "pose.cleanup"
    bl_label = "Cleanup Curves"

    def execute(self, context):
        bpy.ops.ed.undo_push()
    
        if "curve_simplify" in bpy.context.preferences.addons:
           bpy.ops.graph.simplify(error=context.scene.simplify_factor)
           bpy.ops.ed.undo_push()
           bpy.ops.graph.simplify()
        else:
           self.report({'ERROR'}, "Simplify Curves Addon isn't enabled!")

        return {'FINISHED'}  
class OBJECT_OT_FeetSetup(Operator):
    bl_idname = "object.feet_action"
    bl_label = "Feet setup"
    bl_description = "Toggles feets for animation / export"

    def execute(self, context):
       toggle(context);
       return {'FINISHED'}
       
def toggle(context):
        if(context.scene.bones_that_uses_ik == ""):
                self.report({'ERROR'}, "No feet bone was written in the \"Foot bones\" field!")
                return {'FINISHED'}
        obj = context.object
        if obj and obj.type != 'ARMATURE':
                self.report({'ERROR'}, "Select an armature!")
                return {'FINISHED'}
        
        
        
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')


        isSetupAnimation = False
        
        
        allB = context.scene.bones_that_uses_ik.split(',')
        for b in allB:
            name = int(b)
            nameParent = int(b)-1
            Bone = obj.data.edit_bones[str(name)]
            if(Bone.parent != obj.data.edit_bones['root']):
               Bone.parent = obj.data.edit_bones['root']
               isSetupAnimation = True;
            else:
               Bone.parent = obj.data.edit_bones[str(nameParent)]
    
    
            
        bpy.ops.object.mode_set(mode='POSE')
        for bone in obj.pose.bones:
            for constraint in bone.constraints:
                  if constraint.name == "BLEN2MOT_LEG_SETUP":
                    bone.constraints.remove(constraint)
                    
                    
        for b in allB:
           name1 = int(b)-1
           name2 = int(b)
           bone = obj.pose.bones[str(name1)]
           
           if(isSetupAnimation):
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
                    if(isSetupAnimation):
                       group.color_set = 'THEME04' #for animation
                       bpy.ops.pose.select_all(action='SELECT')
                       bpy.ops.pose.group_assign(type=1)
                       bpy.ops.pose.select_all(action='DESELECT')
                       break
                    else:
                       group.color_set = 'THEME02'
                       bpy.ops.pose.select_all(action='SELECT')
                       bpy.ops.pose.group_assign(type=1)
                       bpy.ops.pose.select_all(action='DESELECT')
            
        bone_group_name = "ANIMATION_READY_PART01"
        for group in obj.pose.bone_groups:
                if group.name == bone_group_name:
                    bone_group = group
                    if(isSetupAnimation):
                       group.color_set = 'THEME08'
                       for b in allB:
                          name2 = int(b)
                          bone = obj.pose.bones[str(name2)]
                          bone.bone_group = group
                       
                       break
        bone_group_name = "ANIMATION_READY_PART02"
        for group in obj.pose.bone_groups:
                if group.name == bone_group_name:
                    bone_group = group
                    if(isSetupAnimation):
                       group.color_set = 'THEME07'
                       for b in allB:
                          name2 = int(b)-1
                          bone = obj.pose.bones[str(name2)]
                          bone.bone_group = group
        return {'FINISHED'}


class VIEW3D_PT_MOTPanel(Panel):
    bl_label = "Blen2MOT"
    bl_idname = "VIEW3D_PT_MTP"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MOT'
    boneInfo = ""
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        
        boxSett = layout.box()
        boxSett.label(text="Blen2MOT Setup", icon='IMPORT')
        boxFS = boxSett.box()
        boxFS.prop(scene, "folder_path", text="Export Folder", icon='EXPORT')
        boxFS.prop(scene, "exe_path", text="Blen2MOT Exe", icon='FILE_SCRIPT')
        boxFS.prop(scene, "bone_path", text="Bone File", icon='BONE_DATA')
        boxFS.prop(scene, "output", text="See the program output?", icon='HELP')
        
        
                
        
        boxSett = layout.box()
        
        boxSett.label(text="MOT", icon='PREVIEW_RANGE')
        boxMSA = boxSett.box()
        boxMSA.label(text="MOT Settings", icon='SETTINGS');
        
        boxMSA.prop(scene, "loop", text="Animation loops?", icon='CONSTRAINT')
        boxMSA.prop(scene, "cutscene", text="Full Precision?", icon='OUTLINER_DATA_CAMERA')
        
        boxMSa1 = boxMSA.box()
        chosen = "QUESTION"


        Mode="None"
        armature_obj = bpy.context.active_object
        
        if armature_obj and armature_obj.type == 'ARMATURE':
           for bone in armature_obj.pose.bones:
            for constraint in bone.constraints:
               if "BLEN2MOT" in constraint.name:
                 Mode = "Animation"
                 break
            if Mode != "Animation": 
                Mode = "Export"
             
             
             
             
        if Mode == "Animation":
           chosen = "PLAY"
        if Mode == "Export":
           chosen = "EXPORT"



             
             
        boxMSa1.label(text="Current Mode: " + Mode, icon=chosen);
        
        boxMSA.operator("object.feet_action", text="Toggle Foot Rig", icon='RIGHTARROW_THIN')
        
        boxMSA.prop(scene, "bones_that_uses_ik", text="Foot bones", icon='MOD_ARMATURE')
        

        
        boxMSA.separator()
        boxSett.separator();
        
        boxMS = boxSett.box()
        boxMS.label(text="MOT Utility", icon='PREVIEW_RANGE');
        boxMS.separator();
        
        boxMS1 = boxMS.box()
        boxMS1.label(text="Keyframe Cleanup", icon='KEYFRAME');
        boxKFC = boxMS1.box()#keyframe clear. it's not KFC as the food.
        
        boxKFC.label(text="Remove Location Keyframes from selected:");
        rowMS = boxKFC.row()
        rowMS.operator("pose.delete_x_location", icon='ORIENTATION_GLOBAL')
        rowMS.operator("pose.delete_y_location", icon='ORIENTATION_GLOBAL');
        rowMS.operator("pose.delete_z_location", icon='ORIENTATION_GLOBAL');
        boxKFC.operator("pose.delete_all_location", icon='ORIENTATION_GLOBAL');


        boxMS2 = boxKFC.box()
        boxMS2.label(text="Remove Rotation Keyframes from selected:");

        rowMS = boxMS2.row()
        rowMS.operator("pose.delete_x_rotation", icon='ORIENTATION_GLOBAL')
        rowMS.operator("pose.delete_y_rotation", icon='ORIENTATION_GLOBAL');
        rowMS.operator("pose.delete_z_rotation", icon='ORIENTATION_GLOBAL');     
        boxMS2.operator("pose.delete_all_rotation", icon='ORIENTATION_GLOBAL');
        
        boxMS = boxKFC.box()
        boxMS.label(text="Remove Scale Keyframes from selected:");
        rowMS = boxMS.row()
        rowMS.operator("pose.delete_x_scale", icon='ORIENTATION_GLOBAL')
        rowMS.operator("pose.delete_y_scale", icon='ORIENTATION_GLOBAL');
        rowMS.operator("pose.delete_z_scale", icon='ORIENTATION_GLOBAL');
        boxMS.operator("pose.delete_all_scale", icon='ORIENTATION_GLOBAL');
        
        boxMS = boxMS1.box()
        boxMS.label(text="Curve Cleanup", icon='FCURVE');
        boxMS1 = boxMS.box()
        boxMS1.operator("pose.cleanup", icon='ORIENTATION_GLOBAL');
        boxMS1.prop(scene, "simplify_factor", text="Cleanup Factor")
        
        
        boxSett = layout.box()
        boxSett.label(text="MOT Info", icon='INFO');
        boxIF = boxSett.box()
        boxIF.prop(scene, "show_warning", text="", icon='ERROR')
        
        
        boxSett = layout.box()
        boxMS = boxSett.box()
        boxMS.label(text="MOT File", icon='EXPORT')
        boxEP = boxMS.box()
        boxEP.operator("object.import_action", text="Import MOT", icon='PLAY')
        boxEP.operator("object.export_action", text="Export Animation to MOT", icon='PLAY')
        boxSett.separator();


def register():
    bpy.utils.register_class(OBJECT_OT_Import)
    bpy.utils.register_class(OBJECT_OT_Export)
    bpy.utils.register_class(VIEW3D_PT_MOTPanel)
    bpy.utils.register_class(OBJECT_OT_FeetSetup)
    bpy.utils.register_class(DXOperator)
    bpy.utils.register_class(DYOperator)
    bpy.utils.register_class(DZOperator)
    bpy.utils.register_class(DRXOperator)
    bpy.utils.register_class(DRYOperator)
    bpy.utils.register_class(DRZOperator)
    bpy.utils.register_class(DSXOperator)
    bpy.utils.register_class(DSYOperator)
    bpy.utils.register_class(DSZOperator)
    bpy.utils.register_class(DAOperator) 
    bpy.utils.register_class(DRAOperator)
    bpy.utils.register_class(DSAOperator) 
    bpy.types.Scene.exe_path = StringProperty(
        name="Executable Path",
        description="Path to the MOTExporter executable",
        default="C:/Users/",
        subtype='FILE_PATH'
    )
    bpy.types.Scene.show_warning = StringProperty(
        name="Animation tip:",
        description="The root bone shoud ONLY be used for x and y translations. Meanwhile, bone 0 should only be used for y translations. if you try to apply rotation or position animation that doesn't satisfy any of the bone limitations, the animation may break or not work as expected, however, any other transform animation for any other bone will work fine.",
        default="Hover me!"
    )
    bpy.types.Scene.bone_path = StringProperty(
        name="Bones Path",
        description="Path to the model .bones",
        default="C:/Users/",
        subtype='FILE_PATH'
    )
    bpy.types.Scene.folder_path = StringProperty(
        name="Folder Path",
        description="Path to selected folder",
        default="C:/Users/",
        subtype='DIR_PATH'
    )
    bpy.types.Scene.loop = BoolProperty(
        name="Loops",
        description="If the animation loops",
        default=False
    )
    
    
    
    
    
    bpy.types.Scene.cutscene= BoolProperty(
        name="Full precision",
        description="If the MOT uses Full Precision movements (takes more storage, usually used in cutscenes)",
        default=False
    )
    
    
    
    
    
    
    
    bpy.types.Scene.output = BoolProperty(
        name="See Output",
        description="Check this if you want to see the program output once you export the animation, in case the file isn't working, etc..",
        default=False
    )
    bpy.types.Scene.bones_that_uses_ik = StringProperty(
        name="Bones that utilizes different movement space",
        description="\n(used for feet bones.)\n\nList in the bones that moves in reference from the root bone.\nYou can set them by writting in here the bones in sequence. i.e: root,1,2,5,7\nWrite them with NO SPACES IN BETWEEN, only numbers.\nLeave this space blank if the animation don't utilize IK at all",
        default=""
    )
    bpy.types.Scene.simplify_factor = FloatProperty(
        name="Simplify Factor",
        description="The factor of curve cleanup you want in the animation",
        default=0.1
    )
    bpy.utils.register_class(CleanupOperator)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_Export)
    bpy.utils.unregister_class(OBJECT_OT_Import)
    bpy.utils.unregister_class(OBJECT_OT_FeetSetup)
    bpy.utils.unregister_class(VIEW3D_PT_MOTPanel)
    bpy.utils.unregister_class(DAOperator) 
    bpy.utils.unregister_class(DXOperator)
    bpy.utils.unregister_class(DYOperator)
    bpy.utils.unregister_class(DZOperator)
    bpy.utils.unregister_class(DRAOperator)
    bpy.utils.unregister_class(DRXOperator)
    bpy.utils.unregister_class(DRYOperator)
    bpy.utils.unregister_class(DRZOperator)
    bpy.utils.unregister_class(DSXOperator)
    bpy.utils.unregister_class(DSYOperator)
    bpy.utils.unregister_class(DSZOperator)
    bpy.utils.unregister_class(DSAOperator)
    bpy.utils.unregister_class(CleanupOperator)
    del bpy.types.Scene.simplify_factor
    del bpy.types.Scene.folder_path
    del bpy.types.Scene.cutscene
    del bpy.types.Scene.exe_path
    del bpy.types.Scene.bone_path
    del bpy.types.Scene.loop
    del bpy.types.Scene.bones_that_uses_ik
    del bpy.types.Scene.show_warning
    del bpy.types.Scene.output
if __name__ == "__main__":
    register()
