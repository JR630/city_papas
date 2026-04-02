/**
 * Script principal de funcionalidades JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('CityPapa App Loaded');
    
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
 * Recalcula el total de una venta
 */
function recalcularTotal(cantidadEl, precioEl, totalEl) {
    const cantidad = parseFloat(cantidadEl.value) || 0;
    const precio = parseFloat(precioEl.value) || 0;
    const total = cantidad * precio;
    
    if (totalEl) {
        totalEl.textContent = '$' + total.toFixed(2);
    }
    
    return total;
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
