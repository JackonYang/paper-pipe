SCRIPT_DIR=$(cd $(dirname "$0") && pwd)

proto_dir=proto
python_out_dir=src/configs_pb2

rm -rf $python_out_dir/* && mkdir -p $python_out_dir

pushd $SCRIPT_DIR/../ > /dev/null


ls $proto_dir | grep ".proto" | xargs -I{} \
    protoc --proto_path="$proto_dir" \
        --python_out=${python_out_dir} \
        {}

popd > /dev/null
