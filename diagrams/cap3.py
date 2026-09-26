"""Capítulo III: To-Be Scenario Maps e Impact Maps."""
import csv
import os

from lib import ROOT, Svg, box, esc, label, render

# ---------------------------------------------------------------- To-Be Scenario Mapping
DOING, THINKING, FEELING = '#8fb8f7', '#fde68a', '#bcd5fb'
AI_BADGE = ('<span style="position:absolute;right:-8px;top:-8px;background:#7048e8;color:#fff;border-radius:10px;'
            'font-size:11px;font-weight:700;padding:2px 6px">IA</span>')


def to_be(name, png, title, subtitle, phases):
    col, left, top, row_h = 210, 130, 110, 190
    w = left + col * len(phases) + 20
    h = top + 60 + row_h * 3 + 70
    body = [label(20, 18, w - 40, esc(title), size=26, weight=700),
            label(20, 58, w - 40, esc(subtitle), size=15, color='#555')]
    # cuadrícula
    body.append(box(left, top, col * len(phases), 60 + row_h * 3, '', bg='#fff',
                    style='border:1px solid #ddd'))
    for r, name_row in enumerate(['Phases', 'Doing', 'Thinking', 'Feeling']):
        y = top + (0 if r == 0 else 60 + (r - 1) * row_h)
        hh = 60 if r == 0 else row_h
        body.append(box(20, y, left - 20, hh, '<b>%s</b>' % name_row, bg='transparent', cls='sticky',
                        style='box-shadow:none;font-size:17px;justify-content:flex-start'))
        if r:
            body.append(box(left, y, col * len(phases), 1, '', bg='#ddd'))
    for c, ph in enumerate(phases):
        x = left + c * col
        if c:
            body.append(box(x, top, 1, 60 + row_h * 3, '', bg='#ddd'))
        body.append(box(x + 6, top + 6, col - 12, 48, '<b>%d. %s</b>' % (c + 1, esc(ph['phase'])), bg='transparent',
                        cls='sticky', style='box-shadow:none;font-size:14px'))
        for r, (key, color) in enumerate([('doing', DOING), ('thinking', THINKING), ('feeling', FEELING)]):
            y = top + 60 + r * row_h + 16
            badge = AI_BADGE if (key == 'doing' and ph.get('ai')) else ''
            body.append(box(x + 18, y, col - 36, row_h - 32, esc(ph[key]) + badge, bg=color, cls='sticky',
                            style='font-size:14px'))
    ly = top + 60 + row_h * 3 + 22
    body.append(label(left, ly, w - left, '<span style="background:#7048e8;color:#fff;border-radius:10px;font-size:11px;'
                      'font-weight:700;padding:2px 6px">IA</span>&nbsp; Paso en el que interviene el Agente IA de Triple B. '
                      'Filas: Doing (acciones), Thinking (pensamientos), Feeling (emociones).', size=14, color='#444'))
    render(name, w, h, ''.join(body), png, title)


TO_BE_STUDENT = [
    dict(phase='Perfil verificado', doing='Crea su perfil, verifica su correo universitario y sube su CV maestro y portafolio',
         thinking='“Ahora los clientes sabrán que de verdad soy estudiante”', feeling='Confiado: su perfil tiene respaldo'),
    dict(phase='Configuración del Agente IA', ai=True,
         doing='Acepta el consentimiento y define autonomía (Asistido), umbral, límite diario y categorías',
         thinking='“Yo decido qué puede hacer el agente y hasta dónde”', feeling='Cauteloso, pero en control'),
    dict(phase='Oportunidades recomendadas', ai=True,
         doing='Recibe en la app móvil ofertas compatibles con su horario, con puntaje y razones del match',
         thinking='“Ya no tengo que revisar grupos de WhatsApp o Facebook”', feeling='Aliviado: ahorra horas de búsqueda'),
    dict(phase='Postulación con CV adaptado', ai=True,
         doing='Revisa las diferencias del CV adaptado y aprueba la postulación en un paso',
         thinking='“Resalta lo que sí hice, sin inventar nada”', feeling='Seguro de lo que se envía'),
    dict(phase='Entrevista coordinada', ai=True,
         doing='Confirma una de las franjas propuestas; la invitación llega a su calendario',
         thinking='“No tuve que coordinar por chat durante días”', feeling='Motivado y organizado'),
    dict(phase='Acuerdo, entrega y cobro', doing='Acepta el encargo, entrega el trabajo y recibe el pago liberado desde la custodia',
         thinking='“El pago está garantizado y gano una reseña para mi perfil”', feeling='Tranquilo y orgulloso'),
]

