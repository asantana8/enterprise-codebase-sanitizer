"""
setup_agents_v2.py — Gerador Agnostico e Automatizado de AGENTS.md para Monorepos

Este script varre qualquer estrutura de monorepo ou diretorio multi-projetos,
detecta automaticamente as tecnologias, linguagens e manifestos (Maven, Gradle,
Node/npm, Python, Go, Rust, Docker) e portas configuradas, e gera:

1. Um arquivo AGENTS.md Global Mestre na raiz do monorepo, contendo:
   - Visao geral do ecossistema e mapa dinamico de todos os subprojetos.
   - Regras de seguranca cross-cutting (nao versionar segredos/tokens).
   - Secao de exclusao de contexto (ignore list espelhada do .copilotignore).
   - Diretrizes de invocacao de agentes.
2. Um arquivo AGENTS.md Local na raiz de cada subprojeto identificado, contendo:
   - Frontmatter YAML padronizado.
   - Stack tecnologica e comandos operacionais customizados para a tecnologia.
   - Estrutura de pastas, convencoes e regras de seguranca do servico.
   - Ignore list local anexada.

Uso:
    python setup_agents_v2.py --raiz /caminho/do/monorepo --nome-sistema "MeuSistema"
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

# Configuracao de Logs
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("setup_agents")

# ==============================================================================
# SECAO DE EXCLUSAO DE CONTEXTO (IGNORE LIST)
# ==============================================================================
IGNORE_SECTION_TITLE = "Regras de Exclusao de Contexto (Ignore List)"

IGNORE_SECTION_BODY = """Estas diretrizes espelham o arquivo `.copilotignore` e `.gitignore`. Agentes autonomos (GitHub Copilot, Claude Code, Cursor, Windsurf, etc.) **NAO devem ler, indexar, varrer ou anexar ao contexto** os caminhos abaixo — sao artefatos gerados, binarios ou massas de dados que apenas consomem tokens sem agregar valor semantico.

### 5.1. Build e Compilacao
* Java / Maven / Gradle: `/target/`, `/build/`, `/out/`, `.gradle/`, `.mvn/`, `*.class`, `*.jar`, `*.war`, `*.ear`
* Node / Angular / React: `node_modules/`, `/dist/`, `/.angular/`, `/tmp/`, `/coverage/`, `npm-debug.log*`, `yarn-debug.log*`
* Python: `__pycache__/`, `*.pyc`, `.venv/`, `env/`, `.pytest_cache/`, `.coverage`
* Go / Rust / C++: `/bin/`, `/pkg/`, `/target/`, `*.exe`, `*.so`, `*.dylib`, `*.dll`

### 5.2. Configuracoes de IDE, Caches e Metadados
* IntelliJ IDEA: `.idea/`, `*.iml`, `*.iws`, `*.ipr`
* VS Code: `.vscode/*` (excecoes permitidas: `settings.json`, `tasks.json`, `launch.json`)
* Tooling / Caches: `.cache/`, `.classpath`, `.project`, `.settings/`

### 5.3. Logs, Traces e Temporarios
* `*.log`, `logs/`, `*.tmp`, `*.bak`, `*.swp`, `*.hprof`

### 5.4. Massa de Dados, Mocks e SQL Extenso
* `/src/test/resources/mock-data/`, `*.sql`, `*.csv`, `*.xlsx`, `*.dump`

> **Excecao controlada:** migrations de banco de dados (`db/migration/`, `migrations/`) so devem ser abertas quando a tarefa for explicitamente sobre schema de banco, e sempre de forma pontual (arquivo especifico), nunca em varredura completa.

### 5.5. Arquivos Gerados, Maps e Midias Estaticas
* `*.min.js`, `*.min.css`, `*.map`
* `*.pdf`, `*.png`, `*.jpg`, `*.jpeg`, `*.svg`, `*.ico`, `*.zip`, `*.tar.gz`

