def eh_pescador(usuario):
    return (
        usuario.is_authenticated
        and (
            usuario.is_staff
            or usuario.is_superuser
            or usuario.groups.filter(name__iexact='pescador').exists()
        )
    )
