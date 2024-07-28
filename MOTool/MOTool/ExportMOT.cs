using System;
using System.Collections.Generic;
using System.Numerics;
using System.Security.Permissions;

public class Bone
{
    public Vector3 LocalPosition { get; set; }
    public Vector3 LocalRotation { get; set; }
    public Bone Parent { get; set; }

    public Matrix4x4 GetLocalToWorldMatrix()
    {
        Matrix4x4 translation = Matrix4x4.CreateTranslation(LocalPosition);
        Matrix4x4 rotation = Matrix4x4.CreateFromYawPitchRoll(LocalRotation.Y, LocalRotation.X, LocalRotation.Z);
        return rotation * translation;
    }

    public Vector3 GetGlobalPosition()
    {
        Matrix4x4 localToWorld = GetLocalToWorldMatrix();
        if (Parent != null)
        {
            Matrix4x4 parentMatrix = Parent.GetLocalToWorldMatrix();
            localToWorld *= parentMatrix;
        }
        return new Vector3(localToWorld.M41, localToWorld.M42, localToWorld.M43);
    }
}
public class ExportBones
{

    public static (Vector3 localPosition, Vector3 localRotation) CalculateLocalTransform(Bone boneA, Vector3 targetGlobalPosition)
    {

        Matrix4x4 globalMatrix = Matrix4x4.Identity;
        Bone currentBone = boneA;
        while (currentBone != null)
        {
            globalMatrix *= currentBone.GetLocalToWorldMatrix();
            currentBone = currentBone.Parent;
        }
        Vector3 currentPosition = new Vector3(globalMatrix.M41, globalMatrix.M42, globalMatrix.M43);
        Matrix4x4 rotationMatrix = Matrix4x4.Identity;
        rotationMatrix.M11 = globalMatrix.M11; rotationMatrix.M12 = globalMatrix.M12; rotationMatrix.M13 = globalMatrix.M13;
        rotationMatrix.M21 = globalMatrix.M21; rotationMatrix.M22 = globalMatrix.M22; rotationMatrix.M23 = globalMatrix.M23;
        rotationMatrix.M31 = globalMatrix.M31; rotationMatrix.M32 = globalMatrix.M32; rotationMatrix.M33 = globalMatrix.M33;
        Vector3 desiredPosition = targetGlobalPosition - currentPosition;
        return (desiredPosition, new Vector3(0, 0, 0));
    }





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




