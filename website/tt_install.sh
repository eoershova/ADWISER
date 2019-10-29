mkdir tt; cd tt
wget https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tree-tagger-linux-3.2.2.tar.gz
wget https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tagger-scripts.tar.gz
wget https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/install-tagger.sh
wget https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/english-bnc.par.gz
sudo chmod 777 install-tagger.sh
./install-tagger.sh