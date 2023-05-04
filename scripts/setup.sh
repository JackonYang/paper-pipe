SCRIPT_DIR=$(cd $(dirname "$0") && pwd)

# run brew install if this is MacOS
echo "install protobuf"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt install protobuf-compiler
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install protobuf
else
    echo "unknown os type: $OSTYPE"
fi


function clone_repo() {
    local repo_url=$1
    local repo_dir=$2
    local force=${3:-false}
    if [ "$force" = "true" ]; then
        echo "force clone repo $repo_url to $repo_dir"
        rm -rf $repo_dir
    fi
    if [ ! -d "$repo_dir" ]; then
        git clone $repo_url $repo_dir
    else
        echo "repo $repo_dir already exists"
    fi
}

home_dir=$(cd ~ && pwd)
data_root_dir=$(realpath "$home_dir/.cache-paper-reading")

mkdir -p $data_root_dir

clone_repo \
    git@github.com:JackonYang/paper-crawler-cache.git \
    $data_root_dir/crawler-cache

clone_repo \
	git@github.com:JackonYang/paper-extra-data.git \
    $data_root_dir/paper-extra-data

# clone_repo \
# 	git@github.com:JackonYang/paper-repo.git \
#     paper-repo

pip install -r requirements.txt
