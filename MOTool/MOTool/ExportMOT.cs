using System;
using System.Collections.Generic;
using System.Numerics;
using System.Security.Permissions;




public class ExportBones
{
    public Vector3 pos;
    public int exportID = 0;
    public int parentID = 0;
    public bool useIK;

    public float[] VPX;
    public float[] VPY;
    public float[] VPZ;
    public float[] VRX;
    public float[] VRY;
    public float[] VRZ;

    public Vector3 getPosition(int frame, int relative,int parent, bool IKRelative)
    {
        if (!IKRelative)
            return new Vector3(pos.X + VPX[frame], pos.Y + VPY[frame], pos.Z + VPZ[frame]);
        else
        {
            return new Vector3(
            (pos.X + VPX[frame]),
            (pos.Y + VPY[frame]),
            (pos.Z + VPZ[frame])
            );
        }
    }
    public static Matrix4x4 CalculateGlobalToLocalMatrix(Vector3 parentGlobalPosition, Vector3 boneGlobalPosition)
    {
        Vector3 offset = boneGlobalPosition - parentGlobalPosition;
        return Matrix4x4.CreateTranslation(offset);
    }
    public Vector3 getRotation(int frame)
    {
        return new Vector3(VRX[frame], VRY[frame], VRZ[frame]);
    }


