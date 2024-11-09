﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Numerics;

public class Header
{
    public byte type;
    public sbyte bone;
    public ushort p, dp, m0, dm0, m1, dm1;
    public keyframe[] curves;
    public float[] oP, oM0, oM1;
    public int[] absoluteTime;

    public void calculateHeaderValues()
    {
        float minP = float.MaxValue,
            maxP = float.MinValue,
            minM0 = float.MaxValue,
            maxM0 = float.MinValue,
            minM1 = float.MaxValue,
            maxM1 = float.MinValue;
        for (int i = 0; i < oP.Length; i++)
        {
            float valueP = oP[i];
            float valueM0 = oM0[i];
            float valueM1 = oM1[i];
            switch(type)
            {
                case 16:
                    valueP += MOTConvert.bones_[bone+1].pos.X; break;
                case 17:
                    valueP += MOTConvert.bones_[bone+1].pos.Y; break;
                case 18:
                    valueP += MOTConvert.bones_[bone+1].pos.Z; break;
            } //applies the offset


            if (valueP > maxP) maxP = valueP;
            if (valueP < minP) minP = valueP;
            if (valueM0 > maxM0) maxM0 = valueM0;
            if (valueM0 < minM0) minM0 = valueM0;
            if (valueM1 > maxM1) maxM1 = valueM1;
            if (valueM1 < minM1) minM1 = valueM1;
        }
        float rP = minP;
        float rdP = (maxP - rP) / 255;
        p = IEEEBinary16.ToUshort(rP);
        dp = IEEEBinary16.ToUshort(rdP);
        float rM0 = minM0;
        float rdM0 = (maxM0 - rM0) / 255;
        m0 = IEEEBinary16.ToUshort(rM0);
        dm0 = IEEEBinary16.ToUshort(rdM0);
        float rM1 = minM1;
        float rdM1 = (maxM1 - rM1) / 255;
        m1 = IEEEBinary16.ToUshort(rM1);
        dm1 = IEEEBinary16.ToUshort(rdM1);

        List<keyframe> curve = new List<keyframe>();
        for (int i = 0; i < oP.Length; i++)
        {
            byte cp = (byte)GlobalTools.Map(oP[i], minP, maxP, 0, 255);
            byte cm0 = (byte)GlobalTools.Map(oM0[i], minM0, maxM0, 0, 255);
            byte cm1 = (byte)GlobalTools.Map(oM1[i], minM1, maxM1, 0, 255);
            byte relative_time = 0;
            if (i - 1 > -1)
                relative_time = (byte)(absoluteTime[i] - absoluteTime[i - 1]);
            else
                relative_time = (byte)(absoluteTime[i]);
            curve.Add(new keyframe(cp,cm0,cm1,relative_time));
        }
        curves = curve.ToArray();
    }
}
public class keyframe
{
    public byte cp, cm0, cm1, time;
    public keyframe(byte cp,byte cm0, byte cm1, byte time)
    {
        this.cp = cp;
        this.cm0 = cm0;
        this.cm1 = cm1;
        this.time = time;
    }
}
public class BONES
{
    public Vector3 pos;
    public short parentingOrder;
    public short id;
}