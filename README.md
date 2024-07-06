![image](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/6eebef12-521f-46f2-89fc-45a0b14e9ab4)![image](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/b7d14244-6f85-46e0-bf10-09c5fe56d561)# God Hand Tools

I have lost acess to my old account so i made a new one.
I will update the tools from the old pack.

# Thanks to CarLoiD
He helped me a lot to understand further on how the god hand file system works, me and him got our brains to work on how the files storage their data to bring im the pack.


# DAT Extractor

Works like the classic one, but BETTER, it reads all the contents of the god hand packed data (.dat) and extract all of the contents in there. This one has a more robust code and supports both GPF(Generic packed files) and MPF(Mega package file).
Now you can just drag the folders that you want to be readen on and the program will automatically look through all the subdirectories of it and read each dat that contains in there.
Or, you can simply drag and drog all the dat files on the .exe and it will be processed automatically








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
Using a simple math calculation. we've readen the first 4 bytes of the file, so that means the staring point(offset) of the file should be at offset **4**.
![types](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/26c6a62d-2df1-4bf9-aaff-5632834ef446)

remember that number i told to remember? we're going to use it to determinate the adress that the adresses stop.
each adress of the header is **4 bytes, meant to be readen as a UInt32.**
![types](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/c0415533-ac96-47db-8373-6f01ae7dc2c0)

which means, **in order to get each adress of each file inside the DAT file, we need to read all of the bytes as a UInt32.* In this example, the UInt32 values of the 3 adresses i selected are 4960, 154272 and 475616.
