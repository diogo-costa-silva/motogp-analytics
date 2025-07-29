# Configuração do Ambiente no macOS

## 0. Instalar o Homebrew no macOS

Abre o terminal e executar o seguinte comando:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## 1. Instalar o pyenv (se ainda não estiver instalado):

```bash
brew update
brew install pyenv
```

Depois, no teu ~/.zshrc (ou ~/.bashrc), adiciona:

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

Fecha e reabre o terminal ou faz source ~/.zshrc.


## 2. Instalar a versão de Python que preferires (por exemplo 3.10.9):

```bash
pyenv install 3.10.9
pyenv global 3.10.9  # ou pyenv local 3.10.9 se quiseres para o diretório

```

Verifica com python --version ou pyenv version.


## 3. Criar venv dentro do projeto:

Dentro da pasta onde vais ter o projeto, por exemplo MotoGP-Project/, faz:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

(Se o Python do pyenv estiver configurado como “principal”, vai usar a versão que definiste.)

## 4. Instalar bibliotecas essenciais:

```bash
pip install pandas numpy jupyter requests sqlalchemy
```

Posteriormente, podes adicionar requests, sqlalchemy, etc., conforme fores precisando.

## 5. Cria um ficheiro requirements.txt para registar as libs

```bash
pip freeze > requirements.txt
```
