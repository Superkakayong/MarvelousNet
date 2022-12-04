work_path=$(dirname $(readlink -f $0))
cd ${work_path}

# code for backend prerequisite
echo -e "🧩🧩🧩 \e[32mUpdating Ubuntu software distribution...\e[0m"
sudo apt-get update -y
ret=$?
if [ $ret -ne 0 ]; then
  echo -e "\e[31mFailed to update software distribution.\e[0m"
  exit $ret
fi

echo -e "🧩🧩🧩 \e[32mInstalling python3 with pip3...\e[0m"
sudo apt-get install -y python3-pip
ret=$?
if [ $ret -ne 0 ]; then
  echo -e "\e[31mFailed to install python3 with pip3.\e[0m"
  exit $ret
fi

echo -e "🧩🧩🧩 \e[32mInstalling library used to handle JPEG...\e[0m"
sudo apt-get install -y libjpeg-dev zlib1g-dev
ret=$?
if [ $ret -ne 0 ]; then
  echo -e "\e[31mFailed to install libjpeg-dev.\e[0m"
  exit $ret
fi

echo -e "🧩🧩🧩 \e[32mInstalling torch and torch visions...\e[0m"
pip3 --no-cache-dir install torch==1.10.0+cpu torchvision==0.11.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
ret=$?
if [ $ret -ne 0 ]; then
  echo -e "\e[31mFailed to install torchvision.\e[0m"
  exit $ret
fi

echo -e "🧩🧩🧩 \e[32mInstalling remaining python environments...\e[0m"
pip3 install -r requirements.txt
ret=$?
if [ $ret -ne 0 ]; then
  echo -e "\e[31mFailed to python environments.\e[0m"
  exit $ret
fi
