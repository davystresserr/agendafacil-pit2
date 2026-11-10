# Deploy: Vercel + Neon + domínio no Cloudflare

Aplicação publicada: https://agendafacil-wine.vercel.app

## 1. Pré-requisitos

- Repositório público no GitHub (`agendafacil-pit2`) com este código.
- Conta na [Vercel](https://vercel.com) (pode entrar com o GitHub).
- Conta no [Neon](https://neon.tech) para o PostgreSQL gratuito.
- Um domínio gerenciado no [Cloudflare](https://dash.cloudflare.com) (opcional, para usar um endereço próprio em vez de `*.vercel.app`).

> Por que Vercel e Neon: no plano gratuito do Render o site hibernava e mostrava uma tela de carregamento de até 1 minuto, e o PostgreSQL gratuito expirava em 30 dias. Na Vercel a aplicação roda como função serverless (sem tela de espera) e o banco do Neon não expira.

## 2. Criar o banco no Neon

1. No Neon, crie um projeto na região **AWS South America East 1 (São Paulo)**.
2. Em **Connect**, desligue **Connection pooling** e copie a connection string (`postgresql://…?sslmode=require…`). Ela contém a senha do banco: não a coloque no repositório.
3. No seu computador, crie as tabelas e os dados de demonstração apontando para o Neon:

```bash
export DATABASE_URL='postgresql://...'      # connection string do Neon
export SEED_PASSWORD='uma-senha-forte'      # senha dos usuários de demonstração
flask --app src/wsgi.py db upgrade          # migrações (Alembic)
flask --app src/wsgi.py seed                # serviços, profissionais e usuários (idempotente)
```

A Vercel não roda migrações: sempre que houver uma migração nova, repita o `db upgrade` acima.

## 3. Publicar na Vercel

1. Na Vercel: **Add New → Project** e importe o repositório `agendafacil-pit2`. A Vercel detecta o Flask e usa `src/wsgi.py` como ponto de entrada.
2. Em **Settings → Environment Variables**, cadastre as variáveis abaixo (ambientes Production e Preview).
3. Faça o deploy. Cada `git push` na branch `main` publica de novo.
4. O endereço `/saude` deve responder `{"status":"ok"}`.

O arquivo [`vercel.json`](../vercel.json) fixa a função na região `gru1` (São Paulo), a mesma do banco.

### Variáveis de ambiente usadas

| Variável | Valor | Função |
|---|---|---|
| `DATABASE_URL` | connection string do Neon | conexão com o PostgreSQL (o app converte `postgresql://` para o driver `psycopg`) |
| `SECRET_KEY` | texto aleatório longo | assinatura do cookie de sessão |
| `FLASK_ENV` | `production` | ativa cookies `Secure`, ProxyFix e exige `SECRET_KEY` |
| `TZ_APP` | `America/Sao_Paulo` | fuso do salão |

### Observações do plano gratuito

- A função "esfria" quando fica sem uso; o primeiro acesso depois disso leva cerca de 1 a 2 segundos a mais, sem tela de espera.
- O banco do Neon suspende quando fica sem uso e volta no próximo acesso, em menos de 1 segundo. Ele não expira.
- Para começar o banco do zero, crie um banco novo no Neon, rode o passo 2.3 e troque `DATABASE_URL` na Vercel.

## 4. Domínio próprio com Cloudflare

Exemplo: usar `agenda.seudominio.com.br`.

### 4.1 Na Vercel
1. Abra o projeto `agendafacil` → **Settings → Domains → Add**.
2. Digite `agenda.seudominio.com.br` e salve. A Vercel mostra o destino do CNAME (`cname.vercel-dns.com`).

### 4.2 No Cloudflare
1. Painel do Cloudflare → selecione o domínio → **DNS → Records → Add record**.
2. Preencha:

   | Campo | Valor |
   |---|---|
   | Type | `CNAME` |
   | Name | `agenda` |
   | Target | `cname.vercel-dns.com` (o valor mostrado pela Vercel) |
   | Proxy status | **DNS only (nuvem cinza)** |
   | TTL | Auto |

3. Salve e volte à Vercel. Em alguns minutos o domínio aparece como válido e a Vercel emite o certificado HTTPS.
4. Mantenha a nuvem cinza: a Vercel já entrega HTTPS e CDN, e o proxy do Cloudflare na frente atrapalha a emissão e a renovação do certificado.

> Para usar o domínio raiz (`seudominio.com.br`, sem subdomínio), o Cloudflare aceita CNAME no apex por meio do *CNAME flattening*: crie o registro com Name `@` e o mesmo Target.

## 5. Rodar localmente com PostgreSQL (Docker)

```bash
docker compose up -d                       # PostgreSQL 16 em localhost:5432
cp .env.example .env                       # ajuste SECRET_KEY e SEED_PASSWORD
flask --app src/wsgi.py db upgrade
flask --app src/wsgi.py seed
flask --app src/wsgi.py run --debug
```

## 6. Checklist pós-deploy

- [ ] `/saude` responde `{"status":"ok"}`
- [ ] Login com `admin@agendafacil.com` funciona
- [ ] Um cliente novo consegue se cadastrar e agendar
- [ ] O domínio do Cloudflare abre com cadeado (HTTPS)
- [ ] Link da aplicação preenchido em `entrega/PIT_atividade_8_preenchido.docx` e no README
