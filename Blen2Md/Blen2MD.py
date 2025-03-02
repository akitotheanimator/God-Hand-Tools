bl_info = {
    "name": "Blen2MD",
    "blender": (3, 2, 0),
    "category": "3D View",
    "author": "Akito",
    "version": (1, 0, 0),
    "description": "Export and Import Models directly to MD",
    "tracker_url": "https://github.com/akitotheanimator/God-Hand-Tools/tree/main",
}

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty
from bpy.types import Panel, Operator
from bpy_extras.io_utils import ImportHelper
import mathutils
import math
from mathutils import Vector
import os
import bmesh
import struct

    
    
class OBJECT_OT_ExportMD(bpy.types.Operator):
    bl_idname = "object.export_action_md"
    bl_label = "Export"
    bl_description = "Export model"

    def execute(self, context):
        preferences = bpy.context.preferences.addons['Blen2MD'].preferences
        selected_obj = context.active_object
        
        
        folder_path = preferences.folder_path
        if not folder_path:
            self.report({'WARNING'}, "No folder selected.")
            return {'CANCELLED'}
        if selected_obj is None or selected_obj.type != 'ARMATURE':
            self.report({'WARNING'}, "Select an armature first!")
            return {'CANCELLED'}
        
        child_meshes = [child for child in selected_obj.children if child.type == 'MESH']
        
        if not child_meshes:
            self.report({'INFO'}, "No child meshes found.")
            return {'CANCELLED'}
        modelRet = '';
        def get_bone_hierarchy_depth(bone):
            """Recursively find the depth of the bone in the hierarchy."""
            depth = 0
            while bone.parent:
                bone = bone.parent
                depth += 1
            return depth
        for bone in selected_obj.pose.bones:
                        bone_name = bone.name
                        bone_position = bone.head
                        v1C = bone.head.x
                        v2C = bone.head.y
                        v3C = bone.head.z
                        v1PC = bone.head.x
                        v2PC = bone.head.y
                        v3PC = bone.head.z
                       
                        if bone.parent != None:
                            v1PC = bone.parent.head.x
                            v2PC = bone.parent.head.y
                            v3PC = bone.parent.head.z
                            v1C = v1PC - v1C
                            v2C = v2PC - v2C
                            v3C = v3PC - v3C
                            v1C *= -1;
                            v2C *= -1;
                            v3C *= -1;
                        current_depth = get_bone_hierarchy_depth(bone)
                        if bone.parent:
                           parent_bone_name = bone.parent.name
                           parent_depth = get_bone_hierarchy_depth(bone.parent)
                        else:
                           parent_bone_name = '0'
                           parent_depth = -1
            
                        if bone.parent != None:
                           print(f"Bone: {bone_name}, Position: {v1C,v2C,v3C}")
                        modelRet += ':' + bone_name.replace(":","$").replace(",",".") + ':' + str(current_depth) + ':' + str(parent_bone_name) + ':' + str(v1C).replace(',','.') + ':' + str(v2C).replace(',','.') + ':' + str(v3C).replace(',','.')
                       
        for obj in child_meshes:
         materials = obj.data.materials
         if materials:
          print(f"Materials assigned to {obj.name}:")
          modelRet += "\nmcs:" + obj.name + ":" + str(selected_obj.location).replace(" ","").replace("<Vector(","").replace(", ",",").replace(")>",":") + str(selected_obj.rotation_euler).replace("<Euler (x=","").replace(", y=",",").replace(", z=",",").split(", order=")[0].replace(")","") + ":" + str(selected_obj.scale).replace(" ","").replace("<Vector(","").replace(", ",",").replace(")>",":")  #material code sequence
          
          for i, material in enumerate(materials):
            try:
               print(str(material.name) + "    " + obj.name)
            except Exception as e:
               self.report({'ERROR'}, "The mesh \"" + obj.name + "\" contains a invalid material.")
               return {'CANCELLED'}
            modelRet += "\n" +material.name + "|"
            faces_with_material = []
            for face in obj.data.polygons:
                if face.material_index == i:
                    faces_with_material.append(face.index)
                    
            if len(faces_with_material) == 0:
                self.report({'ERROR'},  "The material \"" + material.name + "\" is assigned in mesh \"" + obj.name+"\", but does not contain any triangle assigned.\n Consider removing the material from the mesh, or assigning a triangle on it.")
                return {'CANCELLED'}
            if faces_with_material:
                for face_index in faces_with_material:
                    modelRet += str(face_index) + ":"
                modelRet = modelRet[:-1]
                
                
                
                for face_index in faces_with_material:
                    face = obj.data.polygons[face_index]
                    
                    modelRet += "\n" + str(face_index) + "+"
                    
                    
                    for loop_index in face.loop_indices:
                        loop = obj.data.loops[loop_index]
                        vertex_index = loop.vertex_index
                        vertex = obj.data.vertices[vertex_index]
                        position = vertex.co
                        
                        normal = obj.data.vertices[vertex_index].normal
                        
                        
                        uv_layer = obj.data.uv_layers.active.data[loop_index] if obj.data.uv_layers.active else None
                        uv = uv_layer.uv if uv_layer else None
                        

                    
                    
                        vertex_groups = vertex.groups
                        
                        
                        bone_weights = []
                        bone_names = []
                        for group in vertex_groups:
                            try:
                               group_name = obj.vertex_groups[group.group].name
                            
                               weight = group.weight
                               bone_names.append(group_name)
                               bone_weights.append(weight)
                            except IndexError:
                               print(f"Warning: Vertex group index out of range for vertex {vertex.index}.")
                        #continue   
                               
                               
                               
                               
                        bone_weights = sorted(zip(bone_weights, bone_names), reverse=True, key=lambda x: x[0])[:3]
                        #print(f"      Vertex {vertex_index}:")
                        modelRet += str(vertex_index) + ":"
                        #print(f"        Position: {position}")
                        
                        
                        if context.scene.map == True:
                           if position.x > 327.68 or position.x < -327.68:
                            self.report({'ERROR'}, "A Vertice has position x " + str(position) + " which exceeds the cordinate limit (327.68 or -327.68).")
                            return {'CANCELLED'}
                           if position.y > 327.68 or position.y < -327.68:
                            self.report({'ERROR'}, "A Vertice has position y " + str(position) + " which exceeds the cordinate limit (327.68 or -327.68).")
                            return {'CANCELLED'}
                           if position.z > 327.68 or position.z < -327.68:
                            self.report({'ERROR'},  "A Vertice has position z " + str(position) + " which exceeds the cordinate limit (327.68 or -327.68).")
                            return {'CANCELLED'}
                        
                        modelRet += str(position).replace("<Vector (","").replace(", ",",").replace(")>",":");
                        #print(f"        Normal: {normal}")
                        if context.scene.map == False:
                          modelRet += str(normal).replace("<Vector (","").replace(", ",",").replace(")>",":");
                        if uv:
                            #print(f"        UV: {uv}")
                            modelRet += str(uv).replace("<Vector (","").replace(", ",",").replace(")>",",");
                            for poly in obj.data.polygons:
                              for other_loop_index in poly.loop_indices:
                                  other_loop = obj.data.loops[other_loop_index]
                                  if other_loop.vertex_index == vertex_index:
                                      other_uv = obj.data.uv_layers.active.data[other_loop_index].uv
                                      modelRet += str(uv).replace("<Vector (","").replace(", ",",").replace(")>",",");
                            modelRet = modelRet[:-1] + ":"
                                      #print(other_uv)
                        else:
                            #print("        No UV coordinates")
                            modelRet += "FFFFFF:"
                            
                            
                        if context.scene.map == False:
                          if bone_weights:
                            #print("WIGHTS?????")
                            retList = ""
                            #print("        Weights:", end=" ")
                            total_weight = 0
                            countOf = 0;
                            for idx, (weight, name) in enumerate(bone_weights):
                                if idx == len(bone_weights) - 1:
                                    modelRet += name.replace(":","$").replace(",",".") + ",";
                                    retList+= str(weight) + ","
                                    countOf=countOf+1;
                                else:
                                    modelRet += name.replace(":","$").replace(",",".") + ",";
                                    retList+= str(weight) + ","
                                    countOf=countOf+1;
                                if name == "0":
                                   print(str(weight) + "  " + name)
                                total_weight += weight
                                



                            if countOf == 4:
                               modelRet = modelRet[:-1]
                               modelRet += ":"
                            if countOf == 3:
                                modelRet += "FFFFF0:"
                                
                            if countOf == 2:
                                modelRet += "FFFFF0,"
                                modelRet += "FFFFF0:"
                            if countOf == 1:
                                modelRet += "FFFFF0,"
                                modelRet += "FFFFF0,"
                                modelRet += "FFFFF0:"
                            
                            retList = retList[:-1]
                                
                                
                            average_weight = total_weight / len(bone_weights)
                            
                            modelRet += str(average_weight) + "," + retList + ":"
                            #print(f", Average weight: {average_weight:.4f}")
                          else:
                            modelRet += "root,root,root,FFFFF0:0.0,0.0,0.0,0.0:"
                            #print("        No bone weights")
                    modelRet = modelRet[:-1]  # Remove the last character         
            else:
                self.report({'ERROR'}, f"  No faces with {material.name}")
                return {'CANCELLED'}
         else:
          self.report({'ERROR'}, f"No materials assigned to {obj.name}")
          return {'CANCELLED'}
    
                
                
                
                
                
                
                    
                    
        file_path = folder_path + "MDTEMP" + selected_obj.name + ".txt"
        with open(file_path, 'w') as file:
           file.write(modelRet)
         
         
           
        #os.system('start /wait \"\"  \"' + context.scene.exe_path + '\" \"' + file_path_args + '\"')
        #print('start cmd /k \"\"' + context.scene.exe_path + '\" \"' + file_path + '\"\" ' + str(context.scene.output) +' \"' + context.scene.input + '\"')
        os.system('start cmd /k \"\"' + preferences.exe_path + '\" \"' + file_path + '\" ' + str(context.scene.output) +' \"' + context.scene.input + '\" + " \""' + str(context.scene.output) + "\" \"" + str(context.scene.map) + "\"")
        
        self.report({'INFO'}, "Finished!")
        return {'FINISHED'}

    
