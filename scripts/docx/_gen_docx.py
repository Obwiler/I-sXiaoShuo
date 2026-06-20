import os, subprocess, glob, sys

def _check_pandoc():
    try:
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print('ERROR: pandoc 未安装。')
        print('  下载: https://pandoc.org/installing.html')
        print('  winget install pandoc | brew install pandoc | apt install pandoc')
        sys.exit(1)
_check_pandoc()

PROJECT = os.environ.get("WEBNOVEL_PROJECT") or os.getcwd()
MD_DIR = os.path.join(PROJECT, '设定', 'md')
OUT_DIR = os.path.join(PROJECT, '设定', 'docx_output')
TEMPLATE = os.path.join(PROJECT, '设定', 'template.docx')
FILTERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'table_filter.lua')

os.makedirs(OUT_DIR, exist_ok=True)

md_files = {
    '00_设定总纲.md': '00_设定总纲.docx',
    '00_人物档案总册.md': '00_人物档案总册.docx',
    '02_大纲章纲.md': '02_大纲章纲.docx',
    '03_伏笔追踪.md': '03_伏笔追踪.docx',
    '04_世界观与势力.md': '04_世界观与势力.docx',
    '第1卷_时间线.md': '第1卷_时间线.docx',
}

for md_file, docx_file in md_files.items():
    src = os.path.join(MD_DIR, md_file)
    dst = os.path.join(OUT_DIR, docx_file)
    
    if not os.path.exists(src):
        print(f'  SKIP {md_file}: source not found')
        continue
    
    cmd = ['pandoc', src, '--from', 'markdown', '--reference-doc=' + TEMPLATE,
           '--lua-filter=' + FILTERS, '-o', dst]
    
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        size = os.path.getsize(dst)
        print(f'  OK  {docx_file} ({size} bytes)')
    else:
        print(f'  FAIL {docx_file}: {r.stderr[:100]}')

print(f'\\n全部完成。输出目录: {OUT_DIR}')
