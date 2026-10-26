import re
import unicodedata


_PROFANITY = {
    'babaca',
    'bosta',
    'bostao',
    'bostinha',
    'buceta',
    'boceta',
    'cacete',
    'caralho',
    'cu',
    'desgraca',
    'foda',
    'fodas',
    'fode',
    'foder',
    'fodia',
    'fodendo',
    'fodido',
    'fodida',
    'fudendo',
    'fudido',
    'fudida',
    'fude',
    'fuder',
    'merda',
    'merdas',
    'pqp',
    'porra',
    'putaria',
    'puta',
    'puto',
    'putas',
    'putos',
    'rabao',
    'rola',
    'retardado',
    'retardada',
}


def contem_palavrao(texto):
    normalizado = unicodedata.normalize('NFKD', texto.casefold())
    normalizado = ''.join(
        caractere for caractere in normalizado
        if not unicodedata.combining(caractere)
    )
    palavras = set(re.findall(r'[a-z0-9]+', normalizado))
    return bool(palavras & _PROFANITY)
