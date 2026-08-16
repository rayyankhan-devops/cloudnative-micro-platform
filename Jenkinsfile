pipeline{
    agent { label "dev" }

    stages{
        stage("Clone Code") {
            steps{
                echo "Cloning Code to jenkings workspace"
                git url: 'https://github.com/rayyankhan-devops/cloudnative-micro-platform.git', branch: 'main'
            }
        }
    }
}