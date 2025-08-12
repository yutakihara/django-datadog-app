# Django + Datadog Application

Azure Container Appsにデプロイされる、Datadog監視機能を統合したDjangoアプリケーションです。

## 🚀 機能

- **Django Web アプリケーション**: Datadog統合のデモ用Webアプリ
- **Datadog監視**: カスタムメトリクス、ログ、ヘルスチェック
- **レスポンシブUI**: Bootstrap5を使用したモダンなUI
- **Docker化**: コンテナベースでのデプロイ
- **CI/CD**: GitHub Actionsによる自動デプロイ

## 📊 エンドポイント

- `/` - ホームページ
- `/metrics/` - アプリケーションメトリクス
- `/api/test/` - APIテストエンドポイント
- `/health/` - ヘルスチェックエンドポイント

## 🛠️ ローカル開発

### 前提条件

- Python 3.11+
- Docker (オプション)

### セットアップ

```bash
# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements.txt

# データベースのマイグレーション
python manage.py migrate

# 開発サーバーの起動
python manage.py runserver
```

### 環境変数

`.env` ファイルで以下の環境変数を設定してください：

```env
DEBUG=True
SECRET_KEY=your-secret-key
DD_API_KEY=your-datadog-api-key  # オプション
DD_APP_KEY=your-datadog-app-key  # オプション
```

## 🐳 Docker

### ローカルでのDockerビルド

```bash
docker build -t django-datadog-app .
docker run -p 8000:8000 django-datadog-app
```

## ☁️ Azure Container Apps デプロイ

### 前提条件

1. Azure CLI のインストール
2. Azure Container Registry (ACR) の作成
3. Azure Container Apps 環境の作成

### Azure リソースの作成

```bash
# リソースグループの作成
az group create --name django-datadog-rg --location japaneast

# Container Registry の作成
az acr create --resource-group django-datadog-rg \
  --name yourdjangoregistry --sku Basic

# Container Apps 環境の作成
az containerapp env create \
  --name django-env \
  --resource-group django-datadog-rg \
  --location japaneast

# Container App の作成
az containerapp create \
  --name django-datadog-app \
  --resource-group django-datadog-rg \
  --environment django-env \
  --image yourdjangoregistry.azurecr.io/django-datadog-app:latest \
  --target-port 8000 \
  --ingress 'external' \
  --registry-server yourdjangoregistry.azurecr.io \
  --env-vars DEBUG=False SECRET_KEY=your-secret-key
```

### GitHub Actions CI/CD

リポジトリで以下のシークレットを設定してください：

- `AZURE_CREDENTIALS`: Azure サービスプリンシパルのJSON
- `DJANGO_SECRET_KEY`: Django のシークレットキー
- `DD_API_KEY`: Datadog APIキー (オプション)
- `DD_APP_KEY`: Datadog アプリケーションキー (オプション)
- `ALLOWED_HOST`: 許可するホスト名

#### Azure サービスプリンシパルの作成

```bash
az ad sp create-for-rbac --name "django-datadog-sp" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/django-datadog-rg \
  --sdk-auth
```

### `.github/workflows/deploy.yml` の設定

デプロイワークフローで以下の環境変数を更新してください：

```yaml
env:
  AZURE_CONTAINER_REGISTRY: "yourdjangoregistry"
  CONTAINER_APP_NAME: "django-datadog-app"
  RESOURCE_GROUP: "django-datadog-rg"
```

## 📈 Datadog 統合

Datadog統合を有効にするには：

1. [Datadog](https://app.datadoghq.com/) でAPIキーを取得
2. 環境変数 `DD_API_KEY` と `DD_APP_KEY` を設定
3. アプリケーションを再起動

### 送信されるメトリクス

- `django.page.views` - ページビュー数
- `django.app.cpu_usage` - CPU使用率
- `django.app.memory_usage` - メモリ使用率
- `django.app.request_count` - リクエスト数
- `django.app.error_rate` - エラー率
- `django.app.response_time` - 応答時間
- `django.api.requests` - API リクエスト数
- `django.api.errors` - API エラー数

## 🔧 トラブルシューティング

### よくある問題

1. **静的ファイルが見つからない**: `python manage.py collectstatic` を実行
2. **Datadog メトリクスが送信されない**: API キーが正しく設定されているか確認
3. **Container Apps でアプリが起動しない**: ログを確認し、環境変数をチェック

### ログの確認

```bash
# Azure Container Apps のログを確認
az containerapp logs show --name django-datadog-app \
  --resource-group django-datadog-rg --follow
```

## 📝 ライセンス

MIT License

## 🤝 コントリビューション

プルリクエストやイシューを歓迎します！

## 📞 サポート

質問やサポートが必要な場合は、GitHubのIssuesを使用してください。
