# Contexto del Proyecto para Agentes de IA

Este repositorio es un paquete de nodos personalizados (custom nodes) para ComfyUI.

## Reglas Estrictas de Desarrollo:

1. **Estructura ComfyUI:** Todo nodo debe ser una clase Python con los métodos y atributos requeridos por la API de ComfyUI (`INPUT_TYPES`, `RETURN_TYPES`, `FUNCTION`, `CATEGORY`).
2. **Registro de Nodos:** El archivo `__init__.py` debe exportar obligatoriamente el diccionario `NODE_CLASS_MAPPINGS` y opcionalmente `NODE_DISPLAY_NAME_MAPPINGS`.
3. **Compatibilidad KJNodes (Set/Get):** Los tensores (Latents, Masks, Images) y el diccionario `state_info` deben pasarse como tipos genéricos u objetos nativos (ej. `LATENT`, `MASK`) sin alterar su referencia interna para que los nodos Get/Set de KJNodes puedan capturarlos asíncronamente a través del árbol del flujo.
4. **Lógica Sequential Batcher:** Cualquier nodo procesador de tiempo debe incorporar heurísticas para aceptar entradas en listas iterativas (List Inputs) y respetar particiones de memoria divisibles (e.g. 4n + 1), asegurando que las secuencias no se rompan y sean tolerantes a los Loop Triggers externos.
5. **No usar tabulaciones:** La indentación debe ser obligatoriamente con espacios.
