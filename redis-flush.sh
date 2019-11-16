
if [ $# -ne 1 ]; then
    echo not really
    exit 1
fi

redis-cli FLUSHALL

