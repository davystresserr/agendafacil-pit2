from agendafacil.models import Profissional, Servico
from tests.conftest import login


def test_painel_admin(client, dados):
    login(client, "admin@teste.com")
    html = client.get("/admin/").get_data(as_text=True)
    assert "Administração" in html and "Corte masculino" in html and "serviços ativos" in html


def test_criar_editar_e_desativar_servico(client, dados):
    login(client, "admin@teste.com")
    assert "Novo serviço" in client.get("/admin/servicos/novo").get_data(as_text=True)
    r = client.post("/admin/servicos/novo", data={"nome": "Pigmentação", "preco": "35,50", "duracao_min": "40"},
                    follow_redirects=True)
    assert "Serviço salvo com sucesso." in r.get_data(as_text=True)
    s = Servico.query.filter_by(nome="Pigmentação").one()
    assert str(s.preco) == "35.50"
    assert 'value="35,50"' in client.get(f"/admin/servicos/{s.id}/editar").get_data(as_text=True)
    r = client.post(f"/admin/servicos/{s.id}/editar", data={"nome": "Pigmentação de barba", "preco": "40",
                                                            "duracao_min": "45"}, follow_redirects=True)
    assert "Pigmentação de barba" in r.get_data(as_text=True)
    r = client.post(f"/admin/servicos/{s.id}/alternar", follow_redirects=True)
    assert "Serviço desativado." in r.get_data(as_text=True) and not s.ativo
    assert "Pigmentação de barba" not in client.get("/").get_data(as_text=True)
    assert client.get("/admin/servicos/999/editar").status_code == 404


def test_servico_invalido(client, dados):
    login(client, "admin@teste.com")
    r = client.post("/admin/servicos/novo", data={"nome": "", "preco": "0", "duracao_min": "1000"})
    html = r.get_data(as_text=True)
    assert r.status_code == 400 and "maior que zero" in html and "entre 5 e 480" in html
    r = client.post(f"/admin/servicos/{dados['corte'].id}/editar", data={"nome": "Barba", "preco": "10",
                                                                         "duracao_min": "30"})
    assert r.status_code == 400 and "Já existe um serviço" in r.get_data(as_text=True)


def test_cadastrar_profissional(client, dados):
    login(client, "admin@teste.com")
    assert "Cadastrar profissional" in client.get("/admin/profissionais").get_data(as_text=True)
    r = client.post("/admin/profissionais", data={"nome": "Bia Souza", "email": "bia@x.com", "senha": "12345678",
                                                  "especialidade": "Cabeleireira",
                                                  "servicos": [str(dados["escova"].id)]}, follow_redirects=True)
    assert "Profissional Bia Souza cadastrado." in r.get_data(as_text=True)
    assert Profissional.query.count() == 2
    r = client.post("/admin/profissionais", data={"nome": "Bia 2", "email": "bia@x.com", "senha": "12345678",
                                                  "servicos": [str(dados["escova"].id)]})
    html = r.get_data(as_text=True)
    assert r.status_code == 400 and "já está cadastrado" in html and 'value="Bia 2"' in html


def test_admin_lista_e_cancela_qualquer_agendamento(client, dados):
    login(client, "ana@teste.com")
    client.post("/agendar", data={"servico_id": dados["corte"].id, "profissional_id": dados["profissional"].id,
                                  "inicio": "2026-10-19T09:00"})
    client.post("/logout")
    login(client, "admin@teste.com")
    html = client.get("/admin/agendamentos").get_data(as_text=True)
    assert "Ana Cliente" in html and "19/10/2026 09:00" in html
    from agendafacil.models import Agendamento
    ag = Agendamento.query.one()
    r = client.post(f"/agendamentos/{ag.id}/cancelar", follow_redirects=True)
    assert "Agendamento cancelado" in r.get_data(as_text=True) and r.request.path == "/admin/agendamentos"
