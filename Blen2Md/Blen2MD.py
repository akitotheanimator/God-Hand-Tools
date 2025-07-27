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
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty,EnumProperty,IntProperty
from bpy.types import Panel, Operator
from bpy_extras.io_utils import ImportHelper,ExportHelper
import mathutils
import math
from mathutils import Vector
import os
import bmesh
import struct
import subprocess

def getConnectsMD(faces_mat):
	ret = []
	
	cur = []
	
	hist = []
	for face in range(0,len(faces_mat)): 
		should_separate = False
		def getArray(GET_FACE):
			return [v.index for v in GET_FACE.verts]
		
		
		cfac = faces_mat[face]
		
		hist.append(cfac)
		v3 = getArray(cfac)
		v2 = getArray(cfac)
		if len(hist) > 3:
			history = []
			v3 = getArray(hist[len(hist)-1])
			v2 = getArray(hist[len(hist)-2])
			v1 = getArray(hist[len(hist)-3])
			v0 = getArray(hist[len(hist)-4])
			history.extend(v3)
			history.extend(v2)
			history.extend(v1)
			history.extend(v0)
			for idx in v3:
				if history.count(idx) > 3:
					should_separate = True
					break
		v3.sort()
		
		
		


		fc0 = getArray(cfac)
		if face == 0:
			fc1 = getArray(faces_mat[face+1])
		else:
			fc1 = getArray(faces_mat[face-1])
			
			
		common = list(set(fc0) & set(fc1))
		unique = list(set(fc0) - set(fc1))
		common.sort()
		unique.sort()

		if should_separate:
			ret.append(cur)
			cur = [v3]
			hist = [cfac]
			#print("SEP_BY_unmatcheable  	  ", v3, "   ", cfac.index)
		else:
			
			if len(common) > 1 and len(common) != 3:
				#print(v3, "   ", cfac.index)
				if face == 0:
					cur.append(v3)
				else:
					cur.append(v3)
			else:
				ret.append(cur)
				cur = [v3]
				hist = [cfac]
				#print("SEP_BY_not_similar      ", v3, "   ", cfac.index)
	ret.append(cur)
	return ret


