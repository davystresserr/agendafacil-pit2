# Deploy: Render + domínio no Cloudflare

## 1. Pré-requisitos

- Repositório público no GitHub (`agendafacil-pit2`) com este código.
- Conta no [Render](https://render.com) (pode entrar com o GitHub).
- Um domínio gerenciado no [Cloudflare](https://dash.cloudflare.com) (opcional, para usar um endereço próprio em vez de `*.onrender.com`).

## 2. Criar banco e aplicação no Render (Blueprint)

O arquivo [`render.yaml`](../render.yaml) descreve tudo: um PostgreSQL 16 gratuito e um serviço web Python.

1. No Render: **New → Blueprint**.
2. Conecte a conta do GitHub e escolha o repositório `agendafacil-pit2`.
3. O Render lê o `render.yaml` e mostra os recursos `agendafacil-db` (PostgreSQL) e `agendafacil` (web).
4. Ele vai pedir o valor de **`SEED_PASSWORD`**: defina uma senha forte. Ela será a senha dos usuários de demonstração (`admin@`, `carlos@`, `ana@`, `cliente@agendafacil.com`). Guarde-a para passar aos colegas que forem testar, se necessário.
5. Clique em **Apply**. O primeiro deploy:
   - instala as dependências (`pip install -r requirements.txt`);
   - executa [`start.sh`](../start.sh), que roda `flask db upgrade` (migrações), `flask seed` (dados de demonstração, idempotente) e inicia o `gunicorn`.
6. Quando o status ficar **Live**, abra `https://agendafacil.onrender.com` (ou o nome que o Render gerar). O endereço `/saude` deve responder `{"status":"ok"}`.

### Variáveis de ambiente usadas

| Variável | Origem | Função |
|---|---|---|
| `DATABASE_URL` | gerada pelo Render a partir do banco | conexão com o PostgreSQL (o app converte `postgres://` para o driver `psycopg`) |
| `SECRET_KEY` | gerada automaticamente (`generateValue`) | assinatura do cookie de sessão |
| `FLASK_ENV=production` | `render.yaml` | ativa cookies `Secure`, ProxyFix e exige `SECRET_KEY` |
| `SEED_PASSWORD` | você informa no painel | senha dos usuários de demonstração |
| `TZ_APP` | `render.yaml` | fuso do salão (`America/Sao_Paulo`) |
| `PYTHON_VERSION` | `render.yaml` | Python 3.12 |

### Observações do plano gratuito

- O serviço web **hiberna** após cerca de 15 minutos sem acesso; o primeiro acesso depois disso leva de 30 a 60 segundos. Avise os colegas testadores.
- O PostgreSQL gratuito do Render **expira após 30 dias**. Para a apresentação, isso é suficiente; depois, é preciso recriá-lo ou migrar para um plano pago.

## 3. Domínio próprio com Cloudflare

Exemplo: usar `agenda.seudominio.com.br`.

### 3.1 No Render
1. Abra o serviço `agendafacil` → **Settings → Custom Domains → Add Custom Domain**.
2. Digite `agenda.seudominio.com.br` e salve. O Render mostra o destino do CNAME, algo como `agendafacil.onrender.com`.

### 3.2 No Cloudflare
1. Painel do Cloudflare → selecione o domínio → **DNS → Records → Add record**.
2. Preencha:

   | Campo | Valor |
   |---|---|
   | Type | `CNAME` |
   | Name | `agenda` |
   | Target | `agendafacil.onrender.com` (o valor mostrado pelo Render) |
   | Proxy status | **DNS only (nuvem cinza)** até o Render emitir o certificado |
   | TTL | Auto |

3. Salve e volte ao Render. Clique em **Verify**. Em alguns minutos o domínio aparece como verificado e o Render emite o certificado HTTPS (Let's Encrypt).
4. Depois da verificação, se quiser usar o proxy do Cloudflare (nuvem laranja):
   - em **SSL/TLS → Overview**, selecione o modo **Full (strict)**. Os modos *Flexible* e *Full* sem *strict* causam loop de redirecionamento ou deixam a conexão até o Render sem validação;
   - ative a nuvem laranja no registro CNAME.

> Para usar o domínio raiz (`seudominio.com.br`, sem subdomínio), o Cloudflare aceita CNAME no apex por meio do *CNAME flattening*: crie o registro com Name `@` e o mesmo Target.

## 4. Rodar localmente com PostgreSQL (Docker)

```bash
docker compose up -d                       # PostgreSQL 16 em localhost:5432
cp .env.example .env                       # ajuste SECRET_KEY e SEED_PASSWORD
flask --app src/wsgi.py db upgrade
flask --app src/wsgi.py seed
flask --app src/wsgi.py run --debug
```

## 5. Checklist pós-deploy

- [ ] `/saude` responde `{"status":"ok"}`
- [ ] Login com `admin@agendafacil.com` funciona
- [ ] Um cliente novo consegue se cadastrar e agendar
- [ ] O domínio do Cloudflare abre com cadeado (HTTPS)
- [ ] Link da aplicação preenchido em `entrega/PIT_atividade_8_preenchido.docx` e no README
