import re,sys,glob
def pins(lib,name):
    s=open(lib).read()
    i=s.find('(symbol "%s"'%name)
    if i<0: return None
    # find end by balanced parens
    d=0;j=i
    while True:
        c=s[j]
        if c=='(':d+=1
        elif c==')':
            d-=1
            if d==0:break
        j+=1
    blk=s[i:j]
    m=re.search(r'\(extends "([^"]+)"',blk)
    if m: return pins(lib,m.group(1))
    return re.findall(r'\(pin \S+ \S+.*?\(name "([^"]*)".*?\(number "([^"]*)"',blk,re.S)
lib,name=sys.argv[1],sys.argv[2]
p=pins('/usr/share/kicad/symbols/'+lib,name)
print(' '.join(f'{n}:{nm}' for nm,n in sorted(p,key=lambda x:(len(x[1]),x[1]))))
