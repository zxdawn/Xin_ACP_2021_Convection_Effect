var="Times,ALKO2_NO_IRR,C2H5O2_NO_IRR,C3H7O2_NO_IRR,CH3CO3_NO_IRR,CH3O2_NO_IRR,ENEO2_NO_IRR,EO2_NO_IRR,ISOPNO3_NO_IRR,ISOPO2_NO_IRR,MACRO2_NO_IRR,MACRO2_NO_a_IRR,MCO3_NO_IRR,MEKO2_NO_IRR,NO3_NO_IRR,NO_HO2_IRR,O3_NO_IRR,PO2_NO_IRR,RO2_NO_IRR,TERPO2_NO_IRR,TOLO2_NO_IRR,XO2_NO_IRR,C10H16_O3_IRR,C2H4_O3_IRR,C3H6_O3_IRR,CH3CO3_HO2_IRR,HO2_O3_IRR,ISOP_O3_IRR,MACR_O3_IRR,MCO3_HO2_IRR,MVK_O3_IRR,NO3_HV_IRR,O3_HV_IRR,O3_HV_a_IRR,O3_NO2_IRR,O3_NO_IRR,OH_O3_IRR,O_M_IRR,O_O3_IRR,O1D_CB4_H2O_IRR"
savedir="subset"
mkdir -p $savedir

for f in IRR_DIAG_d04_2020-09-01_0[4-6]*
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
