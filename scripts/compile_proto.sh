SCRIPT_DIR=$(cd $(dirname "$0") && pwd)

proto_dir=proto
python_out_dir=src/configs_pb2

rm -rf $python_out_dir/* && mkdir -p $python_out_dir

pushd $SCRIPT_DIR/../ > /dev/null


protoc --proto_path="$proto_dir" \
    --python_out=${python_out_dir} \
    "$proto_dir"/*.proto

# use gsed if exists
if [ -x "$(command -v gsed)" ]; then
    sed=gsed
else
    sed=sed
fi

$sed -i -e 's/^import [^ ]*_pb2/from . \0/' $python_out_dir/*_pb2.py

popd > /dev/null
