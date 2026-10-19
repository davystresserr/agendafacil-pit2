// AgendaFácil: validação no cliente, feedback imediato e confirmação de ações destrutivas.
(function () {
  "use strict";

  // Menu responsivo
  const botaoMenu = document.querySelector("[data-menu]");
  const menu = document.getElementById("menu");
  if (botaoMenu && menu) {
    botaoMenu.addEventListener("click", () => {
      const aberto = menu.classList.toggle("aberto");
      botaoMenu.setAttribute("aria-expanded", String(aberto));
    });
  }

  // Fechar mensagens flash
  document.querySelectorAll("[data-fechar]").forEach((b) =>
    b.addEventListener("click", () => b.closest(".flash").remove())
  );

  // Confirmação de senha em tempo real
  document.querySelectorAll("[data-confirma]").forEach((campo) => {
    const original = document.getElementById(campo.dataset.confirma);
    const aviso = document.querySelector("[data-erro-confirmacao]");
    const checar = () => {
      const diferente = campo.value && campo.value !== original.value;
      campo.classList.toggle("invalido", !!diferente);
      campo.setCustomValidity(diferente ? "As senhas não conferem." : "");
      if (aviso) aviso.hidden = !diferente;
    };
    campo.addEventListener("input", checar);
    original.addEventListener("input", checar);
  });

  // Validação HTML5 com destaque do campo e botão "Enviando..."
  document.querySelectorAll("form[data-validar]").forEach((form) => {
    form.addEventListener("submit", (ev) => {
      let valido = true;
      form.querySelectorAll("input, select, textarea").forEach((el) => {
        const ok = el.checkValidity();
        if (el.type !== "radio") el.classList.toggle("invalido", !ok);
        if (!ok && valido) { el.reportValidity(); el.focus(); }
        valido = valido && ok;
      });
      if (!valido) { ev.preventDefault(); return; }
      const botao = form.querySelector("button[type=submit]");
      if (botao) { botao.disabled = true; botao.dataset.texto = botao.textContent; botao.textContent = "Enviando..."; }
    });
    form.addEventListener("input", (ev) => {
      if (ev.target.checkValidity && ev.target.checkValidity()) ev.target.classList.remove("invalido");
    });
  });

  // Ao escolher a data, busca os horários automaticamente
  document.querySelectorAll("[data-auto-enviar]").forEach((el) =>
    el.addEventListener("change", () => el.value && el.form.submit())
  );

  // Diálogo de confirmação para ações destrutivas
  let dialogo = null;
  function obterDialogo() {
    if (dialogo) return dialogo;
    dialogo = document.createElement("dialog");
    dialogo.innerHTML =
      '<h2 style="margin-top:0">Confirmar ação</h2><p data-texto></p>' +
      '<div class="acoes"><button type="button" class="botao botao-secundario" data-nao>Voltar</button>' +
      '<button type="button" class="botao botao-perigo" data-sim>Sim, confirmar</button></div>';
    document.body.appendChild(dialogo);
    return dialogo;
  }
  document.querySelectorAll("form[data-confirmar]").forEach((form) => {
    form.addEventListener("submit", (ev) => {
      if (form.dataset.confirmado) return;
      ev.preventDefault();
      const d = obterDialogo();
      d.querySelector("[data-texto]").textContent = form.dataset.confirmar;
      d.querySelector("[data-sim]").onclick = () => { form.dataset.confirmado = "1"; d.close(); form.requestSubmit ? form.requestSubmit() : form.submit(); };
      d.querySelector("[data-nao]").onclick = () => d.close();
      if (d.showModal) d.showModal(); else if (window.confirm(form.dataset.confirmar)) { form.dataset.confirmado = "1"; form.submit(); }
    });
  });
})();