class OBJECT_OT_ExportMD(Operator, ExportHelper):
	bl_idname = "object.export_action_md"
	bl_label = "Export"
	bl_description = "Exports the whole model, as a MD with skeleton, meshes, etc."
	bl_options = {'REGISTER', 'UNDO'}


	filename: StringProperty(
		name="File Name",
		description="Name of the exported file",
		default="default_model_name.md"
	)
	

	filename_ext = ""
	filter_glob: StringProperty(
		default="",
		options={'HIDDEN'},
		maxlen=255,
	)
	files: CollectionProperty(
		type=bpy.types.PropertyGroup
	)
	map: BoolProperty(
		name="Map model",
		description="Export Mesh as a SCR md",
		default=False,
	)
	okami: BoolProperty(
		name="MD model type 0",
		description="Exports the MD model as a type 0 model (OKAMI MD)",
		default=False,
	)


	@classmethod
	def poll(cls, context):
		active_object = context.active_object  
		return active_object is not None and active_object.type == "ARMATURE"
	
	def invoke(self, context, event):
		directory = os.path.dirname(self.filepath)  # preserve last used folder
		if not directory:  # if first time, use Blender's default export path
			directory = "//"

		filename = bpy.path.ensure_ext(context.active_object.name, self.filename_ext)
		self.filepath = os.path.join(directory, filename)
		return super().invoke(context, event)
	
	
	def execute(self, context):
		

		selected_obj = context.active_object

		if selected_obj is None or selected_obj.type != 'ARMATURE':
			self.report({'WARNING'}, "Select an armature first!")
			return {'CANCELLED'}
		child_meshes = [child for child in selected_obj.children if child.type == 'MESH']
		if not child_meshes:
			self.report({'INFO'}, "No child meshes found.")
			return {'CANCELLED'}
		modelRet = ''



		if any("_" in bone.name for bone in selected_obj.pose.bones):
		    self.report({'ERROR'}, "Cannot export MD with Mirror Links enabled. Revert mirror links before exporting.")
		    return {'CANCELLED'}
			
		def get_bone_hierarchy_depth(bone):
			"""Recursively find the depth of the bone in the hierarchy."""
			depth = 0
			while bone.parent:
				bone = bone.parent
				depth += 1
				
			return depth


		file_path = self.filepath + "." + ("md" if self.map == False else "scr")
		print(file_path)
		
		
		if os.path.exists(file_path):
			os.remove(file_path)
		with open(file_path, 'wb') as f:
			
			for n in child_meshes:
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.select_all(action='DESELECT')
				if n.hide_get():
					n.hide_set(False)  # Unhide the object
				n.select_set(True)
				bpy.context.view_layer.objects.active = n
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
				bpy.ops.mesh.select_all(action='DESELECT')
			
			
			
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.select_all(action='DESELECT')
			selected_obj.select_set(True)
			bpy.context.view_layer.objects.active = selected_obj
			bpy.ops.object.mode_set(mode='EDIT')
			
			aBones = []
			
			for fff in selected_obj.data.edit_bones:
				parseable = tryParse(fff.name)
				if parseable != -99999:
					aBones.append([fff,parseable])

			aBones.sort(key=lambda x: x[1])
			def fill():
				while f.tell() %16 != 0:
					f.write(struct.pack('<b', 0))
			def getArray(GET_FACE):
				return [v.index for v in GET_FACE]
			
			
			
			
			uses_ref_md = False
			nameListy = []
			
			
			if context.scene.md_input:
				if os.path.isfile(context.scene.md_input):
					uses_ref_md = True
					with open(context.scene.md_input, "rb") as fe:
						value = 0
						try:
							value = struct.unpack('<I', fe.read(4))[0]
						except Exception:
							self.report({'ERROR'}, f"The ref md is NULL. the use of ref md was automatically disabled.")
							uses_ref_md = False
							
							
						if value != 7496563:
							self.report({'ERROR'}, f"The ref md is not a MD file. the use of ref md was automatically disabled.")
							uses_ref_md = False
							
						if uses_ref_md == True:
							fe.seek(8)
							meshcount = struct.unpack('<I', fe.read(4))[0]
							
							fe.seek(16)
							
							offsets = []
							for j in range(0,meshcount):
								offsets.append(struct.unpack('<I', fe.read(4))[0])
							
							for j in offsets:
								fe.seek(j+4)
								UNID = struct.unpack('<I', fe.read(4))
								if self.okami == False:
									name_sampled = fe.read(8).decode('utf-8').rstrip('\x00')
								else:
									name_sampled = ""

								fe.seek(j)
								if self.okami == False:
									nameListy.append([name_sampled,UNID,fe.read(112)])
								else:
									nameListy.append([name_sampled,UNID,fe.read(56)])
			

			NAME_REMAINING = []
			for ig in nameListy:
				for n in child_meshes:
					if ig[0] in n.name:
						NAME_REMAINING.append(ig)
						
						
			nme_set1 = set(map(tuple, NAME_REMAINING))
			nme_set2 = set(map(tuple,nameListy))
			
			
			NAME_DIFF = nme_set2 - nme_set1
			#for jjjjj in NAME_DIFF:
			#   print(jjjjj[0])
				
			LENADDITIVE = len(NAME_DIFF)
			
			
			
			
			#f.write(selected_obj.name.encode('utf-8'))
			f.write(struct.pack('<I', 7496563))
			if self.okami == False:
				f.write(struct.pack('<I', 3))
			else:
				f.write(struct.pack('<I', 0))
			f.write(struct.pack('<I', len(child_meshes) + LENADDITIVE))
			f.write(struct.pack('<I', 0))
			
			adresses_offsets = []
			for n in range(0,len(child_meshes) + LENADDITIVE):
				adresses_offsets.append(f.tell())
				f.write(struct.pack('<I', 0))

			

			
			
			
			
			
			fill()
			MDBOffsets = []
			for obj in child_meshes:
				bm = bmesh.new()
				bm.from_mesh(obj.data)
				obj.data.calc_normals_split()
				
				

				MDBOffsets.append(f.tell())
				f.write(struct.pack('<I', 6448237))
				f.write(struct.pack('<I', 0))
			
			
			
				f.write(struct.pack('<H', len(aBones)))
				

				faces_with_material = getFacesAndMaterials(obj,self,bm)
							
					

				f.write(struct.pack('<H', len(faces_with_material)))
				f.write(struct.pack('<I', 0))
				f.write(struct.pack('<I', 0))
				f.write(struct.pack('<I', 0))
				f.write(struct.pack('<I', 0))
				if self.okami == False:
					if self.map == False:
						f.write(struct.pack('<f', 1))
					else:
						f.write(struct.pack('<f', 0))
				else:
					f.write(struct.pack('<f', 0))
				
				mdheaders_offsets = []
				for nt in range(0,len(faces_with_material)):
					mdheaders_offsets.append(f.tell())
					f.write(struct.pack('<I', 0))
				fill()
				
				#Here, the skeleton would be filled, but i will use dummy references.
				
				LEEEET = 0
				for faces_mat in faces_with_material:
					mesh = obj.data
					try:
						tnnnn = int(faces_mat[1].name)
					except Exception:
						self.report({'ERROR'}, f"The material {faces_mat[1].name} is not in index mode.")
						return {'CANCELLED'}
						
					
					BACK_UP = f.tell()
					MDB_REF_OFFSET = MDBOffsets[len(MDBOffsets)-1]
					f.seek(mdheaders_offsets[LEEEET])
					f.write(struct.pack('<I', BACK_UP - MDB_REF_OFFSET))
					f.seek(BACK_UP)
					LEEEET += 1
					
					
					
							
					TRIANG_OFFSET = f.tell()
					f.write(struct.pack('<I', 0))
					
					NORMALS_OFFSET = f.tell()
					f.write(struct.pack('<I', 0))
					
					UV_OFFSET = f.tell()
					f.write(struct.pack('<I', 0))
					
					VERTC_OFFSET = f.tell()
					f.write(struct.pack('<I', 0))
					
					BONEWEIGHTS_OFFSET = f.tell()
					f.write(struct.pack('<I', 0))
					
					WRITTEN_VERTICS_COUNT_OFFSET = f.tell()
					f.write(struct.pack('<H', 0))
					
					TEXTURE_INDEX_OFFSET = f.tell()
					f.write(struct.pack('<H', int(faces_mat[1].name)))
					
					
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))

					
					VWRITESTART = f.tell()
					
					
					
					bm.verts.ensure_lookup_table()
					bm.edges.ensure_lookup_table()
					bm.faces.ensure_lookup_table()
					
						
					tris = getConnectsMD(faces_mat[0])
					reorderedFaces = []
					
					
					for n in tris:
						try:
							ord = stairCase(n)
						except Exception:
							self.report({'ERROR'}, f"Reordening vertices failed! Make sure you have run the Triangle Branch Sorter.")
							return {'CANCELLED'}
							
							
							
					for n in tris:
						ord = stairCase(n)
						varPO = len(reorderedFaces)
						for nn in ord:
							reorderedFaces.append([nn,600])
						reorderedFaces[varPO][1] = 32764

					reorderedTriangles = []
					for n in reorderedFaces:
						for fi in faces_mat[0]:
							curVTS = getArray(fi.verts)
							if len(set(curVTS) & set(n[0])) == 3:   
								#print(set(curVTS) & set(n[0]))
								curSet = []
								
								for j in n[0]:
									for k in fi.verts:
										if j == k.index:
											curSet.append(k)
								reorderedTriangles.append([curSet,n[1],fi])
								break
					
					TLFaces = []
					for jj in reorderedTriangles:
						if jj[1] == 32764:
							for jje in jj[0]:
								TLFaces.extend([[jje,-32768,jj[2]]])
							TLFaces[len(TLFaces)-1][1] = -9999
							
						else:
							TLFaces.extend([[jj[0][2],-9999,jj[2]]])
							
					def getProd(v1,v2,v3,n1,n2,n3):
						edge1 = v2 - v1
						edge2 = v3 - v1
						face_normal = edge1.cross(edge2).normalized()
						average_normal = (n1 + n2 + n3).normalized()
						dot_product = face_normal.dot(average_normal)
						return dot_product




					storedList = []
					for vertic in TLFaces:
						vert = vertic[0]
						if self.map == False:
							f.write(struct.pack('<f', vert.co.x))
							f.write(struct.pack('<f', vert.co.y))
							f.write(struct.pack('<f', vert.co.z))
						else:
							rounded = vert.co * 100.0
							
							if rounded.x > 32767 or rounded.x < -32768:
								self.report({'ERROR'}, "A Vertice has a position x interval of " + str(rounded.x) + " which exceeds the cordinate limit for a map. (327.67 or -327.68).")
								return {'CANCELLED'}
							if rounded.y > 32767 or rounded.y < -32768:
								self.report({'ERROR'}, "A Vertice has a position y interval of " + str(rounded.y) + " which exceeds the cordinate limit for a map. (327.67 or -327.68).")
								return {'CANCELLED'}
							if rounded.z > 32767 or rounded.z < -32768:
								self.report({'ERROR'}, "A Vertice has a position z interval of " + str(rounded.z) + " which exceeds the cordinate limit for a map. (327.67 or -327.68).")
								return {'CANCELLED'}
							
							f.write(struct.pack('<h', round(rounded.x)))
							f.write(struct.pack('<h', round(rounded.y)))
							f.write(struct.pack('<h', round(rounded.z)))
							

								
								

							
							
						
						CO = vertic[1]
						if CO != -32768:
							tss = getProd(vert.co, storedList[len(storedList)-1].co,storedList[len(storedList)-2].co,   vert.normal, storedList[len(storedList)-1].normal,storedList[len(storedList)-2].normal)
							f.write(struct.pack('<h', 1 if tss > 0 else 0))
						else:
							f.write(struct.pack('<h', CO))

						
						if self.map == False:
							f.write(struct.pack('<h', 0)) #this aligns
							
						storedList.append(vert)

						
					
					
					fill()
					CHECKPOINT = f.tell()
					f.seek(TRIANG_OFFSET)
					f.write(struct.pack('<I', VWRITESTART  - TRIANG_OFFSET))
					f.seek(WRITTEN_VERTICS_COUNT_OFFSET)
					f.write(struct.pack('<H', len(TLFaces)))
					f.seek(CHECKPOINT)
					
					
					def map_value(value, in_min, in_max, out_min, out_max):
						return (value - in_min) / (in_max - in_min) * (out_max - out_min) + out_min 
					
					
					
					NWRITESTART = f.tell()
					if self.map == False:
						
						for vert in TLFaces:
							vt = vert[0]
							split_normals = [loop.normal for loop in obj.data.loops if loop.vertex_index == vt.index]
							avg_normal = sum(split_normals, mathutils.Vector()) / len(split_normals)
							avg_normal.normalize()
							
							le = math.sqrt(avg_normal.x*avg_normal.x + avg_normal.y*avg_normal.y + avg_normal.z*avg_normal.z)

							
							
							f.write(struct.pack('<b', int(map_value(avg_normal.x,-1,1,-128,127))))
							f.write(struct.pack('<b', int(map_value(avg_normal.y,-1,1,-128,127))))
							f.write(struct.pack('<b', int(map_value(avg_normal.z,-1,1,-128,127))))
							f.write(struct.pack('<b', 0))

								
						fill()
						CHECKPOINT = f.tell()
						f.seek(NORMALS_OFFSET)
						f.write(struct.pack('<I', NWRITESTART - TRIANG_OFFSET))
						f.seek(CHECKPOINT)
					
					


					uv_layer = bm.loops.layers.uv.active
					if uv_layer is None:
						self.report({'ERROR'}, f"No UV layer was found for mesh {obj.name}.")
						return {'CANCELLED'}
				
				
					UWRITESTART = f.tell()
					for face in TLFaces:
						vert = face[0]
						for loop in face[2].loops:
							if loop.vert.index == vert.index:
								uv = loop[uv_layer].uv
								#print(uv)
								tlUVX = uv.x * 4096.0
								tlUVY = uv.y * -4096.0
								
								
								if tlUVX < -32768 or tlUVX > 32767 or tlUVY < -32768 or tlUVY > 32767:
									self.report({'ERROR'}, f"A UV on {obj.name} exceeds the minimum/maximum allowed position (-32768/32767).")
									return {'CANCELLED'}
								
								f.write(struct.pack('<h', int(tlUVX)))
								f.write(struct.pack('<h', int(tlUVY)))
					
					
					
					
					fill()
					CHECKPOINT = f.tell()
					f.seek(UV_OFFSET)
					f.write(struct.pack('<I', UWRITESTART - TRIANG_OFFSET))
					f.seek(CHECKPOINT)
					
					


					color_layer = obj.data.color_attributes
					COLWRITESTART = f.tell()
					if color_layer:
						cdata = color_layer.active_color
						for fi in TLFaces:
							vert = fi[0]
							written = False
							for loop_index, loop_color in enumerate(cdata.data):
								vertex_index = obj.data.loops[loop_index].vertex_index
								
								if vertex_index == vert.index:
									
									
									written = True
									f.write(struct.pack('<B', int(map_value(loop_color.color[0],0,1,0,128))))
									f.write(struct.pack('<B', int(map_value(loop_color.color[1],0,1,0,128))))
									f.write(struct.pack('<B', int(map_value(loop_color.color[2],0,1,0,128))))
									f.write(struct.pack('<B', int(map_value(loop_color.color[3],0,1,0,128))))
							if written == False:
								f.write(struct.pack('<I', 2155905152))
										
					else:
						for fi in TLFaces:
							vert = fi[0]
							f.write(struct.pack('<I', 2155905152))
						
					fill()
					CHECKPOINT = f.tell()
					f.seek(VERTC_OFFSET)
					f.write(struct.pack('<I', COLWRITESTART - TRIANG_OFFSET))
					f.seek(CHECKPOINT)
					
					WEIWRITESTART = f.tell()
					for fi in TLFaces:
						fi2 = fi[0]
						vertex = obj.data.vertices[fi2.index]
						if len(vertex.groups) > 3:
							self.report({'ERROR'}, f"A vertex is assigned in more than 3 vert groups. Locate the vert group and limit to 3.")
							return {'CANCELLED'}
							
							
						f.write(struct.pack('<b', 0))
						NAMELIS = []
						for group in vertex.groups:
							group_index = group.group
							group_name = obj.vertex_groups[group_index].name
							name_int = 0
							try:
								name_int = (int(group_name.replace("root","1")) -1) * 4 	
							except Exception:
								self.report({'ERROR'}, f"The group {group_name} is not in indexed mode.")
								return {'CANCELLED'}
							NAMELIS.append(name_int)
							
							

						for nm in NAMELIS:
							try:
								f.write(struct.pack('<B', nm))
							except Exception:
								self.report({'ERROR'}, f"The bone count exceeds the max amount of bones a model can have. (63)")
								return {'CANCELLED'}
						
						
						while f.tell() % 4 != 0:
							f.write(struct.pack('<B', 0))
								

						totalWeight = 0.0
						for group in vertex.groups:
							totalWeight += group.weight
						
						percentList = []
						for group in vertex.groups:
							if totalWeight == 0:
								totalWeight = 1
							percent = math.floor(group.weight * 100 / totalWeight)
							percentList.append(percent)

							
						while sum(percentList) < 100:
							percentList[0]+= 1
							
							
						for group in percentList:
							f.write(struct.pack('<B', group))   
						while f.tell() % 4 != 0:
							f.write(struct.pack('<B', 0))
								
					fill()
					CHECKPOINT = f.tell()
					f.seek(BONEWEIGHTS_OFFSET)
					f.write(struct.pack('<I', WEIWRITESTART - TRIANG_OFFSET))
					f.seek(CHECKPOINT)
					
					
			if uses_ref_md:
				for jj in NAME_DIFF:
					MDBOffsets.append(f.tell())
				f.write(struct.pack('<I', 6448237))
				
				f.write(struct.pack('<I', 0))
				f.write(struct.pack('<H', len(aBones)))
				f.write(struct.pack('<H', 1))


				f.write(struct.pack('<I', 0))
				f.write(struct.pack('<I', 0))
				f.write(struct.pack('<I', 0))
				f.write(struct.pack('<I', 0))

				f.write(struct.pack('<f', 0))
				
				
				
				f.write(struct.pack('<I', 48))
				fill()
				f.write(struct.pack('<I', 0 + 32))
				f.write(struct.pack('<I', 32 + 32))
				f.write(struct.pack('<I', 48 + 32))
				f.write(struct.pack('<I', 64 + 32))
				f.write(struct.pack('<I', 80 + 32))

				f.write(struct.pack('<H', 3))
				f.write(struct.pack('<H', 0))
				f.write(struct.pack('<I', 0))
				f.write(struct.pack('<I', 0))


				f.write(struct.pack('<Q', 9223372036854775808))
				f.write(struct.pack('<Q', 9223372036854775808))
				f.write(struct.pack('<Q', 281474976710656))
				f.write(struct.pack('<Q', 0))
				f.write(struct.pack('<Q', 0))   		
				f.write(struct.pack('<Q', 0))   	
				f.write(struct.pack('<Q', 0))   	
				f.write(struct.pack('<Q', 0))
				f.write(struct.pack('<Q', 36170084271554688))
				f.write(struct.pack('<Q', 8421504))
				f.write(struct.pack('<Q', 0))
				f.write(struct.pack('<Q', 0))
				f.write(struct.pack('<Q', 0))
				f.write(struct.pack('<Q', 0))




				
			CAN_I_TELL_YOU_A_JOKE = 0 #nuh uh
			for obj in child_meshes:
				BACK_UP = f.tell()
				f.seek(adresses_offsets[CAN_I_TELL_YOU_A_JOKE])
				f.write(struct.pack('<I', BACK_UP))
				f.seek(BACK_UP)
				
				
				f.write(struct.pack('<i', MDBOffsets[CAN_I_TELL_YOU_A_JOKE] - BACK_UP))
				
				
				
				CAN_I_TELL_YOU_A_JOKE += 1
				
				
				
				#f.write(struct.pack('<i', 0))
				f.write(struct.pack('<i', 0))
				if self.okami == False:
					f.write(obj.name[:8].encode('utf-8'))
					fill()
					
					
				f.write(struct.pack('<f', obj.scale.x))
				f.write(struct.pack('<f', obj.scale.y))
				f.write(struct.pack('<f', obj.scale.z))

				f.write(struct.pack('<f', obj.rotation_euler.x))
				f.write(struct.pack('<f', obj.rotation_euler.y))
				f.write(struct.pack('<f', obj.rotation_euler.z))

				f.write(struct.pack('<f', obj.location.x))
				f.write(struct.pack('<f', obj.location.y))
				f.write(struct.pack('<f', obj.location.z))




				if self.okami == False:
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 1))
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<f', 600))
					f.write(struct.pack('<I', 8323072))
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))
				else:
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))
					f.write(struct.pack('<I', 0))


			if uses_ref_md == True:
				for jj in NAME_DIFF:
					hhoffset = f.tell()
					#print(jj[2])
					#f.write(struct.pack(jj[2]))
					f.write(jj[2])
					lastPOSE = f.tell()
					f.seek(hhoffset)



					f.seek(adresses_offsets[CAN_I_TELL_YOU_A_JOKE])
					f.write(struct.pack('<I', hhoffset))
					f.seek(hhoffset)
				
				
					f.write(struct.pack('<i',  MDBOffsets[CAN_I_TELL_YOU_A_JOKE] - hhoffset))
				
				
				
					CAN_I_TELL_YOU_A_JOKE += 1
					f.seek(lastPOSE)




			#Write bones and ref them through the offset of MDB, since its a uint32 and it can store over an ofsset of 1GB, this is completely fine.
			skeleton_written_on_pos = f.tell()
			pbones = selected_obj.pose.bones
			for bone in aBones:
				
				subtractive = bone[0].parent
				f.write(struct.pack('<f', bone[0].head.x - subtractive.head.x))
				f.write(struct.pack('<f', bone[0].head.y - subtractive.head.y))
				f.write(struct.pack('<f', bone[0].head.z - subtractive.head.z))
				
				if self.okami == False:
					#f.write(struct.pack('<H', 65535)) #this is the bone what mirrors the other
					pbone_s = pbones[bone[0].name]
					#print(pbone_s)
					if "B2MD_MIRRORLINK" in pbone_s:
						parseable = tryParse(pbone_s["B2MD_MIRRORLINK"].split('/////')[0])
						f.write(struct.pack('<H', parseable - 1))
					else:
						f.write(struct.pack('<H', 65535))
						
					
					if bone[0].parent:
						parseable = tryParse(bone[0].parent.name)
						
						
						if parseable != -99999:
							f.write(struct.pack('<h', parseable-1))
						else:
							f.write(struct.pack('<h', -1))
					else:
						f.write(struct.pack('<h', -1))
				else:   	
					if bone[0].parent:
						parseable = tryParse(bone[0].parent.name)
						
						
						if parseable != -99999:
							f.write(struct.pack('<i', parseable-1))
						else:
							f.write(struct.pack('<i', -1))
					else:
						f.write(struct.pack('<i', -1))

			for offset in MDBOffsets:
				f.seek(offset+4)
				f.write(struct.pack('<I', skeleton_written_on_pos - offset))




			
			bpy.ops.object.mode_set(mode='OBJECT')
		self.report({'INFO'}, "Finished!")
		return {'FINISHED'}




