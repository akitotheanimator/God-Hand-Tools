bl_info = {
    "name": "Blen2Seq",
    "blender": (3, 6, 0),
    "category": "3D View",
    "author": "Akito",
    "version": (1, 0, 0),
    "description": "Export Markers directly to SEQ",
    "tracker_url": "https://github.com/akitotheanimator/God-Hand-Tools/tree/main",
}


import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty,CollectionProperty, IntProperty,EnumProperty
from bpy.types import Panel, Operator,OperatorFileListElement,PropertyGroup
from bpy_extras.io_utils import ImportHelper,ExportHelper
import os
import re
import struct
from bl_ui.properties_paint_common import UnifiedPaintPanel
from enum import Enum



class OBJECT_OT_FrameUpdateOperator_seq(Operator):
    bl_idname = "object.frame_update_operator"
    bl_label = "Update Frame"

    def execute(self, context):
        # This will call the draw method directly when the operator runs
        return {'FINISHED'}
    
    
class VIEW3D_PT_SEQPanel(Panel):
    #bl_idname = "object.frame_update_operator"
    bl_label = "SEQ"
    bl_idname = "VIEW3D_PT_SEQ_PANEL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SEQ'
    
        
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object
        
        

        layout.operator("object.import_seq_file_seq")
        layout.operator("object.delete_sequences_seq")
        layout.operator("object.add_event_seq")
        layout.operator("object.export_seq")
        layout.label(text=str(scene.seqname))
        
        if obj != None:
          
          layout.separator()
          layout.prop(scene,"simulate_seq")
          
          if scene.simulate_seq == True:
              layout.prop(scene,"show_type_seq")
              
              
              prop_names = list(obj.keys())
              
              layout.label(text="Frame: " +str(scene.frame_current))
              layout.separator()
              vatq = layout.box()
              
              
              stri = ""
              for prop_name in prop_names:
                  if "SEQ" in prop_name:
                    if scene.show_type_seq==False:
                      #obj["SEQ_SELE"] = prop_name
                      if "SM" in prop_name:
                         spl = prop_name.split('/')
                         name = spl[1]
                         start = int(spl[2])
                         en = int(spl[3])
                         if scene.frame_current >= start and scene.frame_current < en:
                            vat = vatq.box()
                            vav = obj[prop_name]
                            vat.label(text="Type:  " + "Speed Multiplier")
                            tlt = vat.split()
                            tlt.label(text="Start Frame:  " + spl[2])
                            tlt.label(text="End Frame:  " + spl[3])
                            
                            gtt = vat.split()
                            gtt.label(text="Event name: " + name)
                            gtt.label(text="Value:  " + str(vav))
                            op = vat.operator("object.delete_event_seq")
                            op.node = prop_name
                            
                      if "SP" in prop_name:
                         spl = prop_name.split('/')
                         name = spl[1]
                         start = int(spl[2])
                         if scene.frame_current >= start and scene.frame_current < start + 1:
                            vat = vatq.box()
                            vav = obj[prop_name]
                            vat.label(text="Type:  " + "Play Sound")
                            vat.label(text="Start Frame:  " + spl[2])
                            gtt = vat.split()
                            gtt.label(text="Event name: " + name)
                            gtt.label(text="Sound Index:  " + str(vav))
                            op = vat.operator("object.delete_event_seq")
                            op.node = prop_name
                            
                      if "AT" in prop_name:
                         spl = prop_name.split('/')
                         
                         name = spl[1]
                         start = int(spl[2])
                         en = int(spl[3])
                         v1 = spl[4]
                         v2 = spl[5]
                         v3 = spl[6]
                         v4 = spl[7]
                         if scene.frame_current >= start and scene.frame_current < en:
                            vat = vatq.box()
                            vav = obj[prop_name]
                            vat.label(text="Type:  " + "Meta Events")
                            tlt = vat.split()
                            tlt.label(text="Start Frame:  " + spl[2])
                            tlt.label(text="End Frame:  " + spl[3])
                            gtt = vat.split()
                            gtt.label(text="Event name: " + name)
                            gtt.label(text="Value:  " + v1 + ", " + v2 + ", " + v3 + ", " + v4)
                            op = vat.operator("object.delete_event_seq")
                            op.node = prop_name
                            
                            
                            
                            
                      if "EF" in prop_name:
                         spl = prop_name.split('/')
                         name = spl[1]
                         start = int(spl[2])
                         
                         stopcode =  "Don't interrupt" if int(spl[3]) == -1 else "After animation execution"
                         eff_inde = int(spl[4])
                         bone_attach = int(spl[5]) + 1
                         
                         boneName = str(bone_attach)
                         if bone_attach == 0:
                             boneName = "root"
                         
                         particle_amount = int(spl[5])
                         
                         if scene.frame_current >= start and scene.frame_current < start + 1:
                            vat = vatq.box()
                            vav = obj[prop_name]
                            vat.label(text="Type:  " + "Effect Event")
                            tlt = vat.split()
                            tlt.label(text="Start Frame:  " + spl[2])
                            vat.label(text="Effect interruption:  " + stopcode)
               
                            vat.label(text="Event name: " + name)
                            fgt = vat.box()
                            tgt = fgt.split()
                            tgt.label(text="Effect index:  " + spl[4])
                            tgt.label(text="Attach on bone:  " + boneName)
                            fgt.label(text="Spawn amount:  " + spl[6])
                            op = vat.operator("object.delete_event_seq")
                            op.node = prop_name

                         
                         
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                             
                             
                    else:      
                      vat = vatq.box()
                      if "SM" in prop_name:
                         spl = prop_name.split('/')
                         name = spl[1]
                         start = int(spl[2])
                         en = int(spl[3])
                         vav = obj[prop_name]
                         vat.label(text="Type:  " + "Speed Multiplier")
                         tlt = vat.split()
                         tlt.label(text="Start Frame:  " + spl[2])
                         tlt.label(text="End Frame:  " + spl[3])
                         gtt = vat.split()
                         gtt.label(text="Event name: " + name)
                         gtt.label(text="Value:  " + str(vav))
                         
                         op = vat.operator("object.delete_event_seq")
                         op.node = prop_name
                         vat.active = scene.frame_current >= start and scene.frame_current < en


                      #vat = vatq.box()
                      if "SP" in prop_name:
                         spl = prop_name.split('/')
                         name = spl[1]
                         start = int(spl[2])
                         vav = obj[prop_name]
                         vat.label(text="Type:  " + "Play Sound")
                         vat.label(text="Start Frame:  " + spl[2])
                         gtt = vat.split()
                         gtt.label(text="Event name: " + name)
                         gtt.label(text="Sound Index:  " + str(vav))
                         
                         op = vat.operator("object.delete_event_seq")
                         op.node = prop_name
                         vat.active =  scene.frame_current >= start and scene.frame_current < start + 1
                            
                            
                      #vat = vatq.box()
                      if "AT" in prop_name:
                         spl = prop_name.split('/')
                         name = spl[1]
                         start = int(spl[2])
                         en = int(spl[3])
                         v1 = spl[4]
                         v2 = spl[5]
                         v3 = spl[6]
                         v4 = spl[7]
                         vav = obj[prop_name]
                         vat.label(text="Type:  " + "Meta Events")
                         tlt = vat.split()
                         tlt.label(text="Start Frame:  " + spl[2])
                         tlt.label(text="End Frame:  " + spl[3])
                         gtt = vat.split()
                         gtt.label(text="Event name: " + name)
                         gtt.label(text="Value:  " + v1 + ", " + v2 + ", " + v3 + ", " + v4)
                         
                         op = vat.operator("object.delete_event_seq")
                         op.node = prop_name
                         vat.active = scene.frame_current >= start and scene.frame_current < en
                         
                         
                         
                      if "EF" in prop_name:
                         spl = prop_name.split('/')
                         name = spl[1]
                         start = int(spl[2])
                         
                         stopcode =  "Don't interrupt" if int(spl[3]) == -1 else "After animation execution"
                         eff_inde = int(spl[4])
                         bone_attach = int(spl[5])
                         particle_amount = int(spl[5])
                         
                         
                         vav = obj[prop_name]
                         vat.label(text="Type:  " + "Effect Event")
                         tlt = vat.split()
                         tlt.label(text="Start Frame:  " + spl[2])
                         vat.label(text="Effect interruption:  " + stopcode)
               
                         vat.label(text="Event name: " + name)
                         fgt = vat.box()
                         tgt = fgt.split()
                         tgt.label(text="Effect index:  " + spl[4])
                         tgt.label(text="Attached to bone:  " + spl[5])
                         fgt.label(text="Spawn amount:  " + spl[6])
                         
                         op = vat.operator("object.delete_event_seq")
                         op.node = prop_name
                         vat.active = scene.frame_current >= start and scene.frame_current < start + 1

        

