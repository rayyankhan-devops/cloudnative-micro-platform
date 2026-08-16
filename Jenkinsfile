pipeline {
    agent { label 'dev' }
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
                    sh 'npm i'
                    sh 'npm run lint'
                }

                dir('gateway') {
                    sh 'npm i'
                    sh 'npm run lint'
                }

                dir('services/payment-service') {
                    sh 'npm i'
                    sh 'npm run lint'
                }

                dir('services/auth-service') {
                    sh 'go mod download'
                    sh 'go vet ./...'
                }

                dir('services/product-service') {
                    sh 'python3 -m pip install --upgrade pip'
                    sh 'python3 -m pip install -r requirements.txt'
                    sh 'PYTHONPATH=. python3 -m pylint app/'
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
                    sh 'PYTHONPATH=. python3 -m pytest'
                }
            }
        }
    }
}