class OBJECT_OT_RenameSkeleton(bpy.types.Operator):
    bl_idname = "object.rename_skel"
    bl_label = "Rename"
    bl_description = "Renames the skeleton to the god hand indexed format\nSelect an armature, and then, execute this button"

    def execute(self, context):
        
        
        bpy.ops.ed.undo_push()
        selected_obj = context.active_object
        def get_bone_hierarchy_depth(bone):
            """Recursively find the depth of the bone in the hierarchy."""
            depth = 0
            while bone.parent:
                bone = bone.parent
                depth += 1
            return depth
        #for bone in selected_obj.pose.bones:
        for i in range(0, len(selected_obj.pose.bones)):
                        bone_name = selected_obj.pose.bones[i].name
                        bone_position = selected_obj.matrix_world @ selected_obj.pose.bones[i].head
                        
                        current_depth = get_bone_hierarchy_depth(selected_obj.pose.bones[i])
                        if selected_obj.pose.bones[i].parent:
                           parent_bone_name = selected_obj.pose.bones[i].parent.name
                           parent_depth = get_bone_hierarchy_depth(selected_obj.pose.bones[i].parent)
                        else:
                           parent_bone_name = 'nprt0'
                           parent_depth = -1
                        print(bone_name);
                        selected_obj.pose.bones[i].name = str(i);
                        
                        
        selected_obj.pose.bones[0].name = "root";
        
        
        return {'FINISHED'}
    
    
    
    
    
class OBJECT_OT_GetInfo(bpy.types.Operator):
    bl_idname = "object.get_info"
    bl_label = "Info"
    bl_description = "Gets the model info of the reference md"

    def execute(self, context):
        
        context.scene.headerInfo = ""
        context.scene.MInfo = ""
        with open(context.scene.input, "rb") as file:
            
            filemagic = struct.unpack("<I", file.read(4))[0]
            
            
            if filemagic == 7496563:
                #since it only plots the info of the md, we can skip most part of it.
                file.seek(8)
                meshCount = struct.unpack("<I", file.read(4))[0]
                context.scene.headerInfo = "Mesh count: " + str(meshCount)
                file.seek(16)
                for i in range(0, meshCount):
                    
                    file.seek(16 + (i*4));
                    
                    offset = struct.unpack("<I", file.read(4))[0]
                    file.seek(offset + 8)
                    meshName = file.read(8)
                    decodedMesh = meshName.decode("utf-8").strip("\x00")
                    

                    
                    
                    
                    
                    file.seek(offset)
                    negativeOffset = struct.unpack("<i", file.read(4))[0]
                    
                    cOffset = file.tell() + negativeOffset - 4
                    
                    file.seek(cOffset+10)
                    countSubMeshes = struct.unpack("<H", file.read(2))[0]
                    
                    context.scene.MInfo += decodedMesh + "\n"
                    context.scene.headerCount += str(countSubMeshes) + "\n"
                    
                    
                    #print(decodedMesh);
                    print(cOffset)
                
            else:
                self.report({'ERROR'}, f"The reference MD is not a MD file.")
                return {'CANCELLED'}
            
             
             
             
             
        return {'FINISHED'}
    
    
    
    


class Properties(bpy.types.PropertyGroup):
    show_l13: bpy.props.BoolProperty(name="Show Mesh Info", default=True)
    dimensions: bpy.props.IntVectorProperty(
        name="image dimensions",
        description="The dimensions of the output image",
        size=2,
        default=(128, 128)
    )
    colors: bpy.props.IntProperty(
        name="color set",
        description="max colors of the image",
        default=16
    )
    
    
