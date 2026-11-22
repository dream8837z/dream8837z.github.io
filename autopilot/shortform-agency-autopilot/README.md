# Shortform Agency Autopilot v1.0 (B2B 쇼폼 외주 대행 완전 자동화 팩토리)

유튜브 영상(`https://youtu.be/mF7mxHau5dE`, **「부산 달동네에서 50만원으로 3년만에 735억 회사 대표가 된 30대 남자의 하루 | "2027년 개꿀통 부업은 바로 이겁니다"」**, 이웃집사장 · 타철 대표)을 전수 해부·팩트체크하여, 영상에서 **단톡방 참여·무료강의 미끼로 잠가둔 핵심 도구(3초 후킹 140개 사전, 4단계 대본 생성기, AI 무음·NG 자동 컷편집 + CapCut/Premiere 내보내기, Threads/숨고 고객 모집 영업 키트)**를 원가 `$0` 100% 오픈 자동화 코드로 구축한 시스템입니다.

---

## 핵심 기능

1. **3초 후킹 문장 140개 사전 & 실시간 자동 치환기 (`hooks_library.py`)**:
   - 7대 카테고리(정보 격차·직접 비교·실수 경고·숫자 리스트·고정관념 파괴·전문직 권위·스토리 공감) × 20개 = **정확히 140개 검증 후킹 템플릿** 내장.
   - 업종·주제·비교 대상(`A vs B`) 입력 시 실시간 치환 및 TOP 10 자동 스코어링.
2. **4단계 기획·대본 생성기 + 3종 페르소나 변환 (`script_planner.py`)**:
   - **멈추기(3초 훅) → 궁금하게(오픈 루프) → 알려주기(1컷 1메시지 3포인트) → 부탁하기(댓글·DM CTA)** 자동 생성.
   - 표준 프로페셔널 / 친근한 구어체 / 자연스러운 부산 사투리 3종 톤 변환 + ChatGPT/Claude 원클릭 고도화 프롬프트 제공.
3. **AI 무음·NG 자동 컷편집 & 1080×1920 MP4 + CapCut/Premiere 동시 내보내기 (`video_autocutter.py`)**:
   - 오디오 RMS 에너지 기반 무음 구간 탐지 + 발화 NG 키워드(`죄송합니다`, `다시 할게요` 등) 자동 제거.
   - 원가 `$0`으로 `1080×1920 30fps` 한국어 자막·하이라이트 배지 MP4 + `.srt` + **CapCut Desktop `draft_content.json` + Premiere Pro `.fcpxml`** 동시 생성.
4. **3대 고객 모집 영업 키트 & 무한 수정 방지 B2B 계약서 (`client_acquisition.py`)**:
   - Threads 무료 3편 포트폴리오 모객글, 성과 자랑(인사이트 보드) 글, 숨고 10+2 보너스 견적 제안서, 수정 2회 제한 B2B 표준 계약서 가드레일 자동 생성.
5. **현실 단가·CAC·시급 시뮬레이터 & 인터랙티브 웹 스튜디오 (`agency_economics.py`, `studio_builder.py`)**:
   - 브라우저에서 140개 후킹 문장을 실시간 치환·복사하고, 렌더링된 9:16 릴스 MP4를 바로 재생할 수 있는 `output/studio/index.html` 빌드.

---

## 빠른 실행

```bash
cd /home/dream8837/.gemini/antigravity/scratch/shortform-agency-autopilot

# 1. 전체 B2B 쇼폼 자동화 파이프라인 실행 (140 훅 + 3개 클라이언트 MP4/SRT/CapCut/Premiere + 웹 스튜디오)
.venv/bin/python -m agency_engine run

# 2. 전체 유닛 & 통합 테스트 실행
.venv/bin/python -m unittest discover -s tests -t . -v

# 3. Agency Studio 웹 대시보드 로컬 프리뷰
.venv/bin/python -m http.server 8796 --directory output
# 접속: http://localhost:8796/studio/index.html
```
