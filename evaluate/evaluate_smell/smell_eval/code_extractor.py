"""
Extração de código Java limpo a partir do output do modelo.

Estratégia em cascata:
  1. Extrai bloco ```java ... ``` se existir
  2. Extrai bloco ``` ... ``` genérico
  3. Localiza o primeiro token de declaração Java (public/private/protected/void/class)
     e extrai daí até o fechamento do último bloco (contagem de chaves)
  4. Devolve o texto original se nenhuma extração funcionar
"""

import re


def extract_java_code(text: str) -> str:
    """
    Extrai o bloco de código Java do output bruto do modelo.
    Nunca retorna string vazia — devolve o original se não conseguir extrair.
    """
    if not text or not text.strip():
        return text

    # 1. Bloco ```java ... ```
    code = _extract_fenced(text, "java")
    if code:
        return code

    # 2. Bloco ``` ... ``` genérico
    code = _extract_fenced(text, "")
    if code:
        return code

    # 3. Primeira declaração Java reconhecível
    code = _extract_from_declaration(text)
    if code:
        return code

    # 4. Fallback: texto original sem markdown inline
    return _strip_inline_markdown(text)


# Helpers Provados
def _extract_fenced(text: str, lang: str) -> str:
    """Extrai conteúdo de bloco delimitado por triple-backtick."""
    pattern = rf"```{re.escape(lang)}\s*(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    if matches:
        return max(matches, key=len).strip()
    return ""


# Padrões de início de declaração Java
_JAVA_DECL = re.compile(
    r"((?:(?:public|private|protected|static|final|abstract|synchronized)\s+)*"
    r"(?:class|interface|enum|void|boolean|int|long|double|float|String|List|Map|"
    r"Set|Object|[A-Z][a-zA-Z0-9<>\[\]]+)\s+\w+\s*[({])",
    re.MULTILINE,
)


def _extract_from_declaration(text: str) -> str:
    """
    Encontra a primeira declaração Java e extrai até o fechamento do bloco.
    Usa contagem de chaves para determinar o fim.
    """
    match = _JAVA_DECL.search(text)
    if not match:
        return ""

    start = match.start()
    snippet = text[start:]

    # Conta chaves para encontrar o fim do bloco externo
    depth   = 0
    end_pos = len(snippet)

    for i, ch in enumerate(snippet):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end_pos = i + 1
                break

    return snippet[:end_pos].strip()


def _strip_inline_markdown(text: str) -> str:
    """Remove backticks inline e marcadores comuns."""
    text = re.sub(r"`{1,3}java", "", text)
    text = re.sub(r"`{1,3}",    "", text)
    text = re.sub(r"\*\*|__",   "", text)
    return text.strip()