class OBJECT_OT_Retrieve(bpy.types.Operator):
    bl_idname = "object.retrieve"
    bl_label = "Info"
    bl_description = "Gets the images of the materials in the meshes\nSelect an armature, and then, execute this button"

    def execute(self, context):
        scene = bpy.context.scene
        preferences = bpy.context.preferences.addons['Blen2MD'].preferences
        selected_obj = context.active_object
        child_meshes = [child for child in selected_obj.children if child.type == 'MESH']
        processed_images = []
        for obj in child_meshes:
            materials = obj.data.materials
            if materials:
               materials = obj.data.materials
               for mat in materials:
                   if mat and mat.use_nodes:
                       for node in mat.node_tree.nodes:
                           if node.type == 'TEX_IMAGE':
                               image = node.image
                               if image:
                                   if image.filepath not in processed_images:
                                      #self.report({'INFO'}, 'start cmd /k \"\"' + bpy.context.scene.input_IM + '\"\"  \"' + image.filepath + '\ " -resize' + str(scene.collapse.dimensions[0])  + 'x' + str(scene.collapse.dimensions[1]) + ' -colors ' + str(scene.collapse.colors) + ' \"' +  context.scene.input_IM + 'IN.png\"')
                                      os.system('start /wait \"\"  \"' + preferences.input_IM + '\" \"' + image.filepath + '\" -resize ' + str(scene.collapse.dimensions[0])  + 'x' + str(scene.collapse.dimensions[1]) + ' -colors ' + str(scene.collapse.colors) + ' \"' +  image.filepath + 'OUT.png\"')
                                      processed_images.append(image.filepath)
                                   
                                      print(image.filepath)
                                      #os.system('start cmd /k \"\"' + bpy.context.scene.input_IM + '\" \"' + image.filepath + '\" -resize ' + str(scene.collapse.dimensions[0])  + 'x' + str(scene.collapse.dimensions[1]) + ' -colors ' + str(scene.collapse.colors) + ' \"' +  context.scene.input_IM + 'OUT.png\"')
        
        
        return {'FINISHED'}
    
class OBJECT_OT_Unus(bpy.types.Operator):
    bl_idname = "object.unus"
    bl_label = "Utility"
    bl_description = "Removes all groups which the bones doesn't exists\nSelect an armature, and then, execute this button"

    def execute(self, context):
        scene = bpy.context.scene
        
        obj = context.active_object
        bone_names = {bone.name for bone in obj.data.bones}
        
        
        
        child_meshes = [child for child in obj.children if child.type == 'MESH']
        for cm in child_meshes:
            unused_groups = [vg for vg in cm.vertex_groups if vg.name not in bone_names]
            for vg in unused_groups:\
                cm.vertex_groups.remove(vg)
        
        
            
        
        return {'FINISHED'}
    
    
    
class OBJECT_OT_Skeleton(bpy.types.Operator):
    bl_idname = "object.skeleton"
    bl_label = "Utility"
    bl_description = "Loads a skeleton profile + the meshes dummies to the scene.\nSelect something, and then, execute this button"

    def execute(self, context):
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
        armature = bpy.context.object
        
        
        armature.name = os.path.basename(context.scene.input)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        with open(context.scene.input, "rb") as file:
            
            filemagic = struct.unpack("<I", file.read(4))[0]
            
            
            if filemagic == 7496563:
                file.seek(8)
                meshCount = struct.unpack("<I", file.read(4))[0]
                file.seek(16)
                for i in range(0, meshCount):
                    
                    file.seek(16 + (i*4));
                    
                    offset = struct.unpack("<I", file.read(4))[0]
                    file.seek(offset + 8)
                    meshName = file.read(8)
                    decodedMesh = meshName.decode("utf-8").strip("\x00")
                    
                    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
                    empty = bpy.context.object
                    empty.name = decodedMesh
                    empty.parent = armature
                    
                    
                    
                file.seek(16)
                v1 = struct.unpack("<I", file.read(4))[0]
                file.seek(v1)
                v2 = struct.unpack("<i", file.read(4))[0]
                file.seek(v1 + v2 + 8)
                
                #print(file.tell())
                skeletonCount = struct.unpack("<H", file.read(2))[0]
                
                
                
                
                bpy.context.view_layer.objects.active = armature
                bpy.ops.object.mode_set(mode='EDIT')
                armature_data = armature.data
                edit_bones = armature_data.edit_bones
                edit_bones.remove(edit_bones[0])
                
                
                
                
                file.seek(v1 + v2 + 48)
                for i in range(0, skeletonCount):
                    p1 = struct.unpack("<f", file.read(4))[0];
                    p2 = struct.unpack("<f", file.read(4))[0];
                    p3 = struct.unpack("<f", file.read(4))[0];
                    print(struct.unpack("<h", file.read(2))[0])
                    parent = struct.unpack("<h", file.read(2))[0]
                    
                    new_bone = edit_bones.new(str(i))
                    new_bone.head = Vector((p1, p2, p3))
                    new_bone.tail = Vector((p1, p2 + 0.005297, p3))
                    new_bone.head_radius = 0.1;
                    new_bone.tail_radius = 0.05;
                    new_bone.roll = 0;
                    if parent == -1: 
                        new_bone.parent = None
                    else:
                        new_bone.parent = edit_bones[parent]
                        new_bone.head += edit_bones[parent].head
                        new_bone.tail += edit_bones[parent].head
                    
                    
                
            else:
                self.report({'ERROR'}, f"The reference MD is not a MD file.")
                return {'CANCELLED'}
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.object.data.display_type = 'STICK'

        return {'FINISHED'}





