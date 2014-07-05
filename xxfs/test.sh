pkill -f python
python naming_server.py &
sleep 2
python storage_server.py 127.0.0.1 20001 ./s1 100 &
python storage_server.py 127.0.0.1 20002 ./s2 100 &
python storage_server.py 127.0.0.1 20003 ./s3 100 &
python storage_server.py 127.0.0.1 20004 ./s4 100 &