import json

from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from config.settings import (
    CONFIG_PADRAO,
    obter_diretorio_aplicacao
)


FORMATO_CONFIG = "NDT_CONFIG"
VERSAO_APP = "1.2"
VERSAO_CONFIG = 1


def _timestamp():
    return datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )


def _documento(
    configuracoes,
    tipo
):
    return {
        "formato": FORMATO_CONFIG,
        "versao_app": VERSAO_APP,
        "versao_config": VERSAO_CONFIG,
        "tipo": tipo,
        "gerado_em": datetime.now().isoformat(
            timespec="seconds"
        ),
        "configuracoes": deepcopy(
            configuracoes
        )
    }


def exportar_configuracoes(
    configuracoes,
    destino
):
    destino = Path(
        destino
    ).expanduser()

    destino.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        destino,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            _documento(
                configuracoes,
                "exportacao"
            ),
            arquivo,
            indent=4,
            ensure_ascii=False
        )

    return destino


def criar_backup_automatico(
    configuracoes
):
    diretorio = (
        obter_diretorio_aplicacao()
        / "backups"
        / "config"
    )

    diretorio.mkdir(
        parents=True,
        exist_ok=True
    )

    destino = (
        diretorio
        / f"NDT_Config_Backup_{_timestamp()}.json"
    )

    with open(
        destino,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(
            _documento(
                configuracoes,
                "backup_automatico"
            ),
            arquivo,
            indent=4,
            ensure_ascii=False
        )

    return destino


def _normalizar_portas(
    portas
):
    if not isinstance(
        portas,
        dict
    ):
        return None

    resultado = {}

    for porta, servico in portas.items():
        try:
            porta = int(
                porta
            )
        except (
            TypeError,
            ValueError
        ):
            continue

        if not 1 <= porta <= 65535:
            continue

        resultado[
            str(
                porta
            )
        ] = (
            str(
                servico
            ).strip()
            or "TCP"
        )

    return (
        resultado
        if resultado
        else None
    )


def _normalizar_interfaces_web_portas(
    interfaces
):
    if not isinstance(
        interfaces,
        dict
    ):
        return None

    resultado: dict[str, str] = {}

    for porta, protocolo in interfaces.items():
        try:
            numero = int(
                porta
            )

        except (
            TypeError,
            ValueError
        ):
            continue

        if not 1 <= numero <= 65535:
            continue

        protocolo = str(
            protocolo
        ).strip().upper()

        if protocolo not in {
            "HTTP",
            "HTTPS",
            "AUTOMATICO",
            "NENHUMA"
        }:
            protocolo = "NENHUMA"

        resultado[
            str(
                numero
            )
        ] = protocolo

    return resultado


def _normalizar_servicos(
    servicos
):
    if not isinstance(
        servicos,
        list
    ):
        return None

    resultado: list[dict[str, Any]] = []

    for servico in servicos:
        if not isinstance(
            servico,
            dict
        ):
            continue

        nome = str(
            servico.get(
                "nome",
                ""
            )
        ).strip()

        endereco = str(
            servico.get(
                "endereco",
                ""
            )
        ).strip()

        tipo = str(
            servico.get(
                "tipo",
                "PING"
            )
        ).upper().strip()

        if not nome or not endereco:
            continue

        if tipo not in {
            "PING",
            "HTTP"
        }:
            tipo = "PING"

        novo: dict[str, Any] = {
            "nome": nome,
            "endereco": endereco,
            "tipo": tipo
        }

        if "alerta_individual_ativado" in servico:
            novo[
                "alerta_individual_ativado"
            ] = bool(
                servico.get(
                    "alerta_individual_ativado"
                )
            )

        modo = servico.get(
            "alerta_individual_modo"
        )

        if modo in {
            "global",
            "padrao",
            "personalizado"
        }:
            novo[
                "alerta_individual_modo"
            ] = modo

        arquivo = servico.get(
            "alerta_individual_arquivo"
        )

        if isinstance(
            arquivo,
            str
        ):
            novo[
                "alerta_individual_arquivo"
            ] = arquivo

        resultado.append(
            novo
        )

    return resultado


def _normalizar_simples(
    chave,
    valor
):
    padrao = CONFIG_PADRAO[
        chave
    ]

    if isinstance(
        padrao,
        bool
    ):
        return (
            valor
            if isinstance(
                valor,
                bool
            )
            else padrao
        )

    if isinstance(
        padrao,
        int
    ) and not isinstance(
        padrao,
        bool
    ):
        try:
            return int(
                valor
            )
        except (
            TypeError,
            ValueError
        ):
            return padrao

    if isinstance(
        padrao,
        float
    ):
        try:
            return float(
                valor
            )
        except (
            TypeError,
            ValueError
        ):
            return padrao

    if isinstance(
        padrao,
        str
    ):
        return (
            valor
            if isinstance(
                valor,
                str
            )
            else padrao
        )

    return deepcopy(
        valor
    )


def normalizar_configuracoes_importadas(
    dados,
    atuais
):
    resultado = deepcopy(
        atuais
    )

    for chave in CONFIG_PADRAO:
        if chave not in dados:
            continue

        if chave == "portas":
            portas = _normalizar_portas(
                dados[
                    chave
                ]
            )

            if portas is not None:
                resultado[
                    chave
                ] = portas

            continue

        if chave == "interfaces_web_portas":
            interfaces = _normalizar_interfaces_web_portas(
                dados[
                    chave
                ]
            )

            if interfaces is not None:
                resultado[
                    chave
                ] = interfaces

            continue

        if chave == "servicos_down_detector":
            servicos = _normalizar_servicos(
                dados[
                    chave
                ]
            )

            if servicos is not None:
                resultado[
                    chave
                ] = servicos

            continue

        resultado[
            chave
        ] = _normalizar_simples(
            chave,
            dados[
                chave
            ]
        )

    limites = {
        "quantidade_ping": (1, 100),
        "timeout_portas": (0.1, 30.0),
        "max_saltos": (1, 255),
        "limite_variacao_ms": (1, 5000),
        "limite_variacao_http_ms": (50, 10000),
        "limite_latencia_ping_ms": (1, 10000),
        "limite_latencia_http_ms": (50, 30000),
        "intervalo_ping_continuo": (0.1, 60.0),
        "intervalo_down_detector": (1.0, 300.0),
        "falhas_down_detector_offline": (1, 20),
        "tracert_continuo_amostra_minima": (5, 1000),
        "alerta_cooldown_minutos": (0, 1440),
        "registro_incidentes_retencao_dias": (7, 3650)
    }

    for chave, (
        minimo,
        maximo
    ) in limites.items():
        valor = resultado.get(
            chave
        )

        if not isinstance(
            valor,
            (int, float)
        ) or isinstance(
            valor,
            bool
        ):
            continue

        valor = max(
            minimo,
            min(
                valor,
                maximo
            )
        )

        if isinstance(
            CONFIG_PADRAO[
                chave
            ],
            int
        ):
            valor = int(
                valor
            )

        resultado[
            chave
        ] = valor

    portas_existentes = {
        str(
            porta
        )
        for porta in resultado.get(
            "portas",
            {}
        )
    }

    interfaces = resultado.get(
        "interfaces_web_portas",
        {}
    )

    if not isinstance(
        interfaces,
        dict
    ):
        interfaces = {}

    resultado[
        "interfaces_web_portas"
    ] = {
        str(porta): (
            str(
                interfaces.get(
                    str(
                        porta
                    ),
                    "NENHUMA"
                )
            )
            .strip()
            .upper()
            if str(
                interfaces.get(
                    str(
                        porta
                    ),
                    "NENHUMA"
                )
            ).strip().upper()
            in {
                "HTTP",
                "HTTPS",
                "AUTOMATICO",
                "NENHUMA"
            }
            else "NENHUMA"
        )
        for porta in portas_existentes
    }

    if resultado.get(
        "navegador_preferido"
    ) not in {
        "padrao",
        "brave",
        "chrome",
        "edge",
        "personalizado"
    }:
        resultado[
            "navegador_preferido"
        ] = "padrao"

    if resultado.get(
        "alerta_sonoro_modo"
    ) not in {
        "padrao",
        "personalizado"
    }:
        resultado[
            "alerta_sonoro_modo"
        ] = "padrao"

    return resultado


def importar_configuracoes(
    origem,
    atuais
):
    origem = Path(
        origem
    ).expanduser()

    with open(
        origem,
        "r",
        encoding="utf-8"
    ) as arquivo:
        documento = json.load(
            arquivo
        )

    if not isinstance(
        documento,
        dict
    ):
        raise ValueError(
            "Documento de configuração inválido."
        )

    if documento.get(
        "formato"
    ) != FORMATO_CONFIG:
        raise ValueError(
            "O arquivo não é um backup de configurações do NDT."
        )

    versao_config = documento.get(
        "versao_config"
    )

    if not isinstance(
        versao_config,
        int
    ):
        raise ValueError(
            "Versão de configuração inválida."
        )

    if versao_config > VERSAO_CONFIG:
        raise ValueError(
            "Este backup foi criado por uma versão de configuração "
            "mais nova que a suportada pelo NDT atual."
        )

    dados = documento.get(
        "configuracoes"
    )

    if not isinstance(
        dados,
        dict
    ):
        raise ValueError(
            "O arquivo não possui configurações válidas."
        )

    novas = normalizar_configuracoes_importadas(
        dados,
        atuais
    )

    avisos = []

    if (
        novas.get(
            "navegador_preferido"
        )
        == "personalizado"
    ):
        caminho = novas.get(
            "navegador_personalizado",
            ""
        )

        if (
            not caminho
            or not Path(
                caminho
            ).is_file()
        ):
            avisos.append(
                "Navegador personalizado não encontrado neste computador."
            )

    if (
        novas.get(
            "alerta_sonoro_modo"
        )
        == "personalizado"
    ):
        caminho = novas.get(
            "alerta_sonoro_arquivo",
            ""
        )

        if (
            not caminho
            or not Path(
                caminho
            ).is_file()
        ):
            avisos.append(
                "Arquivo WAV global não encontrado neste computador."
            )

    sons_ausentes = 0

    for servico in novas.get(
        "servicos_down_detector",
        []
    ):
        if (
            servico.get(
                "alerta_individual_ativado"
            )
            and servico.get(
                "alerta_individual_modo"
            )
            == "personalizado"
        ):
            caminho = servico.get(
                "alerta_individual_arquivo",
                ""
            )

            if (
                not caminho
                or not Path(
                    caminho
                ).is_file()
            ):
                sons_ausentes += 1

    if sons_ausentes:
        avisos.append(
            f"{sons_ausentes} som(ns) personalizado(s) "
            "de serviço não foram encontrados neste computador."
        )

    return (
        novas,
        {
            "versao_app_origem":
                documento.get(
                    "versao_app",
                    "desconhecida"
                ),
            "versao_config":
                versao_config,
            "gerado_em":
                documento.get(
                    "gerado_em",
                    ""
                ),
            "avisos":
                avisos
        }
    )
