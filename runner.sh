PY=python3

trap 'pkill --parent $$' EXIT

run_bg(){
    (
        while true
        do
            echo "$1 starting"
            $1 && {
                echo "$1 success, waiting $2"
                sleep $2
            } || {
                echo "$1 failure, waiting $3"
                sleep $3
            }
        done
    ) &
}

run_bg "$PY unicheck.py" 10 10
run_bg "$PY downloader.py" 10 10

echo "Press ctrl-c to stop"
while true
do
    sleep 1d
done
