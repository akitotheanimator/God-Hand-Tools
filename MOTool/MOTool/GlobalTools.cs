using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

public static class GlobalTools
{
    public static string FilePath;
    public enum NumberType { BYTE, UBYTE, SHORT, USHORT, INT, UINT, LONG, ULONG,SINGLE,HALF };




    public static void changeColor(ConsoleColor back)
    {
        Console.ForegroundColor = back;
    }
    public static void cleanSection(string message)
    {
        Console.SetCursorPosition(0, Console.CursorTop - 1);
        Console.WriteLine(new string(' ', Console.WindowWidth));
        Console.SetCursorPosition(0, Console.CursorTop - 1);
        Console.WriteLine(message);
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
            case NumberType.HALF:

                byte[] bytes1 = { br.ReadByte(), br.ReadByte() };
                returner = (float)IEEEBinary16.FromBytes(bytes1);
                //Console.WriteLine(returner);
                break;
        }
        return returner;
    }


    public static string getType(sbyte tp)
    {
        string returner = $"not computed.{tp}";
        switch(tp)
        {
            case 16:
                returner = "position.x";
                break;
            case 17:
                returner = "position.y";
                break;
            case 18:
                returner = "position.z";
                break;
            case 19:
                returner = "rotation.x";
                break;
            case 20:
                returner = "rotation.y";
                break;
            case 21:
                returner = "rotation.z";
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
            case -1:
                returner = "Unidentified.-1";
                break;
        }

        return returner;
    }
}

public class IEEEBinary16
{
    private const int SignificandBits = 9;
    private const int ExponentBits = 6;
    private const int Bias = 47;

    // Method to convert from bytes to float (IEEE binary16)
    public static float FromBytes(byte[] bytes, bool bigEndian = false)
    {
        if (bytes.Length != 2)
            throw new ArgumentException("Byte array must be of length 2.");

        // Determine byte order
        if (bigEndian)
            Array.Reverse(bytes);

        ushort halfPrecision = BitConverter.ToUInt16(bytes, 0);

        int exponent = (halfPrecision >> SignificandBits) & ((1 << ExponentBits) - 1);
        int significand = halfPrecision & ((1 << SignificandBits) - 1);
        int sign = (halfPrecision >> 15) & 1;

        // Handle special cases for NaN and Infinity if needed

        // Convert to float
        int biasedExponent = exponent - Bias;
        float value = (float)((sign * -2 + 1) * Math.Pow(2, biasedExponent) * (1 + significand / Math.Pow(2, SignificandBits)));

        return value;
    }

    // Method to convert from float to bytes (IEEE binary16)
    public static byte[] ToBytes(float value, bool bigEndian = false)
    {
        // Convert float to IEEE binary16
        ushort halfPrecision = 0;
        int sign = value < 0 ? 1 : 0;
        value = Math.Abs(value);

        if (float.IsNaN(value) || float.IsInfinity(value))
            throw new ArgumentException("Value cannot be NaN or Infinity.");

        int exponent = (int)Math.Floor(Math.Log(value) / Math.Log(2));
        int significand = (int)Math.Round(value / Math.Pow(2, exponent) * (1 << SignificandBits));

        // Adjust exponent and significand for half precision
        int biasedExponent = exponent + Bias;
        halfPrecision |= (ushort)(sign << 15);
        halfPrecision |= (ushort)((biasedExponent << SignificandBits) & 0x7FF);
        halfPrecision |= (ushort)(significand & ((1 << SignificandBits) - 1));

        byte[] bytes = BitConverter.GetBytes(halfPrecision);

        // Determine byte order
        if (bigEndian)
            Array.Reverse(bytes);

        return bytes;
    }
}