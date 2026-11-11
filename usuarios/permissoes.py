def eh_pescador(usuario):
    return usuario.is_authenticated and (
        usuario.is_staff or usuario.groups.filter(name='Pescador').exists()
    )
