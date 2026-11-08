/* Reads a MAME debugger trace stream; writes sorted unique 68000 PCs (hex, one per line).
   The output file is rewritten every few million lines so a killed run keeps its coverage. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned char seen[1 << 24];
static int hexv(int c) { return c >= '0' && c <= '9' ? c - '0' : c >= 'A' && c <= 'F' ? c - 'A' + 10 : -1; }
static void write_pcs(const char *path) {
    FILE *out = fopen(path, "w");
    if (!out) return;
    for (unsigned v = 0; v < (1u << 24); v++) if (seen[v]) fprintf(out, "%06x\n", v);
    fclose(out);
}
int main(int argc, char **argv) {
    FILE *in = fopen(argv[1], "r");
    static char line[4096];
    long n = 0, lines = 0;
    if (!in) return 1;
    while (fgets(line, sizeof line, in)) {
        unsigned v = 0; int ok = 1;
        for (int i = 0; i < 6; i++) { int h = hexv(line[i]); if (h < 0) { ok = 0; break; } v = v << 4 | h; }
        if (ok && line[6] == ':' && !seen[v]) { seen[v] = 1; n++; }
        if (++lines % 5000000 == 0) write_pcs(argv[2]);
    }
    write_pcs(argv[2]);
    printf("unique pcs %ld\n", n);
    return 0;
}
