#    library.py -- efunc library loader
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

from . import types, _efunc

class EFuncError (Exception):
    def __init__ (self):
        Exception.__init__(self, _efunc.getLibraryError())

class Library:
    def __init__ (self, path):
        self.path = path
        self.handle = _efunc.loadLibrary(path)

        if not self.handle:
            raise EFuncError()
    
    def getFunction (self, name, descriptor):
        func = types.Function(_efunc.loadSymbol(self.handle, name), descriptor)

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