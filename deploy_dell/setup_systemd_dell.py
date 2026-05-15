import paramiko

HOST = "100.91.99.109"
USER = "umbrel"
PASS = "Umbrel1*"
REMOTE_DIR = "gastos_bot"

SERVICE_CONTENT = f"""[Unit]
Description=Telegram Expense Bot
After=network.target

[Service]
User={USER}
Group={USER}
WorkingDirectory=/home/{USER}/{REMOTE_DIR}
Environment=PYTHONPATH=/home/{USER}/.local/lib/python3.12/site-packages
ExecStart=/usr/bin/python3 /home/{USER}/{REMOTE_DIR}/expense_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

def setup_service():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)
    
    # 1. Kill any existing nohup processes first to avoid conflicts
    print("Finalizando processos nohup antigos...")
    ssh.exec_command("pkill -f expense_bot.py")
    
    # 2. Criar o arquivo de serviço localmente no servidor
    print("Criando arquivo de servi\u00e7o systemd...")
    ssh.exec_command(f"echo '{SERVICE_CONTENT}' > /home/{USER}/gastos_bot.service")
    
    # 3. Mover para /etc/systemd/system/ (precisa de sudo)
    print("Instalando o servi\u00e7o com sudo...")
    # Como estamos no Umbrel (geralmente debian-based), usamos systemctl
    # O ssh.exec_command n\u00e3o lida bem com prompts de senha de sudo, 
    # mas no Umbrel o usu\u00e1rio 'umbrel' costuma ter NOPASSWD para comandos systemctl ou podemos passar a senha.
    
    # Tentativa com sudo e entrada de senha
    commands = [
        f"echo '{PASS}' | sudo -S mv /home/{USER}/gastos_bot.service /etc/systemd/system/gastos_bot.service",
        f"echo '{PASS}' | sudo -S systemctl daemon-reload",
        f"echo '{PASS}' | sudo -S systemctl enable gastos_bot.service",
        f"echo '{PASS}' | sudo -S systemctl restart gastos_bot.service"
    ]
    
    for cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        err = stderr.read().decode('utf-8', 'replace')
        if err and "password" not in err.lower(): # Ignora o prompt de "password for umbrel:"
            print(f"Error executing command: {cmd}")
            print(err)
            
    print("\n[OK] Servi\u00e7o systemd configurado e iniciado!")
    print("O bot agora ir\u00e1 iniciar automaticamente em caso de reinicializa\u00e7\u00e3o do servidor.")
    
    ssh.close()

if __name__ == "__main__":
    setup_service()