TO_BE_EMPLOYER = [
    dict(phase='Publicación de la oferta', doing='Publica su requerimiento o puesto de practicante con habilidades, modalidad y presupuesto',
         thinking='“Lo publiqué en minutos, sin pedir recomendaciones en redes”', feeling='Esperanzada'),
    dict(phase='Recepción de postulaciones', ai=True,
         doing='Recibe postulaciones de estudiantes verificados, con CV adaptado y marcadas como asistidas por IA',
         thinking='“Son estudiantes reales y sé cuándo intervino la IA”', feeling='Confiada'),
    dict(phase='Preselección del Agente IA', ai=True,
         doing='Revisa los 5 candidatos más compatibles con sus razones y su portafolio',
         thinking='“Ya no leo CVs que no tienen nada que ver”', feeling='Aliviada: ahorra tiempo de revisión'),
    dict(phase='Entrevista coordinada', ai=True,
         doing='Solicita la entrevista; el agente propone franjas comunes y envía la invitación',
         thinking='“No tengo que perseguir al postulante por WhatsApp”', feeling='Eficiente'),
    dict(phase='Contratación y pago seguro', doing='Contrata y paga en custodia desde la plataforma',
         thinking='“Mi dinero está protegido hasta que reciba el trabajo”', feeling='Segura'),
    dict(phase='Entrega y reseña', doing='Recibe el entregable, lo aprueba (se libera el pago) y deja una reseña',
         thinking='“Volveré a contratar talento universitario”', feeling='Satisfecha'),
]

# ---------------------------------------------------------------- Impact Mapping
def stories():
    with open(os.path.join(ROOT, 'backlog', 'product-backlog.csv'), encoding='utf-8') as f:
        return {r['Issue Key']: r for r in csv.DictReader(f)}


def impact_map(name, png, title, persona, goals):
    us = stories()
    cols = dict(goal=(20, 230), persona=(295, 150), impact=(495, 215), deliv=(760, 215), story=(1025, 400))
    leaf_h, gap = 118, 14
    # altura por hoja (historia)
    y = 110
    nodes, edges = [], []
    for g in goals:
        g_top = y
        imp_nodes = []
        for imp, delivs in g['impacts']:
            i_top = y
            d_nodes = []
            for dtitle, sid in delivs:
                s = us[sid]
                nodes.append(('story', y, leaf_h, '<b>%s</b> — %s' % (sid, esc(s['Description']))))
                nodes.append(('deliv', y, leaf_h, esc(dtitle)))
                d_nodes.append(y + leaf_h / 2)
                edges.append(('deliv', 'story', y + leaf_h / 2, y + leaf_h / 2))
                y += leaf_h + gap
            mid = (i_top + y - gap) / 2
            nodes.append(('impact', mid - 45, 90, esc(imp)))
            for dy in d_nodes:
                edges.append(('impact', 'deliv', mid, dy))
            imp_nodes.append(mid)
        mid = (g_top + y - gap) / 2
        nodes.append(('persona', mid - 50, 100, '<b>%s</b><br><span class="small">%s</span>' % (esc(persona[0]), esc(persona[1]))))
        nodes.append(('goal', mid - 80, 160, '<b>%s</b><br>%s' % (esc(g['id']), esc(g['text']))))
        for iy in imp_nodes:
            edges.append(('persona', 'impact', mid, iy))
        edges.append(('goal', 'persona', mid, mid))
        y += 36
    h = y + 20
    w = cols['story'][0] + cols['story'][1] + 30
    svg = Svg(w, h)
    for a, b, y1, y2 in edges:
        x1 = cols[a][0] + cols[a][1]
        x2 = cols[b][0]
        svg.line([(x1, y1), (x2, y2)], color='#7048e8', width=2, arrow=False, curve=True)
    body = [label(20, 18, w - 40, esc(title), size=26, weight=700)]
    heads = [('goal', 'Business Goals'), ('persona', 'Actors / Personas'), ('impact', 'Impacts'),
             ('deliv', 'Deliverables'), ('story', 'User Stories')]
    for key, text in heads:
        body.append(label(cols[key][0], 66, cols[key][1], text, size=17, weight=700, align='center', color='#444'))
    body.append(svg.render())
    styles = dict(goal='background:#fff;border:2px solid #222;border-radius:14px;font-size:14px',
                  persona='background:#e5dbff;border:2px solid #7048e8;border-radius:50px;font-size:14px',
                  impact='background:#fff;font-size:14px', deliv='background:#fff;font-size:14px',
                  story='background:#f3f0ff;text-align:left;justify-content:flex-start;font-size:13px')
    for kind, ny, nh, text in nodes:
        x, ww = cols[kind]
        body.append(box(x, int(ny), ww, int(nh), text, cls='card', style=styles[kind]))
    render(name, w, h, ''.join(body), png, title)


