# Docker Selenium News Summarization API

## 1. Student News-Source Assignment

* **Registration Number:** FA23-BDS-009
* **Last Three Digits:** 009 → 9
* **Assignment Formula:** (9 % 20) + 1 = 10
* **Assigned News Source:** NPR (Serial Number 10)
* **Search Domain:** npr.org

## 2. Project Overview

This project is a Dockerized News Summarization REST API developed using Python, Flask, Selenium, and Google Chrome.

The application searches NPR for a user-provided keyword, opens the first relevant article, extracts its main text, and generates a short extractive summary.

### How It Works

1. The home page (`/`) displays the student's registration number: **FA23-BDS-009**.
2. The API receives a keyword through the `GET /get` endpoint.
3. Selenium launches Google Chrome in headless mode and searches NPR's internal search page.
4. The scraper selects the first relevant NPR article.
5. Trafilatura extracts the readable article content.
6. A custom local Python summarizer selects important sentences.
7. Flask returns the article URL and summary in JSON format.

The summarizer works locally and does not require an external AI API key or paid service.

## 3. Project Structure

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
    ├── test_api_and_scraper.py
    └── test_summarizer.py
```

## 4. Technologies Used

* **Python 3.12:** Main programming language.
* **Flask:** REST API development.
* **Selenium 4:** Browser automation and news searching.
* **Google Chrome:** Headless browser.
* **ChromeDriver:** Connects Selenium with Google Chrome.
* **Trafilatura:** Extracts readable article text.
* **Custom Extractive Summarizer:** Selects important sentences from the article.
* **Docker:** Containerization and deployment.

## 5. API Specification

| Property        | Details   |
| --------------- | --------- |
| API Endpoint    | `/get`    |
| HTTP Method     | GET       |
| Port            | 7000      |
| Query Parameter | `keyword` |
| News Source     | NPR       |
| Search Domain   | npr.org   |

### Successful Response

The API returns the following JSON fields:

* `registration`
* `newssource`
* `keyword`
* `url`
* `summary`

Example:

```json
{
  "registration": "FA23-BDS-009",
  "newssource": "NPR",
  "keyword": "technology",
  "url": "https://www.npr.org/...",
  "summary": "Article summary appears here."
}
```

The actual article URL and summary depend on the search results available when the API is called.

### Error Handling

* Missing keyword: HTTP 400
* Search or article extraction failure: HTTP 502

## 6. Build and Run Locally with Docker

Make sure Docker is installed and running.

### Build the Docker Image

```bash
docker build -t fatimawaseemdevops/npr-news-api:v1 .
```

### Run the Container

```bash
docker run -d --name npr-news-api -p 7000:7000 fatimawaseemdevops/npr-news-api:v1
```

### Open the Landing Page

```text
http://localhost:7000/
```

The landing page displays the registration number **FA23-BDS-009**.

### Test the API

```bash
curl "http://localhost:7000/get?keyword=technology"
```

### View Container Logs

```bash
docker logs -f npr-news-api
```

### Stop and Remove the Container

```bash
docker stop npr-news-api
docker rm npr-news-api
```

## 7. Docker Hub Deployment

The Docker image is published on Docker Hub.

* **Docker Hub Username:** fatimawaseemdevops
* **Repository:** npr-news-api
* **Image Tag:** v1

Full image name:

```text
fatimawaseemdevops/npr-news-api:v1
```

Pull the image:

```bash
docker pull fatimawaseemdevops/npr-news-api:v1
```

Run the downloaded image:

```bash
docker run -d --name npr-news-api -p 7000:7000 fatimawaseemdevops/npr-news-api:v1
```

## 8. Deployment on AWS EC2

The application is deployed on an Ubuntu EC2 instance.

### Docker Run Command

```bash
docker run -d --restart unless-stopped --name npr-news-api -p 7000:7000 fatimawaseemdevops/npr-news-api:v1
```

### EC2 Security Group

Allow inbound traffic on:

* **Type:** Custom TCP
* **Port:** 7000
* **Source:** As required for public access and instructor evaluation.

### Public Application URLs

Landing page:

```text
http://13.62.166.166:7000/
```

API endpoint:

```text
http://13.62.166.166:7000/get?keyword=technology
```

The public IP must be accessible and the EC2 security group must allow inbound TCP traffic on port 7000.

## 9. Testing

The project includes automated tests:

* `tests/test_api_and_scraper.py`
* `tests/test_summarizer.py`

These tests cover API behavior, scraper-related functionality, and summarization logic.

## 10. Notes and Troubleshooting

* The Docker image requires internet access during the build process to install dependencies, Google Chrome, and ChromeDriver.
* The running container requires internet access to search NPR and retrieve articles.
* Selenium uses headless Chrome, so no graphical browser window is required.
* ChromeDriver is installed to match the Google Chrome version.
* If the API returns HTTP 502, inspect the container logs:

```bash
docker logs npr-news-api
```

* Search results and website layouts may change over time.
* The Docker image is built for `linux/amd64`.

---

**Student Registration:** FA23-BDS-009
**Assigned News Source:** NPR
**Selenium Programming Language:** Python
**Docker Image:** fatimawaseemdevops/npr-news-api:v1
**Application Port:** 7000
