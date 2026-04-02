/**
 * Script principal de funcionalidades JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('CityPapa Admin Panel Loaded');
    
    // Validar formularios antes de enviar
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value || (input.type === 'number' && parseFloat(input.value) <= 0)) {
                    isValid = false;
                    input.style.borderColor = '#EF4444';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Por favor completa todos los campos requeridos correctamente.');
            }
        });
    });
});

/**
 * Genera reportes dinámicos
 */
function generarReporte() {
    console.log('Generando reporte...');
}

/**
 * Exporta tabla a CSV
 */
function exportarTablaCSV(idTabla, nombreArchivo = 'reporte.csv') {
    const tabla = document.getElementById(idTabla);
    if (!tabla) return;
    
    let csv = [];
    const filas = tabla.querySelectorAll('tr');
    
    filas.forEach(fila => {
        const celdas = fila.querySelectorAll('th, td');
        const contenido = Array.from(celdas).map(c => '"' + c.textContent.trim() + '"').join(',');
        csv.push(contenido);
    });
    
    const contenido = csv.join('\n');
    const blob = new Blob([contenido], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = nombreArchivo;
    a.click();
}

/**
 * Formatea un número como moneda
 */
function formatearMoneda(valor) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
    }).format(valor);
}

/**
 * Muestra/oculta un elemento
 */
function toggle(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = element.style.display === 'none' ? 'block' : 'none';
    }
}

/**
 * Confirma una acción peligrosa
 */
function confirmar(mensaje = '¿Estás seguro?') {
    return confirm(mensaje);
}
