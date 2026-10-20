from agendafacil.models import Agendamento, StatusAgendamento
from tests.conftest import criar_usuario, login


def agendar(client, dados, inicio="2026-10-20T10:00"):
    return client.post("/agendar", data={"servico_id": dados["corte"].id, "profissional_id": dados["profissional"].id,
                                         "inicio": inicio, "observacao": "teste"}, follow_redirects=True)


def test_fluxo_de_agendamento_em_passos(client, dados):
    login(client, "ana@teste.com")
    assert "Qual serviço você deseja?" in client.get("/agendar").get_data(as_text=True)
    html = client.get(f"/agendar?servico_id={dados['corte'].id}").get_data(as_text=True)
    assert "Escolha o profissional" in html and "Carlos Barbeiro" in html
    html = client.get(f"/agendar?servico_id={dados['corte'].id}&profissional_id={dados['profissional'].id}"
                      "&data=2026-10-20").get_data(as_text=True)
    assert 'value="2026-10-20T09:00"' in html and "Confirmar agendamento" in html


def test_data_passada_e_dia_sem_horario(client, dados):
    login(client, "ana@teste.com")
    base = f"/agendar?servico_id={dados['corte'].id}&profissional_id={dados['profissional'].id}"
    assert "a partir de hoje" in client.get(base + "&data=2026-10-01").get_data(as_text=True)
    assert "Nenhum horário livre" in client.get(base + "&data=2026-10-25").get_data(as_text=True)


def test_profissional_que_nao_realiza_servico_e_ignorado(client, dados):
    login(client, "ana@teste.com")
    html = client.get(f"/agendar?servico_id={dados['escova'].id}&profissional_id={dados['profissional'].id}")
    assert "Nenhum profissional realiza" in html.get_data(as_text=True)


def test_agendar_e_listar(client, dados):
    login(client, "ana@teste.com")
    r = agendar(client, dados)
    html = r.get_data(as_text=True)
    assert r.request.path == "/meus-agendamentos"
    assert "Agendamento confirmado" in html and "20/10/2026 10:00" in html and "Cancelar" in html


def test_agendar_horario_ocupado(client, dados):
    login(client, "ana@teste.com")
    agendar(client, dados)
    r = agendar(client, dados)
    assert "acabou de ser ocupado" in r.get_data(as_text=True) and r.request.path == "/agendar"
    assert Agendamento.query.count() == 1


def test_agendar_com_dados_incompletos(client, dados):
    login(client, "ana@teste.com")
    r = client.post("/agendar", data={"servico_id": dados["corte"].id}, follow_redirects=True)
    assert "Escolha serviço, profissional e horário." in r.get_data(as_text=True)


def test_cancelar_pelo_cliente(client, dados):
    login(client, "ana@teste.com")
    agendar(client, dados)
    ag = Agendamento.query.one()
    r = client.post(f"/agendamentos/{ag.id}/cancelar", follow_redirects=True)
    assert "Agendamento cancelado" in r.get_data(as_text=True) and ag.status == StatusAgendamento.CANCELADO


def test_cancelamento_tardio_e_bloqueado(app, client, dados):
    login(client, "ana@teste.com")
    agendar(client, dados, "2026-10-19T09:30")  # 1h30 depois do "agora" fixo
    ag = Agendamento.query.one()
    html = client.get("/meus-agendamentos").get_data(as_text=True)
    assert "Cancelamento indisponível" in html
    r = client.post(f"/agendamentos/{ag.id}/cancelar", follow_redirects=True)
    assert "2 horas de antecedência" in r.get_data(as_text=True) and ag.status == StatusAgendamento.AGENDADO


def test_cancelar_agendamento_de_outro_cliente(client, dados):
    login(client, "ana@teste.com")
    agendar(client, dados)
    ag_id = Agendamento.query.one().id
    client.post("/logout")
    criar_usuario("Intruso", "intruso@teste.com")
    login(client, "intruso@teste.com")
    r = client.post(f"/agendamentos/{ag_id}/cancelar", follow_redirects=True)
    assert "não tem permissão" in r.get_data(as_text=True)
    assert client.post("/agendamentos/999/cancelar").status_code == 404


def test_painel_profissional_concluir_e_cancelar(app, client, dados):
    login(client, "ana@teste.com")
    agendar(client, dados, "2026-10-19T09:00")
    agendar(client, dados, "2026-10-20T10:00")
    client.post("/logout")
    login(client, "carlos@teste.com")
    html = client.get("/profissional/").get_data(as_text=True)
    assert "Ana Cliente" in html and "Meus horários disponíveis" in html
    a1, a2 = Agendamento.query.order_by(Agendamento.inicio).all()
    r = client.post(f"/agendamentos/{a1.id}/concluir", follow_redirects=True)
    assert "ainda não começou" in r.get_data(as_text=True)
    app.config["AGORA_FIXO"] = app.config["AGORA_FIXO"].replace(hour=9, minute=10)
    r = client.post(f"/agendamentos/{a1.id}/concluir", follow_redirects=True)
    assert "concluído" in r.get_data(as_text=True) and a1.status == StatusAgendamento.CONCLUIDO
    r = client.post(f"/agendamentos/{a2.id}/cancelar", follow_redirects=True)
    assert "cancelado" in r.get_data(as_text=True) and r.request.path == "/profissional/"
    assert client.post("/agendamentos/999/concluir").status_code == 404


def test_profissional_gerencia_horarios(client, dados):
    login(client, "carlos@teste.com")
    r = client.post("/profissional/horarios", data={"dia_semana": "6", "hora_inicio": "10:00", "hora_fim": "12:00"},
                    follow_redirects=True)
    assert "Horário adicionado." in r.get_data(as_text=True)
    r = client.post("/profissional/horarios", data={"dia_semana": "6", "hora_inicio": "11:00", "hora_fim": "13:00"},
                    follow_redirects=True)
    assert "sobrepõe" in r.get_data(as_text=True)
    r = client.post("/profissional/horarios", data={"dia_semana": "6", "hora_inicio": "", "hora_fim": "13:00"},
                    follow_redirects=True)
    assert "Informe a hora de início." in r.get_data(as_text=True)
    h = [h for h in dados["profissional"].horarios if h.dia_semana == 6][0]
    r = client.post(f"/profissional/horarios/{h.id}/remover", follow_redirects=True)
    assert "Horário removido." in r.get_data(as_text=True)
    r = client.post(f"/profissional/horarios/{h.id}/remover", follow_redirects=True)
    assert "não encontrado" in r.get_data(as_text=True)


def test_usuario_profissional_sem_cadastro_de_profissional(client, dados):
    from agendafacil.models import Papel
    criar_usuario("Sem Perfil", "semperfil@teste.com", Papel.PROFISSIONAL)
    login(client, "semperfil@teste.com")
    assert client.get("/profissional/").status_code == 403
