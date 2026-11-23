"""1-Minute Interactive Helper to Issue KakaoTalk '나에게 보내기' Refresh Token & Register to GitHub Secrets."""

from __future__ import annotations

import base64
import json
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

REDIRECT_URI = "https://dream8837z.github.io/shortform-agency/"
REPO = "dream8837z/dream8837z.github.io"


def main() -> None:
    print("=== 카카오톡 '나에게 보내기' 1회 토큰 발급 & GitHub Secrets 자동 등록 ===")
    rest_key = input("1) 카카오 디벨로퍼스 REST API 키 입력: ").strip()
    client_secret = input("2) Client Secret (미사용 시 엔터): ").strip()

    auth_url = (
        f"https://kauth.kakao.com/oauth/authorize?client_id={urllib.parse.quote(rest_key)}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&response_type=code&scope=talk_message"
    )
    print("\n3) 아래 링크를 브라우저에서 열고 카카오 로그인 → '카카오톡 메시지 전송' 동의 후 이동된 주소의 `code=...` 값을 복사하세요:")
    print(auth_url)
    code = input("\n4) 리다이렉트 URL의 code 값 붙여넣기: ").strip()
    if "code=" in code:
        code = code.split("code=")[-1].split("&")[0]

    form = {
        "grant_type": "authorization_code",
        "client_id": rest_key,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
    if client_secret:
        form["client_secret"] = client_secret

    req = urllib.request.Request(
        "https://kauth.kakao.com/oauth/token",
        data=urllib.parse.urlencode(form).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode("utf-8"))

    refresh_token = data.get("refresh_token", "")
    if not refresh_token:
        raise SystemExit(f"토큰 발급 실패: {data}")

    # Save locally to .env
    env_path = Path(__file__).resolve().parent.parent / ".env"
    lines = [
        f"KAKAO_REST_API_KEY={rest_key}",
        f"KAKAO_REFRESH_TOKEN={refresh_token}",
    ]
    if client_secret:
        lines.append(f"KAKAO_CLIENT_SECRET={client_secret}")
    with env_path.open("a", encoding="utf-8") as f:
        f.write("\n" + "\n".join(lines) + "\n")
    print(f"✅ 로컬 .env 저장 완료: {env_path}")

    # Also register into GitHub Actions Secrets automatically if git credential exists
    try:
        from nacl import encoding, public

        cred_proc = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n", capture_output=True, text=True)
        gh_token = next((l.split("=", 1)[1].strip() for l in cred_proc.stdout.splitlines() if l.startswith("password=")), "")
        if gh_token:
            headers = {"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "kakao-setup"}
            with urllib.request.urlopen(urllib.request.Request(f"https://api.github.com/repos/{REPO}/actions/secrets/public-key", headers=headers), timeout=15) as r:
                pk = json.loads(r.read().decode("utf-8"))
            box = public.SealedBox(public.PublicKey(pk["key"].encode(), encoding.Base64Encoder()))
            pairs = {"KAKAO_REST_API_KEY": rest_key, "KAKAO_REFRESH_TOKEN": refresh_token}
            if client_secret:
                pairs["KAKAO_CLIENT_SECRET"] = client_secret
            for k, v in pairs.items():
                enc = base64.b64encode(box.encrypt(v.encode())).decode()
                put_req = urllib.request.Request(
                    f"https://api.github.com/repos/{REPO}/actions/secrets/{k}",
                    data=json.dumps({"encrypted_value": enc, "key_id": pk["key_id"]}).encode(),
                    headers={**headers, "Content-Type": "application/json"},
                    method="PUT",
                )
                with urllib.request.urlopen(put_req, timeout=15) as r:
                    print(f"✅ GitHub Secret 등록 완료: {k} (HTTP {r.status})")
    except Exception as exc:
        print(f"ℹ️ GitHub Secrets 자동 등록 건너뜀 ({exc}). 수동으로 등록해 주세요.")

    print("\n🎉 완료! 이제 매일 오후 6시(KST) 카카오톡 '나에게 보내기'로 자동 리포트가 발송됩니다.")


if __name__ == "__main__":
    main()
