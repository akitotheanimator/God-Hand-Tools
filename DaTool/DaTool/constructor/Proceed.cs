using System;
using System.CodeDom;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Xml.Linq;
using static GlobalTools;

public static class Proceed
{
    public static void ProceedStep(string file)
    {
        Console.WriteLine("-----------------\nReading file " + file + "...\nThe file is...");
        if (Path.GetExtension(file).Contains("dbp"))
        {
            int type = 0;



            Console.WriteLine("A Dat Body Package.");
            List<string> allFiles = Directory.GetFiles(Path.GetDirectoryName(file), "*", SearchOption.AllDirectories).ToList();
            List<string> top = Directory.GetFiles(Path.GetDirectoryName(file), "*", SearchOption.TopDirectoryOnly).ToList();
            foreach (var h in top)
            {
                for(int f = 0; f < allFiles.Count;f++)
                {
                    if(h == allFiles[f])
                    {
                        allFiles.RemoveAt(f);
                        f -= 1;
                    }
                }
            }


            string fType = "dat";

            byte tp = 0;
            using (FileStream fs = new FileStream(file, FileMode.Open))
            using (BinaryReader br = new BinaryReader(fs))
            {
                tp = br.ReadByte();
                Console.WriteLine("Type: " + tp + ".");
                fType = br.ReadString();
            }


            //Console.WriteLine(Path.GetFileNameWithoutExtension(allFiles[0]));

            allFiles.Sort((a, b) => int.Parse(Path.GetFileNameWithoutExtension(a)
                .Split('_')[1])
            .CompareTo(int.Parse(Path.GetFileNameWithoutExtension(b)
            .Split('_')[1])));


            string[] spli = Path.GetDirectoryName(file).Split('\\');
            Console.WriteLine(Path.GetDirectoryName(file) + "/" + spli[spli.Length - 1].Replace("_extracted", "") + fType);
            using (FileStream fs = new FileStream(Path.GetDirectoryName(file) + "/" + spli[spli.Length-1].Replace("_extracted","") + fType, FileMode.Create))
            using (BinaryWriter br = new BinaryWriter(fs))
            {
                if (tp != 2)
                {
                    br.Write(allFiles.Count);
                    List<uint> offsets = new List<uint>();



                    for (int a = 0; a < allFiles.Count; a++)
                    {
                        offsets.Add((uint)fs.Position);
                        br.Write(0);
                    }
                    for (int a = 0; a < allFiles.Count; a++)
                    {
                        br.Write(Encoding.UTF8.GetBytes(Path.GetExtension(allFiles[a]).Replace(".", "").Replace("dmy", "\0").ToUpper()));
                        while (fs.Position % 4 != 0)
                        {
                            br.Write((byte)0);
                        }
                    }
                    while (fs.Position % 16 != 0)
                    {
                        br.Write((byte)0);
                    }
                    for (int a = 0; a < allFiles.Count; a++)
                    {
                        uint lpos = (uint)fs.Position;
                        fs.Position = offsets[a];
                        if (!Path.GetExtension(allFiles[a]).Contains("dmy"))
                            br.Write(lpos);
                        fs.Position = lpos;

                        Console.WriteLine("Processing file " + Path.GetFileName(allFiles[a]) + ". " + (allFiles.Count - a - 1) + " Files remaining.");
                        br.Write(File.ReadAllBytes(allFiles[a]));
                    }
                } else
                {
                    ushort mC = 0;
                    foreach (var a in allFiles)
                    {
                        if (Path.GetExtension(a).Contains("act")) mC++;
                    }
                    br.Write(File.ReadAllBytes(allFiles[0]));
                    br.Write(mC);
                    br.Write(96);

                    var nameOffset = fs.Position;
                    br.Write(0);

                    var actorMotOffset = fs.Position;
                    br.Write(0);

                    var dataStartOffset = fs.Position;
                    br.Write(0);


                    br.Write(0);


                    #region people: "dayum he programs very well." me when i start programming anything:
                    List<long> sdhOffsets = new List<long>();
                    foreach (var a in allFiles)
                    {
                        if (Path.GetExtension(a).Contains("seq") || Path.GetExtension(a).Contains("dat"))
                        {
                            sdhOffsets.Add(fs.Position);
                            br.Write(0);
                        }
                    }

                    List<long> hOffsets = new List<long>();
                    foreach (var a in allFiles)
                    {
                        if (Path.GetExtension(a).Contains("hmot"))
                        {
                            hOffsets.Add(fs.Position);
                            //Console.WriteLine(fs.Position);
                            br.Write(0);
                        }
                    }
                    var bck = fs.Position;
                    fs.Position = nameOffset;
                    br.Write((uint)bck);
                    fs.Position = bck;

                    foreach (var a in allFiles)
                    {
                        if (Path.GetExtension(a).Contains("act")) br.Write(File.ReadAllBytes(a));
                    }
                    while (fs.Position % 16 != 0) br.Write((byte)0);

                    bck = fs.Position;
                    fs.Position = actorMotOffset;
                    br.Write((uint)bck);
                    fs.Position = bck;

                    List<long> motOffsets = new List<long>(); 
                    foreach (var a in allFiles)
                    {
                        if (Path.GetExtension(a).Contains("mot") && !Path.GetExtension(a).Contains("hmot"))
                        {
                            motOffsets.Add(fs.Position);
                            br.Write(0);
                        }
                    }
                    bck = fs.Position;
                    fs.Position = dataStartOffset;
                    br.Write((uint)bck);
                    fs.Position = bck;
                    uint count = 0;
                    foreach (var a in allFiles)
                    {
                        if (Path.GetExtension(a).Contains("hmot"))
                        {



                            uint lpos = (uint)fs.Position;
                            //Console.WriteLine(lpos);
                            fs.Position = hOffsets[(int)count];
                            if (File.ReadAllBytes(a).Length != 0)
                                br.Write(lpos);
                            else
                                br.Write(0);
                            fs.Position = lpos;



                            br.Write(File.ReadAllBytes(a));

                            count++;
                        }
                    }

                    count = 0;
                    foreach (var a in allFiles)
                    {
                        if (Path.GetExtension(a).Contains("mot") && !Path.GetExtension(a).Contains("hmot"))
                        {
                            uint lpos = (uint)fs.Position;
                            Console.WriteLine(motOffsets[(int)count]);
                            fs.Position = motOffsets[(int)count];
                            if (File.ReadAllBytes(a).Length != 0)
                                br.Write(lpos);
                            else
                                br.Write(0);
                            fs.Position = lpos;

                            //Console.WriteLine(a);
                            br.Write(File.ReadAllBytes(a));
                            count++;

                        }

                    }
                    count = 0;
                    foreach (var a in allFiles)
                    {

                        if (Path.GetExtension(a).Contains("seq") || Path.GetExtension(a).Contains("dat"))
                        {
                            uint lpos = (uint)fs.Position;
                            fs.Position = sdhOffsets[(int)count];
                            if (File.ReadAllBytes(a).Length != 0)
                                br.Write(lpos);
                            else
                                br.Write(0);
                            fs.Position = lpos;

                            //Console.WriteLine(a);



                            br.Write(File.ReadAllBytes(a));
                            count++;
                        }
                    }
                    #endregion
                }
            }
        }
        else
        {
            Console.WriteLine("A Raw file.\nReading format as a Dat package.");
            List<(string, byte[])> data = new List<(string, byte[])>();
            using (FileStream fs = new FileStream(file, FileMode.Open))
            using (BinaryReader br = new BinaryReader(fs))
            {
                GlobalTools.fs = fs;
                GlobalTools.br = br;

                #region type
                Console.Write("Dat type is...");
                int type = 0;
                if (readValue(readValue(4, NumberType.UINT), NumberType.UINT) == 0 &&
                    readValue(readValue(8, NumberType.UINT), NumberType.UINT) == 0 &&
                    readValue(readValue(12, NumberType.UINT), NumberType.UINT) == 0)
                    type = 1;

                if (readValue(0, NumberType.BYTE) == 1 && readValue(4, NumberType.BYTE) == 96)
                    type = 2;

                Console.Write(type + ".");
                Console.WriteLine();
                Console.WriteLine("Gathering files...");

                #endregion
                if (type != 2)
                {
                    if (type == 0 || type == 1)
                    {

                        uint fileOffset = 0;
                        fs.Position = 0;
                        if (1 > 3)
                        {
                            if (type == 1)
                            {
                                int strt = readValue(16, NumberType.INT);
                                fs.Position = 0;
                                data.Add(("FILE_CHUNK", br.ReadBytes(strt)));
                                fileOffset = (uint)strt;
                                fs.Position = strt; //easy as that, i can convert from type 0 to type 1. The start chunk will need to be saved.
                                                    //save file with the name as -1.
                            }
                        }

                        uint count = br.ReadUInt32();

                        Console.WriteLine(count + " files has been found.\nExtracting...");

                        #region get file offsets.
                        List<uint> offsets = new List<uint>();
                        for (int i = 0; i < count; i++)
                        {
                            offsets.Add(br.ReadUInt32() + fileOffset);
                        }
                        offsets.Add((uint)fs.Length); //the last file always goes from the start offset to the end of the file.
                        #endregion
                        #region get file names
                        List<string> names = new List<string>();
                        for (int i = 0; i < count; i++)
                        {
                            names.Add(readValue(fs.Position, NumberType.STRING));
                        }
                        names.Add("lol"); //this too.
                        List<(uint, string)> liNam = new List<(uint, string)>();
                        #endregion
                        for (int i = 0; i < offsets.Count; i++)
                        {
                            liNam.Add((offsets[i], names[i]));
                        }
                        for (int i = 0; i < liNam.Count - 1; i++)
                        {
                            fs.Position = liNam[i].Item1;
                            uint range = 0;

                            List<(uint, string)> tmplst = new List<(uint, string)>();
                            foreach(var f in liNam)
                            {
                                tmplst.Add(f);
                            }



                            tmplst.Sort((a, b) => a.Item1.CompareTo(b.Item1));
                            for (int g = 0; g < tmplst.Count; g++)
                            {
                                if (tmplst[g].Item1 == liNam[i].Item1)
                                {
                                    range = tmplst[g+1].Item1;
                                    break;
                                }
                            }
                            
                            int bCount = (int)(range - fs.Position);



                            if (liNam[i].Item1 == 0) bCount = 0;

                            //Console.WriteLine(liNam[i] + "    " + bCount);
                            data.Add((liNam[i].Item2, br.ReadBytes(bCount)));
                        }

                    }
                }
                else
                {
                    fs.Position = 0;
                    var v1 = br.ReadByte();
                    var v2 = br.ReadByte();

                    data.Add(("DNA", new byte[] {v1,v2}));

                    ushort actorCount = br.ReadUInt16();


                    uint SceneMotionAdresses = br.ReadUInt32();
                    uint SceneActorsAdress = br.ReadUInt32();
                    uint ActorMotsAdresses = br.ReadUInt32();




                    uint MotDataStartField = br.ReadUInt32();
                    fs.Position = 24;

                    List<(string, uint)> adressesSEQ = new List<(string, uint)>();
                    while (fs.Position < SceneMotionAdresses)
                    {
                        //Console.WriteLine(fs.Position);
                        adressesSEQ.Add(("SEQ", br.ReadUInt32()));
                    }
                    var ga = adressesSEQ[1];
                    ga.Item1 = "DAT";
                    adressesSEQ[1] = ga;
                    adressesSEQ.Add(("SEQ",(uint)fs.Length));
                    var backup = fs.Position;

                    for(int sfSE = 0; sfSE < adressesSEQ.Count-1;sfSE++)
                    {
                        
                        fs.Position = adressesSEQ[sfSE].Item2;
                        //Console.WriteLine(fs.Position);
                        uint range = adressesSEQ[sfSE+1].Item2;


                        if (range == 0)
                        {
                            for (int f = sfSE + 1; f < adressesSEQ.Count; f++)
                                if (adressesSEQ[f].Item2 != 0)
                                {
                                    range = adressesSEQ[f].Item2;
                                    break;
                                }

                        }
                        int bCount = (int)(range - adressesSEQ[sfSE].Item2);
                        if (fs.Position == 0) bCount = 0;


                        //Console.WriteLine(adressesSEQ[sfSE].Item2 + "      " + range);


                        data.Add((adressesSEQ[sfSE].Item1, br.ReadBytes(bCount)));
                        if (1 > 4)
                        {
                            fs.Position = sfSE;
                            if (adressesSEQ[sfSE].Item2 != 0)
                            {
                                if (adressesSEQ[sfSE + 1].Item2 == 0)
                                {
                                    for (int g = sfSE; g < adressesSEQ.Count - 1; g++)
                                    {

                                    }
                                }
                                else
                                {
                                    data.Add(("SEQ", br.ReadBytes((int)(adressesSEQ[sfSE + 1].Item2 - adressesSEQ[sfSE].Item2))));
                                }
                            }
                            else
                            {
                                data.Add(("SEQ", br.ReadBytes(0)));
                            }
                        }
                    }

                    fs.Position = backup;




                    List<(string, uint)> adresseshMots = new List<(string, uint)>();
                    while (fs.Position < SceneActorsAdress)
                    {
                        adresseshMots.Add(("HMOT", br.ReadUInt32()));
                    }



                    // backup = fs.Position;
                    List<(string, byte[])> ab = new List<(string, byte[])>();
                    for (int g = 0; g < actorCount;g++)
                    {
                        byte[] allbytes = br.ReadBytes(8);
                        ab.Add(("ACT", allbytes));
                        //data.Add(("ACT",allbytes));
                    }
                    while (fs.Position%16!=0) fs.Position += 1;
                    while (fs.Position < MotDataStartField)
                    {
                        adresseshMots.Add(("MOT", br.ReadUInt32()));
                    }


                    foreach (var f in adressesSEQ)
                    {
                        if (f.Item2 != 0)
                        {
                            adresseshMots.Add(("yotto", f.Item2));
                            break;
                        }
                    }

                    for (int sfSE = 0; sfSE < adresseshMots.Count - 1; sfSE++)
                    {

                        fs.Position = adresseshMots[sfSE].Item2;
                        //Console.WriteLine(fs.Position);
                        uint range = adresseshMots[sfSE + 1].Item2;


                        if (range == 0)
                        {
                            for (int f = sfSE + 1; f < adresseshMots.Count; f++)
                                if (adresseshMots[f].Item2 != 0)
                                {
                                    //Console.WriteLine(adresseshMots[sfSE].Item2 + "      " + adresseshMots[f].Item2);
                                    range = adresseshMots[f].Item2;
                                    break;
                                }

                        }
                        int bCount = (int)(range - adresseshMots[sfSE].Item2);
                        if (fs.Position == 0) bCount = 0;

                        //Console.WriteLine(adresseshMots[sfSE].Item2 + "      " + adresseshMots[sfSE + 1].Item2);
                        data.Add((adresseshMots[sfSE].Item1, br.ReadBytes(bCount)));
                    }
                    foreach(var a in ab)
                    {
                        data.Add(a);
                    }




                    if (1 > 3)
                    {


                        //uint sv2 = br.ReadUInt32();
                        //uint DatStartField = br.ReadUInt32();



                        //adressesHead.Add(DatStartField);



                        List<uint> adressesSceneMot = new List<uint>();
                    while (fs.Position < SceneActorsAdress)
                    {
                        adressesSceneMot.Add(br.ReadUInt32());
                    }



                        List<(string, uint)> Actors = new List<(string, uint)>();
                        for (int i = 0; i < actorCount; i++)
                        {
                            Actors.Add((readValue(fs.Position, NumberType.STRING), readValue(fs.Position + 4, NumberType.UINT)));
                            fs.Position += 8;
                        }






                        fs.Position = ActorMotsAdresses;

                        List<uint> Mots = new List<uint>();
                        while (fs.Position < MotDataStartField)
                        {
                            Mots.Add(br.ReadUInt32());
                        }

                        foreach (var g in adressesSEQ)
                        {

                        }

                    }

                }
                createFile(file, data.ToArray(), (byte)type);
            }

        }




        //Console.ReadLine();
    }
    public static void createFile(string filePath, (string, byte[])[] data,byte type)
    {
        string folder = Path.GetDirectoryName(filePath);
        string name = Path.GetFileNameWithoutExtension(filePath);
        Directory.CreateDirectory(folder + "/" + name + "_extracted");

        folder = folder + "/" + name + "_extracted/";



        uint cname = 0;
        for (int i = 0; i < data.Length;i++)
        {
            if (data[i].Item1 == "FILE_CHUNK")
            {
                Console.WriteLine("Processing file FILE_CHUNK. " + (data.Length - i - 1) + " Files remaining.");


                var f = File.Create(folder + "FILE_CHUNK");
                f.Write(data[i].Item2,0, data[i].Item2.Length);
                //var f = File.Create();
            } else
            {
                if (data[i].Item1 != "")
                {
                    Console.WriteLine("Processing file " + data[i].Item1 + "/" + data[i].Item1 + "_" + cname + "." + data[i].Item1.ToLower() + ". " + (data.Length - i - 1) + " Files remaining.");
                    Directory.CreateDirectory(folder + data[i].Item1);
                    using (FileStream fs = new FileStream(folder + data[i].Item1 + "/" + data[i].Item1 + "_" + cname + "." + data[i].Item1.ToLower(), FileMode.Create))
                    using (BinaryWriter bw = new BinaryWriter(fs))
                        bw.Write(data[i].Item2);
                    cname++;
                }
                else
                {
                    Console.WriteLine("Processing file " + "DMY_" + cname + ".dmy. " + (data.Length - i - 1) + " Files remaining.");

                    Directory.CreateDirectory(folder + "DMY");
                    using (FileStream fs = new FileStream(folder + "DMY/" + "DMY_" + cname + ".dmy", FileMode.Create))
                    using (BinaryWriter bw = new BinaryWriter(fs))
                        bw.Write(data[i].Item2);
                    cname++;
                }
            }
            
        }


        using (FileStream fs = new FileStream(folder + "Body.dbp", FileMode.Create))
        using (BinaryWriter bw = new BinaryWriter(fs))
        {
            bw.Write(type);
            bw.Write(Path.GetExtension(filePath));
        }
        


        Console.WriteLine("Done.");
        //Program.repeat(new string[0]);

    }
}