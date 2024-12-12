using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Numerics;
public static class GlobalTools
{
    public static string FilePath;
    public enum NumberType { BYTE, SBYTE, SHORT, USHORT, INT, UINT, LONG, ULONG,SINGLE,HALF };
    public static dynamic readValue(FileStream fs, BinaryReader br, long offset, NumberType tp)
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
        }
        return returner;
    }

    public static float Map(float value, float fromMin, float fromMax, float toMin, float toMax) {
        float fromRange = fromMax - fromMin;
        float toRange = toMax - toMin;
        return toMin + (value - fromMin) * toRange / fromRange;
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
    public static BONES[] readBones(string bonePath)
    {
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
            return bnl.ToArray();
        }
        catch (Exception e)
        {
            GlobalTools.writeOnConsole("Failed to load .Bones file. This may be the reason: " + e, ConsoleColor.Red);
        }
        return null;
    }
    public static string returnType(byte tp)
    {
        string returner = $"not computed.{tp}";
        switch (tp)
        {
            case 16:
                returner = "location.x";
                break;
            case 17:
                returner = "location.y";
                break;
            case 18:
                returner = "location.z";
                break;
            case 19:
                returner = "rotation_euler.x";
                break;
            case 20:
                returner = "rotation_euler.y";
                break;
            case 21:
                returner = "rotation_euler.z";
                break;
            case 22:
                returner = "scale.x";
                break;
            case 23:
                returner = "scale.y";
                break;
            case 24:
                returner = "scale.z";
                break;
            case 2:
                returner = "Unidentified.2";
                break;
            case 1:
                returner = "Unidentified.1";
                break;
            case 0:
                returner = "Unidentified.1";
                break;
            case 80: //These are values referred to animations that uses non-quantized values.
                returner = "location.x";
                break;
            case 81:
                returner = "location.y";
                break;
            case 82:
                returner = "location.z";
                break;
            case 83:
                returner = "rotation_euler.x";
                break;
            case 84:
                returner = "rotation_euler.y";
                break;
            case 85:
                returner = "rotation_euler.z";
                break;
        }

        return returner;
    }

}

public class IEEEBinary16 { 
    public static ushort ToUshort(float input)
    {
        //float errorFactor = 0.01f;
        ushort s = 0, e = 0;
        if (input < 0) { s = 32768; e = 65535; } else { s = 0; e = 32767; } //to avoid iterating through each number of a ushort, we can firstly determine where it starts and ends since 0 to 32767 will return positive numbers, and vice versa.
        List<(ushort, float)> distanceFactor = new List<(ushort, float)>();
        for (ushort i = s;i < e;i++)
        {
            float distance = Math.Abs(FromUShort(i) - input);//the lowest distance is the best overall match for the number
            //if (distance < errorFactor/10f || distance < errorFactor / 50f || distance < errorFactor / 100f) return i; //if the distance is less than the error factor, the number will be chosen,that's meant to reduce significantly the processing time
            distanceFactor.Add((i, distance)); //in case nothing happens, it will add to a list for sorting the distances, sometimes more larger numbers will require this 
        }
        distanceFactor.Sort((a, b) => a.Item2.CompareTo(b.Item2)); //sorts from distance, so the lowest distance will always be first
        return distanceFactor[0].Item1;
    }
    public static float FromUShort(ushort halfPrecision)
    {
        int exponent = (halfPrecision >> 9) & ((1 << 6) - 1);
        int significand = halfPrecision & ((1 << 9) - 1);
        int sign = (halfPrecision >> 15) & 1;
        int biasedExponent = exponent - 47;
        float value = (float)((sign * -2 + 1) * Math.Pow(2, biasedExponent) * (1 + significand / Math.Pow(2, 9)));
        return value;
    }
}