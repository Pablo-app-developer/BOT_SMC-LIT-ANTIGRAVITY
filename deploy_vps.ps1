# Script de despliegue AUTOMATIZADO - Sin contraseñas
# Requiere haber ejecutado setup_ssh_key.ps1 primero

# Cargar credenciales
if (Test-Path ".\vps_credentials.ps1") {
    . .\vps_credentials.ps1
}
else {
    Write-Host "Error: No se encontro vps_credentials.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "Desplegando SMC FUSION CCXT al VPS..." -ForegroundColor Green
Write-Host ""

# Verificar conexión SSH
Write-Host "[1/7] Verificando conexion SSH..." -ForegroundColor Cyan
$testConnection = ssh root@${VPS_IP} "echo OK" 2>&1
if ($testConnection -notlike "*OK*") {
    Write-Host "Error: No se pudo conectar al VPS" -ForegroundColor Red
    Write-Host "Verifica que setup_ssh_key.ps1 se haya ejecutado correctamente" -ForegroundColor Yellow
    exit 1
}
Write-Host "Conexion OK" -ForegroundColor Green

# Preparar directorios
Write-Host "[2/7] Preparando directorios..." -ForegroundColor Cyan
ssh root@${VPS_IP} "rm -rf ${REMOTE_DIR}; mkdir -p ${REMOTE_DIR}/config ${REMOTE_DIR}/src"

# Copiar archivos en batch
Write-Host "[3/7] Copiando archivos..." -ForegroundColor Cyan
scp -q Dockerfile.ccxt "root@${VPS_IP}:${REMOTE_DIR}/"
scp -q docker-compose.ccxt.yml "root@${VPS_IP}:${REMOTE_DIR}/docker-compose.yml"
scp -q requirements_ccxt.txt "root@${VPS_IP}:${REMOTE_DIR}/"
scp -q .env.ccxt "root@${VPS_IP}:${REMOTE_DIR}/.env.ccxt"
scp -q config/settings_ccxt.py "root@${VPS_IP}:${REMOTE_DIR}/config/"
scp -q config/__init__.py "root@${VPS_IP}:${REMOTE_DIR}/config/"
scp -q src/main_ccxt.py "root@${VPS_IP}:${REMOTE_DIR}/src/"
Write-Host "Archivos copiados" -ForegroundColor Green

# Verificar Docker Compose
Write-Host "[4/7] Verificando Docker..." -ForegroundColor Cyan
$dockerVersion = ssh root@${VPS_IP} "docker-compose --version 2>&1"
Write-Host "Docker Compose: $dockerVersion" -ForegroundColor Gray

# Detener contenedor anterior
Write-Host "[5/7] Limpiando contenedores antiguos..." -ForegroundColor Cyan
ssh root@${VPS_IP} "cd ${REMOTE_DIR}; docker-compose down 2>/dev/null || true"
ssh root@${VPS_IP} "docker system prune -f -a --volumes 2>/dev/null || true"

# Construir imagen
Write-Host "[6/7] Construyendo imagen Docker..." -ForegroundColor Yellow
ssh root@${VPS_IP} "cd ${REMOTE_DIR}; docker-compose build"

# Iniciar bot
Write-Host "[7/7] Iniciando bot..." -ForegroundColor Green
ssh root@${VPS_IP} "cd ${REMOTE_DIR}; docker-compose up -d"

# Verificar estado
Write-Host ""
Write-Host "Verificando estado del bot..." -ForegroundColor Cyan
Start-Sleep -Seconds 3
$status = ssh root@${VPS_IP} "docker ps --filter name=smc_fusion_ccxt_bot --format '{{.Status}}'"

if ($status) {
    Write-Host "Bot desplegado exitosamente!" -ForegroundColor Green
    Write-Host "Estado: $status" -ForegroundColor White
}
else {
    Write-Host "Advertencia: El contenedor no esta corriendo" -ForegroundColor Yellow
    Write-Host "Revisa los logs con: ssh root@${VPS_IP} 'docker logs smc_fusion_ccxt_bot'" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Comandos utiles:" -ForegroundColor Cyan
Write-Host "  Ver logs:  ssh root@${VPS_IP} 'docker logs -f smc_fusion_ccxt_bot'" -ForegroundColor White
Write-Host "  Detener:   ssh root@${VPS_IP} 'cd ${REMOTE_DIR}; docker-compose down'" -ForegroundColor White
Write-Host "  Reiniciar: ssh root@${VPS_IP} 'cd ${REMOTE_DIR}; docker-compose restart'" -ForegroundColor White
Write-Host ""
