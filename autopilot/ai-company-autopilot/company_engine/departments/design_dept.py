"""Department 3: 디자인팀 (Design) — Automated 1080x1350 5-Slide SNS Card News Renderer."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont

from company_engine.config import CompanyConfig
from company_engine.master_verifier import compute_sha256

CARD_W = 1080
CARD_H = 1350


class DesignDepartment:
    """Renders 5 high-contrast 1080x1350 Korean SNS Card News PNG slides at $0 cost."""

    dept_id = "design"
    dept_name_ko = "디자인팀"

    def __init__(self, config: CompanyConfig) -> None:
        self.config = config

    def run(self, run_date: str, card_brief: Dict[str, Any]) -> Dict[str, Any]:
        out_dir = self.config.output_dir / "design" / f"{run_date}_card_news"
        out_dir.mkdir(parents=True, exist_ok=True)

        font_black = str(self.config.resolve_font("black"))
        font_bold = str(self.config.resolve_font("bold"))

        slides_meta: List[Dict[str, Any]] = []
        evidence: List[Dict[str, Any]] = []

        # Slide 1: Cover
        s1_path = out_dir / "slide_01_cover.png"
        self._render_cover(
            s1_path,
            badge=card_brief["badge"],
            headline=card_brief["cover_headline"],
            sub=card_brief["cover_sub"],
            date_label=run_date,
            font_black=font_black,
            font_bold=font_bold,
        )
        slides_meta.append(self._slide_info(1, "표지 (Hook Cover)", s1_path))
        evidence.append(self._png_evidence("카드뉴스 1장 (표지)", s1_path))

        # Slides 2..4: Content Data Cards
        for idx, slide_data in enumerate(card_brief["slides"], start=2):
            sp = out_dir / f"slide_0{idx}_insight.png"
            self._render_content_slide(
                sp,
                slide_num=idx,
                total_slides=5,
                tag=slide_data["tag"],
                headline=slide_data["headline"],
                body=slide_data["body"],
                metric_label=slide_data["metric_label"],
                metric_value=slide_data["metric_value"],
                font_black=font_black,
                font_bold=font_bold,
            )
            slides_meta.append(self._slide_info(idx, slide_data["tag"], sp))
            evidence.append(self._png_evidence(f"카드뉴스 {idx}장 ({slide_data['tag']})", sp))

        # Slide 5: CTA Slide
        s5_path = out_dir / "slide_05_cta.png"
        self._render_cta_slide(
            s5_path,
            headline=card_brief["cta_headline"],
            url=card_brief["cta_url"],
            sub=card_brief["cta_sub"],
            font_black=font_black,
            font_bold=font_bold,
        )
        slides_meta.append(self._slide_info(5, "CTA 마무리", s5_path))
        evidence.append(self._png_evidence("카드뉴스 5장 (CTA)", s5_path))

        manifest = {
            "dept_id": self.dept_id,
            "dept_name_ko": self.dept_name_ko,
            "run_date": run_date,
            "format": f"{CARD_W}x{CARD_H} PNG (4:5 Instagram/YouTube Community)",
            "slide_count": len(slides_meta),
            "slides": slides_meta,
        }
        manifest_path = out_dir / "card_news_manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        evidence.append(
            {
                "label": "디자인팀 카드뉴스 매니페스트 JSON",
                "type": "json",
                "file_path": str(manifest_path),
                "sha256": compute_sha256(manifest_path),
            }
        )

        return {
            "dept_id": self.dept_id,
            "dept_name_ko": self.dept_name_ko,
            "status": "COMPLETED",
            "summary": {
                "slides_rendered": len(slides_meta),
                "resolution": f"{CARD_W}x{CARD_H}",
                "render_cost_usd": 0.0,
                "output_dir": str(out_dir),
            },
            "slides": slides_meta,
            "manifest_path": str(manifest_path),
            "evidence": evidence,
        }

    def _slide_info(self, index: int, title: str, path: Path) -> Dict[str, Any]:
        rel_from_output = path.relative_to(self.config.output_dir).as_posix()
        return {
            "slide_index": index,
            "title": title,
            "file_path": str(path),
            "relative_url": f"../{rel_from_output}",
            "sha256": compute_sha256(path),
            "byte_size": path.stat().st_size,
        }

    def _png_evidence(self, label: str, path: Path) -> Dict[str, Any]:
        return {
            "label": label,
            "type": "png",
            "file_path": str(path),
            "sha256": compute_sha256(path),
            "expected_size": [CARD_W, CARD_H],
        }

    def _create_gradient_bg(self, top_rgb: Tuple[int, int, int], bottom_rgb: Tuple[int, int, int]) -> Image.Image:
        img = Image.new("RGB", (CARD_W, CARD_H), top_rgb)
        draw = ImageDraw.Draw(img)
        for y in range(CARD_H):
            ratio = y / (CARD_H - 1)
            r = int(top_rgb[0] + (bottom_rgb[0] - top_rgb[0]) * ratio)
            g = int(top_rgb[1] + (bottom_rgb[1] - top_rgb[1]) * ratio)
            b = int(top_rgb[2] + (bottom_rgb[2] - top_rgb[2]) * ratio)
            draw.line([(0, y), (CARD_W, y)], fill=(r, g, b))
        return img

    def _draw_footer(self, draw: ImageDraw.ImageDraw, slide_num: int, total: int, font_small: ImageFont.FreeTypeFont) -> None:
        draw.line([(72, CARD_H - 118), (CARD_W - 72, CARD_H - 118)], fill=(45, 58, 86), width=2)
        draw.text((72, CARD_H - 90), self.config.company_name.upper(), fill=(148, 163, 184), font=font_small)
        page_str = f"0{slide_num} / 0{total}"
        bbox = draw.textbbox((0, 0), page_str, font=font_small)
        draw.text((CARD_W - 72 - (bbox[2] - bbox[0]), CARD_H - 90), page_str, fill=(56, 189, 248), font=font_small)

    def _render_cover(
        self,
        path: Path,
        badge: str,
        headline: str,
        sub: str,
        date_label: str,
        font_black: str,
        font_bold: str,
    ) -> None:
        img = self._create_gradient_bg((11, 18, 36), (17, 29, 58))
        draw = ImageDraw.Draw(img)

        # Accent decorative shapes
        draw.rounded_rectangle([72, 92, 540, 152], radius=30, fill=(245, 158, 11))
        f_badge = ImageFont.truetype(font_bold, 28)
        f_head = ImageFont.truetype(font_black, 76)
        f_sub = ImageFont.truetype(font_bold, 34)
        f_small = ImageFont.truetype(font_bold, 26)

        draw.text((100, 105), badge, fill=(10, 15, 30), font=f_badge)
        draw.text((72, 220), f"DAILY REPORT · {date_label}", fill=(56, 189, 248), font=f_small)

        y = 290
        for line in headline.split("\n"):
            draw.text((72, y), line, fill=(248, 250, 252), font=f_head)
            y += 104

        # Highlight panel
        draw.rounded_rectangle([72, y + 60, CARD_W - 72, y + 260], radius=24, fill=(24, 39, 74), outline=(56, 189, 248), width=3)
        wrapped_sub = textwrap.wrap(sub, width=26)
        sy = y + 102
        for wline in wrapped_sub[:3]:
            draw.text((110, sy), wline, fill=(226, 232, 240), font=f_sub)
            sy += 50

        # Swipe indicator pill
        draw.rounded_rectangle([72, CARD_H - 240, 420, CARD_H - 170], radius=35, fill=(30, 64, 175))
        draw.text((112, CARD_H - 222), "옆으로 넘겨서 확인 →", fill=(255, 255, 255), font=f_small)

        self._draw_footer(draw, 1, 5, f_small)
        img.save(path, format="PNG", optimize=True)

    def _render_content_slide(
        self,
        path: Path,
        slide_num: int,
        total_slides: int,
        tag: str,
        headline: str,
        body: str,
        metric_label: str,
        metric_value: str,
        font_black: str,
        font_bold: str,
    ) -> None:
        img = self._create_gradient_bg((12, 20, 40), (19, 32, 62))
        draw = ImageDraw.Draw(img)

        f_tag = ImageFont.truetype(font_bold, 28)
        f_head = ImageFont.truetype(font_black, 62)
        f_body = ImageFont.truetype(font_bold, 36)
        f_mlabel = ImageFont.truetype(font_bold, 28)
        f_mval = ImageFont.truetype(font_black, 66)
        f_small = ImageFont.truetype(font_bold, 26)

        # Tag pill
        draw.rounded_rectangle([72, 96, 560, 156], radius=28, fill=(30, 41, 74), outline=(56, 189, 248), width=2)
        draw.text((100, 110), tag, fill=(56, 189, 248), font=f_tag)

        # Headline
        y = 210
        for line in headline.split("\n"):
            draw.text((72, y), line, fill=(248, 250, 252), font=f_head)
            y += 86

        # Body paragraph
        y += 38
        for wline in textwrap.wrap(body, width=24)[:6]:
            draw.text((72, y), wline, fill=(203, 213, 225), font=f_body)
            y += 56

        # Metric highlight box
        box_top = 860
        draw.rounded_rectangle(
            [72, box_top, CARD_W - 72, box_top + 250],
            radius=28,
            fill=(15, 28, 56),
            outline=(245, 158, 11),
            width=3,
        )
        draw.text((116, box_top + 40), metric_label, fill=(251, 191, 36), font=f_mlabel)
        draw.text((116, box_top + 106), metric_value, fill=(255, 255, 255), font=f_mval)

        self._draw_footer(draw, slide_num, total_slides, f_small)
        img.save(path, format="PNG", optimize=True)

    def _render_cta_slide(
        self,
        path: Path,
        headline: str,
        url: str,
        sub: str,
        font_black: str,
        font_bold: str,
    ) -> None:
        img = self._create_gradient_bg((15, 23, 48), (9, 15, 32))
        draw = ImageDraw.Draw(img)

        f_head = ImageFont.truetype(font_black, 70)
        f_url = ImageFont.truetype(font_bold, 34)
        f_sub = ImageFont.truetype(font_bold, 32)
        f_small = ImageFont.truetype(font_bold, 26)

        draw.rounded_rectangle([72, 110, 380, 170], radius=30, fill=(16, 185, 129))
        draw.text((104, 123), "ACTION NOW", fill=(6, 20, 18), font=f_small)

        y = 250
        for line in headline.split("\n"):
            draw.text((72, y), line, fill=(248, 250, 252), font=f_head)
            y += 96

        # URL CTA button
        draw.rounded_rectangle([72, 560, CARD_W - 72, 690], radius=24, fill=(56, 189, 248))
        draw.text((110, 604), url, fill=(9, 15, 32), font=f_url)

        draw.text((72, 760), sub, fill=(203, 213, 225), font=f_sub)
        draw.text((72, 825), "✔ 좋아요 · 저장 · 프로필 링크에서 바로 확인", fill=(251, 191, 36), font=f_sub)

        self._draw_footer(draw, 5, 5, f_small)
        img.save(path, format="PNG", optimize=True)
