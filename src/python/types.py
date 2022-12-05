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
import sys

class EFuncError (Exception):
    def __init__ (self):
        Exception.__init__(self, _efunc.getLibraryError())

class _CValue:
    __CValue = True

class Char (_CValue):
    size = 1
    
    def __init__ (self, value):
        if type(value) != str or len(value) > 1:
            raise TypeError("Char must be a string of length 1")
        
        self.value = ord(value)
    
    def fromRaw (value):
        return Char(chr(int.from_bytes(value, sys.byteorder, signed = False)))
    
    def toRaw (self):
        return self.value.to_bytes(1, sys.byteorder, signed = False)
    
    def __str__ (self):
        return chr(self.value)

class _Int (_CValue):
    def __init__ (self, value):
        if type(value) != int:
            raise TypeError("Int64 must be an int")

        self.value = value
    
    def _fromRaw (value):
        return (int.from_bytes(value, sys.byteorder, signed = True))
    
    def toRaw (self):
        return self.value.to_bytes(self.size, sys.byteorder, signed = self.signed)

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

class Pointer (_CValue):
    size = 8

    def __init__ (self, addr, layers, final_type):
        self.value = addr
        self.layers = layers
        self.final_type = final_type
    
    def allocate (size):
        return Pointer(_efunc.allocateMemory(size), 1, None)
    
    def fromFinal (value):
        pointer = Pointer(_efunc.allocateMemory(value.size), 1, type(value))
        pointer.write(value)

        return pointer
    
    def fromPointer (value):
        pointer = Pointer(_efunc.allocateMemory(8), value.layers + 1, value.final_type)
        pointer.write(value)

        return pointer
    
    def fromRaw (value):
        return Pointer(int.from_bytes(value, sys.byteorder, signed = False))
    
    def toRaw (self):
        return int.to_bytes(self.value, 8, sys.byteorder, signed = False)
    
    def follow (self, offset = 0):
        raw_value = _efunc.readMemory(self.value + offset, self.final_type.size)

        if self.layers == 1:
            if self.final_type == None:
                raise ValueError("Cannot follow void pointer")

            return self.final_type.fromRaw(raw_value)
        
        return Pointer.fromRaw(raw_value)
    
    def write (self, value):
        return _efunc.writeMemory(self.value, value.toRaw(), value.size)
    
    def rawWrite (self, value, size):
        return _efunc.writeMemory(self.value, value, size)
    
    def rawRead (self, size):
        return _efunc.readMemory(self.value, size)
    
    def free (self):
        return _efunc.freeMemory(self.value)

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
    
    def read (self):
        return self.rawRead(self.len)
    
    def fromChar (value, c_string = True):
        return String(str(value), c_string)
    
    def fromPointer (value, len):
        string = String("", False)
        string.len = len
        string.value = value.value

        return string
    
class FunctionDescriptor:
    def __init__ (self, min_params, ret_type = Int64, varargs = False):
        self.min_params = min_params
        self.ret_type = ret_type
        self.varargs = varargs

class Function (_CValue):
    def __init__ (self, addr, desc):
        self.value = addr
        self.descriptor = desc
    
    def __call__ (self, *args):
        _efunc.setFuncCallSpecs(self.value, len(args), (len(args) - self.descriptor.min_params) if self.descriptor.varargs else 0, self.descriptor.min_params)
        
        for value in args:
            if hasattr(value, "__CValue"):
                _efunc.addFuncCallParam(value.value)
            else:
                if type(value) in [str, bytes]:
                    _efunc.addFuncCallParam(String(value).value)
                elif type(value) == int:
                    _efunc.addFuncCallParam(Int32(value).value)
                else:
                    raise TypeError("Invalid type for C type assumption")
        
        ret = _efunc.callFunc()
        _efunc.cleanCallSpecs()

        if self.descriptor.ret_type == Pointer:
            self.descriptor.ret_type.value = ret
            return self.descriptor.ret_type
        
        return self.descriptor.ret_type(ret)

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

        if type(value_type) == Pointer:
            value = Pointer(addr, value_type.layers + 1, value_type.final_type)
        else:
            value = value_type.fromRaw(_efunc.readMemory(addr, value_type.size))
        
        if not value.value:
            raise EFuncError()

    def close (self):
        _efunc.closeLibrary(self.handle)