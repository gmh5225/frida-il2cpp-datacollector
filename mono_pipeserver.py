import socket
import select
import sys
from struct import *
import zlib
import time
from enum import IntEnum, auto
import threading
import random
import win32pipe
import win32file

WriteByte = 1
WriteWord = 2
WriteDword = 3
WriteQword = 4
WriteUtf8String = 5

PID = 0
API = 0
SESSION = 0


class CEPIPECMD(IntEnum):
    MONOCMD_INITMONO = 0
    MONOCMD_OBJECT_GETCLASS = 1
    MONOCMD_ENUMDOMAINS = 2
    MONOCMD_SETCURRENTDOMAIN = 3
    MONOCMD_ENUMASSEMBLIES = 4
    MONOCMD_GETIMAGEFROMASSEMBLY = 5
    MONOCMD_GETIMAGENAME = 6
    MONOCMD_ENUMCLASSESINIMAGE = 7
    MONOCMD_ENUMFIELDSINCLASS = 8
    MONOCMD_ENUMMETHODSINCLASS = 9
    MONOCMD_COMPILEMETHOD = 10

    MONOCMD_GETMETHODHEADER = 11
    MONOCMD_GETMETHODHEADER_CODE = 12
    MONOCMD_LOOKUPRVA = 13
    MONOCMD_GETJITINFO = 14
    MONOCMD_FINDCLASS = 15
    MONOCMD_FINDMETHOD = 16
    MONOCMD_GETMETHODNAME = 17
    MONOCMD_GETMETHODCLASS = 18
    MONOCMD_GETCLASSNAME = 19
    MONOCMD_GETCLASSNAMESPACE = 20
    MONOCMD_FREEMETHOD = 21
    MONOCMD_TERMINATE = 22
    MONOCMD_DISASSEMBLE = 23
    MONOCMD_GETMETHODSIGNATURE = 24
    MONOCMD_GETPARENTCLASS = 25
    MONOCMD_GETSTATICFIELDADDRESSFROMCLASS = 26
    MONOCMD_GETTYPECLASS = 27
    MONOCMD_GETARRAYELEMENTCLASS = 28
    MONOCMD_FINDMETHODBYDESC = 29
    MONOCMD_INVOKEMETHOD = 30
    MONOCMD_LOADASSEMBLY = 31
    MONOCMD_GETFULLTYPENAME = 32
    MONOCMD_OBJECT_NEW = 33
    MONOCMD_OBJECT_INIT = 34
    MONOCMD_GETVTABLEFROMCLASS = 35
    MONOCMD_GETMETHODPARAMETERS = 36
    MONOCMD_ISCLASSGENERIC = 37
    MONOCMD_ISIL2CPP = 38
    MONOCMD_FILLOPTIONALFUNCTIONLIST = 39
    MONOCMD_GETSTATICFIELDVALUE = 40
    MONOCMD_SETSTATICFIELDVALUE = 41
    MONOCMD_GETCLASSIMAGE = 42
    MONOCMD_FREE = 43
    MONOCMD_GETIMAGEFILENAME = 44
    MONOCMD_GETCLASSNESTINGTYPE = 45
    MONOCMD_LIMITEDCONNECTION = 46


class BinaryReader:
    def __init__(self, pipe):
        self.pipe = pipe

    def ReadInt8(self):
        hr, result = win32file.ReadFile(self.pipe, 1)
        ret = unpack("<b", result)[0]
        return ret

    def ReadInt16(self):
        hr, result = win32file.ReadFile(self.pipe, 2)
        ret = unpack("<h", result)[0]
        return ret

    def ReadInt32(self):
        hr, result = win32file.ReadFile(self.pipe, 4)
        ret = unpack("<i", result)[0]
        return ret

    def ReadInt64(self):
        hr, result = win32file.ReadFile(self.pipe, 8)
        ret = unpack("<q", result)[0]
        return ret

    def ReadUInt8(self):
        hr, result = win32file.ReadFile(self.pipe, 1)
        ret = unpack("<B", result)[0]
        return ret

    def ReadUInt16(self):
        hr, result = win32file.ReadFile(self.pipe, 2)
        ret = unpack("<H", result)[0]
        return ret

    def ReadUInt32(self):
        hr, result = win32file.ReadFile(self.pipe, 4)
        ret = unpack("<I", result)[0]
        return ret

    def ReadUInt64(self):
        hr, result = win32file.ReadFile(self.pipe, 8)
        ret = unpack("<Q", result)[0]
        return ret


class BinaryWriter:
    def __init__(self, pipe):
        self.pipe = pipe

    def WriteInt8(self, number):
        i8 = pack("<b", number)
        win32file.WriteFile(self.pipe, i8)

    def WriteInt16(self, number):
        i16 = pack("<h", number)
        win32file.WriteFile(self.pipe, i16)

    def WriteInt32(self, number):
        i32 = pack("<i", number)
        win32file.WriteFile(self.pipe, i32)

    def WriteInt64(self, number):
        i64 = pack("<q", number)
        win32file.WriteFile(self.pipe, i64)

    def WriteUInt8(self, number):
        ui8 = pack("<B", number)
        win32file.WriteFile(self.pipe, ui8)

    def WriteUInt16(self, number):
        ui16 = pack("<H", number)
        win32file.WriteFile(self.pipe, ui16)

    def WriteUInt32(self, number):
        ui32 = pack("<I", number)
        win32file.WriteFile(self.pipe, ui32)

    def WriteUInt64(self, number):
        ui64 = pack("<Q", number)
        win32file.WriteFile(self.pipe, ui64)

    def WriteUtf8String(self, message):
        win32file.WriteFile(self.pipe, message.encode())


