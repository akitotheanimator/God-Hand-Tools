using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.IO;
using System.Security.Policy;
using System.Numerics;
using System.Globalization;
using System.Data.OleDb;
using System.Reflection;
using System.Runtime.Remoting.Contexts;
public static class Program
{
    public static bool ViewOutput = false;
    public static MdSkeleton MSkeleton;
    public static (string, uint)[] metadata;

    public static bool isNotRestricted;
    static void Main(string[] args)
    {
        //args = new string[] { "C:\\Users\\mathe\\Downloads\\sonic\\sonicMDTEMPMD1.md.txt", "False", "C:\\Users\\mathe\\Downloads\\sonic\\pl00.dat_extacted\\MD\\MD1.md", "False"};
        if (args.Length == 0) //testing a no nesting tip
        {

            Console.WriteLine("No argument was satisfied. Closing now...");
            Thread.Sleep(1000);
            Environment.Exit(0);

        }
        isNotRestricted = bool.Parse(args[args.Length - 1]);
        //Console.WriteLine(args[2]);
        ViewOutput = bool.Parse(args[1]);




        List<(string, uint)> datas = new List<(string, uint)>();


        List<Vector3> PSSK = new List<Vector3>(); //position skeleton
        List<int> OSK = new List<int>(); //order skeleton
        List<short> V1SK = new List<short>(); //v1 skeleton
        List<short> V2SK = new List<short>(); //v1 skeleton

        if(!File.Exists(args[2]))
        {
            Console.WriteLine("The reference md does not exist at path " + args[2] + ".");
            Thread.Sleep(7000);
            Environment.Exit(0);
        }
        using (FileStream fs = new FileStream(args[2], FileMode.Open))
        using (BinaryReader br = new BinaryReader(fs))
        {

            fs.Position = 8;
            uint count = br.ReadUInt32();
            for (int i = 16; i < (count * 4) + 16; i += 4)
            {
                fs.Position = i;



                fs.Position = br.ReadUInt32() + 4;

                uint code = br.ReadUInt32();
                string name = Encoding.UTF8.GetString(br.ReadBytes(8));
                Console.WriteLine(name);
                datas.Add((name, code));
                fs.Position -= 16;



                fs.Position += (br.ReadInt32()+8);
                ushort count2 = br.ReadUInt16();
                fs.Position += 38;

                int checkpoint = (int)fs.Position;

                PSSK.Clear();
                V1SK.Clear();
                V2SK.Clear();
                OSK.Clear();
                for(int f = checkpoint; f < checkpoint + (count2 * 16);f+=16)
                {
                    fs.Position = f;
                    PSSK.Add(new Vector3(br.ReadSingle(), br.ReadSingle(), br.ReadSingle()));
                    V1SK.Add(br.ReadInt16());
                    V2SK.Add(br.ReadInt16());
                    OSK.Add((f - checkpoint) /16);
                }
                //Program.MSkeleton = br.ReadBytes(count2 * 16);
            }
            Program.MSkeleton = new MdSkeleton(PSSK.ToArray(), OSK.ToArray(), V1SK.ToArray(), V2SK.ToArray());
        }
        Program.metadata = datas.ToArray();
        //Console.WriteLine(metadata.Length);




        bool skeleton = true;
        string[] at = File.ReadAllLines(args[0]);
        //File.Delete(args[0]);



        List<Mesh> allMeshes = new List<Mesh>();
        #region get mesh data
        List<Bone> armature = new List<Bone>();
        Mesh cMesh = null;
        for (int i = 0; i < at.Length; i++)
        {
            if (!skeleton)
            {
                if (at[i].Contains("mcs:"))
                {
                    if (cMesh != null)
                    {
                        allMeshes.Add(cMesh);
                    }
                    cMesh = new Mesh();
                    cMesh.name = at[i].Split(':')[1];
                    cMesh.armature = armature.ToArray();
                }
                if (at[i].Contains("|")) //a new face segment
                {
                    #region setup face
                    int materialIndice = 0;
                    try
                    {
                        materialIndice = int.Parse(at[i].Split('|')[0].Split('.')[0]);
                    }
                    catch
                    {
                        Console.WriteLine("The material " + at[i].Split('|')[0].Split('.')[0] + " wasn't in index format. Assign the material name as a number.");
                        Thread.Sleep(9000);
                        Environment.Exit(0);
                    }
                    Console.WriteLine(at[i]);
                    int[] indices = new int[0]; 
                    try
                    {
                        indices = at[i].Split('|')[1].Split(':').Select(int.Parse).ToArray();
                        Console.WriteLine("\"");
                    }
                    catch
                    {
                        Console.WriteLine("The mesh " + cMesh.name + " has a problem.");
                        Thread.Sleep(9000);
                        Environment.Exit(0);
                    }

                    linkedMesh triangle = new linkedMesh();
                    triangle.material = materialIndice;
                    triangle.indices = indices;
                    #endregion

                    List<Triangle> vertices = new List<Triangle>();
                    for (int a = 0; a < indices.Length; a++)
                    {
                        i += 1;
                        Triangle vertice = new Triangle();

                        string[] spl1 = at[i].Split('+');
                        vertice.faceIndice = int.Parse(spl1[0]);
                        string[] data01 = spl1[1].Split(':');


                        for (int j = 0; j < data01.Length; j += 6)
                        {
                            //Console.WriteLine(data01[j]);

                            Vertex vert = new Vertex();

                            //Console.WriteLine(i + "   " + at[i].Split('+')[1]);
                            //Console.WriteLine(data01[j + 0]);
                            int indice = int.Parse(data01[j + 0]);

                            spl1 = data01[j + 1].Split(',');
                            float p1 = float.Parse(spl1[0]);
                            float p2 = float.Parse(spl1[1]);
                            float p3 = float.Parse(spl1[2]);

                            spl1 = data01[j + 2].Split(',');


                            float n1 = float.Parse(spl1[0]);
                            float n2 = float.Parse(spl1[1]);
                            float n3 = float.Parse(spl1[2]);



                            if (data01[j + 3] != "FFFFFF")
                            {
                                spl1 = data01[j + 3].Split(',');


                                float uv1 = float.Parse(spl1[0]);
                                float uv2 = float.Parse(spl1[1]);
                                //Console.WriteLine(uv1 +","+ uv2 + "  " + spl1[0]+","+ spl1[1]);
                                vert.uv = new Vector2(uv1, uv2);
                                List<Vector2> UVsConnect = new List<Vector2>();
                                for(int h = 2; h < spl1.Length;h+=2)
                                {
                                    UVsConnect.Add(new Vector2(float.Parse(spl1[h + 0]), float.Parse(spl1[h + 1])));
                                }
                                vert.connectedUVs = UVsConnect.ToArray();
                                //Console.WriteLine(UVsConnect.Count+ "     CONNECTS!!!");
                            }
                            if (data01[j + 4] != "FF=9")
                            {
                                string[] boneWeights = data01[j + 4].Split(',');
                                //Console.WriteLine(data01[j + 5]);
                                string[] weights = data01[j + 5].Split(',');
                                float weight = float.Parse(weights[0].Replace("FFFFF0", "0")); //the average
                                vert.bones = boneWeights;
                                vert.weight = weight;
                                List<float> wS = new List<float>();
                                for(int gh = 1; gh < weights.Length;gh++)
                                {
                                    wS.Add(float.Parse(weights[gh]));
                                }
                                //Console.WriteLine(data01[j + 5] + "   " + cMesh.name);
                                //Console.WriteLine(vert.eachWeight.Length + "   " + wS.Count);
                                for (int gh = 0; gh < wS.Count; gh++)
                                {
                                    vert.eachWeight[gh] = wS[gh];
                                }
                            }



                            vert.indice = indice;
                            vert.pos = new Vector3(p1, p2, p3);
                            vert.normal = new Vector3(n1, n2, n3);


                            List<Vertex> v = vertice.vertices.ToList();
                            v.Add(vert);
                            vertice.vertices = v.ToArray();
                        }

                        vertice.calculateOrder();
                        vertices.Add(vertice);
                    }
                    triangle.triangles = vertices.ToArray();


                    List<linkedMesh> cFaces = cMesh.faces.ToList();
                    cFaces.Add(triangle);
                    cMesh.faces = cFaces.ToArray();
                }
            }
            if (skeleton)
            {
                string[] skel = at[i].Split(':');
                int id = 0;
                for (int c = 1; c < skel.Length - 1; c += 6)
                {
                    //Console.WriteLine(skel[c]);  
                    //Console.WriteLine(c/6);
                    try {
                        //Console.WriteLine(float.Parse(skel[c + 3]) + "   " + float.Parse(skel[c + 3], CultureInfo.InvariantCulture) + "      " + skel[c]);
                        armature.Add(new Bone(skel[c], int.Parse(skel[c + 1]), int.Parse(skel[c + 2]), new Vector3(float.Parse(skel[c + 3], CultureInfo.InvariantCulture), float.Parse(skel[c + 4], CultureInfo.InvariantCulture), float.Parse(skel[c + 5], CultureInfo.InvariantCulture))));
                    }
                    catch
                    {
                        //Console.WriteLine(skel[c] + "     " + skel[c + 1] + "        "  + skel[c + 2]);
                        try
                        {
                            int.Parse(skel[c + 2]);
                        } catch
                        {
                            Console.WriteLine("The bone \"" + skel[c] + "\" has parent \"" + skel[c + 2] + "\", that wasn't in index format. Assign the parent bone name as a number.");
                        }
                        try
                        {
                            int.Parse(skel[c]);
                        }
                        catch
                        {
                            Console.WriteLine("The bone \"" + skel[c] + "\" wasn't in index format. Assign the bone name as a number.");
                        }
                        Thread.Sleep(9000);
                        Environment.Exit(0);
                    }
                    }
                skeleton = false;
            }
        }
        allMeshes.Add(cMesh);
        #endregion

        //Console.WriteLine(Path.GetDirectoryName(args[0]) + "/" + Path.GetFileNameWithoutExtension(args[0]).Substring(6) + ".md");
        //File.Delete(args[0]);




        core.calculateMD(allMeshes.ToArray(), Path.GetDirectoryName(args[0]) + "/" + Path.GetFileNameWithoutExtension(args[0]).Substring(6) + ".md");
    }
}