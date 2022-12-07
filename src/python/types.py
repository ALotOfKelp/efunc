#    efunc.py -- External function calling for python
#    Copyright © 2022 Iskander Boutel
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY# without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from . import _efunc
import sys, struct

def cvalue (value):
    if hasattr(value, "cvalue"):
        return value
    
    if type(value) in [str, bytes]:
        return String(value)
    elif type(value) == int:
        return Int64(value)
    elif type(value) == float:
        return Double(value)
    
    raise TypeError("Invalid type for C type assumption")

class EFuncError (Exception):
    def __init__ (self):
        Exception.__init__(self, _efunc.getLibraryError())

class cvalue:
    cvalue = True

class Char (cvalue):
    size = 1
    
    def __init__ (self, value):
        if type(value) != str or len(value) > 1:
            raise TypeError("Char must be a string of length 1")
        
        self.value = ord(value)
    
    def __str__ (self):
        return chr(self.value)
    
    def __repr__ (self):
        return str(self)
    
    def __int__ (self):
        return self.value
    
    def __float__ (self):
        return float(int(self))
    
    def fromRaw (value):
        return Char(chr(int.from_bytes(value, sys.byteorder, signed = False)))
    
    def toRaw (self):
        return self.value.to_bytes(1, sys.byteorder, signed = False)
    
    def getValue (self):
        return chr(self.value)
    
    def setValue (self, value):
        self.__init__(value)

class _Int (cvalue):
    def __init__ (self, value):
        if type(value) != int:
            raise TypeError("Int value must be an int")

        self.value = value
    
    def __str__ (self):
        return str(self.value)
    
    def __repr__ (self):
        return str(self)
    
    def __int__ (self):
        return self.value
    
    def __float__ (self):
        return float(int(self))
    
    def _fromRaw (value):
        return (int.from_bytes(value, sys.byteorder, signed = True))
    
    def toRaw (self):
        return self.value.to_bytes(self.size, sys.byteorder, signed = self.signed)
    
    def getValue (self):
        return self.value
    
    def setValue (self, value):
        self.__init__(value)

class Int8 (_Int):
    size = 1
    signed = True

    def fromRaw (value):
        return Int8(Int8._fromRaw(value))

class Int16 (_Int):
    size = 2
    signed = True

    def fromRaw (value):
        return Int16(Int16._fromRaw(value))

class Int32 (_Int):
    size = 4
    signed = True

    def fromRaw (value):
        return Int32(Int32._fromRaw(value))

class Int64 (_Int):
    size = 8
    signed = True

    def fromRaw (value):
        return Int64(Int64._fromRaw(value))

class UInt8 (_Int):
    size = 1
    signed = False

    def fromRaw (value):
        return UInt8(UInt8._fromRaw(value))

class UInt16 (_Int):
    size = 2
    signed = False

    def fromRaw (value):
        return UInt16(UInt16._fromRaw(value))

class UInt32 (_Int):
    size = 4
    signed = False

    def fromRaw (value):
        return UInt32(UInt32._fromRaw(value))

class UInt64 (_Int):
    size = 8
    signed = False

    def fromRaw (value):
        return UInt64(UInt64._fromRaw(value))

class _Float (cvalue):
    _float = True

    def __init__ (self, value):
        if type(value) != float:
            raise TypeError("Float value must be float")
        
        self.value = struct.unpack("Q", struct.pack(self._fcode, value))[0]
    
    def __str__ (self):
        return str(float(self))
    
    def __repr__ (self):
        return str(self)
    
    def __int__ (self):
        return int(float(self))
    
    def __float__ (self):
        return self.getValue()
    
    def _fromRaw (value, _icode):
        return struct.unpack(_icode, value)[0]
    
    def toRaw (self):
        return struct.pack(self._icode, self.value)
    
    def getValue (self):
        return struct.unpack(self._fcode, struct.pack("Q", self.value))[0]
    
    def setValue (self, value):
        self.__init__(value)

class Float (_Float):
    size = 4
    _icode = "I"
    _fcode = "f"

    def fromRaw (value):
        return Float(Float._fromRaw(value, Float._icode))
    
class Double (_Float):
    size = 8
    _icode = "Q"
    _fcode = "d"

    def fromRaw (value):
        return Double(Double._fromRaw(value, Double._icode))

class PointerType:
    def __init__ (self, layers, final_type):
        self.layers = layers
        self.final_type = final_type
    
    def __call__ (self, addr):
        return Pointer(addr, self.layers, self.final_type)
    
    def fromRaw (self, value):
        return Pointer(int.from_bytes(value, sys.byteorder, signed = False), self.layers, self.final_type)

