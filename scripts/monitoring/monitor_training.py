"""
Monitor de progreso del entrenamiento
"""
import time
import os

def monitor_training():
    log_file = 'training_output.log'
    
    print("🔍 MONITOREANDO ENTRENAMIENTO...")
    print("="*70)
    print("Presiona Ctrl+C para salir del monitor\n")
    
    last_size = 0
    
    while True:
        try:
            if os.path.exists(log_file):
                current_size = os.path.getsize(log_file)
                
                if current_size > last_size:
                    with open(log_file, 'r') as f:
                        f.seek(last_size)
                        new_content = f.read()
                        if new_content.strip():
                            print(new_content, end='')
                    last_size = current_size
                
                # Verificar si terminó
                with open(log_file, 'r') as f:
                    content = f.read()
                    if 'ENTRENAMIENTO OPTIMIZADO COMPLETADO' in content:
                        print("\n" + "="*70)
                        print("✅ ENTRENAMIENTO COMPLETADO!")
                        print("="*70)
                        break
                    elif 'Error' in content or 'Traceback' in content:
                        print("\n" + "="*70)
                        print("⚠️  Se detectó un error. Revisa training_output.log")
                        print("="*70)
                        break
            else:
                print(f"⏳ Esperando que se cree {log_file}...")
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n\n👋 Saliendo del monitor...")
            print("El entrenamiento continúa en background.")
            print("Usa: tail -f training_output.log para seguir monitoreando")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_training()

