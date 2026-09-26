# Diagramas como código

Los diagramas del informe se generan desde código para mantenerlos sincronizados con el texto y el backlog.

| Carpeta / archivo | Contenido | Salida |
| --- | --- | --- |
| `diagrams/cap3.py` | To-Be Scenario Maps e Impact Maps (lee las historias de `backlog/product-backlog.csv`) | `imgs/cap3/*.png` |
| `diagrams/cap4.py` | EventStorming, Candidate Context Discovery, Domain Storytelling y Context Map | `imgs/cap4/*.png` |
| `architecture/workspace.dsl` | Modelo C4 en Structurizr DSL (landscape, contexto, contenedores y despliegue) | `imgs/cap4/c4-*.png` |
| `architecture/context-map.cml` | Context Map en ContextMapper DSL | — |

## Cómo regenerar

Desde la raíz del repositorio:

```bash
# Capítulos III y IV (requiere Python 3 y Chromium o Google Chrome)
python3 diagrams/build_diagrams.py          # o: python3 diagrams/build_diagrams.py cap3

# Diagramas C4 (requiere Java 17+; descarga Structurizr CLI y PlantUML en architecture/.tools/)
python3 architecture/render.py
```

Los HTML intermedios quedan en `diagrams/html/` y pueden abrirse en el navegador para revisar un diagrama antes de exportarlo. El modelo C4 también puede abrirse y reorganizarse visualmente en [Structurizr Lite](https://docs.structurizr.com/lite) o en https://structurizr.com/dsl.
