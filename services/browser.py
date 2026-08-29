import os
import shutil
import ssl
import subprocess
import urllib.error
import urllib.request
import webbrowser

from pathlib import Path

from services.logger import logger


CREATE_NO_WINDOW = getattr(
    subprocess,
    "CREATE_NO_WINDOW",
    0
)


NAVEGADORES = {
    "padrao": "Padrão do Windows",
    "brave": "Brave",
    "chrome": "Google Chrome",
    "edge": "Microsoft Edge",
    "personalizado": "Outro navegador..."
}


EXECUTAVEIS = {
    "brave": [
        "brave.exe",
        "brave"
    ],

    "chrome": [
        "chrome.exe",
        "chrome"
    ],

    "edge": [
        "msedge.exe",
        "msedge"
    ]
}


CAMINHOS_RELATIVOS = {
    "brave": [
        (
            "BraveSoftware",
            "Brave-Browser",
            "Application",
            "brave.exe"
        )
    ],

    "chrome": [
        (
            "Google",
            "Chrome",
            "Application",
            "chrome.exe"
        )
    ],

    "edge": [
        (
            "Microsoft",
            "Edge",
            "Application",
            "msedge.exe"
        )
    ]
}


# Compatibilidade com as portas web já reconhecidas
# nas versões anteriores do NDT.
PORTAS_WEB_LEGADAS = {
    443: "HTTPS",
    8443: "HTTPS",
    80: "HTTP",
    8000: "HTTP",
    8080: "HTTP"
}


def obter_nome_navegador(
    navegador
):
    return NAVEGADORES.get(
        navegador,
        "Padrão do Windows"
    )


def localizar_navegador(
    navegador,
    caminho_personalizado=""
):
    if navegador == "padrao":
        return None

    if navegador == "personalizado":
        if not caminho_personalizado:
            return None

        caminho = Path(
            caminho_personalizado
        )

        if caminho.is_file():
            return str(
                caminho
            )

        return None

    executaveis = EXECUTAVEIS.get(
        navegador,
        []
    )

    for executavel in executaveis:
        caminho = shutil.which(
            executavel
        )

        if caminho:
            return caminho

    raizes = [
        os.environ.get(
            "PROGRAMFILES"
        ),

        os.environ.get(
            "PROGRAMFILES(X86)"
        ),

        os.environ.get(
            "LOCALAPPDATA"
        )
    ]

    caminhos_relativos = (
        CAMINHOS_RELATIVOS.get(
            navegador,
            []
        )
    )

    for raiz in raizes:
        if not raiz:
            continue

        for partes in caminhos_relativos:
            caminho = Path(
                raiz
            ).joinpath(
                *partes
            )

            if caminho.exists():
                return str(
                    caminho
                )

    return None


