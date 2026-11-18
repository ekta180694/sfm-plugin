# Host this model on its own, like Control Tower:
#   docker build --build-arg SFM_SOURCE="git+https://github.com/<owner>/<repo>@v1.0.0" -t my-model .
#   docker run -p 8900:8900 my-model
FROM python:3.12-slim
ARG SFM_SOURCE
RUN apt-get update && apt-get install -y --no-install-recommends git libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir "sfm @ ${SFM_SOURCE}" -r requirements.txt
COPY . .
ENV SHOW_BUILD_TAB=0 SFM_UI_HOST=0.0.0.0
EXPOSE 8900
CMD ["python", "ui/server.py"]