class OBJECT_OT_Import(bpy.types.Operator):
    bl_idname = "object.import_action_md"
    bl_label = "Utility"
    bl_description = "Loads the ref model on the scene.\nSelect something, and then, execute this button"

    def execute(self, context):
        
        N1T = bpy.data.meshes.new("LENOTUSE")
        N1T_ = bpy.data.objects.new("LENOTUSE", N1T)
        bpy.context.collection.objects.link(N1T_)
        bpy.context.view_layer.objects.active = N1T_
        
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        
        
        
        
        bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
        armature = bpy.context.object
        bpy.ops.object.mode_set(mode='OBJECT')
 
        bpy.ops.object.select_all(action='DESELECT')
        N1T_.select_set(True)
        bpy.ops.object.delete()
        
        
        bpy.context.view_layer.objects.active = armature
        
        armature.name = os.path.basename(context.scene.input)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        with open(context.scene.input, "rb") as file:
            filemagic = struct.unpack("<I", file.read(4))[0]
            
            
            if filemagic == 7496563:
                file.seek(8)
                meshCount = struct.unpack("<I", file.read(4))[0]
                file.seek(16)
                for i in range(0, meshCount):
                    
                    file.seek(16 + (i*4));
                    
                    offsetl = struct.unpack("<I", file.read(4))[0]
                    
                    
                    file.seek(offsetl + 8)
                    meshName = file.read(8)
                    decodedMesh = meshName.decode("utf-8").strip("\x00")
                    PoseScaX = struct.unpack("<f", file.read(4))[0]
                    PoseScaY = struct.unpack("<f", file.read(4))[0]
                    PoseScaZ = struct.unpack("<f", file.read(4))[0]
                    PoseRotX = struct.unpack("<f", file.read(4))[0]
                    PoseRotY = struct.unpack("<f", file.read(4))[0]
                    PoseRotZ = struct.unpack("<f", file.read(4))[0]
                    PoseLocX = struct.unpack("<f", file.read(4))[0]
                    PoseLocY = struct.unpack("<f", file.read(4))[0]
                    PoseLocZ = struct.unpack("<f", file.read(4))[0]
                    file.seek(offsetl)
                    
                    
                    bl = struct.unpack("<i", file.read(4))[0]
                    v1 = offsetl + bl

                    
                    file.seek(v1+10)
                    subMeshCount = struct.unpack("<H", file.read(2))[0]
                    
                    
                    
                    
                    file.seek(v1 + 28)
                    MeshType = struct.unpack("<f", file.read(4))[0]
                    
                    
                    
                    
                    
                    file.seek(v1 + 32)
                    checkPoint = file.tell();
                    
                    MeshData = []
                    for i in range(0, subMeshCount):
                        file.seek(checkPoint + (i*4));
                        
                        v2 = struct.unpack("<I", file.read(4))[0]
                        offset = v1 + v2
                        
                        file.seek(offset)
                        
                        vertsOffset = offset + struct.unpack("<I", file.read(4))[0]
                        normalOffset = offset + struct.unpack("<I", file.read(4))[0]
                        uvOffset = offset + struct.unpack("<I", file.read(4))[0]
                        colorOffset = offset + struct.unpack("<I", file.read(4))[0]
                        weightsOffset = offset + struct.unpack("<I", file.read(4))[0]
                        
                        VCount = struct.unpack("<H", file.read(2))[0]
                        materialIndex = struct.unpack("<H", file.read(2))[0]
                        
                        
                        
                        vA1 = 0
                        vA2 = 0
                        vA3 = 0
                        verts = []
                        indices = []
                        file.seek(vertsOffset)
                        for i in range(0, VCount):
                            if MeshType == 1:
                               x = struct.unpack("<f", file.read(4))[0]
                               y = struct.unpack("<f", file.read(4))[0]
                               z = struct.unpack("<f", file.read(4))[0]
                               code = struct.unpack("<I", file.read(4))[0]
                            else:
                                
                                
                                    
                                    
                                
                                x = (struct.unpack("<h", file.read(2))[0])
                                y = (struct.unpack("<h", file.read(2))[0])
                                z = (struct.unpack("<h", file.read(2))[0])
                                
                                code = struct.unpack("<H", file.read(2))[0]
                                vA1 = x* 0.01
                                vA2 = y* 0.01
                                vA3 = z* 0.01
                                
                                x = x * 0.01
                                y = y * 0.01
                                z = z * 0.01
                                
                                #print(str(x) + "    " + str(y) + "      OHYEAH")
                            verts.append((x,y,z));
                            indices.append(code);


                        
                        
                        normals = []
                        file.seek(normalOffset)
                        
                        def map_value(value, old_min, old_max, new_min, new_max):
                            return (value - old_min) / (old_max - old_min) * (new_max - new_min) + new_min
                        def map_signed_byte(value):
                            return map_value(value, -128, 127, -1, 1)

                        for i in range(0, VCount):
                            if MeshType == 1:
                               x = (map_signed_byte(struct.unpack("<b", file.read(1))[0]) * -1)
                               y = (map_signed_byte(struct.unpack("<b", file.read(1))[0]) * -1)
                               z = (map_signed_byte(struct.unpack("<b", file.read(1))[0]) * -1)
                               w = (struct.unpack("<b", file.read(1))[0])
                            
                               le = math.sqrt(x*x + y*y + z*z)

                               x = x / le
                               y = y / le
                               z = z / le
                            else:
                                 x = 0
                                 y = 0
                                 z = 0
                                 w = 0

                            normals.append((x* -1,y* -1,z* -1))
                            
                        uv = []
                        file.seek(uvOffset)
                        for i in range(0, VCount):
                            x = (((struct.unpack("<h", file.read(2))[0]))  / 4096.0)
                            y = (((struct.unpack("<h", file.read(2))[0]) * -1.0)  / 4096.0)
                            uv.append((x,y))
                            
                        color = []
                        file.seek(colorOffset)
                        for i in range(0, VCount):
                            r = struct.unpack("<B", file.read(1))[0] / 128.0
                            g = struct.unpack("<B", file.read(1))[0] / 128.0
                            b = struct.unpack("<B", file.read(1))[0] / 128.0
                            a = struct.unpack("<B", file.read(1))[0] / 128.0
                            color.append((r,g,b,a))
                            
                        map = []
                        file.seek(weightsOffset)
                        for i in range(0, VCount):
                            
                            
                            nullB = struct.unpack("<B", file.read(1))[0]
                            B1 = str((int(struct.unpack("<B", file.read(1))[0] / 4)) + 1)
                            B2 = str((int(struct.unpack("<B", file.read(1))[0] / 4)) + 1)
                            B3 = str((int(struct.unpack("<B", file.read(1))[0] / 4)) + 1)
                            
                            if B1 == "0":
                                B1 = B1.replace("0","root")
                            if B2 == "0":
                                B2 = B2.replace("0","root")
                            if B3 == "0":
                                B3 = B3.replace("0","root")     
                                
                                
                                
                            
                            W1 = struct.unpack("<B", file.read(1))[0] / 100.0
                            W2 = struct.unpack("<B", file.read(1))[0] / 100.0
                            W3 = struct.unpack("<B", file.read(1))[0] / 100.0
                            nullW = struct.unpack("<B", file.read(1))[0]
                            
                            map.append((B1,B2,B3,W1,W2,W3))
                            
                        MeshData.append((verts,indices,normals,uv,color,map,materialIndex));
                    
                    mesh = bpy.data.meshes.new(decodedMesh)
                    mesh_object = bpy.data.objects.new(decodedMesh, mesh)
                    
                    
                    
                        
                    armature.rotation_euler[0] = PoseRotX
                    armature.rotation_euler[1] = PoseRotY
                    armature.rotation_euler[2] = PoseRotZ
                    armature.location.x = PoseLocX
                    armature.location.y = PoseLocY
                    armature.location.z = PoseLocZ
                    
                        
                    armature.scale.x = PoseScaX
                    armature.scale.y = PoseScaY
                    armature.scale.z = PoseScaZ
                    
                    bpy.context.collection.objects.link(mesh_object)
                    mesh_object.parent = armature
                    armature_modifier = mesh_object.modifiers.new(name="Armature", type='ARMATURE')
                    armature_modifier.object = armature
                    
                    bm = bmesh.new()
                    normalAbs = []
                    uvAbs = []
                    colorAbs = []
                    weightsAbs = []
                    for e in range(0, len(MeshData)):
                        

                        matName = str(MeshData[e][6]).split(".")[0]
                        print(matName)
                        mat = bpy.data.materials.get(matName)
                        
                        if not mat:
                             mat = bpy.data.materials.new(name=matName)
                        mesh_object.data.materials.append(mat)
                          
                        
                        material_index = mesh_object.data.materials.find(mat.name)

                        for o in range(0, len(MeshData[e][0])):
                            bm.verts.new(MeshData[e][0][o])
                            
                            bm.verts.ensure_lookup_table()
                            
                            if MeshData[e][1][o] == 0:
                                f = bm.faces.new([
                                bm.verts[len(bm.verts)-3],
                                bm.verts[len(bm.verts)-2],
                                bm.verts[len(bm.verts)-1]
                                ])
                                
                                f.material_index = material_index
                                
                            if MeshData[e][1][o] == 1:
                                f = bm.faces.new([
                                bm.verts[len(bm.verts)-2],
                                bm.verts[len(bm.verts)-3],
                                bm.verts[len(bm.verts)-1]
                                ])
                                
                                f.material_index = material_index
                        
                        
                        for o in range(0, len(MeshData[e][2])):
                            normalAbs.append(MeshData[e][2][o])
                            
                            
                        for o in range(0, len(MeshData[e][3])):
                            uvAbs.append((MeshData[e][3][o],MeshData[e][0][o]))
                            
                            
                        for o in range(0, len(MeshData[e][4])):
                            colorAbs.append(MeshData[e][4][o])
                            
                            
                        for o in range(0, len(MeshData[e][5])):
                            if MeshData[e][5][o][0] not in mesh_object.vertex_groups and MeshData[e][5][o][0] != "root":
                                mesh_object.vertex_groups.new(name=MeshData[e][5][o][0])
                            
                            if MeshData[e][5][o][1] not in mesh_object.vertex_groups and MeshData[e][5][o][1] != "root":
                                mesh_object.vertex_groups.new(name=MeshData[e][5][o][1])

                            
                            if MeshData[e][5][o][2] not in mesh_object.vertex_groups and MeshData[e][5][o][2] != "root":
                                mesh_object.vertex_groups.new(name=MeshData[e][5][o][2])
                                
                            weightsAbs.append(MeshData[e][5][o])
                    bm.to_mesh(mesh)
                    
                    
                    bm.free()
                    mesh.update()
                    mesh.use_auto_smooth = True
                    
                    mesh.normals_split_custom_set_from_vertices(normalAbs)
                    uv_layer = mesh.uv_layers.new(name="UVMap")
                    
                    
                    
                    color_layer = mesh.color_attributes.new(name="COLOR", type="FLOAT_COLOR", domain="POINT")
                    
                    iC = 0
                    for c in colorAbs:
                          color_layer.data[iC].color = (c[0], c[1], c[2], c[3])
                          iC = iC + 1

                        
                        

                    for o in range(0, len(weightsAbs)):
                            if weightsAbs[o][0] != "root":
                               vertex_group =  mesh_object.vertex_groups[weightsAbs[o][0]]
                               vertex_group.add([o], weightsAbs[o][3], 'ADD')
                            
                            if weightsAbs[o][1] != "root":
                                
                                
                               vertex_group =  mesh_object.vertex_groups[weightsAbs[o][1]]
                               vertex_group.add([o], weightsAbs[o][4], 'ADD')
                            if weightsAbs[o][2] != "root":
                                
                                
                               vertex_group =  mesh_object.vertex_groups[weightsAbs[o][2]]
                               vertex_group.add([o], weightsAbs[o][5], 'ADD')
                               

                    mesh.update()
                    for face in mesh.polygons:
                        for loop_idx, loop in enumerate(face.loop_indices):
                            uv = uv_layer.data[loop].uv
                            
                            vertex_idx = mesh.loops[loop].vertex_index
                            vertex_coord = mesh.vertices[vertex_idx].co
                            uv[:] = uvAbs[vertex_idx][0]
                file.seek(16)
                v1 = struct.unpack("<I", file.read(4))[0]
                file.seek(v1)
                v2 = struct.unpack("<i", file.read(4))[0]
                file.seek(v1 + v2 + 8)
                skeletonCount = struct.unpack("<H", file.read(2))[0]
                file.seek(v1 + v2 + 4)
                skeletonOffset = struct.unpack("<I", file.read(4))[0]
                
                
                
                bpy.context.view_layer.objects.active = armature

                bpy.ops.object.mode_set(mode='EDIT')
                armature_data = armature.data
                edit_bones = armature_data.edit_bones
                
                
                edit_bones[0].name = ("root")
                edit_bones[0].head = Vector((0.0,0.0,0.0))
                
                edit_bones[0].tail = Vector((0.0, 0.005297, 0.0))
                edit_bones[0].head_radius = 0.1;
                edit_bones[0].tail_radius = 0.05;
                edit_bones[0].roll = 0;
                    
                
                file.seek(v1 + v2 + skeletonOffset)
                for i in range(0, skeletonCount):
                    p1 = struct.unpack("<f", file.read(4))[0];
                    p2 = struct.unpack("<f", file.read(4))[0];
                    p3 = struct.unpack("<f", file.read(4))[0];
                    ls = struct.unpack("<h", file.read(2))[0]
                    parent = struct.unpack("<h", file.read(2))[0] + 1
                    
                    new_bone = edit_bones.new(str(i+1))
                    new_bone.head = Vector((p1, p2, p3))
                    new_bone.tail = Vector((p1, p2 + 0.005297, p3))
                    new_bone.head_radius = 0.1;
                    new_bone.tail_radius = 0.05;
                    new_bone.use_connect = False
                    
                    new_bone.parent = edit_bones[parent]
                    new_bone.head += edit_bones[parent].head
                    if new_bone.name != "root" and edit_bones[parent].name != "root":
                       new_bone.tail += edit_bones[parent].head
                    new_bone.roll = 0;      

                              
                edit_bones = armature_data.edit_bones  
               
                for i in edit_bones:    
                    child_heads = [edit_bones[child.name].head for child in i.children]
                    if len(child_heads) == 0:
                       if i.parent != None:
                        t1 = i.parent.head
                        t2 = i.parent.tail
                        t2 = t2 - t1
                        t1 = t1 - t1
                              
                        i.tail = i.tail + t2
                        i.head = i.head + t1

                        
                        i.head = i.head
                        i.tail = i.tail
                
                        
            else:
                self.report({'ERROR'}, f"The MD is not a MD file.")
                return {'CANCELLED'}
            


        bpy.context.object.show_in_front = True
        bpy.context.object.data.display_type = 'STICK'
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
    
    
class VIEW3D_PT_MDPanel(Panel):
    bl_label = "Blen2MD"
    bl_idname = "VIEW3D_PT_MDP"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MD'
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        preferences = bpy.context.preferences.addons['Blen2MD'].preferences
        
        
        
        l1 = layout.box()
        l1.label(text="File Settings", icon='IMPORT')
        boxFTS = l1.box()
        
        boxFS = boxFTS.box()
        boxFS.label(text="Blen2MD Addon Preferences:");
        boxFS.separator()
        
        
        if preferences:
           if preferences.folder_path:
              boxT1 = boxFS.row()
              split = boxT1.split(factor=0.23)
              split.label(text="Export Folder: ")
            
              VP = split.box()
              VP.label(text=str(preferences.folder_path),icon='EXPORT')

            
            
        
        
        
        
        if preferences:
           if preferences.exe_path:
              boxT1 = boxFS.row()
              split = boxT1.split(factor=0.23)
              split.label(text="Blen2MD: ")
            
              VP = split.box()
              VP.label(text=str(preferences.exe_path),icon='FILE_SCRIPT')
        
        
        
        if preferences:
           if preferences.input_IM:
              boxT1 = boxFS.row()
              split = boxT1.split(factor=0.23)
              split.label(text="ImageMagick: ")
            
              VP = split.box()
              VP.label(text=str(preferences.input_IM),icon='FILE_SCRIPT')
               
              
        boxFTS.separator()
        
        boxFS = boxFTS.box()
        boxFS.label(text="Blen2MD Project Preferences:");
        boxFS.separator()
        boxFS.prop(scene, "output", text="See program's console?", icon='HIDE_OFF');
        boxFS.prop(scene, "map", text="Map Model", icon='PACKAGE');
        boxFS.prop(scene, "input", text="Reference MD", icon='VIEWZOOM')

        #if preferences:
           #if preferences.exe_path:
              #boxFTS.prop(scene, "output", text="See the program output?", icon='HELP')



        l1 = layout.box()
        l1.label(text="MD Utility", icon='MODIFIER');
        
        boxIF = l1.box()

        if context.scene.input:
              boxIF.operator("object.import_action_md", text="Import MD from Ref", icon='MATCUBE')


        boxIF.operator("object.rename_skel", text="Rename skeleton using Index", icon='BONE_DATA')
        if context.scene.input:
              boxIF.operator("object.get_info", text="Load ref model info", icon='TEXT')
        boxIF.operator("object.unus", text="Delete all unusued vert groups", icon='GROUP')
        #if context.scene.input:
              #boxIF.operator("object.skeleton", text="Load skeleton from reference", icon='RNA')
              
              
        boxIF.operator("object.amo", text="Apply deform modifiers", icon='MESH_DATA')      
            
              
              
        boxIF.separator()  
        boxIF2 = boxIF.box()
        bo = boxIF2.box()
        
        bo.label(text="Match Position Operation");
        bo.operator("object.sarm", text="Match Armature poses", icon='MOD_ARMATURE')
        if context.scene.SK == "":
           bo.label(text="No Armature to match.");
        else:
            spl = context.scene.SK.split("\n")
            for bone in spl:
                bo.label(text=bone);
        bo.operator("object.sarmc", text="Clear match operation", icon='MOD_ARMATURE')
        
        
        boxIF2.label(text="");
        bo = boxIF2.box()
        bo.label(text="Match Name Operation");
        bo.operator("object.msarm", text="Match Armature bones", icon='OUTLINER_OB_ARMATURE')
        if context.scene.SKN == "":
           bo.label(text="No Armature bones to match.");
        else:
            spl = context.scene.SKN.split("\n")
            for bone in spl:
                bo.label(text=bone);
        bo.operator("object.msarmc", text="Clear match bone operation", icon='OUTLINER_OB_ARMATURE')
        
        
        
        
        
        
        
       # l1.separator()
        l1 = layout.box()
        l1.label(text="MD Info", icon='INFO');
        
        
        b1 = l1.box()
        b1.label(text=context.scene.headerInfo);
        
        
        splits1 = context.scene.MInfo.split("\n")
        splits2 = context.scene.headerCount.split("\n")
        
        
        props = context.scene.collapse
        #l13 = boxIF.box()
        b1.prop(props, "show_l13", icon="TRIA_DOWN" if props.show_l13 else "TRIA_RIGHT", emboss=False)
        
        if props.show_l13:
          for i in range(len(splits1)-1):
            #boxIF.label(text=line, icon='INFO');
             b01 = b1.row()
             split = b01.split(factor=0.8)
             
             l14 = split.box()
             l14.label(text="Mesh Name:     " +splits1[i]);
             l14.label(text="Submeshes Count:     " +splits2[i]);


        #l1.separator()
        if preferences:
           if preferences.input_IM:
              l1 = layout.box()
              l1.label(text="Texture Utility", icon='MODIFIER');
              b1 = l1.box()
              b1.operator("object.retrieve", text="Retrieve textures and limit colors channels", icon='TEXTURE_DATA')
              b1.prop(props, "dimensions", text="Texture dimensions")
              b1.prop(props, "colors", text="Texture Max Colors")
        
        
        
        
        l1 = layout.box()
        l1.label(text="Vertex Utility", icon='SURFACE_NCURVE');
        b1 = l1.box()
        b1.operator("object.merge", text="Merge Vert Groups", icon='WPAINT_HLT')
        b2 = b1.box()
        b2.label(text="Verts to merge:");
        if context.scene.VGroup == "":
           b2.label(text="No Vert Group queued to merge.");
        else:
            spl = context.scene.VGroup.split("\n")
            for bone in spl:
                b2.label(text=bone);
        
        b1.operator("object.resetmerge", text="Reset merge", icon='WPAINT_HLT')
        b1.separator()
        b1.operator("object.limitverts", text="Limit verts weights to 3 bones", icon='GROUP_BONE')
        
        
        
        l1 = layout.box()
        l1.label(text="Tips", icon='INFO');
        boxIF = l1.box()
        boxIF.prop(scene, "show_warning", text="", icon='ERROR')

        
        
        l1 = layout.box()
        l1.label(text="MD Tools", icon='EXPORT')
        boxEP = l1.box()
        
        if context.scene.input:
              boxEP.operator("object.export_action_md", text="Export Model to MD", icon='PLAY')
        
        
