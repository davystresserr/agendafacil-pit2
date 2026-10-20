from tests.conftest import Config, login


def test_pagina_inicial_lista_servicos(client, dados):
    r = client.get("/")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "Corte masculino" in html and "R$ 45,00" in html


def test_cadastro_login_logout(client, db):
    r = client.post("/cadastro", data={"nome": "Paula Reis", "email": "paula@x.com", "telefone": "43 99999-1111",
                                       "senha": "12345678", "confirmacao": "12345678"}, follow_redirects=True)
    assert "Conta criada com sucesso" in r.get_data(as_text=True)
    r = client.post("/logout", follow_redirects=True)
    assert "Você saiu" in r.get_data(as_text=True)
    r = login(client, "paula@x.com", "12345678")
    assert "Olá, Paula!" in r.get_data(as_text=True)
    assert client.get("/login").status_code == 302  # já logado
    assert client.get("/cadastro").status_code == 302


def test_cadastro_invalido_mostra_erros_e_mantem_dados(client, dados):
    r = client.post("/cadastro", data={"nome": "Ana 2", "email": "ana@teste.com", "senha": "123",
                                       "confirmacao": "123"})
    html = r.get_data(as_text=True)
    assert r.status_code == 400 and "já está cadastrado" in html and "pelo menos 8" in html
    assert 'value="Ana 2"' in html


def test_login_invalido(client, dados):
    r = client.post("/login", data={"email": "ana@teste.com", "senha": "errada"})
    assert r.status_code == 401 and "E-mail ou senha incorretos." in r.get_data(as_text=True)


def test_login_redireciona_por_papel_e_next(client, dados):
    assert login(client, "carlos@teste.com").request.path == "/profissional/"
    client.post("/logout")
    assert login(client, "admin@teste.com").request.path == "/admin/"
    client.post("/logout")
    r = client.post("/login?next=/meus-agendamentos", data={"email": "ana@teste.com", "senha": "senha-teste-123"})
    assert r.headers["Location"] == "/meus-agendamentos"
    client.post("/logout")
    r = client.post("/login?next=https://malicioso.com", data={"email": "ana@teste.com", "senha": "senha-teste-123"})
    assert r.headers["Location"] == "/"


def test_rota_protegida_exige_login(client, dados):
    r = client.get("/meus-agendamentos")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_controle_de_acesso_por_papel(client, dados):
    login(client, "ana@teste.com")
    assert client.get("/admin/").status_code == 403
    assert client.get("/profissional/").status_code == 403
    client.post("/logout")
    login(client, "carlos@teste.com")
    assert client.get("/agendar").status_code == 403
    assert "Acesso negado" in client.get("/admin/").get_data(as_text=True)


def test_paginas_de_erro(client, db):
    r = client.get("/nao-existe")
    assert r.status_code == 404 and "Página não encontrada" in r.get_data(as_text=True)
    assert client.get("/saude").get_json() == {"status": "ok"}


def test_erro_500_personalizado_e_rollback(app, client, db):
    app.config["PROPAGATE_EXCEPTIONS"] = False

    @app.get("/explode")
    def explode():
        raise RuntimeError("falha simulada")

    r = client.get("/explode")
    assert r.status_code == 500 and "Algo deu errado" in r.get_data(as_text=True)


def test_csrf_bloqueia_post_sem_token(dados):
    from agendafacil import create_app

    class ComCSRF(Config):
        WTF_CSRF_ENABLED = True

    app = create_app(ComCSRF)
    with app.app_context():
        from agendafacil.extensions import db
        db.create_all()
        c = app.test_client()
        r = c.post("/login", data={"email": "x@x.com", "senha": "12345678"}, follow_redirects=True)
        assert "Sua sessão expirou" in r.get_data(as_text=True)
        html = c.get("/login").get_data(as_text=True)
        token = html.split('name="csrf_token" value="')[1].split('"')[0]
        r = c.post("/login", data={"email": "x@x.com", "senha": "12345678", "csrf_token": token})
        assert r.status_code == 401  # passou pelo CSRF, falhou na autenticação
        db.drop_all()
