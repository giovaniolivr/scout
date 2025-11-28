/* ======================================================================
   ÍCONES PERSONALIZADOS 
====================================================================== */
const SVG_OLHO_FECHADO = `
<svg width="22" height="22" viewBox="0 0 24 24" fill="none">
  <path d="M4 12C4 12 7 8 12 8C17 8 20 12 20 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <line x1="6" y1="11" x2="6.5" y2="8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <line x1="9.5" y1="9.5" x2="9.5" y2="6.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <line x1="12" y1="9" x2="12" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <line x1="14.5" y1="9.5" x2="14.5" y2="6.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  <line x1="18" y1="11" x2="17.5" y2="8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>
`;

const SVG_OLHO_ABERTO = `
<svg width="22" height="22" viewBox="0 0 48 48" fill="none">
  <path d="M12 24C12 24 16.5 14 24 14C31.5 14 36 24 36 24" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <circle cx="24" cy="24" r="4.5" stroke="currentColor" stroke-width="3" fill="none"/>
  <circle cx="24" cy="24" r="2" fill="currentColor"/>
</svg>
`;

/* ======================================================================
   TOGGLE DE SENHA (AGORA PADRÃO OFICIAL)
====================================================================== */
function setupPasswordToggle(inputId, iconWrapperId) {
    const input = document.getElementById(inputId);
    const wrapper = document.getElementById(iconWrapperId);

    if (!input || !wrapper) return;

    // Ícone inicial
    wrapper.innerHTML = SVG_OLHO_FECHADO;

    wrapper.addEventListener("click", () => {
        const isVisible = input.type === "text";
        input.type = isVisible ? "password" : "text";
        wrapper.innerHTML = isVisible ? SVG_OLHO_FECHADO : SVG_OLHO_ABERTO;
    });
}

/* ======================================================================
   UTILITÁRIOS (NÃO ALTERADOS, TODOS NECESSÁRIOS)
====================================================================== */

// Apenas números
function onlyNumbers(input, length = null) {
    if (!input) return;
    input.addEventListener("input", () => {
        let value = input.value.replace(/\D/g, "");
        if (length && value.length > length) value = value.slice(0, length);
        input.value = value;
    });
}

// Exibir erro
function showError(input, message) {
    clearError(input);

    const alert = document.createElement("small");
    alert.className = "input-error";
    alert.textContent = message;
    alert.style.color = "#f66";
    alert.style.display = "block";
    alert.style.marginTop = "4px";

    input.parentNode.appendChild(alert);
}

// Remover erro
function clearError(input) {
    const alert = input?.parentNode?.querySelector(".input-error");
    if (alert) alert.remove();
}

// Validar CPF
function validateCPF(input) {
    const value = input.value.replace(/\D/g, "");
    clearError(input);

    if (value.length !== 11) {
        showError(input, "O CPF deve conter 11 números.");
        return false;
    }
    return true;
}

// Validar CNPJ
function validateCNPJ(input) {
    const value = input.value.replace(/\D/g, "");
    clearError(input);

    if (value.length !== 14) {
        showError(input, "O CNPJ deve conter 14 números.");
        return false;
    }
    return true;
}

// Validar senha forte
function validatePassword(senhaInput, confirmarInput) {
    clearError(senhaInput);
    clearError(confirmarInput);

    const senha = senhaInput.value;
    const confirmar = confirmarInput.value;

    const hasUpper = /[A-Z]/.test(senha);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(senha);

    if (senha.length < 8) {
        showError(senhaInput, "A senha deve ter no mínimo 8 caracteres.");
        return false;
    }
    if (!hasUpper) {
        showError(senhaInput, "A senha deve conter uma letra maiúscula.");
        return false;
    }
    if (!hasSpecial) {
        showError(senhaInput, "A senha deve conter um caractere especial.");
        return false;
    }
    if (senha !== confirmar) {
        showError(confirmarInput, "As senhas não coincidem.");
        return false;
    }

    return true;
}

// Máscara telefone
function initTelefoneMask(input) {
    if (!input) return;

    if (!input.value.startsWith("+55")) input.value = "+55 ";

    input.addEventListener("keydown", e => {
        if (input.selectionStart <= 3 && ["Backspace", "Delete"].includes(e.key)) {
            e.preventDefault();
        }
    });

    input.addEventListener("input", () => {
        if (!input.value.startsWith("+55")) {
            input.value = "+55 ";
        }

        let clean = input.value.replace(/[^\d+]/g, "");

        input.value = clean.replace(
            /(\+55)(\d{0,2})(\d{0,5})(\d{0,4}).*/,
            (_, p1, ddd, pt1, pt2) => {
                let f = p1;
                if (ddd) f += " (" + ddd;
                if (ddd.length === 2) f += ")";
                if (pt1) f += " " + pt1;
                if (pt2) f += "-" + pt2;
                return f;
            }
        );
    });
}

