work_path=$(dirname $(readlink -f $0))
cd ${work_path}
sudo python3 -m main --hostname 0.0.0.0 --port 80 3 3
