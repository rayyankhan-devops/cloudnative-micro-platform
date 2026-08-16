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
                                sh 'docker build -t $DOCKERHUB_USER/cloudnative-micro-platform:$BUILD_NUMBER frontend/'
                            },
                            'Gateway Image': {
                                sh 'docker build -t $DOCKERHUB_USER/cloudnative-micro-gateway:$BUILD_NUMBER gateway/'
                            },
                            'Auth Service Image': {
                                sh 'docker build -t $DOCKERHUB_USER/cloudnative-micro-auth:$BUILD_NUMBER services/auth-service/'
                            },
                            'Payment Service Image': {
                                sh 'docker build -t $DOCKERHUB_USER/cloudnative-micro-payment:$BUILD_NUMBER services/payment-service/'
                            },
                            'Product Service Image': {
                                sh 'docker build -t $DOCKERHUB_USER/cloudnative-micro-product:$BUILD_NUMBER services/product-service/'
                            }
                        )
                    }
                }
            }
        }
    }
}