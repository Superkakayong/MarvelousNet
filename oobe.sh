work_path=$(dirname $(readlink -f $0))
cd ${work_path}

sh ./manager/prereq_backend.sh
ret=$?
if [ $ret -ne 0 ]; then
  echo -e "\e[31mFailed to install python backend files.\e[0m"
  exit $ret
fi

sh ./build.sh
ret=$?
if [ $ret -ne 0 ]; then
  echo -e "\e[31mFailed to build frontend stuffs.\e[0m"
  exit $ret
fi

