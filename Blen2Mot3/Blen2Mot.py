bl_info = {
    "name": "Blen2Mot General",
    "blender": (3, 6, 0),
    "category": "3D View",
    "author": "Akito",
    "version": (2, 0, 0),
    "description": "Export Animation directly to MOT",
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



        

class B2MPrefs_MOT(bpy.types.AddonPreferences):
    bl_idname = __name__
    open_folder_MOT: BoolProperty(
        name="Open folder after exporting",
        description="after exporting, blender will open the folder where the mot was saved",
        default=True
    )
    
    

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "open_folder_MOT")

class Properties_MOT(PropertyGroup):
    loop_MOT: BoolProperty(
        name="MOT Loops",
        description="If the animation loops",
        default=False
    )


def register():
    bpy.utils.register_class(B2MPrefs_MOT)
    bpy.utils.register_class(Properties_MOT)
    bpy.types.Scene.properties_MOT = bpy.props.PointerProperty(type=Properties_MOT)

def unregister():
    bpy.utils.unregister_class(B2MPrefs_MOT)
    bpy.utils.unregister_class(Properties_MOT)
    del bpy.types.Scene.properties_MOT
    
if __name__ == "__main__":
    register()
