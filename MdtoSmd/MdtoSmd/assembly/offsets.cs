using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

class offsets
{
    public static void process(string path)
    {
            using (var stream = new FileStream(path, FileMode.Open))
            {
                using (var reader = new BinaryReader(stream))
                {
                    int originalOffsetCounting = hx.gatherSingleNumberFromOffset(stream, reader, 8, 4, hx.mode.int32);
                    dynamic[] allOffsets = hx.gatherFromOffsetDuration(stream, reader, 16, originalOffsetCounting, 4, hx.mode.int32);
                    List<string> names = new List<string>();

                    for (int i = 0; i < allOffsets.Length; i++)
                    {
                        List<byte> allbytes = new List<byte>();
                        byte[] all = hx.gatherBYTEFromOffsetDuration(stream, reader, allOffsets[i] + 8, 8, 1);
                        names.Add(Encoding.UTF8.GetString(all) + " " + i);
                    }
                    //Console.WriteLine(names.Count + "   NAMEs");
                    dynamic[] negativeOffset = hx.gatherFromOffsetArrays(stream, reader, allOffsets, hx.mode.int32);
                    dynamic[] concactOffsets = hx.concactOffsets(allOffsets, negativeOffset);
                    essentialOffsets.process(path, concactOffsets, stream, reader, names.ToArray());
                }
            }
    }
}