def tryParse(nm):
	parseable = -99999
	try:
		parseable = int(nm)
		if parseable < 0:
			parseable = -99999
	except:
		pass
	return parseable

class OBJECT_OT_ExportMDPart(bpy.types.Operator, ExportHelper):
	
	bl_idname = "object.export_action_md_part"
	bl_label = "Export"
	bl_description = "Exports only the selected mesh as a part (skeleton info will not be preserved)"
	bl_label = "Export Models"
	bl_options = {'REGISTER', 'UNDO'}

	filename_ext = ".md"
	filter_glob: StringProperty(
		default="*.mdpart",
		options={'HIDDEN'},
		maxlen=255,
	)
	files: CollectionProperty(
		type=bpy.types.PropertyGroup
	)
	map: BoolProperty(
		name="Map model",
		description="Export Mesh as a SCR md",
		default=False,
	)

	@classmethod
	def poll(cls, context):
		active_object = context.active_object  
		return active_object is not None and bpy.context.mode == "OBJECT"  and active_object.type == "MESH"
	
	def execute(self, context):
		obj = context.active_object
		directory = self.filepath
		directory = directory.replace(os.path.basename(directory),"")
		directory = directory[:-1] + "/"


		def get_bone_hierarchy_depth(bone):
			"""Recursively find the depth of the bone in the hierarchy."""
			depth = 0
			while bone.parent:
				bone = bone.parent
				depth += 1
				
			return depth


		file_path = directory + obj.name + "_output.mdpart"
		
		
		
		if os.path.exists(file_path):
			os.remove(file_path)
		with open(file_path, 'wb') as f:
			bpy.context.view_layer.objects.active = obj
			bpy.ops.object.mode_set(mode='EDIT')
			

			def fill():
				while f.tell() %16 != 0:
					f.write(struct.pack('<b', 0))
			def getArray(GET_FACE):
				return [v.index for v in GET_FACE]
			

			

			bm = bmesh.new()
			bm.from_mesh(obj.data)
			obj.data.calc_normals_split()
			
			

			MDBREF = f.tell()
			f.write(struct.pack('<I', 6448237))
			f.write(struct.pack('<I', 0))
		
		
		
			f.write(struct.pack('<H', 0))
			faces_with_material = getFacesAndMaterials(obj,self,bm)
						
				

			f.write(struct.pack('<H', len(faces_with_material)))
			f.write(struct.pack('<I', 0))
			f.write(struct.pack('<I', 0))
			f.write(struct.pack('<I', 0))
			f.write(struct.pack('<I', 0))
			if self.map == False:
				f.write(struct.pack('<f', 1))
			else:
				f.write(struct.pack('<f', 0))
				
				
				
			mdheaders_offsets = []
			for nt in range(0,len(faces_with_material)):
				mdheaders_offsets.append(f.tell())
				f.write(struct.pack('<I', 0))
			fill()
			
			#Here, the skeleton would be filled, but i will use dummy references.
			
			LEEEET = 0
			for faces_mat in faces_with_material:
				mesh = obj.data
				try:
					tnnnn = int(faces_mat[1].name)
				except Exception:
					self.report({'ERROR'}, f"The material {faces_mat[1].name} is not in index mode.")
					return {'CANCELLED'}
					
				
				BACK_UP = f.tell()
				f.seek(mdheaders_offsets[LEEEET])
				f.write(struct.pack('<I', BACK_UP - MDBREF))
				f.seek(BACK_UP)
				LEEEET += 1
				
				
				
						
				TRIANG_OFFSET = f.tell()
				f.write(struct.pack('<I', 0))
				
				NORMALS_OFFSET = f.tell()
				f.write(struct.pack('<I', 0))
				
				UV_OFFSET = f.tell()
				f.write(struct.pack('<I', 0))
				
				VERTC_OFFSET = f.tell()
				f.write(struct.pack('<I', 0))
				
				BONEWEIGHTS_OFFSET = f.tell()
				f.write(struct.pack('<I', 0))
				
				WRITTEN_VERTICS_COUNT_OFFSET = f.tell()
				f.write(struct.pack('<H', 0))
				
				TEXTURE_INDEX_OFFSET = f.tell()
				f.write(struct.pack('<H', int(faces_mat[1].name)))
				
				
				f.write(struct.pack('<I', 0))
				f.write(struct.pack('<I', 0))
				
				
				VWRITESTART = f.tell()
				
				
				
				bm.verts.ensure_lookup_table()
				bm.edges.ensure_lookup_table()
				bm.faces.ensure_lookup_table()
				
					
				tris = getConnectsMD(faces_mat[0])
				reorderedFaces = []
				
				
				for n in tris:
					try:
						ord = stairCase(n)
					except Exception:
						self.report({'ERROR'}, f"Reordening vertices failed! Make sure you have run the Triangle Branch Sorter.")
						return {'CANCELLED'}
						
						
						
				for n in tris:
					ord = stairCase(n)
					varPO = len(reorderedFaces)
					for nn in ord:
						reorderedFaces.append([nn,600])
					reorderedFaces[varPO][1] = 32764

					
				reorderedTriangles = []
				for n in reorderedFaces:
					for fi in faces_mat[0]:
						curVTS = getArray(fi.verts)
						if len(set(curVTS) & set(n[0])) == 3:   
							#print(set(curVTS) & set(n[0]))
							curSet = []
							
							for j in n[0]:
								for k in fi.verts:
									if j == k.index:
										curSet.append(k)
							reorderedTriangles.append([curSet,n[1],fi])
							break
				
				TLFaces = []
				for jj in reorderedTriangles:
					if jj[1] == 32764:
						for jje in jj[0]:
							TLFaces.extend([[jje,-32768,jj[2]]])
						TLFaces[len(TLFaces)-1][1] = -9999
						
					else:
						TLFaces.extend([[jj[0][2],-9999,jj[2]]])
						
				#for jj in TLFaces:
				#	print(jj[1])
				
						
						
				def getProd(v1,v2,v3,n1,n2,n3):
					edge1 = v2 - v1
					edge2 = v3 - v1
					face_normal = edge1.cross(edge2).normalized()
					average_normal = (n1 + n2 + n3).normalized()
					dot_product = face_normal.dot(average_normal)
					#print(dot_product)
					return dot_product

					
				storedList = []
				for vertic in TLFaces:
					vert = vertic[0]
					f.write(struct.pack('<f', vert.co.x))
					f.write(struct.pack('<f', vert.co.y))
					f.write(struct.pack('<f', vert.co.z))
					
					
					CO = vertic[1]
					if CO != -32768:
						tss = getProd(vert.co, storedList[len(storedList)-1].co,storedList[len(storedList)-2].co,   vert.normal, storedList[len(storedList)-1].normal,storedList[len(storedList)-2].normal)
						
						if tss > 0:
							f.write(struct.pack('<h', 1))
						else:
							f.write(struct.pack('<h', 0))
							
							
					else:
						f.write(struct.pack('<h', CO))

					
					if self.map == False:
						f.write(struct.pack('<h', 0)) #this aligns
						
					storedList.append(vert)

					
				
				
				fill()
				CHECKPOINT = f.tell()
				f.seek(TRIANG_OFFSET)
				f.write(struct.pack('<I', VWRITESTART  - TRIANG_OFFSET))
				f.seek(WRITTEN_VERTICS_COUNT_OFFSET)
				f.write(struct.pack('<H', len(TLFaces)))
				f.seek(CHECKPOINT)
				
				
				def map_value(value, in_min, in_max, out_min, out_max):
					return (value - in_min) / (in_max - in_min) * (out_max - out_min) + out_min 
				
				
				
				NWRITESTART = f.tell()
				if self.map == False:
					
					for vert in TLFaces:
						vt = vert[0]
						split_normals = [loop.normal for loop in obj.data.loops if loop.vertex_index == vt.index]
						avg_normal = sum(split_normals, mathutils.Vector()) / len(split_normals)
						avg_normal.normalize()
						
						
						
						le = math.sqrt(avg_normal.x*avg_normal.x + avg_normal.y*avg_normal.y + avg_normal.z*avg_normal.z)
						
						f.write(struct.pack('<b', int(map_value(avg_normal.x,-1,1,-128,127))))
						f.write(struct.pack('<b', int(map_value(avg_normal.y,-1,1,-128,127))))
						f.write(struct.pack('<b', int(map_value(avg_normal.z,-1,1,-128,127))))
						f.write(struct.pack('<b', 0))


					fill()
					CHECKPOINT = f.tell()
					f.seek(NORMALS_OFFSET)
					f.write(struct.pack('<I', NWRITESTART - TRIANG_OFFSET))
					f.seek(CHECKPOINT)
				
				


				uv_layer = bm.loops.layers.uv.active
				if uv_layer is None:
					self.report({'ERROR'}, f"No UV layer was found for mesh {obj.name}.")
					return {'CANCELLED'}
			
			
				UWRITESTART = f.tell()
				for face in TLFaces:
					vert = face[0]
					for loop in face[2].loops:
						if loop.vert.index == vert.index:
							uv = loop[uv_layer].uv
							#print(uv)
							tlUVX = uv.x * 4096.0
							tlUVY = uv.y * -4096.0
							
							
							#print(tlUVX,tlUVY)
							if tlUVX < -32768 or tlUVX > 32767 or tlUVY < -32768 or tlUVY > 32767:
								self.report({'ERROR'}, f"A UV on {obj.name} exceeds the minimum/maximum allowed position (-32768/32767).")
								return {'CANCELLED'}
							
							f.write(struct.pack('<h', int(tlUVX)))
							f.write(struct.pack('<h', int(tlUVY)))
				
				
				
				
				fill()
				CHECKPOINT = f.tell()
				f.seek(UV_OFFSET)
				f.write(struct.pack('<I', UWRITESTART - TRIANG_OFFSET))
				f.seek(CHECKPOINT)
				
				




				color_layer = obj.data.color_attributes
				COLWRITESTART = f.tell()
				if color_layer:
					cdata = color_layer.active_color
					for fi in TLFaces:
						vert = fi[0]
						written = False
						for loop_index, loop_color in enumerate(cdata.data):
							vertex_index = obj.data.loops[loop_index].vertex_index
							
							if vertex_index == vert.index:
								
								
								written = True
								#f.write(struct.pack('<B', max(0, min(round(loop_color.color[0] * 128), 128))))
								#f.write(struct.pack('<B', max(0, min(round(loop_color.color[1] * 128), 128))))
								#f.write(struct.pack('<B', max(0, min(round(loop_color.color[2] * 128), 128))))
								#f.write(struct.pack('<B', max(0, min(round(loop_color.color[3] * 128), 128))))
								
								f.write(struct.pack('<B', int(map_value(loop_color.color[0],0,1,0,128))))
								f.write(struct.pack('<B', int(map_value(loop_color.color[1],0,1,0,128))))
								f.write(struct.pack('<B', int(map_value(loop_color.color[2],0,1,0,128))))
								f.write(struct.pack('<B', int(map_value(loop_color.color[3],0,1,0,128))))
						if written == False:
							f.write(struct.pack('<I', 2155905152))
									
				else:
					for fi in TLFaces:
						vert = fi[0]
						f.write(struct.pack('<I', 2155905152))
					
				fill()
				CHECKPOINT = f.tell()
				f.seek(VERTC_OFFSET)
				f.write(struct.pack('<I', COLWRITESTART - TRIANG_OFFSET))
				f.seek(CHECKPOINT)
				
				WEIWRITESTART = f.tell()
				for fi in TLFaces:
					fi2 = fi[0]
					vertex = obj.data.vertices[fi2.index]
					if len(vertex.groups) > 3:
						self.report({'ERROR'}, f"A vertex is assigned in more than 3 vert groups. Locate the vert group and limit to 3.")
						return {'CANCELLED'}
						
						
					f.write(struct.pack('<b', 0))
					NAMELIS = []
					for group in vertex.groups:
						group_index = group.group
						group_name = obj.vertex_groups[group_index].name
						name_int = 0
						try:
							name_int = (int(group_name.replace("root","1")) -1) * 4 	
						except Exception:
							self.report({'ERROR'}, f"The group {group_name} is not in indexed mode.")
							return {'CANCELLED'}
						NAMELIS.append(name_int)
						
						
						
					#NAMELIS.sort()
					#NAMELIS.reverse()
					for nm in NAMELIS:
						try:
							f.write(struct.pack('<B', nm))
						except Exception:
							self.report({'ERROR'}, f"The bone count exceeds the max amount of bones a model can have. (63)")
							return {'CANCELLED'}
					
					
					while f.tell() % 4 != 0:
						f.write(struct.pack('<B', 0))
							
							
					#print("NEW?")
					totalWeight = 0.0
					for group in vertex.groups:
						totalWeight += group.weight
					
					percentList = []
					for group in vertex.groups:
						if totalWeight == 0:
							totalWeight = 1
						percent = math.floor(group.weight * 100 / totalWeight)
						percentList.append(percent)
					#percentList.sort()
					#percentList.reverse()
					

						
					while sum(percentList) < 100:
						percentList[0]+= 1
						
						
					for group in percentList:
						f.write(struct.pack('<B', group))   
					while f.tell() % 4 != 0:
						f.write(struct.pack('<B', 0))
							
				fill()
				CHECKPOINT = f.tell()
				f.seek(BONEWEIGHTS_OFFSET)
				f.write(struct.pack('<I', WEIWRITESTART - TRIANG_OFFSET))
				f.seek(CHECKPOINT)
					
			
			bpy.ops.object.mode_set(mode='OBJECT')
		self.report({'INFO'}, "Finished!")
		return {'FINISHED'}
	
	
	
	
