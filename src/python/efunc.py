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
        
        self.value = value
    
    def from_raw (value):
        return Char(chr(value))
    
    def to_raw (value):
        return ord(value).to_bytes(1, sys.byteorder, signed = False)

class _Int (_CValue):
    def __init__ (self, value):
        if type(value) != int:
            raise TypeError("Int64 must be an int")

        self.value = value
    
    def _from_raw (value):
        return (int.from_bytes(value, sys.byteorder, signed = True))
    
    def to_raw (self):
        return self.value.to_bytes(self.size, sys.byteorder, signed = self.signed)

class Int8 (_Int):
    size = 1
    signed = True

    def from_raw (value):
        return Int8(Int8._from_raw(value))

class Int16 (_Int):
    size = 2
    signed = True

    def from_raw (value):
        return Int16(Int16._from_raw(value))

class Int32 (_Int):
    size = 4
    signed = True

    def from_raw (value):
        return Int32(Int32._from_raw(value))

class Int64 (_Int):
    size = 8
    signed = True

    def from_raw (value):
        return Int64(Int64._from_raw(value))

class UInt8 (_Int):
    size = 1
    signed = False

    def from_raw (value):
        return UInt8(UInt8._from_raw(value))

class UInt16 (_Int):
    size = 2
    signed = False

    def from_raw (value):
        return UInt16(Int16._from_raw(value))

class UInt32 (_Int):
    size = 4
    signed = False

    def from_raw (value):
        return UInt32(UInt32._from_raw(value))

class UInt64 (_Int):
    size = 8
    signed = False

    def from_raw (value):
        return UInt64(UInt64._from_raw(value))

class Pointer (_CValue):
    size = 8

    def __init__ (self, addr, layers, final_type):
        self.value = addr
        self.layers = layers
        self.final_type = final_type
    
    def allocate (size):
        return Pointer(_efunc.allocateMemory(size), 1, None)
    
    def from_final (value):
        pointer = Pointer(_efunc.allocateMemory(value.size), 1, type(value))
        pointer.write(value.value)

        return pointer
    
    def from_pointer (value):
        pointer = Pointer(_efunc.allocateMemory(8), value.layers + 1, value.final_type)
        pointer.write(value.value)

        return pointer
    
    def from_raw (value):
        return Pointer(int.from_bytes(value, sys.byteorder, signed = False))
    
    def to_raw (self):
        return int.to_bytes(self.value, 8, sys.byteorder, signed = False)
    
    def follow (self, offset = 0):
        raw_value = _efunc.readMemory(self, self.value + offset, self.final_type.size)

        if len(self.references) == 1:
            if self.final_type == None:
                raise ValueError("Cannot follow void pointer")

            return self.final_type.from_raw(raw_value)
        
        return Pointer.from_raw(raw_value)
    
    def write (self, value):
        return _efunc.writeMemory(self.value, value.to_raw(), value.size)
    
    def rawWrite (self, value, size):
        return _efunc.writeMemory(self.value, value, size)
    
    def rawRead (self, size):
        return _efunc.readMemory(self.value, size)
    
    def free (self):
        return _efunc.freeMemory(self.value)

class String (Pointer):
    size = 8

    def __init__ (self, value, c_string = True):
        self.len = len(value)

        if c_string:
            value += b'\0'
            self.len += 1

        Pointer.__init__(self, _efunc.allocateMemory(len(value) + int(c_string)), 1, Char)
        self.rawWrite(value, len(value))
    
    def read (self):
        return self.rawRead(self.len)

class Function (_CValue):
    def __init__ (self, addr, ret_type, stack_start):
        self.value = addr
        self.stack_start = stack_start
        self.ret_type = ret_type
    
    def __call__ (self, *args):
        _efunc.setFuncCallSpecs(self.value, len(args), (len(args) - self.stack_start) if self.stack_start > -1 else 0, self.stack_start)
        
        for value in args:
            if hasattr(value, "__CValue"):
                _efunc.addFuncCallParam(value.value)
            else:
                if type(value) == bytes:
                    _efunc.addFuncCallParam(String(value).value)
                elif type(value) == int:
                    _efunc.addFuncCallParam(Int32(value).value)
                else:
                    raise TypeError("Invalid type for C type assumption")
        
        ret = _efunc.callFunc()
        _efunc.cleanCallSpecs()

        if self.ret_type == Pointer:
            self.ret_type.value = ret
            return self.ret_type
        
        return self.ret_type(ret)

class Library:
    def __init__ (self, path):
        self.path = path
        self.handle = _efunc.loadLibrary(path)

        if not self.handle:
            raise EFuncError()
    
    def getFunction (self, name, ret_type = Int64, stack_start = -1):
        func = Function(_efunc.loadSymbol(self.handle, name), ret_type, stack_start)

        if not func.value:
            raise EFuncError()
        
        return func

    def getVariable (self, name, value_type):
        addr = _efunc.loadSymbol(self.handle, name)

        if type(value_type) == Pointer:
            value = Pointer(addr, value_type.layers + 1, value_type.final_type)
        else:
            value = value_type.from_raw(_efunc.readMemory(addr, value_type.size))
        
        if not value.value:
            raise EFuncError()

    def close (self):
        _efunc.closeLibrary(self.handle)