# read input as arguments
log=`date +"%Y%m%d%H%M%S"`.log
# check the openai key if set in env
echo "Check the required env variables...." | tee -a $log
if [ -z "$OPENAI_KEY" ]; then
    echo "Please set your OPENAI_KEY first in environment variable, then execute the script." | tee -a $log
    exit 1
fi

# enter ther image description
read -p  "Enter your image description: " prompt && echo $prompt | tee -a $log
while [ `expr length "$prompt"` -lt 5 ]
do
    read -p "Please enter more detailed description of the image you want to generate: " prompt && echo $prompt | tee -a $log

done
# enter the image size
read -p "Please enter your image size (available opitons:1024, 512 or 256): " size && echo $size | tee -a $log

while [ "$size" != "256" -a "$size" != "512" -a "$size" != "1024" ]
do
    read -p "Unsatisfied image size: $size, please re-enter your image size (available opitons:1024, 512 or 256): " size && echo $size | tee -a $log
done

echo "Please wait the image to be generated..." | tee -a $log

curl https://api.openai.com/v1/images/generations \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $OPENAI_KEY" \
  -d '{
    "prompt": "'"$prompt"'",
    "n": 1,
    "size": "'"$size"'x'$size'"
  }' | tee -a $log

