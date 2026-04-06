/* ======================================================================
   INPUT HELPERS
====================================================================== */

function onlyNumbers(input, length = null) {
    if (!input) return;
    input.addEventListener("input", () => {
        let value = input.value.replace(/\D/g, "");
        if (length && value.length > length) value = value.slice(0, length);
        input.value = value;
    });
}

function initTelefoneMask(input) {
    if (!input) return;

    if (!input.value.startsWith("+55")) input.value = "+55 ";

    input.addEventListener("keydown", e => {
        if (input.selectionStart <= 3 && ["Backspace", "Delete"].includes(e.key)) {
            e.preventDefault();
        }
    });

    input.addEventListener("input", () => {
        if (!input.value.startsWith("+55")) input.value = "+55 ";

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

/* ======================================================================
   CEP LOOKUP (ViaCEP)
====================================================================== */

function lookupCEP(cepInput) {
    if (!cepInput) return;

    cepInput.addEventListener("blur", () => {
        const cep = cepInput.value.replace(/\D/g, "");
        if (cep.length !== 8) return;

        fetch(`https://viacep.com.br/ws/${cep}/json/`)
            .then(r => r.json())
            .then(data => {
                if (data.erro) return;
                const cidade = document.getElementById("cidade");
                const bairro = document.getElementById("bairro");
                const endereco = document.getElementById("endereco");
                if (cidade) cidade.value = data.localidade;
                if (bairro) bairro.value = data.bairro;
                if (endereco) endereco.value = data.logradouro;
            })
            .catch(() => {});
    });
}

/* ======================================================================
   VERIFY CODE — auto-advance between boxes
====================================================================== */

function initCodeBoxes() {
    const boxes = document.querySelectorAll(".code-box");
    if (!boxes.length) return;

    boxes.forEach((box, i) => {
        box.addEventListener("input", () => {
            if (box.value && i < boxes.length - 1) {
                boxes[i + 1].focus();
            }
        });

        box.addEventListener("keydown", e => {
            if (e.key === "Backspace" && !box.value && i > 0) {
                boxes[i - 1].focus();
            }
        });
    });
}

/* ======================================================================
   INIT
====================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // CEP auto-fill (candidate and company detail forms)
    lookupCEP(document.getElementById("cep"));

    // Phone mask
    initTelefoneMask(document.getElementById("telefone"));

    // Numeric-only inputs
    onlyNumbers(document.getElementById("cpf"), 11);
    onlyNumbers(document.getElementById("cep"), 8);
    onlyNumbers(document.getElementById("company-cnpj"), 14);

    // Verify code boxes auto-advance
    initCodeBoxes();
});