class OBJECT_OT_Merge(bpy.types.Operator):
    bl_idname = "object.merge"
    bl_label = "Utility"
    bl_description = "Creates a vert group merging operation"
    def execute(self, context):
        bpy.ops.ed.undo_push()
        obj = bpy.context.object
        if obj and obj.type == 'ARMATURE' and obj.mode == 'POSE':
            
            if context.scene.VGroup == "":
               selected_bones = bpy.context.selected_pose_bones
               if selected_bones:
                  active_bone = selected_bones
                  
                  for bone in selected_bones:
                      context.scene.VGroup = context.scene.VGroup + bone.name + "\n"
                  context.scene.VGroup = context.scene.VGroup[:-1]
            else:
               selected_bones = bpy.context.selected_pose_bones
               if selected_bones:
                  active_bone = selected_bones[0]
                  
                  spl = context.scene.VGroup.split("\n")
                  for vg in spl:
                    if active_bone.name != vg:
                     child_meshes = [child for child in obj.children if child.type == 'MESH']
                     
                     
                     for objc in child_meshes:
                         group_a = objc.vertex_groups.get(vg)
                         group_b = objc.vertex_groups.get(active_bone.name)
                     
                         if group_a:
                             group_data = {}
                             for vertex in objc.data.vertices:
                                 for group_element in vertex.groups:
                                     if group_element.group == group_a.index:
                                        group_data[vertex.index] = group_element.weight
                             
                             print(f"Vertex Group: {group_a.name}")
                             #for vert_index, weight in group_data.items():
                                   #print(f"  Vertex {vert_index}: Weight {weight}")
                             if group_b:
                                 for vert_index, weight in group_data.items():
                                     group_b.add([vert_index], weight, type='ADD')
                                 objc.vertex_groups.remove(group_a)
                             else:
                                 vertex_group = objc.vertex_groups.new(name=str(active_bone.name))
                                 
                                 for vert_index, weight in group_data.items():
                                     vertex_group.add([vert_index], weight, type='REPLACE')
                                 objc.vertex_groups.remove(group_a)
                             
                         #if group_b:
                             #msh.append(objc)
                             
                             
                             
                             
                         #if not group_a:
                             #self.report({'ERROR'},f"Vertex group '{context.scene.VGroup}' does not exist.")
                             #return
                         #if not group_b:
                               #self.report({'ERROR'},f"Vertex group '{active_bone.name}' does not exist.")
                               #return
                         #e
                     
                     
                     
                     bpy.context.view_layer.objects.active = obj
                     bpy.ops.object.mode_set(mode='EDIT')
                     edit_bones = obj.data.edit_bones
                     
                     spl = context.scene.VGroup.split("\n")
                     for vg in spl:
                        bone_to_delete = edit_bones.get(vg)
                        if bone_to_delete:
                           edit_bones.remove(bone_to_delete)
                         
                     
                     bpy.ops.object.mode_set(mode='POSE')
                      
                     context.scene.VGroup = ""
                     bpy.ops.ed.undo_push()
                    else:
                      self.report({'ERROR'}, f"You're trying to merge the same bone.")
                      return {'CANCELLED'}
                  
                          
        
        return {'FINISHED'}
