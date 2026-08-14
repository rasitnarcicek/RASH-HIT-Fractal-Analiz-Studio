#!/usr/bin/env bash
# Java, Turkce karakterli classpath yolunu (RasitNarcicek) cozemiyor.
# Cozum: derlenmis siniflar + tum bagimliliklar SAF ASCII yola kopyalanir.
set -e
A=/c/Users/RaşitNarçiçek/rakip_analiz/_arsiv
export PATH="$A/apache-maven-3.9.9/bin:$PATH"
export MSYS2_ARG_CONV_EXCL='*'
D=/c/fdrun
rm -rf $D; mkdir -p $D/libs

cd "$A/fd_build"
mvn -B -q dependency:copy-dependencies -DoutputDirectory="$(cygpath -w $D/libs)" 2>&1 | grep ERROR | head -3 || true
cp -r target/classes $D/classes
echo "jar sayisi: $(ls $D/libs/*.jar | wc -l)"

cd $D
cat > dolu_kare.svg <<'EOF'
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect x="56" y="56" width="400" height="400" fill="black" stroke="none"/>
</svg>
EOF
cat > bos_kare.svg <<'EOF'
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect x="56" y="56" width="400" height="400" fill="none" stroke="black" stroke-width="1"/>
</svg>
EOF

for f in dolu_kare bos_kare; do
  echo "======================= $f.svg ======================="
  java -cp "classes;libs/*" uk.co.danielrendall.fractdim.cmd.FractDim \
      -f $f.svg -d 3 -min 2 -max 128 -s 12 -a 1 -p 1 -do Count 2>&1 | tail -30
done
