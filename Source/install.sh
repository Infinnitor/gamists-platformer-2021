#!/bin/bash

echo "---------------------------"
echo "Creating building directory"
echo "---------------------------"

rm -rf building
mkdir -p building --verbose

echo "---------------------------"
echo "Copying Python source files"
echo "---------------------------"
cp *.py building/ --verbose

# echo "---------------------------"
# echo "Copying Data"
# echo "---------------------------"
# cp -r data building/ --verbose

echo "--------------------------------"
echo "Building executable from main.py"
echo "--------------------------------"
cd building
pyinstaller main.py --onefile --clean

cd ..
if [ [ ! -e "building/dist/main" ] ]
	then echo "Executable not built"
	exit
fi

echo "-----------------"
echo "Finished building"
echo "-----------------"

cp building/dist/main . --verbose
chmod +x main --verbose

echo "---------------------------"
echo "Deleting building directory"
echo "---------------------------"

rm -rf building

echo "Running built executable..."
cd building
./main
