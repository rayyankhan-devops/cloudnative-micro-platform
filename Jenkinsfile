pipeline{
    agent { label "dev" }

    stages{
        stage("Clone Code") {
            steps{
                echo "Cloning Code to jenkings workspace"
                git url: 'https://github.com/rayyankhan-devops/cloudnative-micro-platform.git', branch: 'main'
            }
        }
        stage("linting") {
            steps{
                echo "Running linting checks"
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
            }
        }
    }
}