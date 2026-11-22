"""Pro v4.0 Studio Builder — Broadcast Safe-Zone X-Ray, 5-Axis A/B/C Scorecard, 1-Click Handoff ZIP, XHR Progress & Drip CRM."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Dict

from agency_engine.config import VIDEO_FORENSIC_AUDIT, VIDEO_SOURCE


def _esc(val: Any) -> str:
    return html.escape(str(val), quote=True)


class AgencyStudioBuilder:
    """Builds `output/studio/index.html` with XSS-safe DOM rendering, Safe-Zone X-Ray, and 1-Click ZIP Handoff."""

    def build(self, payload: Dict[str, Any], out_html: Path) -> Path:
        out_html.parent.mkdir(parents=True, exist_ok=True)

        run_date = payload["run_date"]
        hooks_catalog_json = json.dumps(payload["hooks_catalog_140"], ensure_ascii=False).replace("</", "<\\/")
        projects_json = json.dumps(payload["projects"], ensure_ascii=False).replace("</", "<\\/")
        econ = payload["economics"]
        acq = payload["acquisition_kit"]
        yt_count = len(payload.get("monetization", {}).get("youtube_queue", {}).get("items", []))

        econ_rows = "".join(
            f"""
            <tr class="{'hl' if t['tier_id'] == 'tier2_standard_retainer' else ''}">
              <td><strong>{_esc(t['name'])}</strong></td>
              <td class="mono">{t['videos_delivered']}편</td>
              <td class="mono">{t['package_price_krw']:,}원</td>
              <td class="mono">{t['unit_price_krw']:,}원</td>
              <td class="mono">{t['total_hours_per_package']}h</td>
              <td class="mono accent">{t['effective_hourly_rate_krw']:,}원/h</td>
              <td class="mono">{t['clients_for_500k_krw']} / {t['clients_for_3m_krw']} / {t['clients_for_10m_krw']}곳</td>
              <td class="muted">{_esc(t['positioning_note'])}</td>
            </tr>
            """
            for t in econ["tiers"]
        )

        audit_rows = "".join(
            f"""
            <tr>
              <td><strong>{_esc(r['topic'])}</strong></td>
              <td class="muted">{_esc(r['video_claim'])}</td>
              <td><span class="tag">{_esc(r['verdict'])}</span></td>
              <td style="color:#f87171">{_esc(r['risk_found'])}</td>
              <td style="color:#4ade80">{_esc(r['our_solution'])}</td>
            </tr>
            """
            for r in VIDEO_FORENSIC_AUDIT
        )

        doc = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Shortform Studio Pro v4.0 — Broadcast &amp; Revenue Edition</title>
  <style>
    :root {{
      --bg:#09090b; --surface:#111114; --surface-2:#18181c; --border:#27272a;
      --text:#fafafa; --muted:#a1a1aa; --dim:#71717a;
      --accent:#ff4d2e; --gold:#f5c451; --green:#22c55e;
    }}
    * {{ box-sizing:border-box; }}
    html, body {{ margin:0; height:100%; background:var(--bg); color:var(--text); font-family:'Pretendard',-apple-system,BlinkMacSystemFont,'Noto Sans KR',sans-serif; -webkit-font-smoothing:antialiased; }}
    .app {{ display:grid; grid-template-columns:248px 1fr; min-height:100vh; }}
    @media (max-width:900px) {{ .app {{ grid-template-columns:1fr; }} .sidebar {{ display:none; }} }}
    .sidebar {{ background:var(--surface); border-right:1px solid var(--border); padding:24px 16px; display:flex; flex-direction:column; gap:6px; position:sticky; top:0; height:100vh; }}
    .brand {{ padding:4px 10px 20px; border-bottom:1px solid var(--border); margin-bottom:12px; }}
    .brand-title {{ font-size:15px; font-weight:800; letter-spacing:-0.02em; display:flex; align-items:center; gap:8px; }}
    .dot {{ width:8px; height:8px; border-radius:50%; background:var(--accent); display:inline-block; }}
    .brand-sub {{ font-size:11px; color:var(--dim); margin-top:4px; }}
    .nav-btn {{ background:transparent; border:1px solid transparent; color:var(--muted); text-align:left; padding:10px 12px; border-radius:8px; font-size:13px; font-weight:600; cursor:pointer; }}
    .nav-btn:hover {{ background:var(--surface-2); color:var(--text); }}
    .nav-btn.active {{ background:var(--surface-2); color:var(--text); border-color:var(--border); }}
    .sidebar-foot {{ margin-top:auto; padding:12px 10px 0; border-top:1px solid var(--border); font-size:11px; color:var(--dim); }}

    .main {{ padding:30px 36px 72px; max-width:1200px; width:100%; }}
    .topbar {{ display:flex; justify-content:space-between; align-items:flex-end; gap:16px; margin-bottom:24px; padding-bottom:16px; border-bottom:1px solid var(--border); }}
    h1 {{ margin:0; font-size:24px; font-weight:800; letter-spacing:-0.03em; }}
    h2 {{ margin:0 0 12px; font-size:16px; font-weight:700; }}
    .muted {{ color:var(--muted); font-size:13px; }}
    .mono {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12px; }}
    .accent {{ color:var(--gold); font-weight:700; }}
    .view {{ display:none; }}
    .view.active {{ display:block; }}

    .metrics {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:12px; margin-bottom:22px; }}
    .metric {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:15px 17px; }}
    .metric-k {{ font-size:11px; color:var(--dim); text-transform:uppercase; letter-spacing:0.06em; }}
    .metric-v {{ font-size:25px; font-weight:800; margin-top:6px; }}
    .metric-s {{ font-size:12px; color:var(--muted); margin-top:4px; }}

    .panel {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:20px; margin-bottom:18px; }}
    .grid-2 {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(420px,1fr)); gap:16px; }}
    .studio-split {{ display:grid; grid-template-columns:312px 1fr; gap:24px; align-items:start; }}
    @media (max-width:900px) {{ .studio-split {{ grid-template-columns:1fr; }} }}

    .phone-stage {{ position:relative; background:#000; border:1px solid var(--border); border-radius:20px; padding:8px; overflow:hidden; }}
    .phone-stage video {{ width:100%; border-radius:14px; display:block; background:#000; aspect-ratio:9/16; object-fit:cover; }}
    .safe-zone-overlay {{ position:absolute; inset:8px; border-radius:14px; pointer-events:none; display:none; overflow:hidden; }}
    .safe-zone-overlay.on {{ display:block; }}
    .sz-top, .sz-bot, .sz-right {{ position:absolute; background:rgba(255,77,46,0.22); border:1px dashed rgba(255,77,46,0.85); color:#fff; font-size:10px; font-weight:700; display:flex; align-items:center; justify-content:center; }}
    .sz-safe {{ position:absolute; border:1.5px dashed rgba(34,197,94,0.9); }}

    .dropzone {{ border:1.5px dashed #3f3f46; border-radius:12px; padding:34px 20px; text-align:center; background:#0c0c0f; cursor:pointer; }}
    .dropzone:hover, .dropzone.drag {{ border-color:var(--accent); background:#141112; }}
    .prog-bar {{ height:6px; background:var(--surface-2); border-radius:999px; overflow:hidden; margin-top:12px; display:none; }}
    .prog-fill {{ height:100%; width:0%; background:var(--accent); transition:width .15s; }}

    .form-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(165px,1fr)); gap:10px; margin-bottom:14px; }}
    label {{ display:block; font-size:11px; color:var(--dim); margin-bottom:5px; text-transform:uppercase; }}
    input, select {{ width:100%; background:var(--bg); color:var(--text); border:1px solid var(--border); border-radius:8px; padding:9px 11px; font-size:13px; }}
    .btn {{ background:var(--surface-2); color:var(--text); border:1px solid var(--border); padding:8px 13px; border-radius:8px; font-size:13px; font-weight:600; cursor:pointer; text-decoration:none; display:inline-block; }}
    .btn:hover {{ border-color:#52525b; }}
    .btn.primary {{ background:var(--text); color:var(--bg); border-color:var(--text); }}
    .btn.accent-btn {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
    .btn.active {{ background:var(--text); color:var(--bg); border-color:var(--text); }}
    .btn.sm {{ padding:5px 9px; font-size:11px; }}

    .tabs {{ display:flex; gap:6px; flex-wrap:wrap; margin-bottom:12px; }}
    .tag {{ display:inline-block; font-size:11px; font-weight:700; padding:3px 8px; border-radius:6px; background:var(--surface-2); border:1px solid var(--border); color:var(--muted); }}
    .tag.live {{ color:#4ade80; border-color:rgba(34,197,94,.35); background:rgba(34,197,94,.1); }}
    .tag.gold {{ color:var(--gold); border-color:rgba(245,196,81,.35); background:rgba(245,196,81,.08); }}
    .scene-row {{ border:1px solid var(--border); background:var(--bg); border-radius:10px; padding:11px 13px; margin-bottom:8px; }}
    .variant-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:10px; margin-bottom:14px; }}
    .variant-card {{ border:1px solid var(--border); background:var(--bg); border-radius:10px; padding:12px; font-size:12px; }}
    .variant-card.win {{ border-color:var(--gold); }}
    .hook-list {{ max-height:430px; overflow-y:auto; display:grid; gap:8px; }}
    .hook-row {{ display:flex; justify-content:space-between; align-items:center; gap:12px; padding:10px 14px; background:var(--bg); border:1px solid var(--border); border-radius:8px; font-size:13px; }}
    pre {{ background:var(--bg); border:1px solid var(--border); border-radius:10px; padding:14px; font-size:12px; color:#d4d4d8; white-space:pre-wrap; max-height:280px; overflow-y:auto; margin:10px 0 12px; }}
    .table-wrap {{ overflow-x:auto; border:1px solid var(--border); border-radius:12px; background:var(--surface); }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th, td {{ padding:11px 13px; border-bottom:1px solid var(--border); text-align:left; vertical-align:top; }}
    th {{ background:var(--surface-2); color:var(--muted); font-size:11px; text-transform:uppercase; }}
    tr.hl {{ background:rgba(245,196,81,.06); }}
    .toast {{ position:fixed; bottom:24px; right:24px; background:#fafafa; color:#09090b; padding:11px 16px; border-radius:10px; font-size:13px; font-weight:700; display:none; z-index:99; box-shadow:0 8px 28px rgba(0,0,0,.5); }}
  </style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-title"><span class="dot"></span> Shortform Studio Pro</div>
      <div class="brand-sub">v4.0 · Broadcast -14 LUFS &amp; Revenue</div>
    </div>
    <button class="nav-btn active" onclick="switchView('deliverables', this)">01 · 릴스 납품 스튜디오</button>
    <button class="nav-btn" onclick="switchView('autocut', this)">02 · 실제 MP4 무음 컷편집</button>
    <button class="nav-btn" onclick="switchView('hooks', this)">03 · 140개 3초 후킹 엔진</button>
    <button class="nav-btn" onclick="switchView('sales', this)">04 · 영업 키트 &amp; 계약서</button>
    <button class="nav-btn" onclick="switchView('audit', this)">05 · 단가 시뮬레이터 &amp; 감사</button>
    <button class="nav-btn" onclick="switchView('monetize', this)">06 · 수익화 퍼널 &amp; 리드 CRM</button>
    <div class="sidebar-foot">
      <div>Broadcast -14 LUFS · Karaoke</div>
      <div style="margin-top:4px;">Run: {_esc(run_date)}</div>
    </div>
  </aside>

  <main class="main">
    <div class="topbar">
      <div>
        <h1>Shortform Agency Autopilot v4.0</h1>
        <div class="muted">WordBoundary 카라오케 자막 · -14 LUFS 사이드체인 BGM · xfade 그레이딩 · Safe-Zone X-Ray · 1클릭 납품 ZIP</div>
      </div>
      <span class="tag live" id="healthBadge">● LIVE v4.0 READY</span>
    </div>

    <div class="metrics">
      <div class="metric"><div class="metric-k">오디오 마스터링</div><div class="metric-v">-14 LUFS</div><div class="metric-s">사이드체인 덕킹 BGM + Whoosh SFX</div></div>
      <div class="metric"><div class="metric-k">렌더링 납품본</div><div class="metric-v" id="metricProjCount">{len(payload['projects'])}편</div><div class="metric-s">MP4 + SRT + CapCut + Premiere ZIP</div></div>
      <div class="metric"><div class="metric-k">3초 후킹 엔진</div><div class="metric-v">{len(payload['hooks_catalog_140'])}개</div><div class="metric-s">5축 100점 리텐션 A/B/C 스코어링</div></div>
      <div class="metric"><div class="metric-k">평균 무음·NG 압축</div><div class="metric-v">-{payload['avg_compression_pct']}%</div><div class="metric-s">15ms 클릭 방지 + -14 LUFS</div></div>
    </div>

    <!-- VIEW 1: DELIVERABLES STUDIO -->
    <section id="view-deliverables" class="view active">
      <div class="panel">
        <h2>신규 클라이언트 원클릭 제작 (v4.0 방송급 -14 LUFS + 카라오케 + ZIP)</h2>
        <div class="form-grid">
          <div><label>클라이언트명</label><input id="newName" value="서울 강남 연세치과" /></div>
          <div><label>업종</label><input id="newInd" value="치과·임플란트" /></div>
          <div><label>주제</label><input id="newTopic" value="임플란트 치과 고를 때 실수 3가지" /></div>
          <div><label>비교 A</label><input id="newA" value="오스템" /></div>
          <div><label>비교 B</label><input id="newB" value="스트라우만" /></div>
          <div>
            <label>페르소나 톤</label>
            <select id="newTone">
              <option value="professional">표준 프로페셔널</option>
              <option value="friendly">친근한 구어체</option>
              <option value="busan">부산 사투리</option>
            </select>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
          <button class="btn accent-btn" id="btnGenClient" onclick="generateNewClient()">신규 v4.0 릴스 즉시 제작</button>
          <span id="genStatus" class="muted">무새로고침 실시간 반영 · 완료 즉시 납품 ZIP 다운로드 가능</span>
        </div>
      </div>

      <div class="tabs" id="projectTabs"></div>
      <div class="panel studio-split">
        <div>
          <div class="tabs" style="margin-bottom:8px;">
            <span class="muted" style="align-self:center;font-size:11px;">Safe-Zone X-Ray:</span>
            <button class="btn sm active" onclick="setSafeZone('projSZ','off',this)">OFF</button>
            <button class="btn sm" onclick="setSafeZone('projSZ','yt',this)">YT Shorts</button>
            <button class="btn sm" onclick="setSafeZone('projSZ','ig',this)">IG Reels</button>
          </div>
          <div class="phone-stage">
            <video id="projVideo" controls playsinline></video>
            <div id="projSZ" class="safe-zone-overlay"></div>
          </div>
          <div id="projStats" class="muted" style="margin-top:12px;"></div>
          <div id="projExports" style="display:flex;gap:6px;flex-wrap:wrap;margin-top:10px;"></div>
        </div>
        <div>
          <h2>5축 바이럴 리텐션 스코어카드 &amp; A/B/C 후킹 비교</h2>
          <div id="variantGrid" class="variant-grid"></div>
          <div class="tabs" id="personaTabs"></div>
          <div id="sceneList"></div>
          <h2 style="margin-top:16px;">ChatGPT / Claude 고도화 프롬프트</h2>
          <pre id="projPrompt"></pre>
          <button class="btn primary" onclick="copyById('projPrompt')">프롬프트 복사</button>
        </div>
      </div>
    </section>

    <!-- VIEW 2: REAL MP4 UPLOAD AUTO-CUT -->
    <section id="view-autocut" class="view">
      <div class="panel">
        <h2>실제 스마트폰 MP4 무음 자동 컷편집 (15ms 클릭 방지 + -14 LUFS + 매직바이트 검증)</h2>
        <div class="form-grid">
          <div><label>무음 기준 (dB)</label><input id="cutDb" type="number" value="-32" min="-60" max="-10" /></div>
          <div><label>최소 무음 길이 (초)</label><input id="cutMin" type="number" step="0.05" value="0.45" min="0.15" max="3.0" /></div>
        </div>
        <div id="dropzone" class="dropzone" onclick="document.getElementById('mp4Input').click()">
          <input id="mp4Input" type="file" accept="video/mp4,video/quicktime,.mp4,.mov,.webm" style="display:none" onchange="handleMp4File(this.files[0])" />
          <div style="font-size:15px;font-weight:700;margin-bottom:6px;">여기에 원본 MP4 / MOV 파일을 드래그하거나 클릭해 선택하세요 (최대 150MB)</div>
          <div class="muted" id="cutStatus">업로드 진행률 실시간 표시 · 완료 즉시 Before/After 비교 재생</div>
          <div id="cutProgBar" class="prog-bar"><div id="cutProgFill" class="prog-fill"></div></div>
        </div>
        <div id="cutResult" style="display:none;margin-top:20px;">
          <div class="grid-2">
            <div><h2>원본 (Before)</h2><div class="phone-stage" style="max-width:300px;"><video id="vidBefore" controls playsinline></video></div></div>
            <div><h2>방송급 자동 컷편집 (After)</h2><div class="phone-stage" style="max-width:300px;"><video id="vidAfter" controls playsinline></video></div></div>
          </div>
          <p id="cutSummary" class="muted" style="margin-top:14px;"></p>
        </div>
      </div>
    </section>

    <!-- VIEW 3: 140 HOOKS ENGINE -->
    <section id="view-hooks" class="view">
      <div class="panel">
        <h2>3초 후킹 문장 140개 실시간 생성기</h2>
        <div class="form-grid">
          <div><label>업종</label><input id="hkIndustry" value="피부과·의료 전문직" oninput="renderHooks()" /></div>
          <div><label>주제</label><input id="hkTopic" value="비수술 리프팅 시술 선택법" oninput="renderHooks()" /></div>
          <div><label>비교 A</label><input id="hkA" value="울쎄라" oninput="renderHooks()" /></div>
          <div><label>비교 B</label><input id="hkB" value="써마지" oninput="renderHooks()" /></div>
          <div>
            <label>카테고리</label>
            <select id="hkCat" onchange="renderHooks()">
              <option value="all">전체 (140개)</option>
              <option value="info_gap">정보 격차·미공개형 (20)</option>
              <option value="comparison">직접 비교·선택형 (20)</option>
              <option value="loss_warning">실수·손실 경고형 (20)</option>
              <option value="listicle_number">숫자·리스트·속도형 (20)</option>
              <option value="contrarian">반전·고정관념 파괴형 (20)</option>
              <option value="authority_pro">전문직·신뢰·데이터형 (20)</option>
              <option value="story_empathy">스토리·공감·경험형 (20)</option>
            </select>
          </div>
        </div>
        <div id="hookCount" class="muted" style="margin-bottom:10px;"></div>
        <div id="hookList" class="hook-list"></div>
      </div>
    </section>

    <!-- VIEW 4: SALES & CONTRACT -->
    <section id="view-sales" class="view">
      <div class="grid-2">
        <div class="panel"><div style="display:flex;justify-content:space-between;align-items:center;"><h2>Threads 무료 3편 포트폴리오 모객글</h2><button class="btn" onclick="copyById('acq1')">복사</button></div><pre id="acq1">{_esc(acq['threads_free_sample_post'])}</pre></div>
        <div class="panel"><div style="display:flex;justify-content:space-between;align-items:center;"><h2>Threads 성과 자랑(인사이트 보드)</h2><button class="btn" onclick="copyById('acq2')">복사</button></div><pre id="acq2">{_esc(acq['threads_insight_proof_post'])}</pre></div>
        <div class="panel"><div style="display:flex;justify-content:space-between;align-items:center;"><h2>숨고(Soomgo) 10+2 보너스 제안서</h2><button class="btn" onclick="copyById('acq3')">복사</button></div><pre id="acq3">{_esc(acq['soomgo_proposal_template'])}</pre></div>
        <div class="panel"><div style="display:flex;justify-content:space-between;align-items:center;"><h2>B2B 표준 계약서 (수정 2회 제한)</h2><button class="btn" onclick="copyById('acq4')">복사</button></div><pre id="acq4">{_esc(acq['b2b_contract_guardrails_md'])}</pre></div>
      </div>
    </section>

    <!-- VIEW 5: ECONOMICS & FORENSIC AUDIT -->
    <section id="view-audit" class="view">
      <div class="panel">
        <h2>현실적 B2B 외주 단가 · CAC · 실질 시급 시뮬레이터</h2>
        <p class="muted" style="margin-bottom:14px;">{_esc(econ['reality_check_summary'])}</p>
        <div class="table-wrap"><table><thead><tr><th>성장 단계</th><th>편수</th><th>패키지</th><th>편당</th><th>총 시간</th><th>실질 시급</th><th>50만/300만/1천만 고객수</th><th>전략</th></tr></thead><tbody>{econ_rows}</tbody></table></div>
      </div>
      <div class="panel">
        <h2>원본 영상 정밀 팩트체크 &amp; 감사 매트릭스</h2>
        <p class="muted" style="margin-bottom:14px;">원본: <a href="{_esc(VIDEO_SOURCE['url'])}" target="_blank" style="color:#fafafa">{_esc(VIDEO_SOURCE['title'])}</a></p>
        <div class="table-wrap"><table><thead><tr><th>핵심 주제</th><th>영상 주장</th><th>판정</th><th>리스크·과장</th><th>구조적 해결책</th></tr></thead><tbody>{audit_rows}</tbody></table></div>
      </div>
    </section>

    <!-- VIEW 6: MONETIZATION FUNNEL & DRIP CRM -->
    <section id="view-monetize" class="view">
      <div class="panel">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
          <div>
            <h2>B2B 수주 랜딩 퍼널 &amp; 3단계 자동 드립 CRM</h2>
            <div class="muted">ROI 계산기 + GitHub Pages 정적 무손실 리드 캡처 + D+0/D+2/D+5 팔로업 시퀀스 자동 생성</div>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <a class="btn primary" href="../public_funnel/index.html" target="_blank">공개 B2B 수주 페이지 열기 ↗</a>
            <button class="btn accent-btn" onclick="refreshCrm()">CRM 새로고침</button>
          </div>
        </div>
        <div class="metrics" style="margin-top:16px;margin-bottom:0;">
          <div class="metric"><div class="metric-k">누적 인바운드 리드</div><div class="metric-v" id="crmLeads">0건</div><div class="metric-s">자동 제안서 + 3단계 드립 생성</div></div>
          <div class="metric"><div class="metric-k">예상 월 매출 (MRR 파이프라인)</div><div class="metric-v accent" id="crmMrr">0원</div><div class="metric-s">확정 MRR: <span id="crmWon">0원</span></div></div>
          <div class="metric"><div class="metric-k">YouTube Shorts 배포 큐</div><div class="metric-v">{yt_count}편</div><div class="metric-s">UTM 수주 링크·고정댓글 포함</div></div>
        </div>
      </div>
      <div class="panel">
        <h2>실시간 리드 CRM &amp; 3단계 드립 원클릭 복사</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th>리드 ID</th><th>브랜드명</th><th>패키지</th><th>예상 MRR</th><th>단계 전환</th><th>3단계 드립 복사</th></tr></thead>
            <tbody id="crmTableBody"><tr><td colspan="6" class="muted">불러오는 중...</td></tr></tbody>
          </table>
        </div>
      </div>
    </section>
  </main>
</div>
<div id="toast" class="toast"></div>

<script>
  const HOOKS = {hooks_catalog_json};
  const PROJECTS = {projects_json};
  let activeProjIdx = 0;
  let activePersona = 'professional';

  function escHtml(s) {{
    return String(s ?? '').replace(/[&<>"']/g, m => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[m]));
  }}
  function toast(msg) {{
    const t = document.getElementById('toast');
    t.textContent = msg; t.style.display = 'block';
    clearTimeout(t._tid); t._tid = setTimeout(() => t.style.display = 'none', 2600);
  }}
  function switchView(id, btn) {{
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('view-' + id).classList.add('active');
    if (btn) btn.classList.add('active');
  }}

  function setSafeZone(elId, mode, btn) {{
    if (btn && btn.parentElement) {{
      btn.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    }}
    const el = document.getElementById(elId);
    if (mode === 'off') {{ el.classList.remove('on'); el.innerHTML = ''; return; }}
    const cfg = mode === 'yt'
      ? {{ top: 14, bot: 28, right: 18, label: 'YT SHORTS' }}
      : {{ top: 15, bot: 32, right: 16, label: 'IG REELS' }};
    el.classList.add('on');
    el.innerHTML = `
      <div class="sz-top" style="top:0;left:0;right:0;height:${{cfg.top}}%">TOP UI (${{cfg.top}}%)</div>
      <div class="sz-bot" style="bottom:0;left:0;right:0;height:${{cfg.bot}}%">CAPTION / AUDIO UI (${{cfg.bot}}%)</div>
      <div class="sz-right" style="top:${{cfg.top}}%;bottom:${{cfg.bot}}%;right:0;width:${{cfg.right}}%">ACTION</div>
      <div class="sz-safe" style="top:${{cfg.top}}%;bottom:${{cfg.bot}}%;left:0;right:${{cfg.right}}%"></div>
    `;
  }}

  function initProjectTabs() {{
    const el = document.getElementById('projectTabs');
    el.innerHTML = '';
    PROJECTS.forEach((p, idx) => {{
      const btn = document.createElement('button');
      btn.className = 'btn';
      btn.textContent = p.script.client_name;
      btn.onclick = () => selectProject(idx);
      el.appendChild(btn);
    }});
    document.getElementById('metricProjCount').textContent = PROJECTS.length + '편';
    if (PROJECTS.length) selectProject(0);
  }}

  function selectProject(idx) {{
    activeProjIdx = idx;
    document.querySelectorAll('#projectTabs button').forEach((b, i) => b.classList.toggle('active', i === idx));
    const p = PROJECTS[idx];
    activePersona = p.script.selected_persona || 'professional';

    const v = document.getElementById('projVideo');
    v.src = p.deliverable.mp4_relative_url;
    v.load();

    document.getElementById('projStats').innerHTML =
      `성우: <strong>${{escHtml(p.deliverable.voice_name || 'KO-Neural')}}</strong> · 길이 <strong>${{escHtml(p.deliverable.final_duration_sec)}}초</strong> ` +
      `(<span style="color:#4ade80">-${{escHtml(p.deliverable.compression_pct)}}%</span> · -14 LUFS)`;

    const cid = encodeURIComponent(p.script.client_id);
    document.getElementById('projExports').innerHTML =
      `<a class="btn primary sm" href="/api/download-bundle/${{cid}}" download>📦 납품 ZIP 일괄 다운로드</a>` +
      `<span class="tag live">MP4 (${{(p.deliverable.mp4_byte_size/1024).toFixed(0)}}KB)</span>` +
      `<span class="tag">.SRT</span><span class="tag">CapCut</span><span class="tag">Premiere</span>`;

    // Render 5-Axis A/B/C Variant Scorecard
    const vg = document.getElementById('variantGrid');
    const vars = p.script.hook_variants || [];
    vg.innerHTML = vars.map(vr => `
      <div class="variant-card ${{vr.variant === p.script.winning_variant ? 'win' : ''}}">
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
          <strong>Variant ${{escHtml(vr.variant)}} · ${{escHtml(vr.scorecard.total_score)}}점 (${{escHtml(vr.scorecard.grade)}})</strong>
          ${{vr.variant === p.script.winning_variant ? '<span class="tag gold">WINNER</span>' : ''}}
        </div>
        <div style="color:#e4e4e7;margin-bottom:6px;">${{escHtml(vr.rendered_hook)}}</div>
        <div class="muted" style="font-size:11px;">3초 잔존 ${{escHtml(vr.scorecard.predicted_3s_hold_pct)}}% · 완시 ${{escHtml(vr.scorecard.predicted_completion_pct)}}%</div>
      </div>
    `).join('');

    document.getElementById('projPrompt').textContent = p.script.llm_upgrade_prompt;
    renderPersonaTabs(p.script.personas);
    renderScenes(p.script.personas[activePersona].scenes);
  }}

  function renderPersonaTabs(personas) {{
    const el = document.getElementById('personaTabs');
    el.innerHTML = '';
    Object.keys(personas).forEach(k => {{
      const btn = document.createElement('button');
      btn.className = 'btn sm' + (k === activePersona ? ' active' : '');
      btn.textContent = personas[k].label;
      btn.onclick = () => {{ activePersona = k; renderPersonaTabs(personas); renderScenes(personas[k].scenes); }};
      el.appendChild(btn);
    }});
  }}

  function renderScenes(scenes) {{
    document.getElementById('sceneList').innerHTML = scenes.map(s => `
      <div class="scene-row">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:4px;">
          <span class="mono" style="color:#a1a1aa">${{escHtml(s.stage)}}</span>
          <span class="tag gold">${{escHtml(s.highlight_keyword)}}</span>
        </div>
        <div style="font-size:14px;font-weight:600;">${{escHtml(s.subtitle)}}</div>
        <div class="muted" style="font-size:12px;margin-top:4px;">${{escHtml(s.camera_direction)}}</div>
      </div>
    `).join('');
  }}

  function renderHooks() {{
    const ind = document.getElementById('hkIndustry').value || '전문직';
    const top = document.getElementById('hkTopic').value || '숏폼 마케팅';
    const a = document.getElementById('hkA').value || 'A안';
    const b = document.getElementById('hkB').value || 'B안';
    const cat = document.getElementById('hkCat').value;
    const filtered = HOOKS.filter(h => cat === 'all' || h.category === cat);
    document.getElementById('hookCount').textContent = `${{filtered.length}} / ${{HOOKS.length}} templates`;
    document.getElementById('hookList').innerHTML = filtered.map(h => {{
      const txt = h.template.replaceAll('{{industry}}', ind).replaceAll('{{topic}}', top).replaceAll('{{compare_a}}', a).replaceAll('{{compare_b}}', b);
      return `<div class="hook-row"><div><span class="tag">${{escHtml(h.hook_id)}}</span> <span style="margin-left:8px;">${{escHtml(txt)}}</span></div><button class="btn sm" onclick="navigator.clipboard.writeText(this.dataset.t);toast('후킹 문구 복사 완료')" data-t="${{escHtml(txt)}}">복사</button></div>`;
    }}).join('');
  }}

  async function generateNewClient() {{
    const btn = document.getElementById('btnGenClient');
    const st = document.getElementById('genStatus');
    btn.disabled = true;
    st.textContent = '⏳ WordBoundary 카라오케 + -14 LUFS 마스터링 + ZIP 패키징 중...';
    try {{
      const res = await fetch('/api/generate-client', {{
        method: 'POST', headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          client_name: document.getElementById('newName').value,
          industry: document.getElementById('newInd').value,
          topic: document.getElementById('newTopic').value,
          compare_a: document.getElementById('newA').value,
          compare_b: document.getElementById('newB').value,
          persona_tone: document.getElementById('newTone').value,
        }})
      }});
      const data = await res.json();
      if (!data.ok) throw new Error(data.error);
      PROJECTS.unshift(data.project);
      initProjectTabs();
      st.textContent = '✅ 제작 완료! 새 클라이언트 릴스와 납품 ZIP이 즉시 반영되었습니다.';
      toast('신규 v4.0 릴스 + 납품 ZIP 생성 완료');
    }} catch (e) {{
      st.textContent = '❌ 오류: ' + e.message;
    }} finally {{
      btn.disabled = false;
    }}
  }}

  const dz = document.getElementById('dropzone');
  dz.addEventListener('dragover', e => {{ e.preventDefault(); dz.classList.add('drag'); }});
  dz.addEventListener('dragleave', () => dz.classList.remove('drag'));
  dz.addEventListener('drop', e => {{ e.preventDefault(); dz.classList.remove('drag'); if (e.dataTransfer.files.length) handleMp4File(e.dataTransfer.files[0]); }});

  function handleMp4File(file) {{
    if (!file) return;
    const st = document.getElementById('cutStatus');
    const bar = document.getElementById('cutProgBar');
    const fill = document.getElementById('cutProgFill');
    bar.style.display = 'block'; fill.style.width = '0%';
    st.textContent = `⏳ "${{file.name}}" 업로드 중...`;

    const db = document.getElementById('cutDb').value;
    const minS = document.getElementById('cutMin').value;
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `/api/autocut-upload?filename=${{encodeURIComponent(file.name)}}&silence_db=${{db}}&min_silence=${{minS}}`);
    xhr.upload.onprogress = ev => {{
      if (ev.lengthComputable) {{
        const pct = Math.round((ev.loaded / ev.total) * 100);
        fill.style.width = pct + '%';
        st.textContent = pct < 100 ? `⏳ 업로드 중 (${{pct}}%)...` : '⏳ FFmpeg 무음 컷편집 + -14 LUFS 마스터링 실행 중...';
      }}
    }};
    xhr.onload = () => {{
      try {{
        const data = JSON.parse(xhr.responseText);
        if (!data.ok) throw new Error(data.error);
        const r = data.result;
        fill.style.width = '100%';
        st.textContent = `✅ 완료! 원본 ${{r.raw_duration_sec}}초 → 컷편집 ${{r.final_duration_sec}}초 (-${{r.compression_pct}}%, 무음 ${{r.silence_gaps_removed}}구간 제거)`;
        document.getElementById('cutResult').style.display = 'block';
        document.getElementById('vidBefore').src = r.input_relative_url;
        document.getElementById('vidAfter').src = r.output_relative_url;
        document.getElementById('cutSummary').textContent = `15ms 클릭 방지 + -14 LUFS 마스터링 · CapCut & Premiere FCPXML 생성 완료`;
        toast('실사 MP4 무음 자동 컷편집 완료');
      }} catch (err) {{
        st.textContent = '❌ 실패: ' + err.message;
      }}
    }};
    xhr.onerror = () => {{ st.textContent = '❌ 네트워크 오류'; }};
    xhr.send(file);
  }}

  async function updateLeadStage(leadId, stage) {{
    try {{
      const r = await fetch('/api/crm/stage', {{
        method: 'POST', headers: {{'Content-Type':'application/json'}},
        body: JSON.stringify({{ lead_id: leadId, stage }})
      }});
      const d = await r.json();
      if (d.ok) {{ toast(`리드 단계 변경: ${{stage}}`); refreshCrm(); }}
    }} catch (e) {{}}
  }}

  async function refreshCrm() {{
    try {{
      const r = await fetch('/api/crm');
      const d = await r.json();
      document.getElementById('crmLeads').textContent = (d.total_leads || 0) + '건';
      document.getElementById('crmMrr').textContent = (d.projected_mrr_krw || 0).toLocaleString() + '원';
      document.getElementById('crmWon').textContent = (d.closed_won_mrr_krw || 0).toLocaleString() + '원';
      const tb = document.getElementById('crmTableBody');
      if (!d.leads || !d.leads.length) {{
        tb.innerHTML = '<tr><td colspan="6" class="muted">아직 접수된 리드가 없습니다.</td></tr>';
        return;
      }}
      window._crmLeads = d.leads;
      tb.innerHTML = d.leads.map((l, idx) => {{
        const drips = (l.follow_up_drip || []).map((dr, di) =>
          `<button class="btn sm" onclick="navigator.clipboard.writeText(window._crmLeads[${{idx}}].follow_up_drip[${{di}}].message);toast('${{escHtml(dr.day)}} 메시지 복사됨')">${{escHtml(dr.day.split(' ')[0])}}</button>`
        ).join(' ');
        return `
          <tr>
            <td class="mono">${{escHtml(l.lead_id)}}</td>
            <td><strong>${{escHtml(l.brand_name)}}</strong><div class="muted" style="font-size:11px;">${{escHtml(l.industry)}}</div></td>
            <td>${{escHtml(l.package_label)}}</td>
            <td class="mono accent">${{(l.expected_mrr_krw||0).toLocaleString()}}원</td>
            <td>
              <select style="padding:4px 8px;font-size:12px;" onchange="updateLeadStage('${{escHtml(l.lead_id)}}', this.value)">
                ${{['PROPOSAL_AUTO_SENT','DRIP_D2_SENT','DRIP_D5_SENT','CLOSED_WON','LOST'].map(st =>
                  `<option value="${{st}}" ${{l.stage===st?'selected':''}}>${{st}}</option>`).join('')}}
              </select>
            </td>
            <td style="display:flex;gap:4px;flex-wrap:wrap;">${{drips || '<span class="muted">-</span>'}}</td>
          </tr>`;
      }}).join('');
    }} catch (e) {{}}
  }}

  function copyById(id) {{
    navigator.clipboard.writeText(document.getElementById(id).textContent);
    toast('클립보드에 복사되었습니다');
  }}

  initProjectTabs();
  renderHooks();
  refreshCrm();
</script>
</body>
</html>
"""
        out_html.write_text(doc, encoding="utf-8")
        return out_html
