using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

public static class baseModel
{
    public static void extract(int offset, FileStream stream, BinaryReader reader, string modelName)
    {

        Console.ForegroundColor = ConsoleColor.Red;
        Console.BackgroundColor = ConsoleColor.Black;

        int localVertexStartOffset = 0;
        int localNormalsStartOffset = 0;
        int localUVStartOffset = 0;
        int localFaceColorStartOffset = 0;
        int localBoneWeightStartOffset = 0;
        int facesCount = 0;
        int texIndex = 0;


        modelHeader currentModel = new modelHeader();
        currentModel.meshName = modelName;

        for (int i = 0; i < 26;i+=2)
        {
            stream.Seek(offset + i, SeekOrigin.Begin);
            switch(i)
            {
                case 0:
                    localVertexStartOffset = reader.ReadInt32();
                    break;
                case 4:
                    localNormalsStartOffset = reader.ReadInt32();
                    break;
                case 8:
                    localUVStartOffset = reader.ReadInt32();
                    break;
                case 12:
                    localFaceColorStartOffset = reader.ReadInt32();
                    break;
                case 16:
                    localBoneWeightStartOffset = reader.ReadInt32();
                    break;
                case 20:
                    facesCount = reader.ReadInt16();
                    break;
                case 22:
                    texIndex = reader.ReadInt16();
                    break;
            }
        }


        int absoluteVertexStartOffset = offset + localVertexStartOffset; currentModel.vertexOffset = absoluteVertexStartOffset;
        int absoluteNormalsStartOffset = offset + localNormalsStartOffset; currentModel.normalsOffset = absoluteNormalsStartOffset;
        int absoluteUVStartOffset = offset + localUVStartOffset; currentModel.UVOffset = absoluteUVStartOffset;
        int absoluteFaceColorStartOffset = offset + localFaceColorStartOffset; currentModel.FaceColorOffset = absoluteFaceColorStartOffset;
        int absoluteBoneWeightStartOffset = offset + localBoneWeightStartOffset; currentModel.boneWeightOffset = absoluteBoneWeightStartOffset;
        currentModel.faceCount = facesCount;
        currentModel.usedTextureIndexOnDat = texIndex;


        Console.WriteLine("vertex");
        //Console.WriteLine(localVertexStartOffset);
        Console.WriteLine(absoluteVertexStartOffset);
        Console.WriteLine("normals");
        //Console.WriteLine(localNormalsStartOffset);
        Console.WriteLine(absoluteNormalsStartOffset);
        Console.WriteLine("uvs");
        //Console.WriteLine(localUVStartOffset);
        Console.WriteLine(absoluteUVStartOffset);
        Console.WriteLine("rbga");
        //Console.WriteLine(localFaceColorStartOffset);
        Console.WriteLine(absoluteFaceColorStartOffset);
        Console.WriteLine("bone weight");
        //Console.WriteLine(localBoneWeightStartOffset);
        Console.WriteLine(absoluteBoneWeightStartOffset);


        mountModel.addOnList(currentModel);
    }
}