def update_frame_seq(self):
    #bpy.ops.object.frame_update_operator('INVOKE_DEFAULT')
    
    if bpy.context.scene.simulate_seq == True:
        for screen in bpy.data.screens:
           for area in screen.areas:
               if area.type == "VIEW_3D":
                  area.tag_redraw()
                  

  
    
class OBJECT_OT_DeleteEvent_seq(Operator):
    bl_idname = "object.delete_event_seq"
    bl_label = "Delete this event"
    bl_description = "deletes the selected event"
    
    
    node: bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object   
        return active_object is not None
    def execute(self, context):
      active_object = context.active_object
      del active_object[self.node]
      return {'FINISHED'}                 
    
    
    
class OBJECT_OT_DeleteSequence_seq(Operator):
    bl_idname = "object.delete_sequences_seq"
    bl_label = "Clear all SEQ events"
    bl_description = "deletes all imported events from the armature"
    @classmethod
    def poll(cls, context):
        active_object = context.active_object   
        return active_object is not None
    def execute(self, context):
      active_object = context.active_object
      

      prop_names = list(active_object.keys())
      for prop_name in prop_names:
          if "SEQ" in prop_name:
             del active_object[prop_name]
      return {'FINISHED'}                 
    
class OBJECT_OT_ImportSequence_seq(Operator, ImportHelper):
    bl_idname = "object.import_seq_file_seq"
    bl_label = "Import SEQ file"
    bl_description = "Import Sequence file"



    files: CollectionProperty(
        name="File Path",
        type=OperatorFileListElement,
        )
    directory: StringProperty(
        subtype='DIR_PATH',
        )
            
    filter_glob: StringProperty(
        default="*.seq",
        options={'HIDDEN'},
        maxlen=255,
    )
    @classmethod
    def poll(cls, context):
        active_object = context.active_object   
        return active_object is not None
    
    def execute(self, context):
      active_object = context.active_object
      

      prop_names = list(active_object.keys())
      for prop_name in prop_names:
          if "SEQ" in prop_name:
             del active_object[prop_name]
   
                        
                           
      directory = self.directory
      for file in self.files:
        context.scene.seqname = "Loaded file: " + file.name
        filepath = os.path.join(directory, file.name)  
        with open(filepath, "rb") as file:
            filemagic = struct.unpack("<Q", file.read(8))[0]
            if filemagic != 5326163:
               self.report({'ERROR'}, "File " + file_path + " file wasn't a SEQ file, cancelling...")
               return {'CANCELLED'}
            
            
            offset_speed_multiplier = struct.unpack("<H", file.read(2))[0]
            count_speed_multiplier = struct.unpack("<H", file.read(2))[0]
            
            offset_sounds = struct.unpack("<H", file.read(2))[0]
            count_sounds = struct.unpack("<H", file.read(2))[0]
            
            offset_attacks = struct.unpack("<H", file.read(2))[0]
            count_attacks = struct.unpack("<H", file.read(2))[0]
            
            offset_effects = struct.unpack("<H", file.read(2))[0]
            count_effects = struct.unpack("<H", file.read(2))[0]
            
            
            file.seek(offset_speed_multiplier)
            for i in range(0,count_speed_multiplier):
                time = struct.unpack("<H", file.read(2))[0]
                end = struct.unpack("<H", file.read(2))[0]
                multiplier = struct.unpack("<f", file.read(4))[0]
                
                active_object["SEQ_SM/" + str(i) + "/" + str(time) + "/" + str(end)] = multiplier
                
                
                
            file.seek(offset_sounds)
            for i in range(0,count_sounds):
                time = struct.unpack("<H", file.read(2))[0]
                soun = struct.unpack("<H", file.read(2))[0]
                byteco = struct.unpack("<Q", file.read(8))[0]
                
                active_object["SEQ_SP/" + str(i) + "/" + str(time)] = soun
                
            file.seek(offset_attacks)
            for i in range(0,count_attacks):
                time = struct.unpack("<H", file.read(2))[0]
                end = struct.unpack("<H", file.read(2))[0]
                
                v1 = struct.unpack("<B", file.read(1))[0]
                v2 = struct.unpack("<B", file.read(1))[0]
                v3 = struct.unpack("<B", file.read(1))[0]
                v4 = struct.unpack("<B", file.read(1))[0]
                active_object["SEQ_AT/" + str(i) + "/" + str(time) + "/"  + str(end) + "/" + str(v1) + "/"+ str(v2) + "/"+ str(v3) + "/"+ str(v4)] = 1
                
                    
            file.seek(offset_effects)
            for i in range(0,count_effects):
                LOOPF = struct.unpack("<i", file.read(4))[0]
                time = struct.unpack("<I", file.read(4))[0]
                
                effect_inde = struct.unpack("<B", file.read(1))[0]
                bone = struct.unpack("<b", file.read(1))[0]
                partic = struct.unpack("<H", file.read(2))[0]
                    
                    
                
                active_object["SEQ_EF/" + str(i) + "/" + str(time) + "/"  + str(LOOPF) + "/" + str(effect_inde) + "/"+ str(bone) + "/"+ str(partic)] = 1
            
      return {'FINISHED'}
  
  
  
  
