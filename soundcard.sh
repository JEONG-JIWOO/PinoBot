printf   "\n\n [step 2], Install Driver"
git clone https://github.com/HinTak/seeed-voicecard #HinTak's repository is more stable than official
cd ./seeed-voicecard || { prirntf "cd seeed-voicecard fail "; exit 127;}
sudo bash ./install.sh || { prirntf "\n\n cd seeed-voicecard install fail , try install use --compat-kernel" ; sudo bash ./install.sh --compat-kernel ;}
cd ..
rm -rf ./seeed-voicecard || { prirntf "remove seeed-voicecard fail "; exit 127;}