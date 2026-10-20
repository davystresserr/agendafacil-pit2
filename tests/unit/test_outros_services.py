import pytest

from agendafacil.models import Papel
from agendafacil.services import auth_service, profissional_service, servico_service
from agendafacil.services.erros import RegraNegocioError, ValidacaoError


def test_cadastro_e_autenticacao(db):
    u = auth_service.cadastrar_cliente("Joana Lima", "JOANA@x.com", "", "12345678", "12345678")
    assert u.email == "joana@x.com" and u.papel == Papel.CLIENTE and u.telefone is None
    assert auth_service.autenticar("joana@x.com", "12345678").id == u.id
    with pytest.raises(RegraNegocioError, match="incorretos"):
        auth_service.autenticar("joana@x.com", "errada")
    with pytest.raises(RegraNegocioError, match="incorretos"):
        auth_service.autenticar("ninguem@x.com", "12345678")


def test_email_unico_no_cadastro(db, dados):
    with pytest.raises(ValidacaoError) as e:
        auth_service.cadastrar_cliente("Outra Ana", "ana@teste.com", None, "12345678")
    assert "já está cadastrado" in e.value.erros["email"]


def test_usuario_inativo_nao_autentica(db, dados):
    dados["cliente"].ativo = False
    db.session.commit()
    with pytest.raises(RegraNegocioError):
        auth_service.autenticar("ana@teste.com", "senha-teste-123")


def test_papel_invalido(db):
    with pytest.raises(ValidacaoError) as e:
        auth_service.criar_usuario("Fulano", "f@x.com", "12345678", papel="root")
    assert "papel" in e.value.erros


def test_crud_servico(db):
    s = servico_service.criar("Hidratação", "50,00", "40", "  ")
    assert s.preco == 50 and s.descricao is None
    with pytest.raises(ValidacaoError) as e:
        servico_service.criar("hidratação", "10", "10")
    assert "nome" in e.value.erros
    with pytest.raises(ValidacaoError) as e:
        servico_service.criar("Novo", "-1", "0")
    assert set(e.value.erros) == {"preco", "duracao_min"}
    servico_service.atualizar(s, "Hidratação profunda", "55", "50", "Com máscara")
    assert s.nome == "Hidratação profunda" and s.duracao_min == 50
    servico_service.alternar_ativo(s)
    assert not s.ativo and servico_service.listar_ativos() == [] and servico_service.listar_todos() == [s]


def test_cadastrar_profissional(db, dados):
    p = profissional_service.cadastrar("Bia Souza", "bia@x.com", "12345678", "Manicure", "", [str(dados["escova"].id)])
    assert p.usuario.papel == Papel.PROFISSIONAL and p.realiza(dados["escova"]) and p.nome == "Bia Souza"
    assert p in profissional_service.listar_ativos() and len(profissional_service.listar_todos()) == 2
    assert profissional_service.que_realizam(dados["escova"]) == [p]


def test_cadastrar_profissional_exige_servico_e_email_valido(db, dados):
    with pytest.raises(ValidacaoError) as e:
        profissional_service.cadastrar("Bia Souza", "bia@x.com", "12345678", servico_ids=[])
    assert "servicos" in e.value.erros
    with pytest.raises(ValidacaoError) as e:
        profissional_service.cadastrar("Bia", "ana@teste.com", "123", servico_ids=[])
    assert {"email", "senha", "servicos"} <= set(e.value.erros)


def test_horarios_do_profissional(db, dados):
    p = dados["profissional"]
    h = profissional_service.adicionar_horario(p, "6", "10:00", "14:00")
    assert h.dia_nome == "Domingo"
    with pytest.raises(RegraNegocioError, match="sobrepõe"):
        profissional_service.adicionar_horario(p, "6", "13:00", "15:00")
    with pytest.raises(ValidacaoError) as e:
        profissional_service.adicionar_horario(p, "9", "", "x")
    assert set(e.value.erros) == {"dia_semana", "hora_inicio", "hora_fim"}
    with pytest.raises(ValidacaoError):
        profissional_service.adicionar_horario(p, "6", "16:00", "15:00")
    profissional_service.remover_horario(p, h.id)
    with pytest.raises(RegraNegocioError, match="não encontrado"):
        profissional_service.remover_horario(p, h.id)