def handler(pipe, command):
    global process_id
    reader = BinaryReader(pipe)
    writer = BinaryWriter(pipe)
    # print(str(CEPIPECMD(command)))
    if command == CEPIPECMD.MONOCMD_INITMONO:
        API.InitMono()
    elif command == CEPIPECMD.MONOCMD_ISIL2CPP:
        API.IsIL2CPP()
    elif command == CEPIPECMD.MONOCMD_ENUMASSEMBLIES:
        API.EnumAssemblies()
    elif command == CEPIPECMD.MONOCMD_GETIMAGEFROMASSEMBLY:
        assembly = reader.ReadUInt64()
        API.GetImageFromAssembly(assembly)
    elif command == CEPIPECMD.MONOCMD_GETIMAGENAME:
        image = reader.ReadUInt64()
        API.GetImageName(image)
    elif command == CEPIPECMD.MONOCMD_ENUMCLASSESINIMAGE:
        image = reader.ReadUInt64()
        if image == 0:
            writer.WriteUInt32(0)
        API.EnumClassesInImage(image)
    elif command == CEPIPECMD.MONOCMD_ENUMDOMAINS:
        writer.WriteUInt32(1)
        domain = API.EnumDomains()
        writer.WriteUInt64(domain)
    elif command == CEPIPECMD.MONOCMD_ENUMMETHODSINCLASS:
        _class = reader.ReadUInt64()
        API.EnumMethodsInClass(_class)
    elif command == CEPIPECMD.MONOCMD_GETCLASSNESTINGTYPE:
        klass = reader.ReadUInt64()
        writer.WriteUInt64(0)
    elif command == CEPIPECMD.MONOCMD_GETFULLTYPENAME:
        klass = reader.ReadUInt64()
        isKlass = reader.ReadUInt8()
        nameformat = reader.ReadUInt32()
        API.GetFullTypeName(klass, isKlass, nameformat)
    elif command == CEPIPECMD.MONOCMD_GETPARENTCLASS:
        klass = reader.ReadUInt64()
        API.GetParentClass(klass)
    elif command == CEPIPECMD.MONOCMD_GETCLASSNAME:
        klass = reader.ReadUInt64()
        API.GetClassName(klass)
    elif command == CEPIPECMD.MONOCMD_GETCLASSNAMESPACE:
        klass = reader.ReadUInt64()
        API.GetClassNameSpace(klass)
    elif command == CEPIPECMD.MONOCMD_GETCLASSIMAGE:
        klass = reader.ReadUInt64()
        API.GetClassImage(klass)
    elif command == CEPIPECMD.MONOCMD_ISCLASSGENERIC:
        klass = reader.ReadUInt64()
        API.IsClassGeneric(klass)
    elif command == CEPIPECMD.MONOCMD_GETSTATICFIELDADDRESSFROMCLASS:
        domain = reader.ReadUInt64()
        klass = reader.ReadUInt64()
        writer.WriteUInt64(0)
    elif command == CEPIPECMD.MONOCMD_ENUMFIELDSINCLASS:
        klass = reader.ReadUInt64()
        API.EnumFieldsInClass(klass)
    elif command == CEPIPECMD.MONOCMD_GETMETHODSIGNATURE:
        method = reader.ReadUInt64()
        API.GetMethodSignature(method)
    elif command == CEPIPECMD.MONOCMD_GETSTATICFIELDVALUE:
        vtable = reader.ReadUInt64()
        field = reader.ReadUInt64()
        API.GetStaticFieldValue(vtable, field)
    elif command == CEPIPECMD.MONOCMD_SETSTATICFIELDVALUE:
        vtable = reader.ReadUInt64()
        field = reader.ReadUInt64()
        val = reader.ReadUInt64()
        API.SetStaticFieldValue(vtable, field, val)
    elif command == CEPIPECMD.MONOCMD_COMPILEMETHOD:
        method = reader.ReadUInt64()
        methodPtr = API.CompileMethod(method)
        writer.WriteUInt64(methodPtr)

    else:
        pass
    return 1


def main_thread(pipe):
    while True:
        try:
            command = READER.ReadUInt8()
            ret = handler(pipe, command)
        except:
            import traceback

            print("EXCEPTION:" + str(CEPIPECMD(command)))
            traceback.print_exc()
            break
        if ret == -1:
            break


def on_message(message, data):
    if message["type"] == "send":
        _type = message["payload"][0]
        value = message["payload"][1]
        if _type == WriteByte:
            WRITER.WriteUInt8(value)
        elif _type == WriteWord:
            WRITER.WriteUInt16(value)
        elif _type == WriteDword:
            WRITER.WriteUInt32(value)
        elif _type == WriteQword:
            WRITER.WriteUInt64(value)
        elif _type == WriteUtf8String:
            WRITER.WriteUtf8String(value)
    else:
        print(message)
        # time.sleep(1)


def pipeserver(session):
    global PID
    global API
    global READER
    global WRITER

    with open("javascript/mono_core.js") as f:
        jscode = f.read()
    script = session.create_script(jscode)
    script.on("message", on_message)
    script.load()
    api = script.exports

    info = api.GetInfo()
    pid = info["pid"]
    PID = pid
    API = api

    pipe = win32pipe.CreateNamedPipe(
        "\\\\.\\pipe\\cemonodc_pid" + str(pid),
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE | win32pipe.PIPE_WAIT,
        1,
        256,
        256,
        0,
        None,
    )
    # print("ConnectNamedPipe start!")
    win32pipe.ConnectNamedPipe(pipe, None)
    print("Connect!")
    READER = BinaryReader(pipe)
    WRITER = BinaryWriter(pipe)
    main_thread(pipe)
    win32pipe.DisconnectNamedPipe(pipe)
