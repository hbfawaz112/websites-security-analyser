## ✅ STEP 0: Finishing the project implementation

Your project structure should look something like this:

```
ai-site-analyser/
├── app.py
├── requirements.txt
└── Dockerfile
```

---

## ✅ STEP 1: Write the Dockerfile

Create a `Dockerfile` in your project root:

```Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

In `app.py`, make sure you run app (flask) with:

```python
app.run(host="0.0.0.0", port=5000)
```

---

## ✅ STEP 2: Install AWS CLI & Docker

* Install Docker Desktop (enable **Linux containers**):
  [https://docs.docker.com/desktop/install/windows-install/](https://docs.docker.com/desktop/install/windows-install/)

* Install AWS CLI:
  [https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-windows.html](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-windows.html)

* Verify:

  ```bash
  docker --version
  aws --version
  ```

---

## ✅ STEP 3: Configure AWS CLI

```bash
aws configure
```

Enter:

* AWS Access Key ID
* AWS Secret Access Key
* Region (e.g. `eu-central-1`)
* Output format: `json`

---

## ✅ STEP 4: Build & Tag Docker Image

In your project directory:

```bash
docker build -t ai-site-analyser .
```

---

## ✅ STEP 5: Create ECR Repo

```bash
aws ecr create-repository --repository-name ai-site-analyser
```

---

## ✅ STEP 6: Authenticate Docker to ECR

```bash
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 861738660302.dkr.ecr.eu-central-1.amazonaws.com
```

> Replace the URI with your own account/repo URI if different.

---

## ✅ STEP 7: Tag and Push Image to ECR

```bash
docker tag ai-site-analyser:latest 861738660302.dkr.ecr.eu-central-1.amazonaws.com/ai-site-analyser:latest
docker push 861738660302.dkr.ecr.eu-central-1.amazonaws.com/ai-site-analyser:latest
```

---

## ✅ STEP 8: Create an ECS Cluster (Fargate)

1. Go to [ECS Console](https://console.aws.amazon.com/ecs)
2. Click **Clusters** > **Create Cluster**
3. Select **Networking only (Fargate)** → Next
4. Name your cluster (e.g., `ai-site-analyser`)
5. Click **Create**

---

## ✅ STEP 9: Create a Task Definition

1. Go to ECS > **Task Definitions** > Create new
2. Launch type: **Fargate**
3. Name it `ai-site-analyser`
4. Add container:

   * Name: `ai-site-analyser-app`
   * Image: `861738660302.dkr.ecr.eu-central-1.amazonaws.com/ai-site-analyser:latest`
   * Port mapping: `80`
5. Set CPU: `0.25 vCPU`, Memory: `512MB` or anything you want
6. Click **Create**

---

## ✅ STEP 10: Run the Task

1. Go to **Clusters** > your cluster > **Tasks** > **Run new task**
2. Launch type: **Fargate**
3. Choose the task definition: `ai-site-analyser-task`
4. Select a **public subnet**
5. Choose or create a **security group** that allows:

   * **Inbound Rule**: HTTP (TCP/80) from `0.0.0.0/0`
6. Click **Run Task**

---

## ✅ STEP 11: Access Your App

1. Go to the **running task** → **ENI (Elastic Network Interface)**
2. Click on it to view the **public IPv4 address**
3. Open in browser:

   ```
   http://<public-ip>/
   ```

# 🧰 Troubleshooting Summary
| Issue                                     | Cause / Description                                         | Fix / Solution                                                                                              |
| ----------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Docker daemon connection error            | Docker not running on your machine                          | Ensure **Docker Desktop** is running and try again                                                          |
| `aws` command not found                   | AWS CLI not installed or not in system `PATH`               | [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) and restart terminal |
| ECS task says "RUNNING" but URL times out | No public IP assigned or incorrect security group settings  | Enable **Auto-assign Public IP** when creating the service                                                  |
| App runs on `127.0.0.1` inside container  | Flask app only listens to localhost inside the container        | Use `host="0.0.0.0"` in `app.run()`                                                                         |
| Port blocked by firewall                  | Security group doesn't allow inbound traffic on port `5000` | Add inbound rule to allow `TCP:5000` from `0.0.0.0/0`                                                       |
| App crashes with missing modules          | Docker image doesn't have required packages installed       | Ensure all dependencies are in `requirements.txt` and installed in Dockerfile                               |
| Wrong AWS region or repository            | Tag or push fails                                           | Confirm correct region and repository name in ECR                                                           |
