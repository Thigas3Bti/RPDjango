def eh_pescador(usuario):
    return (
        usuario.is_authenticated
        and usuario.groups.filter(name='Pescador').exists()
    )