// Validar telefone
function validateTelefone(input) {
    clearError(input);
    const clean = input.value.replace(/\D/g, "");

    const ddd = clean.slice(2, 4);
    const num = clean.slice(4);

    if (ddd.length !== 2 || num.length !== 9) {
        showError(input, "Formato inválido: DDD + número (9 dígitos).");
        return false;
    }
    return true;
}

// Busca CEP
function lookupCEP(input, cb) {
    input.addEventListener("blur", () => {
        const cep = input.value.replace(/\D/g, "");
        clearError(input);

        if (cep.length === 8) {
            fetch(`https://viacep.com.br/ws/${cep}/json/`)
                .then(r => r.json())
                .then(data => {
                    if (!data.erro) cb(data);
                    else showError(input, "CEP não encontrado.");
                })
                .catch(() => showError(input, "Erro ao consultar CEP."));
        } else if (cep.length > 0 && cep.length < 8) {
            showError(input, "CEP deve conter 8 números.");
        }
    });
}

/* ======================================================================
   INICIALIZAÇÃO DA PÁGINA DE CADASTRO DA EMPRESA
====================================================================== */
function initDetailsCompany() {
    const form = document.getElementById("company-details-form");
    if (!form) return;

    const cpf = document.getElementById("cpf");
    const telefone = document.getElementById("telefone");
    const senha = document.getElementById("password");
    const confirmar = document.getElementById("confirm-password");
    const cep = document.getElementById("cep");

    onlyNumbers(cpf, 11);
    onlyNumbers(cep, 8);
    initTelefoneMask(telefone);

    lookupCEP(cep, data => {
        document.getElementById("cidade").value = data.localidade;
        document.getElementById("bairro").value = data.bairro;
        document.getElementById("endereco").value = data.logradouro;
    });

    //Toggle de senha para os dois campos
    setupPasswordToggle("password", "togglePassword");
    setupPasswordToggle("confirm-password", "toggleConfirmPassword");

    form.addEventListener("submit", e => {
        e.preventDefault();

        if (!validateCPF(cpf)) return;
        if (!validateTelefone(telefone)) return;
        if (!validatePassword(senha, confirmar)) return;

        const email = form.dataset.email;
        window.location.href = `/verify/company/?email=${encodeURIComponent(email)}`;
    });
}

// Verify Candidate (4 digits)
function initVerifyCandidate() {
    const form = document.getElementById("verify-candidate-form");
    if (!form) return;

    const boxes = document.querySelectorAll(".code-box");

    boxes.forEach((box, i) => {
        box.addEventListener("input", () => {
            if (box.value && i < boxes.length - 1) {
                boxes[i + 1].focus();
            }
        });
    });

    form.addEventListener("submit", e => {
        e.preventDefault();

        const code = [...boxes].map(i => i.value).join("");

        if (code === "1111") {
            window.location.href = "/register/candidate/details/";
            return;
        }

        alert("Código incorreto.");
        boxes.forEach(b => (b.value = ""));
        boxes[0].focus();
        return;
    });
}

// Verify Company
function initVerifyCompany() {
    const resend = document.getElementById("company-resend-btn");
    const verify = document.getElementById("verify-company-btn");

    if (resend) {
        resend.addEventListener("click", () => {
            alert(`Novo e-mail enviado (mock).`);
        });
    }

    if (verify) {
        verify.addEventListener("click", () => {
            window.location.href = "/company/home/";
        });
    }
}

function initLogin() {
    const form = document.getElementById("login-form");
    if (!form) return;

    const emailInput = document.getElementById("login-email");
    const passwordInput = document.getElementById("login-password");

    console.log("initLogin carregado");

    form.addEventListener("submit", e => {
        e.preventDefault();

        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        console.log("submit disparou");

        // Validação simples
        const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!pattern.test(email)) {
            alert("Digite um e-mail válido.");
            return;
        }

        if (password.length < 1) {
            alert("Digite sua senha.");
            return;
        }

        // MOCK TEMPORÁRIO DE REDIRECIONAMENTO
        if (email.toLowerCase().includes("empresa")) {
            window.location.href = "/company/home/";
        } else {
            window.location.href = "/candidate/home/";
        }
    });
}

/* ======================================================================
   INICIALIZAÇÃO GLOBAL
====================================================================== */
document.addEventListener("DOMContentLoaded", () => {
    initDetailsCompany();
    initVerifyCandidate();
    initVerifyCompany();
    initLogin();
});
