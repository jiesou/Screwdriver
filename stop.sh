pkill -f "python -m server"
pkill -f "yarn dev"
fuser -k 3000/tcp
fuser -k 3001/tcp