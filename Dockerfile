# Python 3.11をベースイメージとして使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 静的ファイルを収集
RUN python manage.py collectstatic --noinput

# ログ用のディレクトリを作成
RUN mkdir -p /app/logs

# ポート8000を公開
EXPOSE 8000

# Datadog APM環境変数を設定
ENV DD_ENV=production
ENV DD_SERVICE=django-datadog-app
ENV DD_VERSION=1.0.0
ENV DD_TRACE_ENABLED=true
ENV DD_PROFILING_ENABLED=true
ENV DD_LOGS_INJECTION=true
ENV DD_DJANGO_INSTRUMENT_TEMPLATES=true
ENV DD_DJANGO_INSTRUMENT_DATABASES=true

# ddtrace-run でgunicornを起動してAPMを有効化
CMD ["ddtrace-run", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "datadog_app.wsgi:application"]
