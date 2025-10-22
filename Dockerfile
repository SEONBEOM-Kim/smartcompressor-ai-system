# Node.js 18 Alpine 이미지 사용 (가벼움)
FROM node:18-alpine

# 작업 디렉토리 설정
WORKDIR /app

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치
RUN npm install

# 프로젝트 파일들 복사
COPY . .

# 포트 3000 노출
EXPOSE 3000

# 서버 실행
CMD ["node", "server/app.js"]
