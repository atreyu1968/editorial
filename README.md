Atreyu Servicios Digitales - Gestión Editorial v2.0Consola profesional para la gestión de sellos, autores y analítica financiera.🚀 Instalación RecomendadaPara evitar errores de permisos, el sistema se instala en /opt/atreyu.Clonar el repositorio:cd /opt
sudo git clone [https://github.com/atreyu1968/editorial.git](https://github.com/atreyu1968/editorial.git) atreyu
cd atreyu
Ejecutar el Instalador:chmod +x install.sh
sed -i 's/\r$//' install.sh
sudo ./install.sh
🛠️ Solución de Errores ComunesError 500 (Permisos)Si instalaste en /root anteriormente, mueve la carpeta y reinstala:sudo mv /root/editorial /opt/atreyu
cd /opt/atreyu
sudo ./install.sh
Resetear PM2 (Si falla el backend)pm2 delete atreyu-backend
pm2 kill
sudo /opt/atreyu/install.sh
🔐 AccesoContraseña: 697457© 2026 Atreyu Servicios Digitales
