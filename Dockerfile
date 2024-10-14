FROM python:3.9-slim

# Install Chrome, dependencies, and git
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    git \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip

# Set up the working directory
WORKDIR /app

# Clone the GitHub repository
ARG GITHUB_REPO_URL
RUN git clone ${GITHUB_REPO_URL} .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory
RUN mkdir -p /app/data

# Set environment variables
ENV CRUNCHBASE_EMAIL=bdm@bracketsltd.com
ENV CRUNCHBASE_PASSWORD=@Brackets23
ENV SCRAPE_LIMIT=10

# Run the script
CMD ["python", "main.py"]
