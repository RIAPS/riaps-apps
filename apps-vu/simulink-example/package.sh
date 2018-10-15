set +e
export outputdir=`mktemp -d`
mkdir $outputdir/Sltest
cp -r pkg/* $outputdir/Sltest
export currentdir=`pwd`
cd  $outputdir
tar czvf Sltest.tar.gz Sltest/*
cd $currentdir
mv $outputdir/Sltest.tar.gz .   

