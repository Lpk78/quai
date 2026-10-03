# HY-24 — Commit the art direction and the demo QR codes, with their index

- **Author:** `MORHI11`
- **Date:** 2026-10-04
- **Branch:** `docs/brand-assets`
- **Issue:** none (specification section 9, tools used; section 3, AI in the creative process)
- **Reviewer:** `SamDana-maker` by one-off swap — the rotation in CLAUDE.md puts `MORHI11`'s work on
  `Lpk78`, but `Lpk78` commissioned and generated this art direction, and reviewing the index of his
  own assets is the weaker of the two checks: the question is whether the attribution and the
  reproducibility claims hold, not whether the images are good. The rotation is unchanged; this is the
  exception, recorded so that the documented rotation and the practised one do not diverge without a
  trace.

## Prompt as typed

```
HY-24 Verser la direction artistique et les QR de démo dans le dépôt, avec leur index

Toute l'identité visuelle de QUAI a été produite avec des outils d'IA générative, et le dépôt n'en dit rien. La section 9 du cahier des charges demande de documenter les outils utilisés, la section 3 reconnaît l'IA dans le processus créatif : c'est un pan entier de notre usage de l'IA qui est invisible.

Les sources sont dans ~/Downloads/QUAI_DA_FINAL, dossier connecté. Les fichiers ont été renommés, ils sont identifiables par leur nom.

LES OUTILS, confirmés par Léo-Paul :
- ChatGPT : le logo, le kit de marque, les personnages, les véhicules, les décors, les maquettes d'écran, les planches de composants, les rendus isolés.
- Claude : le film de 32 secondes de la page d'accueil (web/public/quai-video.mp4).
- Retouche humaine derrière une partie des ressources. Écris-le à ce niveau et pas plus : « certaines ressources ont été retouchées à la main après génération ».
- 08_HIGGSFIELD/Higgsfield_website_workflow.txt est une méthode en dix plans préparée pour Higgsfield et NON utilisée — le film livré vient de Claude. Ne dis pas que Higgsfield a servi. Une piste préparée puis abandonnée fait partie du processus et la section 11 la valorise, présentée comme telle.
N'ajoute aucun autre nom d'outil.

LES QR, décodés par décodeur logiciel et non à l'œil :
10_DEMO_QR/demo-qr-operator-badge.png → QUAI:OPERATOR:QUAI-OP-7842
10_DEMO_QR/demo-qr-parcel-label.png   → QUAI:BOX:QUAI-BOX-0001

Sans eux, personne ne peut rejouer la démo depuis un clone. Verse-les et documente à quel écran chacun sert : le badge sur /login, l'étiquette sur /app/scan. Tu peux vérifier les chaînes autrement si tu veux, mais elles ne viennent pas d'une lecture approximative.

À VERSER depuis 08_SITE_IMAGES/ :
- mockup-01-home, mockup-02-voice-rules, mockup-03-load-plan-3d, mockup-04-route-delivery-order
- ui-kit-01-app-components, ui-kit-02-voice-components, ui-kit-03-plan-route-components
- render-van-open-loaded, render-operator, render-forklift, render-pallet-jack, render-box-quai, render-pin-active, render-pin-inactive, render-button-start-loading, render-tabs-load-view, render-mic-button
- app-icon-dark

À VERSER depuis les autres dossiers :
- 00_MASTER_BOARD/QUAI_master_brand_board.png
- 02_CHARACTERS/QUAI_main_operator_reference.png et QUAI_secondary_characters.png
- 03_OBJECTS_VEHICLES/QUAI_objects_vehicles.png
- 04_ENVIRONMENTS/QUAI_environments.png
- 06_STORYBOARD/QUAI_film_storyboard.png et QUAI_delivery_story.png
- 07_TOKENS/QUAI_colour_palette.png et QUAI_typography.png
- 09_GUIDE/QUAI_FINAL_Brand_Guide.pdf

À NE PAS VERSER : device-frame-blank.png, logo-glow-dark.png, les dossiers _doublons/ et _to_delete/, et les variantes successives de landing_refs.

POIDS : l'ensemble en PNG fait une trentaine de méga-octets, c'est trop. Le dépôt utilise déjà le WebP pour documentation/screenshots/ — convertis par cohérence. Garde le PDF et les deux QR en PNG : un QR recompressé peut devenir illisible.

L'INDEX, et c'est lui qui transforme un tas d'images en preuve : écris assets/brand/README.md. Pour chaque pièce, ce que c'est, à quoi elle a servi, avec quel outil elle a été produite.

Et dis-y ce qui vaut plus que les images : les quatre maquettes documentent aussi ce qu'on a refusé d'en reprendre — les 124 colis, les portes d'accès inventées, la photo de fourgon à la place du plan calculé. Les tableaux d'écarts des PR #63, #64 et #72 disent pourquoi. Renvoie-y.

Reviewer : SamDana-maker. PR normale.
```

## Outcome

(filled at the end)