class OBJECT_OT_SetArmature(bpy.types.Operator):
    bl_idname = "object.sarm"
    bl_label = "Utility"
    bl_description = "Set all the bones of armature 1 to armature 2 (if the bone name mathes)"
    def execute(self, context):
        bpy.ops.ed.undo_push()
        if context.scene.SK == "":
            context.scene.SK = bpy.context.selected_objects[0].name
            
        else:
          selected_objects = bpy.context.selected_objects[0]
          if selected_objects:
            
            print("Selected objects:")
            arm1 = selected_objects
            arm2 = bpy.data.objects.get(context.scene.SK)
            
            bpy.ops.object.select_all(action='DESELECT')

            bpy.context.view_layer.objects.active = arm2
            #bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.object.mode_set(mode='POSE')
            
            
            constraints = []
            for bone_a in arm1.pose.bones:
                bone_b = arm2.pose.bones.get(bone_a.name)
                print(str(bone_a.name))
                if bone_b:
                    print("WTF")
                    #constraint = bone_b.constraints.new(type='COPY_LOCATION')
                    #constraint.name = bone_b.name + "CONSTRAINTCOP"
                    
                    #constraint.target = arm1
                    #constraint.subtarget = bone_a.name
                    #bpy.ops.pose.select_all(action='SELECT')
                    #bpy.ops.constraint.apply(constraint=constraint.name, owner = 'BONE', report=True)
                    
                    
                    
                    #bone_a_global_location = (arm1.matrix_world @ bone_a.matrix).translation
                    #bone_b.matrix.translation = arm2.matrix_world.inverted() @ bone_a_global_location
                    
                    #Positions.append((bone_a_global_location,bone_b,arm2.matrix_world.inverted()))
                    #for bns in Positions:
                        #bns[1].matrix.translation = bns[2] @ bns[0]
                        
                        
                        
                        
                    constraint = bone_b.constraints.new(type='COPY_LOCATION')
                    constraint.target = arm1
                    constraint.subtarget = bone_a.name
                    
                    
                    constraints.append((bone_b,constraint,arm2))
                    
                    #bone_b.head = bone_a.head
                    #bone_b.tail = bone_a.head
                    #bone_b.tail.y = bone_b.tail.y + 0.005297
                
                
            context.scene.SK = ""
            #bpy.ops.object.mode_set(mode='OBJECT')
            #bpy.ops.object.select_all(action='DESELECT')
            #for bone_a in constraints:
                #bpy.ops.constraint.apply(constraint=bone_a.name, owner = 'BONE', report=True)

                
            bpy.ops.pose.armature_apply(selected=False)

            for bones in constraints:
                #global_matrix = bones[2].matrix_world @ bones[0].matrix
                #global_location = global_matrix.translation


                #global_location = bones[2].matrix_world * bones[0].matrix * bones[0].location
                matrix_final = bones[2].matrix_world @ bones[0].matrix
                
                
                
                #bones[0].constraints.remove(bones[1])
                #bpy.ops.constraint.apply(constraint=bones[1].name, owner='BONE')
                bones[0].constraints.remove(bones[1])
                #bpy.ops.object.constraint_apply(constraint=constraint.name)
                #bones[0].location  = matrix_final.to_translation()
                
                #bpy.ops.constraint.delete(constraint="Copy Location", owner='BONE')

                
                #bones[0].location = global_location
                
        return {'FINISHED'}
