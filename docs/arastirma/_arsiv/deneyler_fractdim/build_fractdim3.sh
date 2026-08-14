#!/usr/bin/env bash
# FractDim'i olu paketleme eklentileri (onejar, launch4j) cikarilmis bir
# KOPYA uzerinde derle. Orijinal klon bozulmaz.
set -e
A=/c/Users/RaşitNarçiçek/rakip_analiz/_arsiv
export PATH="$A/apache-maven-3.9.9/bin:$PATH"
W="$A/fd_build"
rm -rf "$W"; mkdir -p "$W"
cp -r /c/Users/RaşitNarçiçek/rakip_analiz/FractDim/code/modules/* "$W"/
cd "$W"
python - <<'PY'
import re
s=open('pom.xml',encoding='utf-8').read()
# onejar ve launch4j <plugin> bloklarini sok
for art in ('onejar-maven-plugin','launch4j-maven-plugin'):
    while True:
        i=s.find(art)
        if i<0: break
        a=s.rfind('<plugin>',0,i); b=s.find('</plugin>',i)
        if a<0 or b<0: break
        s=s[:a]+s[b+len('</plugin>'):]
# olu http depolarini sok
s=re.sub(r'<repository>(?:(?!</repository>).)*?9stmaryrd|googlecode(?:(?!</repository>).)*?</repository>','',s,flags=re.S)
s=re.sub(r'<repositories>.*?</repositories>','',s,flags=re.S)
s=re.sub(r'<pluginRepositories>.*?</pluginRepositories>','',s,flags=re.S)
open('pom.xml','w',encoding='utf-8').write(s)
print("pom temizlendi")
PY
echo "### compile"
mvn -B -DskipTests compile 2>&1 | grep -E "BUILD|ERROR|Compiling|source|release|invalid|target" | head -30
echo "### classpath"
mvn -B -q dependency:build-classpath -Dmdep.outputFile=cp.txt 2>&1 | grep -E "ERROR" | head -5
echo "sinif sayisi: $(find target/classes -name '*.class' 2>/dev/null | wc -l)"
echo "cp: $(wc -c < cp.txt 2>/dev/null || echo YOK)"
