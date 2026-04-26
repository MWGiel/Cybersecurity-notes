# Linux Memory Management – Short Notes

## Virtual Memory
- Each process gets its own **virtual address space** (typically 128TB on x86-64).
- CPU + MMU translate virtual addresses to **physical addresses**.
- Benefits: isolation, security, simplified addressing.

## Page & Page Size
- Memory divided into **pages** (typically 4KB, also 2MB/1GB huge pages).
- Virtual page → Physical page via **page tables**.
- Page fault: accessed page not in physical RAM → kernel loads it (or crashes if invalid).

## Memory Zones

| Zone | Description |
|------|-------------|
| ZONE_DMA | <16MB, for legacy ISA devices |
| ZONE_DMA32 | 16MB–4GB, for 32-bit PCI |
| ZONE_NORMAL | 4GB+, directly mapped, kernel uses |
| ZONE_HIGHMEM | (deprecated) not needed on 64-bit |

## Caches & Swapping

| Mechanism | Purpose |
|-----------|---------|
| **Page Cache** | Caches filesystem pages (disk read/write) |
| **Swap** | Moves inactive pages to disk to free RAM |
| **OOM Killer** | Last resort – kills process when system completely out of memory |

## Key `/proc` Files
```bash
cat /proc/meminfo   # memory stats
cat /proc/swaps     # swap usage
cat /proc/buddyinfo # fragmentation info