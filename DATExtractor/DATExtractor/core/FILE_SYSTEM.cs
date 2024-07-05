using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace FILE_MANAGING
{
    public static class FILE_SYSTEM
    {
        public static ((int, string)[], string,int) getDATInfo(string path)
        {
            string type = "NONE";
            int startOffset = 0;
            (int, string)[] adresses = new(int,string)[0];


            using (FileStream fs = new FileStream(path, FileMode.Open))
            using (BinaryReader br = new BinaryReader(fs))
            {
                fs.Position = 4;
                fs.Position = br.ReadInt32();
                if (br.ReadInt32() != 0)
                {
                    type = "PACKED_MODEL";
                }
                if (br.ReadInt32() == 0)
                {
                    type = "PACKED_MAP";
                }
                int endPosition = 0;

                List<int> adress = new List<int>();
                List<string> types = new List<string>();
                List<(int, string)> returner = new List<(int, string)>();
                switch (type)
                {
                    case "PACKED_MODEL":
                        fs.Position = 0;
                        startOffset = (int)fs.Position;
                        endPosition = 4 +(br.ReadInt32() * 4);
                        for(int i = 4; i < endPosition;i+=4)
                        {
                            fs.Position = i;
                            adress.Add(br.ReadInt32());
                        }
                        for (int i = endPosition; i < ((endPosition-4)*2)+4; i += 4)
                        {
                            fs.Position = i;
                            string encodedName = Encoding.UTF8.GetString(br.ReadBytes(4));
                            types.Add(encodedName);
                        }
                        for (int i = 0; i < adress.Count; i++) returner.Add((adress[i], types[i]));
                        adresses = returner.ToArray();
                        break;
                    case "PACKED_MAP":
                        fs.Position = 16;
                       int additive = br.ReadInt32();
                        fs.Position = 16;
                        fs.Position = br.ReadInt32();
                        startOffset = (int)fs.Position;
                        //544
                        //664
                        int startPosition = (int)fs.Position;
                        endPosition = startPosition + (4 + (br.ReadInt32() * 4));

                        //GD.Print(startPosition + "   " + endPosition + "   " + ((endPosition-4) - startPosition));

                        for (int i = startPosition + 4; i < endPosition; i += 4)
                        {
                            fs.Position = i;
                            adress.Add(br.ReadInt32()+ additive);
                        }
                        for (int i = endPosition; i < endPosition + ((endPosition - 4) - startPosition); i += 4)
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
            return new(adresses, type,startOffset);
        }
    }
}
namespace MD
{
    public static class SCR
    {
        public static string CheckFormat(string path)
        {
            using (FileStream fs = new FileStream(path, FileMode.Open))
            using (BinaryReader br = new BinaryReader(fs))
            {
                if (br.ReadInt32() == 7496563)
                {
                    if (path.Contains(".scr") || path.Contains(".SCR"))
                    {
                        return "Model16";
                    }
                    else
                    {
                        return "Model32";
                    }
                }
                return "PackedFile";
            }
        }
    }
    public class modelConstructor
    {
        public string name;
        public int adress = 0;
    }
}