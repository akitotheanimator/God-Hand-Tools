using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Numerics;






public static class GetMot
{
    public static void processMot(string file)
    {
        if(!Directory.Exists(file.Replace(Path.GetFileName(file), "") + "/MOTIONS_"))
            Directory.CreateDirectory(file.Replace(Path.GetFileName(file),"") + "/MOTIONS_");

        Program.saveFileTo = file.Replace(Path.GetFileName(file), "") + "/MOTIONS_";



        GlobalTools.FilePath = Program.pathForBones;

        List<BONES> bnl = new List<BONES>();
        BONES root = new BONES();
        root.pos = new Vector3(0,0,0);
        //bnl.Add(root);
        using (FileStream fs = new FileStream(Program.pathForBones, FileMode.Open))
        using (BinaryReader br = new BinaryReader(fs))
        {

            for (int i = 0; i < fs.Length; i += 16)
            {
                BONES bn = new BONES();
                bn.pos = new Vector3(GlobalTools.readValue(fs, br, i, GlobalTools.NumberType.SINGLE), GlobalTools.readValue(fs, br, i + 4, GlobalTools.NumberType.SINGLE), GlobalTools.readValue(fs, br, i + 8, GlobalTools.NumberType.SINGLE));
                bn.parentingOrder = GlobalTools.readValue(fs, br, i + 12, GlobalTools.NumberType.SHORT);
                bn.id = GlobalTools.readValue(fs, br, i + 14, GlobalTools.NumberType.SHORT);
                bnl.Add(bn);
                //Console.WriteLine(x + "  " + y + "  " + z + "  " + id2);
            }
        }

        Program.bones_ = bnl.ToArray();
        Program.bones_[1].pos = new Vector3(0,0,0);


        GlobalTools.FilePath = file;
        MOTFile.bones = new MOTBone[0];




        GlobalTools.changeColor(ConsoleColor.Green);
        Console.WriteLine("This is a valid MOT File!");
        GlobalTools.changeColor(ConsoleColor.Yellow);
        Console.WriteLine("Reading Header");

        using (FileStream fs = new FileStream(file, FileMode.Open))
        using (BinaryReader br = new BinaryReader(fs))
        {

            #region read header start
            ushort FrameCount = GlobalTools.readValue(fs, br, 4, GlobalTools.NumberType.USHORT);
            sbyte countOfKeyframedproperties = GlobalTools.readValue(fs, br, 6, GlobalTools.NumberType.UBYTE);
            sbyte UseIK = GlobalTools.readValue(fs, br, 7, GlobalTools.NumberType.UBYTE);
            fs.Position = 8;
            GlobalTools.changeColor(ConsoleColor.Green);
            GlobalTools.cleanSection($"Animation frame count: {FrameCount}, Keyframed components: {countOfKeyframedproperties}");
            #endregion

            GlobalTools.changeColor(ConsoleColor.Yellow);
            Console.WriteLine("Reading Header Data...");
            int propertyEndOffset = (countOfKeyframedproperties * 12) + 8;
            int tempCount = 0;
            GlobalTools.changeColor(ConsoleColor.Blue);

            for (int i = 8; i < propertyEndOffset; i += 12)
            {

                MOTBone bone = new MOTBone();
                MOTHeader keyframe = new MOTHeader();
                if (GlobalTools.readValue(fs, br, i + 8, GlobalTools.NumberType.UINT) != 0 && GlobalTools.readValue(fs, br, i + 8, GlobalTools.NumberType.UINT) < fs.Length && GlobalTools.readValue(fs, br, i, GlobalTools.NumberType.UBYTE) != 127)
                {
                    bone.index = GlobalTools.readValue(fs, br, i, GlobalTools.NumberType.UBYTE);
                    bone.type = GlobalTools.getType(GlobalTools.readValue(fs, br, i + 1, GlobalTools.NumberType.UBYTE));
                    keyframe.keyframeCount = GlobalTools.readValue(fs, br, i + 2, GlobalTools.NumberType.USHORT);
                    keyframe.isAbsoluteCoordinate = GlobalTools.readValue(fs, br, i + 4, GlobalTools.NumberType.UINT) == 1;
                    keyframe.adress = GlobalTools.readValue(fs, br, i + 8, GlobalTools.NumberType.UINT);

                    //Console.WriteLine(GlobalTools.readValue(fs, br, i + 4, GlobalTools.NumberType.INT));

                    bone.data = keyframe;
                    MOTFile.addBone(bone);

                    #region console stuff
                    if(1>3)
                    if (tempCount == 0)
                        Console.WriteLine($"Bone index: {bone.index}   (Keyframe Type: {bone.type}, Total Keyframes on property: {keyframe.keyframeCount} MV{keyframe.isAbsoluteCoordinate}, localized at: 0x{keyframe.adress.ToString("X")})");
                    else
                        Console.WriteLine($"Bone index: {bone.index}   (Keyframe Type: {bone.type}, Total Keyframes on property: {keyframe.keyframeCount} MV{keyframe.isAbsoluteCoordinate}, localized at: 0x{keyframe.adress.ToString("X")} ({tempCount}))");
                    tempCount += 1;

                    //Console.WriteLine(i);
                    #endregion
                }
            }
            //Thread.Sleep(15);
            GlobalTools.changeColor(ConsoleColor.Green);
            Console.WriteLine("Done!");
            GlobalTools.changeColor(ConsoleColor.Yellow);
            Console.WriteLine("Reading MOT data...");
            for (int i = 0; i < MOTFile.bones.Length; i++)
            {
                int additive = 0;

                MOTFile.bones[i].data.P = (float)GlobalTools.readValue(fs, br, MOTFile.bones[i].data.adress + 0, GlobalTools.NumberType.HALF);
                MOTFile.bones[i].data.Dp = (float)GlobalTools.readValue(fs, br, MOTFile.bones[i].data.adress + 2, GlobalTools.NumberType.HALF);
                MOTFile.bones[i].data.M0 = (float)GlobalTools.readValue(fs, br, MOTFile.bones[i].data.adress + 4, GlobalTools.NumberType.HALF);
                MOTFile.bones[i].data.Dm0 = (float)GlobalTools.readValue(fs, br, MOTFile.bones[i].data.adress + 6, GlobalTools.NumberType.HALF);
                MOTFile.bones[i].data.M1 = (float)GlobalTools.readValue(fs, br, MOTFile.bones[i].data.adress + 8, GlobalTools.NumberType.HALF);
                MOTFile.bones[i].data.Dm1 = (float)GlobalTools.readValue(fs, br, MOTFile.bones[i].data.adress + 10, GlobalTools.NumberType.HALF);
                for (uint a = MOTFile.bones[i].data.adress + 12; a < (((MOTFile.bones[i].data.adress + (MOTFile.bones[i].data.keyframeCount * 4) + 12))); a += 4)
                {
                    if (a == fs.Length) break;
                    MOTKeyframe cv = new MOTKeyframe(); //curve
                    //cv.ri = GlobalTools.readValue(fs, br, a, GlobalTools.NumberType.BYTE);
                    additive += GlobalTools.readValue(fs, br, a, GlobalTools.NumberType.BYTE);
                    cv.absolute_index = additive;



                    cv.Cp = GlobalTools.readValue(fs, br, a + 1, GlobalTools.NumberType.BYTE);
                    cv.Cm0 = GlobalTools.readValue(fs, br, a + 2, GlobalTools.NumberType.BYTE);
                    cv.Cm1 = GlobalTools.readValue(fs, br, a + 3, GlobalTools.NumberType.BYTE);
                    MOTFile.addCurve(cv, MOTFile.bones[i].data);
                }
            }



            int greatest = 0;
            for (int i = 0; i < MOTFile.bones.Length; i++)
            {
                if (MOTFile.bones[i].data.curves.Length > greatest) greatest = MOTFile.bones[i].data.curves.Length;
            }
            for (int i = 0; i < MOTFile.bones.Length; i++)
            {
                List<MOTKeyframe> cvs = MOTFile.bones[i].data.curves.ToList();
                if (MOTFile.bones[i].data.curves.Length < greatest)
                {
                    for (int o = MOTFile.bones[i].data.curves.Length; o < greatest; o++)
                    {
                        cvs.Add(cvs[cvs.Count - 1]);
                    }
                }
                if (cvs.Count > 0) MOTFile.bones[i].data.curves = cvs.ToArray();
            }
        }
        GlobalTools.changeColor(ConsoleColor.Green);
        Console.WriteLine("Done!");
        GlobalTools.changeColor(ConsoleColor.Red);
        Console.WriteLine("Quantizing Values...");
        MOTFile.Quantize();
        GlobalTools.changeColor(ConsoleColor.Green);
        Console.WriteLine("Done!");
        SMDExportMOT.Export(file);
    }
}