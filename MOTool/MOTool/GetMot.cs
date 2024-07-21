using OxyPlot;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml.Linq;
using System.Numerics;



using OxyPlot.Series;
using OxyPlot.WindowsForms;




public static class GetMot
{
    public static string returnDecimal(float number, int strictLength)
    {
        //Console.WriteLine(number);
        string verySmallNumberString = number.ToString();
        decimal convertedVerySmallDecimal = Decimal.Parse(verySmallNumberString, System.Globalization.NumberStyles.Float);
        string curString = convertedVerySmallDecimal.ToString().Replace(",", ".");
        string pass1 = "";
        if (curString.Length > strictLength)
        {
            if (curString.Contains("-"))
            {
                string tmpString = curString.Replace("-", "");
                pass1 = curString.Substring(0, strictLength + 1);
            }
            else
            {
                pass1 = curString.Substring(0, strictLength);
            }
        }
        else
        {
            for (int i = curString.Length; i < strictLength; i++)
            {
                if (curString.Contains("."))
                {
                    curString = curString + "0";
                }
                else
                {
                    curString = curString + ".";
                }
            }
            pass1 = curString;
        }
        if (!curString.Contains("-"))
        {
            string tmp = pass1;
            //pass1 = " " + tmp ;
        }
        return pass1;
    }
    public static void processMot(string file)
    {
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



        GlobalTools.FilePath = file;
        MOTFile.bones = new Bone[0];




        GlobalTools.changeColor(ConsoleColor.Green);
        Console.WriteLine("This is a valid MOT File!");
        GlobalTools.changeColor(ConsoleColor.Yellow);
        Thread.Sleep(100);
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
            Console.WriteLine("Header Data:");
            int propertyEndOffset = (countOfKeyframedproperties * 12) + 8;
            int tempCount = 0;
            GlobalTools.changeColor(ConsoleColor.Blue);

            for (int i = 8; i < propertyEndOffset; i += 12)
            {

                Bone bone = new Bone();
                Header keyframe = new Header();
                if (GlobalTools.readValue(fs, br, i + 8, GlobalTools.NumberType.UINT) != 0 && GlobalTools.readValue(fs, br, i + 8, GlobalTools.NumberType.UINT) < fs.Length && GlobalTools.readValue(fs, br, i, GlobalTools.NumberType.UBYTE) != 127)
                {
                    bone.index = GlobalTools.readValue(fs, br, i, GlobalTools.NumberType.UBYTE);
                    bone.type = GlobalTools.getType(GlobalTools.readValue(fs, br, i + 1, GlobalTools.NumberType.UBYTE));
                    keyframe.keyframeCount = GlobalTools.readValue(fs, br, i + 2, GlobalTools.NumberType.USHORT);
                    keyframe.midVal = GlobalTools.readValue(fs, br, i + 4, GlobalTools.NumberType.UINT) == 1;
                    keyframe.adress = GlobalTools.readValue(fs, br, i + 8, GlobalTools.NumberType.UINT);

                    //Console.WriteLine(GlobalTools.readValue(fs, br, i + 4, GlobalTools.NumberType.INT));

                    bone.data = keyframe;
                    MOTFile.addBone(bone);

                    #region console stuff
                    if(1>3)
                    if (tempCount == 0)
                        Console.WriteLine($"Bone index: {bone.index}   (Keyframe Type: {bone.type}, Total Keyframes on property: {keyframe.keyframeCount} MV{keyframe.midVal}, localized at: 0x{keyframe.adress.ToString("X")})");
                    else
                        Console.WriteLine($"Bone index: {bone.index}   (Keyframe Type: {bone.type}, Total Keyframes on property: {keyframe.keyframeCount} MV{keyframe.midVal}, localized at: 0x{keyframe.adress.ToString("X")} ({tempCount}))");
                    tempCount += 1;

                    Thread.Sleep(15);
                    //Console.WriteLine(i);
                    #endregion
                }
            }
            //Thread.Sleep(15);
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
                    Keyframe cv = new Keyframe(); //curve
                    cv.ri = GlobalTools.readValue(fs, br, a, GlobalTools.NumberType.BYTE);
                    additive += GlobalTools.readValue(fs, br, a, GlobalTools.NumberType.BYTE);
                    cv.ai = additive;



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
                List<Keyframe> cvs = MOTFile.bones[i].data.curves.ToList();
                if (MOTFile.bones[i].data.curves.Length < greatest)
                {
                    for (int o = MOTFile.bones[i].data.curves.Length; o < greatest; o++)
                    {
                        cvs.Add(cvs[cvs.Count - 1]);
                    }
                }
                if (cvs.Count > 0) MOTFile.bones[i].data.curves = cvs.ToArray();
            }





