import csv
import json
import sys

from datetime import datetime
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


DIRETORIO_EXPORTACOES = (
    obter_diretorio_aplicacao()
    / "exports"
)


def preparar_diretorio():
    DIRETORIO_EXPORTACOES.mkdir(
        parents=True,
        exist_ok=True
    )


def criar_data_arquivo():
    return datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )


def formatar_duracao(
    segundos
):
    segundos = int(
        segundos or 0
    )

    horas = segundos // 3600

    minutos = (
        segundos % 3600
    ) // 60

    segundos_restantes = (
        segundos % 60
    )

    if horas > 0:
        return (
            f"{horas:02d}:"
            f"{minutos:02d}:"
            f"{segundos_restantes:02d}"
        )

    return (
        f"{minutos:02d}:"
        f"{segundos_restantes:02d}"
    )


def formatar_ms(
    valor
):
    if valor is None:
        return "-"

    return f"{valor} ms"


# ==================================================
# DIAGNÓSTICO NORMAL
# ==================================================


def exportar_relatorio(
    ip,
    dados_ping,
    saltos,
    portas,
    urls_web
):
    preparar_diretorio()

    nome = (
        f"diagnostico_{ip}_"
        f"{criar_data_arquivo()}.txt"
    )

    caminho = (
        DIRETORIO_EXPORTACOES
        / nome
    )

    linhas = []

    linhas.append(
        "NETWORK DIAGNOSTIC TOOL"
    )

    linhas.append(
        "Relatório de diagnóstico"
    )

    linhas.append(
        "=" * 60
    )

    linhas.append(
        f"IP analisado: {ip}"
    )

    linhas.append(
        "Data: "
        + datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )
    )

    linhas.append("")

    # -------------------------------
    # PING
    # -------------------------------

    linhas.append(
        "PING"
    )

    linhas.append(
        "-" * 60
    )

    linhas.append(
        f"Enviados: "
        f"{dados_ping.get('enviados', '-')}"
    )

    linhas.append(
        f"Recebidos: "
        f"{dados_ping.get('recebidos', '-')}"
    )

    linhas.append(
        f"Perdidos: "
        f"{dados_ping.get('perdidos', '-')}"
    )

    linhas.append(
        f"Perda: "
        f"{dados_ping.get('perda', '-')}%"
    )

    linhas.append(
        "Mínimo: "
        + formatar_ms(
            dados_ping.get(
                "minimo"
            )
        )
    )

    linhas.append(
        "Máximo: "
        + formatar_ms(
            dados_ping.get(
                "maximo"
            )
        )
    )

    linhas.append(
        "Média: "
        + formatar_ms(
            dados_ping.get(
                "media"
            )
        )
    )

    linhas.append(
        "Variação: "
        + formatar_ms(
            dados_ping.get(
                "variacao"
            )
        )
    )

    alerta = dados_ping.get(
        "alerta",
        ""
    )

    if alerta:
        linhas.append(
            f"Alerta: {alerta}"
        )

    linhas.append("")

    respostas = dados_ping.get(
        "respostas",
        []
    )

    if respostas:
        linhas.append(
            "Respostas individuais:"
        )

        for resposta in respostas:
            comparador = (
                "<"
                if resposta.get(
                    "menor_que"
                )
                else ""
            )

            linhas.append(
                f"#{resposta.get('numero')} | "
                f"{resposta.get('ip')} | "
                f"{comparador}"
                f"{resposta.get('tempo')} ms | "
                f"TTL {resposta.get('ttl')}"
            )

    linhas.append("")

    # -------------------------------
    # TRACERT
    # -------------------------------

    linhas.append(
        "TRACERT"
    )

    linhas.append(
        "-" * 60
    )

    for salto in saltos:
        linhas.append(
            f"Hop {salto.get('salto')} | "
            f"IP: {salto.get('ip') or '-'} | "
            f"T1: {formatar_ms(salto.get('tempo1'))} | "
            f"T2: {formatar_ms(salto.get('tempo2'))} | "
            f"T3: {formatar_ms(salto.get('tempo3'))} | "
            f"Média: {formatar_ms(salto.get('media'))} | "
            f"Status: {salto.get('status', '-')}"
        )

    linhas.append("")

    # -------------------------------
    # PORTAS
    # -------------------------------

    linhas.append(
        "PORTAS TCP"
    )

    linhas.append(
        "-" * 60
    )

    for porta in portas:
        linhas.append(
            f"Porta {porta.get('porta')} | "
            f"{porta.get('servico')} | "
            f"{porta.get('status')}"
        )

    if urls_web:
        linhas.append("")
        linhas.append(
            "INTERFACES WEB"
        )

        linhas.append(
            "-" * 60
        )

        for url in urls_web:
            linhas.append(
                url
            )

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:
        arquivo.write(
            "\n".join(
                linhas
            )
        )

    return caminho


# ==================================================
# TRACERT CONTÍNUO - TXT
# ==================================================


