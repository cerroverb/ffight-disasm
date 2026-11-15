import sys
F=65536
src=open(sys.argv[1],'rb'); out=open(sys.argv[2],'wb'); i=0
while True:
    b=src.read(F)
    if len(b)<F: break
    if i%10==0: out.write(b)
    i+=1
print('frames read', i)
