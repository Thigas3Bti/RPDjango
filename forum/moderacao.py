import re
import unicodedata


_TERMOS_BLOQUEADOS = {
    'arrombado',
    'arrombada',
    'babaca',
    'corno',
    'desgracado',
    'desgracada',
    'fdp',
    'fudido',
    'fudida',
    'merda',
    'otario',
    'otaria',
    'piranha',
    'retardado',
    'retardada',
    'vagabundo',
    'vagabunda',
    'viado',
}
_FRASES_BLOQUEADAS = (
    'filho da puta',
    'filha da puta',
    'vai tomar no cu',
    'vai se foder',
    'vou te matar',
    'vou matar voce',
)
_LEET_MAP = str.maketrans({'0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't'})


def _normalizar(texto):
    texto = unicodedata.normalize('NFKD', texto.casefold())
    texto = ''.join(caractere for caractere in texto if not unicodedata.combining(caractere))
    texto = texto.translate(_LEET_MAP)
    return re.sub(r'[^a-z]+', ' ', texto)


def contem_conteudo_ofensivo(*textos):
    texto_normalizado = _normalizar(' '.join(texto for texto in textos if texto))
    palavras = set(texto_normalizado.split())
    if palavras.intersection(_TERMOS_BLOQUEADOS):
        return True

    for frase in _FRASES_BLOQUEADAS:
        padrao = re.escape(_normalizar(frase).strip()).replace(r'\ ', r'\s+')
        if re.search(rf'\b{padrao}\b', texto_normalizado):
            return True
    return False
