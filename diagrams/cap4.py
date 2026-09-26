"""Capítulo IV: EventStorming, Candidate Context Discovery, Domain Storytelling y Context Map."""
import re

from lib import ES, Svg, box, esc, label, render


def words(camel):
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', camel).replace('Cv', 'CV')


LEGEND = [('event', 'Domain Event'), ('command', 'Command'), ('actor', 'Actor'), ('policy', 'Policy'),
          ('aggregate', 'Aggregate'), ('readmodel', 'Read Model'), ('external', 'External System'),
          ('hotspot', 'Hotspot')]


def legend(x, y, items=LEGEND):
    out, cx = [], x
    for key, text in items:
        out.append(box(cx, y, 22, 22, '', bg=ES[key], cls='sticky', style='padding:0'))
        out.append(label(cx + 28, y + 1, 150, text, size=14, color='#333'))
        cx += 44 + int(len(text) * 8.6)
    return ''.join(out)


# ---------------------------------------------------------------- EventStorming: Big Picture
LANES = [
    dict(name='Registro y perfiles',
         events=['AccountRegistered', 'StudentProfileCreated', 'StudentVerified', 'MasterCvUpdated',
                 'PortfolioItemAdded', 'EmployerProfileCreated', 'EmployerVerified'],
         external={'AccountRegistered': 'Firebase Authentication'},
         hotspots={'StudentVerified': '¿Cómo verificamos a estudiantes sin correo institucional?'}),
    dict(name='Ofertas y Agente IA',
         events=['AgentMandateGranted', 'JobOfferPublished', 'OpportunityMatched', 'TailoredCvGenerated',
                 'ApplicationDraftPrepared', 'ApplicationDraftApproved', 'ApplicationSubmitted', 'ShortlistGenerated',
                 'InterviewRequested', 'InterviewSlotsProposed', 'InterviewScheduled', 'CandidateHired', 'JobOfferClosed'],
         alt={'AgentMandateGranted': 'AgentMandatePaused', 'TailoredCvGenerated': 'TailoredCvRejected',
              'ApplicationDraftApproved': 'ApplicationDraftDiscarded', 'ApplicationSubmitted': 'ApplicationWithdrawn',
              'InterviewSlotsProposed': 'InterviewSlotsDeclined', 'JobOfferClosed': 'AgentMandateRevoked'},
         hotspots={'TailoredCvGenerated': '¿Cómo evitamos que el CV adaptado invente habilidades?',
                   'ApplicationSubmitted': '¿Cuántas postulaciones autónomas por día?',
                   'ShortlistGenerated': '¿Cómo evitamos sesgos en la preselección?',
                   'InterviewSlotsProposed': '¿Y si el empleador no conecta su calendario?',
                   'CandidateHired': '¿Se cobra comisión en las prácticas?'}),
    dict(name='Servicios, contratación y reputación',
         events=['GigPublished', 'HireRequestSent', 'HireRequestAccepted', 'EngagementStarted', 'PaymentHeldInEscrow',
                 'DeliverySubmitted', 'DeliveryAccepted', 'EngagementCompleted', 'PaymentReleased', 'ReviewSubmitted',
                 'ReputationUpdated'],
         alt={'HireRequestAccepted': 'HireRequestDeclined', 'PaymentHeldInEscrow': 'PaymentFailed',
              'DeliveryAccepted': 'DeliveryRejected'},
         hotspots={'DeliveryAccepted': '¿Qué pasa si el cliente disputa la entrega?',
                   'PaymentHeldInEscrow': '¿Custodia con pasarela o con smart contract?'}),
    dict(name='Comunicación y soporte',
         events=['ConversationStarted', 'MessageSent', 'NotificationSent', 'UserReported', 'UserBlocked',
                 'SupportTicketOpened'],
         hotspots={'NotificationSent': '¿Qué acciones del agente notifican al instante?'}),
]

PIVOTAL = {'StudentVerified', 'AgentMandateGranted', 'JobOfferPublished', 'ApplicationSubmitted', 'CandidateHired',
           'EngagementStarted', 'PaymentReleased', 'ReviewSubmitted'}


