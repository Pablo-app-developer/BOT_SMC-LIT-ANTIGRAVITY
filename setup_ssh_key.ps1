# Script de configuración de SSH Key para acceso sin contraseña
# Ejecutar UNA SOLA VEZ

# Cargar credenciales
if (Test-Path ".\vps_credentials.ps1") {
    . .\vps_credentials.ps1
}
else {
    Write-Host "Error: No se encontro vps_credentials.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "Configurando acceso SSH sin contrasena..." -ForegroundColor Green

# Verificar si ya existe la llave SSH
$sshKeyPath = "$env:USERPROFILE\.ssh\id_rsa"
if (-not (Test-Path $sshKeyPath)) {
    Write-Host "Generando nueva llave SSH..." -ForegroundColor Cyan
    ssh-keygen -t rsa -b 4096 -f $sshKeyPath -N '""'
}

Write-Host "Copiando llave publica al VPS..." -ForegroundColor Cyan
Write-Host "Se te pedira la contrasena UNA ULTIMA VEZ:" -ForegroundColor Yellow

# Copiar la llave pública al VPS
$publicKey = Get-Content "$sshKeyPath.pub"
$command = "mkdir -p ~/.ssh && echo '$publicKey' >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"

ssh root@${VPS_IP} $command

Write-Host ""
Write-Host "Listo! Ahora puedes conectarte sin contrasena." -ForegroundColor Green
Write-Host "Prueba ejecutando: ssh root@${VPS_IP}" -ForegroundColor Cyan
Write-Host ""
