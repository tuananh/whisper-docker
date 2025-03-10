FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu24.04
WORKDIR /root
RUN apt-get update -y && apt-get install -y python3-pip  python3-venv --no-install-recommends

RUN python3 -m venv venv
ENV PATH="/root/venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

# Pre-download the model during build
RUN python3 -c "from faster_whisper.utils import download_model; download_model('large-v3')"

COPY main.py ./

EXPOSE 4444
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4444"] 