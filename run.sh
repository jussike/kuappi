while :
do
    DATE=`date '+%Y-%m-%d %H:%M:%S'`
    echo "Kuappi service started at ${DATE}" | systemd-cat -p info
    python3 -u kuappi.py
done
