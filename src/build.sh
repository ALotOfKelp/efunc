mkdir efunc

clang c/call_func.s -c -o efunc/call_func.o
clang -Wno-unused-result -Wsign-compare -Wunreachable-code -fno-common -dynamic -DNDEBUG -g -fwrapv -O3 -Wall -iwithsysroot/System/Library/Frameworks/System.framework/PrivateHeaders -iwithsysroot/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.8/Headers -arch arm64 -arch x86_64 -Werror=implicit-function-declaration -I/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.8/include/python3.8 -c c/efunc.c -o efunc/efunc.o -std=c17 -arch arm64
clang -bundle -undefined dynamic_lookup -arch arm64 -Wl,-headerpad,0x1000 efunc/efunc.o efunc/call_func.o -o efunc/_efunc.cpython-38-darwin.so
rm efunc/efunc.o efunc/call_func.o

cp python/* efunc