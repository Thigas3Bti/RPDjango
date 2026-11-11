def eh_pescador(usuario):
    if not usuario.is_authenticated or not usuario.is_active:
        return False
    if usuario.is_staff:
        return True
    return usuario.groups.filter(name='Pescador').exists()
    return (
        usuario.is_authenticated
        and usuario.groups.filter(name='Pescador').exists()
    )
