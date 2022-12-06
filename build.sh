work_path=$(dirname $(readlink -f $0))
cd ${work_path}

target_path="$work_path/manager/static"
if [ -d "$target_path" ]; then
  echo -e "\e[33mClearing previous target directory $target_path...\e[0m"
  rm -r $target_path
fi

cd Frontend

cp index.html $target_path
cp index.js $target_path
touch $target_path/.gitkeep

echo -e "👌👌👌 \e[32mDeploy completed!\e[0m"
echo -e "▶️ Please run \e[32mstart.sh\e[0m to start the server." 
