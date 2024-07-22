using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Numerics;

public static class Program
{
    public static string pathForBones;
    public static string saveFileTo;
    public static int ETA=0;
    public static void Main(string[] args)
    {



        GlobalTools.changeColor(ConsoleColor.Green);
        Console.WriteLine("███    ███  █████  ██████  ███████     ██████  ██    ██      █████  ██   ██ ██ ████████  ██████  ██████  ██████  \r\n████  ████ ██   ██ ██   ██ ██          ██   ██  ██  ██      ██   ██ ██  ██  ██    ██    ██    ██      ██ ██   ██ \r\n██ ████ ██ ███████ ██   ██ █████       ██████    ████       ███████ █████   ██    ██    ██    ██  █████  ██   ██ \r\n██  ██  ██ ██   ██ ██   ██ ██          ██   ██    ██        ██   ██ ██  ██  ██    ██    ██    ██      ██ ██   ██ \r\n██      ██ ██   ██ ██████  ███████     ██████     ██        ██   ██ ██   ██ ██    ██     ██████  ██████  ██████  ");
        Console.WriteLine("");
        Read(args);
    }
    public static void Read(string[] args)
    {
        GlobalTools.changeColor(ConsoleColor.White);
        Console.WriteLine("Drag and drop a .MOT OR a FOLDER containing the MOTS on this field.");
        string ans = Console.ReadLine();
        validateMot(ans);
    }
    public static void validateMot(string path)
    {
        string filePath = path.Replace("\"", "").Replace("\n", "");
        if (filePath != "")
        {
            if (File.Exists(filePath))
            {
                byte[] header = File.ReadAllBytes(filePath);
                if (header[0] != 109 && header[1] != 116 && header[2] != 98 && header[3] != 51)
                {
                    GlobalTools.changeColor(ConsoleColor.Red);
                    Console.WriteLine("This is either not a MOT File, or the MOT is corrupted, select another file!");
                    Read(new string[0]);
                    return;
                }
                Console.WriteLine("Drag and drop the bones file of the model in this field.");
                pathForBones = Console.ReadLine().Replace("\"", "").Replace("\n", "");
                GetMot.processMot(filePath);
            }
            if (Directory.Exists(filePath))
            {
                string[] motFiles = Directory.GetFiles(filePath, "*.mot", SearchOption.AllDirectories);
                string[] bonesFile = Directory.GetFiles(filePath, "*.bones", SearchOption.AllDirectories);
                if (bonesFile.Length > 1)
                {
                    GlobalTools.changeColor(ConsoleColor.Red);
                    Console.WriteLine("There's more than 1 .bones file at the given path " + filePath + "! delete the other .bones file.");


                    GlobalTools.changeColor(ConsoleColor.Green);
                    Console.WriteLine("Drag and drop the bones file of the model in this field.");
                    pathForBones = Console.ReadLine().Replace("\"", "").Replace("\n", "");
                } else
                {
                    pathForBones = bonesFile[0];
                }
                if (bonesFile.Length == 0)
                {
                    GlobalTools.changeColor(ConsoleColor.Red);
                    Console.WriteLine("There's no .bones file at the given directory. Please, place the model .bones file to proceed.");


                    GlobalTools.changeColor(ConsoleColor.Green);
                    Console.WriteLine("Drag and drop the bones file of the model in this field.");
                    pathForBones = Console.ReadLine().Replace("\"", "").Replace("\n", "");
                }



                    for (int i = 0; i < motFiles.Length; i++)
                {
                    if (File.Exists(motFiles[i]))
                    {
                        ETA = motFiles.Length - i;
                        GetMot.processMot(motFiles[i]);
                    }
                }
            }
        }
        else
        {
            GlobalTools.changeColor(ConsoleColor.Red);
            Console.WriteLine("The path you provided is blank.");
            Read(new string[0]);
        }
    }
    public static BONES[] bones_;
}
public class BONES
{
    public Vector3 pos;
    public short parentingOrder;
    public short id;
}