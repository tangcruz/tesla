#!/bin/bash

# 构建 Docker 镜像
echo "Building Docker image..."
docker-compose build

# 運行測試
echo "Running tests..."
docker-compose run test

# 如果測試通過，運行 bot
if [ $? -eq 0 ]; then
    echo "Tests passed. Starting the bot..."
    docker-compose up bot
else
    echo "Tests failed. Please fix the issues before running the bot."
fi