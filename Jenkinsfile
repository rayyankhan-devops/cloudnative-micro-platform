pipeline {
    agent { label 'dev' }

    options {
        skipDefaultCheckout(true)
    }

    stages {
        // Clone the code from the Git repository
        stage('Clone Code') {
            steps {
                echo 'Cloning code to Jenkins workspace'
                git branch: 'main',
                    url: 'https://github.com/rayyankhan-devops/cloudnative-micro-platform.git'
            }
        }
        // Gitleaks stage to detect secrets in the codebase
        stage('Gitleaks') {
            steps {
                sh '''
                    mkdir -p gitleaks

                    gitleaks detect \
                        --verbose \
                        --redact \
                        --source . \
                        --report-format json \
                        --report-path gitleaks/gitleaks-report.json || true

                    if [ -f gitleaks/gitleaks-report.json ] && [ "$(cat gitleaks/gitleaks-report.json | tr -d '[:space:]')" = "[]" ]; then
                        rm -f gitleaks/gitleaks-report.json
                        echo "No secrets found. Empty Gitleaks report removed."
                    else
                        echo "Gitleaks report contains findings or could not be generated."
                    fi  
                '''
            }
        }

        // Linting stage to check code quality for all services
        stage('Linting') {
            parallel {
                stage('Frontend Lint') {
                    steps {
                        dir('frontend') {
                            sh 'npm install'
                            sh 'npm run lint'
                        }
                    }
                }

                stage('Gateway Lint') {
                    steps {
                        dir('gateway') {
                            sh 'npm install'
                            sh 'npm run lint'
                        }
                    }
                }

                stage('Payment Service Lint') {
                    steps {
                        dir('services/payment-service') {
                            sh 'npm install'
                            sh 'npm run lint'
                        }
                    }
                }

                stage('Auth Service Lint') {
                    steps {
                        dir('services/auth-service') {
                            sh 'go mod download'
                            sh 'go vet ./...'
                        }
                    }
                }

                stage('Product Service Lint') {
                    steps {
                        dir('services/product-service') {
                            sh '''
                                python3 -m venv .venv
                                .venv/bin/python -m pip install --upgrade pip
                                .venv/bin/python -m pip install -r requirements.txt
                                PYTHONPATH=. .venv/bin/python -m pylint app/
                            '''
                        }
                    }
                }
            }
        }

        // Testing stage to run tests for all services
        stage('Testing') {
            parallel {
                stage('Frontend Tests') {
                    steps {
                        dir('frontend') {
                            sh 'npm test'
                        }
                    }
                }

                stage('Gateway Tests') {
                    steps {
                        dir('gateway') {
                            sh 'npm test'
                        }
                    }
                }

                stage('Payment Service Tests') {
                    steps {
                        dir('services/payment-service') {
                            sh 'npm test'
                        }
                    }
                }

                stage('Auth Service Tests') {
                    steps {
                        dir('services/auth-service') {
                            sh 'go test ./...'
                        }
                    }
                }

                stage('Product Service Tests') {
                    steps {
                        dir('services/product-service') {
                            sh 'PYTHONPATH=. .venv/bin/python -m pytest'
                        }
                    }
                }
            }
        }

        // SCA stage to perform Software Composition Analysis for all services
        stage('SCA') {
            parallel {
                stage('Frontend SCA') {
                    steps {
                        dir('frontend') {
                            sh '''
                                mkdir -p ${WORKSPACE}/sca-reports
                                npm audit --json > ${WORKSPACE}/sca-reports/frontend-audit.json 2>&1 || true
                                echo "--- Frontend npm audit summary ---"
                                npm audit || true
                            '''
                        }
                    }
                }

                stage('Gateway SCA') {
                    steps {
                        dir('gateway') {
                            sh '''
                                mkdir -p ${WORKSPACE}/sca-reports
                                npm audit --json > ${WORKSPACE}/sca-reports/gateway-audit.json 2>&1 || true
                                echo "--- Gateway npm audit summary ---"
                                npm audit || true
                            '''
                        }
                    }
                }

                stage('Payment Service SCA') {
                    steps {
                        dir('services/payment-service') {
                            sh '''
                                mkdir -p ${WORKSPACE}/sca-reports
                                npm audit --json > ${WORKSPACE}/sca-reports/payment-service-audit.json 2>&1 || true
                                echo "--- Payment Service npm audit summary ---"
                                npm audit || true
                            '''
                        }
                    }
                }

                stage('Auth Service SCA') {
                    steps {
                        dir('services/auth-service') {
                            sh '''
                                mkdir -p ${WORKSPACE}/sca-reports
                                govulncheck -json ./... > ${WORKSPACE}/sca-reports/auth-service-vulncheck.json 2>&1 || true
                                echo "--- Auth Service govulncheck summary ---"
                                govulncheck ./... || true
                            '''
                        }
                    }
                }

                stage('Product Service SCA') {
                    steps {
                        dir('services/product-service') {
                            sh '''
                                mkdir -p ${WORKSPACE}/sca-reports
                                .venv/bin/python -m pip install pip-audit --quiet
                                .venv/bin/python -m pip_audit -r requirements.txt -f json -o ${WORKSPACE}/sca-reports/product-service-audit.json || true
                                echo "--- Product Service pip-audit summary ---"
                                .venv/bin/python -m pip_audit -r requirements.txt || true
                            '''
                        }
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'sca-reports/**', allowEmptyArchive: true
                }
            }
        }

        // SonarQube static code analysis
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube Server') {
                    sh "${tool('SonarQube Server')}/bin/sonar-scanner"
                }
            }
        }

        // Quality Gate — waits for SonarQube webhook to report pass/fail
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        // Hadolint — Dockerfile linting for all services
        stage('Hadolint') {
            parallel {
                stage('Frontend Dockerfile') {
                    steps {
                        sh '''
                            mkdir -p ${WORKSPACE}/hadolint-reports
                            hadolint frontend/Dockerfile --format json > ${WORKSPACE}/hadolint-reports/frontend-hadolint.json || true
                            echo "--- Frontend Dockerfile ---"
                            hadolint frontend/Dockerfile || true
                        '''
                    }
                }

                stage('Gateway Dockerfile') {
                    steps {
                        sh '''
                            mkdir -p ${WORKSPACE}/hadolint-reports
                            hadolint gateway/Dockerfile --format json > ${WORKSPACE}/hadolint-reports/gateway-hadolint.json || true
                            echo "--- Gateway Dockerfile ---"
                            hadolint gateway/Dockerfile || true
                        '''
                    }
                }

                stage('Auth Service Dockerfile') {
                    steps {
                        sh '''
                            mkdir -p ${WORKSPACE}/hadolint-reports
                            hadolint services/auth-service/Dockerfile --format json > ${WORKSPACE}/hadolint-reports/auth-service-hadolint.json || true
                            echo "--- Auth Service Dockerfile ---"
                            hadolint services/auth-service/Dockerfile || true
                        '''
                    }
                }

                stage('Payment Service Dockerfile') {
                    steps {
                        sh '''
                            mkdir -p ${WORKSPACE}/hadolint-reports
                            hadolint services/payment-service/Dockerfile --format json > ${WORKSPACE}/hadolint-reports/payment-service-hadolint.json || true
                            echo "--- Payment Service Dockerfile ---"
                            hadolint services/payment-service/Dockerfile || true
                        '''
                    }
                }

                stage('Product Service Dockerfile') {
                    steps {
                        sh '''
                            mkdir -p ${WORKSPACE}/hadolint-reports
                            hadolint services/product-service/Dockerfile --format json > ${WORKSPACE}/hadolint-reports/product-service-hadolint.json || true
                            echo "--- Product Service Dockerfile ---"
                            hadolint services/product-service/Dockerfile || true
                        '''
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'hadolint-reports/**', allowEmptyArchive: true
                }
            }
        }
        // Build Docker images for all services
        stage('Build Docker Images') {
            steps {
                script {
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'dockerHubCreds',
                            usernameVariable: 'DOCKERHUB_USER',
                            passwordVariable: 'DOCKERHUB_PASS'
                        )
                    ]) {
                        parallel(
                            'Frontend Image': {
                                sh 'docker build -t $DOCKERHUB_USER/cloudnative-micro-platform:$BUILD_NUMBER -t $DOCKERHUB_USER/cloudnative-micro-platform:latest frontend/'
                            },
                            'Gateway Image': {
                                sh 'docker build -t $DOCKERHUB_USER/cloudnative-micro-gateway:$BUILD_NUMBER -t $DOCKERHUB_USER/cloudnative-micro-gateway:latest gateway/'
                            },
                            'Auth Service Image': {
                                sh 'docker build -t $DOCKERHUB_USER/cloudnative-micro-auth:$BUILD_NUMBER -t $DOCKERHUB_USER/cloudnative-micro-auth:latest services/auth-service/'
                            },
                            'Payment Service Image': {
                                sh 'docker build -t $DOCKERHUB_USER/cloudnative-micro-payment:$BUILD_NUMBER -t $DOCKERHUB_USER/cloudnative-micro-payment:latest services/payment-service/'
                            },
                            'Product Service Image': {
                                sh 'docker build -t $DOCKERHUB_USER/cloudnative-micro-product:$BUILD_NUMBER -t $DOCKERHUB_USER/cloudnative-micro-product:latest services/product-service/'
                            }
                        )
                    }
                }
            }
        }
        // Trivy image vulnerability scanning
        stage('Image Scanning (Trivy)') {
            steps {
                script {
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'dockerHubCreds',
                            usernameVariable: 'DOCKERHUB_USER',
                            passwordVariable: 'DOCKERHUB_PASS'
                        )
                    ]) {
                        sh 'mkdir -p ${WORKSPACE}/trivy-reports'
                        parallel(
                            'Frontend Image Scan': {
                                sh '''
                                    trivy image --format json --output ${WORKSPACE}/trivy-reports/frontend-trivy.json --severity HIGH,CRITICAL $DOCKERHUB_USER/cloudnative-micro-platform:$BUILD_NUMBER || true
                                    echo "--- Frontend Trivy Scan Summary ---"
                                    trivy image --severity HIGH,CRITICAL $DOCKERHUB_USER/cloudnative-micro-platform:$BUILD_NUMBER || true
                                '''
                            },
                            'Gateway Image Scan': {
                                sh '''
                                    trivy image --format json --output ${WORKSPACE}/trivy-reports/gateway-trivy.json --severity HIGH,CRITICAL $DOCKERHUB_USER/cloudnative-micro-gateway:$BUILD_NUMBER || true
                                    echo "--- Gateway Trivy Scan Summary ---"
                                    trivy image --severity HIGH,CRITICAL $DOCKERHUB_USER/cloudnative-micro-gateway:$BUILD_NUMBER || true
                                '''
                            },
                            'Auth Service Image Scan': {
                                sh '''
                                    trivy image --format json --output ${WORKSPACE}/trivy-reports/auth-service-trivy.json --severity HIGH,CRITICAL $DOCKERHUB_USER/cloudnative-micro-auth:$BUILD_NUMBER || true
                                    echo "--- Auth Service Trivy Scan Summary ---"
                                    trivy image --severity HIGH,CRITICAL $DOCKERHUB_USER/cloudnative-micro-auth:$BUILD_NUMBER || true
                                '''
                            },
                            'Payment Service Image Scan': {
                                sh '''
                                    trivy image --format json --output ${WORKSPACE}/trivy-reports/payment-service-trivy.json --severity HIGH,CRITICAL $DOCKERHUB_USER/cloudnative-micro-payment:$BUILD_NUMBER || true
                                    echo "--- Payment Service Trivy Scan Summary ---"
                                    trivy image --severity HIGH,CRITICAL $DOCKERHUB_USER/cloudnative-micro-payment:$BUILD_NUMBER || true
                                '''
                            },
                            'Product Service Image Scan': {
                                sh '''
                                    trivy image --format json --output ${WORKSPACE}/trivy-reports/product-service-trivy.json --severity HIGH,CRITICAL $DOCKERHUB_USER/cloudnative-micro-product:$BUILD_NUMBER || true
                                    echo "--- Product Service Trivy Scan Summary ---"
                                    trivy image --severity HIGH,CRITICAL $DOCKERHUB_USER/cloudnative-micro-product:$BUILD_NUMBER || true
                                '''
                            }
                        )
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-reports/**', allowEmptyArchive: true
                }
            }
        }
        // Push Docker images to Docker Hub
        stage('Push Docker Images') {
            steps {
                script {
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'dockerHubCreds',
                            usernameVariable: 'DOCKERHUB_USER',
                            passwordVariable: 'DOCKERHUB_PASS'
                        )
                    ]) {
                        sh 'echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin'
                        parallel(
                            'Frontend Image Push': {
                                sh '''
                                    docker push $DOCKERHUB_USER/cloudnative-micro-platform:$BUILD_NUMBER
                                    docker push $DOCKERHUB_USER/cloudnative-micro-platform:latest
                                '''
                            },
                            'Gateway Image Push': {
                                sh '''
                                    docker push $DOCKERHUB_USER/cloudnative-micro-gateway:$BUILD_NUMBER
                                    docker push $DOCKERHUB_USER/cloudnative-micro-gateway:latest
                                '''
                            },
                            'Auth Service Image Push': {
                                sh '''
                                    docker push $DOCKERHUB_USER/cloudnative-micro-auth:$BUILD_NUMBER
                                    docker push $DOCKERHUB_USER/cloudnative-micro-auth:latest
                                '''
                            },
                            'Payment Service Image Push': {
                                sh '''
                                    docker push $DOCKERHUB_USER/cloudnative-micro-payment:$BUILD_NUMBER
                                    docker push $DOCKERHUB_USER/cloudnative-micro-payment:latest
                                '''
                            },
                            'Product Service Image Push': {
                                sh '''
                                    docker push $DOCKERHUB_USER/cloudnative-micro-product:$BUILD_NUMBER
                                    docker push $DOCKERHUB_USER/cloudnative-micro-product:latest
                                '''
                            }
                        )
                    }
                }
            }
            post {
                always {
                    sh 'docker logout || true'
                }
            }
        }
        // Continuous Deployment via Docker Compose
        stage('Deploy') {
            steps {
                echo 'Deploying application stack via Docker Compose...'
                sh '''
                    # Ensure .env exists
                    if [ ! -f .env ]; then
                        cp .env.example .env
                    fi

                    # Deploy and recreate containers
                    docker compose up -d --remove-orphans --force-recreate

                    # Display running container status
                    sleep 10
                    docker compose ps
                '''
            }
        }

        // Dynamic Application Security Testing (DAST) via OWASP ZAP
        stage('OWASP ZAP DAST Scan') {
            steps {
                echo 'Preparing OWASP ZAP scanner...'
                sh '''
                    mkdir -p ${WORKSPACE}/zap-reports
                    chmod 777 ${WORKSPACE}/zap-reports

                    # Clean dangling build images to free disk space
                    docker image prune -f || true

                    # Pre-pull lightweight ZAP image once (prevents concurrent disk exhaustion)
                    docker pull ghcr.io/zaproxy/zaproxy:bare
                '''
                script {
                    parallel(
                        'Frontend DAST Scan': {
                            sh '''
                                docker run --rm --network=host \
                                  -v ${WORKSPACE}/zap-reports:/zap/wrk/:rw \
                                  -t ghcr.io/zaproxy/zaproxy:bare \
                                  zap-baseline.py -t http://100.55.149.140:3000 -r frontend_zap_report.html -J frontend_zap_report.json -I || true
                            '''
                        },
                        'API Gateway DAST Scan': {
                            sh '''
                                docker run --rm --network=host \
                                  -v ${WORKSPACE}/zap-reports:/zap/wrk/:rw \
                                  -t ghcr.io/zaproxy/zaproxy:bare \
                                  zap-baseline.py -t http://100.55.149.140:8000 -r gateway_zap_report.html -J gateway_zap_report.json -I || true
                            '''
                        },
                        'Product API DAST Scan': {
                            sh '''
                                docker run --rm --network=host \
                                  -v ${WORKSPACE}/zap-reports:/zap/wrk/:rw \
                                  -t ghcr.io/zaproxy/zaproxy:bare \
                                  zap-api-scan.py -t http://100.55.149.140:8002/openapi.json -f openapi -r product_api_zap_report.html -J product_api_zap_report.json -I || true
                            '''
                        }
                    )
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'zap-reports/**', allowEmptyArchive: true
                }
            }
        }
    }
}