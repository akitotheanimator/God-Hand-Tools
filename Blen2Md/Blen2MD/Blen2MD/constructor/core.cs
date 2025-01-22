using System;
using System.CodeDom;
using System.Collections;
using System.Collections.Generic;
using System.Data.OleDb;
using System.Diagnostics.Eventing.Reader;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Runtime.Remoting.Messaging;
using System.Text;
using System.Threading.Tasks;
using System.Web;
using System.Linq;
using System.Numerics;
using static System.Net.WebRequestMethods;
using System.Security.Cryptography.X509Certificates;
using System.Net.Configuration;
using System.Runtime.Serialization.Formatters;
using System.Security.Policy;
using System.Threading;
using System.IO.Pipes;
using System.Diagnostics.SymbolStore;

public static class core
{
    public static void calculateMD(Mesh[] model, string saveFile)
    {
        if (3 > 6)
        {
            for (int v = 0; v < model.Length; v++)
            {
                //all.armature
                List<Bone> arm = new List<Bone>();
                foreach (var hg1 in model[v].armature)
                {
                    Console.WriteLine("B4: " + hg1.nameO);
                }
            }
            for (int v = 0; v < model.Length; v++)
            {
                //all.armature
                List<Bone> arm = new List<Bone>();
                foreach (var hg1 in model[v].armature)
                {
                    for (int hg2 = 0; hg2 < Program.MSkeleton.pos.Length; hg2++)
                    {
                        if (int.Parse(hg1.nameO) - 1 == Program.MSkeleton.index[hg2])
                        {
                            hg1.parentName = Program.MSkeleton.v2[hg2];
                            arm.Add(hg1);
                            continue;
                        }
                    }
                }
                model[v].armature = arm.ToArray();
            }
            for (int v = 0; v < model.Length; v++)
            {
                //all.armature
                List<Bone> arm = new List<Bone>();
                foreach (var hg1 in model[v].armature)
                {
                    Console.WriteLine("AFTER: " + hg1.nameO);
                }
            }


            foreach (var all in model)
            {
                foreach (var hg1 in all.armature)
                {

                    foreach (var hg2 in all.armature)
                    {
                        if (hg1.parentName == hg2.name)
                        {
                            hg1.pos = hg2.pos - hg1.pos;
                            continue;
                        }
                    }

                }
            }
        }
        if (Program.isNotRestricted == false)
        {
            List<Bone> sortBones = new List<Bone>();



            for (int y = 0; y < Program.MSkeleton.v2.Length; y++)
            {
                for (int o = 0; o < model[0].armature.Length; o++)
                {
                    if (int.Parse(model[0].armature[o].nameO) == y + 1)
                    {
                        sortBones.Add(model[0].armature[o]);
                    }
                }
            }

            model[0].armature = sortBones.ToArray();
        }
        for (int o = 0; o < model[0].armature.Length; o++)
        {
            model[0].armature[o].index = o;
        }
        List<Vector3> positions = new List<Vector3>();
        for (int o = 0; o < model[0].armature.Length; o++)
        {
            Console.WriteLine("OLHAMATHEUSQFISICAS: " + (int.Parse(model[0].armature[o].nameO)) + "    " + (model[0].armature[o].parentName) + "    " + model[0].armature[o].pos);
            positions.Add(model[0].armature[o].pos);
        }
        for (int v = 0; v < Program.MSkeleton.v2.Length; v++)
        {

            //Console.WriteLine("OLHAMATHEUSQFISICASWAW: " + (v+1) + "   " +  (Program.MSkeleton.v2[v]));
            Console.WriteLine("OLHAMATHEUSQFISICASWAW: " + (v + 1) + "       P:" + (Program.MSkeleton.v2[v] + 1));
        }


        Console.WriteLine(positions.Count);



        List<Mesh> Reorder = new List<Mesh>();
        Console.WriteLine("NAME: " + Program.metadata.Length);
        Console.WriteLine("SKEL: " + Program.MSkeleton.pos.Length);
        if (Program.isNotRestricted == false)
        {
            for (int i = 0; i < Program.metadata.Length; i++)
            {
                for (int e = 0; e < model.Length; e++)
                {
                    Console.WriteLine(Program.metadata[i].Item1 + "  " + model[e].name);
                    if (Program.metadata[i].Item1.Contains(model[e].name))
                    {

                        Reorder.Add(model[e]);
                        Reorder[Reorder.Count - 1].unknownNumber = Program.metadata[i].Item2;
                        continue;
                    }
                }
            }
            if (Reorder.Count != model.Length)
            {

                Console.WriteLine("Mesh count does not match!    Mesh: " + model.Length + "  Found: " + Reorder.Count);
                Thread.Sleep(7000);
                Environment.Exit(0);
            }
            model = Reorder.ToArray();
        }


        for (int i = 0; i < model.Length; i++)
        {
            for (int o = 0; o < model[i].faces.Length; o++)
            {
                int[] getIndicesFromFace(int face)
                {
                    foreach (var t in model[i].faces[o].triangles) if (t.faceIndice == face) return new int[] { t.vertices[0].indice, t.vertices[1].indice, t.vertices[2].indice };
                    return new int[] { 0, 0, 0 };
                }
                Console.WriteLine(model[i].name);
                model[i].faces[o].calculatePosition();

                List<Triangle> tris = model[i].faces[o].triangles.ToList();
                List<Triangle> orderedTris = new List<Triangle>();
                tris[0].f = false;
                orderedTris.Add(tris[0]);
                tris.Remove(tris[0]);


                
                //tris.Remove(tris[0]);
                while (tris.Count > 0)
                {
                    bool f = false;

                    Triangle sel = orderedTris[orderedTris.Count - 1];


                    foreach (var all in tris)
                    {
                        int[] check = new int[] { all.vertices[0].indice, all.vertices[1].indice, all.vertices[2].indice };


                        //Console.WriteLine(sel.vertices[1].indice + "  " + sel.vertices[2].indice + "     " + GlobalTools.returnStringFromArray(check) + "   " + check.Intersect(new int[] { sel.vertices[1].indice, sel.vertices[2].indice }).Count());


                        //if (check.Intersect(new int[] { sel.vertices[1].indice, sel.vertices[2].indice }).Count() == 2 && !orderedTris.Contains(all))

                        //if 2 verts connect, the UVs matches, and the triangle wasn't added yet, it will be added to the sorted list.
                        if (check.Intersect(new int[] { sel.vertices[1].indice, sel.vertices[2].indice }).Count() == 2 && sel.Intersects(all) && !orderedTris.Contains(all))
                        {
                            Triangle cTemp = all;
                            if (all.vertices[0].indice != sel.vertices[1].indice || all.vertices[1].indice != sel.vertices[2].indice)
                            {


                                Triangle reorder = new Triangle();
                                reorder.vertices = new Vertex[3];
                                reorder.vertices[0] = sel.vertices[1];
                                reorder.vertices[1] = sel.vertices[2];


                                foreach (var a in cTemp.vertices)
                                {
                                    int match = 0;
                                    foreach (var b in sel.vertices)
                                    {
                                        if (a.indice == b.indice)
                                        {
                                            match++;
                                        }
                                    }
                                    if (match == 0)
                                    {
                                        reorder.vertices[2] = a;
                                        break;
                                    }
                                }

                                cTemp.vertices = reorder.vertices;
                            }
                            orderedTris.Add(cTemp);
                            tris.Remove(cTemp);
                            f = true;
                            break;
                        }

                        if (f == true) break;
                    }
                    if (f == false)
                    {
                        tris[0].f = false;
                        orderedTris.Add(tris[0]);
                        tris.Remove(tris[0]);
                    }
                } //this is the most robust and consistent system to find the best matching indices(if possible), the best overall method i've found.
                for (int f = 0; f < model[i].faces[o].triangles.Length; f++)
                {
                    //Console.WriteLine(model[i].faces[o].triangles[f].vertices[0].indice + "  " + model[i].faces[o].triangles[f].vertices[1].indice + "   " + model[i].faces[o].triangles[f].vertices[2].indice);

                }
                //Console.WriteLine("OOOOOOOOOOOOO");
                foreach (var a in orderedTris)
                {
                    //VIAAA
                    //Console.WriteLine(a.vertices[0].indice + "  " + a.vertices[1].indice + "   " + a.vertices[2].indice + "   " + a.f + "   " + a.vertices[0].normal + "  " + a.vertices[1].normal + "  " + a.vertices[2].normal);
                }
                // Console.WriteLine("------------");
                model[i].faces[o].triangles = orderedTris.ToArray();



                if (1 > 3)
                {
                    model[i].faces[o].triangles[0].vertices[0].code = 32768;
                    model[i].faces[o].triangles[0].vertices[1].code = 32768;
                    model[i].faces[o].triangles[0].vertices[2].code = 0;
                    #region this method is inneficient due to the amount of iterations crampled together, but for this ocasion it works well, since the game very weak on storage capability.
                    for (int f = 1; f < model[i].faces[o].triangles.Length; f++)
                    {
                        if (model[i].faces[o].triangles[f].vertices[0].indice == model[i].faces[o].triangles[f - 1].vertices[1].indice)
                        {
                            model[i].faces[o].triangles[f].vertices[0].code = -150; //imaginary code, this means the vert will be skipped. (on this code.)
                        }
                        if (model[i].faces[o].triangles[f].vertices[1].indice == model[i].faces[o].triangles[f - 1].vertices[2].indice)
                        {
                            model[i].faces[o].triangles[f].vertices[1].code = -150;
                        }
                        if (model[i].faces[o].triangles[f].vertices[0].indice != model[i].faces[o].triangles[f - 1].vertices[1].indice)
                        {
                            model[i].faces[o].triangles[f].vertices[0].code = 32768;
                        }
                        if (model[i].faces[o].triangles[f].vertices[1].indice != model[i].faces[o].triangles[f - 1].vertices[2].indice || model[i].faces[o].triangles[f].vertices[0].code == 32768)
                        {
                            model[i].faces[o].triangles[f].vertices[1].code = 32768;
                        }
                    }

                    int vCount = 0;
                    for (int f = 1; f < model[i].faces[o].triangles.Length; f++)
                    {
                        vCount++;
                        if (model[i].faces[o].triangles[f].vertices[0].code == 32768) vCount = 0;
                        if (vCount % 2 != 0 && vCount > 0)
                        {
                            Triangle switchPosition(Triangle input)
                            {
                                Triangle ret = input;
                                Vertex f0 = input.vertices[0];
                                Vertex f2 = input.vertices[1];
                                ret.vertices[1] = f0;
                                ret.vertices[0] = f2;
                                return ret;
                            }
                            model[i].faces[o].triangles[f] = switchPosition(model[i].faces[o].triangles[f]);
                            model[i].faces[o].triangles[f].vertices[2].code = 1;
                        }
                    }

                    #endregion
                }



                List<int[]> ore = new List<int[]>();
                int cCo = 0;
                for (int f = 0; f < model[i].faces[o].triangles.Length; f++)
                {

                    Vector3 edge1 = model[i].faces[o].triangles[f].vertices[1].pos - model[i].faces[o].triangles[f].vertices[0].pos;
                    Vector3 edge2 = model[i].faces[o].triangles[f].vertices[2].pos - model[i].faces[o].triangles[f].vertices[0].pos;
                    Vector3 faceNormal = Vector3.Cross(edge1, edge2);
                    faceNormal = Vector3.Normalize(faceNormal);

                    Vector3 averageNormal = (model[i].faces[o].triangles[f].vertices[0].normal + model[i].faces[o].triangles[f].vertices[1].normal + model[i].faces[o].triangles[f].vertices[2].normal) / 3.0f;
                    averageNormal = Vector3.Normalize(averageNormal);
                    float dotProduct = Vector3.Dot(faceNormal, averageNormal);


                    if (model[i].faces[o].triangles[f].f == true)
                    {
                        cCo++;
                        //ore.Add(new int[] {-150, -150, cCo % 2 == 0 ? 0 : 1 });


                        if (dotProduct > 0)
                        {
                            ore.Add(new int[] { -150, -150, 0 });
                        }
                        else
                        {
                            ore.Add(new int[] { -150, -150, 1 });
                        }
                    }
                    else
                    {
                        cCo = 0;
                        if (dotProduct > 0)
                        {
                            ore.Add(new int[] { 32768, 32768, 0 });
                        }
                        else
                        {
                            ore.Add(new int[] { 32768, 32768, 1 });
                        }
                    }
                    model[i].faces[o].triangles[f].codes = ore[ore.Count - 1];
                }




                int c = 0;
                foreach (var f in model[i].faces[o].triangles)
                {
                    //Console.WriteLine("RES " + GlobalTools.returnStringFromVertices(f.vertices) + "      " + GlobalTools.returnStringFromArray(ore[c]) + "      " + f.f + "      " + GlobalTools.returnStringFromArray(f.codes) + "         " + model[i].faces[o].indices.Length + "    " + model[i].name + "   " + model[i].faces[o].material + "         " + f.vertices[0].uv + "," + f.vertices[1].uv + "," + f.vertices[2].uv);
                    Console.WriteLine("RES " + GlobalTools.returnStringFromVertices(f.vertices) + "      " + GlobalTools.returnStringFromArray(ore[c]) + "      "+ "         " + f.vertices[0].uv + "/" + f.vertices[1].uv + "/" + f.vertices[2].uv);
                    c++;
                }
            }
        }





        saveMD(model, saveFile, positions.ToArray());
    }

