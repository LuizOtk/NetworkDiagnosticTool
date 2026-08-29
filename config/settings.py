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

    # Experiência de inicialização
    "exibir_tela_inicializacao": True,

    "alerta_sonoro_geral_ativado": True,
    "alerta_sonoro_servico_indisponivel_ativado": True,
    "alerta_sonoro_modo": "padrao",
    "alerta_sonoro_arquivo": "",

    # Proteção adicional contra flapping:
    # após um alerta individual tocar, uma nova queda do
    # mesmo serviço só poderá tocar novamente depois
    # deste período.
    "alerta_cooldown_minutos": 5,

    # Registro de Incidentes
    "registro_incidentes_ativado": True,
    "registro_incidentes_retencao_dias": 90,

    "servicos_padrao_inicializados": False,
    "servicos_down_detector": [],

    "portas": {
        "80": "HTTP",
        "443": "HTTPS",
        "8000": "HTTP",
        "8080": "HTTP Alternativo",
        "8291": "Winbox"
    },

    # Protocolo usado para abrir interfaces web em portas TCP.
    # Mantemos separado de "portas" para preservar compatibilidade
    # com o scanner atual.
    "interfaces_web_portas": {
        "80": "HTTP",
        "443": "HTTPS",
        "8000": "HTTP",
        "8080": "HTTP",
        "8291": "NENHUMA"
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
                    "exibir_tela_inicializacao",

                    "alerta_sonoro_geral_ativado",
                    "alerta_sonoro_servico_indisponivel_ativado",
                    "alerta_sonoro_modo",
                    "alerta_sonoro_arquivo",
                    "alerta_cooldown_minutos",

                    "registro_incidentes_ativado",
                    "registro_incidentes_retencao_dias",

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

                interfaces_web = dados.get(
                    "interfaces_web_portas"
                )

                if isinstance(
                    interfaces_web,
                    dict
                ):
                    configuracoes[
                        "interfaces_web_portas"
                    ] = interfaces_web

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

    if not isinstance(
        configuracoes.get(
            "exibir_tela_inicializacao"
        ),
        bool
    ):
        configuracoes[
            "exibir_tela_inicializacao"
        ] = True

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

    cooldown = configuracoes.get(
        "alerta_cooldown_minutos",
        5
    )

    if (
        not isinstance(
            cooldown,
            (int, float)
        )
        or isinstance(
            cooldown,
            bool
        )
    ):
        cooldown = 5

    cooldown = int(
        max(
            0,
            min(
                cooldown,
                1440
            )
        )
    )

    configuracoes[
        "alerta_cooldown_minutos"
    ] = cooldown

    registro_ativado = configuracoes.get(
        "registro_incidentes_ativado",
        True
    )

    if not isinstance(
        registro_ativado,
        bool
    ):
        registro_ativado = True

    configuracoes[
        "registro_incidentes_ativado"
    ] = registro_ativado

    retencao = configuracoes.get(
        "registro_incidentes_retencao_dias",
        90
    )

    try:
        retencao = int(
            retencao
        )

    except (
        TypeError,
        ValueError
    ):
        retencao = 90

    retencao = max(
        7,
        min(
            retencao,
            3650
        )
    )

    configuracoes[
        "registro_incidentes_retencao_dias"
    ] = retencao

    portas_atuais = configuracoes.get(
        "portas",
        {}
    )

    interfaces_web = configuracoes.get(
        "interfaces_web_portas",
        {}
    )

    if not isinstance(
        interfaces_web,
        dict
    ):
        interfaces_web = {}

    interfaces_normalizadas = {}

    for porta in portas_atuais:
        porta_texto = str(
            porta
        )

        protocolo = str(
            interfaces_web.get(
                porta_texto,
                ""
            )
        ).strip().upper()

        if protocolo not in {
            "HTTP",
            "HTTPS",
            "AUTOMATICO",
            "NENHUMA"
        }:
            # Migração amigável para instalações antigas.
            try:
                numero_porta = int(
                    porta_texto
                )
            except (
                TypeError,
                ValueError
            ):
                numero_porta = 0

            if numero_porta in {
                443,
                8443
            }:
                protocolo = "HTTPS"

            elif numero_porta in {
                80,
                8000,
                8080
            }:
                protocolo = "HTTP"

            else:
                protocolo = "NENHUMA"

        interfaces_normalizadas[
            porta_texto
        ] = protocolo

    configuracoes[
        "interfaces_web_portas"
    ] = interfaces_normalizadas

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
