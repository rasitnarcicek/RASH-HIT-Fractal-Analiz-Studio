#!/usr/bin/env bash
# FractDim'i GERCEKTEN calistir. Amac: "dolgu olculemiyor" iddiasini
# kod okumayla degil, deneyle kanitlamak.
# Test: DOLU KARE. Dolgu olculebiliyorsa D~2.0, sadece kontur sayiliyorsa D~1.0
set -e
A=/c/Users/RaşitNarçiçek/rakip_analiz/_arsiv
cd "$A/fd_build"
export PATH="$A/apache-maven-3.9.9/bin:$PATH"
mvn -B -q dependency:build-classpath -Dmdep.outputFile=cp.txt 2>&1 | grep ERROR | head -3 || true
CP="target/classes;$(cat cp.txt)"
mkdir -p ../fd_test && cd ../fd_test

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
  echo "=================== $f.svg ==================="
  java -cp "$CP" uk.co.danielrendall.fractdim.cmd.FractDim \
      -f $f.svg -d 3 -min 2 -max 128 -s 12 -a 1 -p 1 -do Count 2>&1 | tail -25
done
