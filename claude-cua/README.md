### Setup

# Worker 1

```bash
./setup.sh  # configure venv, install development dependencies, and install pre-commit hooks
docker build . -t claude-cua:local
export ANTHROPIC_API_KEY=%your_api_key%
docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -v $(pwd)/computer_use_demo:/home/computeruse/computer_use_demo/
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -p 8085:8085 \
    -it claude-cua:local
```

# Worker 2

```
./setup.sh  # configure venv, install development dependencies, and install pre-commit hooks
docker build . -t claude-cua:local
export ANTHROPIC_API_KEY=%your_api_key%
docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -v $(pwd)/computer_use_demo:/home/computeruse/computer_use_demo/
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5901:5900 \
    -p 8502:8501 \
    -p 6081:6080 \
    -p 8081:8080 \
    -p 8086:8085 \
    -it claude-cua:local
```
