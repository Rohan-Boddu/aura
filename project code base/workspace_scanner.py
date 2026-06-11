import os
import ast
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Set, Optional

@dataclass
class ClassInfo:
    name: str
    bases: List[str]
    methods: List[str]
    line_number: int

@dataclass
class FunctionInfo:
    name: str
    args: List[str]
    line_number: int

@dataclass
class EndpointInfo:
    path: str
    method: str
    handler_name: str
    line_number: int

@dataclass
class ModelInfo:
    name: str
    fields: List[str]
    line_number: int

@dataclass
class FileKnowledge:
    file_path: str
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    endpoints: List[EndpointInfo] = field(default_factory=list)
    models: List[ModelInfo] = field(default_factory=list)

@dataclass
class ProjectScanResult:
    project_path: str
    project_type: str
    entry_points: List[str]
    dependencies: List[str]
    database_files: List[str]
    file_inventory: List[Dict[str, Any]]
    routes: List[Dict[str, str]]
    knowledge: Dict[str, Any]

class WorkspaceScanner:
    """Scans projects read-only to extract structural knowledge and API routes."""

    def __init__(self, workspace_path: str):
        self.workspace_path = os.path.abspath(workspace_path)
        self.ignored_dirs = {
            ".git", ".venv", "venv", "env", "node_modules", 
            "build", "dist", "__pycache__", ".idea", ".vscode",
            ".pytest_cache"
        }

    def _should_ignore(self, path: str) -> bool:
        parts = Path(path).parts
        return any(ignored in parts for ignored in self.ignored_dirs)

    def scan(self) -> ProjectScanResult:
        file_inventory = []
        dependencies = set()
        database_files = []
        knowledge = {}
        routes = []

        for root, dirs, files in os.walk(self.workspace_path):
            # Prune directories in-place
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]

            if self._should_ignore(root):
                continue

            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.workspace_path).replace("\\", "/")
                
                try:
                    size = os.path.getsize(full_path)
                except OSError:
                    size = 0
                
                file_inventory.append({
                    "path": rel_path,
                    "size": size,
                    "extension": os.path.splitext(file)[1]
                })

                if file == "requirements.txt":
                    dependencies.update(self._parse_requirements(full_path))
                elif file == "package.json":
                    dependencies.update(self._parse_package_json(full_path))

                if file.endswith((".db", ".sqlite", ".sqlite3")):
                    database_files.append(rel_path)

                if file.endswith(".py"):
                    file_know = self._parse_python_file(full_path, rel_path)
                    if file_know:
                        knowledge[rel_path] = {
                            "classes": [asdict(c) for c in file_know.classes],
                            "functions": [asdict(f) for f in file_know.functions],
                            "endpoints": [asdict(e) for e in file_know.endpoints],
                            "models": [asdict(m) for m in file_know.models],
                        }
                        for e in file_know.endpoints:
                            routes.append({
                                "path": e.path,
                                "method": e.method,
                                "handler": f"{rel_path}:{e.handler_name}"
                            })

        project_type = self._detect_project_type(file_inventory, dependencies, knowledge)
        entry_points = self._detect_entry_points(file_inventory)

        # Factual Project Layout summary based on actual scan
        py_count = sum(1 for f in file_inventory if f["extension"] == ".py")
        js_count = sum(1 for f in file_inventory if f["extension"] in (".js", ".jsx", ".ts", ".tsx"))
        total = len(file_inventory)
        layout_desc = f"{project_type}"
        if total > 0:
            layout_desc += f" ({total} files"
            if py_count or js_count:
                layout_desc += f": {py_count} py, {js_count} js"
            layout_desc += ")"

        return ProjectScanResult(
            project_path=self.workspace_path,
            project_type=layout_desc,  # Used as Project Layout in UI - now more descriptive and factual
            entry_points=entry_points,
            dependencies=sorted(list(dependencies)),
            database_files=database_files,
            file_inventory=file_inventory,
            routes=routes,
            knowledge=knowledge
        )

    def _parse_requirements(self, file_path: str) -> List[str]:
        deps = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith(("#", "-r")):
                        dep = line.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
                        if dep:
                            deps.append(dep.lower())
        except Exception:
            pass
        return deps

    def _parse_package_json(self, file_path: str) -> List[str]:
        deps = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                all_deps = {
                    **data.get("dependencies", {}),
                    **data.get("devDependencies", {})
                }
                deps.extend(all_deps.keys())
        except Exception:
            pass
        return deps

    def _detect_project_type(self, file_inventory: List[Dict], deps: Set[str], knowledge: Dict) -> str:
        dep_str = " ".join(deps)
        if "fastapi" in dep_str:
            return "FastAPI"
        if "flask" in dep_str:
            return "Flask"
        if "react" in dep_str:
            return "React"
        if "vue" in dep_str:
            return "Vue"
        if "django" in dep_str:
            return "Django"

        has_py = False
        has_js = False

        for f in file_inventory:
            ext = f["extension"]
            if ext == ".py":
                has_py = True
            elif ext in (".js", ".jsx", ".ts", ".tsx"):
                has_js = True

        if has_py:
            return "Python"
        if has_js:
            return "JavaScript"
        
        return "Unknown"

    def _detect_entry_points(self, file_inventory: List[Dict]) -> List[str]:
        entry_candidates = {
            "main.py", "app.py", "wsgi.py", "run.py", "server.py", "asgi.py",
            "index.js", "server.js", "app.js", "main.js",
            "index.tsx", "index.jsx", "main.tsx"
        }
        entry_points = []
        for f in file_inventory:
            name = os.path.basename(f["path"])
            if name in entry_candidates:
                entry_points.append(f["path"])
        return entry_points

    def _parse_python_file(self, full_path: str, rel_path: str) -> Optional[FileKnowledge]:
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
            tree = ast.parse(code, filename=full_path)
        except Exception:
            return None

        classes: List[ClassInfo] = []
        functions: List[FunctionInfo] = []
        endpoints: List[EndpointInfo] = []
        models: List[ModelInfo] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(base.attr)
                
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                classes.append(ClassInfo(
                    name=node.name,
                    bases=bases,
                    methods=methods,
                    line_number=node.lineno
                ))

                if self._is_db_model(node):
                    fields = self._extract_model_fields(node)
                    models.append(ModelInfo(
                        name=node.name,
                        fields=fields,
                        line_number=node.lineno
                    ))

            elif isinstance(node, ast.FunctionDef):
                is_method = False
                args = [arg.arg for arg in node.args.args]
                if args and args[0] in ("self", "cls"):
                    is_method = True
                
                is_endpoint = False
                for decorator in node.decorator_list:
                    endpoint = self._extract_endpoint_from_decorator(decorator, node.name, node.lineno)
                    if endpoint:
                        endpoints.append(endpoint)
                        is_endpoint = True
                
                if not is_method and not is_endpoint:
                    functions.append(FunctionInfo(
                        name=node.name,
                        args=args,
                        line_number=node.lineno
                    ))

        return FileKnowledge(
            file_path=rel_path,
            classes=classes,
            functions=functions,
            endpoints=endpoints,
            models=models
        )

    def _is_db_model(self, node: ast.ClassDef) -> bool:
        for base in node.bases:
            name = ""
            if isinstance(base, ast.Name):
                name = base.id
            elif isinstance(base, ast.Attribute):
                name = self._get_func_name(base)
            
            if name in ["Base", "Model", "SQLModel", "models.Model", "declarative_base"]:
                return True
            if name.endswith(".Model") or name.endswith(".SQLModel") or name.endswith(".Base"):
                return True
        
        for item in node.body:
            if isinstance(item, ast.Assign):
                if isinstance(item.value, ast.Call):
                    func_name = self._get_func_name(item.value.func)
                    if any(kw in func_name for kw in ["Column", "Field", "ForeignKey", "relationship"]):
                        return True
        return False

    def _extract_model_fields(self, node: ast.ClassDef) -> List[str]:
        fields = []
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        fields.append(target.id)
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    fields.append(item.target.id)
        return fields

    def _extract_endpoint_from_decorator(self, decorator: ast.AST, handler_name: str, lineno: int) -> Optional[EndpointInfo]:
        if isinstance(decorator, ast.Call):
            decorator_name = self._get_func_name(decorator.func)
            
            if any(kw in decorator_name for kw in ["route", "get", "post", "put", "delete", "patch"]):
                path = "/"
                if decorator.args:
                    first_arg = decorator.args[0]
                    if isinstance(first_arg, ast.Constant):
                        path = str(first_arg.value)
                    elif isinstance(first_arg, ast.Str):
                        path = first_arg.s

                method = "GET"
                decorator_lower = decorator_name.lower()
                if "post" in decorator_lower:
                    method = "POST"
                elif "put" in decorator_lower:
                    method = "PUT"
                elif "delete" in decorator_lower:
                    method = "DELETE"
                elif "patch" in decorator_lower:
                    method = "PATCH"
                elif "route" in decorator_lower:
                    for kw in decorator.keywords:
                        if kw.arg == "methods":
                            if isinstance(kw.value, ast.List):
                                methods = []
                                for el in kw.value.elts:
                                    if isinstance(el, ast.Constant):
                                        methods.append(str(el.value).upper())
                                    elif isinstance(el, ast.Str):
                                        methods.append(el.s.upper())
                                if methods:
                                    method = ",".join(methods)
                
                return EndpointInfo(
                    path=path,
                    method=method,
                    handler_name=handler_name,
                    line_number=lineno
                )
        return None

    def _get_func_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_func_name(node.value)}.{node.attr}"
        return ""
