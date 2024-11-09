using System;
using System.Collections.Generic;
using System.IO;

public class modelHeader
{
    public string meshName;
    public int vertexOffset; //32
    public int normalsOffset; //8 IT'S REPRESENTED BY DEGREES
    public int UVOffset; //32
    public int FaceColorOffset; //32
    public int boneWeightOffset; //32
    public int faceCount; //16
    public int usedTextureIndexOnDat; //16

}
