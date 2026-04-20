# Citation Scan: In-Text Citations Missing from Bibliography

Date: 2026-03-26

## Scope

This note compares the in-text citations in [thesis_main/Manuscript/Full_Thesis_Draft.md](thesis_main/Manuscript/Full_Thesis_Draft.md) against the entries currently present in [thesis_main/TeX/biblio.bib](thesis_main/TeX/biblio.bib).

## Summary

Most of the core valuation, econometrics, and Philippine machine learning citations are present in the bibliography. However, there are 17 unique in-text citations with no matching bibliography entry, plus 2 mismatch cases where the cited source appears to exist in the bibliography under a different year.

## In-Text Citations Not Found in the Bib File

- ~~PSA Region 7, 2025~~
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L13](thesis_main/Manuscript/Full_Thesis_Draft.md#L13) and [thesis_main/Manuscript/Full_Thesis_Draft.md#L148](thesis_main/Manuscript/Full_Thesis_Draft.md#L148)
- ~~Yacim and Boshoff, 2018~~
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L104](thesis_main/Manuscript/Full_Thesis_Draft.md#L104)
- ~~Pai and Wang, 2020~~
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L104](thesis_main/Manuscript/Full_Thesis_Draft.md#L104)
- ~~Grinsztajn et al., 2022~~
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L108](thesis_main/Manuscript/Full_Thesis_Draft.md#L108)
- ~~Lundberg and Lee, 2017~~
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L108](thesis_main/Manuscript/Full_Thesis_Draft.md#L108)
- ~~Becsky-Nagy and Sachicola, 2025~~
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L162](thesis_main/Manuscript/Full_Thesis_Draft.md#L162)
- Wibowo et al., 2023
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L196](thesis_main/Manuscript/Full_Thesis_Draft.md#L196)
- Samsudin et al., 2022
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L196](thesis_main/Manuscript/Full_Thesis_Draft.md#L196)
- Tobler, 1970
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L206](thesis_main/Manuscript/Full_Thesis_Draft.md#L206)
- Google Developers, 2025
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L210](thesis_main/Manuscript/Full_Thesis_Draft.md#L210)
- Humanitarian OpenStreetMap Team, 2024
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L212](thesis_main/Manuscript/Full_Thesis_Draft.md#L212)
- Sinnott, 1984
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L216](thesis_main/Manuscript/Full_Thesis_Draft.md#L216)
- Boeing, 2017
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L222](thesis_main/Manuscript/Full_Thesis_Draft.md#L222) and [thesis_main/Manuscript/Full_Thesis_Draft.md#L371](thesis_main/Manuscript/Full_Thesis_Draft.md#L371)
- Boeing, 2019
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L222](thesis_main/Manuscript/Full_Thesis_Draft.md#L222)
- Fonte et al., 2017
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L224](thesis_main/Manuscript/Full_Thesis_Draft.md#L224)
- Yao et al., 2018
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L224](thesis_main/Manuscript/Full_Thesis_Draft.md#L224)
- Moran, 1950
  Found at [thesis_main/Manuscript/Full_Thesis_Draft.md#L235](thesis_main/Manuscript/Full_Thesis_Draft.md#L235)

## Mismatch Cases

These are likely not true omissions, but they still need correction because the in-text citation does not match the bibliography entry.

- Agosto, 2020
  Cited at [thesis_main/Manuscript/Full_Thesis_Draft.md#L152](thesis_main/Manuscript/Full_Thesis_Draft.md#L152), [thesis_main/Manuscript/Full_Thesis_Draft.md#L218](thesis_main/Manuscript/Full_Thesis_Draft.md#L218), [thesis_main/Manuscript/Full_Thesis_Draft.md#L247](thesis_main/Manuscript/Full_Thesis_Draft.md#L247), and [thesis_main/Manuscript/Full_Thesis_Draft.md#L284](thesis_main/Manuscript/Full_Thesis_Draft.md#L284)
  Bibliography currently has Agosto 2017 at [thesis_main/TeX/biblio.bib#L116](thesis_main/TeX/biblio.bib#L116)
- International Valuation Standards, 2025 / IVS 2025
  Referenced at [thesis_main/Manuscript/Full_Thesis_Draft.md#L39](thesis_main/Manuscript/Full_Thesis_Draft.md#L39), [thesis_main/Manuscript/Full_Thesis_Draft.md#L64](thesis_main/Manuscript/Full_Thesis_Draft.md#L64), [thesis_main/Manuscript/Full_Thesis_Draft.md#L106](thesis_main/Manuscript/Full_Thesis_Draft.md#L106), [thesis_main/Manuscript/Full_Thesis_Draft.md#L268](thesis_main/Manuscript/Full_Thesis_Draft.md#L268), [thesis_main/Manuscript/Full_Thesis_Draft.md#L282](thesis_main/Manuscript/Full_Thesis_Draft.md#L282), and [thesis_main/Manuscript/Full_Thesis_Draft.md#L516](thesis_main/Manuscript/Full_Thesis_Draft.md#L516)
  Bibliography currently has IVS 2020 at [thesis_main/TeX/biblio.bib#L190](thesis_main/TeX/biblio.bib#L190)

## Attribution Note

- TPS 2023 appears as shorthand at [thesis_main/Manuscript/Full_Thesis_Draft.md#L142](thesis_main/Manuscript/Full_Thesis_Draft.md#L142), but the likely source is Otsuka et al. 2023 at [thesis_main/TeX/biblio.bib#L169](thesis_main/TeX/biblio.bib#L169). This should be made explicit in the draft.

## Next Fixes

1. Add bibliography entries for the 17 missing citations.
2. Resolve the Agosto year mismatch.
3. Add a proper IVS 2025 bibliography entry if the thesis is citing the 2025 standards rather than the 2020 edition.
4. Replace or clarify TPS 2023 so the attribution is traceable.
