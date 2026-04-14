import argparse
import base64
import json
import platform
import re
import shutil
import sys
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

WINDOWS_DEFAULT_INSTALL_DIR = Path(r"D:/Antigravity")
MACOS_DEFAULT_INSTALL_DIRS = (
    Path("/Applications/Antigravity.app"),
    Path("~/Applications/Antigravity.app").expanduser(),
)
APP_ROOT_SUFFIX = Path("Contents/Resources/app")
WORKBENCH_RELATIVE_PATHS = (
    Path("out/vs/code/electron-browser/workbench/workbench-jetski-agent.html"),
    Path("out/vs/code/electron-browser/workbench/workbench.html"),
)
INJECT_SCRIPT_TAG = '<script src="../../../../ag_agent_hanhua.js"></script>'


@dataclass(frozen=True)
class RuntimePaths:
    app_root: Path
    product_json_path: Path
    han_hua_js_path: Path
    target_files: tuple[Path, ...]


def normalize_text(text):
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return text


def load_dictionary():
    total_map = {}
    dicts_dir = Path(__file__).resolve().parent / "dicts"
    if dicts_dir.exists():
        for path in sorted(dicts_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            for key, value in data.items():
                normalized_key = normalize_text(key)
                if normalized_key:
                    total_map[normalized_key] = value
    return total_map


def is_valid_app_root(path):
    return (path / "product.json").exists() and (path / "out").exists()


def expand_candidate(candidate):
    candidate = Path(candidate).expanduser()
    candidate_str = str(candidate)
    candidate_options = [candidate]
    if candidate_str.endswith(".app"):
        candidate_options.append(candidate / APP_ROOT_SUFFIX)
    else:
        candidate_options.append(candidate / "resources" / "app")
    for option in candidate_options:
        if is_valid_app_root(option):
            return option
    return None


def format_missing_install_dir_error(tried_paths):
    tried = "\n".join(f"- {path}" for path in tried_paths)
    return (
        f"未找到 Antigravity 安装目录。\n"
        f"当前平台：{platform.system()}\n"
        f"已尝试路径：\n{tried}\n"
        "请使用 --install-dir 手动指定目录，例如：\n"
        'python3 "AntigravityHanHua_GongJu.py" --install-dir "/Applications/Antigravity.app/Contents/Resources/app"'
    )


def resolve_install_dir(install_dir=None):
    tried_paths = []
    if install_dir:
        tried_paths.append(Path(install_dir).expanduser())
        resolved = expand_candidate(install_dir)
        if resolved:
            return resolved
        raise FileNotFoundError(format_missing_install_dir_error(tried_paths))

    candidates = [WINDOWS_DEFAULT_INSTALL_DIR]
    if platform.system() == "Darwin":
        candidates = list(MACOS_DEFAULT_INSTALL_DIRS)

    for candidate in candidates:
        tried_paths.append(Path(candidate).expanduser())
        resolved = expand_candidate(candidate)
        if resolved:
            return resolved
    raise FileNotFoundError(format_missing_install_dir_error(tried_paths))


def build_runtime_paths(app_root):
    app_root = Path(app_root).expanduser()
    return RuntimePaths(
        app_root=app_root,
        product_json_path=app_root / "product.json",
        han_hua_js_path=app_root / "out" / "ag_agent_hanhua.js",
        target_files=tuple(app_root / relative_path for relative_path in WORKBENCH_RELATIVE_PATHS),
    )


def generate_js(paths):
    full_dict = load_dictionary()
    long_entries = sorted(full_dict.items(), key=lambda item: len(item[0]), reverse=True)
    dict_json = json.dumps(full_dict, ensure_ascii=False, indent=4)
    entries_json = json.dumps(long_entries, ensure_ascii=False)
    js_source = """\
(() => {
    const map = new Map(Object.entries(DICT_PLACEHOLDER));
    const lowerMap = new Map();
    for (const [k, v] of map.entries()) lowerMap.set(k.toLowerCase(), v);

    const longEntries = REPLACEMENT_ENTRIES_PLACEHOLDER;
    const done = new WeakSet();

    function norm(s) {
        if (!s) return '';
        return s.replace(/\\s+/g, ' ').replace(/[‘’]/g, "'").replace(/[“”]/g, '"').trim();
    }

    function translateNode(node) {
        try {
            if (!node || done.has(node)) return;
            if (node.nodeType === Node.ELEMENT_NODE) {
                const tag = node.tagName.toUpperCase();
                if (['SCRIPT', 'STYLE', 'CODE', 'PRE', 'INPUT', 'TEXTAREA'].includes(tag)) return;

                for (const attr of ['placeholder', 'title', 'aria-label']) {
                    const v = node.getAttribute(attr);
                    if (v) {
                        const t = norm(v);
                        if (map.has(t)) node.setAttribute(attr, map.get(t));
                        else if (lowerMap.has(t.toLowerCase())) node.setAttribute(attr, lowerMap.get(t.toLowerCase()));
                    }
                }

                if (node.shadowRoot) translateNode(node.shadowRoot);
                for (const child of node.childNodes) translateNode(child);
            } else if (node.nodeType === Node.TEXT_NODE) {
                let originalVal = node.nodeValue;
                if (!originalVal || originalVal.trim().length < 1) return;

                let newVal = originalVal;
                const valNorm = norm(originalVal);
                const valLower = valNorm.toLowerCase();

                if (map.has(valNorm)) {
                    newVal = map.get(valNorm);
                } else if (lowerMap.has(valLower)) {
                    newVal = lowerMap.get(valLower);
                } else {
                    for (const [key, translated] of longEntries) {
                        if (key.length > 20 && valNorm.includes(key)) {
                            newVal = newVal.split(key).join(translated);
                        }
                    }
                }

                if (newVal !== originalVal) {
                    node.nodeValue = newVal;
                    done.add(node);
                    setTimeout(() => done.delete(node), 1000);
                }
            }
        } catch (e) {}
    }

    const observer = new MutationObserver(mutations => {
        for (const m of mutations) {
            if (m.type === 'childList') {
                for (const n of m.addedNodes) translateNode(n);
            } else if (m.type === 'characterData') {
                translateNode(m.target);
            }
        }
    });

    const obsOpts = { childList: true, subtree: true, characterData: true };

    const startEngine = () => {
        if (document.body) {
            observer.observe(document.body, obsOpts);
            translateNode(document.body);
        }
    };

    const origAttachShadow = Element.prototype.attachShadow;
    Element.prototype.attachShadow = function() {
        const sr = origAttachShadow.apply(this, arguments);
        try { observer.observe(sr, obsOpts); } catch(e) {}
        return sr;
    };

    setTimeout(startEngine, 300);
    setTimeout(() => { if (document.body) translateNode(document.body); }, 1500);
    setTimeout(() => { if (document.body) translateNode(document.body); }, 4000);
})();
"""
    final_js = js_source.replace("DICT_PLACEHOLDER", dict_json).replace("REPLACEMENT_ENTRIES_PLACEHOLDER", entries_json)
    paths.han_hua_js_path.parent.mkdir(parents=True, exist_ok=True)
    paths.han_hua_js_path.write_text(final_js, encoding="utf-8")


def inject_html(target_path):
    target_path = Path(target_path)
    if not target_path.exists():
        return False
    content = target_path.read_text(encoding="utf-8")
    content = re.sub(r'<script[^>]*ag_agent_hanhua\.js[^>]*></script>', "", content)
    if "</body>" in content:
        content = content.replace("</body>", f"{INJECT_SCRIPT_TAG}</body>")
    else:
        content = f"{content}{INJECT_SCRIPT_TAG}"
    target_path.write_text(content, encoding="utf-8")
    return True


def update_checksums(paths):
    data = json.loads(paths.product_json_path.read_text(encoding="utf-8"))
    checksums = data.setdefault("checksums", {})
    out_root = paths.app_root / "out"
    for target_path in paths.target_files:
        if not target_path.exists():
            continue
        key = target_path.relative_to(out_root).as_posix()
        checksums[key] = base64.b64encode(sha256(target_path.read_bytes()).digest()).decode("utf-8").rstrip("=")
    paths.product_json_path.write_text(json.dumps(data, indent="\t"), encoding="utf-8")


def backup_files(paths):
    for target_path in paths.target_files:
        backup_path = Path(f"{target_path}.bak")
        if target_path.exists() and not backup_path.exists():
            shutil.copy2(target_path, backup_path)
            print(f"[备份] 已创建原始内容备份: {target_path.name}.bak")


def restore_files(paths):
    print("====== 正在恢复 Antigravity 官方原版 ======")
    changed = False
    for target_path in paths.target_files:
        backup_path = Path(f"{target_path}.bak")
        if backup_path.exists():
            shutil.copy2(backup_path, target_path)
            print(f"[还原] 已恢复: {target_path.name}")
            changed = True
    if paths.han_hua_js_path.exists():
        paths.han_hua_js_path.unlink()
        print("[还原] 已删除汉化核心脚本")
        changed = True
    if changed:
        update_checksums(paths)
        print("[√] 校验值已同步，软件恢复至官方原始状态。")
    else:
        print("[!] 未找到备份文件，可能尚未安装过汉化。")


def run_install(paths):
    print("====== Antigravity 强力修复 V11.0 (Global Scan) ======")
    backup_files(paths)
    generate_js(paths)
    for target_path in paths.target_files:
        if inject_html(target_path):
            print(f"[√] 路径修正并注入: {target_path.name}")
    update_checksums(paths)
    print("[√] 全局路径修复与深度引擎已部署")


def build_parser():
    parser = argparse.ArgumentParser(description="Antigravity 汉化工具")
    parser.add_argument("--huifu", action="store_true", help="恢复官方原版")
    parser.add_argument(
        "--install-dir",
        help="Antigravity 安装目录，可传应用根目录或 resources/app 目录",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        app_root = resolve_install_dir(args.install_dir)
        paths = build_runtime_paths(app_root)
        if args.huifu:
            restore_files(paths)
        else:
            run_install(paths)
        return 0
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
