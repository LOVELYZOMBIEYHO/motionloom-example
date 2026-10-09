"""Bake the authored distant S97 forest into shared static material batches.

Source texture bytes, UVs and alpha-mask materials remain unchanged. Detailed
roadside trees remain separate Models in the DSL. This removes thousands of
small draw submissions without changing the engine or requiring runtime LOD.
"""

from pathlib import Path
from collections import defaultdict
import copy
import hashlib
import json
import math
import struct

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets/reference-forest"
SOURCE = ROOT / "authoring/s96-tree-layout.json"
OUTPUT = ASSETS / "s97-forest-batched.glb"
WIDTHS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
FORMATS = {5121: "B", 5123: "H", 5125: "I", 5126: "f"}


def read(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data)
    assert magic == b"glTF" and version == 2 and length == len(data)
    size, kind = struct.unpack_from("<II", data, 12)
    assert kind == 0x4E4F534A
    document = json.loads(data[20:20+size])
    binary_size, kind = struct.unpack_from("<II", data, 20+size)
    assert kind == 0x004E4942
    return document, data[28+size:28+size+binary_size], data


def accessor(document, binary, identity):
    item = document["accessors"][identity]
    view = document["bufferViews"][item["bufferView"]]
    fmt = "<" + FORMATS[item["componentType"]] * WIDTHS[item["type"]]
    width = struct.calcsize(fmt)
    start = view.get("byteOffset",0) + item.get("byteOffset",0)
    stride = view.get("byteStride",width)
    return [struct.unpack_from(fmt,binary,start+index*stride) for index in range(item["count"])]


