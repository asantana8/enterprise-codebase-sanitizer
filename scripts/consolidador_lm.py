"""Consolida fontes dos projetos precatorios com filtros de seguranca."""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Profile:
    name: str
    extensions: tuple[str, ...]
    subfolders: tuple[str, ...]
    output_prefix: str
    default_project_suffix: str | None = None


PROFILES = {
    "java": Profile(
        "Java",
        (".cs", ".java", ".xsd", ".wsdl"),
        ("src",),
        "consolidado_backend_SIREQ",
    ),
    "angular": Profile(
        "Angular",
        (".html", ".ts"),
        ("src",),
        "consolidado_frontend_SIREQ",
        "-frontend",
    ),
    "postgres": Profile(
        "Postgres",
        (".sql",),
        ("src/main/resources/db",),
        "consolidado_db_SIREQ",
    ),
}
SENSITIVE_FILE_PATTERNS = (
    "web.config", "app.config", "*.config", "appsettings*.json",
    "appsettings*.yml", "appsettings*.yaml", "*.secrets*", "*.secret",
    "*.env", "*.env.local", "*.env.*.local", ".env*", "*.properties",
    "*.properties.local", "*.yml", "*.yaml", "*.pem", "*.key", "*.pub",
    "*.pfx", "*.p12", "*.jks", "*.cer", "*.crt", "*.pwd", "*.password",
    "*credentials*", "*token*", "secrets.json", "secrets.*.json",
    "Dockerfile.local", "*.env.docker", "*.bak", "*.backup", "*.old",
    "*dump*",
)
SENSITIVE_DIRS = {
    "config", ".config", "secrets", ".secrets", "private", "credentials",
    "keys", "certificates", "certs", ".env.local", ".env.production",
    ".env.development", "vault",
}
SENSITIVE_CONTENT_PATTERNS = (
    r"Server\s*=.*Password\s*=",
    r"ConnectionString\s*[=:]\s*['\"].*(?:password|pwd|secret)",
    r"DefaultConnection\s*[=:]\s*['\"].*",
    r"Data\s*Source\s*=.*User\s*Id\s*=.*Password",
    r"password\s*[=:]\s*['\"](?!.*\{\{)",
    r"passwd\s*[=:]\s*['\"]", r"pwd\s*[=:]\s*['\"]",
    r"api[_-]?key\s*[=:]\s*['\"]", r"apikey\s*[=:]\s*['\"]",
    r"api[_-]?secret\s*[=:]\s*['\"]", r"access[_-]?token\s*[=:]\s*['\"]",
    r"auth[_-]?token\s*[=:]\s*['\"]",
    r"bearer\s+[a-zA-Z0-9._\-]+",
    r"process\.env\.\w+.*(?:password|token|key|secret)",
    r"DefaultAzureCredential", r"AccountName\s*=.*AccountKey\s*=",
    r"BlobEndpoint\s*=.*SharedAccessSignature",
    r"secret\s*[=:]\s*['\"]", r"private[_-]?key\s*[=:]\s*['\"]",
    r"oauth[_-]?token\s*[=:]\s*['\"]", r"jwt\s*[=:]\s*['\"]",
)
SENSITIVE_CONTENT_REGEX = tuple(re.compile(pattern, re.IGNORECASE) for pattern in SENSITIVE_CONTENT_PATTERNS)


class Tee:
    def __init__(self, terminal, log_file) -> None:
        self.terminal = terminal
        self.log_file = log_file

    def write(self, text: str) -> int:
        self.terminal.write(text)
        self.log_file.write(text)
        self.log_file.flush()
        return len(text)

    def flush(self) -> None:
        self.terminal.flush()
        self.log_file.flush()


