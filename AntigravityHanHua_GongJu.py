import os
import json
import hashlib
import shutil
import sys
import base64
import argparse

# ★★★ 用户配置区域 ★★★
ANTIGRAVITY_AN_ZHUANG_LU_JING = r"D:\Antigravity"

# 统一目标路径
TARGET_FILES = [
    r"resources\app\out\vs\code\electron-browser\workbench\workbench-jetski-agent.html",
    r"resources\app\out\vs\code\electron-browser\workbench\workbench.html"
]

PRODUCT_JSON_PATH = os.path.join(ANTIGRAVITY_AN_ZHUANG_LU_JING, r"resources\app\product.json")
HAN_HUA_JS_PATH = os.path.join(ANTIGRAVITY_AN_ZHUANG_LU_JING, r"resources\app\out\ag_agent_hanhua.js")

def normalize_text(text):
    import re
    if not text: return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return text

def load_dictionary():
    total_map = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dicts_dir = os.path.join(script_dir, 'dicts')
    if os.path.exists(dicts_dir):
        for filename in os.listdir(dicts_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(dicts_dir, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for k, v in data.items():
                            norm_k = normalize_text(k)
                            if norm_k: total_map[norm_k] = v
                except Exception: pass
    return total_map

def generate_js():
    """生成汉化注入脚本 V11.0 —— 强力扫描版（修复路径错误 + 支持多轮扫描）"""
    full_dict = load_dictionary()
    long_entries = sorted(full_dict.items(), key=lambda x: len(x[0]), reverse=True)
    dict_json = json.dumps(full_dict, ensure_ascii=False, indent=4)
    entries_json = json.dumps(long_entries, ensure_ascii=False)

    js_source = """\
(() => {
    // V12.0 终极隔离版：基于容器回溯的物理隔离引擎
    // 逻辑：不再仅仅检查当前标签，而是向上回溯父级，识别“代码/编辑器”禁区
    const map = new Map(Object.entries(DICT_PLACEHOLDER));
    const lowerMap = new Map();
    for (const [k, v] of map.entries()) lowerMap.set(k.toLowerCase(), v);
    
    const longEntries = REPLACEMENT_ENTRIES_PLACEHOLDER;
    const done = new WeakSet();

    // 禁区类名/属性特征
    const BLOCKED_CLASSES = ['monaco-editor', 'editor-container', 'terminal', 'output-view', 'debug-console', 'code-view', 'artifact-container', 'suggest-widget'];
    const BLOCKED_TAGS = ['SCRIPT', 'STYLE', 'CODE', 'PRE', 'INPUT', 'TEXTAREA', 'SVG', 'CANVAS', 'SYMBOL', 'PATH'];

    function norm(s) {
        if (!s) return '';
        return s.replace(/\\s+/g, ' ').replace(/[‘’]/g, "'").replace(/[“”]/g, '"').trim();
    }

    // 核心隔离判断：回溯检查当前节点是否逻辑上属于“禁止汉化区”
    function isInBlockedZone(node) {
        let curr = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;
        let depth = 0;
        while (curr && depth < 12) { // 向上回溯 12 层
            if (curr.nodeType === Node.ELEMENT_NODE) {
                const tag = curr.tagName.toUpperCase();
                if (BLOCKED_TAGS.includes(tag)) return true;
                if (curr.getAttribute('contenteditable') === 'true') return true;
                
                const className = curr.className || '';
                if (typeof className === 'string') {
                    if (BLOCKED_CLASSES.some(cls => className.includes(cls))) return true;
                }
            }
            curr = curr.parentElement || (curr.parentNode && curr.parentNode.host); // 支持 Shadow DOM 穿透
            depth++;
        }
        return false;
    }

    function translateNode(node) {
        try {
            if (!node || done.has(node)) return;
            
            if (node.nodeType === Node.ELEMENT_NODE) {
                const tag = node.tagName.toUpperCase();
                // 1. 快速排除基础禁止标签
                if (BLOCKED_TAGS.includes(tag)) return;
                
                // 2. 只有当确实不在禁区时，才翻译其属性
                if (!isInBlockedZone(node)) {
                    for (const attr of ['placeholder', 'title', 'aria-label']) {
                        const v = node.getAttribute(attr);
                        if (v) {
                            const t = norm(v);
                            if (map.has(t)) node.setAttribute(attr, map.get(t));
                            else if (lowerMap.has(t.toLowerCase())) node.setAttribute(attr, lowerMap.get(t.toLowerCase()));
                        }
                    }
                }

                if (node.shadowRoot) translateNode(node.shadowRoot);
                for (const child of node.childNodes) translateNode(child);

            } else if (node.nodeType === Node.TEXT_NODE) {
                let originalVal = node.nodeValue;
                if (!originalVal || originalVal.trim().length < 1) return;

                // 核心：在处理文本节点前，必须确认其不在“禁止区”
                if (isInBlockedZone(node)) return;

                let newVal = originalVal;
                const valNorm = norm(originalVal);
                const valLower = valNorm.toLowerCase();
                
                // 1. 精确匹配（含大小写自动纠正）
                if (map.has(valNorm)) {
                    newVal = map.get(valNorm);
                } else if (lowerMap.has(valLower)) {
                    // 短词保护：如果是长度小于 4 的词，且不带明确 UI 容器标识，慎重匹配
                    // 这里由于有了 isInBlockedZone，已经过滤了大部分干扰
                    newVal = lowerMap.get(valLower);
                } else {
                    // 2. 长句子串滑动替换
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
    setTimeout(() => { if(document.body) translateNode(document.body); }, 1500);
    setTimeout(() => { if(document.body) translateNode(document.body); }, 4000);
})();
"""
    final_js = js_source.replace("DICT_PLACEHOLDER", dict_json).replace("REPLACEMENT_ENTRIES_PLACEHOLDER", entries_json)
    with open(HAN_HUA_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(final_js)

def inject_html(html_rel_path):
    abs_path = os.path.join(ANTIGRAVITY_AN_ZHUANG_LU_JING, html_rel_path)
    if not os.path.exists(abs_path): return False
    
    with open(abs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 彻底修正为 4 层相对路径
    inject_str = '<script src="../../../../ag_agent_hanhua.js"></script>'
    
    # 清理旧的（错误的）注入
    import re
    content = re.sub(r'<script.*ag_agent_hanhua\.js.*</script>', '', content)
    
    if '</body>' in content:
        content = content.replace('</body>', f'{inject_str}</body>')
    else:
        content += inject_str
        
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def update_checksums():
    with open(PRODUCT_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for rel_path in TARGET_FILES:
        abs_path = os.path.join(ANTIGRAVITY_AN_ZHUANG_LU_JING, rel_path)
        if os.path.exists(abs_path):
            key = rel_path.replace("\\", "/").replace("resources/app/out/", "")
            sha256_hash = hashlib.sha256()
            with open(abs_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            data['checksums'][key] = base64.b64encode(sha256_hash.digest()).decode('utf-8').rstrip('=')
    
    with open(PRODUCT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent='\t')

def backup_files():
    for rel_path in TARGET_FILES:
        abs_path = os.path.join(ANTIGRAVITY_AN_ZHUANG_LU_JING, rel_path)
        bak_path = abs_path + ".bak"
        if os.path.exists(abs_path) and not os.path.exists(bak_path):
            shutil.copy2(abs_path, bak_path)
            print(f"[备份] 已创建原始内容备份: {os.path.basename(abs_path)}.bak")

def restore_files():
    print("====== 正在恢复 Antigravity 官方原版 ======")
    changed = False
    for rel_path in TARGET_FILES:
        abs_path = os.path.join(ANTIGRAVITY_AN_ZHUANG_LU_JING, rel_path)
        bak_path = abs_path + ".bak"
        if os.path.exists(bak_path):
            shutil.copy2(bak_path, abs_path)
            print(f"[还原] 已恢复: {os.path.basename(abs_path)}")
            changed = True
    
    if os.path.exists(HAN_HUA_JS_PATH):
        os.remove(HAN_HUA_JS_PATH)
        print(f"[还原] 已删除汉化核心脚本")
        changed = True
        
    if changed:
        update_checksums()
        print("[√] 校验值已同步，软件恢复至官方原始状态。")
    else:
        print("[!] 未找到备份文件，可能尚未安装过汉化。")

def main():
    parser = argparse.ArgumentParser(description="Antigravity 汉化工具")
    parser.add_argument("--huifu", action="store_true", help="恢复官方原版")
    args = parser.parse_args()

    if args.huifu:
        restore_files()
        return

    print("====== Antigravity 强力修复 V11.0 (Global Scan) ======")
    backup_files()
    generate_js()
    for html in TARGET_FILES:
        if inject_html(html):
            print(f"[√] 路径修正并注入: {os.path.basename(html)}")
    update_checksums()
    print("[√] 全局路径修复与深度引擎已部署")

if __name__ == "__main__":
    main()
