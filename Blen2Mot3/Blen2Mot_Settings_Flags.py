bl_info = {
    "name": "Blen2Mot Flags",
    "blender": (3, 6, 0),
    "category": "3D View",
    "author": "Akito",
    "version": (2, 0, 0),
    "description": "Export Animation directly to MOT",
    "tracker_url": "https://github.com/akitotheanimator/God-Hand-Tools/tree/main",
}


import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty,CollectionProperty,EnumProperty,IntProperty
from bpy.types import Panel, Operator,OperatorFileListElement,PropertyGroup
from bpy_extras.io_utils import ImportHelper
import os
import re
import struct
from bl_ui.properties_paint_common import UnifiedPaintPanel
from enum import Enum

        
class VIEW3D_PT_MOTFlagPanel_MOT(Panel):
    bl_label = "Settings Flags"
    bl_idname = "VIEW3D_PT_MOT_MOT_PANEL_FLAGS"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MOT'
    
    

    
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
           
        split = layout.split(factor=0.5)
        
        lt = layout.box()
        
        lt.label(text="Foot rig", icon='MENU_PANEL')
        lt.operator("object.feet_action_mot", text="Toggle Foot Rig for Selected", icon='RIGHTARROW_THIN')
        lt.separator()
        lt.separator()
        
        lt.operator("wm.add_new_curve_flags_mot")
        lt.operator("wm.remove_curve_flags_mot")
        lt.label(text="Bones with precise properties:")
        
        
        box = lt.box()
        selected_obj = bpy.context.object            
        selected_pose_bones = [pose_bone for pose_bone in selected_obj.pose.bones] 
        for a in selected_pose_bones:
            prop_names = list(a.keys())

            for prop_name in prop_names:
                if "MOTSF" in prop_name:
                    property = prop_name.split(".")[1]
                    
                    
                    pli = box.split(factor=0.2)
                    pli.label(text="Bone: ")
                    box3 = pli.box()
                    box3.label(text=a.name)
                    
                    pli.label(text=" Property: ")
                    box4 = pli.box()
                    box4.label(text=property)

                    prop_value = a[prop_name]
                    
                    
                    box5 = pli.box()
                    box5.label(text=str(prop_value[0]))
                    box5.label(text=str(prop_value[1]))
                    box6 = pli.box()
                    box6.label(text=str(prop_value[2]))
                    box6.label(text=str(prop_value[3]))
                    
                    


class AddFlagToList_MOT(bpy.types.Operator):
    bl_idname = "bone.add_flag_to_list_mot"
    bl_label = "Add to List"
    bl_description = "Finish the add operation"
    def execute(self, context):
        selected_obj = bpy.context.object
        selected_pose_bones = [pose_bone for pose_bone in selected_obj.pose.bones if pose_bone.bone.select] 
        for a in selected_pose_bones:
            a["MOTSF."+context.scene.property_FLAGS_MOT] = (context.scene.flags_1_MOT,context.scene.flags_2_MOT,context.scene.flags_3_MOT,context.scene.flags_4_MOT)
            
        return {'FINISHED'}  
class RemoveFlagFromList_MOT(bpy.types.Operator):
    bl_idname = "bone.remove_flag_from_list_mot"
    bl_label = "Remove from List"
    bl_description = "Finish the removal operation"
    def execute(self, context):
        
        selected_obj = bpy.context.object            
        selected_pose_bones = [pose_bone for pose_bone in selected_obj.pose.bones if pose_bone.bone.select] 
        for a in selected_pose_bones:
            prop_names = list(a.keys())

            for prop_name in prop_names:
                print(prop_name)
                if "MOTSF" in prop_name:
                    property = prop_name.split(".")[1]
                    if context.scene.property_FLAGS_MOT == property or context.scene.property_FLAGS_MOT == "Every Property" or  context.scene.property_FLAGS_MOT == "All Positions" and "Position" in property or context.scene.property_FLAGS_MOT == "All Rotations" and "Rotation" in property or context.scene.property_FLAGS_MOT == "All Scales" and "Scale" in property or context.scene.property_FLAGS_MOT == "All Scales" and "Scale" in property:
                        del a[prop_name]
        return {'FINISHED'}  

