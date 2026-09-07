# 채움학습.com 본문 기반 타이틀 접미사

## 대상과 보존 범위

- 작업 경로: 새 홈페이지12. 다른 홈페이지 폴더는 수정하지 않았습니다.
- 사이트: https://xn--ru4bz7e9zf0zk.com (채움학습.com)
- GitHub: 01039578283-hub/new12, main. 기존 공개 저장소 설정 유지.
- Vercel: 기존 new12 프로젝트의 production 및 기존 사용자 도메인 사용.
- 변경 전 기준 커밋: bc84eec09bd73bcb5bc483cff1a3b7831b8a9f6e.
- 대상: 전국학원 3개 범주와 과목별학원 18개 범주. 21개 범주 허브 + 7,791개 지역 상세 = 7,812개 HTML.
- 유지: 홈, 전국학원/과목별학원 최상위 허브, 학습가이드, 상담문의의 5개 HTML. 전체 HTML 및 기존 사이트맵은 7,817개.
- 각 대상 페이지의 기존 `|` 앞 타이틀을 유지하고 접미사만 변경. 기존 `og:title`, `twitter:title`이 있으면 같은 제목으로 동기화.
- H1/원고/FAQ/후기/목차/디자인/이미지/ALT/숨김 대표이미지/URL/canonical/robots/JSON-LD는 변경하지 않습니다. 기존 RSS 파일이 없어 새로 만들지 않습니다.

## 선택 방식과 한계

`tools/personalize_title_suffixes.py`와 `tools/title_suffix_rules.py`는 각 페이지의 실제 학습 문단에서 근거가 확인되는 주제만 선택합니다. 지역명이나 임의 순번으로 접미사를 배정하지 않습니다.

- 기존 4개 과목 범주의 subject-manuscript/subject-intro/subject-copy-card 구조와, 새 14개 범주의 독립 subject-content-section 구조를 모두 읽습니다.
- 핵심 답변과 명시된 학생의 어려움을 우선하며, 공통 문장은 범주별 반복 빈도에 따라 가중치를 낮춥니다.
- 전국학원은 각 페이지의 실제 답변을 읽어 준비물 습관, 기초 보완, 공부 분량, 진로 탐색 등의 내용을 반영합니다.
- 주소/학교/등록/수업 가능 여부/운영 안내/후기/가상 상담/체크리스트/숨김 내용에서 학습 주제를 만들어내지 않습니다.
- 초등·중등에 수능/모의고사를 넣지 않으며, 본문에 없는 시험 대비나 성과를 접미사에 추가하지 않습니다.
- 같은 뜻의 두 주제를 한 접미사에 중복 나열하지 않도록 조정합니다.
- **모든 접미사가 서로 다르다는 뜻은 아닙니다.** 기존 본문의 실제 핵심 주제가 같으면 접미사가 같을 수 있습니다. 지역명만 바꾸거나 근거 없는 주제를 추가해 중복을 숨기지 않습니다. 원고의 개별화 수준 자체는 이번 제목 작업으로 바뀌지 않습니다.

## 실행 및 검증

사이트 루트에서 Python 3으로 실행합니다. 외부 모델/API 호출과 원고 재생성은 없습니다.

```text
python -m unittest discover -s tools -p test_title_suffixes.py
python tools/personalize_title_suffixes.py --write
python tools/verify_title_release.py
python tools/personalize_title_suffixes.py --check
python tools/add_subject_anchor_tocs.py --check
```

- 회귀 테스트 63개: 제목 전용 변경, 학년·과목 제한, 실제 문장 근거, 상담/후기 제외, 각 본문 구조, 잘못된 의미 확장 방지.
- 변경 전 고정 Git 커밋과 제목 외 전체 내용을 비교합니다. 디자인·원고·이미지 속성·구조화 데이터까지 이 비교에 포함됩니다.
- 기존 과목별 상세 6,678개, 목차 링크 81,397개는 그대로 유지합니다.
- 모든 대상 페이지의 제목/공유 제목/근거/목차와 사이트맵을 검증합니다.
- `--check`는 재실행해도 추가 제목 변경이 없는지 검사합니다.
- 이후 원래 생성기를 다시 실행했다면, 이 접미사 후처리와 검증도 다시 실행해야 합니다. 범주를 추가할 때는 고정 개수 및 허브 근거를 먼저 갱신해야 합니다.

## 배포와 확인 기록

초기 작업 트리는 깨끗했고 기존 파일 삭제는 없습니다. `.env.local`, `.git`, `.vercel`, tools 등은 기존 `.vercelignore`의 배포 제외를 유지합니다. 기존 Vercel GitHub 연결이 있어 main 푸시의 해당 커밋 배포를 확인합니다. 별도 배포가 필요해도 동일한 검증 커밋만 사용합니다.

배포 완료 후 실제 사용자 도메인에서 모든 범주의 허브 및 대표 지역(명일동, 정렬 첫/중간/마지막)을 확인합니다. 단일 네트워크 오류는 그 URL만 재확인하며, 이를 원고 재생성 사유로 사용하지 않습니다.

```text
python tools/verify_title_release.py --public
```

기록 위치:

- `tools/reports/title-suffix-audit.json`: 페이지별 변경 전후 제목, 본문 근거, 제목 외 내용 해시.
- `tools/reports/title-suffix-local-verification.json`: 전체 로컬 검증 결과.
- `tools/reports/title-suffix-public-verification.json`: 배포 후 실제 공개 URL 검사 결과.
- `tools/reports/title-suffix-release.json`: 최종 커밋/배포/검증 수치.

앞의 두 검증 파일만 Git에 포함합니다. 배포 후 생성하는 기록 및 임시 계획은 Git·사이트 배포에서 제외합니다. 네이버 검색 제목은 재수집 시점과 검색엔진의 제목 재작성에 따라 실제 반영 시점/표현이 다를 수 있습니다.
