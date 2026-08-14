#!/usr/bin/env bash
# FractDim gercek calistirma testi - <path> tabanli SVG'lerle.
# KRITIK SORU: dolu bir kare D~2.0 mi verir (dolgu olculur) yoksa
#              D~1.0 mi (sadece kontur sayilir)?
export MSYS2_ARG_CONV_EXCL='*'
cd /c/fdrun

# Ayni geometri (kare kapali yol), tek fark: fill dolu vs bos
cat > p_dolu.svg <<'EOF'
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <path d="M 56,56 L 456,56 L 456,456 L 56,456 Z" fill="black" stroke="none"/>
</svg>
EOF
cat > p_bos.svg <<'EOF'
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <path d="M 56,56 L 456,56 L 456,456 L 56,456 Z" fill="none" stroke="black" stroke-width="1"/>
</svg>
EOF

for f in p_dolu p_bos; do
  echo "########## $f.svg ##########"
  java -cp "classes;libs/*" uk.co.danielrendall.fractdim.cmd.FractDim \
      -f $f.svg -d 3 -min 2 -max 128 -s 12 -a 1 -p 1 -do Count 2>&1 | grep -v "^log4j" | tail -20
  echo
  echo "--- Stats ---"
  java -cp "classes;libs/*" uk.co.danielrendall.fractdim.cmd.FractDim \
      -f $f.svg -do Stats 2>&1 | grep -v "^log4j" | tail -12
  echo
done
