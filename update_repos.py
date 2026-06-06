import urllib.request
import json
import os

USERNAME = "gustavobarbosa-dev"
API_URL = f"https://api.github.com/users/{USERNAME}/repos?sort=created&direction=desc"

BADGE_COLORS = {
    "Python": "3776AB",
    "TypeScript": "007ACC",
    "JavaScript": "F7DF1E",
    "HTML": "E34F26",
    "CSS": "1572B6",
    "Java": "ED8B00"
}

def fetch_latest_repos():
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            repos = json.loads(response.read().decode())
        return [r for r in repos if not r['fork'] and r['name'] != USERNAME][:4]
    except Exception as e:
        print(f"ERROR: Falha de conexão com a API: {e}")
        return []

def generate_html_table(repos):
    if not repos:
        return "<p align='center' style='color: #FF0000;'>[FALHA_NO_LINK_DE_DADOS]</p>"

    html = '<table align="center" style="width: 100%; text-align: left; border: 1px solid #00FF00;">\n'
    html += '  <tr style="color: #00FF00; background-color: #002200;">\n'
    html += '    <th>OP_CODE</th>\n    <th>DESIGNATION</th>\n    <th>CORE_TECH</th>\n    <th>MISSION_BRIEFING</th>\n  </tr>\n'

    for i, repo in enumerate(repos):
        op_code = f"OP_0{i+1}"
        name = repo['name']
        url = repo['html_url']
        desc = repo['description'] or "Missão confidencial. Sem briefing cadastrado no banco de dados do GitHub."
        lang = repo['language'] or "N/A"
        
        color = BADGE_COLORS.get(lang, "555555")
        logo_color = "black" if lang == "JavaScript" else "white"
        
        if lang != "N/A":
            badge = f'<img src="https://img.shields.io/badge/-{lang}-{color}?style=flat-square&logo={lang.lower()}&logoColor={logo_color}"/>'
        else:
            badge = '<img src="https://img.shields.io/badge/-Classified-333333?style=flat-square"/>'

        html += f'''  <tr>
    <td><b>{op_code}</b></td>
    <td><a href="{url}" style="color: #ffffff;">{name}</a></td>
    <td>{badge}</td>
    <td>{desc}</td>
  </tr>\n'''

    html += '</table>'
    return html

def update_readme(html_content):
    filename = 'README.md'
    if not os.path.exists(filename):
        print(f"CRITICAL ERROR: {filename} não localizado.")
        return

    with open(filename, 'r', encoding='utf-8') as file:
        readme = file.read()
      
    start_marker = ""
    end_marker = ""

    start_idx = readme.find(start_marker)
    end_idx = readme.find(end_marker)

    if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
        print("CRITICAL ERROR: Marcadores ausentes no README.md.")
        return

    before_section = readme[:start_idx + len(start_marker)]
    after_section = readme[end_idx:]

    new_readme = before_section + "\n" + html_content + "\n" + after_section

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(new_readme)
        
    print("SYS_LOG: README.md atualizado com sucesso.")

if __name__ == "__main__":
    print("STATUS: Iniciando extração de dados...")
    repos = fetch_latest_repos()
    html_table = generate_html_table(repos)
    update_readme(html_table)
    print("STATUS: Operação finalizada.")