class OBJECT_OT_RenameSkeleton(bpy.types.Operator):
	bl_idname = "object.rename_skel"
	bl_label = "Rename"
	bl_description = "Renames the skeleton to the god hand indexed format\nSelect an armature, and then, execute this button"


	@classmethod
	def poll(cls, context):
		active_object = context.active_object  
		return active_object is not None and active_object.type == "ARMATURE"
	def execute(self, context):
		bpy.ops.object.mode_set(mode='OBJECT')
		
		
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
						#print(bone_name);
						selected_obj.pose.bones[i].name = str(i);
						
						
		selected_obj.pose.bones[0].name = "root";
		
		
		return {'FINISHED'}
class OBJECT_OT_Unus(bpy.types.Operator):
	bl_idname = "object.unus"
	bl_label = "Utility"
	bl_description = "Removes all groups which the bones doesn't exists\nSelect an armature, and then, execute this button"
	@classmethod
	def poll(cls, context):
		active_object = context.active_object  
		return active_object is not None and bpy.context.mode == "OBJECT" and active_object.type == "ARMATURE"
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
class ImportMD(bpy.types.Operator, ImportHelper):
	"""Import God Hand Model"""
	bl_idname = "import_scene.md"
	bl_label = "Import Models"
	bl_options = {'REGISTER', 'UNDO'}

	filename_ext = ".md"
	filter_glob: StringProperty(
		default="*.md;*.scr",
		options={'HIDDEN'},
		maxlen=255,
	)
	files: CollectionProperty(
		type=bpy.types.PropertyGroup
	)
	connect_bone: BoolProperty(
		name="Connect Bones",
		description="Automatically connect the bones",
		default=False,
	)
	import_mat: BoolProperty(
		name="Import Materials",
		description="Import materials indexes from the model",
		default=True,
	)
	import_vertc: BoolProperty(
		name="Import Vert Colors",
		description="Import vert colors from the model",
		default=True,
	)
	import_norm: BoolProperty(
		name="Import Normals",
		description="Import the model normals",
		default=True,
	)
	def execute(self, context):
		layout = self.layout	 
			
		directory = self.filepath
		directory = directory.replace(os.path.basename(directory),"")
		directory = directory[:-1]
		for file_elem in self.files:
			file_path = f"{directory}/{file_elem.name}"
			IMP_M(file_path,self, context, self.import_mat,self.import_norm,self.import_vertc,self.connect_bone)
		return {'FINISHED'}
class ImportMDImediate(bpy.types.Operator):
	"""Import God Hand Model"""
	bl_idname = "import_scene_imediate.md"
	bl_label = "Import Models"
	bl_options = {'REGISTER', 'UNDO'}
	def execute(self, context):
		IMP_M(context.scene.md_input,self,context,True,True,True,False)
		return {'FINISHED'}
