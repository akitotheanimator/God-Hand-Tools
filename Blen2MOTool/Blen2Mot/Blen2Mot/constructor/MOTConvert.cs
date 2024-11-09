using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Policy;
using System.Text;
using System.Threading.Tasks;
using System.Numerics;
using System.Diagnostics.Eventing.Reader;
public static class MOTConvert
{
    public static BONES[] bones_;
    public static void Convert(List<Header> motHeader, string animationName, string bonePath, string exportPath)
    {
        int allTime = 0;
        GlobalTools.writeOnConsole("Loading .Bones... ", ConsoleColor.Yellow);
        #region load .bones
        try
        {
            List<BONES> bnl = new List<BONES>();
            using (FileStream fs = new FileStream(bonePath, FileMode.Open))
            using (BinaryReader br = new BinaryReader(fs))
            {

                for (int i = 0; i < fs.Length; i += 16)
                {
                    BONES bn = new BONES();
                    bn.pos = new Vector3(GlobalTools.readValue(fs, br, i, GlobalTools.NumberType.SINGLE), GlobalTools.readValue(fs, br, i + 4, GlobalTools.NumberType.SINGLE), GlobalTools.readValue(fs, br, i + 8, GlobalTools.NumberType.SINGLE));
                    bn.parentingOrder = GlobalTools.readValue(fs, br, i + 12, GlobalTools.NumberType.SHORT);
                    bn.id = GlobalTools.readValue(fs, br, i + 14, GlobalTools.NumberType.SHORT);
                    bnl.Add(bn);
                }
            }
            bones_ = bnl.ToArray();
        } catch(Exception e)
        {
            GlobalTools.writeOnConsole("Failed to load .Bones file. This may be the reason: " + e, ConsoleColor.Red);
        }
        #endregion
        GlobalTools.writeOnConsole("Loaded .Bones sucessfully! ", ConsoleColor.Green);
        GlobalTools.writeOnConsole("Calculating header values...", ConsoleColor.Yellow);
        try
        {
            foreach (var h in motHeader)
            {
                if (h.absoluteTime[h.absoluteTime.Length - 1] > allTime) allTime = h.absoluteTime[h.absoluteTime.Length - 1];
                string bone = "";
                if (h.bone + 1 == 0)
                    bone = "root";
                else
                    bone = (h.bone + 1).ToString();
                GlobalTools.writeAtLine("Calculating values of bone: " + bone + " Of type: " + GlobalTools.returnType(h.type) + ".", ConsoleColor.Yellow);
                h.calculateHeaderValues();
                GlobalTools.writeOnConsole(" Sucess!",ConsoleColor.Green);
            }
        } catch(Exception e)
        {
            GlobalTools.writeOnConsole("Failed to calculate the header values. This may be the reason: " + e, ConsoleColor.Red);
        }
        GlobalTools.writeOnConsole("Sorting header...", ConsoleColor.Green);
        motHeader.Sort((a, b) => a.bone.CompareTo(b.bone));
        GlobalTools.writeOnConsole("Sorting types...", ConsoleColor.Green);
        List<Header> sortedTypes = motHeader.GroupBy(x => x.bone).Select(g => g.OrderBy(x => x.type)).SelectMany(g => g).ToList();
        GlobalTools.writeOnConsole("Exporting...", ConsoleColor.Green);
        Export(Path.GetDirectoryName(exportPath) + "/" + animationName + ".MOT", sortedTypes.ToArray(),allTime);
    }
    public static void Export(string path, Header[] data,int allTime)
    {
        List<uint> AdressOffset = new List<uint>();
        List<uint> Offsets = new List<uint>();
        using (FileStream fs = new FileStream(path, FileMode.Create))
        using (BinaryWriter bn = new BinaryWriter(fs))
        {
            GlobalTools.writeOnConsole("Writting header...", ConsoleColor.Yellow);
            bn.Write(862090349);
            bn.Write((ushort)allTime);
            bn.Write((byte)(data.Length+1));

            bn.Write((byte)(Program.loops? 1 : 0));

            for(int i = 0; i < data.Length;i++)
            {
                bn.Write((sbyte)data[i].bone);

                if(data[i].bone == -1 && data[i].type == 17)
                bn.Write((byte)1);
                else
                    bn.Write(data[i].type);


                bn.Write((ushort)(data[i].curves.Length+1));
                if(Program.IKBones.Length > 0)
                {
                    int match = 0;
                    foreach(var ik in Program.IKBones)
                    {
                        if (ik == data[i].bone)
                        {
                            match++; bn.Write((int)1); break;
                        }
                    }
                    if(match == 0)
                    {
                        bn.Write((int)0);
                    }

                }
                else
                {
                    bn.Write((int)0);
                }
                if (data[i].bone == -1 && data[i].type == 17)
                {
                }
                else
                {
                    AdressOffset.Add((uint)fs.Position);
                }
                bn.Write((int)0);
            }
            bn.Write((long)4294967167);
            bn.Write((int)0);
            GlobalTools.writeOnConsole("done!", ConsoleColor.Green);
            GlobalTools.writeOnConsole("Writting keyframe data...", ConsoleColor.Yellow);
            for (int i = 0; i < data.Length;i++)
            {
                if (data[i].bone == -1 && data[i].type == 17)
                {
                }else
                {
                    Offsets.Add((uint)fs.Position);
                    bn.Write(data[i].p);
                    bn.Write(data[i].dp);
                    bn.Write(data[i].m0);
                    bn.Write(data[i].dm0);
                    bn.Write(data[i].m1);
                    bn.Write(data[i].dm1);
                    for (int o = 0; o < data[i].curves.Length; o++)
                    {
                        bn.Write(data[i].curves[o].time);
                        bn.Write(data[i].curves[o].cp);
                        bn.Write(data[i].curves[o].cm0);
                        bn.Write(data[i].curves[o].cm1);
                    }
                }
            }
            Console.WriteLine(AdressOffset.Count + "  " + Offsets.Count);
            GlobalTools.writeOnConsole("done!", ConsoleColor.Green);
            GlobalTools.writeOnConsole("Writting calculated offsets...", ConsoleColor.Yellow);
            for (int i = 0; i < AdressOffset.Count; i++)
            {
                fs.Position = AdressOffset[i];
                //Console.WriteLine(data[i].bone + "  " + data[i].type);
                    bn.Write(Offsets[i]);
            }
            GlobalTools.writeOnConsole("done!", ConsoleColor.Green);
        }
        GlobalTools.writeOnConsole("Animation " + path + " created sucessfully!", ConsoleColor.Green);
        if (!Program.closeAutomatically)
        {
            GlobalTools.writeOnConsole("Press Enter to close the console...", ConsoleColor.Green);
            Console.ReadLine();
        }
        Environment.Exit(0);
    }
}