class OBJECT_OT_ClearArmature(bpy.types.Operator):
    bl_idname = "object.sarmc"
    bl_label = "Utility"
    bl_description = "Clear armature match"
    def execute(self, context):
        context.scene.SK = ""
        return {'FINISHED'}
    
    
class OBJECT_OT_ApllyMo(bpy.types.Operator):
    bl_idname = "object.amo"
    bl_label = "Utility"
    bl_description = "Applies all of the armature modifiers on all meshes of a armature"
    def execute(self, context):
        selected_object = bpy.context.selected_objects[0]
        child_meshes = [child for child in selected_object.children if child.type == 'MESH']
        for obj in child_meshes:
            deform_modifiers = [mod for mod in obj.modifiers if mod.type == 'ARMATURE']

            if deform_modifiers:
                for mod in deform_modifiers:
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                    
                    
        return {'FINISHED'}
        
        
class Blen2MDPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

   
    exe_path: StringProperty(
        name="Blen2MD",
        description="Path to the Blen2MD executable",
        default="C:/Users/",
        subtype='FILE_PATH'
    )
    
    folder_path: StringProperty(
        name="Export Folder Path",
        description="Path to selected folder",
        default="C:/Users/",
        subtype='DIR_PATH'
    )
    input_IM: StringProperty(
        name="ImageMagick",
        description="Path to your copy of ImageMagick",
        default="C:/Users/",
        subtype='FILE_PATH'
    )
    
    

    def draw(self, context):
        layout = self.layout

        layout.label(text="Blen2MD Setup")
        layout.prop(self, "exe_path")
        layout.prop(self, "folder_path")
        layout.prop(self, "input_IM")
        
        
        
        
    