def big_picture(name, png, title, subtitle, pivotal=False):
    per_row, ew, eh, gap, left = 7, 150, 88, 18, 200
    w = left + per_row * (ew + gap) + 20
    y, body, svg_items = 110, [], []
    lane_blocks = []
    for lane in LANES:
        evs = lane['events']
        chunks = [evs[i:i + per_row] for i in range(0, len(evs), per_row)]
        lane_top = y
        for chunk in chunks:
            has_hot = any(e in lane.get('hotspots', {}) for e in chunk)
            has_alt = any(e in lane.get('alt', {}) or e in lane.get('external', {}) for e in chunk)
            hot_h = 92 if has_hot else 0
            ey = y + hot_h
            svg_items.append(((left - 10, ey + eh / 2), (left + len(chunk) * (ew + gap), ey + eh / 2)))
            for i, ev in enumerate(chunk):
                x = left + i * (ew + gap)
                style = 'font-size:14px;font-weight:600'
                tag = ''
                if pivotal and ev in PIVOTAL:
                    style += ';outline:4px solid #c92a2a;outline-offset:3px'
                    tag = ('<span style="position:absolute;left:6px;top:-26px;background:#c92a2a;color:#fff;font-size:11px;'
                           'font-weight:700;padding:1px 6px;border-radius:4px">PIVOTAL</span>')
                body.append(box(x, int(ey), ew, eh, esc(words(ev)) + tag, bg=ES['event'], cls='sticky', style=style))
                if ev in lane.get('hotspots', {}) and not pivotal:
                    body.append(box(x + 8, int(y + 4), ew - 16, 78, esc(lane['hotspots'][ev]), bg=ES['hotspot'],
                                    cls='sticky', style='font-size:12.5px;color:#fff;transform:rotate(-2deg)'))
                if ev in lane.get('alt', {}):
                    body.append(box(x + 10, int(ey + eh + 14), ew - 20, 62, esc(words(lane['alt'][ev])), bg='#ffd8a8',
                                    cls='sticky', style='font-size:13px;border:2px dashed #e8590c'))
                if ev in lane.get('external', {}):
                    body.append(box(x + 10, int(ey + eh + 14), ew - 20, 62, esc(lane['external'][ev]), bg=ES['external'],
                                    cls='sticky', style='font-size:13px'))
            y = ey + eh + (90 if has_alt else 26)
        lane_blocks.append((lane['name'], lane_top, y))
        y += 22
    h = int(y + 70)
    svg = Svg(w, h)
    for (p1, p2) in svg_items:
        svg.line([p1, p2], color='#bbb', width=3)
    bgs = []
    for i, (lname, top, bottom) in enumerate(lane_blocks):
        bgs.append(box(12, int(top) - 8, w - 24, int(bottom - top) + 4, '', bg='#fff' if i % 2 == 0 else '#fbfaf7',
                           style='border:1px solid #e4e2dc;border-radius:8px'))
        body.append(label(26, int(top) + 12, left - 40, '<b>%s</b>' % esc(lname), size=16, color='#444'))
    head = [label(20, 18, w - 40, esc(title), size=26, weight=700), label(20, 58, w - 40, esc(subtitle), size=15, color='#555')]
    items = [('event', 'Domain Event'), ('hotspot', 'Hotspot'), ('external', 'External System')]
    extra = ('<div class="abs" style="left:%dpx;top:%dpx;width:22px;height:22px;background:#ffd8a8;border:2px dashed #e8590c">'
             '</div>' % (560, h - 50)) + label(588, h - 49, 260, 'Evento alternativo (unhappy path)', size=14, color='#333')
    if pivotal:
        items = [('event', 'Domain Event')]
        extra = ('<div class="abs" style="left:200px;top:%dpx;width:22px;height:22px;background:%s;outline:4px solid #c92a2a;'
                 'outline-offset:2px"></div>' % (h - 50, ES['event'])) + label(232, h - 49, 400, 'Pivotal event (cambio de etapa del negocio)', size=14)
    render(name, w, h, ''.join(head + bgs + [svg.render()] + body) + legend(20, h - 50, items) + extra, png, title, scale=1.4)