    public static void saveMD(Mesh[] model, string saveTo, Vector3[] positions)
    {
        using (FileStream fs = new FileStream(saveTo, FileMode.Create))
        using (BinaryWriter bw = new BinaryWriter(fs))
        {
            List<Bone> armature = model[0].armature.ToList();
            List<long> offsetMdbs = new List<long>();


            #region utility voids
            void autoIdent()
            {
                while (fs.Position % 16 != 0) bw.Write((byte)0);
            }
            void writeAtOffset(long position, dynamic what)
            {
                long bkp = fs.Position;
                fs.Position = position;
                bw.Write(what);
                fs.Position = bkp;
            }
            //sbyte Map(double x, double inMin, double inMax, double outMin, double outMax)
            //{
            //    return (sbyte)Math.Round((x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin);
            //}

            double Map(double value, double old_min, double old_max, double new_min, double new_max)
            {
                return (value - old_min) / (old_max - old_min) * (new_max - new_min) + new_min;
            }

            


            #endregion
            bw.Write(7496563);
            bw.Write(3);
            bw.Write(model.Length);
            bw.Write(0);
            List<long> adressWrittingPositions = new List<long>();
            foreach (var g in model)
            {
                adressWrittingPositions.Add((long)fs.Position);
                bw.Write(0);
            }
            autoIdent();
            foreach (var meshes in model)
            {
                long offsetMdb = fs.Position;
                offsetMdbs.Add(offsetMdb);

                bw.Write(6448237);//mdb
                bw.Write(48);
                //bw.Write((ushort)meshes.armature.Length);
                ushort countSkel = (ushort)(Program.MSkeleton.pos.Length);
                bw.Write(countSkel);
                bw.Write((ushort)meshes.faces.Length);

                //bw.Write((ushort)Program.MSkeleton.Length);



                bw.Write(0);
                bw.Write(0);
                bw.Write(0);
                bw.Write(0);
                bw.Write(1f);
                long writeMeshAdressLater = fs.Position;
                for (int g = 0; g < 4; g++) bw.Write(0);

                //Console.WriteLine(Program.MSkeleton.Length);
                //Console.WriteLine(bone.nameO);
                for (int g = 0; g < Program.MSkeleton.pos.Length; g++)
                {
                    //Console.WriteLine(Program.MSkeleton.index[g] + "   "  + g);

                    //Bone p = getBoneParent(armature[g]);
                    //Vector3 v3 = getBoneHiercharyPosition(armature[g]);


                    //bw.Write(Program.MSkeleton.pos[g].X + (armature[g].pos.X - p.pos.X));
                    //bw.Write(Program.MSkeleton.pos[g].Y + (armature[g].pos.Y - p.pos.Y));
                    //bw.Write(Program.MSkeleton.pos[g].Z + (armature[g].pos.Z - p.pos.Z));

                    bw.Write(positions[g].X);
                    bw.Write(positions[g].Y);
                    bw.Write(positions[g].Z);

                    Console.WriteLine((g + 1) + "           " + positions[g]);
                    //bw.Write(Program.MSkeleton.pos[g].X + (armature[g].pos.X);
                    //bw.Write(Program.MSkeleton.pos[g].Y);
                    //bw.Write(Program.MSkeleton.pos[g].Z);
                    bw.Write(Program.MSkeleton.v1[g]);
                    bw.Write(Program.MSkeleton.v2[g]);
                }
                Console.WriteLine("----------------------");

                if (3 > 4)
                {
                    foreach (var bone in armature)
                    {
                        //Console.WriteLine(bone.nameO);
                        for (int g = 0; g < Program.MSkeleton.pos.Length; g++)
                        {
                            //Console.WriteLine(Program.MSkeleton.index[g] + "   "  + g);
                            if ((g + 1).ToString() == bone.nameO)
                            {
                                bw.Write(bone.pos.X);
                                bw.Write(bone.pos.Y);
                                bw.Write(bone.pos.Z);
                                bw.Write(Program.MSkeleton.v1[g]);
                                bw.Write(Program.MSkeleton.v2[g]);
                                continue;
                            }
                        }
                    }
                }
                if (1 > 3)
                {
                    foreach (var bone in armature)
                    {
                        bw.Write(bone.pos.X);
                        bw.Write(bone.pos.Y);
                        bw.Write(bone.pos.Z);
                        bw.Write((short)-1);
                        bw.Write((short)bone.parentName);
                    }
                }
                foreach (var linkedMesh in meshes.faces)
                {
                    writeAtOffset(writeMeshAdressLater, (int)(fs.Position - offsetMdb));
                    writeMeshAdressLater += 4;


                    long offsetMesh = fs.Position;
                    bw.Write(32);
                    long offsetNormal = fs.Position;
                    bw.Write(0);
                    long offsetUV = fs.Position;
                    bw.Write(0);
                    long offsetVertColor = fs.Position;
                    bw.Write(0);
                    long offsetBoneWeight = fs.Position;
                    bw.Write(0);

                    long offsetVerticesCount = fs.Position;
                    bw.Write((ushort)0);
                    bw.Write((ushort)linkedMesh.material);
                    autoIdent();

                    ushort vCount = 0;
                    foreach (var vertices in linkedMesh.triangles)
                    {
                        //Console.WriteLine(vertices.vertices[0].indice + "  " + vertices.vertices[1].indice + "  " + vertices.vertices[2].indice);
                        for (int c = 0; c < 3; c++)
                        {
                            if (vertices.codes[c] != -150)
                            {
                                //Console.WriteLine(vertices.vertices[c].indice + "   " + vertices.vertices[c].code);
                                bw.Write(vertices.vertices[c].pos.X);
                                bw.Write(vertices.vertices[c].pos.Y);
                                bw.Write(vertices.vertices[c].pos.Z);
                                bw.Write(vertices.codes[c]);
                                vCount++;
                            }
                        }
                    }
                    writeAtOffset(offsetVerticesCount, vCount);
                    writeAtOffset(offsetNormal, (uint)(fs.Position - offsetMesh));

                    foreach (var normals in linkedMesh.triangles)
                    {
                        for (int c = 0; c < 3; c++)
                        {
                            if (normals.codes[c] != -150)
                            {
                                //bw.Write(Map(normals.vertices[c].normal.X, -1f, 1f, -128, 127));
                                //bw.Write(Map(normals.vertices[c].normal.Y, -1f, 1f, -128, 127));
                                //bw.Write(Map(normals.vertices[c].normal.Z, -1f, 1f, -128, 127));


                                float le = (float)(Math.Pow(normals.vertices[c].normal.X, 2) + Math.Pow(normals.vertices[c].normal.Y, 2) + Math.Pow(normals.vertices[c].normal.Z, 2));


                                
                                float X = normals.vertices[c].normal.X*-1;
                                float Y = normals.vertices[c].normal.Y*-1;
                                float Z = normals.vertices[c].normal.Z*-1;



                                bw.Write((sbyte)Math.Round(Map(X, -1f, 1f, -128, 127)));
                                bw.Write((sbyte)Math.Round(Map(Y, -1f, 1f, -128, 127)));
                                bw.Write((sbyte)Math.Round(Map(Z, -1f, 1f, -128, 127)));

                                //bw.Write((sbyte)Math.Round(X * 127));
                                //bw.Write((sbyte)Math.Round(Y * 127));
                                //bw.Write((sbyte)Math.Round(Z * 127));


                                //bw.Write((sbyte) Math.Round(Map(X, -1, 1, -128, 127)));

                                //Console.WriteLine((sbyte)Math.Round(Map(X, -1, 1, -128, 127)) + "      " + Math.Round(Map(X, -1, 1, -128, 127)) + "     " + Map(X, -1, 1, -128, 127));

                                //bw.Write((sbyte)Math.Round(Map(Y, -1, 1, -128, 127)));
                                //bw.Write((sbyte)Math.Round(Map(Z, -1, 1, -128, 127)));
                                bw.Write((byte)0);

                                
                            }
                        }
                    }
                    autoIdent();
                    writeAtOffset(offsetUV, (uint)(fs.Position - offsetMesh));

                    foreach (var uv in linkedMesh.triangles)
                    {
                        for (int c = 0; c < 3; c++)
                        {
                            if (uv.codes[c] != -150)
                            {
                                //Console.WriteLine("UV:  " + uv.vertices[c].uv.X * 4100f + "    " + uv.vertices[c].uv.Y * 4100f + "       " + (short)Math.Round(uv.vertices[c].uv.X * 4100f) + "    " + (short)Math.Round(uv.vertices[c].uv.Y * 4100f) + "       " + uv.vertices[c].uv.X + "    " + uv.vertices[c].uv.Y);
                                bw.Write((short)Math.Round(uv.vertices[c].uv.X * 4096f));
                                bw.Write((short)Math.Round(((uv.vertices[c].uv.Y * -1)) * 4096f));
                            }
                        }
                    }
                    autoIdent();
                    writeAtOffset(offsetVertColor, (uint)(fs.Position - offsetMesh));

                    foreach (var color in linkedMesh.triangles)
                    {
                        for (int c = 0; c < 3; c++)
                        {
                            if (color.codes[c] != -150)
                            {
                                bw.Write(2155905152);
                            }
                        }
                    }
                    autoIdent();
                    writeAtOffset(offsetBoneWeight, (uint)(fs.Position - offsetMesh));

                    foreach (var bone in linkedMesh.triangles)
                    {
                        for (int c = 0; c < 3; c++)
                        {
                            if (bone.codes[c] != -150)
                            {
                                List<(byte, byte)> namesWeights = new List<(byte, byte)>();
                                bw.Write((byte)0);
                                foreach (var boneName in armature)
                                {

                                    if (boneName.nameO == bone.vertices[c].bones[0] ||
                                        boneName.nameO == bone.vertices[c].bones[1] ||
                                        boneName.nameO == bone.vertices[c].bones[2])
                                    {
                                        byte chosenWeight = 0;
                                        if (boneName.nameO == bone.vertices[c].bones[0])
                                            chosenWeight = (byte)Math.Round(bone.vertices[c].eachWeight[0] * 100);

                                        if (boneName.nameO == bone.vertices[c].bones[1])
                                            chosenWeight = (byte)Math.Round(bone.vertices[c].eachWeight[1] * 100);

                                        if (boneName.nameO == bone.vertices[c].bones[2])
                                            chosenWeight = (byte)Math.Round(bone.vertices[c].eachWeight[2] * 100);

                                        namesWeights.Add(((byte)boneName.index, chosenWeight));
                                    }

                                }
                                for (int i = 0; i < namesWeights.Count; i++)
                                {
                                    if (namesWeights[i].Item1 == 0)
                                    {
                                        namesWeights.Remove(namesWeights[i]);
                                        i -= 1;
                                    }
                                    else
                                    {
                                        var n1 = namesWeights[i];
                                        n1.Item1 *= 4;
                                        namesWeights[i] = n1;

                                    }
                                }
                                int sm = 0;
                                for (int i = 0; i < namesWeights.Count; i++)
                                {
                                    sm += namesWeights[i].Item2;
                                }
                                for (int i = 0; i < namesWeights.Count; i++)
                                {
                                    var kl = namesWeights[i];
                                    kl.Item2 = (byte)Math.Round(namesWeights[i].Item2 * 100f / sm);
                                    namesWeights[i] = kl;
                                }
                                sm = 0;
                                for (int i = 0; i < namesWeights.Count; i++)
                                {
                                    sm += namesWeights[i].Item2;
                                }
                                sbyte diff = (sbyte)(100 - sm);
                                


                                namesWeights.Sort((a, b) => a.CompareTo(b)); //from lowest to biggest number
                                if (namesWeights.Count > 0)
                                {
                                    var t1 = namesWeights[namesWeights.Count - 1];
                                    t1.Item2 = (byte)(t1.Item2 + diff);
                                    namesWeights[namesWeights.Count - 1] = t1;



                                    sm = 0;
                                    for (int i = 0; i < namesWeights.Count; i++)
                                    {
                                        sm += namesWeights[i].Item2;
                                    }
                                    //Console.WriteLine(sm);


                                    foreach (var g in namesWeights)
                                    {
                                        bw.Write(g.Item1);
                                    }

                                    int pass = 3 - namesWeights.Count;
                                    //Console.WriteLine("BONES:  " + name1 + "    " + name2 + "    " + name3);
                                    for (int gh = 0; gh < pass; gh++) bw.Write((byte)0);


                                    foreach (var g in namesWeights)
                                    {
                                        bw.Write(g.Item2);
                                    }

                                    for (int gh = 0; gh < pass; gh++) bw.Write((byte)0);
                                    bw.Write((byte)0);
                                } else
                                {
                                    bw.Write((byte)0);
                                    bw.Write((byte)0);
                                    bw.Write((byte)0);
                                }
                            }
                        }
                    }
                    autoIdent();
                }

            }
            List<long> adressToWrite = new List<long>();

            for (int f = 0; f < 20; f++) bw.Write(0);
            for (int meshes = 0; meshes < model.Length; meshes++)
            {
                adressToWrite.Add(fs.Position);
                bw.Write((int)(offsetMdbs[meshes] - fs.Position));


                bw.Write(model[meshes].unknownNumber);

                string name = model[meshes].name;
                if (name.Length > 8) name = name.Substring(0, 8);
                bw.Write(Encoding.ASCII.GetBytes(name));
                autoIdent();

                bw.Write(1f); bw.Write(1f); bw.Write(1f); //scales
                bw.Write(0f); bw.Write(0f); bw.Write(0f); //rotations
                bw.Write(0f); bw.Write(0f); bw.Write(0f); //position
                autoIdent();

                bw.Write(0);
                bw.Write(600f);
                bw.Write(8323072);
                bw.Write(0);
                for (int g = 0; g < 8; g++) bw.Write(0);
            }
            for (int g = 0; g < adressWrittingPositions.Count; g++)
            {
                //Console.WriteLine(adressWrittingPositions[g]);
                fs.Position = adressWrittingPositions[g];
                bw.Write((uint)adressToWrite[g]);
            }
        }
    }