class OBJECT_OT_AddEvent_seq(Operator):
    bl_idname = "object.add_event_seq"
    bl_label = "Add a new event"
    bl_description = "Addes a new event to the current armature"
    
    
    node: bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        active_object = context.active_object   
        return active_object is not None and context.active_object.mode == 'POSE'
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        selected_obj = bpy.context.object
        
        layout.label(text="Add a Event of type:")
        layout.prop(context.scene,"event_type_seq")
        
        row1 = layout.split()
        if context.scene.event_type_seq == "Time Multiplier":
           row1.prop(context.scene,"SEQts",text="Event start frame")
           row1.prop(context.scene,"SEQte",text="Event end frame")
           layout.prop(context.scene,"SEQv1",text="Multiplier Value")
           sif = layout.operator("object.add_event_on_seq")
           sif.opco = 0
           
        if context.scene.event_type_seq == "Play Sound":
           layout.prop(context.scene,"SEQts",text="Play sound frame")
           layout.prop(context.scene,"SEQte",text="Sound index")
           sif = layout.operator("object.add_event_on_seq")
           sif.opco = 1
           
           
        if context.scene.event_type_seq == "Meta":
           row1.prop(context.scene,"SEQts",text="Event start frame")
           row1.prop(context.scene,"SEQte",text="Event end frame")
           row1 = layout.split()
           row1.prop(context.scene,"SEQv2",text="Value 1")
           row1.prop(context.scene,"SEQv3",text="Value 2")
           row1 = layout.split()
           row1.prop(context.scene,"SEQv4",text="Value 3")
           row1.prop(context.scene,"SEQv5",text="Value 4")
           sif = layout.operator("object.add_event_on_seq")
           sif.opco = 2
           
        if context.scene.event_type_seq == "Effect":
           layout.prop(context.scene,"stopcode_seq")
           
           layout.prop(context.scene,"SEQts",text="Spawn effect on frame: ")
           layout.prop(context.scene,"SEQv2",text="Effect index: ")
           
           layout.prop(context.scene, "SEQbonese", text="Attach effect on selected bone: ")
           layout.prop(context.scene,"SEQv6",text="Spawn quantity: ")
           sif = layout.operator("object.add_event_on_seq")
           sif.opco = 3
           #layout.prop(context.scene,"SEQv2",text="Attach on bone: " + selected_pose_bones[0])
           #layout.prop(context.scene,"SEQv6",text="Effect index: ")
           
        
        
        
    def execute(self, context):
        #context.scene.SEQts = bpy.context.scene.frame_start
        #context.scene.SEQte = bpy.context.scene.frame_end
        selected_obj = bpy.context.object
        selected_pose_bones = [pose_bone for pose_bone in selected_obj.pose.bones if pose_bone.bone.select] 
        context.scene.SEQbonese = selected_pose_bones[0].name
        return context.window_manager.invoke_popup(self, width=300)
        return {'FINISHED'}     





