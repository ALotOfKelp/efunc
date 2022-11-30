;    call_func.s -- Dynamic parameter passing for C compatible functions
;    Copyright © 2022 Iskander Boutel
;
;    This program is free software: you can redistribute it and/or modify
;    it under the terms of the GNU General Public License as published by
;    the Free Software Foundation, either version 3 of the License, or
;    (at your option) any later version.
;
;    This program is distributed in the hope that it will be useful,
;    but WITHOUT ANY WARRANTY; without even the implied warranty of
;    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;    GNU General Public License for more details.
;
;    You should have received a copy of the GNU General Public License
;    along with this program.  If not, see <https://www.gnu.org/licenses/>.

.section __TEXT, __text
.p2align 2

.globl _efunc_callFunc
_efunc_callFunc:
    mov x5, xzr
    cmp x3, #0
    b.eq L._efunc_callFunc.no_stack

    sub x7, x2, x4
    mov x5, #8
    mul x4, x4, x5
    mul x7, x7, x5
    add x11, x1, x4
    mov x13, x4
    mov x6, #16
    sdiv x5, x7, x6
    mul x5, x5, x6
    subs x6, x7, x5
    b.eq L._efunc_callFunc.no_stack
    add x5, x5, #16
    mov x12, #8
    b L._efunc_callFunc.odd_stack

L._efunc_callFunc.no_stack:
    mov x12, xzr

L._efunc_callFunc.odd_stack:
    sub sp, sp, #32
    stp x29, x30, [sp]
    str x28, [sp, #16]
    mov x29, sp
    sub x29, x29, x12
    sub sp, sp, x5

    mov x8, x0
    mov x9, x1
    mov x10, x2
    mov x2, xzr

    cmp x3, #0
    b.eq L._efunc_callFunc.loop1.done

L._efunc_callFunc.loop1:
    sub x3, x11, x13
    sub x3, x3, x9
    mov x4, sp
    
    add x3, x3, x4
    
    cmp x3, x29
    b.ge L._efunc_callFunc.loop1.done

    ldr x1, [x11]
    str x1, [sp, x2]

    add x2, x2, #8
    add x11, x11, #8
    b L._efunc_callFunc.loop1

L._efunc_callFunc.loop1.done:
    cmp x9, x11
    b.eq L._efunc_callFunc.done
    ldr x0, [x9]
    add x9, x9, #8

    cmp x9, x11
    b.eq L._efunc_callFunc.done
    ldr x1, [x9]
    add x9, x9, #8

    cmp x9, x11
    b.eq L._efunc_callFunc.done
    ldr x2, [x9]
    add x9, x9, #8

    cmp x9, x11
    b.eq L._efunc_callFunc.done
    ldr x3, [x9]
    add x9, x9, #8

    cmp x9, x11
    b.eq L._efunc_callFunc.done
    ldr x4, [x9]
    add x9, x9, #8

    cmp x9, x11
    b.eq L._efunc_callFunc.done
    ldr x5, [x9]
    add x9, x9, #8

    cmp x9, x11
    b.eq L._efunc_callFunc.done
    ldr x6, [x9]
    add x9, x9, #8

    cmp x9, x11
    b.eq L._efunc_callFunc.done
    ldr x7, [x9]
    add x9, x9, #8

L._efunc_callFunc.done:
    mov x28, x12
    blr x8

    mov sp, x29
    add sp, sp, x28
    ldp x29, x30, [sp]
    ldr x28, [sp, #16]
    add sp, sp, #32

    ret