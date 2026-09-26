workspace "Triple B" "Arquitectura de software de Triple B (startup NodoB) documentada con C4 Model." {

    !identifiers flat

    model {
        visitante = person "Visitante" "Estudiante o empleador potencial que llega a la landing page."
        estudiante = person "Estudiante freelancer" "Estudiante universitario que ofrece servicios y delega la búsqueda y postulación al Agente IA."
        empleador = person "Empleador / Emprendedor" "Microempresa, emprendimiento o persona que publica ofertas y contrata servicios."
        admin = person "Administrador de NodoB" "Verifica perfiles, modera reportes y atiende tickets de soporte."

        group "NodoB" {
            landing = softwareSystem "Triple B Landing Page" "Sitio estático con la propuesta de valor, FAQ y llamados a la acción por segmento." "Landing"
            tripleB = softwareSystem "Triple B Platform" "Plataforma freelance para universitarios con un Agente IA que recomienda oportunidades, adapta CVs con información verificada, prepara postulaciones y coordina entrevistas." {
                webApp = container "Web Application" "SPA para estudiantes, empleadores y administradores. i18n (en_US, es_419) y a11y (ARIA)." "Vue 3, TypeScript, Vuetify" "Web Browser"
                mobileApp = container "Mobile Application" "App para estudiantes: recomendaciones, aprobación de postulaciones, confirmación de entrevistas y notificaciones push." "Flutter (Dart)" "Mobile"
                apiGateway = container "API Gateway" "Punto de entrada único. Valida el JWT emitido por Firebase y enruta a los servicios." "Google Cloud API Gateway" "Gateway"
                profilesSvc = container "Profiles & Reputation Service" "Perfiles, verificación de estudiantes, CV maestro, portafolio y reseñas." "NestJS (TypeScript)" "Service"
                marketplaceSvc = container "Marketplace Service" "Servicios (gigs), ofertas y puestos de practicante, búsqueda del catálogo y sugerencia de precio." "NestJS (TypeScript)" "Service"
                agentSvc = container "AI Agent Service" "API del agente: mandatos, recomendaciones, explicación del match, aprobación de borradores y preselección." "NestJS (TypeScript)" "Service"
                agentWorker = container "AI Agent Worker" "Procesa eventos de forma asíncrona: embeddings, matching, CV adaptados con validación de hechos y envío de postulaciones autorizadas." "NestJS (TypeScript)" "Worker"
                hiringSvc = container "Hiring & Engagements Service" "Postulaciones, entrevistas, contrataciones, entregas y pagos en custodia." "NestJS (TypeScript)" "Service"
                commsSvc = container "Communications Service" "Mensajería en tiempo real, notificaciones, reportes y tickets de soporte." "NestJS (TypeScript), WebSocket" "Service"
                eventBus = container "Event Bus" "Tópicos de eventos de dominio (Published Language) entre bounded contexts." "Google Cloud Pub/Sub" "Queue"
                scheduler = container "Agent Scheduler" "Dispara barridos periódicos de oportunidades para los mandatos activos." "Google Cloud Scheduler" "Scheduler"
                profilesDb = container "Profiles DB" "Perfiles, metadatos del CV maestro, portafolio y reseñas." "Cloud SQL for PostgreSQL" "Database"
                marketplaceDb = container "Marketplace DB" "Gigs, ofertas, categorías y taxonomía de habilidades." "Cloud SQL for PostgreSQL" "Database"
                agentDb = container "AI Agent DB" "Mandatos, recomendaciones, borradores y embeddings de perfiles y ofertas." "Cloud SQL for PostgreSQL + pgvector" "Database"
                hiringDb = container "Hiring DB" "Postulaciones, entrevistas, engagements y pagos." "Cloud SQL for PostgreSQL" "Database"
                commsDb = container "Communications DB" "Conversaciones, notificaciones, reportes y tickets." "Cloud SQL for PostgreSQL" "Database"
                fileStorage = container "File Storage" "CV maestros, CV adaptados (PDF) y evidencias de portafolio." "Google Cloud Storage" "Storage"
            }
        }

        firebaseAuth = softwareSystem "Firebase Authentication" "Registro, inicio de sesión con correo o Google, recuperación de contraseña y emisión de JWT." "External"
        vertexAI = softwareSystem "Vertex AI" "Modelos Gemini (generación de texto) y de embeddings (vectorización)." "External"
        googleCalendar = softwareSystem "Google Calendar API" "Disponibilidad (free/busy) e invitaciones de entrevista con enlace de videollamada." "External"
        mercadoPago = softwareSystem "Mercado Pago" "Cobros, custodia y liberación de pagos del marketplace." "External"
        sendGrid = softwareSystem "SendGrid" "Correo transaccional." "External"
        fcm = softwareSystem "Firebase Cloud Messaging" "Notificaciones push web y móvil." "External"
        analytics = softwareSystem "Google Analytics" "Analítica de visitas y conversiones de la landing page." "External"

        # Relaciones a nivel de sistema (vistas Landscape y Context)
        estudiante -> tripleB "Gestiona su perfil, delega la búsqueda al Agente IA, aprueba postulaciones y ofrece servicios" "HTTPS"
        empleador -> tripleB "Publica ofertas, revisa la preselección, entrevista, contrata y paga" "HTTPS"
        admin -> tripleB "Verifica perfiles, modera reportes y atiende tickets" "HTTPS"
        tripleB -> firebaseAuth "Autentica usuarios y valida tokens" "HTTPS"
        tripleB -> vertexAI "Genera embeddings, CV adaptados y explicaciones del match" "HTTPS"
        tripleB -> googleCalendar "Consulta disponibilidad y agenda entrevistas" "HTTPS / OAuth 2.0"
        tripleB -> mercadoPago "Cobra, retiene y libera pagos" "HTTPS"
        mercadoPago -> tripleB "Notifica cambios de estado de pago (webhook)" "HTTPS"
        tripleB -> sendGrid "Envía correos transaccionales" "HTTPS"
        tripleB -> fcm "Envía notificaciones push" "HTTPS"

        # Personas
        visitante -> landing "Conoce la propuesta de valor" "HTTPS"
        estudiante -> webApp "Gestiona su perfil, el mandato del agente, postulaciones y servicios" "HTTPS"
        estudiante -> mobileApp "Revisa recomendaciones, aprueba postulaciones y confirma entrevistas"
        empleador -> webApp "Publica ofertas, revisa la preselección, contrata y paga" "HTTPS"
        admin -> webApp "Verifica perfiles, modera reportes y atiende tickets" "HTTPS"

        # Landing page
        landing -> webApp "Redirige los llamados a la acción de cada segmento" "HTTPS"
        landing -> analytics "Registra visitas y conversiones" "HTTPS"

        # Aplicaciones cliente
        webApp -> firebaseAuth "Autentica usuarios" "Firebase SDK / HTTPS"
        mobileApp -> firebaseAuth "Autentica usuarios" "Firebase SDK / HTTPS"
        webApp -> apiGateway "Consume las APIs" "JSON/HTTPS"
        mobileApp -> apiGateway "Consume las APIs" "JSON/HTTPS"
        webApp -> commsSvc "Mensajería en tiempo real" "WebSocket (WSS)"

        # API Gateway
        apiGateway -> firebaseAuth "Valida la firma del JWT (JWKS)" "HTTPS"
        apiGateway -> profilesSvc "Enruta /students, /employers, /reviews" "JSON/HTTPS"
        apiGateway -> marketplaceSvc "Enruta /gigs, /job-offers" "JSON/HTTPS"
        apiGateway -> agentSvc "Enruta /agent" "JSON/HTTPS"
        apiGateway -> hiringSvc "Enruta /applications, /interviews, /engagements, /payments" "JSON/HTTPS"
        apiGateway -> commsSvc "Enruta /conversations, /notifications, /tickets" "JSON/HTTPS"
        mercadoPago -> apiGateway "Notifica cambios de estado de pago (webhook)" "HTTPS"

        # Profiles & Reputation
        profilesSvc -> profilesDb "Lee y escribe" "SQL/TLS"
        profilesSvc -> fileStorage "Guarda CV maestros y evidencias" "HTTPS"
        profilesSvc -> eventBus "Publica StudentVerified, MasterCvUpdated, ReviewSubmitted" "Pub/Sub"

        # Marketplace
        marketplaceSvc -> marketplaceDb "Lee y escribe" "SQL/TLS"
        marketplaceSvc -> eventBus "Publica JobOfferPublished, JobOfferClosed, GigPublished" "Pub/Sub"

        # AI Agent
        agentSvc -> agentDb "Lee y escribe mandatos, recomendaciones y borradores" "SQL/TLS"
        agentSvc -> vertexAI "Genera explicaciones del match y reordena la preselección" "HTTPS"
        agentSvc -> eventBus "Publica AgentMandateGranted, ApplicationDraftApproved" "Pub/Sub"
        eventBus -> agentWorker "Entrega eventos de ofertas, perfiles y aprobaciones" "Pub/Sub push (HTTPS)"
        scheduler -> agentWorker "Dispara barridos periódicos" "HTTPS"
        agentWorker -> agentDb "Lee y escribe embeddings (pgvector), recomendaciones y borradores" "SQL/TLS"
        agentWorker -> vertexAI "Genera embeddings y CV adaptados" "HTTPS"
        agentWorker -> fileStorage "Guarda CV adaptados en PDF" "HTTPS"
        agentWorker -> hiringSvc "Registra postulaciones autorizadas" "JSON/HTTPS"
        agentWorker -> eventBus "Publica OpportunityMatched, ApplicationDraftPrepared" "Pub/Sub"

        # Hiring & Engagements
        hiringSvc -> hiringDb "Lee y escribe" "SQL/TLS"
        hiringSvc -> googleCalendar "Consulta disponibilidad y crea eventos de entrevista" "HTTPS / OAuth 2.0"
        hiringSvc -> mercadoPago "Crea cobros en custodia y libera pagos" "HTTPS"
        hiringSvc -> eventBus "Publica ApplicationSubmitted, InterviewScheduled, EngagementCompleted, PaymentReleased" "Pub/Sub"
        eventBus -> hiringSvc "Entrega JobOfferClosed" "Pub/Sub push (HTTPS)"
        eventBus -> profilesSvc "Entrega EngagementCompleted (habilita reseñas)" "Pub/Sub push (HTTPS)"

        # Communications
        eventBus -> commsSvc "Entrega los eventos que se notifican" "Pub/Sub push (HTTPS)"
        commsSvc -> commsDb "Lee y escribe" "SQL/TLS"
        commsSvc -> sendGrid "Envía correos transaccionales" "HTTPS"
        commsSvc -> fcm "Envía notificaciones push" "HTTPS"
        fcm -> mobileApp "Entrega notificaciones push"

        production = deploymentEnvironment "Production" {
            deploymentNode "Dispositivo del usuario" "" "Computadora o smartphone" {
                deploymentNode "Navegador web" "" "Chrome, Edge, Firefox o Safari" {
                    containerInstance webApp
                }
                deploymentNode "Smartphone del estudiante" "" "Android 10+ / iOS 16+" {
                    containerInstance mobileApp
                }
            }
            deploymentNode "Firebase Hosting" "Hosting estático con CDN global" "Google Cloud" {
                softwareSystemInstance landing
                hostingCdn = infrastructureNode "CDN de Firebase Hosting" "Sirve la landing page y los archivos de la SPA" "Firebase Hosting"
            }
            deploymentNode "Google Cloud Platform" "" "Región us-central1" {
                deploymentNode "Cloud API Gateway" "" "Servicio administrado" {
                    containerInstance apiGateway
                }
                deploymentNode "Cloud Run" "" "Contenedores serverless con escala a cero" {
                    containerInstance profilesSvc
                    containerInstance marketplaceSvc
                    containerInstance agentSvc
                    containerInstance agentWorker
                    containerInstance hiringSvc
                    containerInstance commsSvc
                }
                deploymentNode "Cloud Pub/Sub" "" "Mensajería administrada" {
                    containerInstance eventBus
                }
                deploymentNode "Cloud Scheduler" "" "Tareas programadas" {
                    containerInstance scheduler
                }
                deploymentNode "Cloud SQL" "" "PostgreSQL 16 + pgvector, una base de datos lógica por bounded context" {
                    containerInstance profilesDb
                    containerInstance marketplaceDb
                    containerInstance agentDb
                    containerInstance hiringDb
                    containerInstance commsDb
                }
                deploymentNode "Cloud Storage" "" "Bucket regional con acceso por URL firmada" {
                    containerInstance fileStorage
                }
                secrets = infrastructureNode "Secret Manager" "Credenciales de Mercado Pago, SendGrid y Google Calendar" "Google Secret Manager"
                observability = infrastructureNode "Cloud Logging & Monitoring" "Logs, métricas, trazas y alertas" "Google Cloud Observability"
            }
            hostingCdn -> webApp "Entrega la SPA" "HTTPS"
        }
    }

    views {
        systemLandscape "Landscape" "System Landscape de NodoB: sistemas propios, usuarios y sistemas externos." {
            include *
            autoLayout lr 250 150
        }
        systemContext tripleB "Context" "Diagrama de contexto de Triple B Platform." {
            include *
            autoLayout lr 250 150
        }
        container tripleB "Containers" "Diagrama de contenedores de Triple B Platform." {
            include *
            autoLayout tb 160 120
        }
        container tripleB "Containers-AIAgent" "Contenedores que participan en el flujo del Agente IA." {
            include estudiante mobileApp webApp apiGateway agentSvc agentWorker scheduler eventBus agentDb fileStorage vertexAI marketplaceSvc profilesSvc hiringSvc
            autoLayout lr 200 120
        }
        deployment tripleB production "Deployment" "Despliegue de Triple B en producción (Google Cloud y Firebase)." {
            include *
            exclude "eventBus -> *" "* -> eventBus" "* -> fileStorage"
            autoLayout lr 200 120
        }

        styles {
            element "Person" {
                shape Person
                background #08427b
                color #ffffff
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Database" {
                shape Cylinder
            }
            element "Queue" {
                shape Pipe
            }
            element "Web Browser" {
                shape WebBrowser
            }
            element "Mobile" {
                shape MobileDevicePortrait
            }
        }
    }
}