### 5.6. Diretrizes Operacionais para o Agente
1. **Nunca** execute buscas recursivas (`grep`/`glob`) sem excluir os padroes acima.
2. Prefira ler o codigo-fonte principal e os manifestos (`pom.xml`, `package.json`, `pyproject.toml`, `go.mod`, etc.) em vez de artefatos compilados.
3. Se um arquivo ignorado for indispensavel para a tarefa, abra **apenas** aquele arquivo e justifique a leitura na resposta.
4. Ao criar novos artefatos gerados, garanta que o padrao correspondente exista no `.copilotignore` e no `.gitignore`."""


def build_ignore_section(number: int) -> str:
    """Monta a secao de ignore list renumerando os subtitulos (N.1, N.2, ...)."""
    body = re.sub(r"^### 5\.", f"### {number}.", IGNORE_SECTION_BODY, flags=re.MULTILINE)
    return f"## 🚫 {number}. {IGNORE_SECTION_TITLE}\n{body}\n"


def append_ignore_section(content: str, number: int | None = None) -> str:
    """Anexa a secao de ignore list ao final do conteudo."""
    if IGNORE_SECTION_TITLE in content:
        return content
    if number is None:
        numbers = [int(n) for n in re.findall(r"^##\s+(?:\S+\s+)?(\d+)\.", content, flags=re.MULTILINE)]
        number = (max(numbers) + 1) if numbers else 5
    return content.rstrip("\n") + "\n\n---\n\n" + build_ignore_section(number)


# ==============================================================================
# ESTRUTURA DE DADOS DO PROJETO DETECTADO
# ==============================================================================
@dataclass
class DetectedProject:
    name: str
    path: Path
    relative_path: str
    category: str
    tech_stack: str
    ports: list[str] = field(default_factory=list)
    manifest_file: str = ""
    build_cmd: str = ""
    test_cmd: str = ""
    run_cmd: str = ""
    description: str = ""


# ==============================================================================
# DETECTOR DE PROJETOS E TECNOLOGIAS
# ==============================================================================
class ProjectDetector:
    """Inspeciona diretorios para identificar tecnologias, manifestos, portas e comandos."""

    @staticmethod
    def detect_ports_in_file(file_path: Path) -> list[str]:
        ports: set[str] = set()
        if not file_path.is_file():
            return []
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            matches = re.findall(
                r"(?:server\.port|PORT|port|EXPOSE)\s*[:=]\s*[\"']?(\d{4,5})[\"']?",
                content,
                re.IGNORECASE,
            )
            for m in matches:
                p = int(m)
                if 1024 <= p <= 65535:
                    ports.add(str(p))
        except Exception as e:
            logger.debug("Erro ao ler portas em %s: %s", file_path, e)
        return sorted(list(ports))

    @classmethod
    def inspect_directory(cls, dir_path: Path, root_path: Path) -> DetectedProject | None:
        rel_path = str(dir_path.relative_to(root_path)).replace("\\", "/")
        if rel_path == ".":
            return None

        if dir_path.name.startswith(".") or dir_path.name in {
            "node_modules",
            "target",
            "build",
            "dist",
            "out",
            "bin",
            "venv",
            ".venv",
        }:
            return None

        # 1. Java / Maven
        pom_xml = dir_path / "pom.xml"
        if pom_xml.is_file():
            return cls._inspect_maven(dir_path, pom_xml, rel_path)

        # 2. Java / Kotlin / Gradle
        build_gradle = dir_path / "build.gradle"
        build_gradle_kts = dir_path / "build.gradle.kts"
        if build_gradle.is_file() or build_gradle_kts.is_file():
            return cls._inspect_gradle(dir_path, rel_path)

        # 3. Node.js / Angular / React / Vue / TypeScript
        package_json = dir_path / "package.json"
        if package_json.is_file():
            return cls._inspect_nodejs(dir_path, package_json, rel_path)

        # 4. Python
        pyproject = dir_path / "pyproject.toml"
        req_txt = dir_path / "requirements.txt"
        if pyproject.is_file() or req_txt.is_file() or (dir_path / "setup.py").is_file():
            return cls._inspect_python(dir_path, rel_path)

        # 5. Go
        go_mod = dir_path / "go.mod"
        if go_mod.is_file():
            return cls._inspect_go(dir_path, go_mod, rel_path)

        # 6. Rust
        cargo_toml = dir_path / "Cargo.toml"
        if cargo_toml.is_file():
            return cls._inspect_rust(dir_path, cargo_toml, rel_path)

        return None

    @classmethod
    def _inspect_maven(cls, dir_path: Path, pom_xml: Path, rel_path: str) -> DetectedProject:
        name = dir_path.name
        description = "Microsservico / Biblioteca Java Maven"
        packaging = "jar"
        java_version = "17/21"

        try:
            tree = ET.parse(pom_xml)
            root = tree.getroot()
            for elem in root.iter():
                tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if tag == "artifactId" and elem.text and name == dir_path.name:
                    name = elem.text
                elif tag == "packaging" and elem.text:
                    packaging = elem.text
                elif tag == "description" and elem.text:
                    description = elem.text.strip()
        except Exception as e:
            logger.debug("Erro ao ler pom.xml em %s: %s", pom_xml, e)

        ports: list[str] = []
        for conf_name in ["application.yml", "application.properties", "application-local.yml"]:
            found_ports = cls.detect_ports_in_file(dir_path / "src" / "main" / "resources" / conf_name)
            for p in found_ports:
                if p not in ports:
                    ports.append(p)

        category = "Biblioteca JAR" if packaging == "jar" and not ports else "Backend / Java"
        tech_stack = f"Java {java_version} / Spring Boot (Maven)"

        return DetectedProject(
            name=name,
            path=dir_path,
            relative_path=rel_path,
            category=category,
            tech_stack=tech_stack,
            ports=ports,
            manifest_file="pom.xml",
            build_cmd="./mvnw clean package -DskipTests",
            test_cmd="./mvnw test",
            run_cmd="./mvnw spring-boot:run",
            description=description,
        )

    @classmethod
    def _inspect_gradle(cls, dir_path: Path, rel_path: str) -> DetectedProject:
        name = dir_path.name
        ports: list[str] = []
        for conf_name in ["application.yml", "application.properties"]:
            found_ports = cls.detect_ports_in_file(dir_path / "src" / "main" / "resources" / conf_name)
            for p in found_ports:
                if p not in ports:
                    ports.append(p)

        category = "Backend / Java (Gradle)"
        return DetectedProject(
            name=name,
            path=dir_path,
            relative_path=rel_path,
            category=category,
            tech_stack="Java / Kotlin (Gradle)",
            ports=ports,
            manifest_file="build.gradle",
            build_cmd="./gradlew build -x test",
            test_cmd="./gradlew test",
            run_cmd="./gradlew bootRun",
            description="Projeto Java/Kotlin gerenciado via Gradle",
        )

    @classmethod
    def _inspect_nodejs(cls, dir_path: Path, pkg_json: Path, rel_path: str) -> DetectedProject:
        name = dir_path.name
        description = "Aplicacao Node.js / Web"
        tech = "Node.js / JavaScript"
        category = "Frontend / Web"

        try:
            data = json.loads(pkg_json.read_text(encoding="utf-8", errors="replace"))
            name = data.get("name", name)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

            if "angular" in str(deps) or "@angular/core" in deps:
                tech = "Angular / TypeScript"
                category = "Frontend SPA (Angular)"
            elif "react" in deps:
                tech = "React / TypeScript" if "typescript" in deps else "React / JavaScript"
                category = "Frontend (React)"
            elif "vue" in deps:
                tech = "Vue.js"
                category = "Frontend (Vue)"
            elif "express" in deps or "nestjs" in deps or "@nestjs/core" in deps:
                tech = "NestJS / Node.js" if "nestjs" in str(deps) else "Node.js Express"
                category = "Backend / Node.js"

            if data.get("description"):
                description = data.get("description")
        except Exception as e:
            logger.debug("Erro ao ler package.json em %s: %s", pkg_json, e)

        ports = cls.detect_ports_in_file(dir_path / ".env")
        if not ports:
            ports = cls.detect_ports_in_file(dir_path / "angular.json")

        return DetectedProject(
            name=name,
            path=dir_path,
            relative_path=rel_path,
            category=category,
            tech_stack=tech,
            ports=ports or (["4200"] if "Angular" in tech else ["3000"]),
            manifest_file="package.json",
            build_cmd="npm run build",
            test_cmd="npm test",
            run_cmd="npm start",
            description=description,
        )

    @classmethod
    def _inspect_python(cls, dir_path: Path, rel_path: str) -> DetectedProject:
        name = dir_path.name
        ports = cls.detect_ports_in_file(dir_path / ".env")
        return DetectedProject(
            name=name,
            path=dir_path,
            relative_path=rel_path,
            category="Backend / Python",
            tech_stack="Python 3.11+",
            ports=ports or ["8000"],
            manifest_file="pyproject.toml / requirements.txt",
            build_cmd="python -m build",
            test_cmd="pytest",
            run_cmd="python main.py",
            description="Servico ou modulo em Python",
        )

    @classmethod
    def _inspect_go(cls, dir_path: Path, go_mod: Path, rel_path: str) -> DetectedProject:
        name = dir_path.name
        try:
            content = go_mod.read_text(encoding="utf-8", errors="replace")
            first_line = content.splitlines()[0] if content.splitlines() else ""
            if first_line.startswith("module"):
                name = first_line.split()[-1].split("/")[-1]
        except Exception:
            pass

        return DetectedProject(
            name=name,
            path=dir_path,
            relative_path=rel_path,
            category="Backend / Go",
            tech_stack="Go (Golang)",
            ports=["8080"],
            manifest_file="go.mod",
            build_cmd="go build ./...",
            test_cmd="go test ./...",
            run_cmd="go run main.go",
            description="Microsservico / Aplicacao em Go",
        )

    @classmethod
    def _inspect_rust(cls, dir_path: Path, cargo_toml: Path, rel_path: str) -> DetectedProject:
        name = dir_path.name
        return DetectedProject(
            name=name,
            path=dir_path,
            relative_path=rel_path,
            category="Backend / Systems (Rust)",
            tech_stack="Rust",
            ports=["8080"],
            manifest_file="Cargo.toml",
            build_cmd="cargo build --release",
            test_cmd="cargo test",
            run_cmd="cargo run",
            description="Servico / Aplicacao em Rust",
        )


# ==============================================================================
# GERADOR DE CONTEUDO PARA AGENTS.MD (GLOBAL E LOCAL)
# ==============================================================================
class AgentsGenerator:
    """Gera arquivos AGENTS.md globais e locais com base nos projetos detectados."""

    def __init__(self, system_name: str, root_path: Path, projects: list[DetectedProject]) -> None:
        self.system_name = system_name
        self.root_path = root_path
        self.projects = projects

    def generate_global_agents(self) -> str:
        """Gera o AGENTS.md Mestre Global para a raiz do Monorepo."""
        lines = [
            f"# 🤖 AGENTS.md — Guia Mestre de Agentes e IA do Ecossistema {self.system_name}\n",
            f"Welcome, AI Agent! Este arquivo e o **Guia Global Mestre de Orientacao para Assistentes de IA** (GitHub Copilot, Claude Code, Cursor, Windsurf, etc.) atuando no monorepo e ecossistema **{self.system_name}**.\n",
            "---\n",
            f"## 🏛️ 1. Visao Geral do Ecossistema {self.system_name}",
            f"O {self.system_name} e um ecossistema de software estruturado em modulos e microsservicos desacoplados para alta escalabilidade, manutenibilidade e qualidade tecnica.\n",
            "### 🚨 Regra de Ouro de Seguranca (Cross-cutting)",
            "> **NUNCA expor, hardcodar ou versionar no Git URLs privadas, chaves de acesso, senhas de banco de dados ou credenciais de rede.**",
            "> ",
            "> * Toda credencial sensivel deve ser injetada estritamente via **Variaveis de Ambiente** (`.env`, `environment variables`) ou **Secrets de CI/CD / Kubernetes**.",
            "> * Em documentacoes e amostras de codigo, utilize exclusivamente *placeholders* (ex: `<DB_HOST>`, `<API_KEY>`).\n",
            "---\n",
            "## 📐 2. Principios Arquiteturais e Separacao de Dominios",
            "Ao sugerir codigo ou arquitetura, respeite as convencoes do projeto:",
            "1. **Isolamento de Responsabilidades:** Mantenha a separacao entre camadas de apresentacao (Frontend), servicos de API (Backend) e persistencia de dados.",
            "2. **Contratos de Interface:** DTOs e payloads de API devem ser fortemente tipados e versionados.",
            "3. **Seguranca por Padrao:** Nao contorne autenticacao ou autorizacao sem diretriz explicita da arquitetura.\n",
            "---\n",
            f"## 🗺️ 3. Mapeamento dos {len(self.projects)} Projetos e Seus Guia-Agentes (`AGENTS.md`)\n",
            "Para obter instrucoes detalhadas de comandos de build, testes, estrutura de pastas e rotas especificas, **navegue ate o `AGENTS.md` do projeto correspondente**:\n",
            "| # | Projeto / Repositorio | Categoria | Porta(s) | AGENTS.md Local | Responsabilidade Resumida |",
            "|---|---|---|---|---|---|",
        ]

        for idx, p in enumerate(self.projects, start=1):
            ports_str = f"`{', '.join(p.ports)}`" if p.ports else "N/A"
            local_link = f"[`./{p.relative_path}/AGENTS.md`](./{p.relative_path}/AGENTS.md)"
            lines.append(
                f"| {idx} | `{p.name}` | {p.category} | {ports_str} | {local_link} | {p.description} |"
            )

        lines.extend([
            "\n---\n",
            "## 🛠️ 4. Diretrizes de Invocacao de Agentes",
            "1. **Ao trabalhar em um modulo especifico:** Leia o arquivo `AGENTS.md` localizado na raiz daquele subprojeto para entender a porta local, a stack tecnologica e os comandos recomendados.",
            "2. **Ao trabalhar em funcionalidades integradas:** Verifique os contratos de DTOs e rotas expostas no API Gateway / Service Discovery.",
            "3. **Regra de Ouro de Execucao:** Sempre prefira modificar arquivos de codigo mantendo os testes unitarios passando (`build_cmd` e `test_cmd`).\n",
            "---",
            "",
        ])

        content = "\n".join(lines)
        return append_ignore_section(content, number=5)

    def generate_local_agents(self, project: DetectedProject) -> str:
        """Gera o AGENTS.md Local para um subprojeto especifico."""
        ports_str = ", ".join(project.ports) if project.ports else "N/A"
        frontmatter = f"""---
