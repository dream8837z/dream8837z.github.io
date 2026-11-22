"""3-Channel Client Acquisition Kit (Threads, Soomgo, Meta) & Anti-Scope-Creep B2B Contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from agency_engine.config import AgencyConfig


class ClientAcquisitionKit:
    """Generates ready-to-use Threads viral offers, Soomgo proposals, DM scripts, and B2B contract guardrails."""

    def __init__(self, config: AgencyConfig) -> None:
        self.config = config

    def generate(self, out_dir: Path) -> Dict[str, Any]:
        out_dir.mkdir(parents=True, exist_ok=True)

        threads_free_sample = """[Threads 무료 포트폴리오 모객 글 — 1편 6분 AI 자동화 전략]

지금 B2B 숏폼(릴스/쇼츠) 레퍼런스 포트폴리오를 새롭게 구축 중이라
선착순 5분께 **무료로 숏폼 1편** 기획+컷편집+자막까지 완성해 드립니다.

✔ 조건: 스마트폰으로 3~5분 대충 찍어 보내주시면 됩니다 (NG·말더듬 그대로 OK)
✔ 퀄리티: 무료라고 대충 만들지 않습니다. 제 포트폴리오로 쓸 거라 3초 후킹부터 직접 잡아드립니다.
✔ 대상: 병원/클리닉·변호사·강사·브랜드 대표님 우선

원하시는 분은 댓글에 **"신청"** 남겨주시면 바로 DM 드리겠습니다!"""

        threads_insight_proof = """[Threads 성과 자랑(인사이트 보드) 인바운드 모객 글]

원본 7분짜리 NG 투성이 스마트폰 영상을
4단계 대본 구조 + AI 자동 컷편집으로 1분 13초 릴스로 바꿨을 때 생긴 일.

- 최근 30일 도달: 367만+
- 신규 팔로워 유입: +600명
- 제작 소요 시간: 기존 4시간 → 15분 단축

전문직 대표님들이 카메라 앞에서 말 잘하실 필요 없습니다.
기획과 컷편집 구조만 바꾸면 됩니다.
월간 10편(+2편 보너스) 패키지 문의는 댓글에 **"견적"** 남겨주세요."""

        soomgo_proposal = """[숨고(Soomgo) 고전환 견적 제안서]

안녕하세요, 대표님! 숏폼(릴스·쇼츠·틱톡) 기획 및 편집 전문 팀입니다.
많은 대표님들이 '촬영은 했는데 편집이 너무 오래 걸리고 조회수가 안 나온다'고 고민하십니다.

저희는 단순 컷편집이 아니라 **4단계 검증 대본(3초 후킹·오픈루프·1컷1메시지·DM CTA)**까지 함께 설계합니다.

📌 제안 패키지 (선착순 런칭 혜택)
- 기본 10편 패키지 계약 시 → **2편 무료 추가(총 12편 납품)**
- 스마트폰 원본 영상만 보내주시면 NG·무음 제거 + 강조 자막 + 줌 펀치 완성 납품
- 원본 수정이 필요하실 경우 CapCut / Premiere Pro 프로젝트 파일 제공 가능

먼저 대표님 업종에 맞는 **3초 후킹 문구 3개**를 무료로 짜드릴까요? 편하게 답장 주세요!"""

        b2b_contract_guardrails = """# B2B 숏폼 외주 표준 계약서 핵심 가드레일 (무한 수정·미수금 방지)

1. **납품 범위 명확화**: 월 10편(+프로모션 2편) 세로형 9:16 MP4(30~60초) + 4단계 기획 대본 + 자막 포함.
2. **수정 횟수 제한 (Anti-Scope-Creep)**: 편당 **무료 수정 최대 2회**(오타·자막 위치·컷 길이 조정)로 제한하며, 기획 전면 변경 또는 3회차부터는 편당 3만원 추가 과금.
3. **클라이언트 원본 전달 SLA**: 클라이언트가 스마트폰 원본 영상 전달 후 영업일 2일 이내 1차 시안 납품.
4. **결제 조건**: 착수 전 선결제 100% (또는 착수금 50% / 5편 납품 시 잔금 50%).
5. **저작권 및 포트폴리오 활용**: 최종 납품물의 상업적 이용권은 잔금 완납 시 클라이언트에 귀속되며, 제작사는 익명/성과 인사이트 포트폴리오로 활용할 수 있음."""

        bundle = {
            "threads_free_sample_post": threads_free_sample,
            "threads_insight_proof_post": threads_insight_proof,
            "soomgo_proposal_template": soomgo_proposal,
            "b2b_contract_guardrails_md": b2b_contract_guardrails,
        }

        json_path = out_dir / "client_acquisition_kit.json"
        json_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")

        contract_path = out_dir / "b2b_contract_guardrails.md"
        contract_path.write_text(b2b_contract_guardrails, encoding="utf-8")

        return {
            **bundle,
            "json_path": str(json_path),
            "contract_path": str(contract_path),
        }
