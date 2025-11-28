/* ======================================================================
   FUNÇÕES UTILITÁRIAS REUTILIZÁVEIS
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

// Telefone com +55
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

// Validação final do telefone
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

// Busca CEP via ViaCEP
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
   INICIALIZADORES — (RODAM SOMENTE QUANDO NECESSÁRIO)
====================================================================== */

// Logout
function initLogout() {
    const btn = document.getElementById("confirmLogout");
    if (!btn) return;

    btn.addEventListener("click", () => {
        window.location.href = "/";
    });
}

// Register Candidate
function initRegisterCandidate() {
    const form = document.getElementById("candidate-email-form");
    if (!form) return;

    const emailInput = document.getElementById("emailInput");

    form.addEventListener("submit", e => {
        e.preventDefault();

        const email = emailInput.value.trim();
        const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!pattern.test(email)) {
            alert("Digite um e-mail válido.");
            return;
        }

        window.location.href = `/verify/candidate/?email=${encodeURIComponent(email)}`;
    });
}

// Register Company (email + CNPJ)
function initRegisterCompany() {
    const form = document.getElementById("company-register-form");
    if (!form) return;

    const email = document.getElementById("company-email");
    const cnpj = document.getElementById("company-cnpj");

    onlyNumbers(cnpj, 14);

    form.addEventListener("submit", e => {
        e.preventDefault();

        if (!validateCNPJ(cnpj)) return;

        window.location.href = `/register/company/details/?email=${encodeURIComponent(email.value.trim())}`;
    });
}

// Candidate Details
function initDetailsCandidate() {
    const form = document.getElementById("candidate-details-form");
    if (!form) return;

    const cpf = document.querySelector('input[placeholder="CPF"]');
    const telefone = document.querySelector('input[placeholder="Telefone"]');
    const senha = document.querySelector('input[placeholder="Senha"]');
    const confirmar = document.querySelector('input[placeholder="Confirmar Senha"]');
    const cep = document.getElementById("cep");

    onlyNumbers(cpf, 11);
    onlyNumbers(cep, 8);
    initTelefoneMask(telefone);

    lookupCEP(cep, data => {
        document.getElementById("cidade").value = data.localidade;
        document.getElementById("bairro").value = data.bairro;
        document.getElementById("endereco").value = data.logradouro;
    });

    form.addEventListener("submit", e => {
        e.preventDefault();

        if (!validatePassword(senha, confirmar)) return;
        if (!validateCPF(cpf)) return;
        if (!validateTelefone(telefone)) return;

        window.location.href = "/candidate/home/";
    });
}

// Company Details
function initDetailsCompany() {
    const form = document.getElementById("company-details-form");
    if (!form) return;

    const cpf = document.getElementById("cpf");
    const telefone = document.getElementById("telefone");
    const senha = document.getElementById("senha");
    const confirmar = document.getElementById("confirmar-senha");
    const cep = document.getElementById("cep");

    onlyNumbers(cpf, 11);
    onlyNumbers(cep, 8);
    initTelefoneMask(telefone);

    lookupCEP(cep, data => {
        document.getElementById("cidade").value = data.localidade;
        document.getElementById("bairro").value = data.bairro;
        document.getElementById("endereco").value = data.logradouro;
    });

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
   INICIALIZA TODOS (mas só ativa o que existe na página)
====================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    initLogout();
    initRegisterCandidate();
    initRegisterCompany();
    initDetailsCandidate();
    initDetailsCompany();
    initVerifyCandidate();
    initVerifyCompany();
    initLogin();
});
