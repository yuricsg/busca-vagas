# Job Monitor

Monitor automático simples de vagas Jr.

Roda no **GitHub Actions**, sem servidor, sem custo.

---

## Como funciona

- Busca vagas no **Gupy** e **LinkedIn RSS** a cada 12 horas
- Filtra por palavras-chave do seu perfil
- Remove vagas com "sênior", "pleno", "lead" etc.
- Guarda as vagas já vistas pra não repetir
- Te manda um **email formatado** só com vagas novas

---

## Setup (5 minutos)

### 1. Criar repositório privado no GitHub
Sobe os arquivos desse projeto num repositório **privado**.

### 2. Configurar App Password no Gmail
O Gmail não permite usar sua senha normal via SMTP. Você precisa de uma **App Password**:

1. Acesse [myaccount.google.com/security](https://myaccount.google.com/security)
2. Ative a **verificação em duas etapas** (se não tiver)
3. Vá em **Senhas de app** → Selecione "Email" → "Outro" → nomeie como "Job Monitor"
4. Copie a senha gerada (16 caracteres)

### 3. Adicionar Secrets no GitHub
No repositório → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Adicione três secrets:

| Nome | Valor |
|---|---|
| `EMAIL_SENDER` | seu.email@gmail.com |
| `EMAIL_PASSWORD` | app password do passo anterior |
| `EMAIL_RECIPIENT` | email onde quer receber (pode ser o mesmo) |

### 4. Ativar o GitHub Actions
Vá em **Actions** no repositório e confirme que está habilitado.

Pronto! O monitor vai rodar automaticamente às **06h e 18h** (horário de Brasília).

---

## Rodar manualmente
Em **Actions** → **Job Monitor** → **Run workflow** → **Run workflow**

Útil pra testar se está funcionando.

---

## Customizar palavras-chave
No arquivo `job_monitor.py`, edite as listas:

```python
KEYWORDS = [
    "desenvolvedor full stack júnior",
    # adicione ou remova termos aqui
]

BLACKLIST = [
    "sênior", "pleno", "lead",
    # adicione termos que você quer excluir
]
```

---

## Estrutura do projeto
```
job_monitor/
├── job_monitor.py              # script principal
├── requirements.txt            # dependências Python
├── seen_jobs.json              # vagas já vistas (gerado automaticamente)
└── .github/
    └── workflows/
        └── job_monitor.yml     # agendamento GitHub Actions
```