def IMP_M(file_path,self, context,import_mat,import_norm,import_vertc,connect_bone):
		context.scene.md_input = file_path
		print("well yeah its workin")
			
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
		
		armature.name = os.path.basename(file_path )
		bpy.ops.object.mode_set(mode='OBJECT')
		#allMCO = []
		
		
		with open(file_path, "rb") as file:
			filemagic = struct.unpack("<I", file.read(4))[0]
			
			
			if filemagic == 7496563:
				mdVersion = struct.unpack("<I", file.read(4))[0]
				
				
				meshCount = struct.unpack("<I", file.read(4))[0]
				file.seek(16)
				for i in range(0, meshCount):
					
					file.seek(16 + (i*4));
					
					offsetl = struct.unpack("<I", file.read(4))[0]
					
					
					file.seek(offsetl + 8)
					if mdVersion == 3:
						meshName = file.read(8)
						decodedMesh = meshName.decode("utf-8").strip("\x00")
					if mdVersion == 0:
						decodedMesh = str(i)
						
					PoseScaX = struct.unpack("<f", file.read(4))[0]
					PoseScaY = struct.unpack("<f", file.read(4))[0]
					PoseScaZ = struct.unpack("<f", file.read(4))[0]
					PoseRotX = struct.unpack("<f", file.read(4))[0]
					PoseRotY = struct.unpack("<f", file.read(4))[0]
					PoseRotZ = struct.unpack("<f", file.read(4))[0]
					PoseLocX = struct.unpack("<f", file.read(4))[0]
					PoseLocY = struct.unpack("<f", file.read(4))[0]
					PoseLocZ = struct.unpack("<f", file.read(4))[0]
					#allMCO.append((PoseLocX,PoseLocY,PoseLocZ,  PoseRotX,PoseRotY,PoseRotZ,  PoseScaX,PoseScaY,PoseScaZ))
					file.seek(offsetl)
					
					
					bl = struct.unpack("<i", file.read(4))[0]
					v1 = offsetl + bl

					
					file.seek(v1+10)
					subMeshCount = struct.unpack("<H", file.read(2))[0]
					
					
					
					
					file.seek(v1 + 28)
					MeshType = struct.unpack("<f", file.read(4))[0]
					if mdVersion == 0:
						MeshType = (MeshType * -1) + 1
					
					
					
					
					
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
								x = x * 0.01
								y = y * 0.01
								z = z * 0.01
								
								#print(str(x) + "    " + str(y) + " 	 OHYEAH")
							verts.append((x,y,z));
							indices.append(code);


						
						
						normals = []
						file.seek(normalOffset)
						
						def map_value(value, old_min, old_max, new_min, new_max):
							return (value - old_min) / (old_max - old_min) * (new_max - new_min) + new_min
						def map_signed_byte(value):
							return map_value(value, -128, 127, -1, 1)
						if normalOffset != 0:
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
						else:
							for i in range(0, VCount):  
								normals.append((1,1,1))
								
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
					
					
					mesh_object.rotation_euler[0] = PoseRotX
					mesh_object.rotation_euler[1] = PoseRotY
					mesh_object.rotation_euler[2] = PoseRotZ
					
					mesh_object.location.x = PoseLocX
					mesh_object.location.y = PoseLocY
					mesh_object.location.z = PoseLocZ
					
					mesh_object.scale.x = PoseScaX
					mesh_object.scale.y = PoseScaY
					mesh_object.scale.z = PoseScaZ
					
					

					
					#armature.rotation_euler[0] = PoseRotX
					#armature.rotation_euler[1] = PoseRotY
					#armature.rotation_euler[2] = PoseRotZ
					
					#armature.location.x = PoseLocX
					#armature.location.y = PoseLocY
					#armature.location.z = PoseLocZ
					
					#armature.scale.x = PoseScaX
					#armature.scale.y = PoseScaY
					#armature.scale.z = PoseScaZ
						

					
					
					
					
					
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
						
						if import_mat == True:
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
								#f = bm.faces.new([
								#bm.verts[len(bm.verts)-3],
								#bm.verts[len(bm.verts)-2],
								#bm.verts[len(bm.verts)-1]
								#])
								f = bm.faces.new([
								bm.verts[len(bm.verts)-3],
								bm.verts[len(bm.verts)-2],
								bm.verts[len(bm.verts)-1]
								])
								if import_mat == True:
								   f.material_index = material_index
								
							if MeshData[e][1][o] == 1:
								#f = bm.faces.new([
								#bm.verts[len(bm.verts)-2],
								#bm.verts[len(bm.verts)-3],
								#bm.verts[len(bm.verts)-1]
								#])
								f = bm.faces.new([
								bm.verts[len(bm.verts)-2],
								bm.verts[len(bm.verts)-3],
								bm.verts[len(bm.verts)-1]
								])
								if import_mat == True:
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
					if import_norm == True:
						mesh.normals_split_custom_set_from_vertices(normalAbs)
					uv_layer = mesh.uv_layers.new(name="UVMap")
					
					
					if import_vertc == True:
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
					
				MIRRORING_ARRAY = []
				file.seek(v1 + v2 + skeletonOffset)
				
				
				for i in range(0, skeletonCount):
					p1 = struct.unpack("<f", file.read(4))[0];
					p2 = struct.unpack("<f", file.read(4))[0];
					p3 = struct.unpack("<f", file.read(4))[0];
					if mdVersion == 3:
						ls = struct.unpack("<h", file.read(2))[0]
						MIRRORING_ARRAY.append(ls)
						parent = struct.unpack("<h", file.read(2))[0] + 1
					if mdVersion == 0:
						parent = struct.unpack("<i", file.read(4))[0] + 1
						
					new_bone = edit_bones.new(str(i+1))
					new_bone.head = Vector((p1, p2, p3))
					new_bone.tail = Vector((p1, p2 + 0.005297, p3))
					new_bone.head_radius = 0.1;
					new_bone.tail_radius = 0.05;
					new_bone.use_connect = False
					
					new_bone.parent = edit_bones[parent]
				
						
					
					new_bone.head += edit_bones[parent].head
					if new_bone.name != "root" and edit_bones[parent].name != "root":
						if not connect_bone:
							new_bone.tail += edit_bones[parent].head
						else:
							new_bone.tail += edit_bones[parent].head
							child_heads = [edit_bones[child.name].head for child in edit_bones[parent].children]
							if len(child_heads) > 1:
								median_point = mathutils.Vector((0.0, 0.0, 0.0))
								for head in child_heads:
									median_point += head
								median_point /= len(child_heads)
								edit_bones[parent].tail = median_point
							else:
								if len(child_heads) > 0:
									edit_bones[parent].tail = new_bone.head
									edit_bones[parent].roll = 0
					new_bone.roll = 0;  	

							  
				edit_bones = armature_data.edit_bones  
				if connect_bone:  
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
								
				bpy.ops.object.mode_set(mode='POSE')
				#edit_bones = armature_data.edit_bones  
				#for i in edit_bones:    
					#i.roll = 0
				pose_bones = armature.pose.bones
				
				
				for i in range(0,len(MIRRORING_ARRAY)):
					if MIRRORING_ARRAY[i] != -1:
						#print(MIRRORING_ARRAY[i])
						pose_bones[str(i + 1)]["B2MD_MIRRORLINK"] = str(MIRRORING_ARRAY[i] + 1) + '/////' + pose_bones[str(i + 1)].name
					#print(pose_bones[i])
					#pbone_s = pbones[bone[0].name]
					#print(pbone_s)
					#if "B2MD_MIRRORLINK" in pbone_s:
						
			else:
				self.report({'ERROR'}, f"The MD is not a MD file.")
				return {'CANCELLED'}
			

					 
					 
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='SELECT')
		#bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

		bpy.ops.object.select_all(action='DESELECT')

		bpy.context.object.show_in_front = True
		bpy.context.object.data.display_type = 'STICK'



		bpy.ops.object.mode_set(mode='EDIT')
		for bone in armature.data.edit_bones:
			#bone.roll = 0.0
			bpy.ops.armature.select_all(action='SELECT')
			bpy.ops.armature.roll_clear()
		bpy.ops.object.mode_set(mode='OBJECT')
def menu_func_import(self, context):
	self.layout.operator(
		ImportMD.bl_idname,
		text="Import God Hand Md ( .md / .scr )",
		icon='SNAP_VOLUME'
	)

class VIEW3D_PT_MDPanel2(Panel):
	bl_label = "Blen2MD Utility"
	bl_idname = "VIEW3D_PT_MDP2"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'MD'
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		l1 = layout.box()
		l1.label(text="MD Utility", icon='MODIFIER');
		
		boxIF = l1.box()
		if os.path.isfile(context.scene.md_input):
			boxIF.operator("import_scene_imediate.md", text="Import MD from Ref", icon='MATCUBE')
		else:
			boxIF.operator("import_scene.md", text="Import MD from Ref", icon='MATCUBE')

		#if context.scene.input:
			  #boxIF.operator("object.skeleton", text="Load skeleton from reference", icon='RNA')
			  
			  
		boxIF.operator("object.amo", text="Apply deform modifiers", icon='MESH_DATA')
		boxIF.separator()
		
		
		
		#boxIF.prop(scene, "branch_size")
		#boxIF.prop(scene, "branch_lookup_size")
		boxIF.prop(context.scene,"lookup_size") 
		boxIF.operator("object.sorbranch", text="Initialize triangle branch sorter", icon='MESH_DATA')
		boxIF.operator("object.unusmat", text="Remove unused materials", icon='MATERIAL')
		
		
		
		if bpy.context.mode == "EDIT_MESH":
			active_obj = bpy.context.active_object
			
			if active_obj:
				typ="Bytes" #light like a feather
				if active_obj.type == "MESH":
					boxIF.label(text="Input info:")
					mesh = bmesh.from_edit_mesh(active_obj.data)
				   
					lto = boxIF.split()
					lto.label(text="Vertice count: " + str(len(mesh.verts)))
					lto.label(text="Face count: " + str(len(mesh.faces)))
					boxIF.prop(context.scene,"nerdStats")
					boxIF.separator()

				   
					mesh.faces.ensure_lookup_table()
					vval = getNumberFList(mesh.faces)
				   
					if vval >= 1024.0:
						vval = vval / 1024.0
						typ = "KB" #yup, sounds about right
					if vval >= 1024.0:
						vval = vval / 1024.0
						typ = "MB" #huge but ok?
					if vval >= 1024.0:
						vval = vval / 1024.0
						typ = "GB" #wtf
					if vval >= 1024.0:
						vval = vval / 1024.0
						typ = "TB" #dude, what the fuck are you doing
					boxIF.label(text=f"Estimated mesh size:  {vval:.2f} {typ}")
					if context.scene.nerdStats == True:
						

						boxIF.label(text=f"Present materials:")
						tll = boxIF.box()
						
						
						errored = False
						faces_with_material = []
						try:
							faces_with_material = getFacesAndMaterials(active_obj,self,mesh)
							for pll in faces_with_material:
								tll.label(text=f"Material \"{pll[1].name}\"",icon="MATERIAL")

							
							
						except Exception:
							errored = True
							tll.label(text=f"A INVALID MATERIAL IS PRESENT ON THIS MESH",icon="CANCEL")
							tll.label(text=f"Possible causes:")
							tll.label(text=f"A material slot wasnt properly created.")
							tll.label(text=f"A material on this mesh doesnt have any Face assigned.")   	
							
							
							
						
						boxIF.label(text="SFC Status:")
						gbo = boxIF.box()
						if errored:
							gbo.label(text="INV_MAT_SETTI")
						
						
						
						#tlis = getConnects(mesh)
						for n in faces_with_material:
							tlis = getConnectsMD(n[0])
							facec = 0
							for nani in range(0,len(tlis)):
								stairCase(tlis[nani])
								#print("--------------")
								for kh in range (0,len(tlis[nani])):
									ico = "LINKED"
									if kh == 0:
										ico = "UNLINKED"
										
									splt = gbo.split()
									
									splt.label(text=f"Face {str(facec)}   {str(tlis[nani][kh])}",icon=ico)
									splt.label(text=f"Assigned to \"{n[1].name}\"",icon="MATERIAL")
									facec += 1
							
							

