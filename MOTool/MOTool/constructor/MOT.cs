using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
public class MOTBone
{
    public sbyte index;
    public byte typeOriginal;
    public string type;
    public MOTHeader data;
}
public class MOTKeyframe
{
    public int absolute_index; //absolute index
    public byte Cp;
    public byte Cm0;
    public byte Cm1;



    public float P0; //when the file uses full values instead of quantized ones
    public float M0;
    public float M1;
}

public class MOTHeader
{
    public uint adress;
    public ushort keyframeCount;
    public bool isAbsoluteCoordinate;


    public float P;
    public float Dp;
    public float M0;
    public float Dm0;
    public float M1;
    public float Dm1;
    public MOTKeyframe[] curves;

    public float[] Values;


    public float Interpol(int frame, int i, bool isQuantized)
    {
        GlobalTools.changeColor(ConsoleColor.Blue);
        float p0 = curves[i].P0;
        float m0 = curves[i].M1;
        float p1 = curves[i + 1].P0;
        float m1 = curves[i + 1].M0;

        if (isQuantized)
        {
            p0 = P + Dp * curves[i].Cp;
            m0 = M1 + Dm1 * curves[i].Cm1;
            p1 = P + Dp * curves[i + 1].Cp;
            m1 = M0 + Dm0 * curves[i + 1].Cm0;
        }


        float t = (float)(frame - curves[i].absolute_index) / (curves[i + 1].absolute_index - curves[i].absolute_index);
        if (t.ToString() == "NaN") t = 0f;

        float ret = (float)(2 * Math.Pow(t,3) - 3 * Math.Pow(t, 2) + 1) * p0 + (float)(Math.Pow(t, 3) - 2 * Math.Pow(t, 2) + t) * m0 + (float)(-2 * Math.Pow(t, 3) + 3 * Math.Pow(t, 2)) * p1 + (float)(Math.Pow(t, 3) - Math.Pow(t, 2)) * m1;


        List<float> floats = new List<float>();
        floats.Add(ret);
        if (Values == null)
        {
            Values = floats.ToArray();
        }
        else
        {
            floats = Values.ToList();
            floats.Add(ret);
            Values = floats.ToArray();
        }
        return ret;
    }

}



public static class MOTFile
{
    public static void Quantize()
    {

        for (int a = 0; a < bones.Length; a++)
        {
            for (int i = 0; i < bones[a].data.curves.Length - 1; i++)
            {
                for (int frame = bones[a].data.curves[i].absolute_index; frame < bones[a].data.curves[i+1].absolute_index; frame++)
                {
                    float v = bones[a].data.Interpol(frame, i, bones[a].typeOriginal < 80);
                }
            }
        }
        
    }

    public static MOTBone[] bones;
    public static void addBone(MOTBone b)
    {
        List<MOTBone> Bones = bones.ToList();
        Bones.Add(b);
        bones = Bones.ToArray();
    }
    public static int[] Distinct(int refi)
    {
        List<int> ind = new List<int>(); //will list every index that has the same property, which means, each one of them will list different actions
        for (int i = 0; i < MOTFile.bones.Length; i++)
        {
            if (MOTFile.bones[i].index == refi) ind.Add(i);
        }
        return ind.ToArray();
    }
    public static bool isIK(int[] re)
    {
        bool ret = false;
        for (int i = 0; i < re.Length; i++)
            if (MOTFile.bones[re[i]].data.isAbsoluteCoordinate)
                ret = true;

        return ret;
    }
    public static int getFrameLength()
    {
        int rlength = -1;
        for (int i = 0; i < bones.Length; i++)
            if (bones[i] != null)
                if (bones[i].data.Values != null)
                    if (bones[i].data.Values.Length > 0)
                        if (rlength < bones[i].data.Values.Length)
                            rlength = bones[i].data.Values.Length;
        return rlength;
    }
    public static void addCurve(MOTKeyframe c, MOTHeader k)
    {
        if (k.curves != null)
        {
            List<MOTKeyframe> Curves = k.curves.ToList();
            Curves.Add(c);
            k.curves = Curves.ToArray();
        }
        else
        {
            List<MOTKeyframe> Curves = new List<MOTKeyframe>();
            Curves.Add(c);
            k.curves = Curves.ToArray();
        }
    }
}
