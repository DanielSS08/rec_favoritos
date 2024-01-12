from flask import Flask, render_template, request, send_file
import json
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def processar_arquivo_bak(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)

        bookmark_bar = dados.get('roots', {}).get('bookmark_bar', {})
        favoritos = bookmark_bar.get('children', [])

        links = []
        for favorito in favoritos:
            try:
                nome = favorito.get('name', '')
                url = favorito.get('url', '')

                if nome and url:
                    links.append({'nome': nome, 'url': url})
            except Exception as e:
                print(f"Erro ao processar favorito: {e}")

        return links
    except Exception as e:
        return f"Erro ao processar arquivo .bak: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="Nenhum arquivo selecionado.")

        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="Nenhum arquivo selecionado.")

        if file:
            caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(caminho_arquivo)

            links = processar_arquivo_bak(caminho_arquivo)
            os.remove(caminho_arquivo)  # Remover o arquivo temporário

            html_content = ''
            for link in links:
                html_content += f'<a href="{link["url"]}">{link["nome"]}</a><br>'

            # Salvar o conteúdo HTML em um arquivo temporário
            temp_html_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.html')
            with open(temp_html_path, 'w', encoding='utf-8') as temp_html:
                temp_html.write(html_content)

            return send_file(temp_html_path, as_attachment=True, download_name='output.html')

    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    app.run(debug=True)
