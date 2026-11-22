"""Executive HQ Web Dashboard Builder — Interactive Single-File Command Center."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Dict

from company_engine.config import VIDEO_8STEP_AUDIT, VIDEO_SOURCE


def _esc(val: Any) -> str:
    return html.escape(str(val), quote=True)


class StudioBuilder:
    """Renders `output/studio/index.html` with live department results, PNG carousel, and 1-click copy packs."""

    def build(self, payload: Dict[str, Any], out_html: Path) -> Path:
        out_html.parent.mkdir(parents=True, exist_ok=True)

        run_date = payload["run_date"]
        master = payload["master_verification"]
        econ = payload["economics"]
        depts = payload["departments"]
        planner = depts["planner"]
        dev = depts["dev"]
        design = depts["design"]
        cs = depts["cs"]
        marketing = depts["marketing"]
        starter = payload["starter_pack"]

        verdict_ok = master["overall_verdict"] == "ALL_VERIFIED_PASS"
        verdict_badge = (
            '<span class="pill pill-green">✔ ALL VERIFIED PASS (SHA-256)</span>'
            if verdict_ok
            else '<span class="pill pill-red">✖ REJECTED UNVERIFIED CLAIMS</span>'
        )

        # Department status cards
        dept_cards_html = []
        for did, dinfo in master["departments"].items():
            ok = dinfo["master_verdict"] == "APPROVED"
            badge = '<span class="pill pill-green">APPROVED</span>' if ok else '<span class="pill pill-red">REJECTED</span>'
            checks_li = "".join(
                f"<li><code>{_esc(c.get('label', Path(c['file_path']).name))}</code> — "
                f"<span class='mono-dim'>{_esc(c.get('proof', {}).get('sha256_prefix', 'N/A'))}… "
                f"({c.get('proof', {}).get('byte_size', 0):,}B)</span></li>"
                for c in dinfo["checks"]
            )
            dept_cards_html.append(
                f"""
                <div class="card">
                  <div class="card-head">
                    <h3>{_esc(dinfo['dept_name_ko'])} <span class="sub-id">@{_esc(did)}</span></h3>
                    {badge}
                  </div>
                  <p class="muted">증거 검증: <strong>{dinfo['verified_count']} / {dinfo['evidence_count']}</strong> 통과</p>
                  <ul class="evidence-list">{checks_li}</ul>
                </div>
                """
            )

        # 8-step video audit rows
        audit_rows = "".join(
            f"""
            <tr>
              <td><strong>{_esc(row['step'])}</strong></td>
              <td>{_esc(row['video_claim'])}</td>
              <td><span class="pill pill-blue">{_esc(row['verdict'])}</span></td>
              <td class="risk-cell">{_esc(row['risk_found'])}</td>
              <td class="sol-cell">{_esc(row['our_solution'])}</td>
            </tr>
            """
            for row in VIDEO_8STEP_AUDIT
        )

        # Economics rows
        econ_rows = "".join(
            f"""
            <tr class="{'row-highlight' if t['recommended'] else ''}">
              <td><strong>{_esc(t['name'])}</strong></td>
              <td>{_esc(t['architecture'])}</td>
              <td class="num">${t['monthly_total_usd']:.2f}/월</td>
              <td class="num">{t['bep_adsense_pv']:,} PV</td>
              <td class="num">{t['bep_cpa_conversions']}건</td>
              <td>{_esc(t['verdict_ko'])}</td>
            </tr>
            """
            for t in econ["tiers"]
        )

        # Site SEO Audit cards
        site_cards = []
        for sa in planner.get("site_audits", []):
            flags = []
            for label, ok in [
                ("robots.txt", sa["has_robots_txt"]),
                ("sitemap.xml", sa["has_sitemap_xml"]),
                ("ads.txt", sa["has_ads_txt"]),
                ("llms.txt", sa["has_llms_txt"]),
            ]:
                cls = "pill-green" if ok else "pill-amber"
                flags.append(f'<span class="pill {cls}">{label}</span>')
            gap_items = "".join(
                f"<li><code>{_esc(g['page'])}</code> — {_esc(', '.join(g['issues']))} "
                f"<span class='pill pill-amber'>{_esc(g['priority'])}</span></li>"
                for g in sa["seo_gaps"][:8]
            ) or "<li>발견된 SEO 갭이 없습니다.</li>"
            site_cards.append(
                f"""
                <div class="card">
                  <div class="card-head">
                    <h3>{_esc(sa['site_name'])}</h3>
                    <span class="score-big">{sa['seo_score']}점</span>
                  </div>
                  <p class="muted">스캔 페이지: <strong>{sa['html_pages_scanned']}개</strong> · Sitemap URL: <strong>{sa['sitemap_url_count']}개</strong></p>
                  <div class="pill-row">{''.join(flags)}</div>
                  <ul class="evidence-list">{gap_items}</ul>
                </div>
                """
            )

        # CS Tickets rows
        cs_rows = "".join(
            f"""
            <tr>
              <td><code>{_esc(t['ticket_id'])}</code></td>
              <td>{_esc(t['customer_name'])}</td>
              <td><strong>{_esc(t['subject'])}</strong></td>
              <td><span class="pill pill-blue">{_esc(t['category'])}</span></td>
              <td><code>@{_esc(t['routed_dept'])}</code></td>
              <td>{'<span class="pill pill-amber">대표자 승인 필요</span>' if t['requires_human_approval'] else '<span class="pill pill-green">자동 초안 완료</span>'}</td>
              <td class="draft-cell">{_esc(t['draft_reply'])}</td>
            </tr>
            """
            for t in cs.get("tickets", [])
        )

        # Card News Slides JSON for JS carousel
        slides_json = json.dumps(design.get("slides", []), ensure_ascii=False)
        channels_json = json.dumps(marketing.get("channels", {}), ensure_ascii=False)
        snippets = starter.get("snippets", {})

        html_doc = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI Company Autopilot HQ — {run_date}</title>
  <style>
    :root {{
      --bg: #070c18; --panel: #0f172a; --panel-2: #16223b; --border: #243352;
      --text: #f1f5f9; --muted: #94a3b8; --blue: #38bdf8; --green: #10b981;
      --amber: #f59e0b; --red: #ef4444; --purple: #a78bfa;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Noto Sans KR', sans-serif;
      background: radial-gradient(circle at top right, #112240 0%, var(--bg) 55%);
      color: var(--text); line-height: 1.55;
    }}
    .wrap {{ max-width: 1320px; margin: 0 auto; padding: 28px 22px 80px; }}
    header {{
      display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start;
      gap: 16px; border-bottom: 1px solid var(--border); padding-bottom: 20px; margin-bottom: 26px;
    }}
    h1 {{ margin: 0; font-size: 28px; letter-spacing: -0.02em; }}
    h2 {{ margin: 36px 0 14px; font-size: 20px; color: var(--blue); display: flex; align-items: center; gap: 8px; }}
    h3 {{ margin: 0 0 8px; font-size: 16px; }}
    .sub-id {{ color: var(--muted); font-size: 13px; font-weight: 500; }}
    .muted {{ color: var(--muted); font-size: 13px; margin: 4px 0 10px; }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin-bottom: 26px; }}
    .kpi {{
      background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px;
    }}
    .kpi-label {{ font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }}
    .kpi-val {{ font-size: 26px; font-weight: 800; margin-top: 6px; color: #fff; }}
    .kpi-sub {{ font-size: 12px; color: var(--blue); margin-top: 4px; }}
    .grid-3 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }}
    .grid-2 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(460px, 1fr)); gap: 18px; }}
    .card {{
      background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 18px;
    }}
    .card-head {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 8px; }}
    .pill {{ display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }}
    .pill-green {{ background: rgba(16,185,129,0.16); color: #34d399; border: 1px solid rgba(16,185,129,0.4); }}
    .pill-red {{ background: rgba(239,68,68,0.16); color: #f87171; border: 1px solid rgba(239,68,68,0.4); }}
    .pill-blue {{ background: rgba(56,189,248,0.14); color: #7dd3fc; border: 1px solid rgba(56,189,248,0.35); }}
    .pill-amber {{ background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.35); }}
    .pill-row {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }}
    .evidence-list {{ margin: 8px 0 0; padding-left: 18px; font-size: 13px; color: #cbd5e1; }}
    .evidence-list li {{ margin-bottom: 5px; }}
    .mono-dim {{ font-family: ui-monospace, SFMono-Regular, monospace; font-size: 11px; color: var(--muted); }}
    .score-big {{ font-size: 22px; font-weight: 800; color: var(--amber); }}
    .table-wrap {{ overflow-x: auto; background: var(--panel); border: 1px solid var(--border); border-radius: 14px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid var(--border); text-align: left; vertical-align: top; }}
    th {{ background: var(--panel-2); color: var(--blue); font-weight: 700; white-space: nowrap; }}
    .row-highlight {{ background: rgba(16,185,129,0.08); }}
    .num {{ font-weight: 700; white-space: nowrap; }}
    .risk-cell {{ color: #fca5a5; }}
    .sol-cell {{ color: #a7f3d0; }}
    .draft-cell {{ max-width: 340px; color: #cbd5e1; }}
    .carousel-box {{ display: grid; grid-template-columns: 360px 1fr; gap: 22px; align-items: start; }}
    @media (max-width: 900px) {{ .carousel-box {{ grid-template-columns: 1fr; }} }}
    .slide-frame {{ background: #040710; border: 1px solid var(--border); border-radius: 14px; padding: 12px; text-align: center; }}
    .slide-frame img {{ width: 100%; max-width: 330px; border-radius: 10px; display: block; margin: 0 auto; }}
    .btn-row {{ display: flex; gap: 8px; justify-content: center; margin-top: 12px; flex-wrap: wrap; }}
    button {{
      background: var(--panel-2); color: var(--text); border: 1px solid var(--border);
      padding: 8px 14px; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 13px;
    }}
    button:hover {{ border-color: var(--blue); color: var(--blue); }}
    button.primary {{ background: var(--blue); color: #07101e; border-color: var(--blue); }}
    pre {{
      background: #060b16; border: 1px solid var(--border); border-radius: 10px;
      padding: 14px; overflow-x: auto; font-size: 12px; color: #e2e8f0; max-height: 280px; white-space: pre-wrap;
    }}
    .tabs {{ display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }}
    .tab-btn.active {{ background: var(--blue); color: #07101e; border-color: var(--blue); }}
  </style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>AI Company Autopilot HQ <span class="pill pill-blue">v1.0</span></h1>
      <p class="muted">
        원본 영상 정밀 해부: <a href="{_esc(VIDEO_SOURCE['url'])}" target="_blank" style="color:#38bdf8">{_esc(VIDEO_SOURCE['title'])}</a>
        ({ _esc(VIDEO_SOURCE['channel']) }) · 실행일: <strong>{_esc(run_date)}</strong>
      </p>
    </div>
    <div>{verdict_badge}</div>
  </header>

  <section class="kpi-grid">
    <div class="kpi">
      <div class="kpi-label">마스터 증거 검증률</div>
      <div class="kpi-val">{master['verification_pass_rate_pct']}%</div>
      <div class="kpi-sub">{master['verified_evidence_items']} / {master['total_evidence_items']} 산출물 SHA-256 검증</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">실제 사이트 스캔</div>
      <div class="kpi-val">{planner['summary']['total_html_pages_scanned']}p</div>
      <div class="kpi-sub">평균 SEO 점수 {planner['summary']['average_seo_score']}점</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">SNS 카드뉴스 렌더링</div>
      <div class="kpi-val">{design['summary']['slides_rendered']}장</div>
      <div class="kpi-sub">1080×1350 PNG · 제작비 $0</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">CS 자동 분류 / 에스컬레이션</div>
      <div class="kpi-val">{cs['summary']['total_tickets']}건</div>
      <div class="kpi-sub">스팸 {cs['summary']['spam_blocked']}건 차단 · 승인대기 {cs['summary']['escalated_to_human']}건</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">월간 토큰 비용 절감</div>
      <div class="kpi-val">${econ['savings_vs_full_agent_teams_usd_per_month']}</div>
      <div class="kpi-sub">풀 에이전트 팀($138) 대비 97% 절감</div>
    </div>
  </section>

  <h2>1. AI 직원 5개 부서 + 총괄 마스터 증거 검증 현황 (거짓말 방지 게이트)</h2>
  <div class="grid-3">{''.join(dept_cards_html)}</div>

  <h2>2. 디자인팀 SNS 카드뉴스 5장 캐러셀 &amp; 마케팅팀 배포 패키지</h2>
  <div class="card carousel-box">
    <div class="slide-frame">
      <img id="slideImg" src="" alt="SNS Card News Slide" />
      <p id="slideMeta" class="muted" style="margin-top:10px;"></p>
      <div class="btn-row">
        <button onclick="prevSlide()">← 이전 장</button>
        <button class="primary" onclick="nextSlide()">다음 장 →</button>
      </div>
    </div>
    <div>
      <div class="tabs" id="channelTabs"></div>
      <p id="channelUtm" class="muted"></p>
      <pre id="channelCaption"></pre>
      <button class="primary" onclick="copyText('channelCaption')">📋 채널 카피 복사</button>
    </div>
  </div>

  <h2>3. 기획팀 &amp; 개발팀 — 실제 보유 사이트 SEO·헬스 감사 결과</h2>
  <div class="grid-2">{''.join(site_cards)}</div>

  <h2>4. CS팀 — 고객 문의 자동 분류 &amp; 인간 승인 게이트</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr><th>티켓</th><th>고객</th><th>제목</th><th>분류</th><th>이관 부서</th><th>승인 상태</th><th>응답 초안</th></tr>
      </thead>
      <tbody>{cs_rows}</tbody>
    </table>
  </div>

  <h2>5. 운영 티어별 월간 토큰 원가 &amp; 손익분기점(BEP) 감사</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr><th>운영 티어</th><th>아키텍처</th><th>월 비용</th><th>AdSense BEP</th><th>CPA BEP</th><th>감사 판정</th></tr>
      </thead>
      <tbody>{econ_rows}</tbody>
    </table>
  </div>

  <h2>6. 영상 8단계 세팅법 전수 감사 매트릭스 (리스크 제거 &amp; 고도화)</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr><th>단계</th><th>영상 원안</th><th>판정</th><th>발견된 리스크</th><th>본 시스템의 구조적 해결책</th></tr>
      </thead>
      <tbody>{audit_rows}</tbody>
    </table>
  </div>

  <h2>7. Claude Code 8단계 원클릭 복붙 스타터 팩</h2>
  <div class="grid-2">
    <div class="card">
      <div class="card-head"><h3>③ 회사 업무 매뉴얼 (CLAUDE.md)</h3><button onclick="copyText('snipClaude')">복사</button></div>
      <pre id="snipClaude">{_esc(snippets.get('claude_md', ''))}</pre>
    </div>
    <div class="card">
      <div class="card-head"><h3>⑤ settings.json &amp; ⑦ /schedule 명령어</h3><button onclick="copyText('snipSched')">복사</button></div>
      <pre id="snipSched">{_esc(snippets.get('settings_json', ''))}\n\n{_esc(snippets.get('schedule_command', ''))}</pre>
    </div>
  </div>
</div>

<script>
  const SLIDES = {slides_json};
  const CHANNELS = {channels_json};
  let slideIdx = 0;

  function renderSlide() {{
    if (!SLIDES.length) return;
    const s = SLIDES[slideIdx];
    document.getElementById('slideImg').src = s.relative_url;
    document.getElementById('slideMeta').textContent =
      `[${{s.slide_index}} / ${{SLIDES.length}}] ${{s.title}} · SHA256: ${{s.sha256.slice(0,12)}}… (${{(s.byte_size/1024).toFixed(1)}} KB)`;
  }}
  function prevSlide() {{ slideIdx = (slideIdx - 1 + SLIDES.length) % SLIDES.length; renderSlide(); }}
  function nextSlide() {{ slideIdx = (slideIdx + 1) % SLIDES.length; renderSlide(); }}

  function renderChannels() {{
    const tabsEl = document.getElementById('channelTabs');
    const keys = Object.keys(CHANNELS);
    keys.forEach((k, idx) => {{
      const btn = document.createElement('button');
      btn.className = 'tab-btn' + (idx === 0 ? ' active' : '');
      btn.textContent = CHANNELS[k].channel_name;
      btn.onclick = () => selectChannel(k, btn);
      tabsEl.appendChild(btn);
    }});
    if (keys.length) selectChannel(keys[0], tabsEl.firstChild);
  }}

  function selectChannel(key, activeBtn) {{
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    if (activeBtn) activeBtn.classList.add('active');
    const ch = CHANNELS[key];
    document.getElementById('channelUtm').textContent = 'UTM 링크: ' + ch.utm_url;
    document.getElementById('channelCaption').textContent = ch.caption;
  }}

  function copyText(elId) {{
    const txt = document.getElementById(elId).textContent;
    navigator.clipboard.writeText(txt).then(() => alert('클립보드에 복사되었습니다!'));
  }}

  renderSlide();
  renderChannels();
</script>
</body>
</html>
"""
        out_html.write_text(html_doc, encoding="utf-8")
        return out_html
