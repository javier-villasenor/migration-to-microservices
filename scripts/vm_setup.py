#!/usr/bin/env python3
"""
Script de instalación automática de la aplicación BookInfo
Para la Práctica Creativa 2 - Parte 1
Grupo: GRUPO G5


Este script automatiza la instalación de la aplicación BookInfo monolítica
en una máquina virtual de Google Cloud.


Uso:
    sudo python3 install_bookinfo.py


Requisitos:
    - Ejecutar en una VM de Google Cloud (Debian/Ubuntu)
    - Tener permisos de superusuario (sudo)
    - Tener el repositorio practica_creativa2 en el mismo directorio que este script
"""


import os
import sys
import subprocess
import shutil
from pathlib import Path


# Configuración
TEAM_ID = "GRUPO G5"
APP_PORT = 8080
APP_DIR = "/opt/bookinfo"
REPO_DIR = "practica_creativa2/bookinfo/src/productpage"
SERVICE_NAME = "bookinfo"


class Colors:
    """Códigos ANSI para colorear la salida"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_step(message):
    """Imprime un mensaje de paso con formato"""
    print(f"\n{Colors.OKBLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'='*60}{Colors.ENDC}\n")


def print_success(message):
    """Imprime un mensaje de éxito"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    """Imprime un mensaje de error"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_warning(message):
    """Imprime un mensaje de advertencia"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def run_command(command, shell=False, check=True, capture_output=False):
    """Ejecuta un comando del sistema"""
    try:
        if capture_output:
            result = subprocess.run(
                command if shell else command.split(),
                shell=shell,
                check=check,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        else:
            subprocess.run(
                command if shell else command.split(),
                shell=shell,
                check=check
            )
            return None
    except subprocess.CalledProcessError as e:
        print_error(f"Error ejecutando comando: {command}")
        if capture_output and e.stderr:
            print(e.stderr)
        raise


def check_root():
    """Verifica que el script se ejecute con privilegios de superusuario"""
    print_step("Verificando privilegios de superusuario")
    if os.geteuid() != 0:
        print_error("Este script debe ejecutarse con privilegios de superusuario (sudo)")
        sys.exit(1)
    print_success("Privilegios de superusuario confirmados")


def check_system():
    """Verifica que el sistema sea compatible"""
    print_step("Verificando sistema operativo")
    if sys.platform != "linux":
        print_error("Este script está diseñado para sistemas Linux (Google Cloud VM)")
        sys.exit(1)
    print_success("Sistema compatible detectado")


def update_system():
    """Actualiza los repositorios del sistema"""
    print_step("Actualizando repositorios del sistema")
    run_command("apt-get update -y")
    print_success("Repositorios actualizados")


def install_dependencies():
    """Instala las dependencias del sistema necesarias"""
    print_step("Instalando dependencias del sistema")
   
    # Lista de paquetes necesarios
    packages = [
        "python3",
        "python3-pip",
        "python3-dev",
        "build-essential",
        "git"
    ]
   
    print(f"Instalando paquetes: {', '.join(packages)}")
    run_command(f"apt-get install -y {' '.join(packages)}")
    print_success("Dependencias del sistema instaladas")


def check_python_version():
    """Verifica la versión de Python"""
    print_step("Verificando versión de Python")
    version = run_command("python3 --version", capture_output=True)
    print(f"Versión de Python detectada: {version}")
   
    # Extraer número de versión
    version_parts = version.split()[1].split('.')
    major, minor = int(version_parts[0]), int(version_parts[1])
   
    if major < 3 or (major == 3 and minor < 6):
        print_warning(f"Python {version} puede no ser compatible. Se recomienda Python 3.9+")
    else:
        print_success(f"Versión de Python compatible: {version}")


def copy_application():
    """Copia la aplicación al directorio de instalación"""
    print_step("Copiando aplicación al directorio de instalación")
   
    # Verificar que existe el directorio del repositorio
    if not os.path.exists(REPO_DIR):
        print_error(f"No se encuentra el directorio del repositorio: {REPO_DIR}")
        print("Asegúrate de que el repositorio practica_creativa2 esté en el mismo directorio que este script")
        sys.exit(1)
   
    # Crear directorio de instalación si no existe
    if os.path.exists(APP_DIR):
        print_warning(f"El directorio {APP_DIR} ya existe. Eliminando...")
        shutil.rmtree(APP_DIR)
   
    # Copiar archivos
    print(f"Copiando {REPO_DIR} -> {APP_DIR}")
    shutil.copytree(REPO_DIR, APP_DIR)
    print_success(f"Aplicación copiada a {APP_DIR}")


def install_python_dependencies():
    """Instala las dependencias de Python desde requirements.txt"""
    print_step("Instalando dependencias de Python")
   
    requirements_file = os.path.join(APP_DIR, "requirements.txt")
    if not os.path.exists(requirements_file):
        print_error(f"No se encuentra el archivo requirements.txt en {APP_DIR}")
        sys.exit(1)
   
    print(f"Instalando desde {requirements_file}")
    run_command(f"pip3 install -r {requirements_file}")
    print_success("Dependencias de Python instaladas")


def configure_firewall():
    """Configura el firewall para permitir tráfico en el puerto de la aplicación"""
    print_step("Configurando firewall")
   
    # Verificar si ufw está instalado
    try:
        run_command("which ufw", capture_output=True)
        ufw_installed = True
    except subprocess.CalledProcessError:
        ufw_installed = False
   
    if ufw_installed:
        print(f"Abriendo puerto {APP_PORT} en UFW")
        try:
            run_command(f"ufw allow {APP_PORT}/tcp", check=False)
            print_success(f"Puerto {APP_PORT} abierto en UFW")
        except:
            print_warning("No se pudo configurar UFW (puede no estar activo)")
    else:
        print_warning("UFW no está instalado")
   
    print_warning("\n⚠️  IMPORTANTE: Debes configurar las reglas de firewall en Google Cloud Console")
    print(f"   Permite tráfico TCP en el puerto {APP_PORT}")
    print("   Consola Google Cloud -> VPC network -> Firewall rules\n")


def create_systemd_service():
    """Crea un servicio systemd para la aplicación"""
    print_step("Creando servicio systemd")
   
    service_content = f"""[Unit]
