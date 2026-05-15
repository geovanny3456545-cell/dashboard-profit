import paramiko

HOST = "100.91.99.109"
USER = "umbrel"
PASS = "Umbrel1*"

def diagnose():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)
    
    commands = [
        "python3 -m pip install --user --break-system-packages pandas python-telegram-bot gspread oauth2client python-dotenv",
        "python3 -c 'import pandas; import telegram; print(\"SUCCESS: imports work\")'",
    ]
    
    for cmd in commands:
        print(f"\n--- Running: {cmd} ---")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', 'replace')
        err = stderr.read().decode('utf-8', 'replace')
        # Use safe printing for Windows
        print(out.encode('ascii', 'replace').decode('ascii'))
        if err:
            print("Error:")
            print(err.encode('ascii', 'replace').decode('ascii'))
            
    ssh.close()

if __name__ == "__main__":
    diagnose()