def abrir_url(
    url,
    navegador="padrao",
    caminho_personalizado=""
):
    if navegador == "padrao":
        logger.info(
            "Abrindo URL no navegador padrão | "
            "URL=%s",
            url
        )

        webbrowser.open(
            url
        )

        return True, "padrao"

    caminho = localizar_navegador(
        navegador,
        caminho_personalizado
    )

    if caminho:
        try:
            subprocess.Popen(
                [
                    caminho,
                    url
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )

            logger.info(
                "URL aberta | "
                "Navegador=%s | "
                "Executável=%s | "
                "URL=%s",
                obter_nome_navegador(
                    navegador
                ),
                caminho,
                url
            )

            return True, navegador

        except OSError:
            logger.exception(
                "Erro ao iniciar navegador | "
                "Navegador=%s | "
                "Caminho=%s",
                navegador,
                caminho
            )

    logger.warning(
        "Navegador configurado não encontrado | "
        "Navegador=%s | "
        "Caminho=%s | "
        "Fallback para navegador padrão.",
        navegador,
        caminho_personalizado
    )

    webbrowser.open(
        url
    )

    return False, "padrao"


def normalizar_protocolo_web(
    protocolo
):
    if protocolo is None:
        return None

    protocolo = str(
        protocolo
    ).strip().upper()

    if protocolo == "HTTP":
        return "HTTP"

    if protocolo == "HTTPS":
        return "HTTPS"

    if protocolo in {
        "AUTOMATICO",
        "AUTOMÁTICO"
    }:
        return "AUTOMATICO"

    return None


def obter_modo_interface_web(
    porta,
    configuracao_portas=None
):
    """
    Retorna um dos modos:
        NENHUMA
        HTTP
        HTTPS
        AUTOMATICO

    Se não existir configuração explícita, aplica compatibilidade
    com as portas web reconhecidas pelas versões anteriores.
    """
    try:
        porta = int(
            porta
        )

    except (
        TypeError,
        ValueError
    ):
        return "NENHUMA"

    if isinstance(
        configuracao_portas,
        dict
    ):
        chave_texto = str(
            porta
        )

        if chave_texto in configuracao_portas:
            configuracao = configuracao_portas[
                chave_texto
            ]

            # Formato atual:
            # "38080": "AUTOMATICO"
            if isinstance(
                configuracao,
                str
            ):
                valor = configuracao.strip().upper()

                if valor in {
                    "HTTP",
                    "HTTPS",
                    "AUTOMATICO",
                    "NENHUMA"
                }:
                    return valor

            # Compatibilidade com um possível formato estruturado.
            if isinstance(
                configuracao,
                dict
            ):
                valor = str(
                    configuracao.get(
                        "interface_web",
                        "NENHUMA"
                    )
                ).strip().upper()

                if valor in {
                    "HTTP",
                    "HTTPS",
                    "AUTOMATICO",
                    "NENHUMA"
                }:
                    return valor

            return "NENHUMA"

        if porta in configuracao_portas:
            configuracao = configuracao_portas[
                porta
            ]

            if isinstance(
                configuracao,
                str
            ):
                valor = configuracao.strip().upper()

                if valor in {
                    "HTTP",
                    "HTTPS",
                    "AUTOMATICO",
                    "NENHUMA"
                }:
                    return valor

    # Compatibilidade com as versões anteriores.
    legado = PORTAS_WEB_LEGADAS.get(
        porta
    )

    if legado is not None:
        return legado

    return "NENHUMA"


def obter_protocolo_web_configurado(
    porta,
    configuracao_portas=None
):
    modo = obter_modo_interface_web(
        porta,
        configuracao_portas
    )

    if modo == "NENHUMA":
        return None

    return modo


def testar_url_web(
    url,
    timeout=1.5
):
    """
    Considera a URL como interface web quando existe uma resposta HTTP.

    Códigos 401, 403, 404 etc. também confirmam que há um servidor HTTP
    respondendo. Para HTTPS local, ignoramos validação de certificado
    porque muitos roteadores/ONUs usam certificado autoassinado.
    """
    requisicao = urllib.request.Request(
        url,
        method="HEAD",
        headers={
            "User-Agent": "NDT/1.2"
        }
    )

    contexto_ssl = None

    if url.lower().startswith(
        "https://"
    ):
        contexto_ssl = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(
            requisicao,
            timeout=timeout,
            context=contexto_ssl
        ) as resposta:
            codigo = getattr(
                resposta,
                "status",
                200
            )

            return {
                "ok": True,
                "codigo": int(
                    codigo
                ),
                "url": url
            }

    except urllib.error.HTTPError as erro:
        # Uma resposta HTTP de erro ainda confirma que o protocolo existe.
        return {
            "ok": True,
            "codigo": int(
                erro.code
            ),
            "url": url
        }

    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
        ValueError
    ):
        return {
            "ok": False,
            "codigo": None,
            "url": url
        }


def detectar_protocolo_web(
    ip,
    porta,
    timeout=1.5
):
    """
    Testa HTTPS primeiro e faz fallback para HTTP.

    Retorna:
        "HTTPS"
        "HTTP"
        None
    """
    url_https = obter_url_porta(
        ip,
        porta,
        "HTTPS"
    )

    if url_https is not None:
        resultado = testar_url_web(
            url_https,
            timeout
        )

        if resultado[
            "ok"
        ]:
            logger.info(
                "Interface web detectada automaticamente | "
                "Porta=%s | Protocolo=HTTPS | URL=%s | Código=%s",
                porta,
                url_https,
                resultado[
                    "codigo"
                ]
            )

            return "HTTPS"

    url_http = obter_url_porta(
        ip,
        porta,
        "HTTP"
    )

    if url_http is not None:
        resultado = testar_url_web(
            url_http,
            timeout
        )

        if resultado[
            "ok"
        ]:
            logger.info(
                "Interface web detectada automaticamente | "
                "Porta=%s | Protocolo=HTTP | URL=%s | Código=%s",
                porta,
                url_http,
                resultado[
                    "codigo"
                ]
            )

            return "HTTP"

    logger.info(
        "Nenhuma interface web detectada automaticamente | "
        "Porta=%s",
        porta
    )

    return None