#this perfectly matches with the tri stripping  
def stairCase(vertices):


	mainSeq = [vertices[0][0], vertices[0][1], vertices[0][2]]

	if len(vertices) > 1:
		def FCO(c,j,curr):
			histc = []
			v1 = curr
			v2 = [vertices[c+1][0], vertices[c+1][1], vertices[c+1][2]]
			v3 = [vertices[c+2][0], vertices[c+2][1], vertices[c+2][2]]
			histc.extend(v1)
			histc.extend(v2)
			histc.extend(v3)

			return histc.count(v1[j])



		refSeq = [vertices[1][0], vertices[1][1], vertices[1][2]]


		UIM = [x for x in mainSeq if x not in refSeq]
		#RIB = [x for x in mainSeq if x in refSeq]
		URIB = [x for x in mainSeq if x in refSeq]



		RIB = []
		retList = []
		
		if len(vertices) == 2:
			#print("well, this is awkward.....")


			UNI = [x for x in vertices[0] if x not in vertices[1]]
			CONJ = [x for x in vertices[0] if x in vertices[1]]
			CONJ.sort()
			
			FirstTriangle = [UNI[0],CONJ[0],CONJ[1]]
			
			UNI = [x for x in vertices[1] if x not in vertices[0]]
			
			
			retList.append(FirstTriangle)
			retList.append([CONJ[0],CONJ[1],UNI[0]])
			#print("OG:")
			#for i in vertices:
			#   print(i)
			#print("REORD:")
			#for i in retList:
			#   print(i)
			return retList
		
		
		
		
		if len(vertices) > 2:
			vt2 = FCO(0,0,URIB)
			vt3 = FCO(0,1,URIB)
			if vt2 > vt3:
				RIB.append(URIB[1])
				RIB.append(URIB[0])
			else:
				RIB.append(URIB[0])
				RIB.append(URIB[1])
				
			#print(mainSeq)
			#print("------")
			FirstTriangle = [UIM[0],RIB[0],RIB[1]]
			retList.append(FirstTriangle)
			
			for i in range(1,len(vertices)):
				UNI = [x for x in vertices[i] if x not in retList[len(retList)-1]]
				retList.append([retList[len(retList)-1][1],retList[len(retList)-1][2],UNI[0]])
		
		
		#print(FirstTriangle)
		#print([vertices[1][0], vertices[1][1], vertices[1][2]])
		#print([vertices[2][0], vertices[2][1], vertices[2][2]])
		#print([vertices[3][0], vertices[3][1], vertices[3][2]])
		
		#print("OG:")
		#for i in vertices:
		#   print(i)
		#print("REORD:")
		#for i in retList:
		#   print(i)
		return retList
		
		




	else:
		return [mainSeq]


	
def getConnects(mesh):
	ret = []
	
	cur = []
	
	hist = []
	for face in range(0,len(mesh.faces)): 
		should_separate = False
		def getArray(GET_FACE):
			return [v.index for v in GET_FACE.verts]
		
		hist.append(mesh.faces[face])
		v3 = getArray(mesh.faces[face])
		v2 = getArray(mesh.faces[face])
		if len(hist) > 3:
			history = []
			v3 = getArray(hist[len(hist)-1])
			v2 = getArray(hist[len(hist)-2])
			v1 = getArray(hist[len(hist)-3])
			v0 = getArray(hist[len(hist)-4])
			history.extend(v3)
			history.extend(v2)
			history.extend(v1)
			history.extend(v0)
			for idx in v3:
				if history.count(idx) > 3:
					should_separate = True
					break
		v3.sort()
		
		
		


		fc0 = getArray(mesh.faces[face])
		if face == 0:
			fc1 = getArray(mesh.faces[face+1])
		else:
			fc1 = getArray(mesh.faces[face-1])
			
		common = list(set(fc0) & set(fc1))
		unique = list(set(fc0) - set(fc1))
		common.sort()
		unique.sort()

		if should_separate:
			ret.append(cur)
			cur = [v3]
			hist = []
			#gbo.label(text="Face " + str(mesh.faces[face].index) + "  " + str(v3),icon="UNLINKED")
		else:
			
			if len(common) > 1 and len(common) != 3:
				if face == 0:
					#gbo.label(text=f"Face {str(mesh.faces[face].index)}   {str(joint)}",icon="LINKED")
					cur.append(v3)
				else:
					cur.append(v3)
					#gbo.label(text=f"Face {str(mesh.faces[face].index)}   {str(joint)}",icon="LINKED")
			else:
				#gbo.label(text=f"Face {str(mesh.faces[face].index)}   {str(v3)}",icon="UNLINKED")
				ret.append(cur)
				cur = [v3]

	ret.append(cur)
	return ret
	
	
	
	
	
	
def getNumber(bm):
	retCount = 2 #starts with two verts
	hist = []
	lastFace = bm.faces[0]
	for face in range(0,len(bm.faces)): 
		hist.append(bm.faces[face])
		should_separate = False
		def getArray(GET_FACE):
			return [v.index for v in GET_FACE.verts]
	
		curf = bm.faces[face]
		v3 = getArray(curf)
		v2 = getArray(curf)
		if len(bm.faces) > 3:
			history = []
			v3 = getArray(bm.faces[face-0])
			v2 = getArray(bm.faces[face-1])
			v1 = getArray(bm.faces[face-2])
			v0 = getArray(bm.faces[face-3])
			history.extend(v3)
			history.extend(v2)
			history.extend(v1)
			history.extend(v0)

			for idx in v3:
				if history.count(idx) > 3:
					should_separate = True
					break

									   
								   
								   
		v3.sort()
		
		fc0 = getArray(bm.faces[face])
		#if face == 0:
		if face == 0:
			fc1 = getArray(bm.faces[face+1])
		else:
			fc1 = getArray(bm.faces[face-1])
								
								
		common = list(set(fc0) & set(fc1))
		unique = list(set(fc0) - set(fc1))
		common.sort()
		unique.sort()


		if should_separate:
			retCount = retCount + 3
			hist = [curf]
		else:
			if len(common) > 1 and len(common) != 3:
				retCount = retCount + 1
			else:
				retCount = retCount + 3
				hist = [curf]
							   
		lastFace = face
	return (32*2) + (retCount * 16) + ((retCount * 4) * 3) + (retCount * 8)

	
	
class VIEW3D_PT_MDPanel3(Panel):
	bl_label = "Blen2MD Vertex Utility"
	bl_idname = "VIEW3D_PT_MDP3"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'MD'
	def draw(self, context):
		layout = self.layout
		scene = context.scene 
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
		b1.operator("object.unus", text="Delete all unusued vert groups", icon='GROUP')
		


class OBJECT_OT_MirrorLink(Operator):
	bl_label = ""
	bl_idname = "object.mrrlnk"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'MD'
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Creates a mirror link between all bones on this skeleton, rendering blender's mirroring pose bone functionality available"
	
	@classmethod
	def poll(cls, context):
		active_object = context.active_object  
		return active_object is not None and active_object.type == "ARMATURE"
		
	
	def execute(self, context):
		bpy.ops.object.mode_set(mode='POSE')
		active_object = context.active_object  
		pbones = active_object.pose.bones	
		codes = []
		skip = []
		for i in pbones:
			if i not in skip:
				if "B2MD_MIRRORLINK" in i:

					t1 = i["B2MD_MIRRORLINK"]
					bn = pbones[t1.split('/////')[0]]
					if bn:
						if "B2MD_MIRRORLINK" in bn:
							t2 = bn["B2MD_MIRRORLINK"]
							if t2.split('/////')[0] == i.name:
								
								skip.append(bn)
		for i in skip:
			codes.append(i["B2MD_MIRRORLINK"])
		for i in codes:
			b1 = pbones[i.split('/////')[0]]
			b2 = pbones[i.split('/////')[1]]

			bn1 = b1.name
			bn2 = b2.name 
			
			b1.name = bn1 + "_" + bn2 + ".left"
			b2.name = bn1 + "_" + bn2 + ".right"
			
			print(b1, "     ", b2)
		return {'FINISHED'}
class OBJECT_OT_MirrorUnLink(Operator):
	bl_label = ""
	bl_idname = "object.mrrulnk"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'MD'
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Reverts all previous links to the default skeleton"
	
	@classmethod
	def poll(cls, context):
		active_object = context.active_object  
		return active_object is not None and active_object.type == "ARMATURE"
		
	
	def execute(self, context):
		bpy.ops.object.mode_set(mode='POSE')
		active_object = context.active_object  
		pbones = active_object.pose.bones	
		codes = []
		for i in pbones:
			if "B2MD_MIRRORLINK" in i:
				i.name = i["B2MD_MIRRORLINK"].split('/////')[1]
				
		return {'FINISHED'}
	
