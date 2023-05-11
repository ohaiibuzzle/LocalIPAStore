Module.ensureInitialized('Foundation');

const O_RDONLY = 0;
const O_WRONLY = 1;
const O_RDWR = 2;
const O_CREAT = 512;

const SEEK_SET = 0;
const SEEK_CUR = 1;
const SEEK_END = 2;


function freeze() {
    for (const { id } of Process.enumerateThreads())
        new NativeFunction(Module.findExportByName(
            'libsystem_kernel.dylib', 'thread_suspend'), 'pointer', ['uint'])(id);
}

function unfreeze() {
    for (const { id } of Process.enumerateThreads())
        new NativeFunction(Module.findExportByName(
            'libsystem_kernel.dylib', 'thread_resume'), 'pointer', ['uint'])(id);
}
function ptrAddr(addr) {
    return typeof (addr) == 'number' ? ptr(addr) : addr;
}

function allocStr(str) {
    return Memory.allocUtf8String(str);
}

function putStr(addr, str) {
    return Memory.writeUtf8String(ptrAddr(addr), str);
}

function getByteArr(addr, l) {
    return Memory.readByteArray(ptrAddr(addr), l);
}

function getU8(addr) {
    return Memory.readU8(ptrAddr(addr));
}

function putU8(addr, n) {
    return Memory.writeU8(ptrAddr(addr), n);
}

function getU16(addr) {
    return Memory.readU16(ptrAddr(addr));
}

function putU16(addr, n) {
    return Memory.writeU16(ptrAddr(addr), n);
}

function getU32(addr) {
    return Memory.readU32(ptrAddr(addr));
}

function putU32(addr, n) {
    return Memory.writeU32(ptrAddr(addr), n);
}

function getU64(addr) {
    return Memory.readU64(ptrAddr(addr));
}

function putU64(addr, n) {
    return Memory.writeU64(ptrAddr(addr), n);
}

function getPt(addr) {
    return Memory.readPointer(ptrAddr(addr));
}

function putPt(addr, n) {
    return Memory.writePointer(ptrAddr(addr), ptrAddr(n));
}

function malloc(size) {
    return Memory.alloc(size);
}

function getExportFunction(type, name, ret, args) {
    let nptr;
    nptr = Module.findExportByName(null, name);
    if (nptr === null) {
        console.log("cannot find " + name);
        return null;
    } else {
        if (type === "f") {
            let funclet = new NativeFunction(nptr, ret, args);
            if (typeof funclet === "undefined") {
                console.log("parse error " + name);
                return null;
            }
            return funclet;
        } else if (type === "d") {
            let datalet = Memory.readPointer(nptr);
            if (typeof datalet === "undefined") {
                console.log("parse error " + name);
                return null;
            }
            return datalet;
        }
    }
}

let NSSearchPathForDirectoriesInDomains = getExportFunction("f", "NSSearchPathForDirectoriesInDomains", "pointer", ["int", "int", "int"]);
let wrapper_open = getExportFunction("f", "open", "int", ["pointer", "int", "int"]);
let read = getExportFunction("f", "read", "int", ["int", "pointer", "int"]);
let write = getExportFunction("f", "write", "int", ["int", "pointer", "int"]);
let lseek = getExportFunction("f", "lseek", "int64", ["int", "int64", "int"]);
let close = getExportFunction("f", "close", "int", ["int"]);
let remove = getExportFunction("f", "remove", "int", ["pointer"]);
let access = getExportFunction("f", "access", "int", ["pointer", "int"]);
let dlopen = getExportFunction("f", "dlopen", "pointer", ["pointer", "int"]);

function getDocumentDir() {
    let NSDocumentDirectory = 9;
    let NSUserDomainMask = 1;
    let npdirs = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, 1);
    return ObjC.Object(npdirs).objectAtIndex_(0).toString();
}

function open(pathname, flags, mode) {
    if (typeof pathname == "string") {
        pathname = allocStr(pathname);
    }
    return wrapper_open(pathname, flags, mode);
}

let modules = null;
function getAllAppModules() {
    if (modules == null) {
        modules = new Array();
        let tmpmods = Process.enumerateModulesSync();
        for (let i = 0; i < tmpmods.length; i++) {
            if (tmpmods[i].path.lastIndexOf(".app") != -1) {
                modules.push(tmpmods[i]);
            }
        }
    }
    return modules;
}