class OBJECT_OT_ResetMerge(bpy.types.Operator):
    bl_idname = "object.resetmerge"
    bl_label = "Utility"
    bl_description = "Resets the group you want to merge"
    def execute(self, context):
        context.scene.VGroup = ""
        return {'FINISHED'}






class OBJECT_OT_SetArmatureToName(bpy.types.Operator):
    bl_idname = "object.msarm"
    bl_label = "Utility"
    bl_description = "Rename all bones of armature 1 to armature 2 if the distance is close enough"
    def execute(self, context):
        bpy.ops.ed.undo_push()
        if context.scene.SKN == "":
            context.scene.SKN = bpy.context.selected_objects[0].name
            
        else:
          selected_objects = bpy.context.selected_objects[0]
          if selected_objects:
            
            print("Selected objects:")
            arm1 = bpy.data.objects.get(context.scene.SKN)
            arm2 = selected_objects
            
            threshold_distance = 0.1
            
            bones1 = arm1.pose.bones
            bones2 = arm2.pose.bones
            for bone1 in bones1:
                bone1_head_world = arm1.matrix_world @ bone1.head
                for bone2 in bones2:
                    bone2_head_world = arm2.matrix_world @ bone2.head
                    distance = (bone1_head_world - bone2_head_world).length
                    if distance <= threshold_distance:
                        bone1.name = bone2.name
            context.scene.SKN = ""
                
                
        return {'FINISHED'}
class OBJECT_OT_ClearArmatureName(bpy.types.Operator):
    bl_idname = "object.msarmc"
    bl_label = "Utility"
    bl_description = "Clear armature names match operation"
    def execute(self, context):
        context.scene.SKN = ""
        return {'FINISHED'}
class OBJECT_OT_Limit(bpy.types.Operator):
    bl_idname = "object.limitverts"
    bl_label = "Utility"
    bl_description = "Limits all vert groups of a selected mesh to only allow 3 bones per vert"
    def execute(self, context):
        bpy.ops.object.vertex_group_limit_total(limit=3)
        return {'FINISHED'}
    
    
def register():
    bpy.utils.register_class(OBJECT_OT_ExportMD)
    bpy.utils.register_class(VIEW3D_PT_MDPanel)
    bpy.utils.register_class(OBJECT_OT_RenameSkeleton)
    bpy.utils.register_class(OBJECT_OT_GetInfo)
    bpy.utils.register_class(Properties)
    bpy.utils.register_class(OBJECT_OT_Retrieve)
    bpy.utils.register_class(OBJECT_OT_Unus)
    bpy.utils.register_class(OBJECT_OT_Skeleton)
    bpy.utils.register_class(OBJECT_OT_Import)
    bpy.utils.register_class(OBJECT_OT_Merge)
    bpy.utils.register_class(OBJECT_OT_ResetMerge)
    bpy.utils.register_class(Blen2MDPreferences)
    bpy.utils.register_class(OBJECT_OT_SetArmature)
    bpy.utils.register_class(OBJECT_OT_ClearArmature)
    bpy.utils.register_class(OBJECT_OT_ApllyMo)
    bpy.utils.register_class(OBJECT_OT_Limit)
    
    bpy.utils.register_class(OBJECT_OT_SetArmatureToName)
    bpy.utils.register_class(OBJECT_OT_ClearArmatureName)
    
    bpy.types.Scene.folder_path = StringProperty(
        name="Folder Path",
        description="Path to selected folder",
        default="C:/Users/",
        subtype='DIR_PATH'
    )
    
    
    
    
    bpy.types.Scene.VGroup = StringProperty(
        name="",
        description="",
        default=""
    )
    
    bpy.types.Scene.SK = StringProperty(
        name="",
        description="",
        default=""
    )
    bpy.types.Scene.SKN = StringProperty(
        name="",
        description="",
        default=""
    )
    
    
    bpy.types.Scene.input = StringProperty(
        name="",
        description="Path to the Md you're using as reference of modding",
        default="C:/Users/",
        subtype='FILE_PATH'
    )
    
    
    
    bpy.types.Scene.show_warning = StringProperty(
        name="Modelling Rules:",
        description="Never:\nExport the model with a QUAD face, otherwise the model will break in-game.\nExport the model without having all your meshes UV Maps done and ready to go. \nTry to save a model without making sure all of the meshes have only 1 material in them\nGive names to the materials. the material names should only be indexed materials. (use the model tm3 as ref)",
        default="Hover me!"
    )
    bpy.types.Scene.output = BoolProperty(
        name="See Output",
        description="Check this if you want to see the program output once you export the model, in case the file isn't working, etc..",
        default=False
    )
    bpy.types.Scene.map = BoolProperty(
        name="Is Map",
        description="Check this if the model you want to export is actually a map model",
        default=False
    )
    
    bpy.types.Scene.headerInfo = bpy.props.StringProperty(
        name="",
        default=""
    )
    bpy.types.Scene.MInfo = bpy.props.StringProperty(
        name="",
        default=""
    )
    bpy.types.Scene.headerCount = bpy.props.StringProperty(
        name="",
        default=""
    )

    bpy.types.Scene.collapse = bpy.props.PointerProperty(type=Properties)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_ExportMD)
    bpy.utils.unregister_class(VIEW3D_PT_MDPanel)
    bpy.utils.unregister_class(OBJECT_OT_RenameSkeleton)
    bpy.utils.unregister_class(OBJECT_OT_GetInfo)
    bpy.utils.unregister_class(Properties)
    bpy.utils.unregister_class(OBJECT_OT_Retrieve)
    bpy.utils.unregister_class(OBJECT_OT_Unus)
    bpy.utils.unregister_class(OBJECT_OT_Skeleton)
    bpy.utils.unregister_class(OBJECT_OT_Import)
    bpy.utils.unregister_class(OBJECT_OT_Merge)
    bpy.utils.unregister_class(OBJECT_OT_ResetMerge)
    bpy.utils.unregister_class(Blen2MDPreferences)
    bpy.utils.unregister_class(OBJECT_OT_SetArmature)
    bpy.utils.unregister_class(OBJECT_OT_ClearArmature)
    bpy.utils.unregister_class( OBJECT_OT_ApllyMo)
    bpy.utils.unregister_class(OBJECT_OT_SetArmatureToName)
    bpy.utils.unregister_class(OBJECT_OT_ClearArmatureName)
    bpy.utils.unregister_class(OBJECT_OT_Limit)
    del bpy.types.Scene.show_warning
    del bpy.types.Scene.output
    del bpy.types.Scene.input
    del bpy.types.Scene.headerInfo
    del bpy.types.Scene.headerCount
    del bpy.types.Scene.collapse
    del bpy.types.Scene.VGroup
    del bpy.types.Scene.SK
if __name__ == "__main__":
    register()
