import sqlite3
import sys

from datetime import datetime, timedelta
from pathlib import Path


def obter_diretorio_aplicacao():
    if getattr(
        sys,
        "frozen",
        False
    ):
        return (
            Path(sys.executable)
            .resolve()
            .parent
        )

    return (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )


DIRETORIO_DADOS = (
    obter_diretorio_aplicacao()
    / "data"
)

ARQUIVO_BANCO = (
    DIRETORIO_DADOS
    / "incidents.db"
)


def _conectar():
    DIRETORIO_DADOS.mkdir(
        parents=True,
        exist_ok=True
    )

    conexao = sqlite3.connect(
        ARQUIVO_BANCO,
        timeout=10
    )

    conexao.row_factory = sqlite3.Row

    conexao.execute(
        "PRAGMA journal_mode=WAL;"
    )

    conexao.execute(
        "PRAGMA foreign_keys=ON;"
    )

    return conexao


def inicializar_banco():
    with _conectar() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS incidentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                tipo TEXT NOT NULL,
                origem TEXT NOT NULL,
                endereco TEXT,

                status_inicial TEXT NOT NULL,
                causa_provavel TEXT,

                inicio TEXT NOT NULL,
                fim TEXT,
                duracao_segundos INTEGER,

                max_servicos_afetados INTEGER DEFAULT 0,
                max_perda REAL DEFAULT 0,
                max_latencia REAL DEFAULT 0,
                max_oscilacao REAL DEFAULT 0,

                detalhes TEXT,

                encerrado INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_incidentes_inicio
            ON incidentes(inicio)
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_incidentes_origem
            ON incidentes(origem)
            """
        )

        conexao.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_incidentes_encerrado
            ON incidentes(encerrado)
            """
        )


def _agora_iso():
    return datetime.now().isoformat(
        timespec="seconds"
    )


def abrir_incidente(
    tipo,
    origem,
    status_inicial,
    endereco="",
    causa_provavel="",
    max_servicos_afetados=0,
    max_perda=0.0,
    max_latencia=0.0,
    max_oscilacao=0.0,
    detalhes=""
):
    inicializar_banco()

    inicio = _agora_iso()

    with _conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO incidentes (
                tipo,
                origem,
                endereco,
                status_inicial,
                causa_provavel,
                inicio,
                max_servicos_afetados,
                max_perda,
                max_latencia,
                max_oscilacao,
                detalhes,
                encerrado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                tipo,
                origem,
                endereco,
                status_inicial,
                causa_provavel,
                inicio,
                int(max_servicos_afetados),
                float(max_perda),
                float(max_latencia),
                float(max_oscilacao),
                detalhes
            )
        )

        return cursor.lastrowid


def atualizar_metricas_incidente(
    incidente_id,
    max_servicos_afetados=None,
    max_perda=None,
    max_latencia=None,
    max_oscilacao=None,
    causa_provavel=None,
    detalhes=None
):
    inicializar_banco()

    campos = []
    valores = []

    if max_servicos_afetados is not None:
        campos.append(
            "max_servicos_afetados = MAX(max_servicos_afetados, ?)"
        )
        valores.append(
            int(max_servicos_afetados)
        )

    if max_perda is not None:
        campos.append(
            "max_perda = MAX(max_perda, ?)"
        )
        valores.append(
            float(max_perda)
        )

    if max_latencia is not None:
        campos.append(
            "max_latencia = MAX(max_latencia, ?)"
        )
        valores.append(
            float(max_latencia)
        )

    if max_oscilacao is not None:
        campos.append(
            "max_oscilacao = MAX(max_oscilacao, ?)"
        )
        valores.append(
            float(max_oscilacao)
        )

    if causa_provavel is not None:
        campos.append(
            "causa_provavel = ?"
        )
        valores.append(
            causa_provavel
        )

    if detalhes is not None:
        campos.append(
            "detalhes = ?"
        )
        valores.append(
            detalhes
        )

    if not campos:
        return False

    valores.append(
        incidente_id
    )

    with _conectar() as conexao:
        cursor = conexao.execute(
            f"""
            UPDATE incidentes
            SET {", ".join(campos)}
            WHERE id = ?
              AND encerrado = 0
            """,
            valores
        )

        return cursor.rowcount > 0


