# InstagramStats

## Requisitos

Requiere el modulo [`instaloader'](https://instaloader.github.io/) de Python.

## Ejecución

Debe ejecutar `python InstagramStats.py <PERFIL> --login <SESION> [--get-stats USUARIO ...] ', donde:

    • <PERFIL>: nombre de usuario del perfil a obtener estadísticas.
    • <SESION>: corresponde al nombre del sitio en donde un usuario comienza su navegación.
    • <USUARIO>: opcional. obtiene estadísticas en particular de los perfiles mencionados.

Por ejemplo,
```python InstagramStats.py zuck --login zuck --get-stats billieeilish joebiden```

## Recomendaciones

Se recomienda no utilizar este programa a la vez que se utiliza Instagram, pues podrá ser considerado como actividad sospechosa para la plataforma.
