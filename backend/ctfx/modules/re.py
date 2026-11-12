import struct
from pathlib import Path
from typing import Dict, Any, List, Optional

ELF_ARCH_MAP = {
    0x03: "x86 (32-bit)",
    0x3E: "x86_64 (AMD64)",
    0x28: "ARM (32-bit)",
    0xB7: "AArch64 (ARM 64-bit)",
    0x08: "MIPS",
    0xF3: "RISC-V",
}

PE_MACHINE_MAP = {
    0x014C: "Intel x86 (32-bit)",
    0x8664: "AMD64 / x86_64",
    0x0200: "Intel Itanium",
    0xAA64: "ARM64 (Little Endian)",
}

SUSPICIOUS_API_SYMBOLS = [
    "system", "execve", "execl", "popen", "ptrace",
    "mprotect", "VirtualAlloc", "VirtualProtect",
    "CreateRemoteThread", "WriteProcessMemory", "WinExec",
    "URLDownloadToFileA", "InternetOpenA", "socket", "connect"
]

class ReverseEngineeringAnalyzer:
    """Static reverse engineering parser for ELF, PE, and Mach-O binary executables."""

    @classmethod
    def analyze_binary(cls, file_path: Path) -> Dict[str, Any]:
        """Inspect binary executable format, architecture, sections, symbols, and suspicious functions."""
        with open(file_path, "rb") as f:
            header = f.read(64)

        if header.startswith(b"\x7fELF"):
            return cls._analyze_elf(file_path)
        elif header.startswith(b"MZ"):
            return cls._analyze_pe(file_path)
        elif header[:4] in (b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe"):
            return cls._analyze_macho(file_path)

        return {"is_executable": False, "error": "Not a recognized binary format (ELF, PE, or Mach-O)"}

    @classmethod
    def _analyze_elf(cls, file_path: Path) -> Dict[str, Any]:
        """Parse ELF header, section headers, and string table."""
        with open(file_path, "rb") as f:
            ident = f.read(16)
            is_64 = ident[4] == 2
            is_little = ident[5] == 1
            endian = "<" if is_little else ">"

            if is_64:
                # 64-bit ELF header
                f.seek(16)
                e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = struct.unpack(
                    f"{endian}HHIQQQIHHHHHH", f.read(48)
                )
            else:
                # 32-bit ELF header
                f.seek(16)
                e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx = struct.unpack(
                    f"{endian}HHIIIIIHHHHHH", f.read(36)
                )

            # Read section headers
            sections = []
            shstrtab_data = b""

            if e_shoff > 0 and e_shnum > 0 and e_shentsize > 0:
                # First pass: find shstrtab
                if e_shstrndx < e_shnum:
                    f.seek(e_shoff + e_shstrndx * e_shentsize)
                    sh_raw = f.read(e_shentsize)
                    if is_64 and len(sh_raw) >= 64:
                        sh_offset = struct.unpack(f"{endian}Q", sh_raw[24:32])[0]
                        sh_size = struct.unpack(f"{endian}Q", sh_raw[32:40])[0]
                        f.seek(sh_offset)
                        shstrtab_data = f.read(sh_size)
                    elif not is_64 and len(sh_raw) >= 40:
                        sh_offset = struct.unpack(f"{endian}I", sh_raw[16:20])[0]
                        sh_size = struct.unpack(f"{endian}I", sh_raw[20:24])[0]
                        f.seek(sh_offset)
                        shstrtab_data = f.read(sh_size)

                # Second pass: read section names
                for i in range(min(e_shnum, 64)):
                    f.seek(e_shoff + i * e_shentsize)
                    sh_raw = f.read(e_shentsize)
                    if is_64 and len(sh_raw) >= 64:
                        sh_name_idx, sh_type, sh_flags, sh_addr, sh_offset, sh_size = struct.unpack(
                            f"{endian}IIQQQQ", sh_raw[:40]
                        )
                    elif not is_64 and len(sh_raw) >= 40:
                        sh_name_idx, sh_type, sh_flags, sh_addr, sh_offset, sh_size = struct.unpack(
                            f"{endian}IIIIII", sh_raw[:24]
                        )
                    else:
                        break

                    name = f"section_{i}"
                    if shstrtab_data and sh_name_idx < len(shstrtab_data):
                        end_idx = shstrtab_data.find(b"\x00", sh_name_idx)
                        if end_idx != -1:
                            name = shstrtab_data[sh_name_idx:end_idx].decode("latin1", errors="replace")

                    sections.append({
                        "name": name,
                        "type": hex(sh_type),
                        "virtual_address": hex(sh_addr),
                        "size": sh_size,
                        "file_offset": sh_offset
                    })

        # Scan for suspicious symbols in whole file
        content = file_path.read_bytes()
        detected_suspicious = [sym for sym in SUSPICIOUS_API_SYMBOLS if sym.encode("ascii") in content]

        return {
            "format": "ELF",
            "bitness": 64 if is_64 else 32,
            "endian": "little" if is_little else "big",
            "architecture": ELF_ARCH_MAP.get(e_machine, f"Unknown (0x{e_machine:x})"),
            "entrypoint": hex(e_entry),
            "total_sections": len(sections),
            "sections": sections[:30],
            "suspicious_apis_detected": detected_suspicious,
        }

    @classmethod
    def _analyze_pe(cls, file_path: Path) -> Dict[str, Any]:
        """Parse Portable Executable (PE) headers and sections."""
        with open(file_path, "rb") as f:
            f.seek(0x3C)
            pe_offset = struct.unpack("<I", f.read(4))[0]
            f.seek(pe_offset)
            pe_sig = f.read(4)
            if pe_sig != b"PE\x00\x00":
                return {"format": "DOS_MZ", "is_pe": False}

            # COFF Header (20 bytes)
            machine, num_sections, timestamp, sym_table, num_syms, opt_hdr_size, characteristics = struct.unpack(
                "<HHIIIHH", f.read(20)
            )

            # Optional Header
            magic = struct.unpack("<H", f.read(2))[0]
            is_pe32_plus = (magic == 0x20B)  # 64-bit

            entrypoint_rva = 0
            if opt_hdr_size > 0:
                f.seek(pe_offset + 24 + 16)
                entrypoint_rva = struct.unpack("<I", f.read(4))[0]

            # Read section headers
            sections = []
            f.seek(pe_offset + 24 + opt_hdr_size)
            for _ in range(min(num_sections, 32)):
                sec_raw = f.read(40)
                if len(sec_raw) < 40:
                    break
                sec_name = sec_raw[:8].rstrip(b"\x00").decode("latin1", errors="replace")
                v_size, v_addr, raw_size, raw_ptr = struct.unpack("<IIII", sec_raw[8:24])
                sections.append({
                    "name": sec_name,
                    "virtual_size": v_size,
                    "virtual_address": hex(v_addr),
                    "raw_data_size": raw_size,
                    "file_offset": raw_ptr
                })

        content = file_path.read_bytes()
        detected_suspicious = [sym for sym in SUSPICIOUS_API_SYMBOLS if sym.encode("ascii") in content]

        return {
            "format": "PE",
            "bitness": 64 if is_pe32_plus else 32,
            "architecture": PE_MACHINE_MAP.get(machine, f"Unknown (0x{machine:x})"),
            "entrypoint_rva": hex(entrypoint_rva),
            "total_sections": len(sections),
            "sections": sections,
            "suspicious_apis_detected": detected_suspicious
        }

    @classmethod
    def _analyze_macho(cls, file_path: Path) -> Dict[str, Any]:
        """Parse Mach-O binary header."""
        with open(file_path, "rb") as f:
            magic = f.read(4)
            is_64 = magic in (b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe")
            is_little = magic in (b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe")
            endian = "<" if is_little else ">"

            cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags = struct.unpack(
                f"{endian}IIIIII", f.read(24)
            )

        return {
            "format": "Mach-O",
            "bitness": 64 if is_64 else 32,
            "endian": "little" if is_little else "big",
            "cpu_type": hex(cputype),
            "command_count": ncmds
        }
