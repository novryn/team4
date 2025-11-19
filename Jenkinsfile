pipeline {
    agent any
    
    environment {
        IMAGE_NAME = "qa-test-image"
        CONTAINER_NAME = "qa-test-container"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '📦 코드 체크아웃'
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '🐳 Docker 이미지 빌드'
                script {
                    // 기존 컨테이너/이미지 삭제
                    bat "docker rm -f %CONTAINER_NAME% 2>nul || echo Container not found"
                    bat "docker rmi -f %IMAGE_NAME% 2>nul || echo Image not found"
                    
                    // 새 이미지 빌드
                    bat "docker build -t %IMAGE_NAME% ."
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo '🧪 테스트 실행'
                script {
                    bat "docker run --name %CONTAINER_NAME% -v %cd%:/workspace %IMAGE_NAME% pytest tests/ --html=report.html --self-contained-html"
                }
            }
        }
        
        stage('Collect Results') {
            steps {
                echo '📊 테스트 결과 수집'
                publishHTML([
                    reportDir: '.',
                    reportFiles: 'report.html',
                    reportName: 'Test Report'
                ])
            }
        }
    }
    
    post {
        always {
            echo '🧹 정리'
            bat "docker rm -f %CONTAINER_NAME% 2>nul || echo Already removed"
        }
        success {
            echo '✅ 테스트 성공!'
        }
        failure {
            echo '❌ 테스트 실패!'
        }
    }
}