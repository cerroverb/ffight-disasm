/* Reads a MAME debugger trace stream; writes sorted unique 68000 PCs (hex, one per line). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned char seen[1 << 24];
static int hexv(int c) { return c >= '0' && c <= '9' ? c - '0' : c >= 'A' && c <= 'F' ? c - 'A' + 10 : -1; }
int main(int argc, char **argv) {
    FILE *in = fopen(argv[1], "r"), *out;
    static char line[4096];
    long n = 0;
    if (!in) return 1;
    while (fgets(line, sizeof line, in)) {
        unsigned v = 0; int ok = 1;
        for (int i = 0; i < 6; i++) { int h = hexv(line[i]); if (h < 0) { ok = 0; break; } v = v << 4 | h; }
        if (ok && line[6] == ':' && !seen[v]) { seen[v] = 1; n++; }
    }
    out = fopen(argv[2], "w");
    for (unsigned v = 0; v < (1u << 24); v++) if (seen[v]) fprintf(out, "%06x\n", v);
    fclose(out);
    printf("unique pcs %ld\n", n);
    return 0;
}