DEFAULT_PROFILE = "java"
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "fontes_consolidados_LM"


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raiz",
        type=Path,
        default=SCRIPT_DIR,
        help=f"Diretorio raiz de varredura (padrao: pasta do script, {SCRIPT_DIR}).",
    )
    parser.add_argument(
        "--perfil",
        choices=PROFILES,
        default=None,
        help=f"Perfil de processamento; se omitido, sera solicitado (padrao: {DEFAULT_PROFILE}).",
    )
    parser.add_argument(
        "--destino",
        type=Path,
        default=None,
        help=f"Pasta de destino do consolidado; se omitida, sera solicitada (padrao: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--diretorio-alvo",
        type=Path,
        default=None,
        help="Diretorio de fontes a consolidar; substitui o diretorio padrao do perfil.",
    )
    parser.add_argument("--prefixo", default="precatorios")
    return parser.parse_args()


def choose_profile(profile_name: str | None) -> Profile:
    if profile_name:
        return PROFILES[profile_name]

    print("Perfis disponiveis:")
    profile_keys = tuple(PROFILES)
    for number, (key, profile) in enumerate(PROFILES.items(), start=1):
        extensions = ", ".join(profile.extensions)
        subfolders = ", ".join(profile.subfolders)
        default_flag = " [padrao]" if key == DEFAULT_PROFILE else ""
        print(f"  {number}. {profile.name} ({extensions}) - subpastas: {subfolders}{default_flag}")

    while True:
        selected = input(f"Escolha o perfil (1-{len(profile_keys)}) [Enter = {DEFAULT_PROFILE}]: ").strip().lower()
        if not selected:
            return PROFILES[DEFAULT_PROFILE]
        if selected in profile_keys:
            return PROFILES[selected]
        if selected.isdigit() and 1 <= int(selected) <= len(profile_keys):
            return PROFILES[profile_keys[int(selected) - 1]]
        print(f"Escolha 1 a {len(profile_keys)}, informe o nome do perfil ou pressione Enter para o padrao.")


def choose_output_dir(destination: Path | None) -> Path:
    if destination:
        return destination.expanduser().resolve()

    while True:
        answer = input(f"Pasta de destino do consolidado [Enter = {DEFAULT_OUTPUT_DIR}]: ").strip().strip('"')
        candidate = Path(answer).expanduser() if answer else DEFAULT_OUTPUT_DIR
        try:
            return candidate.resolve()
        except OSError as error:
            print(f"Caminho invalido ({error}). Tente novamente.")


def choose_target_directory(
    root: Path,
    prefix: str,
    profile: Profile,
    target_directory: Path | None,
) -> Path | None:
    if target_directory:
        return target_directory.expanduser().resolve()

    default_directory = (
        root / f"{prefix}{profile.default_project_suffix}" / profile.subfolders[0]
        if profile.default_project_suffix
        else root
    )
    while True:
        answer = input(f"Pasta alvo da varredura [Enter = {default_directory}]: ").strip().strip('"')
        candidate = Path(answer).expanduser() if answer else default_directory
        try:
            return candidate.resolve()
        except OSError as error:
            print(f"Caminho invalido ({error}). Tente novamente.")


def choose_search_target(
    root: Path,
    prefix: str,
    profile: Profile,
    target_directory: Path | None,
) -> tuple[str, Path | None]:
    if target_directory:
        return prefix, choose_target_directory(root, prefix, profile, target_directory)

    while True:
        mode = input("Modo de busca: [A] Pasta especifica ou [B] Pastas com prefixo definido? ").strip().lower()
        if mode == "a":
            return prefix, choose_target_directory(root, prefix, profile, None)
        if mode == "b":
            selected_prefix = input(f"Prefixo das pastas [Enter = {prefix}]: ").strip()
            return selected_prefix or prefix, None
        print("Opcao invalida. Informe A para pasta especifica ou B para pastas com prefixo.")


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def append_log(path: Path, message: str) -> None:
    with path.open("a", encoding="utf-8") as log:
        log.write(message.rstrip() + "\n\n")


def read_gitignore(root: Path) -> list[str]:
    path = root / ".gitignore"
    if not path.is_file():
        return []
    return [
        line.strip().replace("\\", "/")
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "!"))
    ]


