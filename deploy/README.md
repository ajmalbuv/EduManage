# EduManage — Production Setup (Rootless Podman Quadlet + Systemwide Caddy)

Production deployment configuration for EduManage using rootless Podman Quadlets, systemd user services, and the host's systemwide Caddy reverse proxy (matching the setup from Jetso).

---

## Files

- `Containerfile`: Multi-stage production container build using pinned Python 3.12 and Astral `uv`.
- `entrypoint.sh`: Container startup entrypoint that auto-runs migrations, collects static files, and launches Gunicorn.
- `deploy/edumanage-app.container`: The Podman Quadlet systemd definition (port configurable here).
- `deploy/app.env.example`: The environment variables template for EduManage.
- `deploy/Caddyfile.example`: Systemwide Caddy reverse proxy snippet.
- `deploy.sh`: Builds the image and restarts the systemd user service.

---

## Correct Image Versions Used

| Component | Image | Version / Tag | Rationale |
| :--- | :--- | :--- | :--- |
| **Python Runtime** | `docker.io/library/python` | `3.12-slim-bookworm` | Pinned to Python 3.12 matching `pyproject.toml` requirement (`requires-python = "~=3.12.0"`). Debian Bookworm provides standard `glibc` required by `psycopg2-binary` pre-built wheels and C extensions without Alpine musl compatibility issues. |
| **Package Manager** | `ghcr.io/astral-sh/uv` | `0.5.26` | Pinned stable release for deterministic, ultra-fast virtualenv dependency installation directly from `uv.lock`. |

---

## One-Time Setup on Ubuntu

### 1. Enable User Lingering
Allows rootless Podman containers and systemd user services to start on boot and stay running after logout:
```bash
loginctl enable-linger $USER
```

### 2. Configure Environment
```bash
mkdir -p ~/.config/edumanage
cp deploy/app.env.example ~/.config/edumanage/app.env
chmod 600 ~/.config/edumanage/app.env

# Edit with your real SECRET_KEY, existing DATABASE_URL, and ALLOWED_HOSTS
nano ~/.config/edumanage/app.env
```

### 3. Install Quadlet File
```bash
mkdir -p ~/.config/containers/systemd
cp deploy/edumanage-app.container ~/.config/containers/systemd/

# (Optional) If you want a different port than 8100, edit PublishPort here:
# nano ~/.config/containers/systemd/edumanage-app.container
```

### 4. Configure Systemwide Caddy
Add to your host's systemwide Caddy configuration at `/etc/caddy/Caddyfile`:
```caddy
ajmalbasheer.duckdns.org {
    encode zstd gzip

    reverse_proxy 127.0.0.1:8100 {
        header_up Host {host}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
}
```
Reload the systemwide Caddy service:
```bash
sudo systemctl reload caddy
```

---

## Initial Build & First Run

Run `deploy.sh` to build the container image and start the user service:

```bash
chmod +x deploy.sh entrypoint.sh
./deploy.sh
```

---

## Django Management Tasks

### Create Django Superuser
```bash
podman exec -it edumanage-app python manage.py createsuperuser
```

### Run Django Shell
```bash
podman exec -it edumanage-app python manage.py shell
```

### Check Migration Status
```bash
podman exec -it edumanage-app python manage.py showmigrations
```

---

## Deploying / Updating After `git pull`

Whenever code is updated:

```bash
git pull && ./deploy.sh
```

---

## Service Management & Monitoring

```bash
# Check service status
systemctl --user status edumanage-app

# Follow live container logs
journalctl --user -u edumanage-app -f

# Check health check status
podman healthcheck run edumanage-app
```