class OBJECT_OT_AddEventToSeq(Operator):
    bl_idname = "object.add_event_on_seq"
    bl_label = "Add event"
    bl_description = "Finishes adding a new event to the current armature"
    
    opco: bpy.props.IntProperty()
    def execute(self, context):
        selected_obj = bpy.context.object
        
        name = 0
        lsi = []
        prop_names = list(selected_obj.keys())
        for prop_name in prop_names:
          if "SEQ" in prop_name:
              ple = prop_name.split("/")
              lsi.append(int(ple[1]))
        if len(lsi) > 0:
           lsi.sort()
           name = lsi[len(lsi)-1] + 1
        
        
        
        if self.opco == 0:
           selected_obj["SEQ_SM/" + str(name) + "/" + str(context.scene.SEQts)+ "/" + str(context.scene.SEQte)] = context.scene.SEQv1
        if self.opco == 1:
           selected_obj["SEQ_SP/" + str(name) + "/" + str(context.scene.SEQts)] = context.scene.SEQte
        if self.opco == 2:
           selected_obj["SEQ_AT/" + str(name) + "/" + str(context.scene.SEQts) + "/" + str(context.scene.SEQte)+ "/" + str(context.scene.SEQv2)+ "/" + str(context.scene.SEQv3)+ "/" + str(context.scene.SEQv4)+ "/" + str(context.scene.SEQv5)] = 1
           
        if self.opco == 3:
           selected_obj["SEQ_EF/" + str(name) + "/" + str(context.scene.SEQts) + "/" + str("-1" if context.scene.stopcode_seq == "Dont stop" else "0")+ "/" + str(context.scene.SEQv2)+ "/" + str(int(context.scene.SEQbonese.replace("root","0"))-1)+ "/" + str(context.scene.SEQv6)] = 1
           
           
        return {'FINISHED'} 
    
    
