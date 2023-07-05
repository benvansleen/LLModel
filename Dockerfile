FROM openmodelica/openmodelica:v1.21.0-gui


RUN apt-get update && apt-get install -y \
omlibrary \
python3.10 \
python3-dev \
curl \
qtwayland5 \
python-is-python3


RUN groupadd -r om && useradd -m -r -u 1000 -g om om
USER om
ENV USER=om
ENV QT_QPA_PLATFORM=wayland


RUN curl -sSL https://install.python-poetry.org | python3 -
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc


RUN mkdir -p /home/om/llmodel
RUN mkdir -p /home/om/tmp
WORKDIR /home/om/llmodel
ADD pyproject.toml .
RUN $HOME/.local/bin/poetry config virtualenvs.in-project false
RUN $HOME/.local/bin/poetry install
