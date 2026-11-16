pipeline {
    agent any

    triggers {
        pollSCM('H/5 * * * *')
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        COMPOSE_PROJECT_NAME = "itr-ci-${BUILD_NUMBER}"
        POSTGRES_DB = "itr_db"
        POSTGRES_USER = "itr_user"
        POSTGRES_PASSWORD = "ci_test_password"
        DB_NAME = "itr_db"
        DB_USER = "itr_user"
        DB_PASSWORD = "ci_test_password"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'echo "Commit evaluado:" && git rev-parse --short HEAD'
            }
        }

        stage('Build') {
            steps {
                sh '''
                    docker compose -f docker-compose.ci.yml \
                      -p "$COMPOSE_PROJECT_NAME" build itr_app db
                '''
            }
        }

        stage('Integration Test') {
            steps {
                sh '''
                    docker compose -f docker-compose.ci.yml \
                      -p "$COMPOSE_PROJECT_NAME" up -d --wait db itr_app

                    docker compose -f docker-compose.ci.yml \
                      -p "$COMPOSE_PROJECT_NAME" run --rm --no-deps \
                      itr_app python ITR_V1/check_db.py
                '''
            }
        }
    }

    post {
        always {
            sh '''
                docker compose -f docker-compose.ci.yml \
                  -p "$COMPOSE_PROJECT_NAME" down --volumes --remove-orphans || true
            '''
        }

        success {
            echo 'CI EXITOSO: construcción y prueba de integración completadas.'
        }

        failure {
            echo 'CI FALLIDO: revisar la consola para identificar el error.'
        }
    }
}
