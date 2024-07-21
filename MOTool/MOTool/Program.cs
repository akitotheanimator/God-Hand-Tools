using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;


using System.Windows.Forms;
using OxyPlot;
using OxyPlot.Series;
using OxyPlot.WindowsForms;
using System.Numerics;

public static class Program
{
    public static string pathForBones;
    public static PlotModel plotModel;
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
        Console.WriteLine("Drag and drop a .MOT on this field.");
        string ans = Console.ReadLine();
        validateMot(ans);
    }
    public static void validateMot(string path)
    {
        string filePath = path.Replace("\"", "").Replace("\n", "");
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
            plotModel = new PlotModel { Title = Path.GetFileNameWithoutExtension(filePath) };
            GetMot.processMot(filePath);
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