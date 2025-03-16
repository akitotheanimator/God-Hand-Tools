bl_info = {
    "name": "Blen2Mot Utility",
    "blender": (3, 6, 0),
    "category": "3D View",
    "author": "Akito",
    "version": (2, 0, 0),
    "description": "Export Animation directly to MOT",
    "warning": "Use only EULER Rotations. QUATERNION rotations will be IGNORED",
    "tracker_url": "https://github.com/akitotheanimator/God-Hand-Tools/tree/main",
}


import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty,CollectionProperty
from bpy.types import Panel, Operator,OperatorFileListElement,PropertyGroup
from bpy_extras.io_utils import ImportHelper
import os
import re
import struct
from bl_ui.properties_paint_common import UnifiedPaintPanel
from enum import Enum



class VIEW3D_PT_MOTUtilityPanel(Panel):
    bl_label = "Utility"
    bl_idname = "VIEW3D_PT_MOT_UTILITY_PANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MOT'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        la = layout.box()
        la.label(text="Keyframe Cleanup", icon='KEYFRAME');
        boxKFC = la.box()
        
        boxKFC.label(text="Remove Location Keyframes from selected:");
        rowMS = boxKFC.row()
        rowMS.operator("pose.delete_x_location_mot", icon='ORIENTATION_GLOBAL')
        rowMS.operator("pose.delete_y_location_mot", icon='ORIENTATION_GLOBAL');
        rowMS.operator("pose.delete_z_location_mot", icon='ORIENTATION_GLOBAL');
        boxKFC.operator("pose.delete_all_location_mot", icon='ORIENTATION_GLOBAL');


        boxMS2 = boxKFC.box()
        boxMS2.label(text="Remove Rotation Keyframes from selected:");

        rowMS = boxMS2.row()
        rowMS.operator("pose.delete_x_rotation_mot", icon='ORIENTATION_GLOBAL')
        rowMS.operator("pose.delete_y_rotation_mot", icon='ORIENTATION_GLOBAL');
        rowMS.operator("pose.delete_z_rotation_mot", icon='ORIENTATION_GLOBAL');     
        boxMS2.operator("pose.delete_all_rotation_mot", icon='ORIENTATION_GLOBAL');
        
        boxMS = boxKFC.box()
        boxMS.label(text="Remove Scale Keyframes from selected:");
        rowMS = boxMS.row()
        rowMS.operator("pose.delete_x_scale_mot", icon='ORIENTATION_GLOBAL')
        rowMS.operator("pose.delete_y_scale_mot", icon='ORIENTATION_GLOBAL');
        rowMS.operator("pose.delete_z_scale_mot", icon='ORIENTATION_GLOBAL');
        boxMS.operator("pose.delete_all_scale_mot", icon='ORIENTATION_GLOBAL');
        
        la.separator()
        la.separator()
        
        la.label(text="Curve Cleanup", icon='FCURVE');
        boxMS1 = la.box()
        boxMS1.operator("pose.cleanup_mot", icon='ORIENTATION_GLOBAL');
        boxMS1.prop(scene, "simplify_factor_MOT", text="Cleanup Factor")

def delete_curves(context,self,type):
        bpy.ops.ed.undo_push()
        action = bpy.context.object.animation_data.action
        if not action:
            self.report({'ERROR'}, "No active action found.")
            return {'CANCELLED'}

        selected_bones = bpy.context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "No bones selected.")
            return {'CANCELLED'}



        typ = ""
        res = str(type)
        if type >= 0 and type < 4:
                typ = 'location'
        if type > 3 and type < 8:
                typ = 'rotation_euler'
        if type > 7:
                typ = 'scale'   
                
                
                
                
        if type == 0 or type == 4 or type == 8:
           res = ''     
        if type == 1 or type == 5 or type == 9:
                res = '0'  
        if type == 2 or type == 6 or type == 10:
                res = '1' 
        if type == 3 or type == 7 or type == 11:
                res = '2'
                
                
                

        print(typ + "     " + res + "     " + str(type))
        for fcurve in action.fcurves: 
              if fcurve.data_path.endswith(typ) and res in str(fcurve.array_index):
                bone_name = fcurve.data_path.split('"')[1]
                if bone_name in [bone.name for bone in selected_bones]:
                    action.fcurves.remove(fcurve)
    