def gitignore_reason(file: Path, root: Path, patterns: list[str]) -> str | None:
    relative = file.relative_to(root).as_posix()
    for pattern in patterns:
        if pattern.endswith("/"):
            directory = pattern.rstrip("/")
            if any(part == directory or part.startswith(directory) for part in Path(relative).parts):
                return f".gitignore: diretorio {pattern}"
        elif "/" in pattern and fnmatch.fnmatch(relative, f"*{pattern}*"):
            return f".gitignore: caminho {pattern}"
        elif fnmatch.fnmatch(file.name, pattern) or fnmatch.fnmatch(relative, f"*{pattern}"):
            return f".gitignore: padrao {pattern}"
    return None


def sensitive_name_reason(file: Path, root: Path, gitignore: list[str]) -> str | None:
    for pattern in SENSITIVE_FILE_PATTERNS:
        if fnmatch.fnmatch(file.name.lower(), pattern.lower()):
            return f"padrao sensivel no nome: {pattern}"
    for part in file.relative_to(root).parent.parts:
        if part.lower() in SENSITIVE_DIRS:
            return f"localizado em diretorio sensivel: {part}"
    return gitignore_reason(file, root, gitignore)


def content_reason(content: str) -> str | None:
    for pattern, regex in zip(SENSITIVE_CONTENT_PATTERNS, SENSITIVE_CONTENT_REGEX):
        if regex.search(content):
            preview = pattern[:50]
            return f"conteudo sensivel detectado: padrao '{preview}...'"
    return None


def remove_comments(content: str) -> str:
    """Remove comentários comuns de Java, Angular, SQL e CSS sem alterar strings."""
    result: list[str] = []
    index = 0
    line_start = True
    quote: str | None = None

    while index < len(content):
        character = content[index]
        next_two = content[index:index + 2]
        next_four = content[index:index + 4]

        if quote:
            result.append(character)
            if character == "\\" and quote != "`" and index + 1 < len(content):
                result.append(content[index + 1])
                index += 2
                line_start = False
                continue
            if character == quote:
                quote = None
            line_start = character == "\n"
            index += 1
            continue

        if character in "'\"`":
            quote = character
            result.append(character)
            line_start = False
            index += 1
            continue

        if next_four == "<!--":
            end = content.find("-->", index + 4)
            index = len(content) if end == -1 else end + 3
            continue

        if next_two == "/*":
            end = content.find("*/", index + 2)
            index = len(content) if end == -1 else end + 2
            continue

        if next_two in ("//", "--"):
            end = content.find("\n", index + 2)
            index = len(content) if end == -1 else end
            continue

        if character == "#" and line_start:
            end = content.find("\n", index + 1)
            index = len(content) if end == -1 else end
            continue

        result.append(character)
        line_start = character == "\n" or (line_start and character.isspace())
        index += 1

    return "".join(result)


def write_header(path: Path, root: Path, extensions: tuple[str, ...], projects: list[Path], exclusion_log: Path) -> None:
    path.write_text(
        "=" * 80 + "\nCONSOLIDADO DE FONTES - PROJETO SIREQ\n" + "=" * 80
        + f"\nData de geracao: {datetime.now():%d/%m/%Y %H:%M:%S}"
        + f"\nExtensoes processadas: {', '.join(extensions)}"
        + f"\nPastas processadas: {len(projects)}\n" + "=" * 80 + "\n\n",
        encoding="utf-8",
    )
    exclusion_log.write_text(
        "=" * 80 + "\nLOG DE EXCLUSOES DE SEGURANCA - PROJETO SIREQ\n"
        + "=" * 80 + f"\nData de execucao: {datetime.now():%d/%m/%Y %H:%M:%S}"
        + f"\nDiretorio raiz: {root}\n\n"
        + "PADROES DE SEGURANCA APLICADOS:\n"
        + "--- Extensoes e nomes sensiveis ---\n"
        + "\n".join(SENSITIVE_FILE_PATTERNS)
        + "\n\n--- Diretorios sensiveis ---\n"
        + ", ".join(sorted(SENSITIVE_DIRS)) + "\n\n\n",
        encoding="utf-8",
    )


