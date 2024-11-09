using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

public static class ExtractModel
{
    public static string savePath;
    public static string name;
    public static int type = -1;
    public static void GUI(string path)
    {

        savePath = path;
        name = Path.GetFileName(path);
        type = Path.GetFileName(path).ToLower().Contains("scr") ? 0 : 1; //0 = scr, 1 = md
        offsets.process(path);

    }
}
