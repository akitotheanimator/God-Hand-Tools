# God Hand Tools

I have lost acess to my old account so i made a new one.
I will update the tools from the old pack.

# Thanks to CarLoiD
He helped me a lot to understand further on how the god hand file system works, me and him got our brains to work on how the files storage their data to bring im the pack.


# DAT Extractor

Works like the classic one, but BETTER, it reads all the contents of the god hand packed data (.dat) and extract all of the contents in there. This one has a more robust code and supports both GPF(Generic packed files) and MPF(Mega package file).
Now you can just drag the folders that you want to be readen on and the program will automatically look through all the subdirectories of it and read each dat that contains in there.
Or, you can simply drag and drog all the dat files on the .exe and it will be processed automatically

# MOTool
MOTool is a brand new tool for the pack that converts god hand MOT to valve SMD. You will need a .bones file to convert the files correctly. and it still WIP and BETA.
This wouldn't be possible without KERILK. https://github.com/Kerilk shotouts to this mad lad who documented the whole MOT documentation for the public. Thank you a lot!
in case you're wondering, here's the MOT documentation: https://github.com/Kerilk/bayonetta_tools/wiki/Motion-Formats-%28mot-files%29
Obviously the God Hand MOT is much diferent than the one in bayonetta or nieR, but the value reading & parsing follows the same system.






# File Structure Docs
# DAT 1
The god hand DAT is a file that packs game assets, such as models, for example. It is pretty common to be seen when visualized on a AFS viewer.

![godo hand](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/abd327e4-d0ab-4946-a95f-fc9e2e7fed2b)

There is two main DAT types that can be seen on GOD HAND. Type 1 and type 0.
There's a subtle way to identify both, they have a difference that's crucial to diferentiate them two.

DAT type 1 gives some bytes, before filling a enormous space with *blank bytes*.
![types](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/7662fd94-099e-4d0e-b0ed-8a1f4ff3bd0d)
As you can see, the *blank bytes* covers a very generous portion of the DAT, going from offset 304 to offset 512.

On the other hand, DAT type 0 is straight forward, no blank spaces to be seen.
![types](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/c4cbb102-23e7-4bb3-9ccc-a593ee08a4d1)

pretty subtle BUT essential way to identify both. The file specifies which version they are, but it's a little tricky.
* DAT type 1 is mostly used for big memory consuption that needs to be compressed, the majority of them are map files.
* DAT typ 0 is mostly used for models or such.
* 
# DAT 1.1 - Rules that applies for both types
I have to talk about this.
Normally, files have a sequence of characters that helps to identify the file they're dealing with, for example, the MD files and SCR files from god hand have a file identifier header:
![types](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/54a601f3-e194-4b3b-ad44-743e7cab7069)
However, DAT Files doesn't have a identifier on the Header. The game is almost entirely coded with indexing, and since this is a package file, that's *one of the cases*.

in short, if you're writting a program to read dat files, **you will NOT be able to tell the real file type by string sequence.**

if the file isn't a real dat file, i.e: a audio.mp3 that was renamed to audio.dat, the program will probably encounter errors reading the file, or even crash.

You will need to handle that kind of stuff if you're writting a god hand dat reader or repacker.

# DAT 1.2 - TYPE 0
It's easy to be made sense of. The first 4 bytes are the quantity of files that the DAT containts. Should be reader as a **UInt32**.
in this example, i will use Gene .dat file, that the name is **pl00.dat**.
![types](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/352ed612-e356-43d9-95a4-c5237381c512)

you will have to remember that **UInt32** value *soon*.

And then, the next bytes are all the adresses of all files in the DAT. How to know at which point it should be readen?
Using a simple math calculation. we've readen the first 4 bytes of the file, so that means the staring point(adress/offset) of the file should be at offset **4**.
![types](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/26c6a62d-2df1-4bf9-aaff-5632834ef446)

remember that number i told to remember? we're going to use it to determinate the adress that the adresses stop.
each adress of the header is **4 bytes, meant to be readen as a UInt32.**

![types](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/c0415533-ac96-47db-8373-6f01ae7dc2c0)

Which means, **in order to get each adress of each file inside the DAT file, we need to read all of the bytes as a UInt32.** In this example, the UInt32 values of the 3 adresses i selected are 4960, 154272 and 475616.

The math to calculate the stop point(adress/offset) is quite easy.
First, you get the number of files that the file gives on the **offset 0 of the file**.
then, you do this operation:

* EO = SP + (NOF * 4)
  
Where:
* EO = the exact point that there's no more adresses to be readen.
* SP = the adress that the first adress is located. On the file i'm using as example, the offset is equal **4**.
* NOF = the number of files that the DAT containts. On the file i'm using as example, the value it was given on offset **0** after reading the **UInt32** value of it.
* 4 = an UInt32 takes 4 bytes, so, in order to convert file number to UInt32 bytes, you need to multiply by 4.

![types](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/a49c0a6c-82da-470b-83eb-b81df7545447)

This is all the file offsets.

Now, how to retrieve the File type of each adress.
In pl00.dat, has returned a EO of 2476. So, next step is to go in that adress...
![image](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/45c698d2-3e91-479f-b3ec-b0f675d3af3a)

There's a Area of the DAT that's covered with file types. Seq, Mot, Tm3 and etc. Let's pay closer attention to the duration of this string area.
