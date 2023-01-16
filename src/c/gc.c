/*
    gc.c -- Garbage collector for efunc
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

#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

typedef struct {
    uint64_t addr;
    void *prev;
    void *next;
} Reference;

Reference *efunc_references = NULL;

Reference *efunc_gc_searchReferences (uint64_t addr) {
    Reference *ref = efunc_references;

    while (ref) {
        if (ref->addr == addr) {
            return ref;
        }

        ref = ref->prev;
    }

    return NULL;
}

int efunc_gc_addReference (uint64_t addr) {
    if (efunc_gc_searchReferences(addr)) {
        return 1;
    }

    Reference *old = efunc_references;
    efunc_references = malloc(sizeof(Reference));

    if (old) {
        old->next = efunc_references;
    }

    efunc_references->addr = addr;
    efunc_references->prev = old;
    efunc_references->next = NULL;

    return 0;
}

int efunc_gc_removeReference (uint64_t addr) {
    Reference *ref = efunc_gc_searchReferences(addr);

    if (!ref) {
        return 1;
    }

    if (ref->prev) {
        ((Reference *) ref->prev)->next = ref->next;
    }

    if (ref->next) {
        ((Reference *) ref->next)->prev = ref->prev;
    }

    if (ref == efunc_references) {
        efunc_references = NULL;
    }

    free(ref);

    return 0;
}