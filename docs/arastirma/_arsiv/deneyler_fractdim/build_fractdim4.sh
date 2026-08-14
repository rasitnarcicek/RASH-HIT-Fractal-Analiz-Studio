#!/usr/bin/env bash
# javamathlib 1.0 yok; yerel olarak 1.2-SNAPSHOT kuruldu. Surumu yukselt,
# launch4j'yi BAGIMLILIK listesinden de cikar.
set -e
A=/c/Users/RaşitNarçiçek/rakip_analiz/_arsiv
export PATH="$A/apache-maven-3.9.9/bin:$PATH"
cd "$A/fd_build"
python - <<'PY'
s=open('pom.xml',encoding='utf-8').read()
s=s.replace('<version>1.0</version>','<version>1.2-SNAPSHOT</version>')
while 'launch4j' in s:
    i=s.find('launch4j')
    a=s.rfind('<dependency>',0,i); b=s.find('</dependency>',i)
    if a<0 or b<0: break
    s=s[:a]+s[b+len('</dependency>'):]
open('pom.xml','w',encoding='utf-8').write(s)
print("pom guncellendi")
PY
mvn -B -DskipTests compile 2>&1 | grep -E "BUILD|ERROR|Compiling|symbol|location" | head -40
echo "sinif sayisi: $(find target/classes -name '*.class' 2>/dev/null | wc -l)"