Description=BookInfo Application - {TEAM_ID}
After=network.target


[Service]
Type=simple
User=root
WorkingDirectory={APP_DIR}
Environment="TEAM_ID={TEAM_ID}"
ExecStart=/usr/bin/python3 {APP_DIR}/productpage_monolith.py {APP_PORT}
Restart=on-failure
RestartSec=10


[Install]
WantedBy=multi-user.target
"""
   
    service_file = f"/etc/systemd/system/{SERVICE_NAME}.service"
    print(f"Creando archivo de servicio: {service_file}")
   
    with open(service_file, 'w') as f:
        f.write(service_content)
   
    print_success(f"Servicio {SERVICE_NAME} creado")


def start_service():
    """Inicia el servicio de la aplicación"""
    print_step("Iniciando servicio de la aplicación")
   
    # Recargar configuración de systemd
    run_command("systemctl daemon-reload")
   
    # Habilitar servicio para inicio automático
    run_command(f"systemctl enable {SERVICE_NAME}")
    print_success(f"Servicio {SERVICE_NAME} habilitado para inicio automático")
   
    # Iniciar servicio
    run_command(f"systemctl start {SERVICE_NAME}")
    print_success(f"Servicio {SERVICE_NAME} iniciado")
   
    # Esperar un momento para que el servicio arranque
    import time
    time.sleep(2)
   
    # Verificar estado del servicio
    try:
        status = run_command(f"systemctl is-active {SERVICE_NAME}", capture_output=True)
        if status == "active":
            print_success("El servicio está ejecutándose correctamente")
        else:
            print_warning(f"Estado del servicio: {status}")
    except:
        print_error("El servicio no se pudo iniciar correctamente")
        print("Revisa los logs con: journalctl -u bookinfo -n 50")


def get_public_ip():
    """Obtiene la IP pública de la VM"""
    print_step("Obteniendo IP pública")
   
    try:
        # Método para Google Cloud
        ip = run_command(
            "curl -H 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip",
            shell=True,
            capture_output=True,
            check=False
        )
       
        if ip and ip.strip():
            print_success(f"IP pública: {ip}")
            return ip
        else:
            # Método alternativo usando servicio externo
            ip = run_command("curl -s ifconfig.me", shell=True, capture_output=True, check=False)
            if ip and ip.strip():
                print_success(f"IP pública: {ip}")
                return ip
            else:
                print_warning("No se pudo obtener la IP pública automáticamente")
                print("Puedes consultarla en Google Cloud Console")
                return None
    except Exception as e:
        print_warning(f"Error obteniendo IP pública: {e}")
        return None


def print_final_instructions(public_ip=None):
    """Imprime las instrucciones finales para el usuario"""
    print_step("¡Instalación completada!")
   
    print(f"{Colors.OKGREEN}{Colors.BOLD}✓ La aplicación BookInfo ha sido instalada correctamente{Colors.ENDC}\n")
   
    print(f"{Colors.BOLD}Información del despliegue:{Colors.ENDC}")
    print(f"  • Team ID: {TEAM_ID}")
    print(f"  • Puerto: {APP_PORT}")
    print(f"  • Directorio: {APP_DIR}")
    print(f"  • Servicio: {SERVICE_NAME}")
   
    print(f"\n{Colors.BOLD}Comandos útiles:{Colors.ENDC}")
    print(f"  • Ver estado: systemctl status {SERVICE_NAME}")
    print(f"  • Ver logs: journalctl -u {SERVICE_NAME} -f")
    print(f"  • Reiniciar: systemctl restart {SERVICE_NAME}")
    print(f"  • Detener: systemctl stop {SERVICE_NAME}")
   
    print(f"\n{Colors.BOLD}Acceso a la aplicación:{Colors.ENDC}")
    print(f"  • Local: http://localhost:{APP_PORT}/productpage")
   
    if public_ip:
        print(f"  • Externo: {Colors.OKGREEN}{Colors.BOLD}http://{public_ip}:{APP_PORT}/productpage{Colors.ENDC}")
    else:
        print(f"  • Externo: http://<IP_PUBLICA>:{APP_PORT}/productpage")
        print(f"    (consulta la IP pública en Google Cloud Console)")
   
    print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  IMPORTANTE:{Colors.ENDC}")
    print(f"{Colors.WARNING}   Asegúrate de configurar las reglas de firewall en Google Cloud Console")
    print(f"   para permitir tráfico TCP en el puerto {APP_PORT}{Colors.ENDC}")
   
    print(f"\n{Colors.OKCYAN}{'='*60}{Colors.ENDC}\n")


def main():
    """Función principal"""
    try:
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║   Instalación Automática de BookInfo - Práctica Creativa 2   ║")
        print(f"║   Grupo: {TEAM_ID:^49} ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}\n")
       
        # Pasos de instalación
        check_root()
        check_system()
        update_system()
        install_dependencies()
        check_python_version()
        copy_application()
        install_python_dependencies()
        configure_firewall()
        create_systemd_service()
        start_service()
       
        # Obtener IP pública y mostrar instrucciones finales
        public_ip = get_public_ip()
        print_final_instructions(public_ip)
       
    except KeyboardInterrupt:
        print_error("\n\nInstalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nError durante la instalación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
