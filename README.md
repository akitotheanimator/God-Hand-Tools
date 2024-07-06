# God Hand Tools

I have lost acess to my old account so i made a new one.
I will update the tools from the old pack.

# Thanks to CarLoiD
He helped me a lot to understand further on how the god hand file system works, me and him got our brains to work on how the files storage their data to bring im the pack.


# DAT Extractor

Works like the classic one, but BETTER, it reads all the contents of the god hand packed data (.dat) and extract all of the contents in there. This one has a more robust code and supports both GPF(Generic packed files) and MPF(Mega package file).
Now you can just drag the folders that you want to be readen on and the program will automatically look through all the subdirectories of it and read each dat that contains in there.
Or, you can simply drag and drog all the dat files on the .exe and it will be processed automatically








# File Structure Docs
# DAT
The god hand DAT is a file that packs game assets, such as models, for example. It is pretty common to be seen when visualized on a AFS viewer.

![godo hand](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/abd327e4-d0ab-4946-a95f-fc9e2e7fed2b)

There is two main DAT types that can be seen on GOD HAND: UPD and DAT(i made up those names since i haven't saw anybody to come up with a name for them.)
There's a subtle way to identify both, they have a difference that's crucial to diferentiate them two.

Ultra Packed Data(UPD) gives some bytes, before filling a enormous space with *blank bytes* , as you can see, it covers a very generous of the DAT, going from offset 304 to offset 512.
![types](https://github.com/akitotheanimator/God-Hand-Tools/assets/174764120/7662fd94-099e-4d0e-b0ed-8a1f4ff3bd0d)
