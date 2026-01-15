pipeline {
    agent any

    environment {
        DOCKER_CREDS = 'dockerhub-id'
        K8S_CONFIG   = 'k8s-secret'
        DOCKER_USER  = 'claudia179'
    }

    stages {
        stage('Inizializzazione') {
            steps {
                echo "Inizio pipeline per user: ${DOCKER_USER}"
            }
        }

        stage('Build & Push Microservizi') {
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
    }
}

def processService(serviceDir, imageName, k8sDeployName) {
    stage("${serviceDir} - Test") {
        dir(serviceDir) {
            sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt || echo "Requirements skipped"
                
                # QUESTA È LA RIGA CHE MANCAVA:
                export PYTHONPATH=$PWD
                export FLASK_APP=app.py
                
                if [ -d "tests" ]; then pytest tests/ --junitxml=test-results.xml; fi
            '''
        }
    }

    stage("${serviceDir} - Docker") {
        script {
            dir(serviceDir) {
                docker.withRegistry('', DOCKER_CREDS) {
                    def img = docker.build("${DOCKER_USER}/${imageName}:${BUILD_NUMBER}")
                    img.push()
                    img.push('latest')
                }
            }
        }
    }
    
    stage("${serviceDir} - Deploy") {
        withCredentials([file(credentialsId: K8S_CONFIG, variable: 'KUBECONFIG')]) {
            script {
                sh """
                    kubectl set image deployment/${k8sDeployName} ${k8sDeployName}=${DOCKER_USER}/${imageName}:${BUILD_NUMBER} --record || echo "Deployment non ancora presente, salto aggiornamento."
                """
            }
        }
    }
}