GOALS_STUDENT = [
    dict(id='BG1', text='Lograr que 1 000 estudiantes universitarios de Lima Metropolitana activen el Agente IA en los primeros 6 meses desde el lanzamiento.',
         impacts=[('Confía en delegar la búsqueda al Agente IA', [('Mandato con consentimiento, autonomía y límites', 'US59'),
                                                                   ('Explicación de cada recomendación', 'US61')]),
                  ('Completa un perfil verificado con evidencias', [('Verificación con correo institucional', 'US63'),
                                                                    ('Portafolio de trabajos previos', 'US18')])]),
    dict(id='BG2', text='Reducir en 80% el tiempo semanal que un estudiante dedica a buscar y postular, respecto de la línea base medida en la validación, durante sus primeros 3 meses de uso.',
         impacts=[('Delega la búsqueda de oportunidades', [('Recomendaciones automáticas con match score', 'US51')]),
                  ('Aprueba postulaciones en lugar de redactarlas', [('CV adaptado solo con información verificada', 'US52'),
                                                                     ('Aprobación en un paso desde el móvil', 'US60'),
                                                                     ('Postulación autónoma bajo mandato', 'US53')])]),
    dict(id='BG3', text='Lograr que al menos el 30% de las postulaciones preparadas por el Agente IA se conviertan en entrevistas confirmadas al cierre del primer semestre de operación.',
         impacts=[('Confirma entrevistas sin coordinación manual', [('Propuesta automática de franjas', 'US55')]),
                  ('Da seguimiento a sus postulaciones', [('Panel de actividad del Agente IA', 'US56')])]),
]

GOALS_EMPLOYER = [
    dict(id='BG4', text='Lograr que 150 empleadores o emprendimientos de Lima Metropolitana publiquen al menos una oferta en los primeros 6 meses desde el lanzamiento.',
         impacts=[('Publica su necesidad en Triple B en lugar de redes sociales', [('Publicación guiada de ofertas y prácticas', 'US57'),
                                                                                  ('Llamado a la acción para empleadores', 'US65')])]),
    dict(id='BG5', text='Reducir a menos de 72 horas el tiempo promedio entre la publicación de una oferta y la primera entrevista agendada durante el primer semestre de operación.',
         impacts=[('Revisa solo candidatos compatibles', [('Preselección con razones y sin atributos personales', 'US54')]),
                  ('Agenda entrevistas sin intercambiar mensajes', [('Cruce automático de calendarios', 'US55')])]),
    dict(id='BG6', text='Alcanzar 300 servicios contratados, pagados en custodia y calificados en los primeros 8 meses de operación.',
         impacts=[('Contrata y paga dentro de la plataforma', [('Contratación directa desde el perfil', 'US30'),
                                                               ('Confirmación de la contratación', 'US31')]),
                  ('Decide con base en reputación verificable', [('Calificaciones visibles en el perfil', 'US39'),
                                                                 ('Reseña al finalizar el proyecto', 'US38')])]),
]


def build():
    to_be('to-be-estudiante', 'imgs/cap3/to-be-estudiante.png',
          'To-Be Scenario Map — Estudiante universitario freelancer',
          'User Persona: Julio Bernal · Flujo futuro con Triple B y el Agente IA (modo Asistido por defecto)', TO_BE_STUDENT)
    to_be('to-be-empleador', 'imgs/cap3/to-be-empleador.png',
          'To-Be Scenario Map — Empleador / emprendedor',
          'User Persona: Luisa Fuentes · Flujo futuro de publicación, preselección y contratación', TO_BE_EMPLOYER)
    impact_map('impact-map-estudiante', 'imgs/cap3/impact-map-estudiante.png',
               'Impact Map — Segmento Estudiantes Universitarios Freelancers',
               ('Julio Bernal', 'Estudiante freelancer'), GOALS_STUDENT)
    impact_map('impact-map-empleador', 'imgs/cap3/impact-map-empleador.png',
               'Impact Map — Segmento Empleadores, Microempresas y Emprendedores',
               ('Luisa Fuentes', 'Emprendedora'), GOALS_EMPLOYER)
