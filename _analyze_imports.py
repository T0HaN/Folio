# -*- coding: utf-8 -*-
"""
Статический анализатор импортов для проекта Folio.
"""
import ast
import builtins
import os
import collections
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(ROOT, "app")

BUILTINS = set(dir(builtins))
MAGIC = {"__file__", "__name__", "__doc__", "__package__", "__path__",
         "__spec__", "__loader__", "__builtins__", "__annotations__",
         "__qualname__", "__cached__"}

COMMON_TYPING = {"Optional", "List", "Dict", "Any", "Tuple", "Set", "Union",
                 "Callable", "Type", "Sequence", "Mapping", "Iterable",
                 "Literal", "Protocol", "TypeVar", "Final", "ClassVar", "NoReturn"}


def module_name_to_path(mod):
    parts = mod.split(".")
    base = ROOT
    for p in parts:
        base = os.path.join(base, p)
    if os.path.isfile(base + ".py"):
        return base + ".py"
    if os.path.isfile(os.path.join(base, "__init__.py")):
        return os.path.join(base, "__init__.py")
    if os.path.isdir(base):
        return base
    return None


def collect_module_defs(path):
    """Имена, определённые на уровне модуля."""
    names = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
    except SyntaxError as e:
        return names, {"syntax_error": str(e)}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name):
                    names.add(t.id)
                elif isinstance(t, (ast.Tuple, ast.List)):
                    for el in ast.walk(t):
                        if isinstance(el, ast.Name):
                            names.add(el.id)
        elif isinstance(node, ast.Import):
            for a in node.names:
                names.add(a.asname or a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                if a.name != "*":
                    names.add(a.asname or a.name)
    return names, {}


def collect_imports(path):
    imports = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
    except SyntaxError:
        return imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imports.append(("import", None, a.name, a.asname, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for a in node.names:
                imports.append(("from", mod, a.name, a.asname, node.lineno))
    return imports


def names_in_function(fn):
    """Все имена, связываемые внутри функции (включая вложенные def)."""
    bound = set()
    for a in fn.args.posonlyargs:
        bound.add(a.arg)
    for a in fn.args.args:
        bound.add(a.arg)
    for a in fn.args.kwonlyargs:
        bound.add(a.arg)
    if fn.args.vararg:
        bound.add(fn.args.vararg.arg)
    if fn.args.kwarg:
        bound.add(fn.args.kwarg.arg)
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                for el in ast.walk(t):
                    if isinstance(el, ast.Name):
                        bound.add(el.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            bound.add(node.target.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
        elif isinstance(node, ast.With):
            for item in node.items:
                if item.optional_vars:
                    for el in ast.walk(item.optional_vars):
                        if isinstance(el, ast.Name):
                            bound.add(el.id)
        elif isinstance(node, (ast.For, ast.AsyncFor)) and node.target:
            for el in ast.walk(node.target):
                if isinstance(el, ast.Name):
                    bound.add(el.id)
        elif isinstance(node, ast.comprehension):
            for el in ast.walk(node.target):
                if isinstance(el, ast.Name):
                    bound.add(el.id)
    return bound


def check_body(body, outer_bound, module_defs, label, undefined):
    """Рекурсивно обходит тело, находя неопределённые Load-имена."""
    local_bound = set()
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            local_bound.add(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                for el in ast.walk(t):
                    if isinstance(el, ast.Name):
                        local_bound.add(el.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            local_bound.add(node.target.id)
        elif isinstance(node, ast.Import):
            for a in node.names:
                local_bound.add(a.asname or a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                if a.name != "*":
                    local_bound.add(a.asname or a.name)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            for el in ast.walk(node.target):
                if isinstance(el, ast.Name):
                    local_bound.add(el.id)
        elif isinstance(node, ast.With):
            for item in node.items:
                if item.optional_vars:
                    for el in ast.walk(item.optional_vars):
                        if isinstance(el, ast.Name):
                            local_bound.add(el.id)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            local_bound.add(node.name)

    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            check_body(node.body, outer_bound | local_bound | names_in_function(node),
                       module_defs, label + f".{node.name}", undefined)
        elif isinstance(node, ast.ClassDef):
            class_bound = set()
            for n in node.body:
                if isinstance(n, ast.Assign):
                    for t in n.targets:
                        for el in ast.walk(t):
                            if isinstance(el, ast.Name):
                                class_bound.add(el.id)
            for n in node.body:
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    check_body(n.body, outer_bound | local_bound | class_bound | {node.name} | names_in_function(n),
                               module_defs, label + f".{node.name}", undefined)
        elif isinstance(node, (ast.Import, ast.ImportFrom,
                               ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        else:
            for child in ast.walk(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    continue
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                    nm = child.id
                    if nm in BUILTINS or nm in MAGIC or nm in COMMON_TYPING:
                        continue
                    if nm in module_defs or nm in outer_bound or nm in local_bound:
                        continue
                    undefined.append((nm, child.lineno, label))


def analyze_names(path):
    """Возвращает список потенциально неопределённых имён в файле."""
    undefined = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
    except SyntaxError as e:
        return [("SYNTAX", 0, f"файл не парсится: {e}")]
    module_defs, _ = collect_module_defs(path)
    check_body(tree.body, set(), module_defs, "module", undefined)
    seen = set()
    res = []
    for nm, ln, lbl in undefined:
        key = (nm, ln, lbl)
        if key not in seen:
            seen.add(key)
            res.append((nm, ln, lbl))
    return res



def resolve_local_import(importing_rel, module_name, imported_name):
    """Проверяет, что imported_name существует в локальном модуле module_name."""
    if not module_name.startswith("app"):
        return None
    p = module_name_to_path(module_name)
    if p is None:
        return f"модуль '{module_name}' не найден в проекте"
    if os.path.isdir(p):
        init = os.path.join(p, "__init__.py")
        if not os.path.isfile(init):
            return None
        defs, _ = collect_module_defs(init)
    else:
        defs, _ = collect_module_defs(p)
    if imported_name == "*":
        return None
    if imported_name not in defs:
        return f"в модуле '{module_name}' нет имени '{imported_name}'"
    return None


def check_attribute_use(path):
    """Проверяет обращения вида <локальный модуль>.<атрибут>."""
    problems = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
    except SyntaxError:
        return problems
    local_modules = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                name = a.asname or a.name.split(".")[0]
                if a.name.startswith("app") or a.name == "utils":
                    local_modules[name] = a.name
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for a in node.names:
                alias = a.asname or a.name
                if mod.startswith("app") and a.name in ("utils", "settings", "constants"):
                    local_modules[alias] = f"{mod}.{a.name}"
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            base = node.value.id
            if base in local_modules:
                mod = local_modules[base]
                target_path = module_name_to_path(mod)
                if target_path and os.path.isfile(target_path):
                    defs, _ = collect_module_defs(target_path)
                    if node.attr not in defs:
                        problems.append((node.lineno,
                                         f"{base}.{node.attr}: атрибут не найден в {mod}"))
    return problems


def build_import_graph():
    """Граф зависимостей для поиска циклических импортов."""
    graph = collections.defaultdict(set)
    for root, dirs, files in os.walk(APP):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, ROOT).replace("\\", ".")
            rel = rel[:-3]
            for imp in collect_imports(full):
                kind, mod, *_ = imp
                mod_name = mod if kind == "from" else (mod.split(".")[0] if mod else "")
                if not mod_name or not mod_name.startswith("app"):
                    continue
                p = module_name_to_path(mod_name)
                if not p:
                    continue
                target = os.path.relpath(p, ROOT).replace("\\", ".")
                if target.endswith("__init__"):
                    target = os.path.dirname(target) or target
                elif target.endswith(".py"):
                    target = target[:-3]
                target = target.rstrip(".")
                if target != rel:
                    graph[rel].add(target)
    cycles = []

    def dfs(node, path, seen):
        for nxt in sorted(graph.get(node, [])):
            if nxt in path:
                idx = path.index(nxt)
                cycles.append(path[idx:] + [nxt])
            elif nxt not in seen:
                dfs(nxt, path + [nxt], seen | {nxt})

    for node in sorted(graph):
        dfs(node, [node], {node})
    seen_cycles = set()
    uniq = []
    for cyc in cycles:
        key = tuple(sorted(cyc))
        if key not in seen_cycles:
            seen_cycles.add(key)
            uniq.append(cyc)
    return uniq


def main():
    _out = open("analysis_report.txt", "w", encoding="utf-8")
    sys.stdout = _out
    files = []
    for root, dirs, files_ in os.walk(APP):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in files_:
            if fn.endswith(".py"):
                files.append(os.path.join(root, fn))
    files.sort()

    print("=" * 80)
    print("1. НЕОПРЕДЕЛЁННЫЕ ИМЕНА (потенциальные NameError)")
    print("=" * 80)
    for f in files:
        rel = os.path.relpath(f, ROOT)
        issues = analyze_names(f)
        if issues:
            print(f"\n--- {rel} ---")
            for nm, ln, lbl in issues:
                print(f"  строка {ln}: {nm}  [{lbl}]")

    print()
    print("=" * 80)
    print("2. ИМПОРТЫ НЕСУЩЕСТВУЮЩИХ ИМЁН ИЗ ЛОКАЛЬНЫХ МОДУЛЕЙ")
    print("=" * 80)
    for f in files:
        rel = os.path.relpath(f, ROOT)
        for imp in collect_imports(f):
            kind, mod, name, asname, lineno = imp
            if kind == "from" and mod.startswith("app"):
                err = resolve_local_import(rel, mod, name)
                if err:
                    print(f"  {rel}:{lineno}: from {mod} import {name} -> {err}")

    print()
    print("=" * 80)
    print("3. АТРИБУТЫ ЛОКАЛЬНЫХ МОДУЛЕЙ (utils.xxx, settings.yyy)")
    print("=" * 80)
    for f in files:
        rel = os.path.relpath(f, ROOT)
        for ln, msg in check_attribute_use(f):
            print(f"  {rel}:{ln}: {msg}")

    print()
    print("=" * 80)
    print("4. ЦИКЛИЧЕСКИЕ ИМПОРТЫ")
    print("=" * 80)
    cycles = build_import_graph()
    if cycles:
        for cyc in cycles:
            print("  цикл: " + " -> ".join(cyc))
    else:
        print("  циклов не обнаружено")
    print()
    print("=" * 80)
    print("ГОТОВО")
    print("=" * 80)


if __name__ == "__main__":
    main()