class OBJECT_OT_Export_seq(bpy.types.Operator, ExportHelper):
    bl_idname = "object.export_seq"
    bl_label = "Export SEQ"
    bl_description = "Export SEQ"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".SEQ"
    filter_glob: StringProperty(
        default="*.seq",
        options={'HIDDEN'},
        maxlen=255,
    )
    files: CollectionProperty(
        type=bpy.types.PropertyGroup
    )
    @classmethod
    def poll(cls, context):
        active_object = context.active_object   
        return active_object is not None
    
    
    def execute(self, context):   
      armature = bpy.context.object
     
      directory = self.filepath
      directory = directory.replace(os.path.basename(directory),"")
      directory = directory[:-1]

      sml = []
      spl = []
      mtl = []
      efl = []
      
      prop_names = list(armature.keys())
      for prop_name in prop_names:
          if "SEQ" in prop_name:
              if "SM" in prop_name:
                  sml.append(prop_name+ "/" + str(armature[prop_name]))
              if "SP" in prop_name:
                  spl.append(prop_name+ "/" + str(armature[prop_name]))
              if "AT" in prop_name:
                  mtl.append(prop_name)
              if "EF" in prop_name:
                  efl.append(prop_name)
                  
                  
                  


      for file_elem in self.files:
        file_path = f"{directory}/{file_elem.name}"
        with open(file_path, "wb") as file:
            def writeThenReturn(what,type,on):
                ba = file.tell()
                file.seek(on)
                file.write(struct.pack(type, what))
                file.seek(ba)
            
            
            
            
            file.write(struct.pack('Q', 5326163))
            
            smoffset = file.tell()
            file.write(struct.pack('H', 0))
            file.write(struct.pack('H', len(sml)))
            
            spoffset = file.tell()
            file.write(struct.pack('H', 0))
            file.write(struct.pack('H', len(spl)))
            
            mtoffset = file.tell()
            file.write(struct.pack('H', 0))
            file.write(struct.pack('H', len(mtl)))
            
            efoffset = file.tell()
            file.write(struct.pack('H', 0))
            file.write(struct.pack('H', len(efl)))
            
            
            file.write(struct.pack('Q', 17289300282089472257))
            
            
            
            writeThenReturn(file.tell(),"H",smoffset)
            for i in sml:
                #SEQ_SM/0/121/124/0.20000000298023224
                
                
                spli = i.split("/")
                file.write(struct.pack('H', int(spli[2])))
                file.write(struct.pack('H', int(spli[3])))
                file.write(struct.pack('f', float(spli[4])))
                
            writeThenReturn(file.tell(),"H",spoffset)
            for i in spl:
                spli = i.split("/")
                file.write(struct.pack('H', int(spli[2])))
                file.write(struct.pack('H', int(spli[3])))
                file.write(struct.pack('Q', 0))
                
                
                
            writeThenReturn(file.tell(),"H",mtoffset)
            for i in mtl:
                spli = i.split("/")
                file.write(struct.pack('H', int(spli[2])))
                file.write(struct.pack('H', int(spli[3])))
                file.write(struct.pack('B', int(spli[4])))
                file.write(struct.pack('B', int(spli[5])))
                file.write(struct.pack('B', int(spli[6])))
                file.write(struct.pack('B', int(spli[7])))
                
                
            writeThenReturn(file.tell(),"H",efoffset)
            for i in efl:
                #selected_obj["SEQ_EF/" + str(name) + "/" + str(context.scene.SEQts) + "/" + str("-1" if context.scene.stopcode == "Dont stop" else "0")+ "/" + str(context.scene.SEQv2)+ "/" + str(int(context.scene.SEQbonese.replace("root","0"))-1)+ "/" + str(context.scene.SEQv6)] = 1
                spli = i.split("/")
                file.write(struct.pack('i', int(spli[3])))
                file.write(struct.pack('I', int(spli[2])))
                
                lname = int(spli[5].replace("root","0"))
                
                file.write(struct.pack('B', int(spli[4])))
                file.write(struct.pack('b', lname))
                file.write(struct.pack('H', int(spli[6])))
            while file.tell() % 64 != 0:
                file.write(struct.pack('b', 0))

            
            
      return {'FINISHED'}  
    
