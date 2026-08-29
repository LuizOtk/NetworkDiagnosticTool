import subprocess
import re


# Impede que o Windows abra uma janela de CMD
CREATE_NO_WINDOW = getattr(
    subprocess,
    "CREATE_NO_WINDOW",
    0
)


def executar_ping(
    ip,
    quantidade=4,
    timeout_ms=1000,
    limite_variacao_ms=50
):
    resultado = subprocess.run(
        [
            "ping",
            "-n",
            str(quantidade),
            "-w",
            str(timeout_ms),
            ip
        ],
        capture_output=True,
        text=True,
        encoding="cp850",

        # Executa o ping sem abrir CMD
        creationflags=CREATE_NO_WINDOW
    )

    estatisticas = re.search(
        r"Enviados = (\d+), Recebidos = (\d+), Perdidos = (\d+) \((\d+)%",
        resultado.stdout
    )

    latencia = re.search(
        r"Mínimo = (\d+)ms, Máximo = (\d+)ms, Média = (\d+)ms",
        resultado.stdout
    )

    padrao_resposta = re.compile(
        r"Resposta de\s+"
        r"(\d{1,3}(?:\.\d{1,3}){3}):"
        r".*?tempo([=<])(\d+)ms"
        r".*?TTL=(\d+)",
        re.IGNORECASE
    )

    respostas = []

    for numero, resposta in enumerate(
        padrao_resposta.finditer(
            resultado.stdout
        ),
        start=1
    ):
        ip_resposta = resposta.group(1)
        comparador = resposta.group(2)
        tempo = int(resposta.group(3))
        ttl = int(resposta.group(4))

        respostas.append({
            "numero": numero,
            "ip": ip_resposta,
            "tempo": tempo,
            "menor_que": comparador == "<",
            "ttl": ttl
        })

    if estatisticas:
        enviados = int(
            estatisticas.group(1)
        )

        recebidos = int(
            estatisticas.group(2)
        )

        perdidos = int(
            estatisticas.group(3)
        )

        perda = int(
            estatisticas.group(4)
        )

    else:
        enviados = quantidade
        recebidos = len(respostas)

        perdidos = (
            enviados
            - recebidos
        )

        if enviados > 0:
            perda = round(
                (
                    perdidos
                    / enviados
                )
                * 100
            )

        else:
            perda = 100

    if latencia:
        minimo = int(
            latencia.group(1)
        )

        maximo = int(
            latencia.group(2)
        )

        media = int(
            latencia.group(3)
        )

    else:
        minimo = None
        maximo = None
        media = None

    tempos = [
        resposta["tempo"]
        for resposta in respostas
    ]

    if len(tempos) >= 2:
        variacao = (
            max(tempos)
            - min(tempos)
        )

    else:
        variacao = 0

    motivos_instabilidade = []

    if perda > 0:
        motivos_instabilidade.append(
            "Perda de pacotes detectada: "
            f"{perda}%."
        )

    if variacao >= limite_variacao_ms:
        motivos_instabilidade.append(
            "Variação elevada de latência: "
            f"{variacao} ms."
        )

    instavel = bool(
        motivos_instabilidade
    )

    alerta = " ".join(
        motivos_instabilidade
    )

    return {
        "enviados": enviados,
        "recebidos": recebidos,
        "perdidos": perdidos,
        "perda": perda,
        "minimo": minimo,
        "maximo": maximo,
        "media": media,
        "variacao": variacao,
        "limite_variacao_ms":
            limite_variacao_ms,
        "instavel": instavel,
        "alerta": alerta,
        "respostas": respostas
    }
