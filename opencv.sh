CV_VERSION=3.2.0
CORES=3

sudo apt-get install -y python2.7-dev #python3-dev
sudo apt-get install -y build-essential git cmake pkg-config
sudo apt-get install -y libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install -y libxvidcore-dev libx264-dev
sudo apt-get install -y libgtk2.0-dev
sudo apt-get install -y libatlas-base-dev gfortran
cd ~

wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
pip install numpy

wget -O opencv.zip https://github.com/Itseez/opencv/archive/$CV_VERSION.zip
unzip opencv.zip
wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/$CV_VERSION.zip
unzip opencv_contrib.zip

cd ~/opencv-$CV_VERSION/
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D INSTALL_C_EXAMPLES=ON \
	-D INSTALL_PYTHON_EXAMPLES=ON \
	-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-$CV_VERSION/modules \
	-D BUILD_EXAMPLES=ON ..
make -j$CORES
sudo make install
sudo ldconfig

cd ~/.virtualenvs/cv/lib/python2.7/site-packages/
ln -s /usr/local/lib/python2.7/site-packages/cv2.so cv2.so
#cd /usr/local/lib/python3.4/site-packages/
#sudo mv cv2.cpython-34m.so cv2.so