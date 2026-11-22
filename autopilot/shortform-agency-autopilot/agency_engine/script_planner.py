"""v4.0 4-Stage Script Planner — 5-Axis 100pt Viral Retention Scoring + A/B/C Hook Variants + 3 Personas."""

from __future__ import annotations

import re
from typing import Any, Dict, List

from agency_engine.config import ClientBrief
from agency_engine.hooks_library import HooksLibrary


class ScriptPlanner:
    """Generates 4-stage B2B short-form scripts with 5-axis retention scoring and A/B/C hook variants."""

    def __init__(self, hooks_lib: HooksLibrary) -> None:
        self.hooks_lib = hooks_lib

    def plan_for_brief(self, brief: ClientBrief) -> Dict[str, Any]:
        top_hooks = self.hooks_lib.match_for_brief(brief, top_k=15)

        # Pick 3 distinct strategic A/B/C hook variants
        variant_specs = [
            ("A", "손실회피·경고형 (Loss Aversion)", ("loss_warning", "contrarian")),
            ("B", "비교·권위형 (Comparison & Authority)", ("comparison", "authority_pro")),
            ("C", "정보격차·비결형 (Curiosity & Info Gap)", ("info_gap", "listicle_number", "story_empathy")),
        ]
        hook_variants: List[Dict[str, Any]] = []
        used_ids: set[str] = set()

        for v_code, v_label, cats in variant_specs:
            chosen = next((h for h in top_hooks if h["category"] in cats and h["hook_id"] not in used_ids), None)
            if chosen is None:
                chosen = next((h for h in top_hooks if h["hook_id"] not in used_ids), top_hooks[0])
            used_ids.add(chosen["hook_id"])
            scenes_for_v = self._build_4stage_scenes(brief, chosen["rendered_hook"])
            scorecard = self.score_script(scenes_for_v, chosen["rendered_hook"], brief)
            hook_variants.append(
                {
                    "variant": v_code,
                    "label": v_label,
                    "hook_id": chosen["hook_id"],
                    "category_ko": chosen["category_ko"],
                    "rendered_hook": chosen["rendered_hook"],
                    "scorecard": scorecard,
                }
            )

        # Auto-select highest-scoring variant as winner
        hook_variants.sort(key=lambda x: (-x["scorecard"]["total_score"], x["variant"]))
        winner = hook_variants[0]
        main_hook = winner["rendered_hook"]

        base_scenes = self._build_4stage_scenes(brief, main_hook)
        personas = {
            "professional": {
                "label": "표준 프로페셔널 (신뢰·전문직 톤)",
                "scenes": base_scenes,
            },
            "friendly": {
                "label": "친근한 구어체 (공감·이탈 방지 톤)",
                "scenes": self._apply_friendly_tone(base_scenes),
            },
            "busan": {
                "label": "부산 사투리 캐릭터 (자연스러운 맛살리기)",
                "scenes": self._apply_busan_tone(base_scenes),
            },
        }

        selected_scenes = personas.get(brief.persona_tone, personas["professional"])["scenes"]
        llm_prompt = self._build_llm_upgrade_prompt(brief, top_hooks[:5])

        return {
            "client_id": brief.client_id,
            "client_name": brief.client_name,
            "industry": brief.industry,
            "topic": brief.topic,
            "selected_persona": brief.persona_tone,
            "top_hooks": top_hooks[:10],
            "hook_variants": hook_variants,
            "winning_variant": winner["variant"],
            "retention_scorecard": winner["scorecard"],
            "selected_hook": main_hook,
            "personas": personas,
            "active_scenes": selected_scenes,
            "estimated_duration_sec": sum(s["duration_sec"] for s in selected_scenes),
            "llm_upgrade_prompt": llm_prompt,
        }

    def score_script(self, scenes: List[Dict[str, Any]], hook: str, brief: ClientBrief) -> Dict[str, Any]:
        """5-Axis Quantitative Viral Retention Rubric (100 pts total)."""
        # 1. Hook Velocity (25 pts)
        hook_pts = 16
        if len(hook) <= 46:
            hook_pts += 3
        if re.search(r"\d+|%|vs|VS", hook):
            hook_pts += 3
        if any(k in hook for k in ("절대", "숨기는", "실수", "날립니다", "차이", "비교", "멈추", "비밀")):
            hook_pts += 3
        hook_pts = min(25, hook_pts)

        # 2. Open-Loop Tension (20 pts)
        s2_text = scenes[1]["subtitle"] if len(scenes) > 1 else ""
        loop_pts = 12
        if any(k in s2_text for k in ("세 번째", "끝까지", "핵심", "놓치는")):
            loop_pts += 8
        loop_pts = min(20, loop_pts)

        # 3. Pacing & Micro-Cut Cadence (20 pts)
        avg_dur = sum(s["duration_sec"] for s in scenes) / max(1, len(scenes))
        pacing_pts = 20 if 2.8 <= avg_dur <= 5.0 else 15

        # 4. Proof & Specificity Density (15 pts)
        full_text = " ".join(s["subtitle"] for s in scenes)
        proof_pts = 8
        if brief.compare_a and brief.compare_a in full_text:
            proof_pts += 3
        if any(k in full_text for k in ("데이터", "사례", "기준표", "절반", "90%")):
            proof_pts += 4
        proof_pts = min(15, proof_pts)

        # 5. CTA Friction & Conversion Clarity (20 pts)
        cta_text = scenes[-1]["subtitle"] if scenes else ""
        cta_pts = 10
        if any(k in cta_text for k in ("댓글", "DM", "팔로우")):
            cta_pts += 6
        if any(k in cta_text for k in ("비교표", "체크리스트", "가이드", "저장")):
            cta_pts += 4
        cta_pts = min(20, cta_pts)

        # v5.0 Discriminative Calibration: Lexical diversity (TTR) + Anti-cliche spam penalty
        tokens = re.findall(r"[가-힣a-zA-Z0-9]+", full_text)
        ttr = len(set(tokens)) / max(1, len(tokens))
        cliche_hits = sum(1 for c in ("무조건 대박", "인생 역전", "100% 보장", "기적의") if c in full_text)
        calibration = (2 if ttr >= 0.78 else (-3 if ttr < 0.62 else 0)) - (cliche_hits * 6)

        total = max(0, min(100, hook_pts + loop_pts + pacing_pts + proof_pts + cta_pts + calibration))
        grade = "S" if total >= 92 else ("A" if total >= 84 else ("B" if total >= 74 else "C"))
        est_3s_hold = min(89.5, round(52.0 + (hook_pts / 25.0) * 34.0, 1))
        est_completion = min(68.0, round(24.0 + (total / 100.0) * 39.0, 1))

        return {
            "total_score": total,
            "grade": grade,
            "lexical_diversity_ttr": round(ttr, 2),
            "cliche_penalty": cliche_hits * 6,
            "predicted_3s_hold_pct": est_3s_hold,
            "predicted_completion_pct": est_completion,
            "axes": {
                "hook_velocity_25": hook_pts,
                "open_loop_20": loop_pts,
                "pacing_cadence_20": pacing_pts,
                "proof_density_15": proof_pts,
                "cta_conversion_20": cta_pts,
            },
        }

    def _build_4stage_scenes(self, brief: ClientBrief, main_hook: str) -> List[Dict[str, Any]]:
        from agency_engine.evolution_engine import load_learned_policy

        dm_kw = str(load_learned_policy().get("dm_trigger_keyword", "비교표"))
        return [
            {
                "stage": "1단계 · 멈추기 (3초 후킹)",
                "duration_sec": 3.0,
                "subtitle": main_hook,
                "highlight_keyword": brief.compare_a or brief.topic.split()[0],
                "camera_direction": "빠른 줌인 + 정면 아이컨택 (자기소개 생략, 첫 0.3초 즉시 발화)",
            },
            {
                "stage": "2단계 · 궁금하게 (오픈 루프)",
                "duration_sec": 3.5,
                "subtitle": f"특히 세 번째 기준은 {brief.industry} 현장에서도 90%가 놓치는 핵심입니다. 끝까지 보세요.",
                "highlight_keyword": "세 번째 기준",
                "camera_direction": "손가락 3 표시 + 화면 살짝 확대(108% 펀치 줌)",
            },
            {
                "stage": "3단계 · 알려주기 ① (1컷 1메시지)",
                "duration_sec": 4.5,
                "subtitle": f"첫째, {brief.compare_a}와 {brief.compare_b}는 목적부터 완전히 다릅니다. 가격보다 내 조건 적합도를 먼저 보세요.",
                "highlight_keyword": f"{brief.compare_a} vs {brief.compare_b}",
                "camera_direction": "상단 비교 배지 팝업 + 2초 단위 마이크로 자막 전환",
            },
            {
                "stage": "3단계 · 알려주기 ② (실전 기준)",
                "duration_sec": 4.5,
                "subtitle": "둘째, 겉으로 보이는 홍보 문구 말고 실제 사례와 유지 기간 데이터를 반드시 확인하세요.",
                "highlight_keyword": "실제 데이터",
                "camera_direction": "증거 카드 오버레이 + 컷 점프(무음 0.1초 이하)",
            },
            {
                "stage": "3단계 · 알려주기 ③ (핵심 결론)",
                "duration_sec": 5.0,
                "subtitle": "셋째, 처음 3초에 던진 질문의 답입니다. 나에게 맞는 기준표 하나만 정하면 시행착오가 절반 이하로 줄어듭니다.",
                "highlight_keyword": "시행착오 절반",
                "camera_direction": "핵심 문구 골드 하이라이트 필 배지 + 강조 효과음",
            },
            {
                "stage": "4단계 · 루프 브릿지 + DM CTA",
                "duration_sec": 2.4,
                "subtitle": f"댓글에 '{dm_kw}' 남기시면 바로 보내드릴게요. 그래서 우리가 꼭 먼저 봐야 할 게,",
                "highlight_keyword": f"댓글 '{dm_kw}' → DM",
                "camera_direction": "하단 DM 콜아웃 배지 + 0초 훅으로 끊김 없이 무한 루프 연결",
            },
        ]

    def _apply_friendly_tone(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        replacements = [
            ("있습니다.", "있어요!"),
            ("합니다.", "해요."),
            ("보세요.", "보셔야 해요."),
            ("확인하세요.", "체크해 보세요!"),
            ("줄어듭니다.", "확 줄어들어요."),
            ("다릅니다.", "달라요."),
        ]
        out = []
        for s in scenes:
            txt = s["subtitle"]
            for old, new in replacements:
                txt = txt.replace(old, new)
            out.append({**s, "subtitle": txt})
        return out

    def _apply_busan_tone(self, scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        replacements = [
            ("있습니다.", "있습니다, 진짜로요."),
            ("끝까지 보세요.", "끝까지 한번 들어 보이소."),
            ("먼저 보세요.", "먼저 보셔야 됩니더."),
            ("확인하세요.", "꼭 체크해 보이소."),
            ("줄어듭니다.", "확 줄어듭니다."),
            ("보실 수 있습니다.", "꺼내 보실 수 있심더."),
        ]
        out = []
        for s in scenes:
            txt = s["subtitle"]
            for old, new in replacements:
                txt = txt.replace(old, new)
            out.append({**s, "subtitle": txt})
        return out

    def _build_llm_upgrade_prompt(self, brief: ClientBrief, hooks: List[Dict[str, Any]]) -> str:
        hooks_str = "\n".join(f"- [{h['category_ko']}] {h['rendered_hook']}" for h in hooks)
        return f"""당신은 월 조회수 300만+을 만드는 대한민국 최상위 B2B 숏폼 기획자입니다.
아래 클라이언트 정보를 바탕으로 30~45초 릴스/쇼츠 대본을 작성해 주세요.

[클라이언트 정보]
- 브랜드/업종: {brief.client_name} ({brief.industry})
- 영상 주제: {brief.topic}
- 비교 대상: {brief.compare_a} vs {brief.compare_b}
- 최종 CTA: {brief.cta_action}
- 말투 페르소나: {brief.persona_tone}

[참고할 검증된 3초 후킹 후보]
{hooks_str}

[필수 4단계 구조]
1) 멈추기 (0~3초): 자기소개 금지, 결과/충격 팩트 먼저 제시
2) 궁금하게 (3~6초): "세 번째가 가장 중요합니다" 같은 오픈 루프 삽입
3) 알려주기 (6~25초): 한 컷에 한 메시지, 3가지 실전 근거 제시
4) 부탁하기 (25~30초): 팔로우·저장·댓글 키워드→DM 자동 발송 유도
"""
