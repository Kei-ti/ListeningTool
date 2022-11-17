# ListeningTool

Work on Linux, Mac, and Windows.

## Installation 

```
python version >= 3.8
conda install numpy
```

## Step. 1
Create a wavfile list `configure/list/XXX.list` for listening test by yourself or using `bin/python/list.py`.

For exsample: 
```
python bin/python/list.py --MOS -d data/wav/A data/wav/B -e wav -o configure/list/MOS_sample_audio.list
python bin/python/list.py --XAB -d data/wav/X data/wav/A data/wav/B -e wav -o configure/list/XAB_sample_audio.list
```

## Step. 2
Create a json list `configure/YYY.json` for each listener and evaluation by using `bin/python/configure.py`.

For exsample: 
```
python ./bin/python/configure.py -l configure/list/XAB_sample_audio.list -d X,A,B -c Similarity:A,Fair,B Quality:A,Fair,B -j configure/XAB_person1.json
python ./bin/python/configure.py -l configure/list/MOS_sample_audio.list -d X -c Similarity:1,2,3,4,5 Quality:1,2,3,4,5 -j configure/MOS_person1.json
```

The option `-l` indicates a wavfile list generated in step. 1.

## Step. 3
Create `ZZZ.html` by using `bin/python/html_index.py`.

For example:
```
python ./bin/python/html_index.py -d configure -o ZZZ.html
```

The option `-d` specifies the directory to search json files generated in step. 2.

## Step. 4
Launch listening test server with port `PORT`.

Then, open the displayed URL + `ZZZ.html` in your browser (recommendation: chrome, safari).

For example:
```
python ./bin/python/server.py --port 8000
-> http://127.0.0.1:8000/ZZZ.html
```

Warning: For Windows, the oprion `--thread` is required because the ForkingMixIn class is not available on Windows because there is no fork() on Windows.
https://docs.python.org/3.6/library/socketserver.html#socketserver.ForkingMixIn

## Step. 5 (After listening)
Look a result directory, `./result`


