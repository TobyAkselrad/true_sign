#!/bin/bash

echo "🔍 PROGRESO DEL ENTRENAMIENTO"
echo "="
echo ""

# Verificar si el proceso está corriendo
if pgrep -f "train_models_verbose.py" > /dev/null; then
    echo "✅ Proceso ACTIVO"
    
    # Mostrar stats del proceso
    ps aux | grep train_models_verbose | grep -v grep | awk '{print "   CPU: "$3"% | MEM: "$4"% | TIME: "$10}'
    
    # Tamaño del log
    if [ -f training_verbose.log ]; then
        SIZE=$(du -h training_verbose.log | cut -f1)
        LINES=$(wc -l < training_verbose.log)
        echo "   Log: $SIZE ($LINES líneas)"
    fi
    
    echo ""
    echo "📋 ÚLTIMAS 20 LÍNEAS DEL LOG:"
    echo "─────────────────────────────────────────"
    tail -20 training_verbose.log
    echo ""
    echo "💡 Para ver en tiempo real: tail -f training_verbose.log"
else
    echo "❌ Proceso NO está corriendo"
    
    if [ -f training_verbose.log ]; then
        echo ""
        echo "📋 ÚLTIMAS LÍNEAS DEL LOG:"
        echo "─────────────────────────────────────────"
        tail -20 training_verbose.log
        
        # Check si terminó
        if grep -q "ENTRENAMIENTO COMPLETADO" training_verbose.log; then
            echo ""
            echo "🎉 ¡ENTRENAMIENTO COMPLETADO!"
        elif grep -q "Error" training_verbose.log; then
            echo ""
            echo "⚠️  Hubo un error. Revisa el log completo."
        fi
    fi
fi

echo ""
echo "="

