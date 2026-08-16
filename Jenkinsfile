pipeline {
    agent { label 'dev' }

    options {
        skipDefaultCheckout(true)
    }

    stages {
        stage('Clone Code') {
            steps {
                echo 'Cloning code to Jenkins workspace'
                git branch: 'main',
                    url: 'https://github.com/rayyankhan-devops/cloudnative-micro-platform.git'
            }
        }

        stage('Linting') {
            steps {
                echo 'Running linting checks'

                dir('frontend') {
                    sh 'npm install'
                    sh 'npm run lint'
                }

                dir('gateway') {
                    sh 'npm install'
                    sh 'npm run lint'
                }

                dir('services/payment-service') {
                    sh 'npm install'
                    sh 'npm run lint'
                }

                dir('services/auth-service') {
                    sh 'go mod download'
                    sh 'go vet ./...'
                }

                dir('services/product-service') {
                    sh '''
                        python3 -m venv .venv
                        .venv/bin/python -m pip install --upgrade pip
                        .venv/bin/python -m pip install -r requirements.txt
                        PYTHONPATH=.venv/bin/python -m pylint app/
                    '''
                }
            }
        }

        stage('Testing') {
            steps {
                echo 'Running test checks'

                dir('frontend') {
                    sh 'npm test'
                }

                dir('gateway') {
                    sh 'npm test'
                }

                dir('services/payment-service') {
                    sh 'npm test'
                }

                dir('services/auth-service') {
                    sh 'go test ./...'
                }

                dir('services/product-service') {
                    sh 'PYTHONPATH=. .venv/bin/python -m pytest'
                }
            }
        }
    }
}