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
    public enum NumberType { BYTE, UBYTE, SHORT, USHORT, INT, UINT, LONG, ULONG,SINGLE,HALF };
    public static Vector3 getFromIndice(int indice, (Vector3, int)[] values)
    {
        Console.WriteLine(values.Length + "   " + indice);
        Console.WriteLine("HAIIII " + values[indice].Item1 + "  " +  indice);
        return values[indice].Item1;

        foreach(var a in values)
        {
            Console.WriteLine("HAIIII " +a.Item1 + "  " + a.Item2 + "  " + indice);
            if (a.Item2 == indice) return a.Item1;
        }
        return new Vector3(0,0,0);
    }
    public static string returnStringFromArray(int[] array)
    {
        string a = "";
        foreach (var r in array) a += "," + r;
        a = a.Substring(1);
        return a;
    }
    public static string returnStringFromArray2(string[] array)
    {
        string a = "";
        foreach (var r in array) a += "," + r;
        a = a.Substring(1);
        return a;
    }
    public static string returnStringFromVertices(Vertex[] array)
    {
        string a = "";
        foreach (var r in array) a += "," + r.indice;
        a = a.Substring(1);
        return a;
    }
    public static int[] returnFromVertices(Vertex[] array)
    {
        List<int> v = new List<int>();
        foreach (var r in array) v.Add(r.indice);
        return v.ToArray();
    }
    public static dynamic readValue(FileStream fs, BinaryReader br, long offset, NumberType tp)
    {
        dynamic returner = 0;
        fs.Position = offset;
        switch (tp)
        {
            case NumberType.BYTE:
                returner = br.ReadByte();
                break;
            case NumberType.UBYTE:
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
        }
        return returner;
    }
    public static void writeOnConsole(string input, ConsoleColor color)
    {
        Console.ForegroundColor = color;
        if (Program.ViewOutput) Console.WriteLine(input);
    }
    public static void writeAtLine(string input, ConsoleColor color)
    {
        Console.ForegroundColor = color;
        if (Program.ViewOutput) Console.Write(input);
    }
}