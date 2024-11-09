using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

class essentialOffsets
{
    public static void process(string path, dynamic[] concactOffsets, FileStream stream, BinaryReader reader,string[] modelName)
    {
        List<linkedMesh> allMeshes = new List<linkedMesh>();

        List<string> newNames = new List<string>();
        for (int i = 0; i < concactOffsets.Length; i++)
        {

            int formulaOffset = hx.gatherSingleNumberFromOffset(stream, reader, concactOffsets[i], 1, hx.mode.int32); //if it's written 'mdb.'
            skeletonHeader.boneStartOffset = concactOffsets[i] + hx.gatherSingleNumberFromOffset(stream, reader, concactOffsets[i] + 4, 1, hx.mode.int32);
            skeletonHeader.boneCount = hx.gatherSingleNumberFromOffset(stream, reader, concactOffsets[i] + 8, 1, hx.mode.int16);

            int linkedMeshes = hx.gatherSingleNumberFromOffset(stream, reader, concactOffsets[i] + 10, 1, hx.mode.int16);


            dynamic[] linkedMeshOffset = hx.gatherFromOffsetDuration(stream, reader, concactOffsets[i] + 32, (linkedMeshes * 4), 4, hx.mode.int32);



            List<int> sets = new List<int>();
            linkedMesh placeholder = new linkedMesh();
            for (int k = 0; k < linkedMeshOffset.Length; k++)
            {
                newNames.Add(modelName[i]);
                if (linkedMeshOffset[k] != 0)
                {
                    sets.Add(linkedMeshOffset[k] + concactOffsets[i]);
                    Console.WriteLine("OFFSETSLOL " + (linkedMeshOffset[k] + concactOffsets[i]));
                }
                placeholder.offsets = sets.ToArray();
                allMeshes.Add(placeholder);
            }


        }
        Console.WriteLine(allMeshes.Count + "    COUNTING" + "         " + newNames.Count + "     " + concactOffsets.Length);
        //Console.WriteLine(concactOffsets.Length);

        for(int i = 0; i < allMeshes.Count;i++)
        {
            for (int e = 0; e < allMeshes[i].offsets.Length; e++)
            {
                Console.ForegroundColor = ConsoleColor.White;
                Console.BackgroundColor = ConsoleColor.Black;
                Console.WriteLine(allMeshes[i].offsets[e] + " job Start on " + (newNames[i] + e));
                baseModel.extract(allMeshes[i].offsets[e],stream,reader, (newNames[i] + e));
            }
        }
        mountModel.saveFile(stream,reader);
    }
}
