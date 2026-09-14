# 채움학습.com 공식 학습코칭 콘텐츠 업그레이드

상태: 2026-09-15 로컬 구현·검증 완료. 커밋·푸시·공개 배포하지 않음. 배포는 별도 사용자 요청 후 진행.

## 대상과 보존

- 경로: `C:/Users/1992k/Desktop/홈페이지 정리/새 홈페이지12`
- 도메인: `https://xn--ru4bz7e9zf0zk.com` (채움학습.com)
- 기준 HEAD: `f2ae2251f532f938eae05de8160a5910bab77561`
- 기존 홈·학습가이드·상담문의와 전국학원 4개/과목별학원 19개 허브 수정, 학습코칭 1개 신설. 합계 27 HTML.
- 비대상 HTML 7,791개와 기존 assets 761개 원본 바이트 유지. 동네 상세 원고·지점 정보·기존 URL·연락처·인증·DNS·요금제 변경 없음.
- 010-6839-8283 유지. 통화나 문자 발송은 테스트하지 않았으며 링크만 검사.

## 구현

- 메인: 학습 고민 → 학년·과목 → 학습코칭/AI 요약 → 공식 공간 이미지/영상 → 지역 안내 → FAQ 흐름.
- `/학습코칭/`: 4C(Check/Curriculum/Coaching/Consulting), 계획·학습·생활 관리, 과목별 AI, 결과 활용, FAQ.
- `/학습가이드/`: 계획·오답·시험 준비·학부모 대화를 구체적 실천 예시로 재작성.
- `/상담문의/`: 준비 자료, 개설 학년/과목·비용·프로그램 이용 조건을 확인하는 질문 정리. 전송 폼 없음.
- 23개 허브에 학년/과목별 요약과 맥락에 맞는 학습코칭·실천 가이드 링크 추가. 기존 지역 검색·지점 예시·FAQ·원고·이미지 유지.
- 27개 대상 페이지의 메뉴와 하단 메뉴 통일. 모바일 글자 크기·줄바꿈·버튼 터치 영역·카드 배치 보완. 사진 전체 비율 표시, 이미지 접기/잘라내기 없음.
- 공식 이미지/썸네일 12개(1,826,093 bytes), 영상 카드 3개. 자동재생/iframe 없이 클릭 시 외부 YouTube 이동.
- 허위 성과·후기/센터별 확정되지 않은 운영 조건 추가 없음. 기존 메인의 미확인 일반 후기와 SEO CHECK 작업용 노출 문구는 새 본문으로 교체.
- 본사 프로그램 대상: AI 영어/수학 초1~고3, 국어 중1~고3, 독서 초1~중2. 실제 지점 개설과 별개임을 안내.
- H1/title/description/canonical/OG, FAQ와 JSON-LD 일치, Breadcrumb/Article/Organization/WebSite/WebPage/허브 hasPart 관계 검증. 새 VideoObject 날짜나 성과를 만들지 않음.
- sitemap 7,818 URL(기존 7,817 + 학습코칭 1). RSS 24개(기존 23 + 1). 기존 RSS 항목 보존.

## 원본 및 생성

- 공식 자료: https://www.wawacenter.com/brand/wawacenter · https://www.wawacenter.com/intro/coachingSystem · https://www.wawacenter.com/intro/AISystem
- 영상: avpJfW7eIV0 / f_skFu40U04 / UIXUaBZdNXU. 원본 주소·파일 hash·검사 결과는 `tools/data/learning-upgrade/sources.json`, `tools/reports/learning-upgrade/official-source-check.json`.
- 생성기: `tools/upgrade_learning_20260915.py`. 기준 HEAD에서 대상 파일을 읽고 수정하는 방식이며 HEAD guard 존재. 마지막 반복 실행 changedFiles=0. 이후 HEAD 변경 뒤에는 무조건 재실행하지 말 것.
- 원고: `tools/data/learning-upgrade/*.html`, `content.json`.
- 스타일: `assets/learning-upgrade.css`, `.learning-upgraded` 범위.
- `.vercelignore`의 `tools/` 제외 유지. 작업용 보고서·원본 캡처·로그 백업은 공개 파일 아님.

## 검증 결과

- 독립 정적 감사 28,286/28,286 통과. FAQ 131쌍 본문/스키마 일치, 내부 참조 9,190개 및 앵커 505개 검사.
- 로컬 HTTP 52/52 통과: 수정 HTML 27, assets 19, discovery 4, 기존 동네 상세 2. 응답 바이트가 로컬 파일과 일치.
- 27페이지 × 320/390/1280px = 81 화면 통과. 768px 대표 6개 추가 점검 통과. 가로 넘침·H1·주요 버튼·로드 이미지 확인.
- 대표 6페이지 FAQ 26개를 클릭 열기/Enter 닫기로 확인. 전국학원 초등 허브와 과목별 초3 영어 허브 검색 1건/0건/초기화 371건 확인. 메뉴·동네 상세·AI 영어 앵커 이동 확인.
- 공식 출처 이미지 12개 육안·hash 검증. 모바일 홈 및 4C 화면 육안 검토. 전화/문자 실제 발송 및 외부 영상 전체 재생은 검사 범위 아님.
- 비교용 전문수업 4개 원고와 연속 한글 50자 이상의 동일 문구 없음. 제한된 문구 비교이며 네이버 중복문서 판단이나 노출 순위를 보장하지 않음.
- `git diff --check` 통과. 기준 HEAD 그대로, staged 파일 없음.

보고서: `tools/reports/learning-upgrade/generation.json`, `independent-qa/audit.json`, `independent-qa/local-http.json`, `browser-layouts.json`, `browser-interactions.json`. 화면: `mobile-home.png`, `mobile-coaching.png`.

## 다음 작업

로컬 미리보기: http://127.0.0.1:8812/ · http://127.0.0.1:8812/학습코칭/

배포 요청 시 현재 변경 범위/HEAD 재확인 → 감사 재실행 → 기존 GitHub/Vercel 경로로 배포 → 정식 도메인 실응답 및 비공개 경로 제외 검증. 로컬 통과를 공개 배포 완료로 말하지 말 것.
