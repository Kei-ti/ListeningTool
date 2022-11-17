echo "1. prepare listfiles and wavfiles"
python bin/python/list.py --XAB -d data/wav/X data/wav/A data/wav/B -e wav -o configure/list/XAB_sample_audio.list
python bin/python/list.py --XAB -d data/img/X data/img/A data/img/B -e jpg -o configure/list/XAB_sample_image.list
python bin/python/list.py --XAB -d data/img/X data/wav/A data/wav/B -e jpg wav -o configure/list/XAB_sample_cross.list
python bin/python/list.py --AB -d data/wav/A data/wav/B -e wav -o configure/list/AB_sample_audio.list
python bin/python/list.py --AB -d data/img/A data/img/B -e jpg -o configure/list/AB_sample_image.list
python bin/python/list.py --MOS -d data/wav/A data/wav/B -e wav -o configure/list/MOS_sample_audio.list
python bin/python/list.py --MOS -d data/img/X data/img/A data/img/B -e jpg -o configure/list/MOS_sample_image.list


echo "2. create a configure file"
python ./bin/python/configure.py -l configure/list/XAB_sample_audio.list -d X,A,B -c Similarity:A,Fair,B Quality:A,Fair,B -j configure/XAB_person1.json
python ./bin/python/configure.py -l configure/list/XAB_sample_image.list -d X,A,B -c Similarity:A,Fair,B Quality:A,Fair,B -j configure/XAB_person2.json
python ./bin/python/configure.py -l configure/list/XAB_sample_cross.list -d X,A,B -c Similarity:A,Fair,B Quality:A,Fair,B -j configure/XAB_person3.json
python ./bin/python/configure.py -l configure/list/AB_sample_audio.list -d A,B -c Similarity:A,Fair,B Quality:A,Fair,B -j configure/AB_person1.json
python ./bin/python/configure.py -l configure/list/AB_sample_image.list -d A,B -c Similarity:A,Fair,B Quality:A,Fair,B -j configure/AB_person2.json
python ./bin/python/configure.py -l configure/list/MOS_sample_audio.list -d X -c Similarity:1,2,3,4,5 Quality:1,2,3,4,5 -j configure/MOS_person1.json
python ./bin/python/configure.py -l configure/list/MOS_sample_image.list -d X -c Similarity:1,2,3,4,5 Quality:1,2,3,4,5 -j configure/MOS_person2.json

echo "3. create an index html page, based on files of configure"
python ./bin/python/html_index.py -d configure -o index.html

echo "4. launch CGI server"
python ./bin/python/server.py --port 8000 --thread

echo "5. after evaluations, look at result dir"