def obter_url_porta(
    ip,
    porta,
    protocolo=None
):
    try:
        porta = int(
            porta
        )

    except (
        TypeError,
        ValueError
    ):
        return None

    protocolo = normalizar_protocolo_web(
        protocolo
    )

    if protocolo is None:
        protocolo = PORTAS_WEB_LEGADAS.get(
            porta
        )

    if protocolo is None:
        return None

    if protocolo == "AUTOMATICO":
        return None

    esquema = protocolo.lower()

    # Evita adicionar a porta quando ela já é a
    # porta padrão do respectivo protocolo.
    if (
        protocolo == "HTTP"
        and porta == 80
    ):
        return f"http://{ip}"

    if (
        protocolo == "HTTPS"
        and porta == 443
    ):
        return f"https://{ip}"

    return (
        f"{esquema}://"
        f"{ip}:"
        f"{porta}"
    )


def obter_protocolo_resultado(
    resultado,
    configuracao_portas=None
):
    protocolo_detectado = normalizar_protocolo_web(
        resultado.get(
            "protocolo_web"
        )
    )

    if (
        protocolo_detectado is not None
        and protocolo_detectado != "AUTOMATICO"
    ):
        return protocolo_detectado

    protocolo_interface = normalizar_protocolo_web(
        resultado.get(
            "interface_web"
        )
    )

    if (
        protocolo_interface is not None
        and protocolo_interface != "AUTOMATICO"
    ):
        return protocolo_interface

    return obter_protocolo_web_configurado(
        resultado.get(
            "porta"
        ),
        configuracao_portas
    )


def obter_prioridade_url(
    porta,
    protocolo
):
    """
    HTTPS tem prioridade sobre HTTP.

    Dentro do mesmo protocolo, portas padrão
    têm preferência; depois ordenamos pelo número
    da porta para manter comportamento previsvisível.
    """
    protocolo = normalizar_protocolo_web(
        protocolo
    )

    if protocolo == "HTTPS":
        prioridade_protocolo = 0

        prioridade_padrao = (
            0
            if porta == 443
            else 1
        )

    else:
        prioridade_protocolo = 1

        prioridade_padrao = (
            0
            if porta == 80
            else 1
        )

    return (
        prioridade_protocolo,
        prioridade_padrao,
        porta
    )


def enriquecer_resultados_portas_web(
    ip,
    portas,
    configuracao_portas=None,
    timeout=1.5
):
    """
    Enriquece cada resultado de porta com:

        interface_web_modo
        protocolo_web
        url_web

    A detecção automática acontece somente quando:
    - a porta está ABERTA;
    - o modo está configurado como AUTOMATICO.

    Isso permite executar a detecção dentro da thread de diagnóstico,
    sem bloquear a interface gráfica.
    """
    for resultado in portas:
        porta = resultado.get(
            "porta"
        )

        modo = obter_modo_interface_web(
            porta,
            configuracao_portas
        )

        resultado[
            "interface_web_modo"
        ] = modo

        resultado[
            "protocolo_web"
        ] = None

        resultado[
            "url_web"
        ] = None

        if resultado.get(
            "status"
        ) != "ABERTA":
            continue

        if modo == "NENHUMA":
            continue

        if modo == "AUTOMATICO":
            protocolo = detectar_protocolo_web(
                ip,
                porta,
                timeout
            )

            if protocolo is None:
                continue

        else:
            protocolo = modo

        url = obter_url_porta(
            ip,
            porta,
            protocolo
        )

        resultado[
            "protocolo_web"
        ] = protocolo

        resultado[
            "url_web"
        ] = url

    return portas


def obter_urls_web(
    ip,
    portas,
    configuracao_portas=None
):
    encontrados = []

    for resultado in portas:
        if (
            resultado.get(
                "status"
            )
            != "ABERTA"
        ):
            continue

        porta = resultado.get(
            "porta"
        )

        try:
            porta = int(
                porta
            )

        except (
            TypeError,
            ValueError
        ):
            continue

        protocolo = obter_protocolo_resultado(
            resultado,
            configuracao_portas
        )

        if protocolo is None:
            continue

        if protocolo == "AUTOMATICO":
            protocolo = detectar_protocolo_web(
                ip,
                porta
            )

            if protocolo is None:
                continue

        url = obter_url_porta(
            ip,
            porta,
            protocolo
        )

        if url is None:
            continue

        encontrados.append(
            (
                obter_prioridade_url(
                    porta,
                    protocolo
                ),
                url
            )
        )

    encontrados.sort(
        key=lambda item: item[0]
    )

    return [
        item[1]
        for item in encontrados
    ]


def obter_url_preferencial(
    ip,
    portas,
    configuracao_portas=None
):
    urls = obter_urls_web(
        ip,
        portas,
        configuracao_portas
    )

    if not urls:
        return None

    return urls[0]
