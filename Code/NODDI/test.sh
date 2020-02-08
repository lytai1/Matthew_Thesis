while getopts p: option
do
case "${option}"
in
p) DIR=${OPTARG};;
esac
done

echo $DIR
