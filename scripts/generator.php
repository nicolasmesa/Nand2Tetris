<?php
/*
for ($i=0; $i < 16; $i++) {
	echo "    Or(a=a[$i], b=b[$i], out=out[$i]);\n";
}
*/

/*
for ($i=0; $i < 16; $i++) {
	echo "    Mux(a=a[$i], b=b[$i], sel=sel, out=out[$i]);\n";
}
*/
/*
for ($i=1; $i < 16; $i++) {
	echo "    Or(a=temp_" . ($i - 1) .", b=in[" . ($i + 1) ."], out=temp_$i);\n";
}
*/
for ($i=1; $i < 16; $i++) {
	echo "    FullAdder(a=a[$i], b=b[$i], c=carry" . ($i - 1) . ", sum=out[$i], carry=carry$i);\n";
}
