using System;
using System.Diagnostics;
using System.IO;
using System.Xml.Linq;



public static class EOP
{
    #region convert wav to vag, vag to wav and etc.
    public static void CW(string filePath)
    {
        using (FileStream fs = new FileStream(filePath, FileMode.Open))
        using (BinaryReader bn = new BinaryReader(fs))
        {
            if (GlobalTools.readValue(fs, bn, 0, GlobalTools.NumberType.INT) == 1179011410)
            {

                if (GlobalTools.readValue(fs, bn, 22, GlobalTools.NumberType.SHORT) == 1)
                {
                    GlobalTools.changeColor(ConsoleColor.Green);
                    Console.WriteLine("Correct sampling rate! converting...");
                    Process.Start(Directory.GetCurrentDirectory() + "/MFAudio.exe", $" /OTVAGC \"{filePath}\" \"{filePath.Replace('/', '\\').Replace(".wav", ".vag")}\"");
                }
                else
                {
                    GlobalTools.changeColor(ConsoleColor.Red);
                    Console.WriteLine("The file channels is stereo when it should be mono. The file will be skipped.");
                }
            }
            else
            {
                GlobalTools.changeColor(ConsoleColor.Red);
                Console.WriteLine("This is not a .wav file. skipping.");
            }
        }
    }
    public static void CV(string filePath)
    {
        using (FileStream fs = new FileStream(filePath, FileMode.Open))
        using (BinaryReader bn = new BinaryReader(fs))
        {
            if (GlobalTools.readValue(fs, bn, 0, GlobalTools.NumberType.INT) == 1883717974)
            {
                GlobalTools.changeColor(ConsoleColor.Green);
                Console.WriteLine("Converting vag...");
                Process.Start(Directory.GetCurrentDirectory() + "/MFAudio.exe", $" /OTWAVU \"{filePath}\" \"{filePath.Replace('/', '\\').Replace(".vag", ".wav")}\"");
            }
            else
            {
                GlobalTools.changeColor(ConsoleColor.Red);
                Console.WriteLine("This is not a .vag file. skipping.");
            }
        }
    }
    #endregion
    public static void EF(string filePath)
    {
        Directory.CreateDirectory(filePath.Replace(Path.GetFileName(filePath), Path.GetFileNameWithoutExtension(filePath) + "_SES_CONVERTED/VAG/"));
        Directory.CreateDirectory(filePath.Replace(Path.GetFileName(filePath), Path.GetFileNameWithoutExtension(filePath) + "_SES_CONVERTED/WAV/"));

        List<Info> Infos = new List<Info>();
        using (FileStream fs = new FileStream(filePath, FileMode.Open))
        using (BinaryReader bn = new BinaryReader(fs))
        {
            if (Path.GetExtension(filePath).Contains("ses"))
            {
                if (GlobalTools.readValue(fs, bn, 0, GlobalTools.NumberType.LONG) == 4579260101974771027)
                {
                    uint headerStartOffset = GlobalTools.readValue(fs, bn, 32, GlobalTools.NumberType.UINT);
                    uint headerCount = GlobalTools.readValue(fs, bn, 36, GlobalTools.NumberType.UINT); //header data length
                    uint audioStartOffset = GlobalTools.readValue(fs, bn, 40, GlobalTools.NumberType.UINT); //the offset that the audio data starts to be written
                    uint audioCount = GlobalTools.readValue(fs, bn, 44, GlobalTools.NumberType.UINT);//audio data length

                    #region gather header info
                    uint headerEnd = headerStartOffset + headerCount;
                    for (uint i = headerStartOffset; i < headerEnd; i += 16)
                    {
                        Info f = new Info();
                        f.offset = GlobalTools.readValue(fs, bn, i + 0, GlobalTools.NumberType.UINT) + audioStartOffset;
                        f.sampleRate = GlobalTools.readValue(fs, bn, i + 4, GlobalTools.NumberType.UINT);
                        f.number = GlobalTools.readValue(fs, bn, i + 8, GlobalTools.NumberType.UINT);
                        f.loops = GlobalTools.readValue(fs, bn, i + 12, GlobalTools.NumberType.UINT);
                        f.name = (int)(i - headerStartOffset) / 16;


                        if (f.offset < fs.Length &&
                            GlobalTools.readValue(fs, bn, f.offset, GlobalTools.NumberType.LONG) == 0 &&
                            GlobalTools.readValue(fs, bn, i + 4, GlobalTools.NumberType.LONG) != 0)
                        {
                            Infos.Add(f);
                        }
                    }
                    #endregion
                    #region txt thingy
                    string nameBoRM = filePath.Replace(Path.GetFileName(filePath), Path.GetFileNameWithoutExtension(filePath) + "_SES_CONVERTED/DO NOT READ ME.txt"); //ses body
                    using (FileStream fso = new FileStream(nameBoRM, FileMode.Create))
                    { }
                    string[] s = new string[] { "this .sbo, .sbe and .table files are the body of the .ses, in other words... if you want to be able to mod the game audios, do NOT delete these files!!!" };
                    File.WriteAllLines(nameBoRM, s);
                    #endregion



                    #region sorting
                    Infos.Sort((a, b) => a.offset.CompareTo(b.offset)); //sorts offsets by ascendent order
                    for (int i = 0; i < Infos.Count; i++)
                    {
                        List<byte> d = new List<byte>();
                        Infos[i].file = i;
                        if (i + 1 < Infos.Count)
                        {
                            for (uint o = Infos[i].offset + 16; o < Infos[i + 1].offset; o++)
                            {
                                d.Add(GlobalTools.readValue(fs, bn, o, GlobalTools.NumberType.BYTE));
                            }
                        }
                        else
                        {
                            for (uint o = Infos[i].offset; o < (audioStartOffset + audioCount); o++)
                            {
                                d.Add(GlobalTools.readValue(fs, bn, o, GlobalTools.NumberType.BYTE));
                            }
                        }
                        Infos[i].data = d.ToArray();
                    }
                    Infos.Sort((a, b) => a.name.CompareTo(b.name)); //sorts again but by name instead, so it can preserve the offsets order
                    #endregion

                    #region create the .ses body for modding
                    CSB(filePath, (int)audioStartOffset, (int)(audioCount + audioStartOffset), bn, fs, Infos);
                    #endregion
                    for (int i = 0; i < Infos.Count; i++)
                    {
                        GlobalTools.changeColor(ConsoleColor.Yellow);
                        if (Infos[i].data.Length > 0)
                        {
                            string name = filePath.Replace(Path.GetFileName(filePath), Path.GetFileNameWithoutExtension(filePath) + "_SES_CONVERTED/VAG/" + Infos[i].file + ".vag");
                            using (FileStream fso = new FileStream(name, FileMode.Create))
                            using (BinaryWriter bno = new BinaryWriter(fso))
                            {
                                #region vag header stuff
                                bno.Write((int)1883717974);
                                bno.Write((int)50331648);
                                bno.Write((int)0);
                                #endregion



                                #region the 8 bytes of samplerate
                                uint unknown = Infos[i].sampleRate;
                                byte[] bytes_unknown = BitConverter.GetBytes(unknown);
                                Array.Reverse(bytes_unknown);
                                bno.Write(bytes_unknown);


                                uint sampleRate = Infos[i].sampleRate;
                                byte[] bytes = BitConverter.GetBytes(sampleRate);
                                Array.Reverse(bytes);
                                bno.Write(bytes);
                                #endregion
                                #region fill blank space
                                for (int o = 0; o < 7; o++)
                                {
                                    bno.Write((int)0);
                                }
                                #endregion
                                #region data fill
                                bno.Write(Infos[i].data);
                                #endregion
                            }
                            #region convert
                            string name2 = filePath.Replace(Path.GetFileName(filePath), Path.GetFileNameWithoutExtension(filePath) + "_SES_CONVERTED/WAV/" + Infos[i].name + ".vag");
                            Process.Start(Directory.GetCurrentDirectory() + "/MFAudio.exe", $" /OTWAVU \"{name.Replace('/', '\\')}\" \"{name2.Replace('/', '\\').Replace(".vag", ".wav")}\"");
                            GlobalTools.changeColor(ConsoleColor.Green);
                            Console.WriteLine($"saved file to path {name2.Replace('/', '\\').Replace(".vag", ".wav")}!");
                            #endregion
                        }
                        else
                        {
                            File.Create(filePath.Replace(Path.GetFileName(filePath), Path.GetFileNameWithoutExtension(filePath) + "_SES_CONVERTED/VAG/" + Infos[i].file + "_DUMMY"));
                        }
                    }
                }
                else
                {
                    GlobalTools.changeColor(ConsoleColor.Yellow);
                    Console.WriteLine(filePath + " wasn't a .ses file! skipping...");
                }
            }
            else
            {
                GlobalTools.changeColor(ConsoleColor.Yellow);
                Console.WriteLine(filePath + " wasn't a .ses file! skipping...");
            }
        }
    }
    public static void REOT(string filePath)
    {
        Directory.CreateDirectory(filePath.Replace(Path.GetFileName(filePath), Path.GetFileNameWithoutExtension(filePath) + "_SES_CONVERTED/VAG/"));
        Directory.CreateDirectory(filePath.Replace(Path.GetFileName(filePath), Path.GetFileNameWithoutExtension(filePath) + "_SES_CONVERTED/WAV/"));

        List<Info> Infos = new List<Info>();
        using (FileStream fs = new FileStream(filePath, FileMode.Open))
        using (BinaryReader bn = new BinaryReader(fs))
        {
            if (Path.GetExtension(filePath).Contains("ses"))
            {
                if (GlobalTools.readValue(fs, bn, 0, GlobalTools.NumberType.LONG) == 4579260101974771027)
                {
                    uint headerStartOffset = GlobalTools.readValue(fs, bn, 32, GlobalTools.NumberType.UINT);
                    uint headerCount = GlobalTools.readValue(fs, bn, 36, GlobalTools.NumberType.UINT); //header data length
                    uint audioStartOffset = GlobalTools.readValue(fs, bn, 40, GlobalTools.NumberType.UINT); //the offset that the audio data starts to be written
                    uint audioCount = GlobalTools.readValue(fs, bn, 44, GlobalTools.NumberType.UINT);//audio data length

                    #region gather header info
                    uint headerEnd = headerStartOffset + headerCount;
                    for (uint i = headerStartOffset; i < headerEnd; i += 16)
                    {
                        Info f = new Info();
                        f.offset = GlobalTools.readValue(fs, bn, i + 0, GlobalTools.NumberType.UINT) + audioStartOffset;
                        f.sampleRate = GlobalTools.readValue(fs, bn, i + 4, GlobalTools.NumberType.UINT);
                        f.number = GlobalTools.readValue(fs, bn, i + 8, GlobalTools.NumberType.UINT);
                        f.loops = GlobalTools.readValue(fs, bn, i + 12, GlobalTools.NumberType.UINT);
                        f.name = (int)(i - headerStartOffset) / 16;


                        if (f.offset < fs.Length &&
                            GlobalTools.readValue(fs, bn, f.offset, GlobalTools.NumberType.LONG) == 0 &&
                            GlobalTools.readValue(fs, bn, i + 4, GlobalTools.NumberType.LONG) != 0)
                        {
                            Infos.Add(f);
                        }
                    }
                    #endregion
                    #region sorting
                    Infos.Sort((a, b) => a.offset.CompareTo(b.offset)); //sorts offsets by ascendent order
                    for (int i = 0; i < Infos.Count; i++)
                    {
                        List<byte> d = new List<byte>();
                        Infos[i].file = i;
                        if (i + 1 < Infos.Count)
                        {
                            for (uint o = Infos[i].offset + 16; o < Infos[i + 1].offset; o++)
                            {
                                d.Add(GlobalTools.readValue(fs, bn, o, GlobalTools.NumberType.BYTE));
                            }
                        }
                        else
                        {
                            for (uint o = Infos[i].offset; o < (audioStartOffset + audioCount); o++)
                            {
                                d.Add(GlobalTools.readValue(fs, bn, o, GlobalTools.NumberType.BYTE));
                            }
                        }
                        Infos[i].data = d.ToArray();
                    }
                    Infos.Sort((a, b) => a.name.CompareTo(b.name)); //sorts again but by name instead, so it can preserve the offsets order
                    #endregion

                    #region create the .ses body for modding
                    CSB(filePath, (int)audioStartOffset, (int)(audioCount + audioStartOffset), bn, fs, Infos);
                    #endregion
                }
                else
                {
                    GlobalTools.changeColor(ConsoleColor.Yellow);
                    Console.WriteLine(filePath + " wasn't a .ses file! skipping...");
                }
            }
            else
            {
                GlobalTools.changeColor(ConsoleColor.Yellow);
                Console.WriteLine(filePath + " wasn't a .ses file! skipping...");
            }
        }
    }
    public static void CSB(string file, int start, int end, BinaryReader bnr, FileStream fsr, List<Info> info)
    {
        string name = file.Replace(Path.GetFileName(file), Path.GetFileNameWithoutExtension(file) + "_SES_CONVERTED/" + Path.GetFileNameWithoutExtension(file) + ".sbo"); //ses body
        using (FileStream fs = new FileStream(name, FileMode.Create))
        using (BinaryWriter bn = new BinaryWriter(fs))
        {
            for (int i = 0; i < start; i += 4)
            {
                bn.Write(GlobalTools.readValue(fsr, bnr, i, GlobalTools.NumberType.INT));
            }
        }
        name = file.Replace(Path.GetFileName(file), Path.GetFileNameWithoutExtension(file) + "_SES_CONVERTED/" + Path.GetFileNameWithoutExtension(file) + ".table"); //ses table


        info.Sort((a, b) => a.offset.CompareTo(b.offset)); //sorts offsets by ascendent order


        List<(uint, int, int)> offsetComparer = new List<(uint, int, int)>();
        for (int i = 0; i < info.Count; i++)
        {
            offsetComparer.Add((info[i].offset, i, info[i].name));
        }
        info.Sort((a, b) => a.name.CompareTo(b.name)); //sorts numbers by ascendent order
        offsetComparer.Sort((a, b) => a.Item3.CompareTo(b.Item3));




        using (FileStream fs = new FileStream(name, FileMode.Create))
        using (BinaryWriter bn = new BinaryWriter(fs))
        {
            for (int i = 0; i < info.Count; i++)
            {

                //Console.WriteLine("file:  " + sorter[i].name + ".vag    in offset order: " + info[i].name  +"     Offset Sorter: " + sorter[i].offset + "   OFFSET info: " + info[i].offset);
                Console.WriteLine($"1:  {info[i].name}   2:  {offsetComparer[i].Item2}     offset {info[i].offset}");
                //bn.Write(info[i].name);
                bn.Write(offsetComparer[i].Item2);
            }
        }
        name = file.Replace(Path.GetFileName(file), Path.GetFileNameWithoutExtension(file) + "_SES_CONVERTED/" + Path.GetFileNameWithoutExtension(file) + ".sbe"); //ses body end
        using (FileStream fs = new FileStream(name, FileMode.Create))
        using (BinaryWriter bn = new BinaryWriter(fs))
        {
            for (int i = end; i < bnr.BaseStream.Length; i += 4)
            {
                bn.Write(GlobalTools.readValue(fsr, bnr, i, GlobalTools.NumberType.INT));
            }
        }
    }
    public static void RSES(string filePath)
    {
        List<string> path = new List<string>();

        for (int i = 0; i < 999; i++)
        {
            string cPath = filePath + "/VAG/" + i + ".vag";
            if (File.Exists(cPath)) path.Add(cPath);
            cPath = filePath + "/VAG/" + i + "_DUMMY";
            if (File.Exists(cPath)) path.Add(cPath);
        }
        (byte[][], uint[]) data = Info.readVAG(path.ToArray());


        string[] analyze = Directory.GetFiles(filePath, "*");
        byte[] start = new byte[] { };
        byte[] end = new byte[] { };
        int[] table = new int[] { };
        string name = "";
        foreach (var f in analyze)
        {
            if (f.Contains(".sbo"))
            {
                name = f;
                start = Info.readSBO(f);
            }
            if (f.Contains(".sbe"))
            {
                end = Info.readSBE(f);
            }
            if (f.Contains(".table"))
            {
                table = Info.readTABLE(f);
            }

        }
        using (FileStream fs = new FileStream(name.Replace(Path.GetExtension(name), "_new.ses"), FileMode.Create))
        using (BinaryWriter bn = new BinaryWriter(fs))
        using (BinaryReader bnr = new BinaryReader(fs))
        {
            List<uint> fileOffsets = new List<uint>();
            bn.Write(start);
            uint totalBytes = 0;
            for (int i = 0; i < data.Item1.Length; i++)
            {
                fileOffsets.Add((uint)fs.Position);
                bn.Write(data.Item1[i]);

                Console.WriteLine(data.Item1[i].Length);
                foreach (var k in data.Item1[i])
                {
                   totalBytes++;
                }
            }
            bn.Write(end);

            fs.Position = 44;
            bn.Write(totalBytes);


            uint startOffset = GlobalTools.readValue(fs, bnr, 32, GlobalTools.NumberType.UINT);
            uint endOffset = GlobalTools.readValue(fs, bnr, 36, GlobalTools.NumberType.UINT) + startOffset;
            uint audioOffset = GlobalTools.readValue(fs, bnr, 40, GlobalTools.NumberType.UINT);
            Console.WriteLine(startOffset + "  " + endOffset);
            int cCount = 0;
            for (uint i = startOffset; i < endOffset;i+=16)
            {
                fs.Position = i;
                if (GlobalTools.readValue(fs, bnr, i+4, GlobalTools.NumberType.UINT) != 0)
                {
                    fs.Position = i;
                    bn.Write((uint)fileOffsets[table[cCount]] - audioOffset);

                    fs.Position = i+4;
                    bn.Write(data.Item2[table[cCount]]);
                    cCount += 1;
                } else
                {
                    break;
                }
            }
            
        }
    }
}