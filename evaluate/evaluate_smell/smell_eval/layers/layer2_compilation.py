"""
Camada 2 — Compilation Rate (javac).

Verifica se o código gerado pelo modelo é sintaticamente válido compilando
com javac. Usa extract_java_code() para limpar markdown antes de compilar.

Estratégia de erros:
  - Erros de SINTAXE (';' expected, illegal start of expression, etc.)
  - Erros IGNORÁVEIS (cannot find symbol, incompatible types, etc.)

O código é envolto em um wrapper com stubs do domínio antes de compilar,
permitindo avaliar trechos isolados sem acesso às classes do projeto original.

passed = True  : código compila sem erros de sintaxe
passed = False : erros de sintaxe reais detectados
score = -1.0   : javac não disponível, saída vazia, ou timeout de compilação
"""

import os
import shutil
import subprocess
import tempfile
from typing import Optional

from smell_eval.config import LayerResult
from smell_eval.code_extractor import extract_java_code

# Timeout de compilação. Saídas degeneradas (geração sem parar, concatenação
# de strings profundamente aninhada, etc.) podem fazer o javac travar por
# muito mais que alguns segundos — 600s (10min) dá margem confortável antes
# de descartar o caso como falha de compilação.
_JAVAC_TIMEOUT_SECONDS = 600

# Wrapper com imports e stubs de domínio para compilação isolada de trechos
_WRAPPER = """\
import java.util.*;
import java.io.*;
import java.math.*;
import java.util.concurrent.*;
public class Snippet {{
    // ── stubs de domínio ────────────────────────────────────────
    static class Position {{
        Position(int r, int c) {{}}
        @Override public boolean equals(Object o) {{ return false; }}
    }}
    static class Pawn {{}}
    interface Piece {{ Object getColor(); boolean isValidMove(Position f, Position t); }}
    static class Product {{}}
    static class Order {{
        void setCustomerId(String v) {{}} void setProductId(String v) {{}}
        void setQuantity(int v) {{}} void setTotalPrice(double v) {{}}
        void setDeliveryAddress(String v) {{}}
    }}
    static class Transaction {{
        Transaction(String a, String b, BigDecimal c, String d, String e, String f) {{}}
    }}
    static class AuthToken {{}}
    static class Page<T> {{}}
    static class LogEntry {{
        void setEventType(String v) {{}} void setUserId(String v) {{}}
        void setSessionId(String v) {{}} void setAction(String v) {{}}
        void setResource(String v) {{}} void setStatusCode(int v) {{}}
        void setTimestamp(long v) {{}}
    }}
    static class ScheduledTask {{
        void setId(String v) {{}} void setName(String v) {{}}
        void setCronExpression(String v) {{}} void setMaxRetries(int v) {{}}
        void setTimeout(long v, TimeUnit u) {{}} void setEnabled(boolean v) {{}}
    }}
    static class UserData {{
        public String getFirstName() {{ return ""; }}
        public String getLastName()  {{ return ""; }}
        public String getEmail()     {{ return ""; }}
        public String getPhone()     {{ return ""; }}
        public String getAddress()   {{ return ""; }}
    }}
    static class ProductSearchCriteria {{
        public String  getName()     {{ return ""; }}
        public double  getMinPrice() {{ return 0;  }}
        public double  getMaxPrice() {{ return 0;  }}
        public String  getCategory() {{ return ""; }}
        public boolean isInStock()   {{ return false; }}
    }}
    // ── stubs de dependências ──────────────────────────────────
    boolean isPositionOutOfBounds(Position p)        {{ return false; }}
    boolean isEmpty(Position p)                      {{ return false; }}
    boolean hasNoPieceInPath(Position f, Position t) {{ return true;  }}
    boolean isValidPawnMove(Position f, Position t)  {{ return true;  }}
    void    updateIsKingDead(Position p)             {{}}
    Object  getCell(Position p)                      {{ return null;  }}
    Piece   getPiece(Position p)                     {{ return null;  }}
    void    sendWelcomeEmail(String a, String b, String c) {{}}
    Object  repository  = null;
    Object  logRepository = null;
    Object  scheduler   = null;
    Object  accountRepository = null;
    Object  transactionRepository = null;
    Object  orderRepository = null;

    {code}
}}
"""

# Padrões de erros de sintaxe real
_SYNTAX_ERRORS = (
    "illegal start of expression",
    "reached end of file",
    "';' expected",
    "')' expected",
    "illegal character",
    "unclosed string literal",
    "class, interface, or enum expected",
    "not a statement",
)

# Padrões de erros ignoráveis
_IGNORABLE_ERRORS = (
    "cannot find symbol",
    "package does not exist",
    "cannot override",
    "incompatible types",
    "method does not override",
)


def evaluate(raw_output: str) -> LayerResult:
    """
    Extrai código Java do output bruto, envolve em wrapper e compila com javac.

    Retorna:
        score = 1.0  : código sintaticamente válido (passed=True)
        score = 0.0  : erros de sintaxe detectados (passed=False)
        score = -1.0 : javac não disponível, saída vazia, ou timeout de compilação
    """
    javac = _find_javac()
    if not javac:
        return LayerResult(
            score=-1.0,
            details={"error": "javac not found on system"},
        )

    code = extract_java_code(raw_output)
    if not code or not code.strip():
        return LayerResult(score=0.0, details={"error": "empty output after extraction"}, passed=False)

    wrapped = _WRAPPER.format(code=_indent(code, "    "))

    with tempfile.TemporaryDirectory() as tmpdir:
        java_file = os.path.join(tmpdir, "Snippet.java")
        with open(java_file, "w") as f:
            f.write(wrapped)

        try:
            proc = subprocess.run(
                [javac, java_file],
                capture_output=True,
                text=True,
                timeout=_JAVAC_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return LayerResult(
                score=-1.0,
                details={
                    "error": "javac timeout",
                    "timeout_seconds": _JAVAC_TIMEOUT_SECONDS,
                    "note": "provável saída degenerada do modelo (geração sem parar, "
                            "concatenação de strings profundamente aninhada, etc.)",
                },
                passed=False,
            )

    all_errors    = [l for l in proc.stderr.splitlines() if "error:" in l.lower()]
    syntax_errors = [
        l for l in all_errors
        if any(s in l.lower() for s in _SYNTAX_ERRORS)
        and not any(i in l.lower() for i in _IGNORABLE_ERRORS)
    ]

    valid = len(syntax_errors) == 0
    return LayerResult(
        score=1.0 if valid else 0.0,
        details={
            "syntax_valid":   valid,
            "syntax_errors":  syntax_errors[:5],
            "ignored_errors": len(all_errors) - len(syntax_errors),
        },
        passed=valid,
    )


def _find_javac() -> Optional[str]:
    if shutil.which("javac"):
        return "javac"
    for p in ["/usr/bin/javac", "/usr/local/bin/javac",
              os.path.expanduser("~/.sdkman/candidates/java/current/bin/javac")]:
        if os.path.exists(p):
            return p
    return None


def _indent(code: str, prefix: str) -> str:
    return "\n".join(prefix + line for line in code.splitlines())
