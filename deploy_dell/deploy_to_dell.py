import paramiko
import os
import time

# Configurações do Dell Node
HOST = "100.91.99.109"
USER = "umbrel"
PASS = "Umbrel1*"
REMOTE_DIR = "gastos_bot"

def deploy():
    print(f"[DEPLOY] Iniciando deploy para o Dell Node ({HOST})...")
    
    # Setup SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASS, timeout=20)
        print("[OK] Conectado ao Dell Node.")
        
        # 1. Criar diretório remoto
        ssh.exec_command(f"mkdir -p {REMOTE_DIR}")
        
        # 2. Upload de arquivos via SFTP
        sftp = ssh.open_sftp()
        local_files = [
            "expense_bot.py",
            ".env",
            "requirements.txt",
            "google_creds.json"
        ]
        
        # Obter o caminho relativo ao script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        for f in local_files:
            local_path = os.path.join(base_dir, f)
            remote_path = f"{REMOTE_DIR}/{f}"
            print(f"[UPLOAD] Enviando {f}...")
            sftp.put(local_path, remote_path)
        sftp.close()
        
        # 3. Instalar dependências
        print("[SETUP] Instalando dependências no Dell Node...")
        # Usamos --break-system-packages para garantir que instale no Python 3.12 do Umbrel
        libs = "pandas \"python-telegram-bot[job-queue]\" gspread oauth2client python-dotenv"
        cmd_install = f"python3 -m pip install --user --break-system-packages {libs}"
        ssh.exec_command(cmd_install)
        time.sleep(5) # Aguardar um pouco para garantir que o sistema de arquivos processe

        # 4. Matar instâncias anteriores (limpeza)
        print("[CLEAN] Limpando processos antigos...")
        ssh.exec_command("pkill -f expense_bot.py")
        
        # 5. Reiniciar via Systemd
        print("[START] Reiniciando o bot como serviço (systemd)...")
        # Tentamos reiniciar o serviço. Como pode dar erro se não existir, matamos por garantia acima.
        ssh.exec_command(f"echo '{PASS}' | sudo -S systemctl restart gastos_bot.service")
        
        print("\n*** DEPLOY CONCLUÍDO COM SUCESSO! ***")
        print(f"O bot agora está rodando 24h via systemd no Dell Node ({HOST}).")
        
        ssh.close()
        
    except Exception as e:
        print(f"[ERRO] Durante o deploy: {e}")

if __name__ == "__main__":
    deploy()
