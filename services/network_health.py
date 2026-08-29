import math


STATUS_PROBLEMA = {
    "SEM RESPOSTA",
    "FALHA HTTP",
    "ERRO",
    "POSSÍVEL INSTABILIDADE",
    "LATÊNCIA ALTA"
}


STATUS_CRITICO = {
    "SEM RESPOSTA",
    "FALHA HTTP",
    "ERRO"
}


def analisar_saude_rede(
    resultados,
    minimo_problemas=5,
    percentual_minimo=40
):
    verificados = [
        item
        for item in resultados
        if item.get("status")
        not in {
            None,
            "",
            "AGUARDANDO"
        }
    ]

    problemas = [
        item
        for item in verificados
        if item.get("status")
        in STATUS_PROBLEMA
    ]

    criticos = [
        item
        for item in problemas
        if item.get("status")
        in STATUS_CRITICO
    ]

    total_verificados = len(
        verificados
    )

    total_problemas = len(
        problemas
    )

    if total_verificados == 0:
        return {
            "rede_local_instavel": False,
            "total_verificados": 0,
            "total_problemas": 0,
            "percentual_problemas": 0.0,
            "problemas": [],
            "criticos": []
        }

    percentual = round(
        (
            total_problemas
            / total_verificados
        )
        * 100,
        1
    )

    quantidade_por_percentual = math.ceil(
        total_verificados
        * (
            percentual_minimo
            / 100
        )
    )

    quantidade_necessaria = max(
        minimo_problemas,
        quantidade_por_percentual
    )

    rede_local_instavel = (
        total_problemas
        >= quantidade_necessaria
    )

    return {
        "rede_local_instavel":
            rede_local_instavel,

        "total_verificados":
            total_verificados,

        "total_problemas":
            total_problemas,

        "percentual_problemas":
            percentual,

        "problemas":
            problemas,

        "criticos":
            criticos
    }
