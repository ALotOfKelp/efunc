/*
    efunc.h -- Definitions for efunc wrapper
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

#ifndef __EFUNC_H__
#define __EFUNC_H__

#include <Python.h>
#include <dlfcn.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

extern void *efunc_callFunc (void *func, void *params[], uint64_t nparams, uint8_t stack_params, uint64_t stack_params_start, uint8_t float_result);

int efunc_gc_addReference (uint64_t addr);
int efunc_gc_removeReference (uint64_t addr);

#endif