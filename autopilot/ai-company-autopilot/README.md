# AI Company Autopilot v1.0 (클로드 AI 직원 5명 + 총괄 마스터 무인 사이트 운영·검증·수익화 스튜디오)

유튜브 영상(`https://youtu.be/EDvnavKiWwI`, **「클로드 직원 5명이 제 사이트로 알아서 돈 벌어줍니다 (ai 직원 세팅법 8가지)」**)의 8단계 세팅법을 전수 감사·팩트체크하여, **검증된 핵심 구조(채용 공고, CLAUDE.md 매뉴얼, 5개 부서 + 마스터 분업, 매일 09:00 스케줄, 거짓말 방지 2줄 검수, GSC/SEO 점검 + SNS 카드뉴스 수익화)**는 100% 코드로 완전 자동화하고 **보안 위험(무제한 '항상 허용')·PC 꺼짐 중단·월 $138+ 멀티 에이전트 토큰 폭증·LLM 거짓 완료 보고(환각)**를 구조적으로 제거한 풀스택 무인 운영 시스템입니다.

---

## 핵심 고도화 기능 (영상 8단계 완전 자동화)

1. **①·③·⑤·⑥ Claude Code 8단계 스타터 팩 자동 생성 (`workspace_bootstrapper.py`)**:
   - `output/claude_starter_pack/`에 `job_posting.md`, 내 사이트(`dream8837z.github.io`, `pseo-revenue-autopilot`) 맞춤형 `CLAUDE.md`, `~/.claude/settings.json`용 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 패치, `.claude/agents/` 6개 부서 에이전트 정의서, `/schedule` 명령어 및 **PC가 꺼져도 매일 KST 09:00 실행되는 `.github/workflows/daily_ai_company.yml`**을 자동 생성합니다.
2. **④ 최소 권한 & 보안 가드레일 (`security_guard.py`)**:
   - 영상의 위험한 폴더 "항상 허용" 대신 부서별 읽기/쓰기 **소유권 매트릭스(`permissions_policy.json`)**, `.env`/시크릿 파일 접근 차단, 파괴적 명령(`rm -rf`, `git push --force`) 차단을 강제합니다.
3. **실제 작동하는 5개 AI 부서 무인 워커 (`company_engine/departments/`)**:
   - **기획팀 (`planner_dept.py`)**: 실제 보유 사이트(`dream8837z.github.io`, `pseo-revenue-autopilot/dist`)의 HTML·`sitemap.xml`·`robots.txt`·`ads.txt`·`llms.txt`·JSON-LD·메타태그를 스캔해 SEO 점수 및 우선순위 백로그 산출.
   - **개발팀 (`dev_dept.py`)**: 내부 깨진 링크 점검 및 라이브 사이트를 무단 덮어쓰지 않는 안전한 `<head>` SEO 패치 제안서(`.md`) 자동 생성.
   - **디자인팀 (`design_dept.py`)**: 원가 `$0`으로 `1080×1350` 4:5 인스타그램·유튜브 커뮤니티용 **한국어 SNS 카드뉴스 5장 캐러셀 PNG** 무인 렌더링.
   - **CS팀 (`cs_dept.py`)**: 유입 문의 자동 분류(버그/제휴·결제/콘텐츠 요청/스팸 차단), 개발팀 이관, 제휴·환불 고위험 티켓 인간 승인 게이트(`requires_human_approval`).
   - **마케팅팀 (`marketing_dept.py`)**: 렌더링된 카드뉴스 5장 + 인스타그램·유튜브 커뮤니티·스레드용 카피 및 UTM 수익화 트래킹 링크 번들 생성.
4. **⑦ 총괄 마스터 거짓말 방지 기계적 증거 게이트 (`master_verifier.py`)**:
   - 영상의 2줄 규칙(*"직접 열어 증거를 보여줄 것 / 확인 못 한 건 못했다고 말할 것"*)을 코드 레벨로 구현: 모든 부서 산출물을 직접 다시 열어 **파일 실존·0바이트 방지·SHA-256 해시 대조·JSON 파싱·PNG 해상도(`1080×1350`) 및 픽셀 분산(빈 이미지 방지)**을 검증하며, 미통과 시 즉시 `UNVERIFIED_REJECTED` 처리합니다.
5. **토큰 원가 & BEP 감사 + Executive HQ 웹 관제 대시보드 (`economics_auditor.py`, `studio_builder.py`)**:
   - 5인 에이전트 팀 매일 API 풀가동(월 `$138`) 대비 **97% 비용 절감(월 `$3.60` / 로컬 무인 `$0`)** 하이브리드 아키텍처와 인터랙티브 HQ 대시보드(`output/studio/index.html`)를 제공합니다.

---

## 빠른 실행

```bash
cd /home/dream8837/.gemini/antigravity/scratch/ai-company-autopilot

# 1. AI 직원 5명 + 총괄 마스터 전체 일일 무인 파이프라인 실행
.venv/bin/python -m company_engine run

# 2. 총괄 마스터 증거 재검증만 단독 실행
.venv/bin/python -m company_engine verify

# 3. 전체 유닛 & 통합 테스트 실행
.venv/bin/python -m unittest discover -s tests -t . -v

# 4. Executive HQ 웹 대시보드 로컬 프리뷰
.venv/bin/python -m http.server 8795 --directory output
# 접속: http://localhost:8795/studio/index.html
```
