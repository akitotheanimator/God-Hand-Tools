# God Hand Tools

**This whole pack is made in C# frameworks 4.8**

**some of the tools in this pack outputs SMD's. Install this addon for blender in order to import smd's on blender:** http://steamreview.org/BlenderSourceTools/

I have lost acess to my old account so i made a new one.
God Hand Tools's purpose is to bring people packs of tools to convert god hand files to more flexible and modern ones.

# Thanks to CarLoiD and Kerilk
Carloid helped me a lot to understand further on how the god hand file system works, me and him got our brains to work on how the files storage their data to bring im the pack.
**CarLoid's github page: https://github.com/CarLoiD**

And huge thanks to Kerilk, Shotouts to this mad lad who documented the whole MOT documentation for the public. Thank you a lot!


**Kerilk's github page: https://github.com/Kerilk**

**in case you're wondering, here's the MOT documentation: https://github.com/Kerilk/bayonetta_tools/wiki/Motion-Formats-%28mot-files%29**

# DAT Extractor [obsolete]

Works like the classic one, but BETTER, it reads all the contents of the god hand packed data (.dat) and extract all of the contents in there. This one has a more robust code and supports:
* GPFs(Generic package files, includes pl or em dats...)
* MPFs(Mega package file, includes map dats...)
* PEFs(Packed Event File, includes ev dats...)
  
Now you can just drag the folders that you want to be readen on and the program will automatically look through all the subdirectories of it and read each dat that contains in there.
Or, you can simply drag and drog all the dat files on the .exe and it will be processed automatically.

# MdtoSmd2.0 [obsolete]

Like the old one, it converts god hand .md models to valve smd. It has new features, like saving the bones as a *.bones* file. 
**you will need this tool in order to use MOTool.**
It have a map model support but **it's very W.I.P. i don't recomend trying to use it on map models.**

![godo](https://github.com/user-attachments/assets/cdf22492-cbc3-4f20-a309-c0eb025a6a8b)



# MOTool [obsolete]
MOTool is a brand new tool for the pack that converts god hand MOT to valve SMD. You will need a .bones file to convert the files correctly, which i have implemented on the brand new version of MdtoSmd.
**This tool still works fine, But Blen2MOT now has the same functionality and works better.**

![ezgif-1-5676d2ae5a](https://github.com/user-attachments/assets/d4294290-a0af-49c9-9fd6-1f06f7bd6b9b)


**However, In order to have the MOTool to convert the .MOT to .smd, you need to extract your .MD model using MDToSMD2.0,which is disponibilized on my god hand toolpack.**
How to use the tool: 

https://www.youtube.com/watch?v=GyOX3qUXCUM

# SESTool (Thanks to MuzzleFlash)

My lastest tool, thanks to MFAudio, the creation of Muzzleflash, now God Hand .SES audio banks can be edited!
Note: **SESTool doesn't work if a MFAudio executable isn't located in the same path as the SESTool executable.**
Check MFAudio, by MuzzleFlash!

https://gamebanana.com/tools/6656

How to use it: 

https://youtu.be/5khJHuOooMw
----------------------------
 Blender Tools
 ![2 Sem Título_20241109160626](https://github.com/user-attachments/assets/df00439e-6725-4db2-9497-db5a61a2a9d1)
----------------------------

 
# Blen2MOT 2.0
*THIS TOOL WILL NOT BE UPDATED FOR SUPPORT OF NEWER BLENDER VERSIONS. THE SCRIPT WAS WRITTEN IN BLENDER 3.6 AND UNLESS I CHANGE MY MIND I WILL NOT MANTAIN UPDATES FOR FUTURE BLENDER VERSIONS.*

Export animations from Blender to God hand MOT Format.
Import God hand MOT to Blender.
This tool comes with a blender .py addon that needs to be installed.
You will need a god hand model that had been extracted with MdToSmd tool in order to animate for the game!

![ezgif-7-9a93bc8ca1](https://github.com/user-attachments/assets/46f1cfab-3a34-4e91-a2cb-26967363dcc5)

How to use:

https://www.youtube.com/watch?v=-plPDKMJBEA

**Rules:**
* ONLY USE EULER ROTATIONS. QUATERNION ROTATION will be IGNORED.
* Apply IK on bones by checking the hierchary list. input in the bone IK Field the corresponding "Level" number of the bone you want to use.
* NEVER rename a bone.
* NEVER export the animation with non-baked constraints. Bake the animation first or the constraints will be IGNORED.
 
**Tips:**
* (In case you want to animate Gene.)Some animations in God Hand uses Animated Camera. To animate the god hand camera , keep in mind how the camera works. In gene's skeleton, we can see a bone called 28 and 29.
In this case, bone 28 is where the camera is located, and bone 29 is where the camera will look at. To animate the camera's FOV, animate bone 28 Y Rotation.
* Make sure to always optimize the animation. Either using F-Curve addon or cleaning up the curves manually. I know it's harder manually but sometimes that's the best option.

# Blen2MD 1.0
*THIS TOOL WILL NOT BE UPDATED FOR SUPPORT OF NEWER BLENDER VERSIONS. THE SCRIPT WAS WRITTEN IN BLENDER 3.6 AND UNLESS I CHANGE MY MIND I WILL NOT MANTAIN UPDATES FOR FUTURE BLENDER VERSIONS.*

## This tool wouldn't be possible without the help of *Rin/anasrar* and *JADERLINK!*
* Rin's github: https://github.com/anasrar/
* Jader's github: https://github.com/JADERLINK/
  
Thank you two!

Export models from Blender to God hand MD Format.
Import God hand MD to Blender.
This tool comes with a blender .py addon that needs to be installed.

it is finally possible!

![ezgif-1-b0a17db52e](https://github.com/user-attachments/assets/ad621802-e48d-45f0-a2f4-baec1c40e807)

The Texture Utility will require you to download a copy of imagemagick. I have implemented if for being a light source code program, besides it's free.

https://imagemagick.org/

>if you don't like using the texture utility or having to download imagemagick, texture indexing can also be done with other programs like GIMP.


# DaTool

The best dat tool from this pack. Different from DAT Extractor, this one has the ability to Repack too! And supports a large variety of file types such as:
* DAT
* SCP
* CMP
* EFF
* I
* ID
* DA
* IDD
* EMD
* EFM


  

# if you need any help about my tools contact me in discord srnoobi#3108!


# Blen2MOT 3.0

Blen2mot, but with new functionalities.
basically, this version is completely dependent and doesn't need the C# version of the program to be set up.
and now, you can individually set the precision curves rather than having the precision property to be applied on ALL curves.

![4](https://github.com/user-attachments/assets/e76ac0f3-50e3-4f79-a85d-c2ac89a47cea)

You can also now set flags for the curves individually. And the foot rig is now toggled by selecting the bones.
The ability to import HMOT's (although, HMOT export isn't currently available)
some changes on the UI, etc...


# Blen2SEQ

## This tool wouldn't be possible without the help of *Roni Evil!*
* Roni Evil's youtube: https://www.youtube.com/@ronievil

Blen2SEQ is a SEQ event importer and exporter. You can use it to edit the events in your MOT animation! You can:
* Manipulate the animation speed
* Play sounds
* Set special events
* Spawn effects

![bagnan](https://github.com/user-attachments/assets/c6b1b3d7-2f35-4414-984a-4e233762dd10)

  

# if you need any help about my tools contact me in discord srnoobi#3108!
