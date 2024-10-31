﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace IOH
{
    public static class IOHelper
    {
        public static string FilePath;
        public enum NumberType { BYTE, UBYTE, SHORT, USHORT, INT, UINT, LONG, ULONG, SINGLE,STRING };

        public static void changeColor(ConsoleColor back)
        {
            Console.ForegroundColor = back;
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
                case NumberType.STRING:
                    returner = Encoding.UTF8.GetString(br.ReadBytes(4));
                    break;
            }
            return returner;
        }
    }
}