const FAT_MAGIC = 0xcafebabe;
const FAT_CIGAM = 0xbebafeca;
const MH_MAGIC = 0xfeedface;
const MH_CIGAM = 0xcefaedfe;
const MH_MAGIC_64 = 0xfeedfacf;
const MH_CIGAM_64 = 0xcffaedfe;
const LC_SEGMENT = 0x1;
const LC_SEGMENT_64 = 0x19;
const LC_ENCRYPTION_INFO = 0x21;
const LC_ENCRYPTION_INFO_64 = 0x2C;

function pad(str, n) {
    return Array(n - str.length + 1).join("0") + str;
}

function swap32(value) {
    value = pad(value.toString(16), 8)
    let rs = "";
    for (let i = 0; i < value.length; i = i + 2) {
        rs += value.charAt(value.length - i - 2);
        rs += value.charAt(value.length - i - 1);
    }
    return parseInt(result, 16)
}

function dumpModule(name) {
    const modules = getAllAppModules();

    let targetmod = null;
    let i = 0;
    for (; i < modules.length; i++) {
        if (modules[i].path.indexOf(name) != -1) {
            targetmod = modules[i];
            break;
        }
    }
    if (targetmod == null) {
        console.log("Cannot find module");
        return;
    }
    let modbase = modules[i].base;
    let modsize = modules[i].size;
    let newmodname = modules[i].name;
    let newmodpath = getDocumentDir() + "/" + newmodname + ".fid";
    let oldmodpath = modules[i].path;


    if (!access(allocStr(newmodpath), 0)) {
        remove(allocStr(newmodpath));
    }

    let fmodule = open(newmodpath, O_CREAT | O_RDWR, 0);
    let foldmodule = open(oldmodpath, O_RDONLY, 0);

    if (fmodule == -1 || foldmodule == -1) {
        console.log("Cannot open file" + newmodpath);
        return;
    }

    let is64bit = false;
    let size_of_mach_header = 0;
    let magic = getU32(modbase);
    let cur_cpu_type = getU32(modbase.add(4));
    let cur_cpu_subtype = getU32(modbase.add(8));
    if (magic == MH_MAGIC || magic == MH_CIGAM) {
        is64bit = false;
        size_of_mach_header = 28;
    } else if (magic == MH_MAGIC_64 || magic == MH_CIGAM_64) {
        is64bit = true;
        size_of_mach_header = 32;
    }

    const BUFSIZE = 4096;
    let buffer = malloc(BUFSIZE);

    read(foldmodule, buffer, BUFSIZE);

    let fileoffset = 0;
    let filesize = 0;
    magic = getU32(buffer);
    if (magic == FAT_CIGAM || magic == FAT_MAGIC) {
        let off = 4;
        let archs = swap32(getU32(buffer.add(off)));
        for (let i = 0; i < archs; i++) {
            let cputype = swap32(getU32(buffer.add(off + 4)));
            let cpusubtype = swap32(getU32(buffer.add(off + 8)));
            if (cur_cpu_type == cputype && cur_cpu_subtype == cpusubtype) {
                fileoffset = swap32(getU32(buffer.add(off + 12)));
                filesize = swap32(getU32(buffer.add(off + 16)));
                break;
            }
            off += 20;
        }

        if (fileoffset == 0 || filesize == 0)
            return;

        lseek(fmodule, 0, SEEK_SET);
        lseek(foldmodule, fileoffset, SEEK_SET);
        for (let i = 0; i < parseInt(filesize / BUFSIZE); i++) {
            read(foldmodule, buffer, BUFSIZE);
            write(fmodule, buffer, BUFSIZE);
        }
        if (filesize % BUFSIZE) {
            read(foldmodule, buffer, filesize % BUFSIZE);
            write(fmodule, buffer, filesize % BUFSIZE);
        }
    } else {
        let readLen = 0;
        lseek(foldmodule, 0, SEEK_SET);
        lseek(fmodule, 0, SEEK_SET);
        while (readLen = read(foldmodule, buffer, BUFSIZE)) {
            write(fmodule, buffer, readLen);
        }
    }

    let ncmds = getU32(modbase.add(16));
    let off = size_of_mach_header;
    let offset_cryptid = -1;
    let crypt_off = 0;
    let crypt_size = 0;
    let segments = [];
    for (let i = 0; i < ncmds; i++) {
        let cmd = getU32(modbase.add(off));
        let cmdsize = getU32(modbase.add(off + 4));
        if (cmd == LC_ENCRYPTION_INFO || cmd == LC_ENCRYPTION_INFO_64) {
            offset_cryptid = off + 16;
            crypt_off = getU32(modbase.add(off + 8));
            crypt_size = getU32(modbase.add(off + 12));
        }
        off += cmdsize;
    }

    if (offset_cryptid != -1) {
        let tpbuf = malloc(8);
        putU64(tpbuf, 0);
        lseek(fmodule, offset_cryptid, SEEK_SET);
        write(fmodule, tpbuf, 4);
        lseek(fmodule, crypt_off, SEEK_SET);
        write(fmodule, modbase.add(crypt_off), crypt_size);
    }

    close(fmodule);
    close(foldmodule);
    return newmodpath
}


