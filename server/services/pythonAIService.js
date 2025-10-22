const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class PythonAIService {
    constructor() {
        this.pythonPath = 'python'; // 또는 'python3'
        this.scriptPath = path.join(__dirname, '../../ai/ai_cli.py');
        this.isAvailable = false;
        this.checkPythonAvailability();
    }

    async checkPythonAvailability() {
        try {
            const result = await this.runPythonScript('--version');
            this.isAvailable = true;
            console.log('✅ Python AI 서비스 사용 가능');
        } catch (error) {
            console.log('❌ Python AI 서비스 사용 불가:', error.message);
            this.isAvailable = false;
        }
    }

    async runPythonScript(args, inputData = null) {
        return new Promise((resolve, reject) => {
            const python = spawn(this.pythonPath, [this.scriptPath, ...args], {
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let stdout = '';
            let stderr = '';

            python.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            python.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            python.on('close', (code) => {
                if (code === 0) {
                    try {
                        const result = JSON.parse(stdout);
                        resolve(result);
                    } catch (e) {
                        resolve({ success: true, output: stdout });
                    }
                } else {
                    reject(new Error(`Python script failed: ${stderr}`));
                }
            });

            if (inputData) {
                python.stdin.write(JSON.stringify(inputData));
                python.stdin.end();
            }
        });
    }

    async analyzeAudio(audioFilePath) {
        if (!this.isAvailable) {
            return {
                success: false,
                error: 'Python AI 서비스가 사용 불가능합니다.'
            };
        }

        try {
            const result = await this.runPythonScript(['--analyze', audioFilePath]);
            return {
                success: true,
                result: result
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async collectFieldData(data) {
        if (!this.isAvailable) {
            return {
                success: false,
                error: 'Python AI 서비스가 사용 불가능합니다.'
            };
        }

        try {
            const result = await this.runPythonScript(['--collect-data'], data);
            return {
                success: true,
                result: result
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    getStatus() {
        return {
            available: this.isAvailable,
            pythonPath: this.pythonPath,
            scriptPath: this.scriptPath
        };
    }
}

module.exports = new PythonAIService();
