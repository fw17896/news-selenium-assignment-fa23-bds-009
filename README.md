# Docker Selenium News Summarization API

## 1. Student news-source assignment

Registration number: **FA23-BDS-009**

Last three digits: `009` → 9

Formula: `(9 % 20) + 1 = 10`

Assigned source: **NPR** (serial number 10)  
Search domain: `npr.org`

## 2. What this project does

0. The home page `/` is a web page that shows the registration number **FA23-BDS-009**.
1. Receives a keyword at `GET /get`.
2. Uses Selenium + Google Chrome to search Bing (DuckDuckGo as fallback) for `site:npr.org <keyword>`; redirect links are decoded to the real URL.
3. Selects the first search result hosted on NPR.
4. Opens the article and extracts its readable text using Trafilatura.
5. Creates a short extractive summary using a local Python summarization module.
6. Returns the required JSON response.

The summarizer is extractive: it selects important sentences from the article. It does not require an API key or paid AI service.

## 3. Project structure

```text
news_selenium_assignment/
├── app.py
├── news_scraper.py
├── summarizer.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── README.md
└── tests/
    └── test_summarizer.py
```

## 4. Build and run locally with Docker

Install Docker Desktop (Windows/macOS) or Docker Engine (Linux), then open a terminal in this project folder.

Build the image:

```bash
docker build -t YOUR_DOCKERHUB_USERNAME/npr-news-api:v1 .
```

Run the container:

```bash
docker run -d --name npr-news-api -p 7000:7000 YOUR_DOCKERHUB_USERNAME/npr-news-api:v1
```

Check the service:

```bash
curl http://localhost:7000/health
```

Expected:

```json
{"status":"ok"}
```

Call the API:

```bash
curl "http://localhost:7000/get?keyword=artificial%20intelligence"
```

The API returns:

```json
{
  "registration": "FA23-BDS-009",
  "newssource": "NPR",
  "keyword": "artificial intelligence",
  "url": "https://www.npr.org/...",
  "summary": "..."
}
```

The exact article URL and summary depend on the search results at request time.

To view container logs:

```bash
docker logs -f npr-news-api
```

To stop and remove the container:

```bash
docker stop npr-news-api
docker rm npr-news-api
```

## 5. Push the image to Docker Hub

First create a public repository named `npr-news-api` on Docker Hub. Then:

```bash
docker login
docker push YOUR_DOCKERHUB_USERNAME/npr-news-api:v1
```

Replace `YOUR_DOCKERHUB_USERNAME` with your actual Docker Hub username. Submit the full image name, including `:v1`.

## 6. Deploy on an Ubuntu EC2 instance (if required)

Install Docker on the Ubuntu VM, then copy or clone this project and run:

```bash
docker build -t YOUR_DOCKERHUB_USERNAME/npr-news-api:v1 .
docker run -d --restart unless-stopped --name npr-news-api -p 7000:7000 YOUR_DOCKERHUB_USERNAME/npr-news-api:v1
```

In the EC2 security group, allow inbound **TCP port 7000** from the source range required by your instructor. For a public demonstration, use your instance public IP:

```text
http://YOUR_EC2_PUBLIC_IP:7000/get?keyword=artificial%20intelligence
```

Do not use a private `172.31.x.x` address from outside the EC2 network.

## 7. API specification

- Endpoint: `/get`
- Method: `GET`
- Port: `7000`
- Required query parameter: `keyword`
- Successful response fields: `registration`, `newssource`, `keyword`, `url`, `summary`
- Missing keyword: HTTP 400
- Search/extraction failure: HTTP 502

## 8. Technology choices

- **Python 3.12:** application and Selenium code (language used for Selenium: **Python**).
- **Google Chrome:** browser used in headless mode inside the container.
- **Selenium 4:** browser automation.
- **ChromeDriver:** downloaded during the Docker build to match the installed Google Chrome version.
- **Trafilatura:** extracts the main article text from the web page.
- **Flask:** exposes the REST API.
- **Custom extractive summarizer:** ranks and selects important sentences locally.

## 9. Notes / troubleshooting

- The image build needs internet access to install Chrome and its matching ChromeDriver. The running container needs internet access to reach Bing and NPR.
- Search engine layouts and publisher pages can change. If the search engine blocks automated requests, the scraper may return HTTP 502; inspect `docker logs npr-news-api`.
- Do not hard-code an article URL: the endpoint must search using the keyword each time.
- The Docker image is built for `linux/amd64`. On an ARM computer, build with `docker build --platform linux/amd64 ...` if your instructor's server expects AMD64.
- The assignment's example IP is a sample. Use the public IP assigned to your own VM if deploying to a server.
