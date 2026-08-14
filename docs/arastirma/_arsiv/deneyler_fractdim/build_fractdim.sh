#!/usr/bin/env bash
# FractDim derleme denemesi. Sinirli sure, basarisiz olursa duruma raporlanir.
set -x
cd /c/Users/RaşitNarçiçek/rakip_analiz/_arsiv || exit 1
MV=apache-maven-3.9.9
if [ ! -d "$MV" ]; then
  curl -sL -o mvn.zip "https://archive.apache.org/dist/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.zip" || exit 2
  unzip -q mvn.zip || exit 3
fi
export PATH="$PWD/$MV/bin:$PATH"
mvn -version || exit 4

# 1) JavaMathLib
[ -d JavaMathLib ] || git clone -q --depth 1 https://github.com/danielrendall/JavaMathLib.git
cd JavaMathLib || exit 5
echo "=== POM JavaMathLib ==="
grep -E "<artifactId>|<version>|<source>|<target>|<release>" pom.xml | head -20
mvn -q -B -DskipTests install 2>&1 | tail -25
echo "JAVAMATHLIB_EXIT=$?"
cd ..

# 2) FractDim
cd /c/Users/RaşitNarçiçek/rakip_analiz/FractDim/code/modules || exit 6
echo "=== POM FractDim compiler ayarlari ==="
grep -B2 -A6 "maven-compiler-plugin" pom.xml
export PATH="/c/Users/RaşitNarçiçek/rakip_analiz/_arsiv/$MV/bin:$PATH"
mvn -B -DskipTests package 2>&1 | tail -40
echo "FRACTDIM_EXIT=$?"
ls -la target/*.jar 2>/dev/null