    public (Vector3 globalPosition, Vector3 globalEuler) getGlobal(int frame, int relative)
    {
        List<int> ids = new List<int>();



        int cur_parent = parentID;
        ids.Add(exportID);
        ids.Add(parentID);
        while (cur_parent > 0)
        {
            cur_parent = SMDExportMOT.exportBones[cur_parent].parentID;
            ids.Add(cur_parent);
        }

        Vector3 curZeroP = new Vector3(0, 0, 0);
        Vector3 curZeroR = new Vector3(0, 0, 0);
        //curZeroP -= getPosition(frame);
        //curZeroR -= getRotation(frame);
        for (int i = 0; i < ids.Count - 1; i++)
        {
            //parentPositions.Add(SMDExportMOT.exportBones[ids[i]].getPosition(frame));
            //parentRotation.Add(SMDExportMOT.exportBones[ids[i]].getRotation(frame));

            //curZeroP -= SMDExportMOT.exportBones[ids[i]].getPosition(frame);
            //curZeroR -= SMDExportMOT.exportBones[ids[i]].getRotation(frame);
            Bone cbn = new Bone();
            cbn.LocalPosition = SMDExportMOT.exportBones[ids[i]].getPosition(frame);
            cbn.LocalRotation = SMDExportMOT.exportBones[ids[i]].getRotation(frame);

            Bone cbp = new Bone();
            cbp.LocalPosition = SMDExportMOT.exportBones[ids[i+1]].getPosition(frame);
            cbp.LocalPosition = SMDExportMOT.exportBones[ids[i+1]].getPosition(frame);
            cbn.Parent = cbp;

            Console.WriteLine(ids[i]);
        }

        Console.WriteLine("-----------------------------------------");
        Console.WriteLine(parentID + "   " + exportID + "   " + SMDExportMOT.exportBones[parentID].parentID + "   " + SMDExportMOT.exportBones[SMDExportMOT.exportBones[parentID].parentID].parentID + "    " + SMDExportMOT.exportBones[SMDExportMOT.exportBones[SMDExportMOT.exportBones[parentID].parentID].parentID].parentID);
        Console.WriteLine("-----------------------------------------");
        Console.WriteLine(curZeroP);
        Console.WriteLine("-----------------------------------------");
        //(Vector3 p, Vector3 r) = CalculateLocalTransform();
        return (getPosition(frame) - curZeroP, getRotation(frame) - curZeroR);
    }
    public Vector3 getPosition(int frame)
    {
        return new Vector3(pos.X + VPX[frame], pos.Y + VPY[frame], pos.Z + VPZ[frame]);

    }
    public Vector3 getRotation(int frame)
    {
        //Console.WriteLine(VRX.Length + "  " + VRY.Length + "    " + VRZ.Length + "    " + frame);
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


        for (int i = 0; i < MOTFile.getFrameLength(); i++)
            tmp.Add(0);


        if (VPX.Length == 0 || VPX.Length < tmp.Count)
            VPX = tmp.ToArray();
        if (VPY.Length == 0 || VPY.Length < tmp.Count)
            VPY = tmp.ToArray();
        if (VPZ.Length == 0 || VPZ.Length < tmp.Count)
            VPZ = tmp.ToArray();
        if (VRX.Length == 0 || VRX.Length < tmp.Count)
            VRX = tmp.ToArray();
        if (VRY.Length == 0 || VRY.Length < tmp.Count)
            VRY = tmp.ToArray();
        if (VRZ.Length == 0 || VRZ.Length < tmp.Count)
            VRZ = tmp.ToArray();
    }
}
public static class SMDExportMOT
{
    public static ExportBones[] exportBones;
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
        #endregion
        for (int i = 0; i < Program.bones_.Length; i++)
        {
            ExportBones export = new ExportBones();

            export.parentID = Program.bones_[i].id;//only the indexes that were used on the animation
            export.exportID = Program.bones_[i].parentingOrder;//the parent of the current "exportID" bone
            //Console.WriteLine(export.exportID);
            export.pos = Program.bones_[i].pos;

            int[] bone_datas = MOTFile.Distinct(export.exportID - 1);
            for (int p = 0; p < bone_datas.Length; p++)
            {
                export.useIK = MOTFile.bones[bone_datas[p]].data.isAbsoluteCoordinate;
                if (MOTFile.bones[bone_datas[p]].type == "position.x") export.VPX = MOTFile.bones[bone_datas[p]].data.Values;
                if (MOTFile.bones[bone_datas[p]].type == "position.y") export.VPY = MOTFile.bones[bone_datas[p]].data.Values;
                if (MOTFile.bones[bone_datas[p]].type == "position.z") export.VPZ = MOTFile.bones[bone_datas[p]].data.Values;
                if (MOTFile.bones[bone_datas[p]].type == "rotation.x") export.VRX = MOTFile.bones[bone_datas[p]].data.Values;
                if (MOTFile.bones[bone_datas[p]].type == "rotation.y") export.VRY = MOTFile.bones[bone_datas[p]].data.Values;
                if (MOTFile.bones[bone_datas[p]].type == "rotation.z") export.VRZ = MOTFile.bones[bone_datas[p]].data.Values;
            }
            ebns.Add(export);
        }
        exportBones = ebns.ToArray();

        for (int i = 0; i < exportBones.Length; i++)
        {
            exportBones[i].fillMissing();
        }
        int get = -32168;