class AddFlags_MOT(bpy.types.Operator, UnifiedPaintPanel):
    bl_idname = "wm.add_new_curve_flags_mot"
    bl_label = "Add Flag to Curve"
    bl_description = "add a flags to the curve of a bone"
    
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object  
        if active_object != None and context.active_object.mode == 'POSE':
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
        layout.prop(context.scene,"property_FLAGS_MOT")
        
        row1 = layout.split()
        row1.prop(context.scene,"flags_1_MOT",text="Flag 1")
        row1.prop(context.scene,"flags_2_MOT",text="Flag 2")
        row2 = layout.split()
        row2.prop(context.scene,"flags_3_MOT",text="Flag 3")
        row2.prop(context.scene,"flags_4_MOT",text="Flag 4")
        
        
        layout.operator("bone.add_flag_to_list_mot")
        
        
    def execute(self, context):
        return context.window_manager.invoke_popup(self, width=300)
        return {'FINISHED'}  
        

        
    
class RemoveFlags_MOT(bpy.types.Operator, UnifiedPaintPanel):
    bl_idname = "wm.remove_curve_flags_mot"
    bl_label = "Remove Flags"
    bl_description = "remove a precision movement to a bone. If you set a precision movement, once the MOT export, the movements will be a lot more precise (If keyframes were created for that bone)"
    
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object  
        if active_object != None and context.active_object.mode == 'POSE':
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
        layout.prop(context.scene,"property_FLAGS_MOT")
        layout.operator("bone.remove_flag_from_list_mot")
        
        
    def execute(self, context):
        return context.window_manager.invoke_popup(self, width=300)
        return {'FINISHED'} 
    
    
    
def toggle(context,self):
        obj = context.object
        if obj and obj.type != 'ARMATURE':
                self.report({'ERROR'}, "No feet bone was written in the \"Foot rig\" field!")
                return {'CANCELLED'}
        
        
        
        bpy.ops.object.mode_set(mode='POSE')
        selected_bones = [bone.name for bone in obj.pose.bones if bone.bone.select]
        ik_feet_bones = ""
        for i in selected_bones:
            ik_feet_bones += i + ","
        ik_feet_bones  = ik_feet_bones[:-1]
        
        
        
        bpy.ops.object.mode_set(mode='EDIT')


        setup = False
        
        
        allB = ik_feet_bones.split(',')
        for b in allB:
            bone1 = obj.data.edit_bones[b]
            bone2 = obj.data.edit_bones[b].parent
            
            bog = obj.data.edit_bones[str(int(b.replace("root","0"))-2)]
            
            
            if bone2.name != "root":
                setup = True
                bone1.parent = obj.data.edit_bones["root"]
            
            else:
                bone3 = obj.data.edit_bones[str(int(b.replace("root","0"))-1)]
                bone1.parent = bone3
                         
        bpy.ops.object.mode_set(mode='POSE')
        
        
        
        #for bone_group_name in obj.pose.bone_groups:
        #    obj.pose.bone_groups.remove(obj.pose.bone_groups[bone_group_name.name])
        
        bone_group_name = "SPACE_SWITCH"
        if bone_group_name in obj.pose.bone_groups != False:
           new_bone_group1 = obj.pose.bone_groups[bone_group_name]
        else:
           new_bone_group1 = obj.pose.bone_groups.new(name=bone_group_name)
        new_bone_group1.color_set = 'THEME02'
        
        
        bone_group_name = "FOLLOWER"
        if bone_group_name in obj.pose.bone_groups != False:
           new_bone_group2 = obj.pose.bone_groups[bone_group_name]
        else:
           new_bone_group2 = obj.pose.bone_groups.new(name=bone_group_name)
        new_bone_group2.color_set = 'THEME04'
        
        
        bone_group_name = "DEFAULT"           
        if bone_group_name in obj.pose.bone_groups != False:
           new_bone_group3 = obj.pose.bone_groups[bone_group_name]
        else:
           new_bone_group3 = obj.pose.bone_groups.new(name=bone_group_name)
        new_bone_group3.color_set = 'DEFAULT'
        
        
        for bone_group_name in obj.pose.bone_groups:
           if bone_group_name.name != "SPACE_SWITCH" and bone_group_name.name != "FOLLOWER" and bone_group_name.name != "DEFAULT":
               obj.pose.bone_groups.remove(obj.pose.bone_groups[bone_group_name.name])
               
               
               
        for b in allB:
            bone1 = obj.pose.bones[b]
            bone = obj.pose.bones[str(int(b.replace("root","0"))-1)]
            bone2 = obj.pose.bones[str(int(b.replace("root","0"))-2)]
            
            
            bone.bone_group = new_bone_group1
            bone1.bone_group = new_bone_group2
            
            
                           
            if(setup):
                constraint_exists = any(constraint.name == "BLEN2MOT_LEG_SETUP" for constraint in bone.constraints)
                if not constraint_exists:
                   constraint = bone.constraints.new('TRACK_TO')
                   constraint.name = "BLEN2MOT_LEG_SETUP"
                   constraint.track_axis = 'TRACK_NEGATIVE_Y'
                   constraint.up_axis = 'UP_Z'
                   constraint.use_target_z = True
                   constraint.target = obj
                   constraint.subtarget = str(b)
                   
                   prop_names = list(bone2.keys())
                   fi = 0
                   for prop_name in prop_names:
                     if "MOTSF.All Rotations" in prop_name:
                         va = bone2["MOTSF.All Rotations"]
                         fi += 1
                         bone2["MOTSF.All Rotations"] = (1,va[1],va[2],va[3])
                         break
                   if fi == 0:     
                         bone2["MOTSF.All Rotations"] = (1,0,0,0)
            else:
                
                prop_names = list(bone2.keys())
                for prop_name in prop_names:
                       if "MOTSF.All Rotations" in prop_name:
                         va = bone2["MOTSF.All Rotations"]
                         if va[0] == 1 and va[1] == 0 and  va[2] == 0 and  va[3] == 0:
                             del bone2[prop_name]
                         else:
                             if va[0] == 1:
                                 va[0] = 0
                         
                for constraint in bone.constraints:
                    if constraint.name == "BLEN2MOT_LEG_SETUP":
                        bone.constraints.remove(constraint)
                bone.bone_group = new_bone_group3
                bone1.bone_group = new_bone_group3
        
        return {'FINISHED'}
    