sistema: {self.system_name}
modulo: {project.name}
categoria: {project.category.lower().replace(' ', '_')}
topico_principal: Guia do Agente de IA para {project.name}
publico_alvo: Assistentes de IA, Desenvolvedores
---"""

        content = f"""{frontmatter}

# AGENTS.md — {project.name}

Este arquivo estabelece o contexto de execucao, convencoes de arquitetura, limites de responsabilidade e regras operacionais para assistentes de IA atuando no repositorio **`{project.name}`**.

---

## 1. Visao Geral e Fronteiras do Servico
* **Funcao Principal:** {project.description}
* **Stack Tecnologica:** {project.tech_stack}
* **Manifesto de Dependencias:** `{project.manifest_file}`
* **Porta(s) de Execucao Local:** `{ports_str}`

---

## 2. Comandos Operacionais e Execucao
* **Compilacao / Build:** `{project.build_cmd}`
* **Execucao de Testes:** `{project.test_cmd}`
* **Execucao Local:** `{project.run_cmd}`

---

## 3. Diretrizes Arquiteturais & Boas Praticas
1. **Preservacao de Padroes:** Siga o padrao arquitetural estabelecido nas pastas do projeto.
2. **Seguranca de Codigo:** NUNCA insira dados de acesso ou chaves de API hardcodadas neste servico. Utilize injecao via variaveis de ambiente.
3. **Mantenha os Testes Verdes:** Antes de finalizar uma tarefa, garanta que a suite de testes (`{project.test_cmd}`) execute sem falhas.