class VIEW3D_PT_MDPanel4(Panel):
	bl_label = "Blen2MD Skeleton"
	bl_idname = "VIEW3D_PT_MDP4"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'MD'
	@classmethod
	def poll(cls, context):
		active_object = context.active_object  
		return active_object is not None and active_object.type == "ARMATURE"
	#skeleton_mirror_ids = ["",""]
	def draw(self, context):
		layout = self.layout
		scene = context.scene 


		layout.label(text="Naming:")
		layout.operator("object.rename_skel", text="Rename skeleton using Index", icon='BONE_DATA')
		layout.separator()
		layout.separator()
		layout.label(text="Operations:")
		boxIF2 = layout.box()
		
		

		
		
		
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
		layout.separator()  
		
		
		
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
		
		

		
		
		layout.separator()
		
		layout.label(text="Mirroring Operations:",icon="MOD_MIRROR") 
		layout.operator("object.mrrlnk", text="Create mirror links", icon='OUTLINER_OB_ARMATURE')
		layout.operator("object.mrrulnk", text="Revert mirror links", icon='OUTLINER_OB_ARMATURE')
		
		layout.separator()
		layout.label(text="Current armature bones: ",icon="ARMATURE_DATA") 
		l1 = layout.box()

		active_object = context.active_object  
		bones = active_object.data.bones
		pbones = active_object.pose.bones	
		for bone in bones:
			parseable = -99999
			try:
				parseable = int(bone.name)
			except:
				#print("")
				yeahhhhhhhhhhhhhhherror = "lol"

			additive = ""
			tis_bone_is_new = False
			if "NEWBONE" in active_object:
					newbone_list = list(active_object["NEWBONE"])
					if parseable in newbone_list:
						tis_bone_is_new = True
						additive = "* "
			
			MIRROR_BONE = "Have no mirror bone set."
			#MODICO = "EVENT_X"
			MODICO = "SEQUENCE_COLOR_09"
			if "B2MD_MIRRORLINK" in pbones[bone.name]:
				MIRROR_BONE = "mirrors bone " + pbones[bone.name]["B2MD_MIRRORLINK"].split('/////')[0]
				#MODICO = "MOD_MIRROR"
				#MODICO = "EVENT_OS"
				MODICO = "SEQUENCE_COLOR_05"
				
				
			if bone.parent:
				wre = l1.box()
				vvv = wre.split()
				
				
				
				
				if parseable != -99999:
					vvv.label(text=f"{additive}{bone.name} | Child of: {bone.parent.name}",icon="SEQUENCE_COLOR_04")
				else:
					vvv.label(text=f"{additive}{bone.name} Not compatible.",icon="SEQUENCE_COLOR_01")

				op = vvv.operator("object.add_bone",text="Add Children")
				op.node = bone.name
				op.lmode = True
				op = vvv.operator("object.add_bone",text="Add Parent")
				op.node = bone.name
				op.lmode = False
				op = vvv.operator("object.delete_bone")
				op.node = bone.name
				
				
				vvv = wre.split()
				vvv.label(text=f"{additive}{bone.name} {MIRROR_BONE}",icon=MODICO)
				op = vvv.operator("object.sbonm", text="Set selected bone as a mirror bone", icon="CON_ARMATURE")
				op.node = bone.name
				op = vvv.operator("object.sbonmd", text="Remove linked mirror bone", icon="CON_ARMATURE")
				op.node = bone.name
				l1.separator()
			else:
				wre = l1.box()
				vvv = wre.split()
				if parseable != -99999:
					vvv.label(text=f"{additive}{bone.name} | Child of: No parent",icon="SEQUENCE_COLOR_04")
					op = vvv.operator("object.add_bone",text="Add Children")
					op.node = bone.name
					op.lmode = True
				else:
					if bone.name != "root":
						vvv.label(text=f"Bone \"{bone.name}\" Not compatible for exporting.",icon="SEQUENCE_COLOR_01")
						op = vvv.operator("object.delete_bone")
						op.node = bone.name
					else:
						vvv.label(text=f"{additive}{bone.name} | Child of: No parent",icon="SEQUENCE_COLOR_04")
						op = vvv.operator("object.add_bone",text="Add Children")
						op.node = bone.name
						op.lmode = True
				l1.separator()
				vvv = wre.split()
				vvv.label(text=f"{additive}{bone.name} {MIRROR_BONE}",icon=MODICO)
				op = vvv.operator("object.sbonm", text="Set selected bone as a mirror bone", icon="CON_ARMATURE")
				op.node = bone.name
				
				op = vvv.operator("object.sbonmd", text="Remove linked mirror bone", icon="CON_ARMATURE")
				op.node = bone.name

class OBJECT_OT_MirrorDel(Operator):
	bl_label = ""
	bl_idname = "object.sbonmd"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'MD'
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Removes the linked mirror bone from the selected bone (if any)"
	node: bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		active_object = context.active_object  
		return active_object is not None and active_object.type == "ARMATURE"
		
	
	def execute(self, context):
		#print("wawa")
		
		active_object = context.active_object  
		bones = active_object.pose.bones
		selected_bones = [bone for bone in active_object.pose.bones if bone.bone.select]
		print(bones[self.node])
		if bones[self.node]:
			if "B2MD_MIRRORLINK" in bones[self.node]:
				del bones[self.node]["B2MD_MIRRORLINK"]
	
		return {'FINISHED'}
class OBJECT_OT_MirrorBone(Operator):
	bl_label = ""
	bl_idname = "object.sbonm"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'MD'
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Defines if the bone can have mirrored motions with another bone"
	node: bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		active_object = context.active_object  
		return active_object is not None and active_object.type == "ARMATURE"
		
	
	def execute(self, context):
		#print("wawa")
		
		active_object = context.active_object  
		bones = active_object.pose.bones
		selected_bones = [bone for bone in active_object.pose.bones if bone.bone.select]
		print(bones[self.node])
		if bones[self.node]:
			if bones[self.node].name != selected_bones[0].name:
				bones[self.node]["B2MD_MIRRORLINK"] = selected_bones[0].name + '/////' + pose_bones[str(i + 1)].name
				
				if "B2MD_MIRRORLINK" in selected_bones[0]:
					last_val = selected_bones[0]["B2MD_MIRRORLINK"]
					selected_bones[0]["B2MD_MIRRORLINK"] = pose_bones[str(i + 1)].name + '/////' + selected_bones[0].name
					
					
					vn = active_object.pose.bones[last_val.split('/////')[0]]
					if "B2MD_MIRRORLINK" in vn:
						del vn["B2MD_MIRRORLINK"]
				else:
					selected_bones[0]["B2MD_MIRRORLINK"] = pose_bones[str(i + 1)].name + '/////' + selected_bones[0].name
			else:
				self.report({'ERROR'}, f"Can't assign a mirror bone if they're the same.")
				return {'CANCELLED'}
		return {'FINISHED'}
	
	
	
class OBJECT_OT_UnusMat(Operator):
	bl_label = ""
	bl_idname = "object.unusmat"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'MD'
	bl_options = {'REGISTER', 'UNDO'}
	bl_description = "Removes all unused materials from the selected mesh (UNUSED meaning the material has NO VERTICES assigned on it or INVALID materials)"
	
	node: bpy.props.StringProperty()
	@classmethod
	def poll(cls, context):
		active_object = context.active_object  
		return active_object is not None
	
	def execute(self, context):
		obj = context.active_object
		bpy.ops.object.mode_set(mode='EDIT')
		
		bm = bmesh.new()
		bm.from_mesh(obj.data)
		
		
		
		
		
		materials = obj.data.materials
		if materials:
			ALLMATS = []
			

			if ALLMATS == []:
				for i, material in enumerate(materials):
					leMat = []

					try:
						tl1 = material.name
						#print(tl1)
					except Exception as e:
						#obj.data.materials.pop(index=i)
						ALLMATS.append(material.name)
						
					for face in bm.faces:
						if face.material_index == i:
							for vert in face.verts:
								leMat.append(vert)
							
					#print(len(leMat))
					if len(leMat) == 0:
						ALLMATS.append(material.name)
			
			for nn in ALLMATS:
				for i, material in enumerate(materials):
					if material.name == nn:
						obj.data.materials.pop(index=i)
						materials = obj.data.materials
						break
		else:
			self.report({'ERROR'}, f"No materials assigned to {obj.name}")
			return {'CANCELLED'}
		
		

	



		
		bpy.ops.object.mode_set(mode='OBJECT')
		return {'FINISHED'}
		
		
class OBJECT_OT_AddBone(Operator):
	bl_idname = "object.add_bone"
	bl_label = ""
	bl_description = "creates a bone that's either parent or children of the selected bone"
	bl_options = {'REGISTER', 'UNDO'}
	node: bpy.props.StringProperty()
	lmode: bpy.props.BoolProperty()
	def execute(self, context):
		bpy.ops.object.mode_set(mode='EDIT')
		print(self.lmode)
		allbnames = []
		active_object = context.active_object
		bones = active_object.data.bones
		for bone in bones:
			parseable = -99999
			try:
				parseable = int(bone.name.replace("root","-99"))
			except:
				print("")
			if parseable != -99999:
				allbnames.append(parseable)

		allbnames.sort()
		print(allbnames)

		relative = active_object.data.edit_bones.get(self.node)
		
		new_bone = active_object.data.edit_bones.new(str(allbnames[-1]+1))

		if "NEWBONE" in active_object:
			newbone_list = list(active_object["NEWBONE"])
			newbone_list.append(allbnames[-1] + 1)
			active_object["NEWBONE"] = newbone_list
		else:
			active_object["NEWBONE"] = [allbnames[-1]+1]



		if self.lmode == True: #add as children
			new_bone.parent = relative
		else:
			new_bone.parent = relative.parent
			relative.parent = new_bone
	
	
		new_bone.head = (0, 0, 0)
		new_bone.tail = (0, 0.005297, 0)
		new_bone.roll = 0
		bpy.ops.object.mode_set(mode='OBJECT')
		return {'FINISHED'}
class OBJECT_OT_DeleteBone(Operator):
	bl_idname = "object.delete_bone"
	bl_label = "Delete this bone"
	bl_description = "deletes the selected bone"
	bl_options = {'REGISTER', 'UNDO'}
	node: bpy.props.StringProperty()
	def execute(self, context):
		print("huh??????????????")
		print(self.node)
		
		bpy.ops.object.mode_set(mode='EDIT')


		active_object = context.active_object  
		bone = active_object.data.edit_bones.get(self.node)

		parseable = -99999
		try:
			parseable = int(bone.name.replace("root","-99"))
		except:
			print("")
		if parseable != -99999:
	
			if "NEWBONE" in active_object:
				newbone_list = list(active_object["NEWBONE"])
				if parseable in newbone_list:
					newbone_list.remove(parseable)
				active_object["NEWBONE"] = newbone_list
				if len(newbone_list) == 0:
					del active_object["NEWBONE"]





		if bone:
			active_object.data.edit_bones.remove(bone)


		bpy.ops.object.mode_set(mode='OBJECT')
		return {'FINISHED'}
class VIEW3D_PT_MDPanel6(Panel):
	bl_label = "Blen2MD Export"
	bl_idname = "VIEW3D_PT_MDP6"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = 'MD'
	def draw(self, context):
		layout = self.layout
		scene = context.scene 
		l1 = layout.box()
		l1.label(text="MD Tools", icon='EXPORT')
		boxEP = l1.box()
		boxEP.operator("object.export_action_md_part", text="Export Mesh to MD", icon='PLAY')
		   
		   
		#if context.scene.md_input:
		boxEP.operator("object.export_action_md", text="Export Model to MD", icon='PLAY')
def get_child_meshes_recursive(obj):
	meshes = []
	for child in obj.children:
		if child.type == 'MESH':
			meshes.append(child)
		meshes.extend(get_child_meshes_recursive(child))
	return meshes
