var="XLONG,XLAT,XTIME,Times,T,P,PB,PH,PHB,HGT,U,V,W,QCLOUD,QICE,QVAPOR,QRAIN,QGRAUP,QSNOW,no,no2,o3,co,chem_o3,vmix_o3,advh_o3,advz_o3"
savedir="subset"
mkdir -p $savedir

for f in wrfout_d04_2020-09-01_0[4-6]*
do
    echo "Subsetting ${f}: ${var}"
    new_f="${savedir}/${f}_subset"
    if [[ -e $new_f ]]; then
        echo "$new_f exists, Skip ..."
    else
        ncks -F -O -d Time,1,,1000 -v $var $f "$new_f"
        echo "  Saved to $new_f"
    fi
done
