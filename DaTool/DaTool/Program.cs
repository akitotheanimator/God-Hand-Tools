using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System;

using System.IO;
using System.Collections.Generic;
using System;
public static class Program
{

    public static void Main(string[] args)
    {
        Console.ForegroundColor = ConsoleColor.Green;
        Console.WriteLine("________       ___________           .__   \r\n\\______ \\ _____\\__    ___/___   ____ |  |  \r\n |    |  \\\\__  \\ |    | /  _ \\ /  _ \\|  |  \r\n |    `   \\/ __ \\|    |(  <_> |  <_> )  |__\r\n/_______  (____  /____| \\____/ \\____/|____/\r\n        \\/     \\/                          ");
        Console.WriteLine("><<                      ><       ><<   ><<  ><<><<< ><<<<<<    ><<<<     \r\n><<                     >< <<     ><<  ><<   ><<     ><<      ><<    ><<  \r\n><<      ><<   ><<     ><  ><<    ><< ><<    ><<     ><<    ><<        ><<\r\n><< ><<   ><< ><<     ><<   ><<   >< ><      ><<     ><<    ><<        ><<\r\n><<   ><<   ><<<     ><<<<<< ><<  ><<  ><<   ><<     ><<    ><<        ><<\r\n><<   ><<    ><<    ><<       ><< ><<   ><<  ><<     ><<      ><<     ><< \r\n><< ><<     ><<    ><<         ><<><<     ><<><<     ><<        ><<<<     \r\n          ><<                                                             ");

        repeat(args);
    }
    public static void repeat(string[] args)
    {
        List<string> dir = new List<string>();
        if (args.Length == 0)
        {
            //if no files were dragged to the application
            Console.WriteLine("Drag and drop a DAT/SCP/CMP/EFF/I/ID/DA/IDD/EMD/EFM file (or folder containing these files) inside this console.");

            Console.WriteLine("The program will scan ALL the directories in a folder recursively.");
            Console.WriteLine("To repack, simply drag the generated dbp file on this console.");
            string path = Console.ReadLine();
            if (Directory.Exists(path))
            {
                string[] allFiles = Directory.GetFiles(path, "*.*", SearchOption.AllDirectories);
                for (int i = 0; i < allFiles.Length; i++)
                {
                    if (!allFiles[i].Contains("_extacted"))
                    {
                        dir.Add(allFiles[i].Replace("\"", ""));
                        Console.WriteLine($"Added {allFiles[i]} from {path} to the queue list.");
                    }
                }
            }
            else
            {
                if (!path.Contains("_extacted"))
                {
                    Console.WriteLine($"Added {path} to the queue list.");
                    dir.Add(path.Replace("\"", ""));
                }
            }
        }
        else
        {
            //if files were dragged to the application
            for (int i = 0; i < args.Length; i++)
            {
                if (Directory.Exists(args[i]))
                {
                    string[] allFiles = Directory.GetFiles(args[i], "*.*", SearchOption.AllDirectories);
                    for (int f = 0; f < allFiles.Length; f++)
                    {
                        if (!allFiles[f].Contains("_extacted"))
                        {
                            dir.Add(allFiles[f].Replace("\"", ""));
                            Console.WriteLine($"Added {allFiles[f]} from {args[i]} to the queue list.");
                        }
                    }
                }
                else
                {
                    if (!args[i].Contains("_extacted"))
                    {
                        Console.WriteLine($"Added {args[i]} to the queue list.");
                        dir.Add(args[i].Replace("\"", ""));
                    }

                }
            }
        }
        if (dir.Count == 0)
        {
            Console.WriteLine("There was no files on the Input. Please, Drag them on the window console...");
            repeat(new string[0]);
        }
        for (int i = 0; i < dir.Count; i++)
        {
            Proceed.ProceedStep(dir[i]);
        }
        repeat(args);
    }
}