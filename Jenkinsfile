pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'
        DOCKER_IMAGE = 'cithit/tewelljd'
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/tewelljd-cloud/225-lab3-7.git'
        KUBECONFIG = credentials('tewelljd-fl26')
        TARGET_URL = 'http://10.48.229.171'
    }

    stages {
        stage('Checkout') {
            steps {
                cleanWs()
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[url: "${GITHUB_URL}"]]
                ])
            }
        }

        stage('Lint HTML') {
            steps {
                sh 'npm install htmlhint --save-dev'
                sh 'npx htmlhint *.html'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.withRegistry(
                        'https://registry-1.docker.io',
                        "${DOCKER_CREDENTIALS_ID}"
                    ) {
                        docker.build(
                            "${DOCKER_IMAGE}:${IMAGE_TAG}",
                            "-f Dockerfile.build ."
                        )
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry(
                        'https://index.docker.io/v1/',
                        "${DOCKER_CREDENTIALS_ID}"
                    ) {
                        docker.image(
                            "${DOCKER_IMAGE}:${IMAGE_TAG}"
                        ).push()
                    }
                }
            }
        }

        stage('Deploy to Dev Environment') {
            steps {
                sh '''
                    sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${IMAGE_TAG}|" deployment-dev.yaml
                    kubectl apply -f deployment-dev.yaml
                    kubectl rollout status deployment/dev-deployment --timeout=180s
                '''
            }
        }

        stage('Run Acceptance Tests') {
            steps {
                script {
                    sh 'docker stop qa-tests || true'
                    sh 'docker rm qa-tests || true'
                    sh 'docker build -t qa-tests -f Dockerfile.test .'
                    sh 'docker run --rm qa-tests'
                }
            }
        }

        stage('Run Security Checks') {
            steps {
                sh 'docker pull public.ecr.aws/portswigger/dastardly:latest'
                sh '''
                    docker run --user $(id -u) \
                        -v ${WORKSPACE}:${WORKSPACE}:rw \
                        -e BURP_START_URL=${TARGET_URL} \
                        -e BURP_REPORT_FILE_PATH=${WORKSPACE}/dastardly-report.xml \
                        public.ecr.aws/portswigger/dastardly:latest
                '''
            }
        }

        stage('Deploy to Prod Environment') {
            steps {
                sh '''
                    sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${IMAGE_TAG}|" deployment-prod.yaml

                    echo "=== Recreating production deployment ==="
                    kubectl delete deployment prod-deployment --ignore-not-found=true
                    kubectl apply -f deployment-prod.yaml
                    kubectl rollout status deployment/prod-deployment --timeout=180s
                '''
            }
        }

        stage('Check Kubernetes Cluster') {
            steps {
                sh 'kubectl get all'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'dastardly-report.xml',
                             allowEmptyArchive: true

            junit testResults: 'dastardly-report.xml',
                  skipPublishingChecks: true,
                  allowEmptyResults: true
        }

        success {
            slackSend(
                color: 'good',
                message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
            )
        }

        unstable {
            slackSend(
                color: 'warning',
                message: "Build Unstable: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
            )
        }

        failure {
            slackSend(
                color: 'danger',
                message: "Build Failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
            )
        }
    }
}
