workspace=~/linycs
software=~/linycs/softwares

if [ ! -d "$software" ]; then
    mkdir -p $software
fi

cd $software

# ! necessary apt software
# update command -> function
install_apt_software() {
    # if current user is root, then set apt_command to "apt"
    if [ "$EUID" -eq 0 ]; then
        apt_command="apt"
    else
        apt_command="sudo apt"
    fi

    $apt_command update && $apt_command install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        ffmpeg \
        git \
        libegl1 \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libfuse2 \
        ninja-build \
        pkg-config \
        wget \
        ssh \
        npm \
        tmux
    # clean up
    $apt_command clean
}

config_pinyin() {
    echo "! 不建议直接脚本安装拼音，最好装适合自己机器的"
    # # pinyin
    # install_apt_software \
    #         fcitx5 \
    #         fcitx5-chinese-addons \
    #         fcitx5-module-cloudpinyin \
    #         fcitx5-pinyin-gui
    # im-config -n fcitx5
    # # * then reboot or login again to make fcitx5 work
    # # ? check [web](https://modelers.csdn.net/69a78d5c7bbde9200b9d1d00.html) to view detailed steps.
    # fcitx5-configtool
    # echo "GTK_IM_MODULE DEFAULT=fcitx5
    # QT_IM_MODULE  DEFAULT=fcitx5
    # XMODIFIERS    DEFAULT=@im=fcitx5" >> ~/.profile
    # # * then reboot or login again to make fcitx5 work
    # fcitx5 -d
}

# ! git related
config_git() {
    git config --global user.name "linycs"
    git config --global user.email "lnykyks@gmail.com"
    git config --list
}

# ! ssh
config_ssh() {
    touch ~/.ssh/config
    echo "Host github.com
        HostName github.com
        User git
        #IdentityFile ~/.ssh/TODO" >> ~/.ssh/config
    echo "Host gitee.com
        HostName gitee.com
        User git
        #IdentityFile ~/.ssh/TODO" >> ~/.ssh/config
}

# TODO after configure ssh key & git, run: `ssh -T git@github.com`

# ! work related 
config_softwares() {
    # vscode
    wget https://vscode.download.prss.microsoft.com/dbazure/download/stable/1b6a188127eeaf9194f945eb6eb89a657e93c54c/code_1.130.0-1784734578_amd64.deb
    sudo dpkg -i code*.deb

    # install extensions in vscode
    # list: python, tabout, better comments, docker, remote-ssh, remote development, git graph

    ## microsoft edge
    wget https://packages.microsoft.com/repos/edge/pool/main/m/microsoft-edge-stable/microsoft-edge-stable_150.0.4078.105-1_amd64.deb?brand=M102
    sudo dpkg -i microsoft*.deb
    ## feishu
    wget https://lf3-ug-sign.feishucdn.com/ee-appcenter/6e3610b5/Feishu-linux_x64-7.66.11.deb?lk3s=fb957577&x-expires=1785222585&x-signature=AxCvVahhUeUOqIkvB4v1Eihe358%3D
    sudo dpkg -i Feishu*.deb

    # snipaste
    wget https://download.snipaste.com/archives/Snipaste-2.11.3-x86_64.AppImage
}

# ! ai tools
# 读取 api_key
read -p "请输入你的API_KEY: " api_key

config_cc() {
    sudo npm install -g @anthropic-ai/claude-code
    cc_config_path=~/.claude/settings.json
    if [ ! -d ~/.claude ]; then
        mkdir -p ~/.claude
    fi
    if [ ! -f $cc_config_path ]; then
        touch $cc_config_path
    fi

    echo '{
    "model": "claude-opus-4-8",
    "env": {
        "ANTHROPIC_BASE_URL": "https://switchbot.work",
        "ANTHROPIC_AUTH_TOKEN": "'"$api_key"'",
        "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": "1",
        "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-8",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-sonnet-5",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-haiku-4-5-20251001",
        "CLAUDE_CODE_DISABLE_1M_CONTEXT": "1"
    }
}' > $cc_config_path
}

## codex
config_codex() {
    sudo npm install -g @openai/codex
    codex_config_path=~/.codex/config.toml
    if [ ! -d ~/.codex ]; then
        mkdir -p ~/.codex
    fi
    if [ ! -f $codex_config_path ]; then
        touch $codex_config_path
    fi
    echo 'model_provider = "switchbot_ai"
model = "gpt-5.5"
model_reasoning_effort = "xhigh"
preferred_auth_method = "apikey"

[model_providers.switchbot_ai]
name = "switchbot_ai"
base_url = "https://switchbot.work/v1"
wire_api = "responses"
requires_openai_auth = true' > $codex_config_path

    codex_api_path=~/.codex/auth.json
    if [ ! -f $codex_api_path ]; then
        touch $codex_api_path
    fi
    echo '{
    "OPENAI_API_KEY": "'"$api_key"'"
}' > $codex_api_path
}

# 配置软件
config_softwares
install_apt_software
# 配置 ssh, git
config_git
config_ssh
# 安装 cc
config_cc
# 安装 codex
config_codex
