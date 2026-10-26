pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'cithit/tewelljd'
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'
        GITHUB_URL = 'https://github.com/tewelljd-cloud/225-lab3-7.git'
        KUBECONFIG = credentials('tewelljd-fl26')
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        TARGET_URL = 'http://10.48.229.171'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: "${GITHUB_URL}"
            }
        }

        stage('Lint HTML') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$WORKSPACE:/work" \
                      -w /work \
                      node:alpine \
                      sh -c "npx --yes html-validate index.html"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      -f Dockerfile.build \
                      -t ${DOCKER_IMAGE}:${IMAGE_TAG} \
                      -t ${DOCKER_IMAGE}:latest \
                      .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: "${DOCKER_CREDENTIALS_ID}",
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login \
                          -u "$DOCKER_USER" --password-stdin

                        docker push ${DOCKER_IMAGE}:${IMAGE_TAG}
                        docker push ${DOCKER_IMAGE}:latest

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Dev Environment') {
            steps {
                sh '''
                    sed -i "s|image: .*|image: ${DOCKER_IMAGE}:${IMAGE_TAG}|" deployment-dev.yaml

                    kubectl apply -f deployment-dev.yaml
                    kubectl rollout status deployment/dev-deployment \
                      --timeout=180s
                '''
            }
        }

        stage('Inspect Dev Services') {
            steps {
                sh '''
                    echo "=== Deployments ==="
                    kubectl get deployments

                    echo "=== Pods ==="
                    kubectl get pods -o wide

                    echo "=== Services ==="
                    kubectl get services

                    echo "=== dev-service endpoints ==="
                    kubectl get endpoints dev-service -o wide

                    echo "=== pods and labels ==="
                    kubectl get pods --show-labels -o wide

                    echo "=== Ingress ==="
                    kubectl get ingress
                '''
            }
        }

        stage('Run Acceptance Tests') {
            steps {
                sh '''
                    docker build \
                      -f Dockerfile.test \
                      -t lab3-7-acceptance-tests \
                      .

                    docker run --rm \
                      --network host \
                      -e TARGET_URL=${TARGET_URL} \
                      lab3-7-acceptance-tests
                '''
            }
        }

        stage('Run Security Checks') {
            steps {
                sh '''
                    docker pull public.ecr.aws/portswigger/dastardly:latest

                    docker run --user $(id -u) \
                      -v "${WORKSPACE}:${WORKSPACE}:rw" \
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

                    kubectl apply -f deployment-prod.yaml
                '''
            }
        }

        stage('Check Kubernetes Cluster') {
            steps {
                sh '''
                    echo "=== Nodes ==="
                    kubectl get nodes

                    echo "=== All Pods ==="
                    kubectl get pods -A

                    echo "=== All Services ==="
                    kubectl get services -A

                    echo "=== Deployments ==="
                    kubectl get deployments
                '''
            }
        }
    }

    post {
        always {
            junit testResults: '**/test-results.xml',
                  allowEmptyResults: true

            archiveArtifacts artifacts: 'dastardly-report.xml',
                             allowEmptyArchive: true
        }

        success {
            echo 'Lab 3.7 pipeline completed successfully.'
        }

        unstable {
            echo 'The pipeline is unstable. Review the test and security reports.'
        }

        failure {
            echo 'The pipeline failed. Review Console Output for the failing stage.'
        }
    }
}
