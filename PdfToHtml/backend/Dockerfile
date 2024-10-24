# 使用 Python 3.9 官方映像作為基礎映像
FROM python:3.9-slim

# 設置工作目錄在容器內
WORKDIR /app

# 將依賴文件複製到容器內
COPY requirements.txt .

# 安裝依賴
RUN pip install fastapi uvicorn
RUN pip install --no-cache-dir -r requirements.txt

# 將本地代碼複製到容器內
COPY . .

# 定義容器啟動時運行的命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]