FROM rofrano/nyu-devops-base:sp25

USER root

WORKDIR /app

# Copy Pipfiles first for dependency caching
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip pipenv && \
    pipenv install --system --dev && \
    pip install flask-cors behave webdriver-manager

RUN pip install flask-cors
# Copy the rest of your project (including tests)
COPY . /app

# Install user mode tools
COPY .devcontainer/scripts/install-tools.sh /tmp/
RUN cd /tmp && bash ./install-tools.sh

# --- Add Node.js & npm for building React frontend ---
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean

# Build React frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Set back to Flask app directory
WORKDIR /app

RUN apt-get update && \
    apt-get install -y wget gnupg2 && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean
