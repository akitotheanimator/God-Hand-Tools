using System;
using System.Collections.Generic;
using System.IO;

public static class skeletonHeader
{
    public static int boneStartOffset; //32
    public static int boneCount; //16
    public static float constant = 1; //not sure what it means. it's almost awlays set to 0000803F("1") anyways
}
