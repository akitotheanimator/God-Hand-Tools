using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.IO;
using System.Net;
using System.Globalization;

public static class Program
{
    public static bool ViewOutput = false;
    public static bool closeAutomatically = true;
    public static bool loops;
    public static byte[] IKBones;
    static void Main(string[] args)
    {


        if (args.Length > 0)
        {
            string[] arg = File.ReadAllLines(args[0]);


            List<byte> BonesIK = new List<byte>();
            string infoPath = arg[0];
            string animationName = arg[1];
            string bonesPath = arg[4];
            string[] ikboneSplit = arg[3].Split(',');
            loops = bool.Parse(arg[2]);
            infoPath = arg[0];
            animationName = arg[1];
            #region bones
            foreach (var a in ikboneSplit)
            {
                try
                {
                    BonesIK.Add(byte.Parse(a));
                }
                catch
                {
                    if (a != "")
                    {
                        GlobalTools.writeOnConsole(a + "  was not formatted correctly, remove spaces or weird characters from the bone IK list.",ConsoleColor.DarkRed);
                        closeAutomatically = false;
                    }
                }
            }
            #endregion
            if (arg.Length > 5)
            {
                ViewOutput = bool.Parse(arg[5]);
                IKBones = BonesIK.ToArray();
                bonesPath = arg[4];


            } else
            {
                ViewOutput = bool.Parse(arg[4]);
                IKBones = BonesIK.ToArray();
                bonesPath = arg[3];
            }
            closeAutomatically = ViewOutput == false;




            GlobalTools.writeOnConsole("Animation name: " + animationName, ConsoleColor.Green);
            if (loops)
                GlobalTools.writeOnConsole("Animation loops?: " + loops, ConsoleColor.Green);
            else
                GlobalTools.writeOnConsole("Animation loops?: " + loops, ConsoleColor.Red);
            if (IKBones.Length > 0)
            {
                foreach (var c in IKBones)
                    GlobalTools.writeOnConsole("Bone: " + c + " uses IK", ConsoleColor.Green);
            }
            GlobalTools.writeOnConsole("Uses .bones file from path: " + bonesPath, ConsoleColor.Green);


            List<string> sections = new List<string>();
            string[] split = File.ReadAllLines(infoPath);
            string ret = "";
            List<Header> data = new List<Header>();
            for (int i = 0; i < split.Length - 1; i++)
            {
                ret += split[i] + "\n";
                if (split[i + 1].Contains("BONE=") || split[i + 1].Contains("finish"))
                {
                    sections.Add(ret);
                    ret = "";
                }
            }
            for (int i = 0; i < sections.Count; i++)
            {
                sbyte bone = (sbyte)(byte.Parse(sections[i].Split('|')[0].Replace("BONE=", "").Replace("root", "0").Replace("Root", "0")) - 1);
                byte type = returnType(sections[i].Split('\n')[1]);
                string[] values = sections[i].Split('\n');
                if (type != 254)
                {
                    Header h = new Header();
                    List<float> kval = new List<float>();
                    List<float> km0 = new List<float>();
                    List<float> km1 = new List<float>();
                    List<int> ktime = new List<int>();
                    for (int c = 2; c < values.Length - 1; c++)
                    {
                        //Console.WriteLine(values[c] + "   " + c);
                        string[] val = values[c].Split('^');
                        int time = int.Parse(val[0].Replace(".0", ""));
                        float value = float.Parse(val[1], CultureInfo.InvariantCulture);
                        float m0 = float.Parse(val[2], CultureInfo.InvariantCulture);
                        float m1 = float.Parse(val[3], CultureInfo.InvariantCulture);
                        kval.Add(value);
                        km0.Add(m0);
                        km1.Add(m1);
                        ktime.Add(time);
                    }
                    h.type = type;
                    h.bone = bone;
                    h.oP = kval.ToArray();
                    h.oM0 = km0.ToArray();
                    h.oM1 = km1.ToArray();
                    h.absoluteTime = ktime.ToArray();
                    data.Add(h);
                }
            }
            File.Delete(infoPath);
            File.Delete(args[0]);
            string message = "";
            ConsoleColor color = ConsoleColor.Green;
            if (data.Count < 90)
            {
                color = ConsoleColor.Green;
                message = "This is a good amount of data!";
            }
            if (data.Count > 90)
            {
                color = ConsoleColor.Yellow;
                message = "Quite an excessive amount of data. The file might need optimisations.";
            }
            if (data.Count > 130)
            {
                color = ConsoleColor.Red;
                message = "Too much excessive amount of data. You will probably need to cleanup the animation to import it onto the game.";
            }
            GlobalTools.writeOnConsole(data.Count + " animation headers were created. " + message, color);
            GlobalTools.writeAtLine("", ConsoleColor.Yellow);
            MOTConvert.Convert(data, animationName, bonesPath, infoPath);
        }
        else
        {
            Console.WriteLine("No argument was satisfied. Closing now...");
            Thread.Sleep(1000);
            Environment.Exit(0);
        }
    }
    public static byte returnType(string identifier)
    {
        switch (identifier)
        {
            case "Location (X)":
                return 16;
            case "Location (Y)":
                return 17;
            case "Location (Z)":
                return 18;

            case "Rotation (Euler, X)":
                return 19;
            case "Rotation (Euler, Y)":
                return 20;
            case "Rotation (Euler, Z)":
                return 21;
        }
        return 254;
    }
}