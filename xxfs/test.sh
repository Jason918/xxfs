pkill -f python
python naming_server.py &
sleep 2
rm s*/*
python storage_server.py 127.0.0.1 20001 ./s1 100 &
python storage_server.py 127.0.0.1 20002 ./s2 100 &
python storage_server.py 127.0.0.1 20003 ./s3 100 &
python storage_server.py 127.0.0.1 20004 ./s4 100 &
python storage_server.py 127.0.0.1 20005 ./s5 100 &
# python storage_server.py 127.0.0.1 20006 ./s6 100 &
# python storage_server.py 127.0.0.1 20007 ./s7 100 &
# python storage_server.py 127.0.0.1 20008 ./s8 100 &
# sleep 1
# python xx.py add project_doc.pdf /a
# ./xx.py add config.py /t
# ./xx.py append /t/config.py test.sh
# sleep 2

# pkill -f 20005 
