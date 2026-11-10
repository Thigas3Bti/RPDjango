// Aguarda o carregamento completo do HTML/DOM antes de executar o código
// DOMContentLoaded garante que todos os elementos estejam disponíveis
document.addEventListener("DOMContentLoaded", function () {
    // Seleciona o elemento HTML com id="currentDate" para exibir a data
    // getElementById retorna null se o elemento não existir
    const dateElement = document.getElementById("currentDate");

    // Verifica se o elemento foi encontrado antes de usar (evita erros se não existir)
    if (dateElement) {
        // Cria um novo objeto Date com data/hora atual
        const date = new Date();
        
        // Define as opções de formatação para a data em português
        // weekday: "long" = nome do dia completo (ex: Segunda-feira)
        // day: "2-digit" = dia com 2 dígitos (01, 02, ... 31)
        // month: "long" = nome do mês completo (ex: agosto)
        // year: "numeric" = ano com 4 dígitos (ex: 2024)
        const options = { weekday: "long", day: "2-digit", month: "long", year: "numeric" };
        
        // Formata a data de acordo com a localidade "pt-BR" (português do Brasil)
        // e atribui o resultado ao elemento HTML (replace textContent)
        // Exemplo de resultado: "quinta-feira, 05 de agosto de 2024"
        dateElement.textContent = date.toLocaleDateString("pt-BR", options);
    }
});

const secretCommandScript = document.querySelector("script[data-surprise-url]");
const secretSurpriseUrl = secretCommandScript?.dataset.surpriseUrl;
const secretSurpriseCommand = "surpresa";
let typedSecretCommand = "";

document.addEventListener("keydown", function (event) {
    if (
        event.repeat
        || document.activeElement.matches("input, textarea, select, [contenteditable='true']")
    ) {
        typedSecretCommand = "";
        return;
    }

    if (!secretSurpriseUrl || event.key.length !== 1) {
        return;
    }

    typedSecretCommand = (typedSecretCommand + event.key.toLowerCase())
        .slice(-secretSurpriseCommand.length);

    if (typedSecretCommand === secretSurpriseCommand) {
        window.location.assign(secretSurpriseUrl);
    }
});