            Thread.Sleep(50);
            Console.WriteLine("Creating SMD...");
        }



        GlobalTools.changeColor(ConsoleColor.Green);
        Console.WriteLine("Done!");
        GlobalTools.changeColor(ConsoleColor.Yellow);
        Console.WriteLine("Quantizing Values...");
        MOTFile.Quantize();



        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);

        //Program.plotModel = new PlotModel { Title = "Hermite Curve" };


        var plotView = new PlotView
        {
            Model = Program.plotModel,
            Dock = DockStyle.Fill
        };
        var form = new Form
        {
            Text = file,
            Width = 1280,
            Height = 720
        };
        plotView.Name = Path.GetFileNameWithoutExtension(file);

        form.Controls.Add(plotView);
        Application.Run(form);


        using (FileStream fs = new FileStream(file.Replace(Path.GetFileName(file), "") + Path.GetFileNameWithoutExtension(file) + ".smd", FileMode.Create))
        using (StreamWriter sw = new StreamWriter(fs))
        {


            for(int i = 0; i < Program.bones_.Length-1;i++)
            {
                Console.WriteLine(CalculateRotation(Program.bones_[i].pos, Program.bones_[i+1].pos));
            }

            sw.WriteLine("version 1\nnodes");
            if (1 > 3)
            {
                List<int> BoneIndex = new List<int>();
                for (int i = 0; i < MOTFile.bones.Length; i++)
                {
                    BoneIndex.Add(MOTFile.bones[i].index);
                }
                BoneIndex = BoneIndex.Distinct().ToList();
            }
            for (int i = 0; i < Program.bones_.Length; i++)
            {
                //sw.WriteLine($"{BoneIndex[i] + 1} \"{BoneIndex[i]}\" {BoneIndex[i]}");
                sw.WriteLine($"{Program.bones_[i].parentingOrder} \"{Program.bones_[i].parentingOrder}\" {Program.bones_[i].id}");
                Console.WriteLine();
            }



            sw.WriteLine("end\nskeleton");
            for (int i = 0; i < MOTFile.bones[0].data.Values.Length; i+=2)
            {
                sw.WriteLine("time " + i);
                int curb = -10;
                int aculmulative = 0;
                for (int o = 0; o < MOTFile.bones.Length; o++)
                {

                        float p1 = Program.bones_[MOTFile.bones[o].index+1].pos.X;
                        float p2 = Program.bones_[MOTFile.bones[o].index + 1].pos.Y;
                        float p3 = Program.bones_[MOTFile.bones[o].index + 1].pos.Z;
                        float r1 = 0;
                        float r2 = 0;
                        float r3 = 0;


                        int[] getHowMany = MOTFile.Distinct(MOTFile.bones[o].index);


                        for (int u = 0; u < getHowMany.Length; u++)
                        {
                            //Console.WriteLine(MOTFile.bones[getHowMany[u]].type + "  " + MOTFile.bones[getHowMany[u]].data.curves[i].quantizedValue);
                            //Console.WriteLine(MOTFile.bones[getHowMany[u]].index + 1);

                            if (MOTFile.bones[getHowMany[u]].type == "position.x") p1 += MOTFile.bones[getHowMany[u]].data.Values[i];
                            if (MOTFile.bones[getHowMany[u]].type == "position.y") p2 += MOTFile.bones[getHowMany[u]].data.Values[i];
                            if (MOTFile.bones[getHowMany[u]].type == "position.z") p3 += MOTFile.bones[getHowMany[u]].data.Values[i];
                            if (MOTFile.bones[getHowMany[u]].type == "rotation.x") r1 += MOTFile.bones[getHowMany[u]].data.Values[i];
                            if (MOTFile.bones[getHowMany[u]].type == "rotation.y") r2 += MOTFile.bones[getHowMany[u]].data.Values[i];
                            if (MOTFile.bones[getHowMany[u]].type == "rotation.z") r3 += MOTFile.bones[getHowMany[u]].data.Values[i];
                        }

                        sw.WriteLine($"{MOTFile.bones[o].index + 1}\t{returnDecimal(p1, 8)} {returnDecimal(p2, 8)} {returnDecimal(p3, 8)}\t{returnDecimal(r1, 8)} {returnDecimal(r2, 8)} {returnDecimal(r3, 8)}");
                        aculmulative += 1;
                        curb = MOTFile.bones[o].index;
                    }
                }
            

            //0   0 0 0   1.570796 0 0
            //1   1 0 0   0 0 0
        }

    }

    public static Vector3 CalculateRotation(Vector3 pos1, Vector3 pos2)
    {
        Vector3 direction = pos2 - pos1;
        Vector3 d2 = Vector3.Normalize(direction);
        return new Vector3((float)Math.Atan2(d2.Y, d2.Z), (float)Math.Atan2(d2.X, Math.Sqrt(d2.Y * d2.Y + d2.Z * d2.Z)), 0);
    }


}