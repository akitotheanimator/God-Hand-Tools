using System;
using System.Diagnostics;
using System.IO;

public class Program
{
    public static void Main(string[] args)
    {
        GlobalTools.changeColor(ConsoleColor.White);
        Console.WriteLine("   _____ .____    _____  _______                .                                           \r\n  (      /       (      '   /      __.    __.   |                                           \r\n   `--.  |__.     `--.      |    .'   \\ .'   \\  |                                           \r\n      |  |           |      |    |    | |    |  |                                           \r\n \\___.'  /----/ \\___.'      /     `._.'  `._.' /\\__                                         \r\n _                       .    .     _  _______   ___                                        \r\n \\ ___  ,    .          /|    /   / | '   /    .'   `.                                      \r\n |/   \\ |    `         /  \\   |_-'  |     |    |     |                                      \r\n |    ` |    |        /---'\\  |  \\  |     |    |     |                                      \r\n `___,'  `---|.     ,'      \\ /   \\ /     /     `.__.'                                      \r\n         \\___/                                                                              \r\n __   __ .____     .               _                                                        \r\n |    |  /        /|    ,   .   ___/ `   __.                                                \r\n |\\  /|  |__.    /  \\   |   |  /   | | .'   \\                                               \r\n | \\/ |  |      /---'\\  |   | ,'   | | |    |                                               \r\n /    /  /    ,'      \\ `._/| `___,' /  `._.'                                               \r\n                                   `                                                        \r\n _                   __   __ .     .              .          .____  .                 _     \r\n \\ ___  ,    .       |    |  /     / ____  ____   |     ___  /      |     ___    ____ /     \r\n |/   \\ |    `       |\\  /|  |     |    /     /   |   .'   ` |__.   |    /   `  (     |,---.\r\n |    ` |    |       | \\/ |  |     |  ,/    ,/    |   |----' |      |   |    |  `--.  |'   `\r\n `___,'  `---|.      /    /   `._.'  /__.' /__.' /\\__ `.___, /     /\\__ `.__/| \\___.' /    |\r\n         \\___/                       `     `                                                ");
        Console.WriteLine("Write down a operation.");

        GlobalTools.changeColor(ConsoleColor.Green);
        Console.WriteLine("------SES utilities------");
        Console.WriteLine("1: Extract .SES contents\n2: Repack .VAGs to the .SES\n3: Regenerate .SES Table, SBE and SBO Files");
        GlobalTools.changeColor(ConsoleColor.Blue);
        Console.WriteLine("------WAV utilities------");
        Console.WriteLine("4: Convert .WAV to .VAG\n5: Convert .VAG to .WAV");



        GlobalTools.changeColor(ConsoleColor.White);

        string res = Console.ReadLine();
        switch (res)
        {
            case "1":
                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write("drag and drop a ");
                GlobalTools.changeColor(ConsoleColor.Green);
                Console.Write(".SES file ");
                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write("or ");
                GlobalTools.changeColor(ConsoleColor.Green);
                Console.Write("Folder");
                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write(" in this console...");
                Console.WriteLine("");
                string fpath = Console.ReadLine();

                if(File.Exists(fpath) && !Directory.Exists(fpath))
                {
                    EOP.EF(fpath);
                }

                if (!File.Exists(fpath) && Directory.Exists(fpath))
                {
                    GlobalTools.changeColor(ConsoleColor.Green);
                    Console.WriteLine("Reading paths...");
                    string[] paths = Directory.GetFiles(fpath,"*");
                    Console.WriteLine("Paths queue count: " + paths.Length);
                    for (int i = 0; i < paths.Length;i++)
                    {
                        GlobalTools.changeColor(ConsoleColor.Green);
                        Console.WriteLine("------------");
                        Console.WriteLine("working with file "+paths[i]);
                        Console.WriteLine("----------->");
                        EOP.EF(paths[i]);
                    }
                }
                break;
            case "2":
                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write("drag and drop a ");


                GlobalTools.changeColor(ConsoleColor.Green);
                Console.Write("Folder ");


                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write("containing the ");

                GlobalTools.changeColor(ConsoleColor.Green);
                Console.Write("\".SBO\" File ");

                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write("and the ");

                GlobalTools.changeColor(ConsoleColor.Green);
                Console.Write("\"VAG\" Folder.");

                Console.WriteLine("");
                string vagspath = Console.ReadLine();

                if (File.Exists(vagspath) && !Directory.Exists(vagspath))
                {
                    Console.Write("Provided path isn't a folder.");
                    Main(args);
                }

                if (!File.Exists(vagspath) && Directory.Exists(vagspath))
                {
                    GlobalTools.changeColor(ConsoleColor.Green);
                    Console.WriteLine("Reading paths...");
                    EOP.RSES(vagspath);
                }
                break;
            case "3":
                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write("drag and drop a ");
                GlobalTools.changeColor(ConsoleColor.Green);
                Console.Write(".SES file ");
                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write("or ");
                GlobalTools.changeColor(ConsoleColor.Green);
                Console.Write("Folder");
                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write(" in this console...");
                Console.WriteLine("");
                string fpath3 = Console.ReadLine();

                if (File.Exists(fpath3) && !Directory.Exists(fpath3))
                {
                    EOP.EF(fpath3);
                }

                if (!File.Exists(fpath3) && Directory.Exists(fpath3))
                {
                    GlobalTools.changeColor(ConsoleColor.Green);
                    Console.WriteLine("Reading paths...");
                    string[] paths = Directory.GetFiles(fpath3, "*");
                    Console.WriteLine("Paths queue count: " + paths.Length);
                    for (int i = 0; i < paths.Length; i++)
                    {
                        GlobalTools.changeColor(ConsoleColor.Green);
                        Console.WriteLine("------------");
                        Console.WriteLine("working with file " + paths[i]);
                        Console.WriteLine("----------->");
                        EOP.REOT(paths[i]);
                    }
                }
                break;
            case "4":
                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write("drag and drop a ");
                GlobalTools.changeColor(ConsoleColor.Green);
                Console.Write(".WAV file ");
                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write("or ");
                GlobalTools.changeColor(ConsoleColor.Green);
                Console.Write("Folder");
                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write(" in this console. (the ideal sampling rate is 11025 for better results, higher sampling rates will increase the audio quality, but will take more room in the .SES.\n The only type of .WAV files supported is 16-BIT MONO WAV files.");
                Console.WriteLine("");
                string wavpath = Console.ReadLine();

                if (File.Exists(wavpath) && !Directory.Exists(wavpath))
                {
                    EOP.CW(wavpath);
                }

                if (!File.Exists(wavpath) && Directory.Exists(wavpath))
                {
                    GlobalTools.changeColor(ConsoleColor.Green);
                    Console.WriteLine("Reading paths...");
                    string[] paths = Directory.GetFiles(wavpath, "*");
                    Console.WriteLine("Paths queue count: " + paths.Length);
                    for (int i = 0; i < paths.Length; i++)
                    {
                        GlobalTools.changeColor(ConsoleColor.Green);
                        Console.WriteLine("------------");
                        Console.WriteLine("working with file " + paths[i]);
                        Console.WriteLine("----------->");
                        EOP.CW(paths[i]);
                    }
                }
                break;
            case "5":
                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write("drag and drop a ");
                GlobalTools.changeColor(ConsoleColor.Green);
                Console.Write(".VAG file ");
                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write("or ");
                GlobalTools.changeColor(ConsoleColor.Green);
                Console.Write("Folder");
                GlobalTools.changeColor(ConsoleColor.White);
                Console.Write(" in this console.");
                Console.WriteLine("");
                string vagpath = Console.ReadLine();

                if (File.Exists(vagpath) && !Directory.Exists(vagpath))
                {
                    EOP.CV(vagpath);
                }

                if (!File.Exists(vagpath) && Directory.Exists(vagpath))
                {
                    GlobalTools.changeColor(ConsoleColor.Green);
                    Console.WriteLine("Reading paths...");
                    string[] paths = Directory.GetFiles(vagpath, "*");
                    Console.WriteLine("Paths queue count: " + paths.Length);
                    for (int i = 0; i < paths.Length; i++)
                    {
                        GlobalTools.changeColor(ConsoleColor.Green);
                        Console.WriteLine("------------");
                        Console.WriteLine("working with file " + paths[i]);
                        Console.WriteLine("----------->");
                        EOP.CV(paths[i]);
                    }
                }
                break;
        }


        

    }
}


