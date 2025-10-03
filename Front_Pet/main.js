// Navegação Mobile
// Verifique se há algum código assim no seu JS:

document.addEventListener("DOMContentLoaded", () => {
  const mobileMenuToggle = document.getElementById("mobileMenuToggle")
  const navMenu = document.getElementById("navMenu")

  if (mobileMenuToggle && navMenu) {
    mobileMenuToggle.addEventListener("click", () => {
      navMenu.classList.toggle("active")
    })

    // Fechar menu ao clicar em um link
    const navLinks = navMenu.querySelectorAll(".nav-link")
    navLinks.forEach((link) => {
      link.addEventListener("click", () => {
        navMenu.classList.remove("active")
      })
    })
  }
})

// Função para abrir modal da galeria
function openModal(imageSrc) {
  const modal = document.getElementById("imageModal")
  const modalImage = document.getElementById("modalImage")

  if (modal && modalImage) {
    modalImage.src = imageSrc
    modal.classList.add("active")
    document.body.style.overflow = "hidden"
  }
}

// Função para fechar modal da galeria
function closeModal() {
  const modal = document.getElementById("imageModal")

  if (modal) {
    modal.classList.remove("active")
    document.body.style.overflow = "auto"
  }
}

// Fechar modal ao clicar fora da imagem
document.addEventListener("click", (e) => {
  const modal = document.getElementById("imageModal")
  if (modal && e.target === modal) {
    closeModal()
  }
})

// Fechar modal com tecla ESC
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeModal()
  }
})

// Função para solicitar informações (página de produtos)
function solicitarInfo(categoria) {
  let mensagem = ""

  switch (categoria) {
    case "limpeza":
      mensagem = "Gostaria de mais informações sobre os serviços de limpeza e banho."
      break
    case "tosa":
      mensagem = "Tenho interesse nos serviços de tosa. Podem me enviar mais detalhes?"
      break
    case "racao":
      mensagem = "Preciso de orientação sobre rações e alimentação para meu pet."
      break
    default:
      mensagem = "Gostaria de mais informações sobre os serviços oferecidos."
  }

  // Redirecionar para página de contato com mensagem pré-preenchida
  const url = `contato.html?msg=${encodeURIComponent(mensagem)}`
  window.location.href = url
}

// Pré-preencher formulário de contato se houver parâmetros na URL
document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search)
  const mensagem = urlParams.get("msg")
  const mensagemField = document.getElementById("mensagem")

  if (mensagem && mensagemField) {
    mensagemField.value = mensagem
  }
})

// Manipulação do formulário de contato
document.addEventListener("DOMContentLoaded", () => {
  const contactForm = document.getElementById("contactForm")

  if (contactForm) {
    contactForm.addEventListener("submit", (e) => {
      e.preventDefault()

      // Coletar dados do formulário
      const formData = new FormData(contactForm)
      const dados = {
        nome: formData.get("nome"),
        email: formData.get("email"),
        telefone: formData.get("telefone"),
        pet: formData.get("pet"),
        servico: formData.get("servico"),
        mensagem: formData.get("mensagem"),
        newsletter: formData.get("newsletter") ? true : false,
      }

      // Validação básica
      if (!dados.nome || !dados.email || !dados.telefone || !dados.mensagem) {
        alert("Por favor, preencha todos os campos obrigatórios.")
        return
      }

      // Validação de email
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(dados.email)) {
        alert("Por favor, insira um e-mail válido.")
        return
      }

      // Simular envio do formulário
      const submitButton = contactForm.querySelector(".submit-button")
      const originalText = submitButton.textContent

      submitButton.textContent = "Enviando..."
      submitButton.disabled = true

      // Simular delay de envio
      setTimeout(() => {
        alert("Mensagem enviada com sucesso! Entraremos em contato em breve.")
        contactForm.reset()
        submitButton.textContent = originalText
        submitButton.disabled = false

        // Se inscreveu na newsletter
        if (dados.newsletter) {
          console.log("Cliente inscrito na newsletter:", dados.email)
        }

        console.log("Dados do formulário:", dados)
      }, 2000)
    })
  }
})

// Animações suaves ao rolar a página
document.addEventListener("DOMContentLoaded", () => {
  // Observador para animações de entrada
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1"
        entry.target.style.transform = "translateY(0)"
      }
    })
  }, observerOptions)

  // Aplicar animação aos cards de serviço
  const serviceCards = document.querySelectorAll(".service-card")
  serviceCards.forEach((card) => {
    card.style.opacity = "0"
    card.style.transform = "translateY(30px)"
    card.style.transition = "opacity 0.6s ease, transform 0.6s ease"
    observer.observe(card)
  })

  // Aplicar animação aos itens da galeria
  const galleryItems = document.querySelectorAll(".gallery-item")
  galleryItems.forEach((item, index) => {
    item.style.opacity = "0"
    item.style.transform = "translateY(30px)"
    item.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`
    observer.observe(item)
  })
})

// Smooth scroll para links internos
document.addEventListener("DOMContentLoaded", () => {
  const links = document.querySelectorAll('a[href^="#"]')

  links.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault()

      const targetId = this.getAttribute("href").substring(1)
      const targetElement = document.getElementById(targetId)

      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }
    })
  })
})

// Função para destacar link ativo na navegação
document.addEventListener("DOMContentLoaded", () => {
  const currentPage = window.location.pathname.split("/").pop() || "index.html"
  const navLinks = document.querySelectorAll(".nav-link")

  navLinks.forEach((link) => {
    const linkPage = link.getAttribute("href")
    if (linkPage === currentPage || (currentPage === "" && linkPage === "index.html")) {
      link.classList.add("active")
    } else {
      link.classList.remove("active")
    }
  })
})

// Função para formatar telefone automaticamente
document.addEventListener("DOMContentLoaded", () => {
  const telefoneInput = document.getElementById("telefone")

  if (telefoneInput) {
    telefoneInput.addEventListener("input", (e) => {
      let value = e.target.value.replace(/\D/g, "")

      if (value.length <= 11) {
        if (value.length <= 2) {
          value = value.replace(/(\d{0,2})/, "($1")
        } else if (value.length <= 6) {
          value = value.replace(/(\d{2})(\d{0,4})/, "($1) $2")
        } else if (value.length <= 10) {
          value = value.replace(/(\d{2})(\d{4})(\d{0,4})/, "($1) $2-$3")
        } else {
          value = value.replace(/(\d{2})(\d{5})(\d{0,4})/, "($1) $2-$3")
        }
      }

      e.target.value = value
    })
  }
})

// Adicionar efeito de loading aos botões
document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".cta-button, .submit-button")

  buttons.forEach((button) => {
    button.addEventListener("click", function () {
      if (!this.disabled) {
        this.style.transform = "scale(0.98)"
        setTimeout(() => {
          this.style.transform = "scale(1)"
        }, 150)
      }
    })
  })
})
// ...existing code...

// Alternância de tema claro/escuro
document.addEventListener("DOMContentLoaded", () => {
  const toggleThemeBtn = document.getElementById("toggleTheme");
  if (!toggleThemeBtn) return;

  // Aplica o tema salvo ao carregar
  if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark");
    toggleThemeBtn.textContent = "🌞";
  } else {
    toggleThemeBtn.textContent = "🌚";
  }

  toggleThemeBtn.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    const isDark = document.body.classList.contains("dark");
    toggleThemeBtn.textContent = isDark ? "🌞" : "🌚";
    localStorage.setItem("theme", isDark ? "dark" : "light");
  });
});