def exportar_tracert_continuo_txt(
    sessao
):
    preparar_diretorio()

    destino = sessao.get(
        "destino",
        "destino"
    )

    nome = (
        f"tracert_continuo_{destino}_"
        f"{criar_data_arquivo()}.txt"
    )

    caminho = (
        DIRETORIO_EXPORTACOES
        / nome
    )

    linhas = []

    linhas.append(
        "NETWORK DIAGNOSTIC TOOL"
    )

    linhas.append(
        "Relatório de Tracert contínuo"
    )

    linhas.append(
        "=" * 80
    )

    linhas.append(
        f"Versão: "
        f"{sessao.get('versao', '1.1')}"
    )

    linhas.append(
        f"Destino: {destino}"
    )

    linhas.append(
        f"Início: "
        f"{sessao.get('inicio', '-')}"
    )

    linhas.append(
        f"Fim: "
        f"{sessao.get('fim', '-')}"
    )

    linhas.append(
        "Duração: "
        + formatar_duracao(
            sessao.get(
                "duracao_segundos"
            )
        )
    )

    linhas.append(
        f"Ciclos: "
        f"{sessao.get('ciclos', 0)}"
    )

    linhas.append(
        f"Amostra mínima: "
        f"{sessao.get('amostra_minima', '-')}"
    )

    linhas.append(
        "Análise automática: "
        + (
            "ATIVA"
            if sessao.get(
                "amostra_atingida"
            )
            else "AMOSTRA INSUFICIENTE"
        )
    )

    linhas.append("")
    linhas.append(
        "RESULTADOS"
    )
    linhas.append(
        "=" * 80
    )

    cabecalho = (
        f"{'Hop':<5}"
        f"{'IP':<18}"
        f"{'Env':>7}"
        f"{'Rec':>7}"
        f"{'Perda':>9}"
        f"{'Melhor':>10}"
        f"{'Média':>10}"
        f"{'Pior':>10}"
        f"{'Último':>10}  "
        f"Status"
    )

    linhas.append(
        cabecalho
    )

    linhas.append(
        "-" * 105
    )

    for salto in sessao.get(
        "resultados",
        []
    ):
        linhas.append(
            f"{salto.get('salto', '-'):<5}"
            f"{str(salto.get('ip', '-')):<18}"
            f"{salto.get('enviados', 0):>7}"
            f"{salto.get('recebidos', 0):>7}"
            f"{str(salto.get('perda', 0)) + '%':>9}"
            f"{formatar_ms(salto.get('melhor')):>10}"
            f"{formatar_ms(salto.get('media')):>10}"
            f"{formatar_ms(salto.get('pior')):>10}"
            f"{formatar_ms(salto.get('ultimo')):>10}  "
            f"{salto.get('status', '-')}"
        )

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:
        arquivo.write(
            "\n".join(
                linhas
            )
        )

    return caminho


# ==================================================
# TRACERT CONTÍNUO - CSV
# ==================================================


def exportar_tracert_continuo_csv(
    sessao
):
    preparar_diretorio()

    destino = sessao.get(
        "destino",
        "destino"
    )

    nome = (
        f"tracert_continuo_{destino}_"
        f"{criar_data_arquivo()}.csv"
    )

    caminho = (
        DIRETORIO_EXPORTACOES
        / nome
    )

    with open(
        caminho,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:
        escritor = csv.writer(
            arquivo,

            # O ponto e vírgula costuma abrir
            # corretamente em Excel pt-BR.
            delimiter=";"
        )

        escritor.writerow([
            "Destino",
            destino
        ])

        escritor.writerow([
            "Início",
            sessao.get(
                "inicio",
                "-"
            )
        ])

        escritor.writerow([
            "Fim",
            sessao.get(
                "fim",
                "-"
            )
        ])

        escritor.writerow([
            "Duração",
            formatar_duracao(
                sessao.get(
                    "duracao_segundos"
                )
            )
        ])

        escritor.writerow([
            "Ciclos",
            sessao.get(
                "ciclos",
                0
            )
        ])

        escritor.writerow([
            "Amostra mínima",
            sessao.get(
                "amostra_minima",
                "-"
            )
        ])

        escritor.writerow([])

        escritor.writerow([
            "Salto",
            "IP",
            "Enviados",
            "Recebidos",
            "Perda %",
            "Melhor ms",
            "Média ms",
            "Pior ms",
            "Último ms",
            "Status"
        ])

        for salto in sessao.get(
            "resultados",
            []
        ):
            escritor.writerow([
                salto.get(
                    "salto"
                ),
                salto.get(
                    "ip"
                ),
                salto.get(
                    "enviados"
                ),
                salto.get(
                    "recebidos"
                ),
                salto.get(
                    "perda"
                ),
                salto.get(
                    "melhor"
                ),
                salto.get(
                    "media"
                ),
                salto.get(
                    "pior"
                ),
                salto.get(
                    "ultimo"
                ),
                salto.get(
                    "status"
                )
            ])

    return caminho


# ==================================================
# TRACERT CONTÍNUO - JSON
# ==================================================


def exportar_tracert_continuo_json(
    sessao
):
    preparar_diretorio()

    destino = sessao.get(
        "destino",
        "destino"
    )

    nome = (
        f"tracert_continuo_{destino}_"
        f"{criar_data_arquivo()}.json"
    )

    caminho = (
        DIRETORIO_EXPORTACOES
        / nome
    )

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            sessao,
            arquivo,
            indent=4,
            ensure_ascii=False
        )

    return caminho