class Pointer (cvalue):
    size = 8

    def __init__ (self, addr, layers, final_type):
        self.value = addr
        self.layers = layers
        self.final_type = final_type
    
    def __str__ (self):
        return str(self.value)
    
    def __repr__ (self):
        return str(self)
    
    def __int__ (self):
        return self.value
    
    def __float__ (self):
        return float(self.value)
    
    def allocate (size):
        return Pointer(_efunc.allocateMemory(size), 1, None)
    
    def fromFinal (value):
        pointer = Pointer(_efunc.allocateMemory(cvalue(value.size)), 1, type(value))
        pointer.write(value)

        return pointer
    
    def fromPointer (value):
        pointer = Pointer(_efunc.allocateMemory(8), value.layers + 1, value.final_type)
        pointer.write(value)

        return pointer
    
    def toRaw (self):
        return int.to_bytes(self.value, 8, sys.byteorder, signed = False)
    
    def follow (self, offset = 0):
        raw_value = _efunc.readMemory(self.value + offset, self.final_type.size)

        if self.layers == 1:
            if self.final_type == None:
                raise ValueError("Cannot follow void pointer")

            return self.final_type.fromRaw(raw_value)
        
        return Pointer.fromRaw(raw_value)
    
    def write (self, value, offset = 0):
        return _efunc.writeMemory(self.value + offset, cvalue(value).toRaw(), value.size)
    
    def rawWrite (self, value, size, offset = 0):
        return _efunc.writeMemory(self.value + offset, value, size)
    
    def rawRead (self, size, offset = 0):
        return _efunc.readMemory(self.value + offset, size)
    
    def free (self):
        return _efunc.freeMemory(self.value)
    
    def getValue (self):
        return self.value
    
    def setValue (self, value):
        if type(value) != int:
            raise TypeError("Pointer address must be integer")

        self.value = value
    
    def cast (self, new_type):
        self.layers = new_type.layers
        self.final_type = new_type.final_type
    
    def getType (self):
        return PointerType(self.layers, self.final_type)

class String (Pointer):
    size = 8

    def __init__ (self, value, c_string = True):
        if type(value) == str:
            value = value.encode()

        self.len = len(value)

        if c_string:
            value += b'\0'
            self.len += 1

        Pointer.__init__(self, _efunc.allocateMemory(len(value) + int(c_string)), 1, Char)
        self.rawWrite(value, len(value))
    
    def __str__ (self):
        return self.read().decode()
    
    def __repr__ (self):
        return str(self)
    
    def read (self):
        return self.rawRead(self.len)
    
    def fromChar (value, c_string = True):
        return String(str(value), c_string)
    
    def fromPointer (value, len):
        string = String("", False)
        string.len = len
        string.value = cvalue(value).value

        return string
    
    def getValue (self):
        return self.read()
    
    def setValue (self, value):
        self.__init__(value, self.c_string)

class Member:
    def __init__ (self, name, type, size = None):
        self.name = name
        self.type = type
        self.size = size if size else type.size

class StructInstance (Pointer):
    size = 8

    def __init__ (self, type, **values):
        self.type = type
        Pointer.__init__(self, _efunc.allocateMemory(type.calculateSize()), 1, None)

        for i in values:
            if hasattr(values[i], "cvalue"):
                self.write(values[i], type.calculateOffset(i))
            else:
                self.write(self.type.getMemberType(i)(values[i]), type.calculateOffset(i))
    
    def getMember (self, name):
        for i in self.type.members:
            if i.name == name:
                return i.type.fromRaw(self.rawRead(i.size, self.type.calculateOffset(name)))
    
        raise AttributeError("No such member")
    
    def setMember (self, name, value):
        for i in self.type.members:
            if i.name == name:
                self.write(cvalue(value), self.type.calculateOffset(name))
                return
        
        raise AttributeError("No such member")

class StructType:
    def __init__ (self, members):
        self.members = members
    
    def generateInstance (self, **values):
        return StructInstance(self, **values)

    def calculateSize (self):
        size = 0

        for i in self.members:
            size += i.size
        
        return size
    
    def calculateOffset (self, name):
        offset = 0

        for i in self.members:
            if i.name == name:
                break
            
            offset += i.size
        
        if offset == self.calculateSize():
            raise AttributeError("No such member")
        
        return offset
    
    def getMemberType (self, name):
        for i in self.members:
            if i.name == name:
                return i.type
        
        raise AttributeError("No such member")
        
class FunctionDescriptor:
    def __init__ (self, min_params, ret_type = Int64, varargs = False):
        self.min_params = min_params
        self.ret_type = ret_type
        self.varargs = varargs

class Function (cvalue):
    def __init__ (self, addr, desc):
        self.value = addr
        self.descriptor = desc
    
    def __str__ (self):
        return str(self.value)
    
    def __repr__ (self):
        return str(self)
    
    def __int__ (self):
        return self.value
    
    def __float__ (self):
        return float(int(self))
    
    def __call__ (self, *args):
        _efunc.setFuncCallSpecs(self.value, len(args), (len(args) - self.descriptor.min_params) if self.descriptor.varargs else 0, self.descriptor.min_params, int(hasattr(self.descriptor.ret_type, "_float")))
        
        for value in args:
            _efunc.addFuncCallParam(cvalue(value))
        
        ret = _efunc.callFunc()
        _efunc.cleanCallSpecs()
        
        if hasattr(self.descriptor.ret_type, "_float"):
            temp = self.descriptor.ret_type(1.0)
            temp.value = ret
            return temp
        
        return self.descriptor.ret_type(ret)
    
    def getValue (self):
        return self.value
    
    def setValue (self, value):
        self.value = value

class Library:
    def __init__ (self, path):
        self.path = path
        self.handle = _efunc.loadLibrary(path)

        if not self.handle:
            raise EFuncError()
    
    def getFunction (self, name, descriptor):
        func = Function(_efunc.loadSymbol(self.handle, name), descriptor)

        if not func.value:
            raise EFuncError()
        
        return func

    def getVariable (self, name, value_type):
        addr = _efunc.loadSymbol(self.handle, name)
        value = value_type.fromRaw(_efunc.readMemory(addr, value_type.size))
        
        if not value.value:
            raise EFuncError()

    def close (self):
        _efunc.closeLibrary(self.handle)