def register():
    bpy.app.handlers.frame_change_post.append(update_frame_seq)
    bpy.utils.register_class(VIEW3D_PT_SEQPanel)
    bpy.utils.register_class(OBJECT_OT_FrameUpdateOperator_seq)
    bpy.utils.register_class(OBJECT_OT_ImportSequence_seq)
    bpy.utils.register_class(OBJECT_OT_DeleteSequence_seq)
    bpy.utils.register_class(OBJECT_OT_DeleteEvent_seq)
    bpy.utils.register_class(OBJECT_OT_AddEvent_seq)
    bpy.utils.register_class(OBJECT_OT_AddEventToSeq)
    bpy.utils.register_class(OBJECT_OT_Export_seq)
    
    bpy.types.Scene.simulate_seq = BoolProperty(
        name="Show Events on panel",
        description="The code will show what properties are playing from a SEQ (if loaded)",
        default=False
    )
    bpy.types.Scene.show_type_seq = BoolProperty(
        name="Show currently active as highlight",
        description="The code will show the currently active seq properties and their respective values as a highlight. if it's bright white, it's active",
        default=False
    )
    
    bpy.types.Scene.seqname = StringProperty(
        name="Show currently active as highlight",
        description="The code will show the currently active seq properties and their respective values as a highlight. if it's bright white, it's active",
        default=""
    )
    bpy.types.Scene.event_type_seq = EnumProperty(
          name="",
          description="",
          items=(
            ('Time Multiplier', "Time Multiplier", "The animation mutiplier speed of the animation"),
            ('Play Sound', 'Play Sound', "Plays a sound from a index"),
            ('Meta', "Meta", "The meta events values depends on the dat you're dealling with, the meta events can do a lot of things, like changing the hand shapes"),
            ('Effect', "Effect", "Spawns a game effect attached to a bone of the model"),
          ),
          default='Time Multiplier',
    )
    
    bpy.types.Scene.stopcode_seq = EnumProperty(
          name="",
          description="",
          items=(
            ('Stop effect after animation execution', "Stop effect after animation execution", "once the animation reaches to the end, the effect will be destroyed"),
            ('Dont stop', 'Dont stop', "Even after the animation finishes, the effect will continue playing until the effect reaches to it's end. Looped effects will be seen on the game FOREVER, so be careful"),
          ),
          default='Stop effect after animation execution',
    )
    
    
    bpy.types.Scene.SEQv1 = FloatProperty(
          name="",
          description="",
          default=1,
    )
    bpy.types.Scene.SEQv2 = IntProperty(
          name="",
          description="",
          default=0,
          min=0,
          max=255,
    )
    bpy.types.Scene.SEQv3 = IntProperty(
          name="",
          description="",
          default=0,
          min=0,
          max=255,
    )
    bpy.types.Scene.SEQv4 = IntProperty(
          name="",
          description="",
          default=0,
          min=0,
          max=255,
    )
    bpy.types.Scene.SEQv5 = IntProperty(
          name="",
          description="",
          default=0,
          min=0,
          max=255,
    )
    bpy.types.Scene.SEQv6 = IntProperty(
          name="",
          description="",
          default=1,
          min=0,
          max=65535,
          
    )

    bpy.types.Scene.SEQts = IntProperty(
          name="",
          description="",
          default=1,
          min=0,
          max=65535,
    )
    bpy.types.Scene.SEQte = IntProperty(
          name="",
          description="",
          default=1,
          min=0,
          max=65535,
          
    )
    bpy.types.Scene.SEQbonese = StringProperty(
          name="",
          description="",
          default="",
          
    )
    
def unregister():
    bpy.app.handlers.frame_change_post.remove(update_frame_seq)
    bpy.utils.unregister_class(VIEW3D_PT_SEQPanel_seq)
    bpy.utils.unregister_class(OBJECT_OT_FrameUpdateOperator_seq)
    bpy.utils.unregister_class(OBJECT_OT_ImportSequence_seq)
    bpy.utils.unregister_class(OBJECT_OT_DeleteSequence_seq)
    bpy.utils.unregister_class(OBJECT_OT_DeleteEvent_seq)
    bpy.utils.unregister_class(OBJECT_OT_AddEvent_seq)
    bpy.utils.unregister_class(OBJECT_OT_AddEventToSeq)
    bpy.utils.unregister_class(OBJECT_OT_Export_seq)
    del bpy.types.Scene.simulate_seq
    del bpy.types.Scene.event_type_seq
    
if __name__ == "__main__":
    register()
