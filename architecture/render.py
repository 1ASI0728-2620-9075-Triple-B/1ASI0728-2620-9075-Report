#!/usr/bin/env python3
"""Renderiza los diagramas C4 definidos en workspace.dsl (Structurizr DSL) a PNG.

Flujo: Structurizr CLI exporta cada vista a C4-PlantUML y PlantUML la dibuja.
Uso (desde la raíz del repositorio):  python3 architecture/render.py
Requiere Java 17+. Si no se encuentran, descarga Structurizr CLI y PlantUML en architecture/.tools/.
Los mismos diagramas pueden verse y editarse en Structurizr Lite o en https://structurizr.com/dsl.
"""
import glob
import os
import re
import subprocess
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(HERE, '.tools')
BUILD = os.path.join(HERE, 'build')
OUT = os.path.join(ROOT, 'imgs', 'cap4')
CLI_URL = 'https://github.com/structurizr/cli/releases/download/v2025.11.09/structurizr-cli.zip'
PUML_URL = 'https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar'
EXTERNAL = ['FirebaseAuthentication', 'VertexAI', 'GoogleCalendarAPI', 'MercadoPago', 'SendGrid',
            'FirebaseCloudMessaging', 'GoogleAnalytics']
NAMES = {'Landscape': 'c4-system-landscape', 'Context': 'c4-context', 'Containers': 'c4-containers',
         'Containers-AIAgent': 'c4-containers-ai-agent', 'Deployment': 'c4-deployment'}


def tools():
    os.makedirs(TOOLS, exist_ok=True)
    cli = os.path.join(TOOLS, 'structurizr-cli', 'structurizr.sh')
    if not os.path.exists(cli):
        zpath = os.path.join(TOOLS, 'structurizr-cli.zip')
        urllib.request.urlretrieve(CLI_URL, zpath)
        zipfile.ZipFile(zpath).extractall(os.path.join(TOOLS, 'structurizr-cli'))
    jar = os.path.join(TOOLS, 'plantuml.jar')
    if not os.path.exists(jar):
        urllib.request.urlretrieve(PUML_URL, jar)
    return cli, jar


def main():
    cli, jar = tools()
    os.makedirs(BUILD, exist_ok=True)
    subprocess.run(['bash', cli, 'export', '-w', os.path.join(HERE, 'workspace.dsl'), '-f', 'plantuml/c4plantuml',
                    '-o', BUILD], check=True)
    os.makedirs(OUT, exist_ok=True)
    for src in glob.glob(os.path.join(BUILD, 'structurizr-*.puml')):
        view = os.path.basename(src)[len('structurizr-'):-len('.puml')]
        text = open(src, encoding='utf-8').read()
        for name in EXTERNAL:  # sistemas externos en gris (System_Ext)
            text = re.sub(r'\bSystem\(%s,' % name, 'System_Ext(%s,' % name, text)
        # Layout sin Graphviz y mayor resolución
        text = text.replace('@startuml', '@startuml\n!pragma layout smetana\nskinparam dpi 120', 1)
        dst = os.path.join(BUILD, NAMES.get(view, view) + '.puml')
        open(dst, 'w', encoding='utf-8').write(text)
        os.remove(src)
    subprocess.run(['java', '-DPLANTUML_LIMIT_SIZE=16384', '-jar', jar, '-tpng', '-charset', 'UTF-8', '-o', OUT] + glob.glob(os.path.join(BUILD, '*.puml')),
                   check=True)
    for png in sorted(glob.glob(os.path.join(OUT, 'c4-*.png'))):
        print('✓', os.path.relpath(png, ROOT))


if __name__ == '__main__':
    main()
