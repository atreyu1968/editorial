Atreyu Servicios Digitales - Gestión Editorial v2.0

Este es el sistema integral de gestión para Atreyu Servicios Digitales. Permite administrar sellos editoriales, autores, series, biblioteca, calendario operativo y analítica financiera con persistencia en SQLite.

🚀 Instalación en Servidor Ubuntu (Limpio)

Para desplegar la aplicación en un servidor recién contratado, sigue estos pasos:

Clonar el repositorio:

git clone [https://github.com/atreyu1968/editorial.git](https://github.com/atreyu1968/editorial.git)
cd editorial


Ejecutar el instalador automático:

chmod +x install.sh
sudo ./install.sh


🔐 Acceso y Seguridad

URL: http://[IP_DE_TU_SERVIDOR]

Contraseña maestra: 697457

📁 Estructura del Proyecto

index.html: Interfaz de usuario (React/Tailwind) con gestión de Drive y ROI.

api_backend.py: Servidor de datos (FastAPI) y base de datos (SQLite).

install.sh: Script de configuración automática (Nginx, Python, PM2).

static/: Carpeta para recursos. Recuerda subir tu logo ASD.png aquí.

static/uploads/: Almacenamiento automático de portadas y fotos.

🛠️ Mantenimiento

Reiniciar servicios: pm2 restart atreyu-backend

Ver logs en tiempo real: pm2 logs atreyu-backend

Base de Datos: El archivo editorial.db se crea automáticamente tras la primera ejecución.

© 2026 Atreyu Servicios Digitales
