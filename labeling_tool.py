#!/usr/bin/env python3
"""
전문가 라벨링 GUI (labeling_tool.py)
Streamlit을 사용한 스펙트로그램 라벨링 도구입니다.
"""

import streamlit as st
import os
import shutil
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LabelingTool:
    """전문가 라벨링 도구 클래스"""
    
    def __init__(self):
        self.labels = {
            "정상 가동음": "normal",
            "냉기 누설 신호": "leak", 
            "과부하 신호": "overload"
        }
        self.labeled_dir = Path("labeled_data")
        self.unlabeled_dir = None
        self.current_image_index = 0
        self.image_files = []
        
    def setup_directories(self):
        """라벨링 디렉토리 구조 설정"""
        # 라벨별 디렉토리 생성
        for label_name in self.labels.keys():
            label_dir = self.labeled_dir / self.labels[label_name]
            label_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("라벨링 디렉토리 구조 설정 완료")
    
    def load_images(self, input_dir):
        """이미지 파일들을 로드합니다."""
        self.unlabeled_dir = Path(input_dir)
        
        if not self.unlabeled_dir.exists():
            st.error(f"입력 디렉토리를 찾을 수 없습니다: {input_dir}")
            return False
        
        # 지원하는 이미지 확장자
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        
        # 이미지 파일 목록 생성
        self.image_files = []
        for ext in image_extensions:
            self.image_files.extend(list(self.unlabeled_dir.glob(f"*{ext}")))
            self.image_files.extend(list(self.unlabeled_dir.glob(f"*{ext.upper()}")))
        
        self.image_files.sort()  # 파일명 순으로 정렬
        
        if not self.image_files:
            st.error(f"입력 디렉토리에 이미지 파일이 없습니다: {input_dir}")
            return False
        
        logger.info(f"총 {len(self.image_files)}개의 이미지를 로드했습니다.")
        return True
    
    def display_image(self, image_path):
        """이미지를 화면에 표시합니다."""
        try:
            # 이미지 로드 및 표시
            img = mpimg.imread(image_path)
            
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.imshow(img, cmap='magma')
            ax.set_title(f"스펙트로그램: {image_path.name}", fontsize=16, fontweight='bold')
            ax.axis('off')
            
            # Streamlit에 표시
            st.pyplot(fig)
            plt.close(fig)
            
        except Exception as e:
            st.error(f"이미지 로드 중 오류 발생: {e}")
            logger.error(f"이미지 로드 오류: {e}")
    
    def move_to_labeled_folder(self, image_path, label):
        """이미지를 라벨링된 폴더로 이동합니다."""
        try:
            if label not in self.labels:
                st.error(f"잘못된 라벨입니다: {label}")
                return False
            
            # 대상 디렉토리
            target_dir = self.labeled_dir / self.labels[label]
            
            # 파일명에 타임스탬프 추가 (중복 방지)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{timestamp}_{image_path.name}"
            target_path = target_dir / new_filename
            
            # 파일 이동
            shutil.move(str(image_path), str(target_path))
            
            logger.info(f"이미지 이동 완료: {image_path.name} -> {target_dir.name}/{new_filename}")
            return True
            
        except Exception as e:
            st.error(f"파일 이동 중 오류 발생: {e}")
            logger.error(f"파일 이동 오류: {e}")
            return False
    
    def run_labeling_interface(self, input_dir):
        """라벨링 인터페이스를 실행합니다."""
        st.set_page_config(
            page_title="스펙트로그램 라벨링 도구",
            page_icon="🎵",
            layout="wide"
        )
        
        st.title("🎵 스펙트로그램 전문가 라벨링 도구")
        st.markdown("---")
        
        # 디렉토리 설정
        self.setup_directories()
        
        # 이미지 로드
        if not self.load_images(input_dir):
            return
        
        # 사이드바 - 진행 상황
        with st.sidebar:
            st.header("📊 진행 상황")
            total_images = len(self.image_files)
            remaining_images = len([f for f in self.image_files if f.exists()])
            progress = (total_images - remaining_images) / total_images if total_images > 0 else 0
            
            st.progress(progress)
            st.metric("전체 이미지", total_images)
            st.metric("남은 이미지", remaining_images)
            st.metric("완료율", f"{progress:.1%}")
            
            st.markdown("---")
            st.header("🏷️ 라벨 설명")
            for label_name, label_key in self.labels.items():
                st.write(f"**{label_name}** ({label_key})")
                if label_key == "normal":
                    st.caption("정상적인 압축기 가동음")
                elif label_key == "leak":
                    st.caption("냉매 누설로 인한 이상 신호")
                elif label_key == "overload":
                    st.caption("과부하 상태의 이상 신호")
        
        # 메인 영역
        if remaining_images == 0:
            st.success("🎉 모든 이미지 라벨링이 완료되었습니다!")
            
            # 라벨링 결과 통계
            st.header("📈 라벨링 결과 통계")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                normal_count = len(list((self.labeled_dir / "normal").glob("*")))
                st.metric("정상 가동음", normal_count)
            
            with col2:
                leak_count = len(list((self.labeled_dir / "leak").glob("*")))
                st.metric("냉기 누설 신호", leak_count)
            
            with col3:
                overload_count = len(list((self.labeled_dir / "overload").glob("*")))
                st.metric("과부하 신호", overload_count)
            
            return
        
        # 현재 이미지 찾기
        current_image = None
        for i, img_path in enumerate(self.image_files):
            if img_path.exists():
                current_image = img_path
                self.current_image_index = i
                break
        
        if current_image is None:
            st.error("라벨링할 이미지를 찾을 수 없습니다.")
            return
        
        # 현재 이미지 정보
        st.header(f"📸 현재 이미지: {current_image.name}")
        st.caption(f"진행률: {self.current_image_index + 1}/{total_images}")
        
        # 이미지 표시
        self.display_image(current_image)
        
        # 라벨링 버튼들
        st.markdown("---")
        st.header("🏷️ 라벨 선택")
        st.write("아래 버튼 중 하나를 클릭하여 현재 이미지를 라벨링하세요:")
        
        # 3개 컬럼으로 버튼 배치
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ 정상 가동음", key="normal", use_container_width=True, type="primary"):
                if self.move_to_labeled_folder(current_image, "정상 가동음"):
                    st.success("정상 가동음으로 라벨링되었습니다!")
                    st.rerun()
        
        with col2:
            if st.button("⚠️ 냉기 누설 신호", key="leak", use_container_width=True, type="secondary"):
                if self.move_to_labeled_folder(current_image, "냉기 누설 신호"):
                    st.success("냉기 누설 신호로 라벨링되었습니다!")
                    st.rerun()
        
        with col3:
            if st.button("🚨 과부하 신호", key="overload", use_container_width=True, type="secondary"):
                if self.move_to_labeled_folder(current_image, "과부하 신호"):
                    st.success("과부하 신호로 라벨링되었습니다!")
                    st.rerun()
        
        # 건너뛰기 버튼
        st.markdown("---")
        if st.button("⏭️ 이 이미지 건너뛰기", use_container_width=True):
            st.info("이미지를 건너뛰었습니다.")
            st.rerun()
        
        # 키보드 단축키 안내
        st.markdown("---")
        with st.expander("⌨️ 키보드 단축키"):
            st.write("""
            - **1**: 정상 가동음
            - **2**: 냉기 누설 신호  
            - **3**: 과부하 신호
            - **스페이스바**: 건너뛰기
            """)
        
        # 라벨링 히스토리
        with st.expander("📋 최근 라벨링 히스토리"):
            recent_labels = []
            for label_dir in self.labeled_dir.iterdir():
                if label_dir.is_dir():
                    for img_file in sorted(label_dir.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                        recent_labels.append({
                            "파일명": img_file.name,
                            "라벨": label_dir.name,
                            "시간": datetime.fromtimestamp(img_file.stat().st_mtime).strftime("%H:%M:%S")
                        })
            
            if recent_labels:
                for item in recent_labels:
                    st.write(f"**{item['라벨']}** - {item['파일명']} ({item['시간']})")
            else:
                st.write("아직 라벨링된 이미지가 없습니다.")

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='스펙트로그램 라벨링 도구')
    parser.add_argument('--input-dir', default='data/spectrograms', 
                       help='라벨링할 스펙트로그램 이미지 디렉토리')
    parser.add_argument('--port', type=int, default=8501, 
                       help='Streamlit 서버 포트 (기본값: 8501)')
    
    args = parser.parse_args()
    
    # 라벨링 도구 초기화
    labeling_tool = LabelingTool()
    
    # Streamlit 앱 실행
    labeling_tool.run_labeling_interface(args.input_dir)

if __name__ == "__main__":
    # Streamlit으로 직접 실행할 때
    import sys
    
    if len(sys.argv) > 1:
        # 명령행 인수가 있으면 argparse 사용
        main()
    else:
        # Streamlit으로 직접 실행
        labeling_tool = LabelingTool()
        
        # 기본 입력 디렉토리 설정
        default_input_dir = "data/spectrograms"
        
        st.set_page_config(
            page_title="스펙트로그램 라벨링 도구",
            page_icon="🎵",
            layout="wide"
        )
        
        st.title("🎵 스펙트로그램 전문가 라벨링 도구")
        
        # 입력 디렉토리 선택
        input_dir = st.text_input(
            "라벨링할 스펙트로그램 이미지 디렉토리를 입력하세요:",
            value=default_input_dir,
            help="스펙트로그램 이미지 파일들이 있는 디렉토리 경로"
        )
        
        if st.button("라벨링 시작", type="primary"):
            if input_dir and os.path.exists(input_dir):
                labeling_tool.run_labeling_interface(input_dir)
            else:
                st.error(f"디렉토리를 찾을 수 없습니다: {input_dir}")
