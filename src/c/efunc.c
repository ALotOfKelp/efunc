/*
    efunc.c -- Python wrapper for call_func.s
    Copyright © 2022 Iskander Boutel

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

#include <Python.h>
#include <dlfcn.h>
#include <string.h>

void *efunc_func = NULL;
void **efunc_params;
uint64_t efunc_nparams;
uint64_t efunc_stack_params;
uint64_t efunc_stack_params_start;
uint64_t efunc_param_index;

extern void *efunc_callFunc (void *func, void *params[], uint64_t nparams, uint8_t stack_params, uint64_t stack_params_start);

static PyObject *method_loadLibrary (PyObject *self, PyObject *args) {
    char *name;

    if (!PyArg_ParseTuple(args, "s", &name)) {
        return NULL;
    }

    return PyLong_FromLong(dlopen(name, RTLD_LAZY));
}

static PyObject *method_loadSymbol (PyObject *self, PyObject *args) {
    char *name;
    void *handle;

    if (!PyArg_ParseTuple(args, "Ls", &handle, &name)) {
        return NULL;
    }

    return PyLong_FromLong(dlsym(handle, name));
}

static PyObject *method_closeLibrary (PyObject *self, PyObject *args) {
    void *handle;

    if (!PyArg_ParseTuple(args, "L", &handle)) {
        return NULL;
    }

    return PyLong_FromLong(dlclose(handle));
}

static PyObject *method_getLibraryError (PyObject *self, PyObject *args) {
    return Py_BuildValue("s", dlerror());
}

static PyObject *method_readMemory (PyObject *self, PyObject *args) {
    void *pointer;
    uint64_t len;

    if (!PyArg_ParseTuple(args, "LL", &pointer, &len)) {
        return NULL;
    }

    return Py_BuildValue("y#", pointer, len);
}

static PyObject *method_writeMemory (PyObject *self, PyObject *args) {
    void *pointer;
    Py_buffer value;
    uint64_t len;

    if (!PyArg_ParseTuple(args, "Ly*L", &pointer, &value, &len)) {
        return NULL;
    }

    return PyLong_FromLong(memcpy(pointer, value.buf, len));
}

static PyObject *method_allocateMemory (PyObject *self, PyObject *args) {
    uint64_t size;

    if (!PyArg_ParseTuple(args, "L", &size)) {
        return NULL;
    }

    return PyLong_FromLong(malloc(size));
}

static PyObject *method_freeMemory (PyObject *self, PyObject *args) {
    void *address;

    if (!PyArg_ParseTuple(args, "L", &address)) {
        return NULL;
    }

    free(address);

    return Py_None;
}

static PyObject *method_setFuncCallSpecs (PyObject *self, PyObject *args) {
    if (!PyArg_ParseTuple(args, "LLLL", &efunc_func, &efunc_nparams, &efunc_stack_params, &efunc_stack_params_start)) {
        return NULL;
    }

    efunc_params = malloc(efunc_nparams * sizeof(void *));
    efunc_param_index = 0;

    return PyLong_FromLong(efunc_func);
}

static PyObject *method_addFuncCallParam (PyObject *self, PyObject *args) {
    if (!PyArg_ParseTuple(args, "L", &(efunc_params[efunc_param_index]))) {
        return NULL;
    }

    efunc_param_index++;

    return PyLong_FromLong(efunc_param_index);
}

static PyObject *method_callFunc (PyObject *self) {
    if (!efunc_func) {
        PyErr_SetString(PyExc_RuntimeError, "No function specified");
        return NULL;
    }

    return PyLong_FromLong(efunc_callFunc(efunc_func, efunc_params, efunc_nparams, efunc_stack_params, efunc_stack_params_start));
}

static PyObject *method_cleanCallSpecs (PyObject *self) {
    free(efunc_params);
    efunc_func = NULL;

    return Py_None;
}

static PyMethodDef efunc_methods[] = {
    {"loadLibrary", method_loadLibrary, METH_VARARGS},
    {"loadSymbol", method_loadSymbol, METH_VARARGS},
    {"closeLibrary", method_closeLibrary, METH_VARARGS},
    {"getLibraryError", method_getLibraryError, METH_VARARGS},
    {"writeMemory", method_writeMemory, METH_VARARGS},
    {"readMemory", method_readMemory, METH_VARARGS},
    {"allocateMemory", method_allocateMemory, METH_VARARGS},
    {"freeMemory", method_freeMemory, METH_VARARGS},
    {"setFuncCallSpecs", method_setFuncCallSpecs, METH_VARARGS},
    {"addFuncCallParam", method_addFuncCallParam, METH_VARARGS},
    {"callFunc", method_callFunc, METH_NOARGS},
    {"cleanCallSpecs", method_cleanCallSpecs, METH_NOARGS}
};

static struct PyModuleDef efunc_module = {
    PyModuleDef_HEAD_INIT,
    "_efunc",
    "Python interface to external functions",
    -1,
    efunc_methods
};

PyMODINIT_FUNC PyInit__efunc (void) {
    return PyModule_Create(&efunc_module);
}