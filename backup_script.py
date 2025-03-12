#!/usr/bin/env python
import datetime
import os
import subprocess
import shutil
from django.conf import settings

def create_backup():
    """
    Creates a database backup for the JoburipentruRomani project on PythonAnywhere.
    Keeps only the latest 7 backups to save space.
    """
    # Directory for backups (create if doesn't exist)
    backup_dir = os.path.expanduser("~/backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Format today's date for the backup filename
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    backup_file = os.path.join(backup_dir, f"joburipentruromani_db_backup_{today}.sql")
    
    # Get database credentials from environment variables
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    
    # Command to backup MySQL database
    command = f"mysqldump -h {db_host} -u {db_user} -p'{db_password}' {db_name} > {backup_file}"
    
    try:
        # Execute the command
        result = subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE)
        print(f"✅ Backup creat cu succes: {backup_file}")
        
        # Check if backup file was created and has content
        if os.path.exists(backup_file) and os.path.getsize(backup_file) > 0:
            print(f"   Dimensiune backup: {os.path.getsize(backup_file) / (1024*1024):.2f} MB")
            
            # Create a compressed version
            try:
                compressed_file = f"{backup_file}.gz"
                with open(backup_file, 'rb') as f_in:
                    with open(f"{backup_file}.gz", 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove the uncompressed file if compression was successful
                if os.path.exists(compressed_file) and os.path.getsize(compressed_file) > 0:
                    os.remove(backup_file)
                    print(f"   Backup comprimat: {compressed_file}")
                    print(f"   Dimensiune după comprimare: {os.path.getsize(compressed_file) / (1024*1024):.2f} MB")
                    
                    # Use the compressed file for rotation
                    backup_file = compressed_file
            except Exception as e:
                print(f"⚠️ Avertisment: Nu s-a putut comprima backup-ul: {str(e)}")
            
            # Cleanup old backups
            cleanup_old_backups(backup_dir, 7)
        else:
            print(f"❌ Eroare: Fișierul de backup nu a fost creat sau este gol")
    
    except subprocess.CalledProcessError as e:
        print(f"❌ Eroare la crearea backup-ului: {e.stderr.decode('utf-8')}")
    except Exception as e:
        print(f"❌ Eroare neașteptată: {str(e)}")

def cleanup_old_backups(backup_dir, keep_days):
    """
    Removes old backup files, keeping only the most recent ones.
    
    Args:
        backup_dir: Directory containing backup files
        keep_days: Number of most recent backups to keep
    """
    print(f"\n🧹 Curățare backup-uri vechi (păstrând ultimele {keep_days})...")
    
    # Get all backup files
    backup_files = []
    for f in os.listdir(backup_dir):
        if f.startswith("joburipentruromani_db_backup_") and (f.endswith(".sql") or f.endswith(".sql.gz")):
            backup_path = os.path.join(backup_dir, f)
            creation_time = os.path.getctime(backup_path)
            backup_files.append((backup_path, creation_time))
    
    # Sort by creation time (newest first)
    backup_files.sort(key=lambda x: x[1], reverse=True)
    
    # Delete older backups
    if len(backup_files) > keep_days:
        for old_file, _ in backup_files[keep_days:]:
            try:
                os.remove(old_file)
                print(f"   Șters: {os.path.basename(old_file)}")
            except Exception as e:
                print(f"   ⚠️ Nu s-a putut șterge {os.path.basename(old_file)}: {str(e)}")
    else:
        print(f"   Nu există backup-uri vechi de șters. Total backup-uri: {len(backup_files)}")

if __name__ == "__main__":
    print("🔄 Începe procesul de backup...")
    create_backup()
    print("✅ Proces de backup finalizat.")
