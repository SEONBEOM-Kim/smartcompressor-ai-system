const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();
const PORT = 3001;

// 미들웨어 설정
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'static')));

// 업로드 디렉토리 생성
const uploadDir = path.join(__dirname, 'data', 'real_audio_uploads');
const augmentedDir = path.join(__dirname, 'data', 'augmented_audio');
const processedDir = path.join(__dirname, 'data', 'processed_audio');

[uploadDir, augmentedDir, processedDir].forEach(dir => {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
});

// Multer 설정 (오디오 파일 업로드)
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const originalName = file.originalname.replace(/\.[^/.]+$/, '');
        cb(null, `real_${timestamp}_${originalName}.wav`);
    }
});

const upload = multer({
    storage: storage,
    fileFilter: (req, file, cb) => {
        const allowedTypes = ['audio/wav', 'audio/mp3', 'audio/m4a', 'audio/ogg'];
        if (allowedTypes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error('오디오 파일만 업로드 가능합니다. (wav, mp3, m4a, ogg)'), false);
        }
    },
    limits: {
        fileSize: 50 * 1024 * 1024 // 50MB 제한
    }
});

// 메인 페이지
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'static', 'data_upload_interface.html'));
});

// 데이터 업로드 페이지
app.get('/upload', (req, res) => {
    res.sendFile(path.join(__dirname, 'static', 'data_upload_interface.html'));
});

