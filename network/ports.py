import socket


def testar_porta(ip, porta, timeout=1.0):
    conexao = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    conexao.settimeout(timeout)

    try:
        resultado = conexao.connect_ex(
            (ip, porta)
        )

        if resultado == 0:
            return "ABERTA"

        elif resultado in [10060, 110]:
            return "TIMEOUT"

        else:
            return "FECHADA"

    except OSError:
        return "ERRO"

    finally:
        conexao.close()


def testar_portas(ip, portas_config, timeout=1.0):
    resultados = []

    for porta, servico in portas_config.items():
        numero_porta = int(porta)

        status = testar_porta(
            ip,
            numero_porta,
            timeout
        )

        resultados.append({
            "porta": numero_porta,
            "servico": servico,
            "status": status
        })

    prioridade = {
        "ABERTA": 0,
        "TIMEOUT": 1,
        "FECHADA": 2,
        "ERRO": 3
    }

    resultados.sort(
        key=lambda item: (
            prioridade.get(
                item["status"],
                99
            ),
            item["porta"]
        )
    )

    return resultados
