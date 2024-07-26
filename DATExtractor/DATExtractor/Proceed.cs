using System.IO;
using System.Collections.Generic;
using System.Collections;
using static FILE_MANAGING.FILE_SYSTEM;

public static class Proceed
{

    public static void ProceedStep(string arg)
    {
        byte[] file = File.ReadAllBytes(arg);



        if (Path.GetExtension(arg) == ".dat")
        {
            if (!Directory.Exists(arg.Replace(".dat", ".dat_extacted"))) Directory.CreateDirectory(arg.Replace(".dat", ".dat_extacted"));
            string rootFolder = arg.Replace(".dat", ".dat_extacted");
            if (!File.Exists(rootFolder + "/readme.txt"))
            {
                var writer = File.CreateText(rootFolder + "/readme.txt");
                writer.WriteLine("Extracted using DAT Extractor (That extractor)\nThe files has sequences from 1 to infinity. Why?\nBecause the way DAT packed files are made uses only indexing. \n so a name for these files doesn't really exist.");
                writer.Dispose();
            }

            ((uint, string)[], string, uint) tempMemory = getDATInfo(arg);
            for (int i = 0; i < tempMemory.Item1.Length; i++)
            {
                Directory.CreateDirectory(rootFolder + "/" + (tempMemory.Item1[i].Item2.Replace("\0","")) + "/");


                string selectedFolder = rootFolder + "/" + (tempMemory.Item1[i].Item2.Replace("\0", "")) + "/";
                if (i + 1 < tempMemory.Item1.Length)
                {
                    using (FileStream fs = new FileStream(selectedFolder + tempMemory.Item1[i].Item2.Replace("\0", "") + i + "." + tempMemory.Item1[i].Item2.Replace("\0", "").ToLower(), FileMode.Create))
                    {
                        for (uint off = tempMemory.Item1[i].Item1; off < tempMemory.Item1[i + 1].Item1; off++)
                        {
                            fs.WriteByte(file[off]);
                        }
                    }
                }
                else
                {
                    using (FileStream fs = new FileStream(selectedFolder + tempMemory.Item1[i].Item2.Replace("\0", "") + i + "." + tempMemory.Item1[i].Item2.Replace("\0", "").ToLower(), FileMode.Create))
                    {
                        for (uint off = tempMemory.Item1[i].Item1; off < file.Length; off++)
                        {
                            fs.WriteByte(file[off]);
                        }
                    }
                }
            }
        }
        else
        {
            Console.WriteLine($"The file {Path.GetFileName(arg)} is not a DAT file! Skipping...");
        }
    }
}