    public void fillMissing()
    {
        List<float> tmp = new List<float>();
        if (VPX == null) VPX = new float[0];
        if (VPY == null) VPY = new float[0];
        if (VPZ == null) VPZ = new float[0];
        if (VRX == null) VRX = new float[0];
        if (VRY == null) VRY = new float[0];
        if (VRZ == null) VRZ = new float[0];


        for (int i = 0; i < SMDExportMOT.animation_length; i++)
            tmp.Add(0);
        if (VPX.Length == 0)
            VPX = tmp.ToArray();
        if (VPY.Length == 0)
            VPY = tmp.ToArray();
        if (VPZ.Length == 0)
            VPZ = tmp.ToArray();
        if (VRX.Length == 0)
            VRX = tmp.ToArray();
        if (VRY.Length == 0)
            VRY = tmp.ToArray();
        if (VRZ.Length == 0)
            VRZ = tmp.ToArray();
    }
}
public static class SMDExportMOT
{
    public static ExportBones[] exportBones;
    public static int animation_length = -1;
    #region valve decimal thingy
    public static string returnDecimal(float number)
    {
        string verySmallNumberString = number.ToString();
        decimal convertedVerySmallDecimal = Decimal.Parse(verySmallNumberString, System.Globalization.NumberStyles.Float);
        string curString = convertedVerySmallDecimal.ToString().Replace(",", ".");
        string pass1 = "";
        if (curString.Length > 8)
        {
            if (curString.Contains("-"))
            {
                pass1 = curString.Substring(0, 8 + 1);
            }
            else
            {
                pass1 = curString.Substring(0, 8);
            }
        }
        else
        {
            for (int i = curString.Length; i < 8; i++)
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
        return pass1;
    }
    #endregion
    public static void Export(string file)
    {


        GlobalTools.changeColor(ConsoleColor.Magenta);
        Console.WriteLine("Generating SMD Animation: " + file.Replace(Path.GetFileName(file), "") + Path.GetFileNameWithoutExtension(file) + ".smd.");


        #region initialize variables and etc
        exportBones = new ExportBones[0];
        List<ExportBones> ebns = exportBones.ToList();
        animation_length = -32568;
        int cidx = -32568;
        #endregion
        for (int i = 0; i < Program.bones_.Length; i++)
        {
            ExportBones export = new ExportBones();

            export.parentID = Program.bones_[i].id;//only the indexes that were used on the animation
            export.exportID = Program.bones_[i].parentingOrder;//the parent of the current "exportID" bone
            //Console.WriteLine(export.exportID);
            export.pos = Program.bones_[i].pos;

            int[] bone_datas = MOTFile.Distinct(export.exportID-1);
            for (int p = 0; p < bone_datas.Length; p++)
            {
                export.useIK = MOTFile.bones[bone_datas[p]].data.isAbsoluteCoordinate;
                if (MOTFile.bones[bone_datas[p]].type == "position.x") export.VPX = MOTFile.bones[bone_datas[p]].data.Values;
                if (MOTFile.bones[bone_datas[p]].type == "position.y") export.VPY = MOTFile.bones[bone_datas[p]].data.Values;
                if (MOTFile.bones[bone_datas[p]].type == "position.z") export.VPZ = MOTFile.bones[bone_datas[p]].data.Values;
                if (MOTFile.bones[bone_datas[p]].type == "rotation.x") export.VRX = MOTFile.bones[bone_datas[p]].data.Values;
                if (MOTFile.bones[bone_datas[p]].type == "rotation.y") export.VRY = MOTFile.bones[bone_datas[p]].data.Values;
                if (MOTFile.bones[bone_datas[p]].type == "rotation.z") export.VRZ = MOTFile.bones[bone_datas[p]].data.Values;
                animation_length = MOTFile.bones[0].data.Values.Length;
            }
            ebns.Add(export);
        }
        exportBones = ebns.ToArray();

        for(int i = 0; i < exportBones.Length;i++)
        {
            exportBones[i].fillMissing();
        }



        using (FileStream fs = new FileStream(Program.saveFileTo+"/" + Path.GetFileNameWithoutExtension(file) + ".smd", FileMode.Create))
        using (StreamWriter sw = new StreamWriter(fs))
        {

            sw.WriteLine("version 1\nnodes");
            for (int i = 0; i < Program.bones_.Length; i++)
            {
                if (Program.bones_[i].parentingOrder == 0 && Program.bones_[i].id == -1)
                    sw.WriteLine($"{Program.bones_[i].parentingOrder} \"root\" {Program.bones_[i].id}");
                else
                {
                    sw.WriteLine($"{Program.bones_[i].parentingOrder} \"{Program.bones_[i].parentingOrder}\" {Program.bones_[i].id}");
                }
            }

            int scheduleIK = -32168;

            sw.WriteLine("end\nskeleton");
            for (int frame = 0; frame < MOTFile.bones[0].data.Values.Length; frame++)
            {
                sw.WriteLine("time " + frame);
                for (int bone_frames = 0; bone_frames < exportBones.Length; bone_frames++)
                {
                    if (!exportBones[bone_frames].useIK)
                    {
                        scheduleIK -= 1;
                        if (scheduleIK == 0)
                        {
                            Vector3 p = exportBones[bone_frames].getPosition(frame, bone_frames-1, 1, true);
                            Vector3 r = exportBones[bone_frames].getRotation(frame);
                            sw.WriteLine($"{exportBones[bone_frames].exportID}\t{returnDecimal(p.X)} {returnDecimal(p.Y)} {returnDecimal(p.Z)}\t{returnDecimal(r.X)} {returnDecimal(r.Y)} {returnDecimal(r.Z)}");
                            scheduleIK = -32168;
                        } else
                        {
                            Vector3 p = exportBones[bone_frames].getPosition(frame,0, 1, false);
                            Vector3 r = exportBones[bone_frames].getRotation(frame);
                            sw.WriteLine($"{exportBones[bone_frames].exportID}\t{returnDecimal(p.X)} {returnDecimal(p.Y)} {returnDecimal(p.Z)}\t{returnDecimal(r.X)} {returnDecimal(r.Y)} {returnDecimal(r.Z)}");
                        }
                    } else
                    {
                        scheduleIK = 2;
                        Vector3 p = exportBones[bone_frames].getPosition(frame,0, 1,false);
                        Vector3 r = exportBones[bone_frames].getRotation(frame);
                        sw.WriteLine($"{exportBones[bone_frames].exportID}\t{returnDecimal(p.X)} {returnDecimal(p.Y)} {returnDecimal(p.Z)}\t{returnDecimal(r.X)} {returnDecimal(r.Y)} {returnDecimal(r.Z)}");
                    }

                }
            }
        }

        Console.WriteLine("File saved sucesfully at " + (Program.saveFileTo + "/" + Path.GetFileNameWithoutExtension(file) + ".smd") + "!");
        if(Program.ETA > 0)
        {
            GlobalTools.changeColor(ConsoleColor.White);
            Console.WriteLine(Program.ETA + " Files remaining!");
        }
        Console.WriteLine("-------------------------------------------------------");
    }
}