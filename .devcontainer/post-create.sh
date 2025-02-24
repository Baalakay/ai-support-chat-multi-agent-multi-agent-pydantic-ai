#!/bin/bash
set -e

echo "Setting up development environment..."

# Install Rye (Modern package manager replacement for pip, requirements.txt, setup.py [**Rye uses pyproject.toml in Pythom projects] ) 
curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" RYE_TOOLCHAIN="$(which python)"  bash
export PATH="$HOME/.rye/shims:${PATH}"
echo 'source "$HOME/.rye/env"' >> ~/.bashrc
echo 'source "$HOME/.rye/env"' >> ~/.zshrc

# Setup ZSH plugins
echo "Setting up ZSH plugins..."
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
git clone https://github.com/zsh-users/zsh-completions ${ZSH_CUSTOM:-${ZSH:-~/.oh-my-zsh}/custom}/plugins/zsh-completions
git clone https://github.com/zsh-users/zsh-history-substring-search ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-history-substring-search
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

# Setup dotfiles
echo "Setting up dotfiles..."
git clone https://github.com/Baalakay/.dotfiles.git ~/.dotfiles
cd ~/.dotfiles
stow --adopt .
git reset --hard
cd $LOCAL_WORKSPACE_FOLDER

### Project Specific Settings ####

# Instals backend dependencies from pyproject.toml
rye sync

# Install frontend dependencies
cd frontend
npm install
cd ..

echo "Development environment setup complete!"

