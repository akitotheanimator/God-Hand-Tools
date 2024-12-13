# God Hand Tools

**This whole pack is made in C# frameworks 4.8**

I have lost acess to my old account so i made a new one.
God Hand Tools's purpose is to bring people packs of tools to convert god hand files to more flexible and modern ones.

# Thanks to CarLoiD and Kerilk
Carloid helped me a lot to understand further on how the god hand file system works, me and him got our brains to work on how the files storage their data to bring im the pack.
**CarLoid's github page: https://github.com/CarLoiD**

And huge thanks to Kerilk, Shotouts to this mad lad who documented the whole MOT documentation for the public. Thank you a lot!


**Kerilk's github page: https://github.com/Kerilk**

**in case you're wondering, here's the MOT documentation: https://github.com/Kerilk/bayonetta_tools/wiki/Motion-Formats-%28mot-files%29**

# DAT Extractor

Works like the classic one, but BETTER, it reads all the contents of the god hand packed data (.dat) and extract all of the contents in there. This one has a more robust code and supports:
* GPFs(Generic package files, includes pl or em dats...)
* MPFs(Mega package file, includes map dats...)
* PEFs(Packed Event File, includes ev dats...)
  
Now you can just drag the folders that you want to be readen on and the program will automatically look through all the subdirectories of it and read each dat that contains in there.
Or, you can simply drag and drog all the dat files on the .exe and it will be processed automatically.

# MdtoSmd2.0

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

# Blen2MOT 2.0
*THIS TOOL WILL NOT BE UPDATED FOR SUPPORT OF NEWER BLENDER VERSIONS. THE SCRIPT WAS WRITTEN IN BLENDER 3.6 AND UNLESS I CHANGE MY MIND I WILL NOT MANTAIN UPDATES FOR FUTURE BLENDER VERSIONS.*

 ![2 Sem Título_20241109160626](https://github.com/user-attachments/assets/df00439e-6725-4db2-9497-db5a61a2a9d1)

 
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


# Tutorials
**Here are the basis tutorials of the toolpack**
* T1-How to extract God Hand's dat file from the ISO and extract the dat contents: https://giphy.com/gifs/3I7f85WEJ4h7AHXjyP
* T2-How to convert God Hand's md file to smd:
* T3-How to convert God Hand's mot file to smd(follow this after T2):

**Import the stuff on blender**
* T4-How to import a md on Blender(follow this after T2):
* How to import a mot on Blender(Using MOTool)(follow this after T4):

# if you need anything contact me in discord srnoobi#3108!
