using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.IO;
using System.Security.Policy;
using System.Numerics;
using System;
using System.Diagnostics.Eventing.Reader;
using System.Xml.Linq;
using System.Data.SqlTypes;
public class Bone
{
    public int name, parentName;
    public string nameO;
    public Vector3 pos;
    public int index;
    public Bone(string na, int n, int pn, Vector3 p)
    {
        nameO = na;
        name = n;
        parentName = pn;
        pos = p;
    }
}

public class Mesh
{
    public string name = "";
    public Bone[] armature;
    public linkedMesh[] faces = new linkedMesh[] { };
    public uint unknownNumber = 0; //meshes have a serial of numbers that i have absolutely NO CLUE of what it is
}
public class linkedMesh
{
    public int material;
    public int[] indices;
    public Triangle[] triangles;

    public void calculatePosition()
    {
        List<Triangle> t = triangles.ToList();
        t.Sort((a,b) => a.valueOrder.CompareTo(b.valueOrder));
        triangles = t.ToArray();
    }
}
public class Triangle
{
    public int faceIndice;
    public Vertex[] vertices = new Vertex[] {}; //3 verts
    public decimal valueOrder;

    public bool f = true;
    public int[] codes;

    public void calculateOrder()
    {
        List<Vertex> v = vertices.ToList();
        v.Sort((a ,b) => a.indice.CompareTo(b.indice));
        vertices = v.ToArray();
        BigInteger bigInteger = BigInteger.Parse("" + vertices[0].indice + "" + vertices[1].indice + "" + vertices[2].indice);
        //Console.WriteLine(bigInteger);
        valueOrder = (decimal)bigInteger;
        //valueOrder = (ulong)(vertices[0].indice + vertices[1].indice + vertices[2].indice);
    }
    public bool Intersects(Triangle reference)
    {
        foreach (var r in reference.vertices)
            foreach (var v in r.connectedUVs)
                foreach (var v1 in vertices)
                    if (v1.uv == v) return true;
        return false;
    }
}
public class Vertex
{
    public int indice;
    public Vector3 pos;
    public Vector3 normal;
    public Vector2 uv = new Vector2(0, 0);
    public Vector2[] connectedUVs = new Vector2[0];

    public string[] bones = new string[] { "0", "0", "0" };
    public float weight = 1;
    public float[] eachWeight = new float[3] { 0, 0, 0 };
    public int code = -150;

}
public class MdSkeleton
{
    public Vector3[] pos;
    public int[] index;
    public short[] v1, v2;
    public MdSkeleton(Vector3[] PSSK, int[] OSK, short[] V1, short[] V2)
    {
        pos = PSSK;
        index = OSK;
        v1 = V1;
        v2 = V2;
    }
}
