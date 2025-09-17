import os
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import multiprocessing as mp
from functools import partial
import time
import json
from datetime import datetime
from models.optimized_signal_preprocessing import OptimizedSignalPreprocessor

class ParallelAudioProcessor:
    def __init__(self, n_workers: int = None, use_multiprocessing: bool = True):
        self.n_workers = n_workers or min(mp.cpu_count(), 8)
        self.use_multiprocessing = use_multiprocessing
        self.results = []
        
        # 프로세스 풀 생성
        if use_multiprocessing:
            self.executor_class = ProcessPoolExecutor
        else:
            self.executor_class = ThreadPoolExecutor
    
    def _process_single_file(self, file_path: str, output_dir: str = "processed_features") -> Dict:
        """단일 파일 처리 (병렬 실행용)"""
        try:
            # 각 프로세스에서 새로운 전처리기 생성
            preprocessor = OptimizedSignalPreprocessor()
            
            result = preprocessor.preprocess_audio_optimized(
                file_path, 
                save_features=True,
                output_dir=output_dir
            )
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'file_path': file_path}
    
    def process_files_parallel(self, file_paths: List[str], 
                             output_dir: str = "processed_features",
                             progress_callback: Callable = None) -> Dict:
        """파일들을 병렬로 처리"""
        try:
            print(f"병렬 처리 시작: {len(file_paths)}개 파일, {self.n_workers}개 워커")
            
            # 출력 디렉토리 생성
            os.makedirs(output_dir, exist_ok=True)
            
            # 병렬 처리 실행
            results = []
            start_time = time.time()
            
            with self.executor_class(max_workers=self.n_workers) as executor:
                # 작업 제출
                future_to_file = {
                    executor.submit(self._process_single_file, file_path, output_dir): file_path 
                    for file_path in file_paths
                }
                
                # 결과 수집
                completed_count = 0
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    
                    try:
                        result = future.result()
                        results.append(result)
                        completed_count += 1
                        
                        # 진행률 콜백
                        if progress_callback:
                            progress_callback(completed_count, len(file_paths), result)
                        
                        print(f"완료 ({completed_count}/{len(file_paths)}): {os.path.basename(file_path)}")
                        
                    except Exception as e:
                        print(f"파일 처리 오류 {file_path}: {e}")
                        results.append({
                            'success': False, 
                            'error': str(e), 
                            'file_path': file_path
                        })
            
            # 결과 분석
            successful_results = [r for r in results if r.get('success', False)]
            failed_results = [r for r in results if not r.get('success', False)]
            
            processing_time = time.time() - start_time
            
            summary = {
                'success': True,
                'total_files': len(file_paths),
                'successful_count': len(successful_results),
                'failed_count': len(failed_results),
                'processing_time': processing_time,
                'files_per_second': len(file_paths) / processing_time,
                'failed_files': [r['file_path'] for r in failed_results],
                'output_dir': output_dir,
                'timestamp': datetime.now().isoformat()
            }
            
            # 요약 저장
            summary_file = os.path.join(output_dir, "parallel_processing_summary.json")
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"병렬 처리 완료: {len(successful_results)}/{len(file_paths)} 파일 성공")
            print(f"처리 시간: {processing_time:.2f}초 ({summary['files_per_second']:.2f} 파일/초)")
            
            return summary
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def process_directory_parallel(self, input_dir: str, 
                                 output_dir: str = "processed_features",
                                 file_extensions: List[str] = None) -> Dict:
        """디렉토리 내 파일들을 병렬로 처리"""
        try:
            if file_extensions is None:
                file_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.aac']
            
            # 오디오 파일 찾기
            audio_files = []
            for root, dirs, files in os.walk(input_dir):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in file_extensions):
                        audio_files.append(os.path.join(root, file))
            
            if not audio_files:
                return {'success': False, 'error': '오디오 파일을 찾을 수 없습니다.'}
            
            print(f"발견된 오디오 파일: {len(audio_files)}개")
            
            # 병렬 처리
            return self.process_files_parallel(audio_files, output_dir)
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_dataset_parallel(self, file_paths: List[str], labels: List[int],
                              output_file: str = "refrigerant_dataset.npz",
                              output_dir: str = "processed_features") -> Dict:
        """병렬 처리로 데이터셋 생성"""
        try:
            if len(file_paths) != len(labels):
                return {'success': False, 'error': '파일과 레이블의 개수가 일치하지 않습니다.'}
            
            print(f"병렬 데이터셋 생성 시작: {len(file_paths)}개 파일")
            
            # 병렬 처리
            processing_result = self.process_files_parallel(file_paths, output_dir)
            
            if not processing_result['success']:
                return processing_result
            
            # 성공한 결과만 수집
            successful_results = []
            for result in processing_result.get('results', []):
                if result.get('success', False):
                    successful_results.append(result)
            
            if not successful_results:
                return {'success': False, 'error': '처리된 결과가 없습니다.'}
            
            # 데이터셋 생성
            dataset_result = self._create_dataset_from_results(successful_results, labels, output_file)
            
            if dataset_result['success']:
                print(f"병렬 데이터셋 생성 완료: {output_file}")
            
            return dataset_result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _create_dataset_from_results(self, results: List[Dict], labels: List[int], 
                                   output_file: str) -> Dict:
        """처리 결과로부터 데이터셋 생성"""
        try:
            # 특성 추출
            mfccs_original = []
            mfccs_compressor = []
            mfccs_refrigerant = []
            compressor_cycles = []
            spectral_features = []
            temporal_features = []
            
            for result in results:
                features = result['features']
                
                # MFCC 특성
                if features.get('mfccs_original') is not None:
                    mfccs_original.append(features['mfccs_original'])
                if features.get('mfccs_compressor') is not None:
                    mfccs_compressor.append(features['mfccs_compressor'])
                if features.get('mfccs_refrigerant') is not None:
                    mfccs_refrigerant.append(features['mfccs_refrigerant'])
                
                # 압축기 주기 특성
                if features.get('compressor_cycle'):
                    compressor_cycles.append(list(features['compressor_cycle'].values()))
                else:
                    compressor_cycles.append([0] * 7)  # 기본값
                
                # 스펙트럼 특성
                if features.get('spectral_original'):
                    spectral_features.append(list(features['spectral_original'].values()))
                else:
                    spectral_features.append([0] * 8)  # 기본값
                
                # 시간적 특성
                if features.get('temporal'):
                    temporal_features.append(list(features['temporal'].values()))
                else:
                    temporal_features.append([0] * 6)  # 기본값
            
            # 배열로 변환
            dataset = {
                'mfccs_original': np.array(mfccs_original),
                'mfccs_compressor': np.array(mfccs_compressor),
                'mfccs_refrigerant': np.array(mfccs_refrigerant),
                'compressor_cycles': np.array(compressor_cycles),
                'spectral_features': np.array(spectral_features),
                'temporal_features': np.array(temporal_features),
                'labels': np.array(labels),
                'file_paths': [result['file_path'] for result in results]
            }
            
            # 데이터셋 저장
            np.savez_compressed(output_file, **dataset)
            
            # 메타데이터 저장
            metadata = {
                'total_samples': len(results),
                'feature_shapes': {
                    'mfccs_original': dataset['mfccs_original'].shape,
                    'mfccs_compressor': dataset['mfccs_compressor'].shape,
                    'mfccs_refrigerant': dataset['mfccs_refrigerant'].shape,
                    'compressor_cycles': dataset['compressor_cycles'].shape,
                    'spectral_features': dataset['spectral_features'].shape,
                    'temporal_features': dataset['temporal_features'].shape
                },
                'label_distribution': {
                    'class_0': int(np.sum(labels == 0)),
                    'class_1': int(np.sum(labels == 1))
                },
                'created_at': datetime.now().isoformat()
            }
            
            metadata_file = output_file.replace('.npz', '_metadata.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return {'success': True, 'dataset_file': output_file, 'metadata': metadata}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def benchmark_performance(self, file_paths: List[str], 
                            output_dir: str = "benchmark_results") -> Dict:
        """성능 벤치마크"""
        try:
            print("성능 벤치마크 시작...")
            
            # 단일 스레드 처리
            print("단일 스레드 처리 테스트...")
            start_time = time.time()
            
            preprocessor = OptimizedSignalPreprocessor()
            single_thread_results = []
            
            for file_path in file_paths[:5]:  # 처음 5개 파일만 테스트
                result = preprocessor.preprocess_audio_optimized(file_path)
                single_thread_results.append(result)
            
            single_thread_time = time.time() - start_time
            
            # 병렬 처리
            print("병렬 처리 테스트...")
            parallel_result = self.process_files_parallel(file_paths[:5], output_dir)
            parallel_time = parallel_result['processing_time']
            
            # 성능 비교
            speedup = single_thread_time / parallel_time
            efficiency = speedup / self.n_workers
            
            benchmark_result = {
                'single_thread_time': single_thread_time,
                'parallel_time': parallel_time,
                'speedup': speedup,
                'efficiency': efficiency,
                'n_workers': self.n_workers,
                'test_files': len(file_paths[:5])
            }
            
            # 벤치마크 결과 저장
            os.makedirs(output_dir, exist_ok=True)
            benchmark_file = os.path.join(output_dir, "benchmark_results.json")
            with open(benchmark_file, 'w', encoding='utf-8') as f:
                json.dump(benchmark_result, f, indent=2, ensure_ascii=False)
            
            print(f"벤치마크 완료:")
            print(f"  단일 스레드: {single_thread_time:.2f}초")
            print(f"  병렬 처리: {parallel_time:.2f}초")
            print(f"  속도 향상: {speedup:.2f}x")
            print(f"  효율성: {efficiency:.2f}")
            
            return benchmark_result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# 사용 예제
if __name__ == "__main__":
    # 병렬 처리기 생성
    processor = ParallelAudioProcessor(n_workers=4, use_multiprocessing=True)
    
    # 샘플 파일 목록
    sample_files = [
        "audio1.wav", "audio2.wav", "audio3.wav", "audio4.wav", "audio5.wav"
    ]
    
    # 실제 파일이 있는지 확인
    existing_files = [f for f in sample_files if os.path.exists(f)]
    
    if existing_files:
        # 병렬 처리
        result = processor.process_files_parallel(existing_files)
        
        if result['success']:
            print(f"병렬 처리 완료: {result['successful_count']}개 파일")
            
            # 성능 벤치마크
            benchmark_result = processor.benchmark_performance(existing_files)
            
            if benchmark_result.get('success', True):
                print(f"속도 향상: {benchmark_result['speedup']:.2f}x")
        else:
            print(f"병렬 처리 실패: {result['error']}")
    else:
        print("테스트할 오디오 파일이 없습니다.")
        print("사용법:")
        print("processor = ParallelAudioProcessor(n_workers=4)")
        print("result = processor.process_files_parallel(file_paths)")
