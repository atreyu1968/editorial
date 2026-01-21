#!/bin/bash

# =================================================================
# INSTALADOR ATREYU v3.0 - VITE + REACT + FASTAPI
# =================================================================

APP_DIR="/opt/atreyu"
echo "🚀 Iniciando instalación de Atreyu Servicios Digitales..."

# 1. Dependencias del Sistema
sudo apt update
sudo apt install -y curl python3-pip python3-venv nginx sqlite3

# 2. Node.js 18.x (Necesario para Vite)
if ! command -v node &> /dev/null || [ $(node -v | cut -d'v' -f2 | cut -d'.' -f1) -lt 18 ]; then
    echo "📦 Instalando Node.js 18..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
fi

# 3. PM2 Global
sudo npm install -g pm2

# 4. Estructura de Carpetas
sudo mkdir -p $APP_DIR/src
sudo mkdir -p $APP_DIR/static/uploads
sudo chown -R $USER:$USER $APP_DIR

# 5. Backend (Python)
cd $APP_DIR
python3 -m venv venv
./venv/bin/pip install fastapi uvicorn pydantic python-multipart

# 6. Frontend (NPM)
if [ -f "package.json" ]; then
    npm install
else
    echo "❌ ERROR: package.json no encontrado en $APP_DIR"
    exit 1
fi

# 7. Configuración de Nginx
sudo bash -c "cat > /etc/nginx/sites-available/atreyu" <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /static {
        alias $APP_DIR/static;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/atreyu /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

# 8. Arranque con PM2
pm2 delete atreyu-backend atreyu-frontend 2>/dev/null
pm2 start "$APP_DIR/venv/bin/python3 -m uvicorn api_backend:app --host 127.0.0.1 --port 8000" --name "atreyu-backend"
pm2 start "npm run dev -- --host" --name "atreyu-frontend"
pm2 save

echo "✅ SISTEMA DESPLEGADO. Accede a través de tu IP."
