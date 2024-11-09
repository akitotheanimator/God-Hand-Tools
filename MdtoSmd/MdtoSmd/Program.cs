using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;

class Program
{
    public static void Main(string[] args)
    {
        Console.WriteLine("      ::::::::   ::::::::  :::::::::    :::   :::   ::::::::: ::::::::::: ::::::::   ::::::::    :::   :::   ::::::::: \r\n    :+:    :+: :+:    :+: :+:    :+:  :+:+: :+:+:  :+:    :+:    :+:    :+:    :+: :+:    :+:  :+:+: :+:+:  :+:    :+: \r\n   +:+        +:+        +:+    +:+ +:+ +:+:+ +:+ +:+    +:+    +:+    +:+    +:+ +:+        +:+ +:+:+ +:+ +:+    +:+  \r\n  +#++:++#++ +#+        +#++:++#:  +#+  +:+  +#+ +#+    +:+    +#+    +#+    +:+ +#++:++#++ +#+  +:+  +#+ +#+    +:+   \r\n        +#+ +#+        +#+    +#+ +#+       +#+ +#+    +#+    +#+    +#+    +#+        +#+ +#+       +#+ +#+    +#+    \r\n#+#    #+# #+#    #+# #+#    #+# #+#       #+# #+#    #+#    #+#    #+#    #+# #+#    #+# #+#       #+# #+#    #+#     \r\n########   ########  ###    ### ###       ### #########     ###     ########   ########  ###       ### #########       ");
        Console.WriteLine("><<                      ><       ><<   ><<  ><<><<< ><<<<<<    ><<<<     \r\n><<                     >< <<     ><<  ><<   ><<     ><<      ><<    ><<  \r\n><<      ><<   ><<     ><  ><<    ><< ><<    ><<     ><<    ><<        ><<\r\n><< ><<   ><< ><<     ><<   ><<   >< ><      ><<     ><<    ><<        ><<\r\n><<   ><<   ><<<     ><<<<<< ><<  ><<  ><<   ><<     ><<    ><<        ><<\r\n><<   ><<    ><<    ><<       ><< ><<   ><<  ><<     ><<      ><<     ><< \r\n><< ><<     ><<    ><<         ><<><<     ><<><<     ><<        ><<<<     \r\n          ><<                                                             ");

        repeat(args);
    }

    public static void repeat(string[] args)
    {
        List<string> dir = new List<string>();
        if (args.Length == 0)
        {
            //if no files were dragged to the application
            Console.WriteLine("Drag and drop a file or folder inside this console.");
            string path = Console.ReadLine();
            if (Directory.Exists(path))
            {
                string[] allFiles = Directory.GetFiles(path, "*.*", SearchOption.AllDirectories);
                for (int i = 0; i < allFiles.Length; i++)
                {
                    dir.Add(allFiles[i].Replace("\"", ""));
                    Console.WriteLine($"Added {allFiles[i]} from {path} to the queue list.");
                }
            }
            else
            {
                Console.WriteLine($"Added {path} to the queue list.");
                dir.Add(path.Replace("\"", ""));
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
                        dir.Add(allFiles[f].Replace("\"", ""));
                        Console.WriteLine($"Added {allFiles[f]} from {args[i]} to the queue list.");
                    }
                }
                else
                {
                    Console.WriteLine($"Added {args[i]} to the queue list.");
                    dir.Add(args[i].Replace("\"", ""));

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
            ExtractModel.GUI(dir[i]);
        }
    }
}