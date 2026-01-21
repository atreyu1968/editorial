#!/bin/bash

# =================================================================
# INSTALADOR ATREYU v2.7 - REVISIÓN TOTAL
# =================================================================

APP_DIR="/opt/atreyu"
echo "🚀 Iniciando despliegue de Atreyu Servicios Digitales v2.7..."

# 1. Dependencias del sistema
sudo apt update
sudo apt install -y python3-pip python3-venv nginx sqlite3

# 2. Configuración de carpetas
sudo mkdir -p $APP_DIR/static/uploads
sudo chown -R $USER:$USER $APP_DIR

# 3. Entorno de Python y Librerías
cd $APP_DIR
python3 -m venv venv
./venv/bin/pip install fastapi uvicorn pydantic python-multipart

# 4. Permisos para Nginx (Usuario www-data)
sudo chown -R www-data:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

# 5. Nginx Config
sudo bash -c "cat > /etc/nginx/sites-available/atreyu" <<EOF
server {
    listen 80;
    server_name _;
    root $APP_DIR;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
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

# 6. PM2 - Gestión de proceso
sudo npm install -g pm2
pm2 delete atreyu-backend 2>/dev/null
pm2 start "$APP_DIR/venv/bin/python3 -m uvicorn api_backend:app --host 127.0.0.1 --port 8000" --name "atreyu-backend"
pm2 save

echo "✅ SISTEMA ATREYU v2.7 DESPLEGADO CORRECTAMENTE"
