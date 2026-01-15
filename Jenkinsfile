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
    stage("${serviceDir} - Build & Push") {
        dir(serviceDir) {
            withDockerRegistry(credentialsId: 'dockerhub-id', url: 'https://index.docker.io/v1/') {
                // Build dell'immagine
                sh "docker build -t ${DOCKER_USER}/${imageName}:${BUILD_NUMBER} ."
                sh "docker push ${DOCKER_USER}/${imageName}:${BUILD_NUMBER}"
                
                // Aggiorna anche il tag 'latest' per comodità
                sh "docker tag ${DOCKER_USER}/${imageName}:${BUILD_NUMBER} ${DOCKER_USER}/${imageName}:latest"
                sh "docker push ${DOCKER_USER}/${imageName}:latest"
            }
        }
    }

    stage("${serviceDir} - Deploy") {
        withCredentials([file(credentialsId: 'k8s-secret', variable: 'KUBECONFIG')]) {
            script {
                // 1. Applica la configurazione (Crea deployment/service se non esistono)
                // Legge il file dalla cartella k8s/ che hai appena creato
                sh "kubectl apply -f k8s/${serviceDir}.yaml"
                
                // 2. Forza l'aggiornamento all'immagine appena buildata (tag BUILD_NUMBER)
                sh "kubectl set image deployment/${k8sDeployName} ${k8sDeployName}=${DOCKER_USER}/${imageName}:${BUILD_NUMBER} --record"
            }
        }
    }
}
