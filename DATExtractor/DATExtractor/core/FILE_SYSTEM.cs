using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using static IOH.IOHelper;

namespace FILE_MANAGING
{
    public static class FILE_SYSTEM
    {
        public static ((uint, string)[], string, uint) getDATInfo(string path)
        {
            string type = "NONE";
            uint startOffset = 0;
            (uint, string)[] adresses = new (uint, string)[0];
            using (FileStream fs = new FileStream(path, FileMode.Open))
            using (BinaryReader br = new BinaryReader(fs))
            {
                if (readValue(fs, br, readValue(fs, br, 4, NumberType.UINT), NumberType.UINT) != 0)
                {
                    type = "PACKED_MODEL";
                }
                if (readValue(fs, br, readValue(fs, br, 4, NumberType.UINT), NumberType.UINT) == 0)
                {
                    type = "PACKED_MAP";
                }
                if (readValue(fs, br, 4, NumberType.UINT) == 96)
                {
                    type = "PACKED_EVENT"; //used in cutscenes
                }

                
                uint Counting = 0;
                List<uint> adress = new List<uint>();
                List<string> types = new List<string>();
                List<(uint, string)> returner = new List<(uint, string)>();
                switch (type)
                {
                    case "PACKED_MODEL":
                        #region start offset
                        fs.Position = 0;
                        startOffset = (uint)fs.Position;
                        #endregion
                        Counting = readValue(fs, br, 0, NumberType.UINT)*4;
                        Counting += 4;
                        uint currentOffset = 0;
                        for (uint i = 4; i < Counting; i += 4)
                        {
                            if (readValue(fs, br, i, NumberType.UINT) != 0)
                            {
                                adress.Add(readValue(fs, br, i, NumberType.UINT));
                            }
                            currentOffset = i;
                        }
                        for (uint i = Counting; i < Counting + currentOffset; i += 4)
                        {

                            if (readValue(fs, br, i, NumberType.UINT) != 0)
                            {

                                types.Add(readValue(fs, br, i, NumberType.STRING));
                            }
                        }
                        break;
                    case "PACKED_MAP":
                        fs.Position = 16;
                        uint additive = br.ReadUInt32();
                        fs.Position = 16;
                        fs.Position = br.ReadInt32();
                        startOffset = (uint)fs.Position;
                        uint startPosition = (uint)fs.Position;
                        Counting = startPosition + (4 + (br.ReadUInt32() * 4));

                        for (uint i = startPosition + 4; i < Counting; i += 4)
                        {
                            fs.Position = i;
                            adress.Add(br.ReadUInt32() + additive);
                        }
                        for (uint i = Counting; i < Counting + ((Counting - 4) - startPosition); i += 4)
                        {
                            fs.Position = i;
                            string encodedName = Encoding.UTF8.GetString(br.ReadBytes(4));
                            types.Add(encodedName);
                        }
                        break;

                    case "PACKED_EVENT":

                        List<(uint,string)> sort = new List<(uint, string)>();


                        fs.Position = 16;
                        uint fileStartingPoint = br.ReadUInt32();

                        fs.Position = 28;
                        uint fileEndingPoint = br.ReadUInt32();

                        fs.Position = 8;
                        uint ignoreFrom = br.ReadUInt32();

                        fs.Position = 12;
                        uint ignoreTo = br.ReadUInt32();

                        fs.Position = 4;
                        uint motStart = br.ReadUInt32();



                        for (uint i = 20; i < motStart; i += 4) //gather the SEQ's till the mot section start
                        {
                            fs.Position = i;
                            if (i != motStart && br.ReadUInt32() > 0 && i != 28) //if the adress isn't equals the mot starting adress and if the number isn't equals 0
                            {
                                fs.Position = i;
                                sort.Add((br.ReadUInt32(), "SEQ"));
                            }
                        }

                        for (uint i = motStart;i < ignoreFrom;i+=4)
                        {
                            fs.Position = i;
                            if (br.ReadUInt32() > 0) //if the adress isn't equals the mot starting adress and if the number isn't equals 0
                            {
                                fs.Position = i;
                                sort.Add((br.ReadUInt32(), "MOT"));
                            }
                        }
                        for (uint i = ignoreTo; i < fileStartingPoint; i += 4)
                        {
                            fs.Position = i;
                            if (br.ReadUInt32() > 0) //if the adress isn't equals the mot starting adress and if the number isn't equals 0
                            {
                                fs.Position = i;
                                sort.Add((br.ReadUInt32(), "MOT"));
                            }
                        }
                        string rootFolder = path.Replace(".dat", ".dat_extacted");
                        if (!File.Exists(rootFolder + "/UTILIZED ELEMENTS.txt"))
                        {
                            var writer = File.CreateText(rootFolder + "/UTILIZED ELEMENTS.txt");
                            writer.WriteLine("The file was recognized as a packed event file. \nUtilized .dat elements:");
                            for(uint i = ignoreFrom;i <  ignoreTo;i+=4)
                            {
                                if(readValue(fs, br, i, NumberType.UINT) > 0)
                                writer.WriteLine(readValue(fs, br, i, NumberType.STRING).ToString().Replace("\0", "") + ".dat");
                            }

                            writer.Dispose();
                        }


                        sort.Add((fileEndingPoint, "MISC"));


                        sort.Sort((x, y) => x.Item1.CompareTo(y.Item1));
                        for(int i = 0; i < sort.Count;i++)
                        {
                            adress.Add(sort[i].Item1);
                            types.Add(sort[i].Item2);
                        }



                        break;

                }
                for (int i = 0; i < adress.Count; i++) returner.Add((adress[i], types[i]));
                adresses = returner.ToArray();
            }
            var ret = (adresses, type, startOffset);
            return ret;
        }
    }
}