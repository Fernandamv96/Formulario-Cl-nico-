/**
 * Validación de formulario del lado del cliente.
 * Complementa (no reemplaza) la validación del servidor en app.py.
 */
(function () {
  const form = document.getElementById("clinicalForm");
  if (!form) return;

  const REQUIRED_IDS = [
    "nombres", "apellidos", "tipo_documento", "numero_documento",
    "fecha_nacimiento", "sexo", "motivo_consulta",
  ];

  function setFieldError(input, message) {
    const field = input.closest(".field");
    if (!field) return;
    field.classList.toggle("has-error", Boolean(message));

    let errorEl = field.querySelector(".field-error");
    if (message) {
      if (!errorEl) {
        errorEl = document.createElement("span");
        errorEl.className = "field-error";
        field.appendChild(errorEl);
      }
      errorEl.textContent = message;
    } else if (errorEl) {
      errorEl.remove();
    }
  }

  function validateRequired(input) {
    if (!input.value.trim()) {
      setFieldError(input, "Este campo es obligatorio.");
      return false;
    }
    setFieldError(input, "");
    return true;
  }

  function validateEmail(input) {
    if (!input.value.trim()) { setFieldError(input, ""); return true; }
    const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value.trim());
    setFieldError(input, ok ? "" : "El correo electrónico no es válido.");
    return ok;
  }

  function validateDateOfBirth(input) {
    if (!input.value) { setFieldError(input, "Este campo es obligatorio."); return false; }
    const value = new Date(input.value + "T00:00:00");
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (value > today) {
      setFieldError(input, "La fecha de nacimiento no puede ser futura.");
      return false;
    }
    setFieldError(input, "");
    return true;
  }

  function validateNumberRange(input) {
    if (!input.value.trim()) { setFieldError(input.closest(".field") ? input : input, ""); return true; }
    const val = parseFloat(input.value);
    const min = input.hasAttribute("min") ? parseFloat(input.min) : -Infinity;
    const max = input.hasAttribute("max") ? parseFloat(input.max) : Infinity;
    const ok = !Number.isNaN(val) && val >= min && val <= max;
    // Los inputs de signos vitales no tienen wrapper .field-error dedicado en el DOM,
    // así que solo aplicamos el estilo visual de alerta.
    input.classList.toggle("vital-out-of-range", !ok);
    return ok;
  }

  // Validación en vivo mientras se escribe / al perder el foco
  REQUIRED_IDS.forEach((id) => {
    const input = document.getElementById(id);
    if (!input) return;
    input.addEventListener("blur", () => validateRequired(input));
    input.addEventListener("input", () => {
      if (input.closest(".field").classList.contains("has-error")) validateRequired(input);
    });
  });

  const emailInput = document.getElementById("email");
  if (emailInput) {
    emailInput.addEventListener("blur", () => validateEmail(emailInput));
  }

  const dobInput = document.getElementById("fecha_nacimiento");
  if (dobInput) {
    dobInput.addEventListener("change", () => validateDateOfBirth(dobInput));
  }

  form.querySelectorAll('input[type="number"]').forEach((input) => {
    input.addEventListener("input", () => validateNumberRange(input));
  });

  // Validación final al enviar
  form.addEventListener("submit", (event) => {
    let valid = true;

    REQUIRED_IDS.forEach((id) => {
      const input = document.getElementById(id);
      if (input && !validateRequired(input)) valid = false;
    });

    if (emailInput && !validateEmail(emailInput)) valid = false;
    if (dobInput && !validateDateOfBirth(dobInput)) valid = false;

    if (!valid) {
      event.preventDefault();
      const firstError = form.querySelector(".has-error input, .has-error select, .has-error textarea");
      if (firstError) {
        firstError.scrollIntoView({ behavior: "smooth", block: "center" });
        firstError.focus();
      }
    }
  });
})();
