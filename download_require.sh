# adjust to latest version (see www.mkgmap.org.uk)
MKGMAP="mkgmap-r4922" 
SPLITTER="splitter-r645"

if [[ $OSTYPE == 'linux'* ]]; then
    sudo apt update
    sudo apt upgrade
    sudo apt install curl
    sudo apt install python3-pip
    sudo apt install openjdk-13-jre-headless
    sudo apt install unzip
fi

if [ ! -d "mkgmap" ]; then
    curl -L -o "mkgmap.zip" "https://www.mkgmap.org.uk/download/${MKGMAP}.zip"  
    unzip "mkgmap.zip"
    rm "mkgmap.zip"
    mv ${MKGMAP} mkgmap
fi

if [ ! -d "splitter" ]; then
    curl -L -o "splitter.zip" "https://www.mkgmap.org.uk/download/${SPLITTER}.zip"   
    unzip "splitter.zip"
    rm "splitter.zip"
    mv ${SPLITTER} splitter
fi

if [ ! -f "sea.zip" ]; then
    curl -L -o "sea.zip" "http://osm.thkukuk.de/data/sea-latest.zip"
fi

pip install -r requirements.txt
