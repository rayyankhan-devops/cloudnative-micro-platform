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
    }
}