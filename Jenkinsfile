pipeline {
    agent any

    environment {
        // Credenziali salvate in Jenkins
        DOCKER_CREDS = 'dockerhub-id'
        K8S_CONFIG   = 'k8s-secret'
        DOCKER_USER  = 'claudia179'
    }

    stages {
        stage('Inizializzazione') {
            steps {
                echo "🚀 Avvio Pipeline CI/CD per ${DOCKER_USER}"
            }
        }

        // --------------------------------------------------------
        // FASE 1: PARALLEL PIPELINE PER OGNI MICROSERVIZIO
        // (Unit Test -> Build -> Push -> Deploy)
        // --------------------------------------------------------
        stage('Gestione Microservizi') {
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
                    steps { processService('log-analytics-service', 'analytics-img', 'analytics-deployment') }
                }
            }
        }

        // --------------------------------------------------------
        // FASE 2: TEST DI INTEGRAZIONE FINALE (POSTMAN/NEWMAN)
        // Eseguiti solo se il deploy è andato a buon fine
        // --------------------------------------------------------
        stage('Integration Tests (Postman)') {
            steps {
                script {
                    echo "🔍 Ricerca ed esecuzione collezioni Postman..."
                    
                    // Cerca tutti i file JSON nelle cartelle 'tests' dei servizi
                    // Esempio: auth-service/tests/auth_collection.json
                    def collections = findFiles(glob: '**/tests/*_collection.json')

                    if (collections.length > 0) {
                        docker.image('postman/newman').inside {
                            collections.each { collection ->
                                echo "⚡ Eseguendo test: ${collection.path}"
                                // Esegue newman. 
                                // Nota: Assicurati che le URL nel JSON puntino ai Service K8s (es. http://auth-service:5000)
                                sh "newman run ${collection.path} --reporters cli"
                            }
                        }
                    } else {
                        echo "⚠️ Nessun file Postman trovato. Salto questo step."
                    }
                }
            }
        }
    }
}

// --------------------------------------------------------
// FUNZIONE CORE: Gestisce il ciclo di vita del singolo servizio
// --------------------------------------------------------
def processService(serviceDir, imageName, k8sDeployName) {
    
    // 1. UNIT TESTING (Sandbox Pattern)
    // Avviamo un DB pulito solo per la durata del test
    stage("${serviceDir} - Unit Tests") {
        dir(serviceDir) {
            script {
                echo "🧪 [${serviceDir}] Avvio DB Sandbox..."
                
                docker.image('postgres:13').withRun('-e POSTGRES_DB=test_db -e POSTGRES_USER=test_user -e POSTGRES_PASSWORD=test_pass') { c ->
                    
                    // Wait for DB ready
                    docker.image('postgres:13').inside("--link ${c.id}:db") {
                        sh 'while ! pg_isready -h db -U test_user; do sleep 1; done'
                    }

                    // Esecuzione Pytest con Injection della Variabile
                    docker.image('python:3.9').inside("--link ${c.id}:db") {
                        sh 'pip install -r requirements.txt'
                        // Qui avviene la magia: DATABASE_URL attiva la logica nel tuo conftest.py
                        withEnv(['DATABASE_URL=postgresql://test_user:test_pass@db:5432/test_db']) {
                            sh 'pytest'
                        }
                    }
                }
            }
        }
    }

    // 2. BUILD & PUSH
    stage("${serviceDir} - Build & Push") {
        dir(serviceDir) {
            withDockerRegistry(credentialsId: 'dockerhub-id', url: 'https://index.docker.io/v1/') {
                sh "docker build -t ${DOCKER_USER}/${imageName}:${BUILD_NUMBER} ."
                sh "docker push ${DOCKER_USER}/${imageName}:${BUILD_NUMBER}"
                sh "docker tag ${DOCKER_USER}/${imageName}:${BUILD_NUMBER} ${DOCKER_USER}/${imageName}:latest"
                sh "docker push ${DOCKER_USER}/${imageName}:latest"
            }
        }
    }

    // 3. DEPLOY SU KUBERNETES
    stage("${serviceDir} - Deploy") {
        withCredentials([file(credentialsId: 'k8s-secret', variable: 'KUBECONFIG')]) {
            script {
                // Applica o Aggiorna le risorse YAML
                sh "kubectl apply -f k8s/${serviceDir}.yaml"
                
                // Aggiorna l'immagine
                sh "kubectl set image deployment/${k8sDeployName} ${k8sDeployName}=${DOCKER_USER}/${imageName}:${BUILD_NUMBER} --record"
                
                // IMPORTANTE: Aspetta che il deploy sia finito prima di passare ai test di integrazione
                sh "kubectl rollout status deployment/${k8sDeployName} --timeout=60s"
            }
        }
    }
}
