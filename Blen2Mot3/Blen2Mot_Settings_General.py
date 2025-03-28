bl_info = {
    "name": "Blen2Mot Settings General",
    "blender": (3, 6, 0),
    "category": "3D View",
    "author": "Akito",
    "version": (2, 0, 0),
    "description": "Export Animation directly to MOT",
    "tracker_url": "https://github.com/akitotheanimator/God-Hand-Tools/tree/main",
}


import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty,CollectionProperty,EnumProperty
from bpy.types import Panel, Operator,OperatorFileListElement,PropertyGroup
from bpy_extras.io_utils import ImportHelper
import os
import re
import struct
from bl_ui.properties_paint_common import UnifiedPaintPanel
from enum import Enum

        
class VIEW3D_PT_MOTSettingsPanel(Panel):
    bl_label = "Settings"
    bl_idname = "VIEW3D_PT_MOT_MOT_PANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MOT'
    
    

    
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        tool = context.scene.properties_MOT
        obj = context.object
           
        split = layout.split(factor=0.5)
        split.prop(tool, "loop_MOT")
        
        split.label(icon="LOOP_FORWARDS")
        layout.separator()
        #layout.box()
        layout.separator()
        
        lt = layout.box()
        lt.operator("wm.add_new_precise_bone_mot")
        lt.operator("wm.remove_new_precise_bone_mot")
        lt.label(text="Bones with precise properties:")
        
        
        box = lt.box()
        
        
        selected_obj = bpy.context.object            
        selected_pose_bones = [pose_bone for pose_bone in selected_obj.pose.bones] 
        for a in selected_pose_bones:
            prop_names = list(a.keys())

            for prop_name in prop_names:
                if "MOTFP" in prop_name:
                    property = prop_name.split(".")[1]
                    pli = box.split(factor=0.2)
                    pli.label(text="Bone: ")
                    box3 = pli.box()
                    box3.label(text=a.name)
                    
                    pli.label(text=" Property: ")
                    box4 = pli.box()
                    box4.label(text=property)



class AddBoneToList_MOT(bpy.types.Operator):
    bl_idname = "bone.add_to_list_mot"
    bl_label = "Add to List"
    bl_description = "Finish the add operation"
    def execute(self, context):
        selected_obj = bpy.context.object
        if selected_obj != None:
          selected_pose_bones = [pose_bone for pose_bone in selected_obj.pose.bones if pose_bone.bone.select] 
          for a in selected_pose_bones:
            a["MOTFP."+context.scene.property_MOT] = 1
        return {'FINISHED'}  
class RemoveBoneFromList_MOT(bpy.types.Operator):
    bl_idname = "bone.remove_from_list_mot"
    bl_label = "Remove from List"
    bl_description = "Finish the removal operation"
    def execute(self, context):

        
        selected_obj = bpy.context.object            
        selected_pose_bones = [pose_bone for pose_bone in selected_obj.pose.bones if pose_bone.bone.select] 
        for a in selected_pose_bones:
            prop_names = list(a.keys())

            for prop_name in prop_names:
                print(prop_name)
                if "MOTFP" in prop_name:
                    property = prop_name.split(".")[1]
                    if context.scene.property_MOT == property or context.scene.property_MOT == "Every Property" or  context.scene.property_MOT == "All Positions" and "Position" in property or context.scene.property_MOT == "All Rotations" and "Rotation" in property or context.scene.property_MOT == "All Scales" and "Scale" in property or context.scene.property_MOT == "All Scales" and "Scale" in property:
                        del a[prop_name]
        return {'FINISHED'}  

class AddBonePrecision_MOT(bpy.types.Operator, UnifiedPaintPanel):
    bl_idname = "wm.add_new_precise_bone_mot"
    bl_label = "Add Precision movement"
    bl_description = "add a precision movement to a bone. If you set a precision movement, once the MOT export, the movements will be a lot more precise (If keyframes were created for that bone)"
    
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object 
        if active_object != None: 
           selected_pose_bones = [pose_bone for pose_bone in active_object.pose.bones if pose_bone.bone.select]  
           return active_object is not None and context.active_object.mode == 'POSE' and len(selected_pose_bones) > 0
        
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        selected_obj = bpy.context.object
        selected_pose_bones = [pose_bone for pose_bone in selected_obj.pose.bones if pose_bone.bone.select] 
        bones = "" 
        for a in selected_pose_bones:
            bones+= a.name+", ";
        bones = bones[:-2]
            
        layout.label(text="Selected bone(s): " + bones)
        layout.prop(context.scene,"property_MOT")
        layout.operator("bone.add_to_list_mot")
        
        
    def execute(self, context):
        return context.window_manager.invoke_popup(self, width=300)
        return {'FINISHED'}  
        

        
    
class RemoveBonePrecision_MOT(bpy.types.Operator, UnifiedPaintPanel):
    bl_idname = "wm.remove_new_precise_bone_mot"
    bl_label = "Remove Precision movement"
    bl_description = "remove a precision movement to a bone. If you set a precision movement, once the MOT export, the movements will be a lot more precise (If keyframes were created for that bone)"
    
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object  
        if active_object != None:
           selected_pose_bones = [pose_bone for pose_bone in active_object.pose.bones if pose_bone.bone.select]  
           return active_object is not None and context.active_object.mode == 'POSE' and len(selected_pose_bones) > 0
        
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        selected_obj = bpy.context.object
        
    
        
        
        
        selected_pose_bones = [pose_bone for pose_bone in selected_obj.pose.bones if pose_bone.bone.select] 
        bones = "" 
        for a in selected_pose_bones:
            bones+= a.name+", ";
        bones = bones[:-2]
            
        layout.label(text="Selected bone(s): " + bones)
        layout.prop(context.scene,"property_MOT")
        layout.operator("bone.remove_from_list_mot")
        
        
    def execute(self, context):
        return context.window_manager.invoke_popup(self, width=300)
        return {'FINISHED'}  
def register():
    bpy.utils.register_class(VIEW3D_PT_MOTSettingsPanel)
    bpy.utils.register_class(AddBonePrecision_MOT)
    bpy.utils.register_class(AddBoneToList_MOT)
    bpy.utils.register_class(RemoveBonePrecision_MOT)
    bpy.utils.register_class(RemoveBoneFromList_MOT)
    bpy.types.Scene.property_MOT = EnumProperty(
          name="Property",
          description="Sets the UP Axis of the model.",
          items=(
            ('Position X', "Position X", ""),
            ('Position Y', "Position Y", ""),
            ('Position Z', "Position Z", ""),
            ('Rotation X', "Rotation X", ""),
            ('Rotation Y', "Rotation Y", ""),
            ('Rotation Z', "Rotation Z", ""),
            ('Scale X', "Scale X", ""),
            ('Scale Y', "Scale Y", ""),
            ('Scale Z', "Scale Z", ""),
            ('All Positions', "All Positions", ""),
            ('All Rotations', "All Rotations", ""),
            ('All Scales', "All Scales", ""),
            ('Every Property', "Every Property", ""),
          ),
          default='Position X',
    ) 


def unregister():
    del bpy.types.Scene.property_MOT
    
    bpy.utils.unregister_class(VIEW3D_PT_MOTSettingsPanel)
    bpy.utils.unregister_class(AddBonePrecision_MOT)
    bpy.utils.unregister_class(AddBoneToList_MOT)
    bpy.utils.unregister_class(RemoveBonePrecision_MOT)
    bpy.utils.unregister_class(RemoveBoneFromList_MOT)
    
if __name__ == "__main__":
    register()