class Builder:
    def __init__(self):
        self.payload = bytearray()
        self.document = {"asset":{"version":"2.0","generator":"S97 static forest material batches"},
                         "scene":0,"scenes":[{"nodes":[0]}],"nodes":[{"mesh":0}],
                         "meshes":[{"name":"s97_authored_distant_forest","primitives":[]}],
                         "bufferViews":[],"accessors":[],"images":[],"textures":[],
                         "samplers":[],"materials":[]}
        self.images = {}
        self.samplers = {}
        self.textures = {}
        self.materials = {}
        self.groups = defaultdict(lambda: {"positions":[],"normals":[],"uvs":[],"indices":[]})

    def view(self,data,target=None):
        self.payload.extend(b"\0" * (-len(self.payload)%4))
        node = {"buffer":0,"byteOffset":len(self.payload),"byteLength":len(data)}
        if target is not None:
            node["target"] = target
        identity = len(self.document["bufferViews"])
        self.document["bufferViews"].append(node)
        self.payload.extend(data)
        return identity

    def texture(self,source,binary,identity):
        texture = source["textures"][identity]
        image = source["images"][texture["source"]]
        view = source["bufferViews"][image["bufferView"]]
        start = view.get("byteOffset",0)
        content = binary[start:start+view["byteLength"]]
        fingerprint = hashlib.sha256(content).hexdigest()
        if fingerprint not in self.images:
            self.images[fingerprint] = len(self.document["images"])
            self.document["images"].append({"name":image.get("name",fingerprint[:12]),
                "bufferView":self.view(content),"mimeType":image["mimeType"]})
        sampler = source.get("samplers",[])[texture["sampler"]] if "sampler" in texture else {}
        key = json.dumps(sampler,sort_keys=True)
        if key not in self.samplers:
            self.samplers[key] = len(self.document["samplers"])
            self.document["samplers"].append(copy.deepcopy(sampler))
        pair = (self.images[fingerprint],self.samplers[key])
        if pair not in self.textures:
            self.textures[pair] = len(self.document["textures"])
            self.document["textures"].append({"source":pair[0],"sampler":pair[1]})
        return self.textures[pair]

    def material(self,source,binary,identity):
        material = copy.deepcopy(source["materials"][identity])
        def visit(node):
            if isinstance(node,dict):
                for key,value in node.items():
                    if key.endswith("Texture") and isinstance(value,dict) and "index" in value:
                        value["index"] = self.texture(source,binary,value["index"])
                    else:
                        visit(value)
            elif isinstance(node,list):
                for value in node:
                    visit(value)
        visit(material)
        key = json.dumps(material,sort_keys=True)
        if key not in self.materials:
            self.materials[key] = len(self.document["materials"])
            self.document["materials"].append(material)
        return self.materials[key]

    def append(self,source,binary,primitive,pose):
        material = self.material(source,binary,primitive["material"])
        group = self.groups[material]
        offset = len(group["positions"])
        attrs = primitive["attributes"]
        position = accessor(source,binary,attrs["POSITION"])
        normal = accessor(source,binary,attrs["NORMAL"])
        uv = accessor(source,binary,attrs["TEXCOORD_0"])
        indices = accessor(source,binary,primitive["indices"])
        yaw = math.radians(pose["rotationY"])
        c,s = math.cos(yaw),math.sin(yaw)
        scale = pose["scale"]
        tx,ty,tz = pose["position"]
        for x,y,z in position:
            group["positions"].append((tx+scale*(c*x+s*z),ty+scale*y,tz+scale*(-s*x+c*z)))
        for x,y,z in normal:
            group["normals"].append((c*x+s*z,y,-s*x+c*z))
        group["uvs"].extend(uv)
        group["indices"].extend((row[0]+offset,) for row in indices)

    def values(self,values,dimension,integer=False,bounds=False):
        fmt = "<" + ("I" if integer else "f") * dimension
        payload = bytearray()
        for row in values:
            payload.extend(struct.pack(fmt,*row))
        item = {"bufferView":self.view(payload,34963 if integer else 34962),
                "componentType":5125 if integer else 5126,"count":len(values),
                "type":"SCALAR" if dimension == 1 else f"VEC{dimension}"}
        if bounds:
            item["min"] = [min(row[i] for row in values) for i in range(dimension)]
            item["max"] = [max(row[i] for row in values) for i in range(dimension)]
        identity = len(self.document["accessors"])
        self.document["accessors"].append(item)
        return identity

    def write(self):
        triangles = vertices = 0
        for material,group in self.groups.items():
            triangles += len(group["indices"])//3
            vertices += len(group["positions"])
            self.document["meshes"][0]["primitives"].append({
                "attributes":{"POSITION":self.values(group["positions"],3,bounds=True),
                              "NORMAL":self.values(group["normals"],3),
                              "TEXCOORD_0":self.values(group["uvs"],2)},
                "indices":self.values(group["indices"],1,integer=True),"material":material,"mode":4})
        self.payload.extend(b"\0"*(-len(self.payload)%4))
        self.document["buffers"] = [{"byteLength":len(self.payload)}]
        document = json.dumps(self.document,separators=(",",":")).encode()
        document += b" "*(-len(document)%4)
        data = struct.pack("<4sII",b"glTF",2,28+len(document)+len(self.payload))
        data += struct.pack("<II",len(document),0x4E4F534A)+document
        data += struct.pack("<II",len(self.payload),0x004E4942)+self.payload
        OUTPUT.write_bytes(data)
        return {"file":str(OUTPUT.relative_to(ROOT)),"bytes":len(data),
                "sha256":hashlib.sha256(data).hexdigest(),"triangles":triangles,
                "vertices":vertices,"materialPrimitives":len(self.groups),
                "embeddedImages":len(self.images)}


def build():
    poses = json.loads(SOURCE.read_text())
    builder = Builder()
    cache = {}
    source_counts = defaultdict(int)
    for pose in poses:
        if pose["asset"] == "s97_near_tree":
            continue
        asset = pose["sourceFile"]
        if asset not in cache:
            cache[asset] = read(ROOT / asset)
        document,binary,_ = cache[asset]
        for primitive in document["meshes"][0]["primitives"]:
            builder.append(document,binary,primitive,pose)
        source_counts[asset] += 1
    result = builder.write()
    result["layoutSha256"] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    result["treeCount"] = sum(source_counts.values())
    result["sources"] = dict(source_counts)
    result["imageBytesPreserved"] = True
    result["notes"] = "Static world transforms and original alpha masks; no camera-facing billboard rotation or automatic runtime LOD."
    (ROOT / "authoring/s96-tree-batch-report.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    build()