class OBJECT_OT_FeetSetup_MOT(Operator):
    bl_idname = "object.feet_action_mot"
    bl_label = "Feet setup"
    bl_description = ""

    def execute(self, context):
       toggle(context,self);
       return {'FINISHED'}
    @classmethod
    def poll(cls, context):
        active_object = context.active_object  
        if active_object != None and context.active_object.mode == 'POSE':
           selected_pose_bones = [pose_bone for pose_bone in active_object.pose.bones if pose_bone.bone.select]  
           return active_object is not None and context.active_object.mode == 'POSE' and len(selected_pose_bones) > 0
        
        
        
def register():
    bpy.utils.register_class(VIEW3D_PT_MOTFlagPanel_MOT)
    bpy.utils.register_class(AddFlags_MOT)
    bpy.utils.register_class(AddFlagToList_MOT)
    bpy.utils.register_class(RemoveFlags_MOT)
    bpy.utils.register_class(RemoveFlagFromList_MOT)
    bpy.utils.register_class(OBJECT_OT_FeetSetup_MOT)
    bpy.types.Scene.property_FLAGS_MOT = EnumProperty(
          name="Property",
          description="Sets the UP Axis of the model",
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
    
    
    
    bpy.types.Scene.flags_1_MOT = IntProperty(
          name="Flags",
          description="Curve Flags",
          default=0,
          min=0,
          max=255,
    )
    bpy.types.Scene.flags_2_MOT = IntProperty(
          name="Flags",
          description="Curve Flags",
          default=0,
          min=0,
          max=255,
    )
    bpy.types.Scene.flags_3_MOT = IntProperty(
          name="Flags",
          description="Curve Flags",
          default=0,
          min=0,
          max=255,
    )
    bpy.types.Scene.flags_4_MOT = IntProperty(
          name="Flags",
          description="Curve Flags",
          default=0,
          min=0,
          max=255,
    )
    
    
def unregister():
    del bpy.types.Scene.property_FLAGS_MOT
    del bpy.types.Scene.flags_1_MOT
    del bpy.types.Scene.flags_2_MOT
    del bpy.types.Scene.flags_3_MOT
    del bpy.types.Scene.flags_4_MOT
    bpy.utils.unregister_class(OBJECT_OT_FeetSetup_MOT)
    bpy.utils.unregister_class(VIEW3D_PT_MOTFlagPanel_MOT)
    bpy.utils.unregister_class(AddFlags_MOT)
    bpy.utils.unregister_class(AddFlagToList_MOT)
    bpy.utils.unregister_class(RemoveFlags_MOT)
    bpy.utils.unregister_class(RemoveFlagFromList_MOT)
    
if __name__ == "__main__":
    register()
