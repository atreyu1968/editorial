#!/bin/bash

# =================================================================
# INSTALADOR AUTOMÁTICO - ATREYU SERVICIOS DIGITALES v2.0
# =================================================================

echo "🚀 Iniciando despliegue profesional de Atreyu Servicios Digitales..."

# 1. Actualización y dependencias críticas
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx git curl nodejs npm sqlite3

# 2. Instalación de PM2 para gestión de procesos persistentes
sudo npm install -g pm2

# 3. Configuración del entorno Python
echo "🐍 Configurando entorno de Python y API..."
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pydantic python-multipart

# 4. Estructura de carpetas y permisos
mkdir -p static/uploads
chmod -R 775 static/

# 5. Configuración de Nginx como Proxy Inverso
echo "🌐 Configurando servidor web Nginx..."
sudo rm -f /etc/nginx/sites-enabled/default
sudo bash -c "cat > /etc/nginx/sites-available/atreyu" <<EOF
server {
    listen 80;
    server_name _;

    root $(pwd);
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /static {
        alias $(pwd)/static;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/atreyu /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# 6. Lanzamiento del servicio Backend con PM2
echo "⚙️ Iniciando base de datos SQLite y servidor API..."
pm2 start venv/bin/uvicorn --name "atreyu-backend" -- api_backend:app --host 127.0.0.1 --port 8000

# 7. Configuración de persistencia tras reinicios del hardware
pm2 save
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u $USER --hp $HOME

echo "✅ INSTALACIÓN COMPLETADA EXITOSAMENTE"
echo "Accede a través de la dirección IP de tu instancia de Ubuntu."
echo "IMPORTANTE: Sube tu archivo ASD.png a la carpeta /static"