class OBJECT_OT_Branch(bpy.types.Operator):
	bl_idname = "object.sorbranch"
	bl_label = "Utility"
	bl_description = "Sorts face indice by branches, it can decrease the size of a model considerably, but can take a long time to finish depending on the model face count"

	#@classmethod
	#def poll(cls, context):
	#   return bpy.context.mode == "EDIT_MESH"

	def execute(self, context):
		obj = bpy.context.object
		if obj and obj.type != 'MESH':
			self.report({'ERROR'}, f"No mesh selected.")
			return {'FINISHED'}
		bpy.ops.object.mode_set(mode='EDIT')
		me = obj.data
		bm = bmesh.from_edit_mesh(me)
		
		
		bm.faces.ensure_lookup_table()
		
		
		currentFace = bm.faces[0] #get the first face
		mat_index = currentFace.material_index
		selMat = None

		if mat_index < len(obj.data.materials):
			selMat = obj.data.materials[mat_index]
		#print(selMat.name)




		faces_with_material = getFacesAndMaterials(obj,self,bm)
		for l in range(0, len(faces_with_material)):
			if faces_with_material[l][1].name == selMat.name:
				h = faces_with_material[l]
				a = faces_with_material[0]
				faces_with_material[0] = h
				faces_with_material[l] = a
		
		




		def MASTER_OP(REFFACE):
			currentFace = REFFACE
			
			
			allfaces = []
			#for i in bm.faces:
			for i in iterator[0]:
				if i != currentFace:
					allfaces.append(i)

			def get_uv_edges(face, uv_layer):
				uv_edges = set()
				loops = face.loops
				for i, loop in enumerate(loops):
					uv1 = tuple(loop[uv_layer].uv)
					uv2 = tuple(loops[(i + 1) % len(loops)][uv_layer].uv)
					edge = tuple(sorted([uv1, uv2]))
				uv_edges.add(edge)
				return uv_edges
			def faces_share_uv_edge(face_a, face_b, uv_layer):
				uv_edges_a = get_uv_edges(face_a, uv_layer)
				uv_edges_b = get_uv_edges(face_b, uv_layer)
				return not uv_edges_a.isdisjoint(uv_edges_b)

		
			
			
			allHist = []
			def GetConnectand(REF_FACE, HIST_LIST):
				all_paths = []
				
				# Append the current face to the traversal history
				HIST_LIST.append(REF_FACE)
				uv_layer = bm.loops.layers.uv.active
				
				
				direct_neighbors = []
				for edge in REF_FACE.edges:
					for linked_face in edge.link_faces:
						if linked_face in iterator[0]:
							if linked_face != REF_FACE and linked_face not in HIST_LIST and linked_face not in allHist:
								
								#print(faces_share_uv_edge(linked_face, REF_FACE, uv_layer))
								
								
								if faces_share_uv_edge(linked_face, REF_FACE, uv_layer):
								
									to_add = True

									if len(HIST_LIST) > 3:
										def getArray(GET_FACE):
											return [v.index for v in GET_FACE.verts]

										history = []
										v3 = getArray(linked_face)
										v2 = getArray(HIST_LIST[-1])
										v1 = getArray(HIST_LIST[-2])
										v0 = getArray(HIST_LIST[-3])
										history.extend(v0)
										history.extend(v1)
										history.extend(v2)
										history.extend(v3)

										for idx in v3:
											if history.count(idx) > 3:
												to_add = False
												break

									if to_add:
										direct_neighbors.append(linked_face)

				# Recursive case
				if direct_neighbors:
					for neighbor in direct_neighbors:
						# Recursively call with a COPY of the current history
						result_paths = GetConnectand(neighbor, HIST_LIST[:])
						all_paths.extend(result_paths)
				else:
					# No more valid neighbors, this path is complete
					all_paths.append(HIST_LIST[:])
				return all_paths



			def GetBestBranch(REF_FACE,UTILIZED_FACES):
				allp = GetConnectand(REF_FACE,UTILIZED_FACES)
				allp.sort(key=len, reverse=True)
				return allp[0]
			HIS=[]
			USED_FACES = []
			f1 = GetBestBranch(currentFace,HIS)
			USED_FACES.extend(f1)
			allHist.extend(f1)


			#print(len(USED_FACES))
			for i in iterator[0]:
				if i not in USED_FACES:
					HIS=[]
					vtall = GetBestBranch(i,HIS)
					USED_FACES.extend(vtall)
					allHist.extend(vtall)
			return USED_FACES
		

		#print(faces_with_material)
		AllBestFaces = []
		for iterator in faces_with_material:
			
			clen = context.scene.lookup_size
			RetFaces = []
			if clen < len(iterator[0]):
				for k in range(0,clen):
					RetFaces.append([MASTER_OP(iterator[0][k]),getNumberFList(MASTER_OP(iterator[0][k]))])
					#print(getNumberFList(MASTER_OP(iterator[0][k])))
			else:
				for k in range(0,len(iterator[0])):
					#print(getNumberFList(MASTER_OP(iterator[0][k])))
					RetFaces.append([MASTER_OP(iterator[0][k]),getNumberFList(MASTER_OP(iterator[0][k]))])


			sortes = sorted(RetFaces, key=lambda x: x[1])
			AllBestFaces.extend(sortes[0][0])
				
		#print(sortes[0][1],sortes[len(sortes)-1][1])

			
		#print("BEESTAFACES",len(AllBestFaces))
		
		print(getNumberFList(bm.faces), "    ", getNumberFList(AllBestFaces))
		
		for i in range(0,len(AllBestFaces)):
			AllBestFaces[i].index = i
		bm.faces.sort()
		bmesh.update_edit_mesh(me)



			#for i in bm.faces:
			#    FaceBranch = GetBestBranch(currentFace,HISTORY_LIST)




		#bpy.ops.object.mode_set(mode='OBJECT')
		return {'FINISHED'}
	
def getFacesAndMaterials(obj,self,bm):
	materials = obj.data.materials
	faces_with_material = []
	if materials:
		for i, material in enumerate(materials):
			leMat = []
			try:
				tl1 = material.name
				tl2 = obj.name
			except Exception as e:
				self.report({'ERROR'}, "The mesh \"" + obj.name + "\" contains a invalid material.")
				return {'CANCELLED'}
				
			for face in bm.faces:
				if face.material_index == i:
					leMat.append(face)
			if len(leMat) == 0:
				self.report({'ERROR'},  "The material \"" + material.name + "\" is assigned in mesh \"" + obj.name+"\", but does not contain any triangle assigned.\n Consider removing the material from the mesh, or assigning a triangle on it.")
				return {'CANCELLED'}
			faces_with_material.append([leMat,material])
	else:
		self.report({'ERROR'}, f"No materials assigned to {obj.name}")
		return {'CANCELLED'}
	return faces_with_material
def getNumberFList(faces):
	retCount = 2 #starts with two verts
	hist = []
	lastFace = faces[0]
	for face in range(0,len(faces)): 
		hist.append(faces[face])
		should_separate = False
		def getArray(GET_FACE):
			return [v.index for v in GET_FACE.verts]
	
	
		curf = faces[face]
		v3 = getArray(curf)
		v2 = getArray(curf)
		if len(faces) > 3:
			history = []
			v3 = getArray(faces[face-0])
			v2 = getArray(faces[face-1])
			v1 = getArray(faces[face-2])
			v0 = getArray(faces[face-3])
			history.extend(v3)
			history.extend(v2)
			history.extend(v1)
			history.extend(v0)

			for idx in v3:
				if history.count(idx) > 3:
					should_separate = True
					break

									   
								   
								   
		v3.sort()
		
		fc0 = getArray(faces[face])
		#if face == 0:
		if face == 0:
			fc1 = getArray(faces[face+1])
		else:
			fc1 = getArray(faces[face-1])
								
								
		common = list(set(fc0) & set(fc1))
		unique = list(set(fc0) - set(fc1))
		common.sort()
		unique.sort()


		if should_separate:
			retCount = retCount + 3
			hist = [curf]
		else:
			if len(common) > 1 and len(common) != 3:
				retCount = retCount + 1
			else:
				retCount = retCount + 3
				hist = [curf]
							   
		lastFace = face
	return (32*2) + (retCount * 16) + ((retCount * 4) * 3) + (retCount * 8)
	
	
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
									if group_b:
										for vert_index, weight in group_data.items():
											group_b.add([vert_index], weight, type='ADD')
										objc.vertex_groups.remove(group_a)
									else:
										vertex_group = objc.vertex_groups.new(name=str(active_bone.name))
										for vert_index, weight in group_data.items():
											vertex_group.add([vert_index], weight, type='REPLACE')
										objc.vertex_groups.remove(group_a)
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
				bpy.ops.object.mode_set(mode='POSE')
				
				
				constraints = []
				for bone_a in arm1.pose.bones:
					bone_b = arm2.pose.bones.get(bone_a.name)
					print(str(bone_a.name))
					if bone_b:
						print("WTF")
						constraint = bone_b.constraints.new(type='COPY_LOCATION')
						constraint.target = arm1
						constraint.subtarget = bone_a.name
						constraints.append((bone_b,constraint,arm2))
				context.scene.SK = ""
				bpy.ops.pose.armature_apply(selected=False)
				for bones in constraints:
					matrix_final = bones[2].matrix_world @ bones[0].matrix
					bones[0].constraints.remove(bones[1])
					
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

	@classmethod
	def poll(cls, context):
		active_object = context.active_object  
		return active_object is not None and bpy.context.mode == "OBJECT" and active_object.type == "ARMATURE"


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
	
	

	def draw(self, context):
		layout = self.layout

		layout.label(text="Blen2MD Setup")
		layout.prop(self, "exe_path")
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

	@classmethod
	def poll(cls, context):
		active_object = context.active_object  
		return active_object is not None and bpy.context.mode == "OBJECT" and active_object.type == "MESH"
	def execute(self, context):
		bpy.ops.object.vertex_group_limit_total(limit=3)
		return {'FINISHED'}    
classes = [
    OBJECT_OT_ExportMD,
    OBJECT_OT_ExportMDPart,
    VIEW3D_PT_MDPanel2,
    VIEW3D_PT_MDPanel3,
    VIEW3D_PT_MDPanel4,
    VIEW3D_PT_MDPanel6,
    OBJECT_OT_RenameSkeleton,
    OBJECT_OT_Unus,
    OBJECT_OT_Merge,
    OBJECT_OT_ResetMerge,
    Blen2MDPreferences,
    OBJECT_OT_SetArmature,
    OBJECT_OT_ClearArmature,
    OBJECT_OT_ApllyMo,
    OBJECT_OT_Limit,
    ImportMD,
    ImportMDImediate,
    OBJECT_OT_SetArmatureToName,
    OBJECT_OT_ClearArmatureName,
    OBJECT_OT_Branch,
    OBJECT_OT_DeleteBone,
    OBJECT_OT_AddBone,
    OBJECT_OT_UnusMat,
    OBJECT_OT_MirrorBone,
    OBJECT_OT_MirrorDel,
    OBJECT_OT_MirrorLink,
    OBJECT_OT_MirrorUnLink,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

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
    bpy.types.Scene.md_input = StringProperty(
        name="",
        description="Path to the Md you're using as reference of modding",
        default="C:/Users/",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.console_md_output = BoolProperty(
        name="See Output",
        description="Check this if you want to see the program output once you export the model, in case the file isn't working, etc..",
        default=False
    )
    bpy.types.Scene.lookup_size = IntProperty(
        name="Lookup Size",
        description="How many face checks the branch sorter should use to determine the best branch (per material on the mesh)",
        default=50
    )
    bpy.types.Scene.nerdStats = BoolProperty(
        name="Activate nerd stats",
        description="If you're creating the SFC, Enabling this is recommended",
        default=False
    )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


    del bpy.types.Scene.console_md_output
    del bpy.types.Scene.md_input
    del bpy.types.Scene.VGroup
    del bpy.types.Scene.SK
    del bpy.types.Scene.SKN
    del bpy.types.Scene.lookup_size
    del bpy.types.Scene.nerdStats
if __name__ == "__main__":
	register()