// 오디오 파일 업로드 API
app.post('/api/upload/audio', upload.single('audioFile'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ success: false, message: '파일이 선택되지 않았습니다.' });
        }

        const fileInfo = {
            id: Date.now(),
            originalName: req.file.originalname,
            fileName: req.file.filename,
            filePath: req.file.path,
            fileSize: req.file.size,
            uploadTime: new Date().toISOString(),
            status: 'uploaded'
        };

        console.log('오디오 파일 업로드 완료:', fileInfo);
        res.json({ success: true, data: fileInfo });

    } catch (error) {
        console.error('업로드 오류:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 업로드된 파일 목록 조회
app.get('/api/upload/files', (req, res) => {
    try {
        const files = fs.readdirSync(uploadDir)
            .filter(file => file.endsWith('.wav') || file.endsWith('.mp3') || file.endsWith('.m4a') || file.endsWith('.ogg'))
            .map(file => {
                const filePath = path.join(uploadDir, file);
                const stats = fs.statSync(filePath);
                return {
                    fileName: file,
                    fileSize: stats.size,
                    uploadTime: stats.birthtime.toISOString(),
                    filePath: filePath
                };
            })
            .sort((a, b) => new Date(b.uploadTime) - new Date(a.uploadTime));

        res.json({ success: true, files });
    } catch (error) {
        console.error('파일 목록 조회 오류:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 간단한 데이터 증강 (Node.js로 구현)
app.post('/api/augment/:fileName', async (req, res) => {
    try {
        const { fileName } = req.params;
        const { augmentCount = 10, label = 'unknown' } = req.body;
        
        const sourceFile = path.join(uploadDir, fileName);
        if (!fs.existsSync(sourceFile)) {
            return res.status(404).json({ success: false, message: '파일을 찾을 수 없습니다.' });
        }

        console.log(`데이터 증강 시작: ${fileName} -> ${augmentCount}개`);

        // 간단한 파일 복사 기반 증강 (실제로는 더 복잡한 오디오 처리가 필요)
        const augmentedFiles = [];
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        
        for (let i = 0; i < augmentCount; i++) {
            try {
                // 원본 파일 읽기
                const originalData = fs.readFileSync(sourceFile);
                
                // 간단한 변형 (실제로는 오디오 처리 라이브러리 필요)
                const augmentedData = Buffer.from(originalData);
                
                // 파일명 생성
                const augmentedFileName = `${label}_augmented_${timestamp}_${i + 1}.wav`;
                const augmentedFilePath = path.join(augmentedDir, augmentedFileName);
                
                // 파일 저장
                fs.writeFileSync(augmentedFilePath, augmentedData);
                
                augmentedFiles.push({
                    fileName: augmentedFileName,
                    filePath: augmentedFilePath,
                    originalFile: fileName,
                    augmentationType: 'copy_based',
                    createdTime: new Date().toISOString()
                });
                
                console.log(`증강 완료 (${i + 1}/${augmentCount}): ${augmentedFileName}`);
                
            } catch (error) {
                console.error(`증강 실패 (${i + 1}/${augmentCount}):`, error);
                continue;
            }
        }

        console.log(`데이터 증강 완료: ${augmentedFiles.length}/${augmentCount}개 파일 생성`);
        
        res.json({ 
            success: true, 
            message: `${augmentedFiles.length}개의 증강 데이터가 생성되었습니다.`,
            augmentedFiles: augmentedFiles
        });

    } catch (error) {
        console.error('데이터 증강 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '데이터 증강 실패: ' + error.message
        });
    }
});

// 증강된 데이터 목록 조회
app.get('/api/augment/files', (req, res) => {
    try {
        const files = fs.readdirSync(augmentedDir)
            .filter(file => file.endsWith('.wav'))
            .map(file => {
                const filePath = path.join(augmentedDir, file);
                const stats = fs.statSync(filePath);
                return {
                    fileName: file,
                    fileSize: stats.size,
                    createdTime: stats.birthtime.toISOString(),
                    filePath: filePath
                };
            })
            .sort((a, b) => new Date(b.createdTime) - new Date(a.createdTime));

        res.json({ success: true, files });
    } catch (error) {
        console.error('증강 파일 목록 조회 오류:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 파일 삭제 API
app.delete('/api/upload/:fileName', (req, res) => {
    try {
        const { fileName } = req.params;
        const filePath = path.join(uploadDir, fileName);
        
        if (fs.existsSync(filePath)) {
            fs.unlinkSync(filePath);
            console.log('파일 삭제 완료:', fileName);
            res.json({ success: true, message: '파일이 삭제되었습니다.' });
        } else {
            res.status(404).json({ success: false, message: '파일을 찾을 수 없습니다.' });
        }
    } catch (error) {
        console.error('파일 삭제 오류:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 통계 API
app.get('/api/stats', (req, res) => {
    try {
        const uploadedFiles = fs.readdirSync(uploadDir)
            .filter(file => file.endsWith('.wav') || file.endsWith('.mp3') || file.endsWith('.m4a') || file.endsWith('.ogg'));
        
        const augmentedFiles = fs.readdirSync(augmentedDir)
            .filter(file => file.endsWith('.wav'));
        
        const totalUploadSize = uploadedFiles.reduce((sum, file) => {
            const filePath = path.join(uploadDir, file);
            const stats = fs.statSync(filePath);
            return sum + stats.size;
        }, 0);
        
        const totalAugmentedSize = augmentedFiles.reduce((sum, file) => {
            const filePath = path.join(augmentedDir, file);
            const stats = fs.statSync(filePath);
            return sum + stats.size;
        }, 0);
        
        res.json({
            success: true,
            stats: {
                uploadedFiles: uploadedFiles.length,
                augmentedFiles: augmentedFiles.length,
                totalUploadSize: totalUploadSize,
                totalAugmentedSize: totalAugmentedSize,
                totalSize: totalUploadSize + totalAugmentedSize
            }
        });
    } catch (error) {
        console.error('통계 조회 오류:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// 서버 시작
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 데이터 업로드 서버가 http://localhost:${PORT} 에서 실행 중입니다`);
    console.log(`📁 업로드 디렉토리: ${uploadDir}`);
    console.log(`🔄 증강 데이터 디렉토리: ${augmentedDir}`);
    console.log(`📊 업로드 인터페이스: http://localhost:${PORT}/upload`);
});

// 에러 처리
process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});