def encerrar_incidente(
    incidente_id,
    causa_provavel=None,
    detalhes=None
):
    inicializar_banco()

    with _conectar() as conexao:
        registro = conexao.execute(
            """
            SELECT inicio
            FROM incidentes
            WHERE id = ?
              AND encerrado = 0
            """,
            (
                incidente_id,
            )
        ).fetchone()

        if registro is None:
            return False

        inicio = datetime.fromisoformat(
            registro["inicio"]
        )

        fim = datetime.now()

        duracao = max(
            0,
            int(
                (
                    fim - inicio
                ).total_seconds()
            )
        )

        campos = [
            "fim = ?",
            "duracao_segundos = ?",
            "encerrado = 1"
        ]

        valores = [
            fim.isoformat(
                timespec="seconds"
            ),
            duracao
        ]

        if causa_provavel is not None:
            campos.append(
                "causa_provavel = ?"
            )
            valores.append(
                causa_provavel
            )

        if detalhes is not None:
            campos.append(
                "detalhes = ?"
            )
            valores.append(
                detalhes
            )

        valores.append(
            incidente_id
        )

        cursor = conexao.execute(
            f"""
            UPDATE incidentes
            SET {", ".join(campos)}
            WHERE id = ?
              AND encerrado = 0
            """,
            valores
        )

        return cursor.rowcount > 0


def listar_incidentes(
    limite=500,
    somente_abertos=False
):
    inicializar_banco()

    limite = max(
        1,
        min(
            int(limite),
            5000
        )
    )

    consulta = """
        SELECT
            id,
            tipo,
            origem,
            endereco,
            status_inicial,
            causa_provavel,
            inicio,
            fim,
            duracao_segundos,
            max_servicos_afetados,
            max_perda,
            max_latencia,
            max_oscilacao,
            detalhes,
            encerrado
        FROM incidentes
    """

    parametros = []

    if somente_abertos:
        consulta += """
            WHERE encerrado = 0
        """

    consulta += """
        ORDER BY inicio DESC
        LIMIT ?
    """

    parametros.append(
        limite
    )

    with _conectar() as conexao:
        registros = conexao.execute(
            consulta,
            parametros
        ).fetchall()

    return [
        dict(
            registro
        )
        for registro in registros
    ]


def obter_incidente_aberto(
    tipo,
    origem
):
    inicializar_banco()

    with _conectar() as conexao:
        registro = conexao.execute(
            """
            SELECT *
            FROM incidentes
            WHERE tipo = ?
              AND origem = ?
              AND encerrado = 0
            ORDER BY inicio DESC
            LIMIT 1
            """,
            (
                tipo,
                origem
            )
        ).fetchone()

    if registro is None:
        return None

    return dict(
        registro
    )


def limpar_incidentes_antigos(
    dias_retencao=90
):
    inicializar_banco()

    try:
        dias_retencao = int(
            dias_retencao
        )
    except (
        TypeError,
        ValueError
    ):
        dias_retencao = 90

    dias_retencao = max(
        1,
        dias_retencao
    )

    limite = (
        datetime.now()
        - timedelta(
            days=dias_retencao
        )
    ).isoformat(
        timespec="seconds"
    )

    with _conectar() as conexao:
        cursor = conexao.execute(
            """
            DELETE FROM incidentes
            WHERE encerrado = 1
              AND fim IS NOT NULL
              AND fim < ?
            """,
            (
                limite,
            )
        )

        return cursor.rowcount


def limpar_incidentes_encerrados():
    """
    Remove somente incidentes já encerrados.

    Incidentes em andamento nunca são apagados por esta função.
    """
    inicializar_banco()

    with _conectar() as conexao:
        cursor = conexao.execute(
            """
            DELETE FROM incidentes
            WHERE encerrado = 1
            """
        )

        return cursor.rowcount


def obter_resumo_hoje():
    inicializar_banco()

    inicio_dia = (
        datetime.now()
        .replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
        .isoformat(
            timespec="seconds"
        )
    )

    with _conectar() as conexao:
        total = conexao.execute(
            """
            SELECT COUNT(*) AS total
            FROM incidentes
            WHERE inicio >= ?
            """,
            (
                inicio_dia,
            )
        ).fetchone()["total"]

        criticos = conexao.execute(
            """
            SELECT COUNT(*) AS total
            FROM incidentes
            WHERE inicio >= ?
              AND (
                    status_inicial IN (
                        'SEM RESPOSTA',
                        'FALHA HTTP',
                        'ERRO'
                    )
                    OR tipo = 'REDE_LOCAL'
              )
            """,
            (
                inicio_dia,
            )
        ).fetchone()["total"]

    return {
        "total": int(total),
        "criticos": int(criticos)
    }


# Cria o arquivo/tabelas assim que o módulo for carregado.
inicializar_banco()