def find_profile_files(
    project: Path,
    subfolders: tuple[str, ...],
    extensions: tuple[str, ...],
    excluded_directories: tuple[str, ...] = (),
) -> list[Path]:
    files: set[Path] = set()
    for subfolder in subfolders:
        normalized = subfolder.replace("\\", "/").strip("/")
        matching_directories = {
            path for path in project.rglob("*")
            if path.is_dir()
            and path.relative_to(project).as_posix() == normalized
            and not any(part.lower() in excluded_directories for part in path.relative_to(project).parts)
        }
        for directory in matching_directories:
            files.update(
                path for path in directory.rglob("*")
                if path.is_file()
                and path.suffix.lower() in extensions
                and not any(part.lower() in excluded_directories for part in path.relative_to(project).parts)
            )
    return sorted(files, key=lambda path: str(path).lower())


def find_target_files(
    target_directory: Path,
    extensions: tuple[str, ...],
    excluded_directories: tuple[str, ...] = (),
) -> list[Path]:
    return sorted(
        (
            path for path in target_directory.rglob("*")
            if path.is_file()
            and path.suffix.lower() in extensions
            and not any(part.lower() in excluded_directories for part in path.relative_to(target_directory).parts)
        ),
        key=lambda path: str(path).lower(),
    )


def consolidate(
    root: Path,
    profile: Profile,
    prefix: str,
    output_dir: Path,
    target_directory: Path | None = None,
) -> int:
    extensions = profile.extensions
    subfolders = profile.subfolders
    projects = (
        [target_directory.parent]
        if target_directory and target_directory.is_dir()
        else ([] if target_directory else sorted((path for path in root.iterdir() if path.is_dir() and path.name.lower().startswith(prefix.lower())), key=lambda path: path.name.lower()))
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{profile.output_prefix}_{timestamp()}.txt"
    exclusion_path = output_dir / f"exclusoes_seguranca_{timestamp()}.log"
    write_header(output_path, root, extensions, projects, exclusion_path)
    totals = {"processed": 0, "added": 0, "excluded": 0}

    if not projects:
        if target_directory:
            print(f"Diretorio alvo nao encontrado: {target_directory}")
            return 0
        print(f"Nenhuma pasta com prefixo '{prefix}' encontrada em: {root}")
        return 0
    search_description = (
        f"Pasta alvo: {target_directory}"
        if target_directory
        else f"Encontradas {len(projects)} pasta(s) com prefixo '{prefix}'"
    )
    print("=" * 38 + f"\n{search_description}\n" + "=" * 38)
    print(f"Arquivos serao consolidados em:\n{output_path}\n" + "=" * 38)

    for project in projects:
        with output_path.open("a", encoding="utf-8") as output:
            output.write("=" * 80 + f"\nPROJETO: {project.name}\nData: {datetime.now():%d/%m/%Y %H:%M:%S}\nCaminho: {project}\n" + "=" * 80 + "\n\n")
        print(f"\n>>> Entrando em: {project}")
        gitignore = read_gitignore(project)
        excluded_directories = ("node_modules",) if profile is PROFILES["angular"] else ()
        files = (
            find_target_files(target_directory, extensions, excluded_directories)
            if target_directory
            else find_profile_files(project, subfolders, extensions, excluded_directories)
        )
        valid_files = []
        for file in files:
            reason = sensitive_name_reason(file, project, gitignore)
            if reason:
                print(f"  [!] Excluido: {file.name} ({reason})")
                append_log(exclusion_path, f"[{datetime.now():%H:%M:%S}] EXCLUIDO: {file}\n           Motivo: {reason}")
                totals["excluded"] += 1
            else:
                valid_files.append(file)
        print(f"  Encontrados {len(valid_files)} arquivo(s) valido(s). Processando..." if valid_files else f"  Nenhum arquivo com extensoes: {', '.join(extensions)} encontrado apos filtros.")
        for file in valid_files:
            totals["processed"] += 1
            try:
                content = file.read_text(encoding="utf-8", errors="replace")
                content_without_comments = remove_comments(content)
                reason = content_reason(content_without_comments)
                if reason:
                    print(f"  [?] BLOQUEADO (conteudo sensivel): {file.name}")
                    append_log(exclusion_path, f"[{datetime.now():%H:%M:%S}] BLOQUEADO: {file}\n           Motivo: {reason}")
                    totals["excluded"] += 1
                    continue
                with output_path.open("a", encoding="utf-8") as output:
                    output.write(f"----------------------------------------------------------\nPath do arquivo: {file}\nNome do arquivo: {file.name}\n-----------------------------------------------------------\n{content_without_comments}\n\n")
                print(f"  [?] Adicionado: {file.name}")
                totals["added"] += 1
            except OSError as error:
                print(f"  [?] ERRO ao ler arquivo: {file.name} - {error}")
                append_log(exclusion_path, f"[{datetime.now():%H:%M:%S}] ERRO: {file}\n           Motivo: {error}")
                totals["excluded"] += 1
        print(f"<<< Saindo de: {project}")

    print("\n" + "=" * 38 + "\nRESUMO DA EXECUCAO:\n" + "=" * 38)
    print(f"Total de arquivos processados: {totals['processed']}\nTotal de arquivos adicionados: {totals['added']}\nTotal de arquivos excluidos: {totals['excluded']}")
    print("=" * 38 + f"\nConsolidado final salvo em:\n{output_path}\n\nLog de exclusoes salvo em:\n{exclusion_path}\n" + "=" * 38)
    return 0


def run_consolidation(args: argparse.Namespace) -> int:
    try:
        profile = choose_profile(args.perfil)
        print(f"\nPerfil selecionado: {profile.name}")
        print(f"Extensoes: {', '.join(profile.extensions)}")
        print(f"Subpastas: {', '.join(profile.subfolders)}")
        output_dir = choose_output_dir(args.destino)
        root = args.raiz.resolve()
        prefix, target_directory = choose_search_target(root, args.prefixo, profile, args.diretorio_alvo)
        if target_directory:
            print(f"Diretorio alvo: {target_directory}")
        print(f"Pasta de destino: {output_dir}\n")
        return consolidate(root, profile, prefix, output_dir, target_directory)
    except OSError as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1


def main() -> int:
    args = arguments()
    while True:
        print("\n" + "=" * 48)
        print(" CONSOLIDADOR DE FONTES - PROJETO SIREQ")
        print("=" * 48)
        print(f"Raiz da busca: {args.raiz}")
        print(f"Prefixo padrao: {args.prefixo}")
        print("\n  1. Iniciar nova consolidacao")
        print("  2. Sair")
        print("=" * 48)
        try:
            option = input("Escolha uma opcao: ").strip()
        except EOFError:
            print("\nEntrada encerrada. Finalizando o consolidador.")
            return 0

        if option == "1":
            try:
                run_consolidation(args)
            except EOFError:
                print("\nEntrada encerrada. Finalizando o consolidador.")
                return 0
        elif option == "2":
            print("Encerrando o consolidador.")
            return 0
        else:
            print("Opcao invalida. Escolha 1 para consolidar ou 2 para sair.")


if __name__ == "__main__":
    log_path = Path(__file__).resolve().parent / f"consolidador_lm_{timestamp()}.log"
    with log_path.open("w", encoding="utf-8") as log_file:
        output = Tee(sys.stdout, log_file)
        errors = Tee(sys.stderr, log_file)
        with redirect_stdout(output), redirect_stderr(errors):
            exit_code = main()
    sys.exit(exit_code)