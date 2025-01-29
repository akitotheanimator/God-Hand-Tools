using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.CodeDom;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.WindowsRuntime;
using System.Numerics;
using System.Threading;
public static class GlobalTools
{
    public static string FilePath;
    public static FileStream fs;
    public static BinaryReader br;
    //took some time for me to actually do this lmao.

    public enum NumberType { BYTE, SBYTE, SHORT, USHORT, INT, UINT, LONG, ULONG,SINGLE,HALF,STRING };
    public static dynamic readValue(long offset, NumberType tp)
    {
        dynamic returner = 0;
        fs.Position = offset;
        switch (tp)
        {
            case NumberType.BYTE:
                returner = br.ReadByte();
                break;
            case NumberType.SBYTE:
                returner = br.ReadSByte();
                break;
            case NumberType.SHORT:
                returner = br.ReadInt16();
                break;
            case NumberType.USHORT:
                returner = br.ReadUInt16();
                break;
            case NumberType.INT:
                returner = br.ReadInt32();
                break;
            case NumberType.UINT:
                returner = br.ReadUInt32();
                break;
            case NumberType.LONG:
                returner = br.ReadInt64();
                break;
            case NumberType.ULONG:
                returner = br.ReadUInt64();
                break;

            case NumberType.SINGLE:
                returner = br.ReadSingle();
                break;
            case NumberType.STRING:
                returner = Encoding.UTF8.GetString(br.ReadBytes(4)).Replace("\0", "");
                break;
        }
        return returner;
    }
}