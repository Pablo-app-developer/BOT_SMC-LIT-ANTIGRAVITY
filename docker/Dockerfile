# Base image with Wine to run Windows apps (MT5) on Linux
# Using a community image or building from debian-slim + wine
FROM scottyhardy/docker-wine:latest

# Install Python and dependencies inside the Wine environment
# Note: This is complex because we need Windows Python installed via Wine
# For simplification in this template, we assume using a Linux python that talks to 
# a Windows MT5 via a bridge or using a custom Wine-Python setup.
# 
# However, the standard way for "headless" MT5 is often using the MetaAPI service 
# or a specific Windows Container.
#
# Below is a standard setup for a Linux based Python bot, assuming MT5 is handled via
# a connector or MetaAPI, OR attempting to run MT5.exe via Wine.

USER root

# Install python3 and pip for Linux (Logic layer)
RUN apt-get update && apt-get install -y python3 python3-pip

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the bot
CMD ["python3", "src/main.py"]
