#!/bin/bash
if [ "$EUID" -eq 0 ]
	then echo "Do not run as root, it can cause unwanted behaviour"
	exit
fi

echo "---------------------------"
echo "Creating building directory"
echo "---------------------------"

rm -rf building
mkdir -p building --verbose

echo "---------------------------"
echo "Copying Python source files"
echo "---------------------------"
cp *.py building/ --verbose

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

rm -rf building --verbose

echo "---------------------------"
echo "Running built executable..."
echo "---------------------------"
./main
