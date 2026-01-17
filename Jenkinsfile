pipeline {
    agent any

    environment {
        // Configurazione Globale e Credenziali
        DOCKER_CREDS = 'dockerhub-id'
        K8S_CONFIG   = 'k8s-secret'
        DOCKER_USER  = 'claudia179'
    }

    stages {
        stage('Inizializzazione') {
            steps {
                echo "Avvio dell'esecuzione della pipeline CI/CD per l'utente: ${DOCKER_USER}"
            }
        }

        // --------------------------------------------------------
        // FASE 1: PIPELINE PARALLELA PER I MICROSERVIZI
        // (Test Unitari -> Build -> Push -> Deploy)
        // --------------------------------------------------------
        stage('Gestione Ciclo di Vita Microservizi') {
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
        // FASE 2: TEST DI INTEGRAZIONE (POSTMAN/NEWMAN)
        // Eseguiti solo in caso di deploy avvenuto con successo
        // --------------------------------------------------------
        stage('Test di Integrazione (Postman)') {
            steps {
                script {
                    echo "Avvio scansione dei file di collezione Postman tramite shell..."
                    
                    // Utilizzo del comando 'find' nativo per individuare i file JSON delle collezioni
                    def findOutput = sh(script: 'find . -type f -path "*/tests/*_collection.json"', returnStdout: true).trim()

                    if (findOutput) {
                        // Converte l'output in una lista di percorsi
                        def collections = findOutput.split("\n")
                        
                        // --entrypoint='': Sovrascrive il comando di default di Newman che causava l'uscita immediata.
                        // -u 0:0: Esegue come root per evitare problemi di permessi.
                        docker.image('postman/newman').inside("--entrypoint='' -u 0:0") {
                            collections.each { collectionPath ->
                                echo "Esecuzione della collezione Postman: ${collectionPath} tramite Newman..."
                                // Esegue i test e riporta i risultati in console (cli)
                                sh "newman run ${collectionPath} --reporters cli"
                            }
                        }
                    } else {
                        echo "Nessun file di collezione Postman trovato. La fase di test di integrazione sarà saltata."
                    }
                }
            }
        }
    }
}

// --------------------------------------------------------
// FUNZIONE CORE: Gestore del ciclo di vita del servizio
// --------------------------------------------------------
def processService(serviceDir, imageName, k8sDeployName) {
    
    // 1. TEST UNITARI (Pattern Sandbox)
    stage("${serviceDir} - Test Unitari") {
        dir(serviceDir) {
            script {
                echo "[${serviceDir}] Inizializzazione del database PostgreSQL Sandbox effimero per i test unitari..."
                
                // Avvio del container database isolato
                docker.image('postgres:13').withRun('-e POSTGRES_DB=test_db -e POSTGRES_USER=test_user -e POSTGRES_PASSWORD=test_pass') { c ->
                    
                    // Attesa disponibilità del database (Health Check)
                    docker.image('postgres:13').inside("--link ${c.id}:db") {
                        sh 'while ! pg_isready -h db -U test_user; do sleep 1; done'
                    }

                    // Esecuzione Test Python
                    // NOTA: Esecuzione come root (-u 0:0) necessaria per pip install
                    docker.image('python:3.9').inside("--link ${c.id}:db -u 0:0") {
                        
                        echo "[${serviceDir}] Installazione delle dipendenze Python dal file requirements.txt..."
                        sh 'pip install -r requirements.txt'
                        
                        echo "[${serviceDir}] Esecuzione dei test unitari localizzati in tests/test_unit.py..."
                        // Iniezione della variabile d'ambiente per forzare l'uso del DB Sandbox
                        withEnv(['DATABASE_URL=postgresql://test_user:test_pass@db:5432/test_db']) {
                            sh 'pytest tests/test_unit.py'
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
                echo "[${serviceDir}] Creazione dell'immagine Docker..."
                sh "docker build -t ${DOCKER_USER}/${imageName}:${BUILD_NUMBER} ."
                
                echo "[${serviceDir}] Invio dell'immagine al registry Docker Hub..."
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
                echo "[${serviceDir}] Applicazione della configurazione Kubernetes..."
                sh "kubectl apply -f k8s/${serviceDir}.yaml"
                
                echo "[${serviceDir}] Aggiornamento dell'immagine di deployment..."
                sh "kubectl set image deployment/${k8sDeployName} ${k8sDeployName}=${DOCKER_USER}/${imageName}:${BUILD_NUMBER} --record"
                
                echo "[${serviceDir}] Verifica dello stato del rollout..."
                sh "kubectl rollout status deployment/${k8sDeployName} --timeout=60s"
            }
        }
    }
}
