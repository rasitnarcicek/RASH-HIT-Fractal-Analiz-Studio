#!/usr/bin/env bash
# onejar/launch4j PAKETLEME eklentileri olu depolarda. Bize paket degil DERLEME lazim.
# 'package' yerine 'compile' + classpath ile dogrudan calistirma.
set -e
A=/c/Users/RaşitNarçiçek/rakip_analiz/_arsiv
export PATH="$A/apache-maven-3.9.9/bin:$PATH"
cd "$A/JavaMathLib" 2>/dev/null && { echo "### JavaMathLib kurulumu"; mvn -q -B -DskipTests install 2>&1 | tail -5; echo "  -> ok"; }
cd /c/Users/RaşitNarçiçek/rakip_analiz/FractDim/code/modules
echo "### FractDim compile"
mvn -B -DskipTests compile 2>&1 | grep -E "BUILD|ERROR|WARNING.*source|Compiling|release" | head -25
echo "### classpath"
mvn -B -q dependency:build-classpath -Dmdep.outputFile=cp.txt 2>&1 | tail -5
echo "CP uzunluk: $(wc -c < cp.txt 2>/dev/null || echo YOK)"
ls -la target/classes 2>/dev/null | head -5
