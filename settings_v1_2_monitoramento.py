import json
import sys

from copy import deepcopy
from pathlib import Path

from config.service_presets import PRESET_SERVICOS


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


ARQUIVO_CONFIG = (
    obter_diretorio_aplicacao()
    / "config.json"
)


def obter_servicos_padrao():
    servicos = []

    for servico in PRESET_SERVICOS:
        servicos.append({
            "nome":
                servico["nome"],

            "endereco":
                servico["endereco"],

            "tipo":
                servico["tipo"]
        })

    return servicos


CONFIG_PADRAO = {
    "quantidade_ping": 4,
    "timeout_portas": 1.0,
    "max_saltos": 30,

    "limite_variacao_ms": 50,
    "limite_variacao_http_ms": 500,

    "limite_latencia_ping_ms": 100,
    "limite_latencia_http_ms": 1000,

    "intervalo_ping_continuo": 1.0,
    "intervalo_down_detector": 5.0,
    "falhas_down_detector_offline": 3,
    "tracert_continuo_amostra_minima": 30,

    "navegador_preferido": "padrao",
    "navegador_personalizado": "",
    "abrir_interface_web_automaticamente": True,

    "alerta_sonoro_geral_ativado": True,
    "alerta_sonoro_servico_indisponivel_ativado": True,
    "alerta_sonoro_modo": "padrao",
    "alerta_sonoro_arquivo": "",

    "servicos_padrao_inicializados": False,
    "servicos_down_detector": [],

    "portas": {
        "80": "HTTP",
        "443": "HTTPS",
        "8000": "HTTP",
        "8080": "HTTP Alternativo",
        "8291": "Winbox"
    }
}


def carregar_configuracoes():
    configuracoes = deepcopy(
        CONFIG_PADRAO
    )

    if ARQUIVO_CONFIG.exists():
        try:
            with open(
                ARQUIVO_CONFIG,
                "r",
                encoding="utf-8"
            ) as arquivo:
                dados = json.load(
                    arquivo
                )

            if isinstance(
                dados,
                dict
            ):
                campos = [
                    "quantidade_ping",
                    "timeout_portas",
                    "max_saltos",

                    "limite_variacao_ms",
                    "limite_variacao_http_ms",

                    "limite_latencia_ping_ms",
                    "limite_latencia_http_ms",

                    "intervalo_ping_continuo",
                    "intervalo_down_detector",
                    "falhas_down_detector_offline",
                    "tracert_continuo_amostra_minima",

                    "navegador_preferido",
                    "navegador_personalizado",
                    "abrir_interface_web_automaticamente",

                    "alerta_sonoro_geral_ativado",
                    "alerta_sonoro_servico_indisponivel_ativado",
                    "alerta_sonoro_modo",
                    "alerta_sonoro_arquivo",

                    "servicos_padrao_inicializados"
                ]

                for campo in campos:
                    if campo in dados:
                        configuracoes[
                            campo
                        ] = dados[
                            campo
                        ]

                portas = dados.get(
                    "portas"
                )

                if (
                    isinstance(
                        portas,
                        dict
                    )
                    and portas
                ):
                    configuracoes[
                        "portas"
                    ] = portas

                servicos = dados.get(
                    "servicos_down_detector"
                )

                if isinstance(
                    servicos,
                    list
                ):
                    configuracoes[
                        "servicos_down_detector"
                    ] = servicos

        except (
            json.JSONDecodeError,
            OSError
        ):
            pass

    navegador = configuracoes.get(
        "navegador_preferido"
    )

    navegadores_validos = {
        "padrao",
        "brave",
        "chrome",
        "edge",
        "personalizado"
    }

    if navegador not in navegadores_validos:
        configuracoes[
            "navegador_preferido"
        ] = "padrao"

    modo_alerta = configuracoes.get(
        "alerta_sonoro_modo"
    )

    modos_alerta_validos = {
        "padrao",
        "personalizado"
    }

    if modo_alerta not in modos_alerta_validos:
        configuracoes[
            "alerta_sonoro_modo"
        ] = "padrao"

    for campo_alerta in (
        "alerta_sonoro_geral_ativado",
        "alerta_sonoro_servico_indisponivel_ativado"
    ):
        if not isinstance(
            configuracoes.get(
                campo_alerta
            ),
            bool
        ):
            configuracoes[
                campo_alerta
            ] = True

    if not isinstance(
        configuracoes.get(
            "alerta_sonoro_arquivo"
        ),
        str
    ):
        configuracoes[
            "alerta_sonoro_arquivo"
        ] = ""

    if not configuracoes[
        "servicos_padrao_inicializados"
    ]:
        configuracoes[
            "servicos_down_detector"
        ] = obter_servicos_padrao()

        configuracoes[
            "servicos_padrao_inicializados"
        ] = True

        salvar_configuracoes(
            configuracoes
        )

    return configuracoes


def salvar_configuracoes(
    configuracoes
):
    with open(
        ARQUIVO_CONFIG,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            configuracoes,
            arquivo,
            indent=4,
            ensure_ascii=False
        )
