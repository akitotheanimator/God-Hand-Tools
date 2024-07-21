using System;
using System.Collections.Generic;
using System.DirectoryServices.ActiveDirectory;
using System.Linq;
using System.Runtime.Intrinsics.Arm;
using System.Text;
using System.Threading.Tasks;

using OxyPlot;
using OxyPlot.Series;
using OxyPlot.WindowsForms;
public class Bone
{
    public sbyte index;
    public string type;
    public Header data;
}
public class Keyframe
{
    public int ri;
    public int ai;
    public byte Cp;
    public byte Cm0;
    public byte Cm1;
}

public class Header
{
    public uint adress;
    public ushort keyframeCount;
    public bool midVal;


    public float P;
    public float Dp;
    public float M0;
    public float Dm0;
    public float M1;
    public float Dm1;
    public Keyframe[] curves;

    public float[] Values;


    public float Interpol(int frame, int i)
    {
        GlobalTools.changeColor(ConsoleColor.Blue);
        float p0 = P + Dp * curves[i].Cp;
        float m0 = M1 + Dm1 * curves[i].Cm1;
        float p1 = P + Dp * curves[i+1].Cp;
        float m1 = M0 + Dm0 * curves[i+1].Cm0;







        //Console.WriteLine(curves[i].Cp + "  " + p0 + "  " + curves[i].Cm1 + "  " + m0 + "  " + curves[i].Cm0 + "  " + m1);

        //Console.WriteLine(cusrves[i].RelativeFrameIndex + "   " + curves[i + 1].RelativeFrameIndex);

        //float t = (frame - startIndex) / (float)(stopIndex - startIndex);

        //Console.WriteLine(curves[i].ai + "    " + curves[i + 1].ai);



        float t = (float)(frame - curves[i].ai) / (curves[i + 1].ai - curves[i].ai);
        if (t.ToString() == "NaN") t = 0f;




        float t2 = (float)Math.Pow(t, 2);
        float t3 = (float)Math.Pow(t, 3);
        float a = 2 * t3 - 3 * t2 + 1;
        float b = t3 - 2 * t2 + t;
        float c = -2 * t3 + 3 * t2;
        float d = t3 - t2;

        float ret = a * p0 + b * m0 + c * p1 + d * m1;



        //float ret = (float)(2 * Math.Pow(t,3) - 3 * Math.Pow(t, 2) + 1) * p0 + (float)(Math.Pow(t, 3) - 2 * Math.Pow(t, 2) + t) * m0 + (float)(-2 * Math.Pow(t, 3) + 3 * Math.Pow(t, 2)) * p1 + (float)(Math.Pow(t, 3) - Math.Pow(t, 2)) * m1;


        //Console.WriteLine($"p0:{p0}    m0:{m0}    p1:{p1}    m1:{m1}    t:{t}    ret:{ret}    frame:{frame}    i:{i}");


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



            var lineSeries = new OxyPlot.Series.LineSeries();
            for (int i = 0; i < bones[a].data.curves.Length - 1; i++)
            {
                GlobalTools.changeColor(ConsoleColor.Green);
                //Console.WriteLine(bones[a].data.curves[i].ai + "    " + bones[a].data.curves[i+1].ai);
                //Console.WriteLine(bones[a].data.Interpol(i, i) / 4100f);
                for (int frame = bones[a].data.curves[i].ai; frame <= bones[a].data.curves[i+1].ai; frame++)
                {
                    float v = bones[a].data.Interpol(frame, i);
                    lineSeries.Points.Add(new OxyPlot.DataPoint(frame, v));
                }
            }
            Program.plotModel.Series.Add(lineSeries);
        }
        
    }

    public static Bone[] bones;
    public static void addBone(Bone b)
    {
        List<Bone> Bones = bones.ToList();
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
    public static void addCurve(Keyframe c, Header k)
    {
        if (k.curves != null)
        {
            List<Keyframe> Curves = k.curves.ToList();
            Curves.Add(c);
            k.curves = Curves.ToArray();
        }
        else
        {
            List<Keyframe> Curves = new List<Keyframe>();
            Curves.Add(c);
            k.curves = Curves.ToArray();
        }
    }
}