class CleanupOperator(bpy.types.Operator):
    bl_idname = "pose.cleanup_mot"
    bl_label = "Cleanup Curves"

    def execute(self, context):
        bpy.ops.ed.undo_push()
    
        if "curve_simplify" in bpy.context.preferences.addons:
           bpy.ops.graph.simplify(error=context.scene.simplify_factor_MOT)
           bpy.ops.ed.undo_push()
           bpy.ops.graph.simplify()
        else:
           self.report({'ERROR'}, "Simplify Curves Addon isn't enabled!")

        return {'FINISHED'}  
    
    
    
class DAOperator(bpy.types.Operator):
    bl_idname = "pose.delete_all_location_mot"
    bl_label = "XYZ"

    def execute(self, context):
        delete_curves(context,self,0)
        return {'FINISHED'} 
class DXOperator(bpy.types.Operator):
    bl_idname = "pose.delete_x_location_mot"
    bl_label = "X"

    def execute(self, context):
        delete_curves(context,self,1)
        return {'FINISHED'}  
                
class DYOperator(bpy.types.Operator):
    bl_idname = "pose.delete_y_location_mot"
    bl_label = "Y"

    def execute(self, context):
        delete_curves(context,self,2)
        return {'FINISHED'}  
    
class DZOperator(bpy.types.Operator):
    bl_idname = "pose.delete_z_location_mot"
    bl_label = "Z"

    def execute(self, context):
        delete_curves(context,self,3)
        return {'FINISHED'}  
    
class DRAOperator(bpy.types.Operator):
    bl_idname = "pose.delete_all_rotation_mot"
    bl_label = "XYZ"

    def execute(self, context):
        delete_curves(context,self,4)
        return {'FINISHED'}  
class DRXOperator(bpy.types.Operator):
    bl_idname = "pose.delete_x_rotation_mot"
    bl_label = "X"

    def execute(self, context):
        delete_curves(context,self,5)
        return {'FINISHED'}  
                
class DRYOperator(bpy.types.Operator):
    bl_idname = "pose.delete_y_rotation_mot"
    bl_label = "Y"

    def execute(self, context):
        delete_curves(context,self,6)
        return {'FINISHED'}  
    
class DRZOperator(bpy.types.Operator):
    bl_idname = "pose.delete_z_rotation_mot"
    bl_label = "Z"

    def execute(self, context):
        delete_curves(context,self,7)
        return {'FINISHED'}   
class DSAOperator(bpy.types.Operator):
    bl_idname = "pose.delete_all_scale_mot"
    bl_label = "XYZ"

    def execute(self, context):
        delete_curves(context,self,8)
        return {'FINISHED'}  

class DSXOperator(bpy.types.Operator):
    bl_idname = "pose.delete_x_scale_mot"
    bl_label = "X"

    def execute(self, context):
        delete_curves(context,self,9)
        return {'FINISHED'}  
class DSYOperator(bpy.types.Operator):
    bl_idname = "pose.delete_y_scale_mot"
    bl_label = "Y"

    def execute(self, context):
        delete_curves(context,self,10)
        return {'FINISHED'}  
    
class DSZOperator(bpy.types.Operator):
    bl_idname = "pose.delete_z_scale_mot"
    bl_label = "Z"

    def execute(self, context):
        delete_curves(context,self,11)
        return {'FINISHED'} 

    
def register():
    bpy.utils.register_class(VIEW3D_PT_MOTUtilityPanel)
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
    bpy.utils.register_class(CleanupOperator)
    bpy.types.Scene.simplify_factor_MOT = FloatProperty(
        name="Simplify Factor",
        description="The factor of curve cleanup you want in the animation",
        default=0.01
    )
    

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_MOTUtilityPanel)
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
    del bpy.types.Scene.simplify_factor_MOT
    
if __name__ == "__main__":
    register()
