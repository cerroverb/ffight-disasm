import sys
p=sys.argv[1]; n=int(sys.argv[3])
with open(p,'rb') as f:
    f.seek((n-1)*65536); b=f.read(65536)
def r(a): return b[a-0xFF0000]
print(f"{sys.argv[2]:28} frame {n}: credits P1/shared={r(0xFF818C):02X} P2={r(0xFF8194):02X} P3={r(0xFF819C):02X} "
      f"1C5={r(0xFF81C5):02X} 1C6={r(0xFF81C6):02X} in play P1={r(0xFF8380):02X} P2={r(0xFF8480):02X} P3={r(0xFF8580):02X} mode={r(0xFF8000):02X}{r(0xFF8001):02X}")