        using (FileStream fs = new FileStream(Program.saveFileTo + "/" + Path.GetFileNameWithoutExtension(file) + ".smd", FileMode.Create))
        using (StreamWriter sw = new StreamWriter(fs))
        {

            sw.WriteLine("version 1\nnodes");
            for (int i = 0; i < Program.bones_.Length; i++)
            {
                if (Program.bones_[i].parentingOrder == 0 && Program.bones_[i].id == -1)
                    sw.WriteLine($"{Program.bones_[i].parentingOrder} \"root\" {Program.bones_[i].id}");
                else
                {
                    if (!MOTFile.isIK(MOTFile.Distinct(Program.bones_[i].parentingOrder)))
                    {
                        get -= 1;
                        if (get == 0)
                        {
                            sw.WriteLine($"{Program.bones_[i].parentingOrder} \"{Program.bones_[i].parentingOrder}\" {Program.bones_[i].id}");
                            get = -32168;
                        }
                        else
                        {
                            sw.WriteLine($"{Program.bones_[i].parentingOrder} \"{Program.bones_[i].parentingOrder}\" {Program.bones_[i].id}");
                        }

                    }
                    else
                    {
                        get = 3;
                        sw.WriteLine($"{Program.bones_[i].parentingOrder} \"{Program.bones_[i].parentingOrder}\" {Program.bones_[i].id}");
                    }
                }
            }

            int scheduleIK = -32168;

            sw.WriteLine("end\nskeleton");
            for (int frame = 0; frame < MOTFile.getFrameLength(); frame++)
            {
                sw.WriteLine("time " + frame);
                for (int bone_frames = 0; bone_frames < exportBones.Length; bone_frames++)
                {
                    if (!exportBones[bone_frames].useIK)
                    {
                        scheduleIK -= 1;
                        if (scheduleIK == 0)
                        {
                            //(Vector3 p, Vector3 r) = exportBones[bone_frames].getGlobal(frame,0);
                            Vector3 p = exportBones[bone_frames].getPosition(frame);
                            Vector3 r = exportBones[bone_frames].getRotation(frame);
                            sw.WriteLine($"{exportBones[bone_frames].exportID}\t{returnDecimal(p.X)} {returnDecimal(p.Y)} {returnDecimal(p.Z)}\t{returnDecimal(r.X)} {returnDecimal(r.Y)} {returnDecimal(r.Z)}");
                            scheduleIK = -32168;
                        }
                        else
                        {
                            Vector3 p = exportBones[bone_frames].getPosition(frame);
                            Vector3 r = exportBones[bone_frames].getRotation(frame);
                            sw.WriteLine($"{exportBones[bone_frames].exportID}\t{returnDecimal(p.X)} {returnDecimal(p.Y)} {returnDecimal(p.Z)}\t{returnDecimal(r.X)} {returnDecimal(r.Y)} {returnDecimal(r.Z)}");
                        }
                    }
                    else
                    {
                        scheduleIK = 2;
                        Vector3 p = exportBones[bone_frames].getPosition(frame);
                        Vector3 r = exportBones[bone_frames].getRotation(frame);
                        sw.WriteLine($"{exportBones[bone_frames].exportID}\t{returnDecimal(p.X)} {returnDecimal(p.Y)} {returnDecimal(p.Z)}\t{returnDecimal(r.X)} {returnDecimal(r.Y)} {returnDecimal(r.Z)}");
                    }

                }
            }
        }
        GlobalTools.changeColor(ConsoleColor.White);
        Console.WriteLine("File saved sucesfully at " + (Program.saveFileTo + "/" + Path.GetFileNameWithoutExtension(file) + ".smd") + "!");
        if (Program.ETA - 1 > 0)
        {
            Console.WriteLine((Program.ETA - 1) + " Files remaining!");
        }
        Console.WriteLine("-------------------------------------------------------");
    }
}