using System;
using System.Collections.Generic;
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
                                Console.WriteLine(readValue(fs, br, i, NumberType.UINT));
                                adress.Add(readValue(fs, br, i, NumberType.UINT));
                            }
                            currentOffset = i;
                        }
                        for (uint i = Counting; i < Counting + currentOffset; i += 4)
                        {

                            if (readValue(fs, br, i, NumberType.UINT) != 0)
                            {

                                Console.WriteLine(readValue(fs, br, i, NumberType.STRING));
                                types.Add(readValue(fs, br, i, NumberType.STRING));
                            }
                        }
                        for (int i = 0; i < adress.Count; i++) returner.Add((adress[i], types[i]));
                        adresses = returner.ToArray();
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
                        for (int i = 0; i < adress.Count; i++) returner.Add((adress[i], types[i]));
                        adresses = returner.ToArray();
                        break;
                }
            }
            return new(adresses, type, startOffset);
        }
    }
}