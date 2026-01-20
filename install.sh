#!/bin/bash

# =================================================================
# INSTALADOR ATREYU v2.1 - SOLUCIÓN PERMISOS Y PM2
# =================================================================

APP_DIR="/opt/atreyu"
echo "🚀 Iniciando despliegue de Atreyu Servicios Digitales en $APP_DIR..."

# 1. Instalación de dependencias del sistema
sudo apt update
sudo apt install -y python3-pip python3-venv nginx nodejs npm sqlite3

# 2. Instalación global de PM2
sudo npm install -g pm2

# 3. Configuración de la aplicación
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR
cd $APP_DIR

# 4. Entorno virtual de Python
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pydantic python-multipart

# 5. Estructura de archivos y permisos para Nginx
mkdir -p static/uploads
sudo chown -R www-data:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR

# 6. Configuración de Nginx
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

# 7. Configuración de PM2 (Forzando el intérprete de Python para evitar error de Node)
pm2 delete atreyu-backend 2>/dev/null
pm2 start "$APP_DIR/venv/bin/python3 -m uvicorn api_backend:app --host 127.0.0.1 --port 8000" --name "atreyu-backend"
pm2 save

echo "✅ Instalación finalizada. Visita la IP de tu servidor."