# ---------------------------------------------------------------- EventStorming: Process level
def process_level(name, png, title, subtitle, steps):
    per_row, cw, card, left = 6, 205, 170, 30
    w = left + per_row * cw + 20
    slots = [('top', 84), ('command', 64), ('aggregate', 48), ('event', 64), ('bottom', 56)]
    gap = 22
    row_h = sum(h for _, h in slots) + gap * (len(slots) - 1) + 60
    rows = (len(steps) + per_row - 1) // per_row
    h = 110 + rows * row_h + 60
    svg = Svg(w, h)
    body = [label(20, 18, w - 40, esc(title), size=26, weight=700), label(20, 58, w - 40, esc(subtitle), size=15, color='#555')]
    prev_event = None
    for n, st in enumerate(steps):
        r, c = divmod(n, per_row)
        x = left + c * cw
        y = 110 + r * row_h
        body.append(label(x, y - 2, card, '<b>Paso %d</b>' % (n + 1), size=13, color='#777', align='center'))
        y += 22
        centers = []
        for slot, sh in slots:
            kind, text = st.get(slot, (None, None)) if slot in ('top', 'bottom') else (slot, st.get(slot))
            if text:
                ww = card if kind != 'actor' else card - 50
                xx = x + (card - ww) // 2
                style = 'font-size:13.5px'
                if kind in ('event', 'command'):
                    style += ';font-weight:600'
                body.append(box(xx, y, ww, sh, esc(words(text) if kind in ('event', 'command') else text),
                                bg=ES[kind], cls='sticky', style=style))
                centers.append((x + card // 2, y, y + sh, kind))
            y += sh + gap
        for a, b in zip(centers, centers[1:]):
            if b[3] in ('external', 'readmodel'):
                svg.line([(a[0], a[2] + 2), (b[0], b[1] - 4)], color='#999', dashed=True)
            else:
                svg.line([(a[0], a[2] + 2), (b[0], b[1] - 4)])
        ev = [cc for cc in centers if cc[3] == 'event']
        if ev and prev_event and prev_event[0] < ev[0][0]:
            svg.line([(prev_event[0] + card // 2 + 2, (prev_event[1] + prev_event[2]) // 2),
                      (ev[0][0] - card // 2 - 4, (ev[0][1] + ev[0][2]) // 2)], color='#e8590c', width=2)
        prev_event = ev[0] if ev else prev_event
    render(name, w, h, ''.join(body) + svg.render() + legend(20, h - 44, LEGEND[:-1]), png, title, scale=1.4)


AGENT_FLOW = [
    dict(top=('actor', 'Estudiante'), command='GrantAgentMandate', aggregate='AgentMandate', event='AgentMandateGranted',
         bottom=('readmodel', 'Agent Activity Dashboard')),
    dict(top=('actor', 'Empleador'), command='PublishJobOffer', aggregate='JobOffer', event='JobOfferPublished'),
    dict(top=('policy', 'Cuando se publica una oferta, evaluar estudiantes con mandato activo'), command='MatchOpportunity',
         aggregate='MatchRecommendation', event='OpportunityMatched', bottom=('external', 'Vertex AI (embeddings)')),
    dict(top=('policy', 'Si el match score ≥ umbral, preparar la postulación'), command='GenerateTailoredCv',
         aggregate='TailoredCv', event='TailoredCvGenerated', bottom=('external', 'Vertex AI (Gemini)')),
    dict(top=('policy', 'El CV adaptado solo usa hechos del CV maestro'), command='PrepareApplicationDraft',
         aggregate='ApplicationDraft', event='ApplicationDraftPrepared', bottom=('readmodel', 'Recommended Opportunities')),
    dict(top=('actor', 'Estudiante'), command='ApproveApplicationDraft', aggregate='ApplicationDraft',
         event='ApplicationDraftApproved', bottom=('external', 'Firebase Cloud Messaging')),
    dict(top=('policy', 'Aprobado (o modo Autónomo dentro de límites): enviar'), command='SubmitApplication',
         aggregate='Application', event='ApplicationSubmitted'),
    dict(top=('actor', 'Empleador'), command='GenerateShortlist', aggregate='Shortlist', event='ShortlistGenerated',
         bottom=('readmodel', 'Shortlist View')),
    dict(top=('actor', 'Empleador'), command='RequestInterview', aggregate='Interview', event='InterviewRequested'),
    dict(top=('policy', 'Cuando se solicita una entrevista, proponer franjas comunes'), command='ProposeInterviewSlots',
         aggregate='Interview', event='InterviewSlotsProposed', bottom=('external', 'Google Calendar API')),
    dict(top=('actor', 'Estudiante'), command='ConfirmInterviewSlot', aggregate='Interview', event='InterviewScheduled',
         bottom=('external', 'Google Calendar API')),
    dict(top=('actor', 'Empleador'), command='HireCandidate', aggregate='Application', event='CandidateHired'),
]

GIG_FLOW = [
    dict(top=('actor', 'Estudiante'), command='PublishGig', aggregate='Gig', event='GigPublished',
         bottom=('readmodel', 'Gig Catalog')),
    dict(top=('actor', 'Cliente'), command='SendHireRequest', aggregate='HireRequest', event='HireRequestSent'),
    dict(top=('actor', 'Estudiante'), command='AcceptHireRequest', aggregate='HireRequest', event='HireRequestAccepted'),
    dict(top=('policy', 'Al aceptar la solicitud, iniciar el engagement'), command='StartEngagement',
         aggregate='Engagement', event='EngagementStarted', bottom=('readmodel', 'Engagement Tracker')),
    dict(top=('actor', 'Cliente'), command='PayIntoEscrow', aggregate='Payment', event='PaymentHeldInEscrow',
         bottom=('external', 'Mercado Pago')),
    dict(top=('actor', 'Estudiante'), command='SubmitDelivery', aggregate='Engagement', event='DeliverySubmitted'),
    dict(top=('actor', 'Cliente'), command='AcceptDelivery', aggregate='Engagement', event='EngagementCompleted'),
    dict(top=('policy', 'Al completar, liberar el pago menos la comisión de 10%'), command='ReleasePayment',
         aggregate='Payment', event='PaymentReleased', bottom=('external', 'Mercado Pago')),
    dict(top=('actor', 'Cliente'), command='SubmitReview', aggregate='Review', event='ReviewSubmitted',
         bottom=('readmodel', 'Public Profile & Reviews')),
    dict(top=('policy', 'Cuando se registra una reseña, recalcular la reputación'), command='UpdateReputation',
         aggregate='StudentProfile', event='ReputationUpdated'),
]

# ---------------------------------------------------------------- Candidate contexts
CONTEXTS = [
    dict(name='AI Agent', kind='Core Domain', color='#7048e8',
         purpose='Recomienda oportunidades, adapta el CV y actúa en nombre del estudiante bajo un mandato.',
         events=['AgentMandateGranted', 'AgentMandatePaused', 'AgentMandateRevoked', 'OpportunityMatched',
                 'TailoredCvGenerated', 'TailoredCvRejected', 'ApplicationDraftPrepared', 'ApplicationDraftApproved',
                 'ApplicationDraftDiscarded', 'ShortlistGenerated', 'InterviewSlotsProposed']),
    dict(name='Profiles & Reputation', kind='Core Domain', color='#7048e8',
         purpose='Fuente de verdad de identidad profesional verificada: perfiles, CV maestro, portafolio y reputación.',
         events=['StudentProfileCreated', 'StudentVerified', 'MasterCvUpdated', 'PortfolioItemAdded',
                 'EmployerProfileCreated', 'EmployerVerified', 'ReviewSubmitted', 'ReputationUpdated']),
    dict(name='Marketplace', kind='Supporting Subdomain', color='#1c7ed6',
         purpose='Publicación y descubrimiento de servicios (gigs) y ofertas; sugerencia de precio.',
         events=['GigPublished', 'GigPaused', 'JobOfferPublished', 'JobOfferUpdated', 'JobOfferClosed', 'PriceSuggested']),
    dict(name='Hiring & Engagements', kind='Supporting Subdomain', color='#1c7ed6',
         purpose='Postulaciones, entrevistas, contrataciones, entregas y pagos en custodia.',
         events=['ApplicationSubmitted', 'ApplicationWithdrawn', 'InterviewRequested', 'InterviewScheduled', 'CandidateHired',
                 'HireRequestSent', 'HireRequestAccepted', 'EngagementStarted', 'PaymentHeldInEscrow', 'DeliverySubmitted',
                 'EngagementCompleted', 'PaymentReleased']),
    dict(name='Communications', kind='Generic Subdomain', color='#868e96',
         purpose='Mensajería, notificaciones, reportes, bloqueos y tickets de soporte.',
         events=['ConversationStarted', 'MessageSent', 'NotificationSent', 'UserReported', 'UserBlocked',
                 'SupportTicketOpened']),
]


def candidate_contexts(name, png):
    w = 1420
    body = [label(20, 18, w - 40, 'Candidate Context Discovery — eventos agrupados en bounded contexts candidatos', size=26, weight=700),
            label(20, 58, w - 40, 'Técnicas: start-with-value (núcleo de valor) y look-for-pivotal-events (cambios de etapa). '
                  'Los eventos provienen de la sesión de EventStorming.', size=15, color='#555')]
    layout = [(20, 110, 690), (720, 110, 680), (20, 0, 450), (480, 0, 520), (1010, 0, 390)]
    y2 = 0
    tops = []
    for i, ctx in enumerate(CONTEXTS):
        x, y, ww = layout[i]
        cols = max(1, (ww - 30) // 150)
        rows = (len(ctx['events']) + cols - 1) // cols
        hh = 118 + rows * 74
        tops.append((x, y, ww, hh))
    row1_h = max(t[3] for t in tops[:2])
    for i in range(2, 5):
        x, _, ww, hh = tops[i]
        tops[i] = (x, 110 + row1_h + 24, ww, hh)
    for ctx, (x, y, ww, hh) in zip(CONTEXTS, tops):
        body.append(box(x, y, ww, hh, '', bg='#fff', style='border:3px dashed %s;border-radius:14px' % ctx['color']))
        body.append(label(x + 16, y + 10, ww - 30, '<b style="font-size:20px">%s</b> &nbsp;<span style="background:%s;color:#fff;'
                          'border-radius:10px;padding:2px 8px;font-size:12px">%s</span>' % (esc(ctx['name']), ctx['color'], ctx['kind']),
                          size=14))
        body.append(label(x + 16, y + 44, ww - 30, esc(ctx['purpose']), size=13.5, color='#555'))
        cols = max(1, (ww - 30) // 150)
        for k, ev in enumerate(ctx['events']):
            r, c = divmod(k, cols)
            body.append(box(x + 16 + c * 150, y + 100 + r * 74, 138, 62, esc(words(ev)), bg=ES['event'], cls='sticky',
                            style='font-size:12.5px;font-weight:600'))
        y2 = max(y2, y + hh)
    h = y2 + 30
    render(name, w, h, ''.join(body), png, 'Candidate Context Discovery', scale=1.4)


# ---------------------------------------------------------------- Domain Storytelling
ICON = dict(student='🧑‍🎓', employer='👩‍💼', agent='🤖', cv='📃', offer='📢', match='🎯', draft='📝', app='📨',
            calendar='📅', invite='✉️', pay='💳', review='⭐', gig='🧰', list='📋', doc='📄', pause='⏸️', trash='🗑️',
            system='🏦', prefs='⚙️')
GROUP_COLORS = {'Marketplace': '#1c7ed6', 'AI Agent': '#7048e8', 'Profiles & Reputation': '#9c36b5',
                'Hiring & Engagements': '#2b8a3e', 'Communications': '#868e96', 'Externo': '#c2255c'}
ACTORS = {'luisa': ('employer', 'Luisa (empleadora)'), 'cliente': ('employer', 'Luisa (cliente)'),
          'julio': ('student', 'Julio (estudiante)'), 'agent': ('agent', 'Agente IA'),
          'gcal': ('calendar', 'Google Calendar'), 'mp': ('system', 'Mercado Pago')}


def domain_story(name, png, title, subtitle, sentences):
    """Historias de dominio en notación pictográfica (actor → actividad → objeto de trabajo → actor),
    presentadas como oraciones numeradas; el color indica el bounded context que atiende cada paso."""
    w, row_h, top = 1560, 86, 116
    h = top + row_h * len(sentences) + 70
    body = [label(20, 18, w - 40, esc(title), size=26, weight=700), label(20, 58, w - 40, esc(subtitle), size=15, color='#555')]
    svg = Svg(w, h)

    def actor(x, y, key):
        icon, text = ACTORS[key]
        return (label(x, y - 4, 70, ICON[icon], size=40, align='center', style='line-height:1') +
                label(x + 72, y + 8, 170, '<b>%s</b>' % esc(text), size=15))

    for n, (who, verb, obj_icon, obj, to_verb, to_who, ctx) in enumerate(sentences, 1):
        y = top + (n - 1) * row_h
        c = GROUP_COLORS[ctx]
        body.append(box(20, y, w - 40, row_h - 12, '', bg='#fff', style='border-left:7px solid %s;border-radius:8px;'
                        'box-shadow:0 1px 2px rgba(0,0,0,.08)' % c))
        svg.circle(56, y + 37, 17, '#343a40', str(n), size=15)
        body.append(actor(84, y + 14, who))
        svg.line([(330, y + 37), (600, y + 37)], color='#495057', width=2.2)
        body.append(label(330, y + 10, 270, esc(verb), size=14, weight=600, align='center', color='#333', style='white-space:nowrap'))
        body.append(label(612, y + 12, 60, ICON[obj_icon], size=34, align='center', style='line-height:1'))
        body.append(label(676, y + 22, 300, esc(obj), size=15))
        if to_who:
            svg.line([(990, y + 37), (1090, y + 37)], color='#495057', width=2.2)
            body.append(label(990, y + 10, 100, esc(to_verb), size=14, weight=600, align='center', color='#333'))
            body.append(actor(1098, y + 14, to_who))
        body.append(label(w - 250, y + 26, 220, '<span style="background:%s;color:#fff;border-radius:10px;padding:3px 10px;'
                          'font-size:12.5px">%s</span>' % (c, esc(ctx)), size=13, align='right'))
    ly = h - 44
    body.append(label(20, ly, w - 40, 'Notación: <b>actor</b> → actividad → <b>objeto de trabajo</b> (→ actor destinatario). '
                      'El color del borde indica el bounded context que atiende la actividad.', size=14, color='#444'))
    render(name, w, h, ''.join(body) + svg.render(), png, title, scale=1.4)


def stories_dst():
    domain_story('dst-1-postulacion-asistida', 'imgs/cap4/dst-1-postulacion-asistida.png',
                 'Domain Storytelling 1 — Postulación asistida por el Agente IA',
                 'Escenario principal en modo Asistido: ninguna postulación se envía sin la aprobación del estudiante.', [
        ('luisa', 'publica', 'offer', 'Oferta de práctica', '', None, 'Marketplace'),
        ('agent', 'lee', 'offer', 'Oferta de práctica', '', None, 'AI Agent'),
        ('agent', 'compara la oferta con', 'cv', 'CV maestro verificado de Julio', '', None, 'Profiles & Reputation'),
        ('agent', 'genera', 'match', 'Recomendación (match score y razones)', '', None, 'AI Agent'),
        ('agent', 'genera (solo hechos verificados)', 'cv', 'CV adaptado', '', None, 'AI Agent'),
        ('agent', 'prepara y notifica', 'draft', 'Borrador de postulación', 'a', 'julio', 'Communications'),
        ('julio', 'revisa y aprueba', 'draft', 'Borrador de postulación', '', None, 'AI Agent'),
        ('agent', 'envía', 'app', 'Postulación asistida por IA', 'para', 'luisa', 'Hiring & Engagements'),
        ('luisa', 'revisa', 'app', 'Postulación asistida por IA', '', None, 'Hiring & Engagements'),
    ])
    domain_story('dst-2-preseleccion-entrevista', 'imgs/cap4/dst-2-preseleccion-entrevista.png',
                 'Domain Storytelling 2 — Preselección de candidatos y entrevista',
                 'El empleador revisa la preselección del Agente IA y se agenda la entrevista según los calendarios.', [
        ('luisa', 'solicita', 'list', 'Preselección de su oferta', 'al', 'agent', 'AI Agent'),
        ('agent', 'ordena por compatibilidad', 'app', 'Postulaciones de la oferta', '', None, 'AI Agent'),
        ('agent', 'entrega (sin atributos personales)', 'list', 'Preselección: top 5 con razones', 'a', 'luisa', 'AI Agent'),
        ('luisa', 'solicita', 'invite', 'Entrevista con Julio', '', None, 'Hiring & Engagements'),
        ('gcal', 'devuelve', 'calendar', 'Disponibilidad de ambas partes', '', None, 'Externo'),
        ('agent', 'propone', 'calendar', 'Tres franjas comunes', 'a', 'julio', 'AI Agent'),
        ('julio', 'confirma', 'calendar', 'Una franja', '', None, 'Hiring & Engagements'),
        ('gcal', 'envía', 'invite', 'Invitación con enlace de videollamada', 'a', 'luisa', 'Externo'),
    ])
    domain_story('dst-3-contratacion-pago', 'imgs/cap4/dst-3-contratacion-pago.png',
                 'Domain Storytelling 3 — Contratación de un servicio y pago en custodia',
                 'Flujo del marketplace de servicios (gigs): del catálogo a la reseña.', [
        ('cliente', 'busca y elige', 'gig', 'Servicio de diseño (gig) de Julio', '', None, 'Marketplace'),
        ('cliente', 'envía', 'doc', 'Solicitud de contratación', 'a', 'julio', 'Hiring & Engagements'),
        ('julio', 'acepta', 'doc', 'Solicitud de contratación', '', None, 'Hiring & Engagements'),
        ('cliente', 'deposita', 'pay', 'Pago del servicio', 'en', 'mp', 'Hiring & Engagements'),
        ('mp', 'retiene en custodia', 'pay', 'Pago del servicio', '', None, 'Externo'),
        ('julio', 'entrega', 'doc', 'Entregable', 'a', 'cliente', 'Hiring & Engagements'),
        ('cliente', 'acepta', 'doc', 'Entregable', '', None, 'Hiring & Engagements'),
        ('mp', 'libera (menos 10% de comisión)', 'pay', 'Pago del servicio', 'a', 'julio', 'Externo'),
        ('cliente', 'registra', 'review', 'Reseña del trabajo de Julio', '', None, 'Profiles & Reputation'),
    ])
    domain_story('dst-4-control-del-estudiante', 'imgs/cap4/dst-4-control-del-estudiante.png',
                 'Domain Storytelling 4 — El estudiante mantiene el control del Agente IA',
                 'Caminos alternativos: rechazo de un borrador, pausa y revocación del mandato.', [
        ('agent', 'prepara', 'draft', 'Borrador de postulación', 'para', 'julio', 'AI Agent'),
        ('julio', 'rechaza con motivo', 'draft', 'Borrador de postulación', '', None, 'AI Agent'),
        ('agent', 'ajusta', 'prefs', 'Preferencias (categoría excluida)', '', None, 'AI Agent'),
        ('julio', 'pausa durante exámenes', 'pause', 'Mandato del agente', '', None, 'AI Agent'),
        ('agent', 'descarta', 'draft', 'Borradores pendientes', '', None, 'AI Agent'),
        ('julio', 'revoca', 'pause', 'Mandato del agente', '', None, 'AI Agent'),
        ('agent', 'elimina', 'trash', 'CV adaptados no enviados y embeddings', '', None, 'AI Agent'),
    ])


# ---------------------------------------------------------------- Context Map
def context_map(name, png):
    w, h = 1500, 960
    bcs = {
        'P': ('Profiles & Reputation', 'Core', (40, 380, 300, 140)),
        'A': ('AI Agent', 'Core', (430, 380, 300, 140)),
        'C': ('Communications', 'Generic', (830, 380, 280, 140)),
        'M': ('Marketplace', 'Supporting', (1160, 120, 300, 140)),
        'H': ('Hiring & Engagements', 'Supporting', (1160, 640, 300, 140)),
    }
    exts = {
        'Firebase Authentication': (40, 600, 240, 56),
        'Vertex AI (Gemini, Embeddings)': (330, 250, 230, 64),
        'SendGrid · Firebase Cloud Messaging': (830, 590, 270, 60),
        'Google Calendar API': (880, 724, 240, 48),
        'Mercado Pago': (880, 782, 240, 48),
    }
    colors = {'Core': '#7048e8', 'Supporting': '#1c7ed6', 'Generic': '#868e96'}
    svg = Svg(w, h)
    badges = []

    def rel(num, pts, pattern, at, color='#343a40', ext=False):
        svg.line(pts, color=color, width=2.6)
        bx, by = at
        if ext:
            badges.append('<div class="abs" style="left:%dpx;top:%dpx;background:#fff0f6;border:1.5px solid %s;border-radius:6px;'
                          'font-size:12.5px;font-weight:700;color:%s;padding:1px 6px">%s</div>' % (bx, by, color, color, pattern))
            return
        badges.append('<div class="abs" style="left:%dpx;top:%dpx;display:flex;align-items:center;gap:6px;white-space:nowrap">'
                      '<span style="background:#343a40;color:#fff;border-radius:12px;font-size:13px;font-weight:700;padding:2px 8px">%s</span>'
                      '<span style="background:#fff;border:1.5px solid #343a40;border-radius:6px;font-size:13px;font-weight:600;'
                      'padding:1px 6px">%s</span></div>' % (bx, by, num, pattern))

    rel('R1', [(340, 450), (430, 450)], 'C/S', (330, 404))
    rel('R2', [(1160, 190), (580, 190), (580, 380)], 'C/S', (800, 160))
    rel('R3', [(1160, 710), (580, 710), (580, 520)], 'CF', (800, 680))
    rel('R4', [(1310, 260), (1310, 640)], 'CF', (1322, 440))
    rel('R5', [(190, 380), (190, 80), (1310, 80), (1310, 120)], 'CF', (700, 50))
    rel('R6', [(1310, 780), (1310, 880), (310, 880), (310, 520)], 'C/S', (700, 850))
    rel('R7', [(730, 450), (830, 450)], 'CF', (716, 404))
    rel('R8', [(1180, 260), (1080, 380)], 'CF', (1136, 300))
    rel('R9', [(1180, 640), (1080, 520)], 'CF', (1136, 560))
    pink = '#c2255c'
    rel('', [(160, 600), (160, 520)], 'ACL', (170, 552), pink, True)
    rel('', [(445, 314), (445, 380)], 'ACL', (455, 334), pink, True)
    rel('', [(965, 590), (965, 520)], 'ACL', (975, 542), pink, True)
    rel('', [(1120, 748), (1160, 748)], 'ACL', (1050, 700), pink, True)
    rel('', [(1120, 806), (1200, 806), (1200, 780)], 'ACL', (1130, 812), pink, True)
    body = [label(20, 12, 900, 'Context Map — Triple B', size=26, weight=700), svg.render()]
    for key, (txt, kind, (x, y, ww, hh)) in bcs.items():
        body.append(box(x, y, ww, hh, '<div><div style="font-size:20px;font-weight:700">%s</div><div style="margin-top:8px">'
                        '<span style="background:%s;color:#fff;border-radius:10px;padding:2px 10px;font-size:13px">%s Domain</span>'
                        '</div></div>' % (esc(txt), colors[kind], kind), cls='card', style='border:3px solid %s' % colors[kind]))
    for txt, (x, y, ww, hh) in exts.items():
        body.append(box(x, y, ww, hh, esc(txt), cls='card', style='border:2px dashed %s;background:#fff0f6;font-size:13.5px;'
                        'padding:4px' % pink))
    body += badges
    body.append(label(20, h - 38, w - 40, 'Flecha: upstream → downstream · <b>C/S</b> Customer/Supplier (downstream con ACL) · '
                      '<b>CF</b> Conformist · upstream expone Open Host Service / Published Language · '
                      '<span style="color:%s">rosado: sistemas externos integrados mediante Anticorruption Layer (ACL)</span>' % pink,
                      size=13.5, color='#444'))
    render(name, w, h, ''.join(body), png, 'Context Map', scale=1.4)


def build():
    big_picture('eventstorming-big-picture', 'imgs/cap4/eventstorming-big-picture.png',
                'EventStorming — Big Picture de Triple B',
                'Línea de tiempo de eventos de dominio por flujo de negocio, con hotspots y caminos alternativos.')
    process_level('eventstorming-agente-ia', 'imgs/cap4/eventstorming-agente-ia.png',
                  'EventStorming — Process level: postulación asistida por el Agente IA',
                  'Actores y políticas disparan comandos sobre agregados, que emiten eventos; se indican sistemas externos y read models.',
                  AGENT_FLOW)
    process_level('eventstorming-contratacion', 'imgs/cap4/eventstorming-contratacion.png',
                  'EventStorming — Process level: contratación de un servicio y pago en custodia',
                  'Flujo del marketplace de servicios con pago retenido hasta la aceptación de la entrega.', GIG_FLOW)
    big_picture('candidate-pivotal-events', 'imgs/cap4/candidate-pivotal-events.png',
                'Candidate Context Discovery — Paso 1: pivotal events',
                'Se marcan los eventos que cambian la etapa del negocio; delimitan las fronteras candidatas entre contextos.',
                pivotal=True)
    candidate_contexts('candidate-contexts', 'imgs/cap4/candidate-contexts.png')
    stories_dst()
    context_map('context-map', 'imgs/cap4/context-map.png')
