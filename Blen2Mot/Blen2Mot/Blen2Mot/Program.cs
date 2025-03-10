﻿using System;
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
    public static bool isFullPrecision;

    public static bool import;

    public static BONES[] bones;


    static void Main(string[] args)
    {

        if (args.Length == 0)
        {
            Console.WriteLine("No argument was satisfied. Closing now...");
            Thread.Sleep(1000);
            Environment.Exit(0);
        }
        import = bool.Parse(args[1]);
        if (import == false)
        {
            string[] arg = File.ReadAllLines(args[0]);
            File.Delete(args[0]);

            List<byte> BonesIK = new List<byte>();
            string infoPath = arg[0];
            string animationName = arg[1];
            string bonesPath = arg[4];
            bones = GlobalTools.readBones(bonesPath);
            isFullPrecision = bool.Parse(arg[6]);
            //Console.WriteLine(isFullPrecision);
            string[] ikboneSplit = new string[] { };
            if (arg[3] != "")
                ikboneSplit = arg[3].Split(',');
            //Console.WriteLine(arg[2]);
            loops = bool.Parse(arg[2]);
            infoPath = arg[0];
            animationName = arg[1];
            #region bones

            foreach (var a in ikboneSplit)
            {
                try
                {
                    BonesIK.Add((byte)(byte.Parse(a) - (byte)(3)));
                }
                catch
                {
                    if (a != "")
                    {
                        GlobalTools.writeOnConsole(a + "  was not formatted correctly, remove spaces or weird characters from the bone IK list.", ConsoleColor.DarkRed);
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


            }
            else
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

            File.Delete(infoPath);


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
                    if (3 > 4)
                    {
                        if (h.bone == -1 && GlobalTools.returnType(h.type).Contains("rotation"))
                        {
                            Console.WriteLine("WARNING: Root bone has animated rotation. The program will ignore the root bone rotation curves to avoid the animation to break entirely.\nPress any key to continue.");
                            Console.ReadLine();
                        }
                        else
                        {
                            data.Add(h);
                        }
                    }
                    data.Add(h);
                }
            }
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
            MOTConvert.Convert(data, animationName, infoPath);
        }
        else
        {
            bones = GlobalTools.readBones(args[2]);


            using (FileStream fs = new FileStream(args[0], FileMode.Open))
            using (BinaryReader bnr = new BinaryReader(fs))
            {
                fs.Position = 0;
                if (bnr.ReadInt32() != 862090349)
                {
                    Console.WriteLine("The file isn't a MOT file!");
                    Thread.Sleep(1000);
                    Environment.Exit(0);
                }
                ushort totalFrameCount = GlobalTools.readValue(fs, bnr, 4, GlobalTools.NumberType.USHORT);
                byte totalPropertyCount = GlobalTools.readValue(fs, bnr, 6, GlobalTools.NumberType.BYTE);
                byte Loops = GlobalTools.readValue(fs, bnr, 7, GlobalTools.NumberType.BYTE);





                List<Header> headers = new List<Header>();
                #region get headers n stuff
                for (long i = 8; i < (long)((totalPropertyCount * 12) + 8); i += 12)
                {
                    Header head = new Header();
                    head.bone = GlobalTools.readValue(fs, bnr, i + 0, GlobalTools.NumberType.SBYTE);
                    head.type = GlobalTools.readValue(fs, bnr, i + 1, GlobalTools.NumberType.BYTE);
                    head.keyframeCount = GlobalTools.readValue(fs, bnr, i + 2, GlobalTools.NumberType.USHORT);
                    head.usesRootSpace = GlobalTools.readValue(fs, bnr, i + 4, GlobalTools.NumberType.UINT);
                    if (head.type > 10)
                        head.adress = GlobalTools.readValue(fs, bnr, i + 8, GlobalTools.NumberType.UINT);
                    else
                        head.oP = new float[1] { GlobalTools.readValue(fs, bnr, i + 8, GlobalTools.NumberType.SINGLE) };
                    //Console.WriteLine(head.adress + "   " + i);
                    //if(head.keyframeCount != 65535)
                    if (!GlobalTools.returnType(head.type).Contains("not computed."))
                        headers.Add(head);
                }
                using (FileStream fs1 = new FileStream(args[0].Replace(".mot", ".BTE0").Replace(".MOT", ".BTE0"), FileMode.Create))
                using (BinaryWriter bw1 = new BinaryWriter(fs1))
                {


                    #endregion
                    List<(int, bool)> queueList = new List<(int, bool)>();
                    bw1.Write(headers.Count);
                    for (int i = 0; i < headers.Count; i++)
                    {
                        //quantized data + the keyframe count
                        //bw1.Write((byte)254);
                        bw1.Write(headers[i].bone);
                        bw1.Write(headers[i].type);
                        long psL = fs1.Position;
                        bw1.Write(0);
                        List<dynamic> vals = new List<dynamic>();

                        fs.Position = headers[i].adress;
                        if (headers[i].type < 80)
                        {

                            if (headers[i].usesRootSpace != 0)
                            {
                                queueList.Add((headers[i].bone + 3, false));
                            }
                            for (int o = 0; o < queueList.Count; o++)
                            {
                                if (queueList[o].Item2 == true && queueList[o].Item1 != headers[i].bone)
                                {
                                    queueList.Remove(queueList[o]);
                                    o -= 1;
                                }
                            }
                            if (headers[i].type > 10)
                            {
                                float PMin = IEEEBinary16.FromUShort(GlobalTools.readValue(fs, bnr, headers[i].adress + 0, GlobalTools.NumberType.USHORT));
                                float PMax = IEEEBinary16.FromUShort(GlobalTools.readValue(fs, bnr, headers[i].adress + 2, GlobalTools.NumberType.USHORT));

                                float M0Min = IEEEBinary16.FromUShort(GlobalTools.readValue(fs, bnr, headers[i].adress + 4, GlobalTools.NumberType.USHORT));
                                float M0Max = IEEEBinary16.FromUShort(GlobalTools.readValue(fs, bnr, headers[i].adress + 6, GlobalTools.NumberType.USHORT));

                                float M1Min = IEEEBinary16.FromUShort(GlobalTools.readValue(fs, bnr, headers[i].adress + 8, GlobalTools.NumberType.USHORT));
                                float M1Max = IEEEBinary16.FromUShort(GlobalTools.readValue(fs, bnr, headers[i].adress + 10, GlobalTools.NumberType.USHORT));

                                uint timeAbsolute = 0;

                                for (long c = headers[i].adress + 12; c < headers[i].adress + (12 + (headers[i].keyframeCount * 4)); c += 4)
                                {
                                    timeAbsolute += GlobalTools.readValue(fs, bnr, c + 0, GlobalTools.NumberType.BYTE);
                                    float p0 = PMin + PMax * GlobalTools.readValue(fs, bnr, c + 1, GlobalTools.NumberType.BYTE);
                                    float m0 = M0Min + M0Max * GlobalTools.readValue(fs, bnr, c + 2, GlobalTools.NumberType.BYTE);
                                    float m1 = M1Min + M1Max * GlobalTools.readValue(fs, bnr, c + 3, GlobalTools.NumberType.BYTE);

                                    //Console.WriteLine(a.bone + "      " + (a.bone + 1) +"   " + bones[a.bone + 1].pos + "    " + a.usesRootSpace);
                                    int matches = 0;
                                    for (int o = 0; o < queueList.Count; o++)
                                    {
                                        if (queueList[o].Item1 == headers[i].bone + 1)
                                        {
                                            matches++;
                                            //Console.WriteLine(a.bone + "   " + a.type);
                                            var f = queueList[o];
                                            f.Item2 = true;
                                            queueList[o] = f;

                                            switch (headers[i].type)
                                            {
                                                case 16:
                                                    p0 = bones[0].pos.X + p0; break;
                                                case 17:
                                                    p0 = bones[0].pos.Y + p0; break;
                                                case 18:
                                                    p0 = bones[0].pos.Z + p0; break;
                                            }
                                            break;
                                        }
                                    }
                                    if (matches == 0)
                                    {
                                        switch (headers[i].type)
                                        {
                                            case 16:
                                                p0 -= bones[headers[i].bone + 1].pos.X;
                                                break;
                                            case 17:
                                                p0 -= bones[headers[i].bone + 1].pos.Y;
                                                break;
                                            case 18:
                                                p0 -= bones[headers[i].bone + 1].pos.Z;
                                                break;
                                        }
                                    }

                                    vals.Add(timeAbsolute);
                                    vals.Add(p0);
                                    vals.Add(m0);
                                    vals.Add(m1);
                                }
                            }
                            else
                            {
                                float zero = 0;
                                float v = headers[i].oP[0];


                                int matches = 0;
                                for (int o = 0; o < queueList.Count; o++)
                                {
                                    if (queueList[o].Item1 == headers[i].bone + 1)
                                    {
                                        matches++;
                                        var f = queueList[o];
                                        f.Item2 = true;
                                        queueList[o] = f;

                                        switch (headers[i].type)
                                        {
                                            case 0:
                                                v = bones[0].pos.X + v; break;
                                            case 1:
                                                v = bones[0].pos.Y + v; break;
                                            case 2:
                                                v = bones[0].pos.Z + v; break;
                                        }
                                        break;
                                    }
                                }
                                if (matches == 0)
                                {

                                    switch (headers[i].type)
                                    {
                                        case 0:
                                            v -= bones[headers[i].bone + 1].pos.X;
                                            break;
                                        case 1:
                                            v -= bones[headers[i].bone + 1].pos.Y;
                                            break;
                                        case 2:
                                            v -= bones[headers[i].bone + 1].pos.Z;
                                            break;
                                    }
                                }
                                vals.Add(zero);
                                vals.Add(v);
                                vals.Add(zero);
                                vals.Add(zero);
                            }
                        }
                        else
                        {
                            for (long c = headers[i].adress; i < headers[i].adress + (headers[i].keyframeCount * 16); c += 16)
                            {
                                ushort t = GlobalTools.readValue(fs, bnr, c + 0, GlobalTools.NumberType.USHORT);
                                float p0 = GlobalTools.readValue(fs, bnr, c + 4, GlobalTools.NumberType.SINGLE);
                                float m0 = GlobalTools.readValue(fs, bnr, c + 8, GlobalTools.NumberType.SINGLE);
                                float m1 = GlobalTools.readValue(fs, bnr, c + 12, GlobalTools.NumberType.SINGLE);

                                int matches = 0;
                                for (int o = 0; o < queueList.Count; o++)
                                {
                                    if (queueList[o].Item1 == headers[i].bone + 1)
                                    {
                                        matches++;
                                        //Console.WriteLine(a.bone + "   " + a.type);
                                        var f = queueList[o];
                                        f.Item2 = true;
                                        queueList[o] = f;

                                        switch (headers[i].type)
                                        {
                                            case 16:
                                                p0 = bones[0].pos.X + p0; break;
                                            case 17:
                                                p0 = bones[0].pos.Y + p0; break;
                                            case 18:
                                                p0 = bones[0].pos.Z + p0; break;
                                        }
                                        break;
                                    }
                                }
                                if (matches == 0)
                                {
                                    switch (headers[i].type)
                                    {
                                        case 16:
                                            p0 -= bones[headers[i].bone + 1].pos.X;
                                            break;
                                        case 17:
                                            p0 -= bones[headers[i].bone + 1].pos.Y;
                                            break;
                                        case 18:
                                            p0 -= bones[headers[i].bone + 1].pos.Z;
                                            break;
                                        case 80:
                                            p0 += bones[headers[i].bone + 1].pos.X; break;
                                        case 81:
                                            p0 += bones[headers[i].bone + 1].pos.Y; break;
                                        case 82:
                                            p0 += bones[headers[i].bone + 1].pos.Z; break;
                                    }
                                }

                                vals.Add(t);
                                vals.Add(p0);
                                vals.Add(m0);
                                vals.Add(m1);
                            }
                        }

                        long bk = fs1.Position;
                        fs1.Position = psL;
                        bw1.Write(vals.Count);
                        fs1.Position = bk;
                        for (int g = 0; g < vals.Count; g+=4)
                        {
                            bw1.Write((uint)vals[g]);
                            bw1.Write((float)vals[g+1]);
                            bw1.Write((float)vals[g+2]);
                            bw1.Write((float)vals[g+3]);
                        }
                        vals.Clear();
                    }
                    fs1.Close();
                }
            }
        }
        //Console.ReadLine();
    }
    public static byte returnType(string identifier)
    {
        if (!isFullPrecision)
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
        else
            switch (identifier)
            {
                case "Location (X)":
                    return 80;
                case "Location (Y)":
                    return 81;
                case "Location (Z)":
                    return 82;

                case "Rotation (Euler, X)":
                    return 83;
                case "Rotation (Euler, Y)":
                    return 84;
                case "Rotation (Euler, Z)":
                    return 85;
            }
        return 254;
    }
}