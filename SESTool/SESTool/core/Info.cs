using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

public class Info
{
    public uint offset; //offset
    public uint sampleRate; //sample rate
    public uint number; //have no clue of what this is for
    public uint loops; //if it loops or not
    public int name; //name to identify the file, it is necessary in this case cuz i will use a sorting algorithm to order the offsets by ascendent
    public int file; //name to save the file
    public byte[] data; //the chunk data


    public static byte[] readSBE(string path)
    {
        return File.ReadAllBytes(path);
    }
    public static byte[] readSBO(string path)
    {
        return File.ReadAllBytes(path);
    }
    public static int[] readTABLE(string path)
    {
        List<int> orders = new List<int>();
        using (FileStream fs = new FileStream(path, FileMode.Open))
        using (BinaryReader bn = new BinaryReader(fs))
        {
            for (uint i = 0; i < fs.Length; i += 4)
            {
                fs.Position = i;
                orders.Add(bn.ReadInt32());
            }
        }
        return orders.ToArray();
    }
    public static (byte[][], uint[]) readVAG(string[] path)
    {
        List<uint> sampleRate = new List<uint>();
        List<byte[]> data = new List<byte[]>();
        for (int i = 0; i < path.Length; i++)
        {
            using (FileStream fs = new FileStream(path[i], FileMode.Open))
            using (BinaryReader bn = new BinaryReader(fs))
            {
                List<byte> curData = new List<byte>();
                if (fs.Length > 0)
                {
                    byte[] sample = BitConverter.GetBytes(GlobalTools.readValue(fs, bn, 16, GlobalTools.NumberType.UINT));
                    Array.Reverse(sample);
                    sampleRate.Add(BitConverter.ToUInt32(sample, 0));
                }
                else
                {
                    sampleRate.Add(11025);
                }

                for (int f = 0; f < 16; f++)
                {
                    curData.Add(0);
                }
                bool startReadng = false;
                for (uint e = 32; e < fs.Length; e += 16)
                {
                    fs.Position = e;


                    if (startReadng)
                    {
                        for (uint f = e; f < e + 16; f++)
                        {
                            fs.Position = f;
                            curData.Add(bn.ReadByte());
                        }
                    }
                    if (e + 24 < fs.Length)
                        if (GlobalTools.readValue(fs, bn, e + 16, GlobalTools.NumberType.LONG) != 0 || GlobalTools.readValue(fs, bn, e + 24, GlobalTools.NumberType.LONG) != 0)
                        {
                            startReadng = true;
                        }
                }
                data.Add(curData.ToArray());
            }
        }
        return (data.ToArray(), sampleRate.ToArray());
    }
}