"""
        return append_ignore_section(content, number=4)


# ==============================================================================
# FLUXO PRINCIPAL
# ==============================================================================
def main() -> int:
    parser = argparse.ArgumentParser(description="Gerador Agnostico de AGENTS.md para Monorepos")
    parser.add_argument(
        "--raiz",
        type=Path,
        default=Path.cwd(),
        help="Diretorio raiz do monorepo (padrao: diretorio atual)",
    )
    parser.add_argument(
        "--nome-sistema",
        type=str,
        default="Monorepo",
        help="Nome do ecossistema/sistema principal (padrao: Monorepo)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula a execucao sem escrever arquivos em disco",
    )

    args = parser.parse_args()
    root_path = args.raiz.resolve()

    if not root_path.is_dir():
        logger.error("Diretorio raiz invalido: %s", root_path)
        return 1

    logger.info("Iniciando varredura agnostica em: %s", root_path)
    logger.info("Nome do Sistema: %s", args.nome_sistema)

    detected_projects: list[DetectedProject] = []
    for item in sorted(root_path.iterdir(), key=lambda p: p.name.lower()):
        if item.is_dir():
            project = ProjectDetector.inspect_directory(item, root_path)
            if project:
                detected_projects.append(project)
                logger.info(
                    "  [+] Detectado: %s (%s | %s | Portas: %s)",
                    project.name,
                    project.category,
                    project.tech_stack,
                    ", ".join(project.ports) if project.ports else "N/A",
                )

    if not detected_projects:
        logger.warning("Nenhum subprojeto com manifesto reconhecido foi encontrado em %s.", root_path)
        return 0

    generator = AgentsGenerator(args.nome_sistema, root_path, detected_projects)

    global_content = generator.generate_global_agents()
    global_path = root_path / "AGENTS.md"

    if args.dry_run:
        logger.info("[DRY-RUN] Geraria AGENTS.md Mestre na raiz (%s)", global_path)
    else:
        global_path.write_text(global_content, encoding="utf-8")
        logger.info("AGENTS.md Mestre Global salvo em: %s", global_path)

    for p in detected_projects:
        local_content = generator.generate_local_agents(p)
        local_path = p.path / "AGENTS.md"
        if args.dry_run:
            logger.info("[DRY-RUN] Geraria AGENTS.md Local em %s", local_path)
        else:
            local_path.write_text(local_content, encoding="utf-8")
            logger.info("AGENTS.md Local salvo em: %s", local_path)

    logger.info("Concluido! %d subprojetos mapeados com sucesso.", len(detected_projects))
    return 0


if __name__ == "__main__":
    sys.exit(main())