function walkDylibs(app_path, dirBlacklist) {
    console.log("walking dylibs at " + app_path + " with blacklist " + dirBlacklist.toString());
    let defaultManager = ObjC.classes.NSFileManager.defaultManager();
    let enumerator = defaultManager.enumeratorAtPath_(app_path);
    let dylibs = [];
    let frameworks = [];

    let path;
    while (path = enumerator.nextObject()) {
        // console.log("path: " + path.toString());
        for (let dir in dirBlacklist) {
            if (path.toString().indexOf(dirBlacklist[dir]) != -1) {
                console.log("Skipping " + path.toString() + " because it is in blacklist");
                enumerator.skipDescendants();
                continue;
            }
        }

        if (path.hasSuffix_(".bundle") ||
            path.hasSuffix_(".momd") ||
            path.hasSuffix_(".strings") ||
            path.hasSuffix_(".appex") ||
            path.hasSuffix_(".app") ||
            path.hasSuffix_(".lproj") ||
            path.hasSuffix_(".storyboardc")) {
            enumerator.skipDescendants();
            continue;
            };

        if (path.pathExtension() == "dylib") {
            dylibs.push(path);
        } else if (path.pathExtension() == "framework") {
            frameworks.push(path);
        }
    }
    return [dylibs, frameworks];
}

function loadAllDynamicLibrary2(app_path, dirBlacklist) {
    // freeze();
    let dylibs = [];
    let frameworks = [];

    let walkResult = walkDylibs(app_path, dirBlacklist);
    dylibs = walkResult[0];
    frameworks = walkResult[1];

    for (let i = 0; i < frameworks.length; i++) {
        let bundle = ObjC.classes.NSBundle.bundleWithPath_(app_path + "/" + frameworks[i]);
        if (bundle.isLoaded()) {
            console.log("[frida-ios-dump]: " + bundle.bundlePath() + " has been loaded. ");
        } else {
            if (bundle.load()) {
                console.log("[frida-ios-dump]: Load " + bundle.bundlePath() + " success. ");
            } else {
                console.log("[frida-ios-dump]: Load " + bundle.bundlePath() + " failed. ");
            }
        }
    }
    for (let i = 0; i < dylibs.length; i++) {
        let file_path = dylibs[i];
        let file_name = file_path.lastPathComponent();
        let is_loaded = 0;
        for (let j = 0; j < modules.length; j++) {
            if (modules[j].path.indexOf(file_name) != -1) {
                is_loaded = 1;
                console.log("[frida-ios-dump]: " + file_name + " has been dlopen.");
                break;
            }
        }

        if (!is_loaded) {
            try {
                if (dlopen(allocStr(file_path.UTF8String()), 9)) {
                    console.log("[frida-ios-dump]: dlopen " + file_name + " success. ");
                } else {
                    console.log("[frida-ios-dump]: dlopen " + file_name + " failed. ");
                }
            } catch (e) {
                // Try again
                try {
                    if (dlopen(allocStr(file_path.UTF8String()), 9)) {
                        console.log("[frida-ios-dump]: dlopen " + file_name + " success. ");
                    } else {
                        console.log("[frida-ios-dump]: dlopen " + file_name + " failed twice. ");
                    }
                }
                catch (e) {
                    console.log("[frida-ios-dump]: dlopen " + file_name + " massively failed. ");
                }
            }
        }
    }
}

function handleMessage(message) {
    // freeze();
    const modules = getAllAppModules();
    
    let dirBlacklist = message.blacklist;
    let app_path = ObjC.classes.NSBundle.mainBundle().bundlePath();
    loadAllDynamicLibrary2(app_path, dirBlacklist);
    // start dump
   
    for (let i = 0; i < modules.length; i++) {
        console.log("start dump " + modules[i].path);
        let result = dumpModule(modules[i].path);
        send({ dump: result, path: modules[i].path });
    }
    send({ app: app_path.toString() });
    send({ done: "ok" });
    recv(handleMessage);
}

recv(handleMessage);