    public static void saveMDBKP(Mesh[] model, string saveTo, Vector3[] positions)
    {
        using (FileStream fs = new FileStream(saveTo, FileMode.Create))
        using (BinaryWriter bw = new BinaryWriter(fs))
        {
            List<Bone> armature = model[0].armature.ToList();
            List<long> offsetMdbs = new List<long>();


            #region utility voids
            void autoIdent()
            {
                while (fs.Position % 16 != 0) bw.Write((byte)0);
            }
            void writeAtOffset(long position, dynamic what)
            {
                long bkp = fs.Position;
                fs.Position = position;
                bw.Write(what);
                fs.Position = bkp;
            }
            sbyte Map(double x, double inMin, double inMax, double outMin, double outMax)
            {
                return (sbyte)Math.Round((x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin);
            }
            #endregion
            bw.Write(7496563);
            bw.Write(3);
            bw.Write(model.Length);
            bw.Write(0);
            List<long> adressWrittingPositions = new List<long>();
            foreach (var g in model)
            {
                adressWrittingPositions.Add((long)fs.Position);
                bw.Write(0);
            }
            autoIdent();
            foreach (var meshes in model)
            {
                long offsetMdb = fs.Position;
                offsetMdbs.Add(offsetMdb);

                bw.Write(6448237);//mdb
                bw.Write(48);
                //bw.Write((ushort)meshes.armature.Length);
                ushort countSkel = (ushort)(Program.MSkeleton.pos.Length);
                bw.Write(countSkel);
                bw.Write((ushort)meshes.faces.Length);

                //bw.Write((ushort)Program.MSkeleton.Length);



                bw.Write(0);
                bw.Write(0);
                bw.Write(0);
                bw.Write(0);
                bw.Write(1f);
                long writeMeshAdressLater = fs.Position;
                for (int g = 0; g < 4; g++) bw.Write(0);

                //Console.WriteLine(Program.MSkeleton.Length);
                //Console.WriteLine(bone.nameO);
                for (int g = 0; g < Program.MSkeleton.pos.Length; g++)
                {
                    //Console.WriteLine(Program.MSkeleton.index[g] + "   "  + g);

                    //Bone p = getBoneParent(armature[g]);
                    //Vector3 v3 = getBoneHiercharyPosition(armature[g]);


                    //bw.Write(Program.MSkeleton.pos[g].X + (armature[g].pos.X - p.pos.X));
                    //bw.Write(Program.MSkeleton.pos[g].Y + (armature[g].pos.Y - p.pos.Y));
                    //bw.Write(Program.MSkeleton.pos[g].Z + (armature[g].pos.Z - p.pos.Z));

                    bw.Write(positions[g].X);
                    bw.Write(positions[g].Y);
                    bw.Write(positions[g].Z);

                    Console.WriteLine((g + 1) + "           " + positions[g]);
                    //bw.Write(Program.MSkeleton.pos[g].X + (armature[g].pos.X);
                    //bw.Write(Program.MSkeleton.pos[g].Y);
                    //bw.Write(Program.MSkeleton.pos[g].Z);
                    bw.Write(Program.MSkeleton.v1[g]);
                    bw.Write(Program.MSkeleton.v2[g]);
                }
                Console.WriteLine("----------------------");

                if (3 > 4)
                {
                    foreach (var bone in armature)
                    {
                        //Console.WriteLine(bone.nameO);
                        for (int g = 0; g < Program.MSkeleton.pos.Length; g++)
                        {
                            //Console.WriteLine(Program.MSkeleton.index[g] + "   "  + g);
                            if ((g + 1).ToString() == bone.nameO)
                            {
                                bw.Write(bone.pos.X);
                                bw.Write(bone.pos.Y);
                                bw.Write(bone.pos.Z);
                                bw.Write(Program.MSkeleton.v1[g]);
                                bw.Write(Program.MSkeleton.v2[g]);
                                continue;
                            }
                        }
                    }
                }
                if (1 > 3)
                {
                    foreach (var bone in armature)
                    {
                        bw.Write(bone.pos.X);
                        bw.Write(bone.pos.Y);
                        bw.Write(bone.pos.Z);
                        bw.Write((short)-1);
                        bw.Write((short)bone.parentName);
                    }
                }
                foreach (var linkedMesh in meshes.faces)
                {
                    writeAtOffset(writeMeshAdressLater, (int)(fs.Position - offsetMdb));
                    writeMeshAdressLater += 4;


                    long offsetMesh = fs.Position;
                    bw.Write(32);
                    long offsetNormal = fs.Position;
                    bw.Write(0);
                    long offsetUV = fs.Position;
                    bw.Write(0);
                    long offsetVertColor = fs.Position;
                    bw.Write(0);
                    long offsetBoneWeight = fs.Position;
                    bw.Write(0);

                    long offsetVerticesCount = fs.Position;
                    bw.Write((ushort)0);
                    bw.Write((ushort)linkedMesh.material);
                    autoIdent();

                    ushort vCount = 0;
                    foreach (var vertices in linkedMesh.triangles)
                    {
                        //Console.WriteLine(vertices.vertices[0].indice + "  " + vertices.vertices[1].indice + "  " + vertices.vertices[2].indice);
                        for (int c = 0; c < 3; c++)
                        {
                            if (vertices.codes[c] != -150)
                            {
                                //Console.WriteLine(vertices.vertices[c].indice + "   " + vertices.vertices[c].code);
                                bw.Write(vertices.vertices[c].pos.X);
                                bw.Write(vertices.vertices[c].pos.Y);
                                bw.Write(vertices.vertices[c].pos.Z);
                                bw.Write(vertices.codes[c]);
                                vCount++;
                            }
                        }
                    }
                    writeAtOffset(offsetVerticesCount, vCount);
                    writeAtOffset(offsetNormal, (uint)(fs.Position - offsetMesh));

                    foreach (var normals in linkedMesh.triangles)
                    {
                        for (int c = 0; c < 3; c++)
                        {
                            if (normals.codes[c] != -150)
                            {
                                bw.Write(Map(normals.vertices[c].normal.X, -1f, 1f, -128, 127));
                                bw.Write(Map(normals.vertices[c].normal.Y, -1f, 1f, -128, 127));
                                bw.Write(Map(normals.vertices[c].normal.Z, -1f, 1f, -128, 127));
                                bw.Write((byte)0);
                            }
                        }
                    }
                    autoIdent();
                    writeAtOffset(offsetUV, (uint)(fs.Position - offsetMesh));

                    foreach (var uv in linkedMesh.triangles)
                    {
                        for (int c = 0; c < 3; c++)
                        {
                            if (uv.codes[c] != -150)
                            {
                                Console.WriteLine("UV:  " + uv.vertices[c].uv.X * 4100f + "    " + uv.vertices[c].uv.Y * 4100f + "       " + (short)Math.Round(uv.vertices[c].uv.X * 4100f) + "    " + (short)Math.Round(uv.vertices[c].uv.Y * 4100f) + "       " + uv.vertices[c].uv.X + "    " + uv.vertices[c].uv.Y);
                                bw.Write((short)Math.Round(uv.vertices[c].uv.X * 4100f));
                                bw.Write((short)Math.Round(uv.vertices[c].uv.Y * 4100f));
                            }
                        }
                    }
                    autoIdent();
                    writeAtOffset(offsetVertColor, (uint)(fs.Position - offsetMesh));

                    foreach (var color in linkedMesh.triangles)
                    {
                        for (int c = 0; c < 3; c++)
                        {
                            if (color.codes[c] != -150)
                            {
                                bw.Write(2155905152);
                            }
                        }
                    }
                    autoIdent();
                    writeAtOffset(offsetBoneWeight, (uint)(fs.Position - offsetMesh));

                    foreach (var bone in linkedMesh.triangles)
                    {
                        for (int c = 0; c < 3; c++)
                        {
                            if (bone.codes[c] != -150)
                            {
                                byte name1 = 0;
                                byte name2 = 0;
                                byte name3 = 0;

                                foreach (var boneName in armature)
                                {

                                    if (boneName.nameO == bone.vertices[c].bones[0])
                                    {
                                        //name1 = (byte)boneName.name;
                                        name1 = (byte)boneName.index;
                                    }
                                    if (boneName.nameO == bone.vertices[c].bones[1])
                                    {
                                        name2 = (byte)boneName.index;
                                    }
                                    if (boneName.nameO == bone.vertices[c].bones[2])
                                    {
                                        name3 = (byte)boneName.index;
                                    }

                                }
                                //name1 -= 1;
                                //name2 -= 1;
                                //name3 -= 1;

                                name1 *= 4;
                                name2 *= 4;
                                name3 *= 4;

                                //bw.Write(name1); bw.Write(name2); bw.Write(name3); bw.Write(name4);
                                int pass = 0;
                                bw.Write((byte)0);
                                if (bone.vertices[c].eachWeight[0] != 0)
                                {
                                    bw.Write(name1);
                                }
                                else
                                {
                                    pass += 1;
                                }
                                if (bone.vertices[c].eachWeight[1] != 0)
                                {
                                    bw.Write(name2);
                                }
                                else
                                {
                                    pass += 1;
                                }
                                if (bone.vertices[c].eachWeight[2] != 0)
                                {
                                    bw.Write(name3);
                                }
                                else
                                {
                                    pass += 1;
                                }
                                Console.WriteLine("BONES:  " + name1 + "    " + name2 + "    " + name3);
                                for (int gh = 0; gh < pass; gh++) bw.Write((byte)0);
                                //bw.Write((byte)0); bw.Write((byte)4); bw.Write((byte)0); bw.Write((byte)0);



                                byte v1 = (byte)Math.Round(bone.vertices[c].eachWeight[0] * 100f);
                                byte v2 = (byte)Math.Round(bone.vertices[c].eachWeight[1] * 100f);
                                byte v3 = (byte)Math.Round(bone.vertices[c].eachWeight[2] * 100f);

                                int res = v1 + v2 + v3;


                                List<byte> nbs = new List<byte>();

                                nbs.Add((byte)Math.Ceiling(v1 * 100f / res));
                                nbs.Add((byte)Math.Ceiling(v2 * 100f / res));
                                nbs.Add((byte)Math.Ceiling(v3 * 100f / res));

                                for (int i = 0; i < nbs.Count; i++)
                                {
                                    if (nbs[i] == 0)
                                    {
                                        nbs.Remove(nbs[i]);
                                        i -= 1;
                                    }
                                }


                                int finalSum = nbs.Sum(n => (byte)n);

                                //if ((v1Final + v2Final + v3Final) != 100)

                                //the sum of the weights need to always be 100, because it is the total of bones that control that vert.
                                //if the sum surpasses the limit of 100, it will result on weird deformations.


                                if (3 > 7)
                                {
                                    while (finalSum > 100)
                                    {
                                        nbs.Sort((a, b) => a.CompareTo(b));

                                        nbs[nbs.Count - 1] -= 1;
                                        finalSum = nbs[0] + nbs[1] + nbs[2];
                                        Console.WriteLine(finalSum);
                                    }
                                }
                                while (finalSum > 100)
                                {
                                    nbs.Sort((a, b) => a.CompareTo(b));

                                    nbs[0] -= 1;
                                    finalSum = nbs.Sum(n => (byte)n);
                                }
                                Console.WriteLine("SUM:   " + (v1 + v2 + v3) + "     Transformed:     " + finalSum);


                                foreach (var g in nbs)
                                {
                                    bw.Write(g);
                                }
                                int rest = 4 - nbs.Count;
                                for (int a = 0; a < rest; a++)
                                {
                                    bw.Write((byte)0);
                                }
                                //bw.Write(nbs[0]);
                                //bw.Write(nbs[1]);
                                //bw.Write(nbs[2]);

                                //bw.Write((byte)0);








                                //bw.Write(0);
                                //bw.Write(100);
                            }
                        }
                    }
                    autoIdent();
                }

            }
            List<long> adressToWrite = new List<long>();

            for (int f = 0; f < 20; f++) bw.Write(0);
            for (int meshes = 0; meshes < model.Length; meshes++)
            {
                adressToWrite.Add(fs.Position);
                bw.Write((int)(offsetMdbs[meshes] - fs.Position));


                bw.Write(model[meshes].unknownNumber);

                string name = model[meshes].name;
                if (name.Length > 8) name = name.Substring(0, 8);
                bw.Write(Encoding.ASCII.GetBytes(name));
                autoIdent();

                bw.Write(1f); bw.Write(1f); bw.Write(1f); //scales
                bw.Write(0f); bw.Write(0f); bw.Write(0f); //rotations
                bw.Write(0f); bw.Write(0f); bw.Write(0f); //position
                autoIdent();

                bw.Write(0);
                bw.Write(600f);
                bw.Write(8323072);
                bw.Write(0);
                for (int g = 0; g < 8; g++) bw.Write(0);
            }
            for (int g = 0; g < adressWrittingPositions.Count; g++)
            {
                //Console.WriteLine(adressWrittingPositions[g]);
                fs.Position = adressWrittingPositions[g];
                bw.Write((uint)adressToWrite[g]);
            }
        }
    }
}