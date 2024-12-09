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
from bpy.props import StringProperty, BoolProperty, FloatProperty
from bpy.types import Panel, Operator
from bpy_extras.io_utils import ImportHelper
import os

class OBJECT_OT_Export(Operator):
    bl_idname = "object.export_action"
    bl_label = "Export"
    bl_description = "Export animation F-Curves with Hermite interpolation values"

    def execute(self, context):
        folder_path = context.scene.folder_path
        if not folder_path:
            self.report({'WARNING'}, "No folder selected.")
            return {'CANCELLED'}
        obj = context.object
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
           
        os.system('start /wait \"\"  \"' + context.scene.exe_path + '\" \"' + file_path_args + '\"')
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
    bl_description = "Prepares feets for animation / export"

    def execute(self, context):
        if(context.scene.bones_that_uses_ik == ""):
                self.report({'ERROR'}, "No feet bone was written in the \"Foot bones\" field!")
                return {'FINISHED'}
        obj = context.object
        
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')


        isSetupAnimation = False
        
        
        allB = context.scene.bones_that_uses_ik.split(',')
        for b in allB:
            name = int(b)+3
            nameParent = int(b)+2
            Bone = obj.data.edit_bones[str(name)]
            if(Bone.parent != obj.data.edit_bones['root']):
               Bone.parent = obj.data.edit_bones['root']
               isSetupAnimation = True;
            else:
               Bone.parent = obj.data.edit_bones[str(nameParent)]
    
    
    
            
        bpy.ops.object.mode_set(mode='POSE')
        for b in allB:
           name1 = int(b)+2
           name2 = int(b)+3
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
           else:
               for constraint in bone.constraints:
                  if constraint.name == "BLEN2MOT_LEG_SETUP":
                    bone.constraints.remove(constraint)
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
                          name2 = int(b)+3
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
                          name2 = int(b)+2
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
        
        
        layout.label(text="File Settings", icon='IMPORT')
        boxFS = layout.box()
        boxFS.prop(scene, "folder_path", text="Export Folder", icon='EXPORT')
        boxFS.prop(scene, "exe_path", text="MOTExporter", icon='FILE_SCRIPT')
        boxFS.prop(scene, "bone_path", text="Bone File", icon='BONE_DATA')
        boxFS.prop(scene, "output", text="See the program output?", icon='HELP')
        layout.separator()
        
        
        
        layout.label(text="MOT", icon='PREVIEW_RANGE')
        boxMSA = layout.box()
        boxMS = boxMSA.box()
        boxMS.label(text="MOT Settings", icon='SETTINGS');
        
        
        boxMS.prop(scene, "loop", text="Animation loops?", icon='CONSTRAINT')
        boxMS.prop(scene, "cutscene", text="Full Precision?", icon='OUTLINER_DATA_CAMERA')
        
        
        
        boxMS.operator("object.feet_action", text="Toggle Foot Rig", icon='RIGHTARROW_THIN')
        
        boxMS.prop(scene, "bones_that_uses_ik", text="Foot bones", icon='MOD_ARMATURE')
        
        boxHI = boxMS.box()
        boxHI.separator();
        boxHI.label(text="Bone hierchary", icon='MOD_ARMATURE')
        boxHI.separator();
        
        armature_obj = bpy.context.active_object
        if armature_obj and armature_obj.type == 'ARMATURE':
            bones = armature_obj.data.bones
            def print_bone_info(bone, level=0):
                parent_index = -1 if bone.parent is None else bones.find(bone.parent.name)
                bn = ""
                if "root" in bone.name:
                    bn = str(int(bone.name.replace("root", "0")) - 3)
                else:
                    if bone.name.isdigit():
                       bn = str(int(bone.name) - 3)
                    
                    
                boxHI.label(text=f"Bone: {bone.name}     |||     Level: {bn}");
                boxHI.scale_y = 0.5
                for child_bone in bone.children:
                    print_bone_info(child_bone, level + 1)
            for bone in bones:
                if bone.parent is None:
                    print_bone_info(bone)
        else:
            boxHI.label(text="Armature not found.");
        
        boxHI.separator();
        boxMS.separator()
        boxMS = boxMSA.box()
        
        
        boxMS1 = boxMS.box()
        boxMS1.label(text="MOT Utility", icon='PREVIEW_RANGE');
        boxMS1.separator();
        
        
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
        

        
        boxMS1.label(text="Curve Cleanup", icon='FCURVE');
        boxMS1 = boxMS1.box()
        boxMS1.operator("pose.cleanup", icon='ORIENTATION_GLOBAL');
        boxMS1.prop(scene, "simplify_factor", text="Cleanup Factor")
        
        
        
        layout.label(text="MOT Info", icon='INFO');
        boxIF = layout.box()
        boxIF.prop(scene, "show_warning", text="", icon='ERROR')
        layout.separator();
        
        layout.label(text="MOT Exporting", icon='EXPORT')
        boxEP = layout.box()
        boxEP.operator("object.export_action", text="Export Animation to MOT", icon='PLAY')


def register():
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
