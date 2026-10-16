#!/usr/bin/env bash
set -euo pipefail

echo "📦 Building EduManage image..."
podman build -t localhost/edumanage:latest .

echo "🔄 Reloading systemd & restarting edumanage-app..."
systemctl --user daemon-reload
systemctl --user restart edumanage-app.service

echo "✅ Deployment complete!"
