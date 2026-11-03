import re
import unicodedata


_PALAVROES = {
    'bosta',
    'cacete',
    'caralho',
    'cu',
    'foda',
    'merda',
    'porra',
    'puta',
}


def contem_palavrao(texto):
    texto_normalizado = unicodedata.normalize('NFKD', texto.casefold())
    texto_sem_acentos = ''.join(
        caractere
        for caractere in texto_normalizado
        if not unicodedata.combining(caractere)
    )
    palavras = re.findall(r'[a-z0-9]+', texto_sem_acentos)
    return any(palavra in _PALAVROES for palavra in palavras)
