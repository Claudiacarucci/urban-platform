pipeline {
    agent any

    environment {
        // LE TUE VARIABILI CONFIGURATE
        DOCKER_CREDS = 'dockerhub-id'
        K8S_CONFIG   = 'k8s-secret'    // L'ID che mi hai indicato
        DOCKER_USER  = 'claudia179'    // Il tuo username Docker Hub
    }

    stages {
        stage('Analisi e Deploy Microservizi') {
            parallel {
                stage('Auth Service') {
                    when { changeset "auth-service/**" }
                    steps { processService('auth-service', 'auth-service-img', 'auth-deployment') }
                }
                stage('Assignment Service') {
                    when { changeset "assignment-service/**" }
                    steps { processService('assignment-service', 'assignment-service-img', 'assignment-deployment') }
                }
                stage('Ticket Service') {
                    when { changeset "ticket-service/**" }
                    steps { processService('ticket-service', 'ticket-service-img', 'ticket-deployment') }
                }
                stage('Map Service') {
                    when { changeset "map-service/**" }
                    steps { processService('map-service', 'map-service-img', 'map-deployment') }
                }
                stage('Media Service') {
                    when { changeset "media-service/**" }
                    steps { processService('media-service', 'media-service-img', 'media-deployment') }
                }
                stage('Notification Service') {
                    when { changeset "notification-service/**" }
                    steps { processService('notification-service', 'notification-service-img', 'notification-deployment') }
                }
                stage('Geo Service') {
                    when { changeset "geo-service/**" }
                    steps { processService('geo-service', 'geo-service-img', 'geo-deployment') }
                }
                stage('Log Analytics') {
                    when { changeset "log-analytics-service/**" }
                    steps { processService('log-analytics-service', 'log-analytics-img', 'log-analytics-deployment') }
                }
            }
        }
    }
}

// FUNZIONE AUTOMATICA: Fa Test, Build, Push e Deploy per un servizio
def processService(serviceDir, imageName, k8sDeployName) {
    
    // 1. UNIT TEST
    stage("${serviceDir} - Test") {
        dir(serviceDir) {
            sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt || echo "Nessun requirement trovato"
                export FLASK_APP=app.py
                # Se esiste la cartella tests, esegui pytest
                if [ -d "tests" ]; then pytest tests/ --junitxml=test-results.xml; fi
            '''
        }
    }

    // 2. BUILD & PUSH (Docker Hub)
    stage("${serviceDir} - Build & Push") {
        script {
            dir(serviceDir) {
                docker.withRegistry('', DOCKER_CREDS) {
                    // Costruisce l'immagine: claudia179/nome-servizio:numero-build
                    def img = docker.build("${DOCKER_USER}/${imageName}:${BUILD_NUMBER}")
                    img.push()         // Push della versione specifica
                    img.push('latest') // Push della versione 'latest'
                }
            }
        }
    }
    
    // 3. DEPLOY SU KUBERNETES (Aggiorna l'immagine nel cluster)
    stage("${serviceDir} - K8s Deploy") {
        withCredentials([file(credentialsId: K8S_CONFIG, variable: 'KUBECONFIG')]) {
            script {
                // Nota: Il comando 'set image' funziona solo se il deployment esiste già nel cluster.
                // Se è la prima volta assoluta, potrebbe dare errore se non hai fatto 'kubectl apply' dei file yaml.
                // Usiamo '|| true' per non far fallire la pipeline se il deployment non esiste ancora.
                sh """
                    kubectl set image deployment/${k8sDeployName} ${k8sDeployName}=${DOCKER_USER}/${imageName}:${BUILD_NUMBER} --record || echo "Deployment ${k8sDeployName} non trovato, salto aggiornamento."
                """
            }
        }
    }
}
