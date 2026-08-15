from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SubjectCategory:
    slug: str
    label: str
    workbook: str | None
    level: str
    grade_number: int
    subject: str
    school_field: str
    grade_field: str
    national_category: str
    representative_offset: int
    existing: bool = False

    @property
    def grade_code(self) -> str:
        prefix = {"초등": "초", "중등": "중", "고등": "고"}[self.level]
        return f"{prefix}{self.grade_number}"

    @property
    def grade_label(self) -> str:
        school = {"초등": "초등학교", "중등": "중학교", "고등": "고등학교"}[self.level]
        return f"{school} {self.grade_number}학년"


# Root hub order is intentional: existing and new categories are presented by
# school level, grade, then subject.  Representative offsets are unique across
# the complete catalog, which also prevents same-row collisions in a 371-image
# pool when the generator uses a category-specific cyclic permutation.
SUBJECT_CATALOG: tuple[SubjectCategory, ...] = (
    SubjectCategory("초3수학학원", "초3 수학학원", "초3 수학학원 원고.xlsx", "초등", 3, "수학", "타깃학교\n(초)", "가능학년\n(수학)", "초등학생학원", 0),
    SubjectCategory("초3영어학원", "초3 영어학원", "초3 영어학원.xlsx", "초등", 3, "영어", "타깃학교\n(초)", "가능학년\n(영어)", "초등학생학원", 1),
    SubjectCategory("초4수학학원", "초4 수학학원", "초4 수학학원 원고.xlsx", "초등", 4, "수학", "타깃학교\n(초)", "가능학년\n(수학)", "초등학생학원", 2),
    SubjectCategory("초4영어학원", "초4 영어학원", "초4 영어학원 원고.xlsx", "초등", 4, "영어", "타깃학교\n(초)", "가능학년\n(영어)", "초등학생학원", 3),
    SubjectCategory("초5수학학원", "초5 수학학원", "초5 수학학원 원고.xlsx", "초등", 5, "수학", "타깃학교\n(초)", "가능학년\n(수학)", "초등학생학원", 4),
    SubjectCategory("초5영어학원", "초5 영어학원", "초5 영어학원 원고.xlsx", "초등", 5, "영어", "타깃학교\n(초)", "가능학년\n(영어)", "초등학생학원", 5),
    SubjectCategory("초6수학학원", "초6 수학학원", None, "초등", 6, "수학", "타깃학교\n(초)", "가능학년\n(수학)", "초등학생학원", 6, True),
    SubjectCategory("초6영어학원", "초6 영어학원", None, "초등", 6, "영어", "타깃학교\n(초)", "가능학년\n(영어)", "초등학생학원", 7, True),
    SubjectCategory("중1수학학원", "중1 수학학원", None, "중등", 1, "수학", "타깃학교\n(중)", "가능학년\n(수학)", "중학생학원", 8, True),
    SubjectCategory("중1영어학원", "중1 영어학원", None, "중등", 1, "영어", "타깃학교\n(중)", "가능학년\n(영어)", "중학생학원", 9, True),
    SubjectCategory("중2수학학원", "중2 수학학원", "중2 수학학원 원고.xlsx", "중등", 2, "수학", "타깃학교\n(중)", "가능학년\n(수학)", "중학생학원", 10),
    SubjectCategory("중2영어학원", "중2 영어학원", "중2 영어학원 원고.xlsx", "중등", 2, "영어", "타깃학교\n(중)", "가능학년\n(영어)", "중학생학원", 11),
    SubjectCategory("중3수학학원", "중3 수학학원", "중3 수학학원 원고.xlsx", "중등", 3, "수학", "타깃학교\n(중)", "가능학년\n(수학)", "중학생학원", 12),
    SubjectCategory("중3영어학원", "중3 영어학원", "중3 영어학원 원고.xlsx", "중등", 3, "영어", "타깃학교\n(중)", "가능학년\n(영어)", "중학생학원", 13),
    SubjectCategory("고1수학학원", "고1 수학학원", "고1 수학학원 원고.xlsx", "고등", 1, "수학", "타깃학교\n(고)", "가능학년\n(수학)", "고등학생학원", 14),
    SubjectCategory("고1영어학원", "고1 영어학원", "고1 영어학원 원고.xlsx", "고등", 1, "영어", "타깃학교\n(고)", "가능학년\n(영어)", "고등학생학원", 15),
    SubjectCategory("고2수학학원", "고2 수학학원", "고2 수학학원 원고.xlsx", "고등", 2, "수학", "타깃학교\n(고)", "가능학년\n(수학)", "고등학생학원", 16),
    SubjectCategory("고2영어학원", "고2 영어학원", "고2 영어학원 원고.xlsx", "고등", 2, "영어", "타깃학교\n(고)", "가능학년\n(영어)", "고등학생학원", 17),
)


BY_SLUG = {category.slug: category for category in SUBJECT_CATALOG}
NEW_CATEGORIES = tuple(category for category in SUBJECT_CATALOG if not category.existing)
PROTECTED_CATEGORIES = tuple(category for category in SUBJECT_CATALOG if category.existing)


def validate_catalog() -> None:
    if len(SUBJECT_CATALOG) != 18 or len(NEW_CATEGORIES) != 14 or len(PROTECTED_CATEGORIES) != 4:
        raise RuntimeError("과목 카탈로그 수가 예상과 다릅니다")
    slugs = [category.slug for category in SUBJECT_CATALOG]
    labels = [category.label for category in SUBJECT_CATALOG]
    offsets = [category.representative_offset for category in SUBJECT_CATALOG]
    workbooks = [category.workbook for category in NEW_CATEGORIES]
    for name, values in (("slug", slugs), ("label", labels), ("representative_offset", offsets), ("workbook", workbooks)):
        if len(values) != len(set(values)):
            raise RuntimeError(f"과목 카탈로그 {name} 값이 중복됩니다")
    if any(category.workbook is None for category in NEW_CATEGORIES):
        raise RuntimeError("신규 범주에는 원고 파일명이 필요합니다")


validate_catalog()
